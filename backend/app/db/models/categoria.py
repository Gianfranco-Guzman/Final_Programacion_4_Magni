from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Categoria(SQLModel, table=True):
    """Modelo de categorías de productos: Pizza, Bebidas, Postres, etc."""

    __tablename__ = "categoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(
        index=True,
        unique=True,
        max_length=100,
        description="Nombre único de la categoría"
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Descripción de la categoría"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de última actualización"
    )

    # Relación con productos
    productos: list["Producto"] = Relationship(back_populates="categoria")

    def __repr__(self) -> str:
        return f"<Categoria id={self.id} nombre={self.nombre}>"
