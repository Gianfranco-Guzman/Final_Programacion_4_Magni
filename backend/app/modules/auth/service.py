from fastapi import HTTPException, status
from sqlmodel import select

from app.core.security import hash_password, verify_password
from app.db.models.rol import Rol
from app.db.models.usuario import Usuario, UsuarioRol
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.auth.schemas import RegisterRequest, UsuarioResponse, RolResponse


class AuthService:
    @staticmethod
    def obtener_roles_usuario(user: Usuario, uow: SqlModelUnitOfWork) -> list[str]:
        """Obtiene los nombres de los roles de un usuario."""
        session = uow.session
        statement = (
            select(Rol.nombre)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .where(UsuarioRol.usuario_id == user.id)
        )
        return list(session.exec(statement).all())

    @staticmethod
    def autenticar(email: str, password: str, uow: SqlModelUnitOfWork) -> tuple[Usuario, list[str]]:
        """Autentica y retorna (usuario, roles)."""
        session = uow.session
        statement = select(Usuario).where(Usuario.email == email)
        user = session.exec(statement).first()

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña inválidos",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo",
            )

        roles = AuthService.obtener_roles_usuario(user, uow)
        return user, roles

    @staticmethod
    def crear_usuario(request: RegisterRequest, uow: SqlModelUnitOfWork) -> Usuario:
        session = uow.session
        statement = select(Usuario).where(Usuario.email == request.email)
        existing_user = session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email ya está registrado",
            )

        nuevo_usuario = Usuario(
            email=request.email,
            password_hash=hash_password(request.password),
            nombre=request.nombre,
            is_active=True,
        )

        session.add(nuevo_usuario)
        uow.flush()

        client_rol = session.exec(select(Rol).where(Rol.nombre == "CLIENT")).first()
        if client_rol:
            session.add(UsuarioRol(usuario_id=nuevo_usuario.id, rol_id=client_rol.id))

        return nuevo_usuario

    @staticmethod
    def obtener_usuario_con_roles(
        usuario_id: int, uow: SqlModelUnitOfWork
    ) -> UsuarioResponse:
        session = uow.session
        statement = select(Usuario).where(Usuario.id == usuario_id)
        usuario = session.exec(statement).first()

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        roles_nombres = AuthService.obtener_roles_usuario(usuario, uow)
        roles = [RolResponse(id=0, nombre=r) for r in roles_nombres]

        return UsuarioResponse(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            is_active=usuario.is_active,
            roles=roles,
        )
