from fastapi import APIRouter, Depends, status

from app.core.config import get_settings
from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UsuarioResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login de usuario",
    responses={
        200: {"description": "Login exitoso"},
        401: {"description": "Credenciales inválidas"},
    },
)
async def login(
    request: LoginRequest,
    uow: SqlModelUnitOfWork = Depends(get_uow),
) -> TokenResponse:
    user = AuthService.autenticar(request.email, request.password, uow)
    access_token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


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
    usuario = AuthService.crear_usuario(request, uow)

    return UsuarioResponse(
        id=usuario.id,
        email=usuario.email,
        nombre=usuario.nombre,
        is_active=usuario.is_active,
        roles=[],
    )


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
