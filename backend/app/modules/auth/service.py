from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.security import (
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.modules.auth.model import RefreshToken, Usuario
from app.db.unit_of_work import UnitOfWork
from app.modules.auth.schemas import (
    AdminActionResponse,
    AdminUserDetailResponse,
    RegisterRequest,
    RolResponse,
    UsuarioResponse,
)


class AuthService:
    @staticmethod
    def crear_refresh_token(usuario: Usuario, uow: UnitOfWork) -> str:
        refresh_token = create_refresh_token({"sub": str(usuario.id)})
        payload = decode_refresh_token(refresh_token)
        if payload is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo generar refresh token")

        token_record = RefreshToken(
            usuario_id=usuario.id,
            token_hash=hash_token(refresh_token),
            jti=payload["jti"],
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
        uow.refresh_tokens.save(token_record)
        uow.flush()
        return refresh_token

    @staticmethod
    def rotar_refresh_token(refresh_token: str, uow: UnitOfWork) -> tuple[Usuario, list[str], str]:
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token requerido")

        payload = decode_refresh_token(refresh_token)
        if payload is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido o expirado")

        token_record = uow.refresh_tokens.get_active_by_token_hash(hash_token(refresh_token))
        if token_record is None or token_record.jti != payload.get("jti"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revocado o inválido")

        usuario_id = payload.get("sub")
        try:
            usuario_id_int = int(usuario_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")

        usuario = uow.usuarios.get_by_id(usuario_id_int)
        if not usuario or not usuario.is_active or usuario.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inactivo o inexistente")

        uow.refresh_tokens.revoke(token_record)
        nuevo_refresh = AuthService.crear_refresh_token(usuario, uow)
        roles = AuthService.obtener_roles_usuario(usuario, uow)
        return usuario, roles, nuevo_refresh

    @staticmethod
    def revocar_refresh_token(refresh_token: str | None, uow: UnitOfWork) -> None:
        if not refresh_token:
            return
        token_record = uow.refresh_tokens.get_active_by_token_hash(hash_token(refresh_token))
        if token_record is not None:
            uow.refresh_tokens.revoke(token_record)
            uow.flush()

    @staticmethod
    def obtener_roles_usuario(user: Usuario, uow: UnitOfWork) -> list[str]:
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
    def autenticar(email: str, password: str, uow: UnitOfWork) -> tuple[Usuario, list[str]]:
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
    def crear_usuario(request: RegisterRequest, uow: UnitOfWork) -> UsuarioResponse:
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
        usuario_id: int, uow: UnitOfWork
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
    def listar_usuarios(uow: UnitOfWork) -> list[AdminUserDetailResponse]:
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
        usuario_id: int, activo: bool, uow: UnitOfWork
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
