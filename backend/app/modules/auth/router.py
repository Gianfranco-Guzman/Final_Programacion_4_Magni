from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import get_settings
from app.core.dependencies import get_current_user, require_role
from app.core.security import create_access_token
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.modules.auth.schemas import (
    AdminActionResponse,
    AdminUserDetailResponse,
    LoginRequest,
    RegisterRequest,
    SessionResponse,
    UsuarioResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _set_auth_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=access_token,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
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
    response: Response,
    uow: SqlModelUnitOfWork = Depends(get_uow),
) -> SessionResponse:
    user, roles = AuthService.autenticar(request.email, request.password, uow)
    access_token = create_access_token({"sub": str(user.id), "roles": roles})
    _set_auth_cookie(response, access_token)

    return SessionResponse(message="Login exitoso. Sesión iniciada.")


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
    response: Response,
    uow: SqlModelUnitOfWork = Depends(get_uow),
) -> SessionResponse:
    user, roles = AuthService.autenticar(
        form_data.username, form_data.password, uow)
    access_token = create_access_token({"sub": str(user.id), "roles": roles})
    _set_auth_cookie(response, access_token)

    return SessionResponse(message="Login exitoso. Sesión iniciada.")


@router.post(
    "/logout",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión y limpiar cookie",
)
async def logout(response: Response) -> SessionResponse:
    _clear_auth_cookie(response)
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
    uow: SqlModelUnitOfWork = Depends(get_uow),
) -> UsuarioResponse:
    return AuthService.crear_usuario(request, uow)


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
    uow: SqlModelUnitOfWork = Depends(get_uow),
) -> UsuarioResponse:
    return AuthService.obtener_usuario_con_roles(current_user.id, uow)


# ─── Rutas de administración (RBAC: solo ADMIN) ───────────────────────────


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
    uow: SqlModelUnitOfWork = Depends(get_uow),
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
    uow: SqlModelUnitOfWork = Depends(get_uow),
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
    uow: SqlModelUnitOfWork = Depends(get_uow),
) -> AdminActionResponse:
    return AuthService.toggle_usuario_activo(usuario_id, activo=True, uow=uow)
