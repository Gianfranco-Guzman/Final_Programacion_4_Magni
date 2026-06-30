from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.Config.config import get_settings
from app.core.Config.dependencies import get_current_user, require_role
from app.core.rate_limit import auth_rate_limiter
from app.core.security import create_access_token
from app.modules.auth.model import Usuario
from app.db.unit_of_work import UnitOfWork, get_uow
from app.modules.auth.schemas import (
    AdminActionResponse,
    AdminUserDetailResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    SessionResponse,
    UsuarioResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _set_auth_cookie(response: Response, access_token: str) -> None:  #fucion para configurar la cookie
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=access_token,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        samesite=settings.auth_cookie_samesite, 
        secure=settings.auth_cookie_secure,
        path="/",
    )


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        samesite=settings.auth_cookie_samesite,
        secure=settings.auth_cookie_secure,
        path="/",
    )


def _clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.auth_cookie_name,
        httponly=True,
        samesite=settings.auth_cookie_samesite,
        secure=settings.auth_cookie_secure,
        path="/",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        httponly=True,
        samesite=settings.auth_cookie_samesite,
        secure=settings.auth_cookie_secure,
        path="/",
    )


def _client_identifier(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _build_session_response(message: str, access_token: str, refresh_token: str) -> SessionResponse:
    return SessionResponse(
        message=message,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        refresh_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60,
    )


@router.post(
    "/login",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Login de usuario con cookie HttpOnly",
    responses={
        200: {"description": "Login exitoso"},
        401: {"description": "Credenciales inválidas"},
    },
)
async def login(
    request: LoginRequest,
    http_request: Request,
    response: Response,
    uow: UnitOfWork = Depends(get_uow),
) -> SessionResponse:
    identifier = _client_identifier(http_request)
    auth_rate_limiter.ensure_allowed("login", identifier)
    try:
        user, roles = AuthService.autenticar(request.email, request.password, uow)
    except Exception:
        auth_rate_limiter.register_failure("login", identifier)
        raise
    auth_rate_limiter.clear("login", identifier)
    access_token = create_access_token({"sub": str(user.id), "roles": roles})
    refresh_token = AuthService.crear_refresh_token(user, uow)
    _set_auth_cookie(response, access_token)
    _set_refresh_cookie(response, refresh_token)

    return _build_session_response("Login exitoso. Sesión iniciada.", access_token, refresh_token)


@router.post(
    "/token",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Login OAuth2 con cookie HttpOnly",
    responses={
        200: {"description": "Login exitoso"},
        401: {"description": "Credenciales inválidas"},
    },
)
async def login_oauth2(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    http_request: Request,
    response: Response,
    uow: UnitOfWork = Depends(get_uow),
) -> SessionResponse:
    identifier = _client_identifier(http_request)
    auth_rate_limiter.ensure_allowed("login", identifier)
    try:
        user, roles = AuthService.autenticar(
            form_data.username, form_data.password, uow)
    except Exception:
        auth_rate_limiter.register_failure("login", identifier)
        raise
    auth_rate_limiter.clear("login", identifier)
    access_token = create_access_token({"sub": str(user.id), "roles": roles})
    refresh_token = AuthService.crear_refresh_token(user, uow)
    _set_auth_cookie(response, access_token)
    _set_refresh_cookie(response, refresh_token)

    return _build_session_response("Login exitoso. Sesión iniciada.", access_token, refresh_token)


@router.post(
    "/refresh",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Renovar access token usando refresh token",
)
async def refresh_session(
    request: Request,
    response: Response,
    body: RefreshTokenRequest | None = None,
    uow: UnitOfWork = Depends(get_uow),
) -> SessionResponse:
    refresh_token = body.refresh_token if body and body.refresh_token else request.cookies.get(settings.refresh_cookie_name)
    user, roles, new_refresh_token = AuthService.rotar_refresh_token(refresh_token, uow)
    access_token = create_access_token({"sub": str(user.id), "roles": roles})
    _set_auth_cookie(response, access_token)
    _set_refresh_cookie(response, new_refresh_token)
    return _build_session_response("Sesión renovada exitosamente.", access_token, new_refresh_token)


@router.post(
    "/logout",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión y limpiar cookie",
)
async def logout(
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(get_uow),
) -> SessionResponse:
    AuthService.revocar_refresh_token(request.cookies.get(settings.refresh_cookie_name), uow)
    _clear_auth_cookie(response)
    _clear_refresh_cookie(response)
    return SessionResponse(message="Sesión cerrada exitosamente")


@router.post(
    "/register",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registro de nuevo usuario",
    responses={
        201: {"description": "Usuario creado"},
        422: {"description": "Email ya registrado"},
    },
)
async def register(
    request: RegisterRequest,
    http_request: Request,
    uow: UnitOfWork = Depends(get_uow),
) -> UsuarioResponse:
    identifier = _client_identifier(http_request)
    auth_rate_limiter.ensure_allowed("register", identifier)
    try:
        created = AuthService.crear_usuario(request, uow)
    except Exception:
        auth_rate_limiter.register_failure("register", identifier)
        raise
    auth_rate_limiter.clear("register", identifier)
    return created


@router.get(
    "/me",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario actual",
    responses={
        200: {"description": "Información del usuario autenticado"},
        401: {"description": "No autenticado o token inválido"},
    },
)
async def get_me(
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> UsuarioResponse:
    return AuthService.obtener_usuario_con_roles(current_user.id, uow)


@router.get(
    "/admin/usuarios",
    response_model=list[AdminUserDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los usuarios (solo admin)",
    responses={
        200: {"description": "Lista de usuarios con roles"},
        403: {"description": "No autorizado — se requiere rol ADMIN"},
    },
)
async def admin_listar_usuarios(
    _admin: Usuario = Depends(require_role("ADMIN")),
    uow: UnitOfWork = Depends(get_uow),
) -> list[AdminUserDetailResponse]:
    return AuthService.listar_usuarios(uow)


@router.patch(
    "/admin/usuarios/{usuario_id}/desactivar",
    response_model=AdminActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Desactivar usuario (solo admin)",
    responses={
        200: {"description": "Usuario desactivado"},
        403: {"description": "No autorizado — se requiere rol ADMIN"},
        404: {"description": "Usuario no encontrado"},
    },
)
async def admin_desactivar_usuario(
    usuario_id: int,
    _admin: Usuario = Depends(require_role("ADMIN")),
    uow: UnitOfWork = Depends(get_uow),
) -> AdminActionResponse:
    return AuthService.toggle_usuario_activo(usuario_id, activo=False, uow=uow)


@router.patch(
    "/admin/usuarios/{usuario_id}/activar",
    response_model=AdminActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Reactivar usuario (solo admin)",
    responses={
        200: {"description": "Usuario reactivado"},
        403: {"description": "No autorizado — se requiere rol ADMIN"},
        404: {"description": "Usuario no encontrado"},
    },
)
async def admin_activar_usuario(
    usuario_id: int,
    _admin: Usuario = Depends(require_role("ADMIN")),
    uow: UnitOfWork = Depends(get_uow),
) -> AdminActionResponse:
    return AuthService.toggle_usuario_activo(usuario_id, activo=True, uow=uow)
