from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class UsuarioRol(SQLModel, table=True):

    __tablename__ = "usuario_rol"

    usuario_id: int = Field(foreign_key="usuario.id", primary_key=True)
    rol_id: int = Field(foreign_key="rol.id", primary_key=True)


class Usuario(SQLModel, table=True):

    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(
        index=True,
        unique=True,
        max_length=255,
        description="Email único del usuario"
    )
    password_hash: str = Field(
        max_length=255,
        description="Hash bcrypt de la contraseña"
    )
    nombre: str = Field(
        max_length=100,
        description="Nombre completo del usuario"
    )
    is_active: bool = Field(
        default=True,
        description="Estado activo/inactivo del usuario"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de creación"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de última actualización"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Fecha de eliminación lógica (soft delete)"
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email} nombre={self.nombre}>"
