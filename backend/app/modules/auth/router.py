from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from app.db.base import get_session
from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.core.config import get_settings
from app.db.models.usuario import Usuario
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
    }
)
async def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Autentica un usuario y retorna un JWT access token.

    - **email**: Email del usuario
    - **password**: Contraseña (mínimo 8 caracteres)

    Retorna:
    - **access_token**: JWT para autenticación
    - **token_type**: "bearer"
    - **expires_in**: Segundos hasta expiración
    """
    # Autenticar usuario
    user = AuthService.autenticar(request.email, request.password, session)

    # Crear JWT token
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
    }
)
async def register(
    request: RegisterRequest,
    session: Session = Depends(get_session)
) -> UsuarioResponse:
    """
    Registra un nuevo usuario en el sistema con rol CLIENT.

    - **email**: Email único
    - **password**: Contraseña (mínimo 8 caracteres)
    - **nombre**: Nombre completo (mínimo 2 caracteres)

    Retorna:
    - **id**: ID del usuario creado
    - **email**: Email del usuario
    - **nombre**: Nombre del usuario
    - **roles**: Roles asignados (incluye CLIENT por defecto)
    """
    usuario = AuthService.crear_usuario(request, session)

    return UsuarioResponse(
        id=usuario.id,
        email=usuario.email,
        nombre=usuario.nombre,
        is_active=usuario.is_active,
        roles=[],  # Se agrega rol CLIENT en el servicio
    )


@router.get(
    "/me",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario actual",
    responses={
        200: {"description": "Información del usuario autenticado"},
        401: {"description": "No autenticado o token inválido"},
    }
)
async def get_me(
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> UsuarioResponse:
    """
    Retorna la información del usuario actualmente autenticado.

    Headers requeridos:
    - **Authorization**: Bearer <access_token>

    Retorna:
    - **id**: ID del usuario
    - **email**: Email del usuario
    - **nombre**: Nombre del usuario
    - **roles**: Roles del usuario
    """
    return UsuarioResponse(
        id=current_user.id,
        email=current_user.email,
        nombre=current_user.nombre,
        is_active=current_user.is_active,
        roles=[],  # TODO: Cargar desde relación N:M en FASE 2
    )
