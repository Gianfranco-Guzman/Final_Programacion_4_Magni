from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class UsuarioRol(SQLModel, table=True):

    __tablename__ = "usuario_rol"

    usuario_id: int = Field(foreign_key="usuario.id", primary_key=True)
    rol_id: int = Field(foreign_key="rol.id", primary_key=True)
    asignado_por_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    expires_at: Optional[datetime] = Field(default=None)


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
    apellido: str = Field(
        default="",
        max_length=80,
        description="Apellido del usuario"
    )
    celular: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Celular de contacto del usuario"
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

    roles: list["Rol"] = Relationship(
        back_populates="usuarios",
        link_model=UsuarioRol,
        sa_relationship_kwargs={
            "primaryjoin": "Usuario.id == UsuarioRol.usuario_id",
            "secondaryjoin": "UsuarioRol.rol_id == Rol.id",
        },
    )
    direcciones: list["DireccionEntrega"] = Relationship(back_populates="usuario")

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email} nombre={self.nombre}>"


class Rol(SQLModel, table=True):

    __tablename__ = "rol"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(
        index=True,
        unique=True,
        max_length=50,
        description="Nombre unico del rol (ADMIN, CLIENT, STOCK, PEDIDOS)"
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Descripcion del rol"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de creacion"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de ultima actualización"
    )

    usuarios: list["Usuario"] = Relationship(
        back_populates="roles",
        link_model=UsuarioRol,
        sa_relationship_kwargs={
            "primaryjoin": "Rol.id == UsuarioRol.rol_id",
            "secondaryjoin": "UsuarioRol.usuario_id == Usuario.id",
        },
    )

    def __repr__(self) -> str:
        return f"<Rol id={self.id} nombre={self.nombre}>"


class RefreshToken(SQLModel, table=True):

    __tablename__ = "refresh_token"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    token_hash: str = Field(index=True, unique=True, max_length=128)
    jti: str = Field(index=True, unique=True, max_length=100)
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    revoked_at: Optional[datetime] = Field(default=None)
