from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.auth.schemas import (
    AdminActionResponse,
    AdminUserDetailResponse,
    RegisterRequest,
    RolResponse,
    UsuarioResponse,
)


class AuthService:
    @staticmethod
    def obtener_roles_usuario(user: Usuario, uow: SqlModelUnitOfWork) -> list[str]:
        """Obtiene los nombres de los roles de un usuario."""
        return uow.roles.get_names_for_user(user.id)

    @staticmethod
    def _usuario_a_response(usuario: Usuario, roles_nombres: list[str]) -> UsuarioResponse:
        """Convierte un Usuario + roles a UsuarioResponse."""
        roles = [RolResponse(id=0, nombre=r) for r in roles_nombres]
        return UsuarioResponse(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            celular=usuario.celular,
            is_active=usuario.is_active,
            roles=roles,
        )

    @staticmethod
    def autenticar(email: str, password: str, uow: SqlModelUnitOfWork) -> tuple[Usuario, list[str]]:
        """Autentica y retorna (usuario, roles)."""
        user = uow.usuarios.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña inválidos",
            )

        if not user.is_active or user.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo",
            )

        roles = AuthService.obtener_roles_usuario(user, uow)
        return user, roles

    @staticmethod
    def crear_usuario(request: RegisterRequest, uow: SqlModelUnitOfWork) -> UsuarioResponse:
        """Registra un nuevo usuario con rol CLIENT y retorna UsuarioResponse con roles."""
        existing_user = uow.usuarios.get_by_email(request.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email ya está registrado",
            )

        nuevo_usuario = Usuario(
            email=request.email,
            password_hash=hash_password(request.password),
            nombre=request.nombre,
            apellido=request.apellido,
            celular=request.celular,
            is_active=True,
        )

        uow.usuarios.save(nuevo_usuario)
        uow.flush()

        client_rol = uow.roles.get_by_name("CLIENT")
        if client_rol:
            uow.roles.assign_to_user(nuevo_usuario.id, client_rol.id)

        return AuthService._usuario_a_response(nuevo_usuario, ["CLIENT"])

    @staticmethod
    def obtener_usuario_con_roles(
        usuario_id: int, uow: SqlModelUnitOfWork
    ) -> UsuarioResponse:
        usuario = uow.usuarios.get_by_id(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        roles_nombres = AuthService.obtener_roles_usuario(usuario, uow)
        return AuthService._usuario_a_response(usuario, roles_nombres)

    @staticmethod
    def listar_usuarios(uow: SqlModelUnitOfWork) -> list[AdminUserDetailResponse]:
        """Lista todos los usuarios con sus roles (solo para admin)."""
        usuarios = uow.usuarios.list_all()

        result = []
        for user in usuarios:
            roles_nombres = AuthService.obtener_roles_usuario(user, uow)
            roles = [RolResponse(id=0, nombre=r) for r in roles_nombres]
            result.append(AdminUserDetailResponse(
                id=user.id,
                email=user.email,
                nombre=user.nombre,
                apellido=user.apellido,
                celular=user.celular,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
                deleted_at=user.deleted_at,
                roles=roles,
            ))
        return result

    @staticmethod
    def toggle_usuario_activo(
        usuario_id: int, activo: bool, uow: SqlModelUnitOfWork
    ) -> AdminActionResponse:
        """Activa o desactiva un usuario."""
        usuario = uow.usuarios.get_by_id(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        
        usuario.is_active = activo
        uow.usuarios.save(usuario)

        roles_nombres = AuthService.obtener_roles_usuario(usuario, uow)
        roles = [RolResponse(id=0, nombre=r) for r in roles_nombres]

        return AdminActionResponse(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            celular=usuario.celular,
            is_active=usuario.is_active,
            roles=roles,
        )
