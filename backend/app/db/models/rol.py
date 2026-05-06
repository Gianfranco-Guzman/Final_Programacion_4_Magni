from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Rol(SQLModel, table=True):
    """Modelo de roles en el sistema: ADMIN, CLIENT, STOCK, PEDIDOS"""

    __tablename__ = "rol"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(
        index=True,
        unique=True,
        max_length=50,
        description="Nombre único del rol (ADMIN, CLIENT, STOCK, PEDIDOS)"
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Descripción del rol"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de última actualización"
    )

    def __repr__(self) -> str:
        return f"<Rol id={self.id} nombre={self.nombre}>"
