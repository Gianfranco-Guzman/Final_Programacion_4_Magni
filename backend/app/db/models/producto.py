from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Producto(SQLModel, table=True):

    __tablename__ = "producto"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(
        index=True,
        max_length=150,
        description="Nombre del producto"
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Descripcion detallada del producto"
    )
    precio: float = Field(
        gt=0,
        description="Precio del producto (debe ser mayor a 0)"
    )
    stock_cantidad: int = Field(
        ge=0,
        description="Cantidad en stock disponible"
    )
    categoria_id: int = Field(
        foreign_key="categoria.id",
        description="ID de la categoría"
    )
    codigo: str = Field(
        index=True,
        max_length=50,
        description="Código único entre productos activos (SKU). Unicidad validada a nivel servicio."
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Fecha de eliminación lógica (soft delete)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de última actualización"
    )

    categoria: Optional["Categoria"] = Relationship(back_populates="productos")

    def __repr__(self) -> str:
        return f"<Producto id={self.id} nombre={self.nombre} precio={self.precio}>"

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
