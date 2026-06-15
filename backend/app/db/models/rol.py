from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.db.models.usuario import UsuarioRol


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
