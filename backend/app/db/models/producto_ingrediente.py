from typing import Optional
from decimal import Decimal

from sqlalchemy import Column, Enum as SAEnum, Numeric
from sqlmodel import SQLModel, Field, Relationship

from app.db.models.enums import UnidadMedida


class ProductoDetalle(SQLModel, table=True):

    __tablename__ = "producto_ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)

    producto_id: int = Field(
        foreign_key="producto.id",
        description="ID del producto"
    )
    ingrediente_id: int = Field(
        foreign_key="ingrediente.id",
        description="ID del ingrediente"
    )
    cantidad: Decimal = Field(
        default=Decimal("1"),
        sa_column=Column(Numeric(12, 3), nullable=False, server_default="1"),
        description="Cantidad requerida del ingrediente en el producto"
    )
    unidad_medida: UnidadMedida = Field(
        sa_column=Column(
            SAEnum(UnidadMedida, name="unidad_medida_enum", native_enum=False),
            nullable=False,
            server_default=UnidadMedida.UNIDAD.value,
        ),
        description="Unidad de medida utilizada en el detalle"
    )
    orden: int = Field(
        default=1,
        description="Orden visual del ingrediente dentro del detalle"
    )
    es_removible: bool = Field(
        default=True,
        description="Indica si el ingrediente puede removerse en una personalización"
    )
    es_opcional: bool = Field(
        default=False,
        description="Indica si el ingrediente es opcional en la composición base"
    )

    producto: Optional["Producto"] = Relationship(back_populates="ingredientes")
    ingrediente: Optional["Ingrediente"] = Relationship(back_populates="productos")
