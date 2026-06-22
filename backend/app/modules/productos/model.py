from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Enum as SAEnum, Numeric, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import SQLModel, Field, Relationship

from app.db.enums import TipoProducto, UnidadMedida


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


class ProductoCategoria(SQLModel, table=True):

    __tablename__ = "producto_categoria"

    producto_id: int = Field(
        foreign_key="producto.id",
        primary_key=True,
        description="ID del producto"
    )
    categoria_id: int = Field(
        foreign_key="categoria.id",
        primary_key=True,
        description="ID de la categoría"
    )
    es_principal: bool = Field(
        default=False,
        description="Indica si es la categoría principal del producto"
    )

    producto: Optional["Producto"] = Relationship(back_populates="producto_categorias")
    categoria: Optional["Categoria"] = Relationship(back_populates="producto_categorias")


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
