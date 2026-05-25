from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.modules.auth.schemas import RolResponse


class AdminUserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = Field(default=None, description="Email del usuario")
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(default=None, min_length=2, max_length=80)
    celular: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = Field(default=None, description="Estado activo/inactivo")


class AdminUserRolesRequest(BaseModel):
    roles: list[str] = Field(..., min_length=1, description="Lista de roles a asignar")


class AdminUserRead(BaseModel):
    id: int
    email: str
    nombre: str
    apellido: str
    celular: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    roles: list[RolResponse] = []

    model_config = {"from_attributes": True}


class AdminUserListResponse(BaseModel):
    items: list[AdminUserRead]
    total: int
    page: int
    size: int
    pages: int


class AdminUserActionResponse(BaseModel):
    message: str
    usuario: AdminUserRead
