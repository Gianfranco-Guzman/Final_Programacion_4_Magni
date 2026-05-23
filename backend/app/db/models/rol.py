from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


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
        default_factory=datetime.utcnow,
        description="Fecha de creacion"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de ultima actualización"
    )

    # Relaciones
    usuarios: List["Usuario"] = Relationship(back_populates="roles", link_model="UsuarioRol")

    def __repr__(self) -> str:
        return f"<Rol id={self.id} nombre={self.nombre}>"
