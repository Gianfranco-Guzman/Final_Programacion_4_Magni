from typing import Annotated

from fastapi import Depends, HTTPException, Request, WebSocket, WebSocketException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):        #clase para obtener el token de la cookie o del header Authorization
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


def _resolve_user_from_token(uow: SqlModelUnitOfWork, token: str) -> Usuario:      #para saber el usuario a partir del ttoken
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

    user = uow.usuarios.get_by_id(user_id_int)

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
    uow: Annotated[SqlModelUnitOfWork, Depends(get_uow)],
) -> Usuario:
    return _resolve_user_from_token(uow, token)


def get_user_role_names(uow: SqlModelUnitOfWork, user_id: int) -> list[str]:
    return uow.roles.get_names_for_user(user_id)


async def get_optional_current_user(
    token: Annotated[str | None, Depends(optional_oauth2_scheme)],
    uow: Annotated[SqlModelUnitOfWork, Depends(get_uow)],
) -> Usuario | None:
    if token is None:
        return None

    return _resolve_user_from_token(uow, token)


def user_has_any_role(user: Usuario | None, roles: list[str], uow: SqlModelUnitOfWork) -> bool:
    if user is None:
        return False

    return uow.roles.user_has_any_role(user.id, roles)


async def get_current_websocket_user(
    websocket: WebSocket,
    uow: Annotated[SqlModelUnitOfWork, Depends(get_uow)],
) -> Usuario:
    settings = get_settings()
    token = websocket.cookies.get(settings.auth_cookie_name)
    if not token:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="No autenticado")

    try:
        return _resolve_user_from_token(uow, token)
    except HTTPException as exc:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=exc.detail)


def _normalize_allowed_roles(allowed_roles: tuple[str | list[str] | tuple[str, ...], ...]) -> list[str]:      #normalizar los roles permitidos
    if len(allowed_roles) == 1 and isinstance(allowed_roles[0], (list, tuple)):
        return list(allowed_roles[0])

    return [role for role in allowed_roles if isinstance(role, str)]


def require_role(*allowed_roles: str | list[str] | tuple[str, ...]):

    normalized_roles = _normalize_allowed_roles(allowed_roles)

    async def role_checker(
        current_user: Usuario = Depends(get_current_user),
        uow: SqlModelUnitOfWork = Depends(get_uow),
    ) -> Usuario:
        if not normalized_roles:
            return current_user

        user_roles = get_user_role_names(uow, current_user.id)

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
