from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.base import get_session
from app.db.models.rol import Rol
from app.db.models.usuario import Usuario, UsuarioRol
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str | None:
        settings = get_settings()
        token = request.cookies.get(settings.auth_cookie_name)

        if not token:
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                token = authorization.removeprefix("Bearer ").strip()

        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No autenticado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

        return token


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/v1/auth/token")
optional_oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl="/api/v1/auth/token",
    auto_error=False,
)


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _resolve_user_from_token(session: Session, token: str) -> Usuario:
    credentials_exception = _credentials_exception()

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise credentials_exception

    user = session.exec(select(Usuario).where(Usuario.id == user_id_int)).first()

    if user is None:
        raise credentials_exception

    if not user.is_active or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cuenta de usuario desactivada",
        )

    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> Usuario:
    return _resolve_user_from_token(session, token)


async def get_optional_current_user(
    token: Annotated[str | None, Depends(optional_oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> Usuario | None:
    if token is None:
        return None

    return _resolve_user_from_token(session, token)


def user_has_any_role(user: Usuario | None, roles: list[str], session: Session) -> bool:
    if user is None:
        return False

    statement = (
        select(Rol.nombre)
        .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
        .where(UsuarioRol.usuario_id == user.id)
    )
    user_roles: list[str] = list(session.exec(statement).all())

    return any(role in roles for role in user_roles)


def _normalize_allowed_roles(allowed_roles: tuple[str | list[str] | tuple[str, ...], ...]) -> list[str]:
    if len(allowed_roles) == 1 and isinstance(allowed_roles[0], (list, tuple)):
        return list(allowed_roles[0])

    return [role for role in allowed_roles if isinstance(role, str)]


def require_role(*allowed_roles: str | list[str] | tuple[str, ...]):
    """
    Factory de dependencias para control de acceso basado en roles (RBAC).

    Obtiene el usuario autenticado via get_current_user y consulta los roles
    desde la BD via UnitOfWork, garantizando que reflejan el estado actual
    del usuario.

    Uso:
        @router.get("/admin/...", dependencies=[Depends(require_role("ADMIN"))])
        _admin: Usuario = Depends(require_role("ADMIN"))
    """

    normalized_roles = _normalize_allowed_roles(allowed_roles)

    async def role_checker(
        current_user: Usuario = Depends(get_current_user),
        uow: SqlModelUnitOfWork = Depends(get_uow),
    ) -> Usuario:
        if not normalized_roles:
            return current_user

        session = uow.session
        statement = (
            select(Rol.nombre)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .where(UsuarioRol.usuario_id == current_user.id)
        )
        user_roles: list[str] = list(session.exec(statement).all())

        if not any(role in normalized_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Permisos insuficientes. Tus roles: {user_roles}. "
                    f"Se requiere uno de: {normalized_roles}"
                ),
            )

        return current_user

    return role_checker
