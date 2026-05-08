from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, description="Contraseña")


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, max_length=255, description="Contraseña")
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Segundos hasta expiración")


class RolResponse(BaseModel):
    id: int
    nombre: str


class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre: str
    is_active: bool
    roles: list[RolResponse] = []

    model_config = {"from_attributes": True}
