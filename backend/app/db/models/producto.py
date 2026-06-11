from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal

from sqlalchemy import Column, Enum as SAEnum, Numeric, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import SQLModel, Field, Relationship

from app.db.models.enums import TipoProducto


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
    precio_venta: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column("precio", Numeric(12, 2), nullable=False, server_default="0"),
        description="Precio de venta manual del producto"
    )
    precio_costo_calculado: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 2), nullable=False, server_default="0"),
        description="Costo calculado del producto a partir de sus ingredientes"
    )
    descuento_porcentaje: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(5, 2), nullable=False, server_default="0"),
        description="Descuento porcentual del producto"
    )
    tipo_producto: TipoProducto = Field(
        sa_column=Column(
            SAEnum(TipoProducto, name="tipo_producto_enum", native_enum=False),
            nullable=False,
            server_default=TipoProducto.FABRICADO.value,
        ),
        description="Tipo operativo del producto"
    )
    imagenes_url: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(Text()), nullable=True),
        description="Lista de URLs de imagenes del producto"
    )
    unidad_venta_id: Optional[int] = Field(
        default=None,
        foreign_key="unidad_medida.id",
        description="Unidad de venta del producto"
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
    disponible: bool = Field(
        default=True,
        description="Disponibilidad lógica del producto en catálogo"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Fecha de eliminación lógica (soft delete)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de creación"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de última actualización"
    )

    producto_categorias: list["ProductoCategoria"] = Relationship(back_populates="producto")
    ingredientes: list["ProductoDetalle"] = Relationship(back_populates="producto")

    def __repr__(self) -> str:
        return f"<Producto id={self.id} nombre={self.nombre} precio_venta={self.precio_venta}>"

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def precio(self) -> Decimal:
        return self.precio_venta

    @precio.setter
    def precio(self, value: Decimal | float | int) -> None:
        self.precio_venta = Decimal(str(value))
