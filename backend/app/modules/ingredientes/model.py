from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Enum as SAEnum, Numeric
from sqlmodel import SQLModel, Field, Relationship

from app.core.enums import TipoMovimientoIngrediente, UnidadMedida


class UnidadMedidaCatalogo(SQLModel, table=True):

    __tablename__ = "unidad_medida"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True, max_length=50)
    simbolo: str = Field(index=True, unique=True, max_length=10)
    tipo: str = Field(max_length=20)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Ingrediente(SQLModel, table=True):

    __tablename__ = "ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(
        index=True,
        unique=True,
        max_length=100,
        description="Nombre único del ingrediente"
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Descripción del ingrediente"
    )
    es_alergeno: bool = Field(
        default=False,
        description="Indica si el ingrediente es un alérgeno común"
    )
    unidad_medida: UnidadMedida = Field(
        sa_column=Column(
            SAEnum(UnidadMedida, name="unidad_medida_enum", native_enum=False),
            nullable=False,
            server_default=UnidadMedida.UNIDAD.value,
        ),
        description="Unidad de medida base del ingrediente"
    )
    stock_actual: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 3), nullable=False, server_default="0"),
        description="Stock actual disponible del ingrediente"
    )
    stock_minimo: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 3), nullable=False, server_default="0"),
        description="Stock mínimo deseado del ingrediente"
    )
    costo_unitario: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 2), nullable=False, server_default="0"),
        description="Costo unitario del ingrediente según su unidad base"
    )
    permite_fraccion: bool = Field(
        default=False,
        description="Indica si el ingrediente permite cantidades fraccionadas"
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

    productos: list["ProductoDetalle"] = Relationship(back_populates="ingrediente")
    movimientos_stock: list["MovimientoStockIngrediente"] = Relationship(back_populates="ingrediente")

    def __repr__(self) -> str:
        return f"<Ingrediente id={self.id} nombre={self.nombre}>"


class MovimientoStockIngrediente(SQLModel, table=True):
    __tablename__ = "movimiento_stock_ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    ingrediente_id: int = Field(foreign_key="ingrediente.id", index=True)
    pedido_id: Optional[int] = Field(default=None, foreign_key="pedido.id", index=True)
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    movimiento_referencia_id: Optional[int] = Field(default=None, foreign_key="movimiento_stock_ingrediente.id")
    tipo_movimiento: TipoMovimientoIngrediente = Field(
        sa_column=Column(
            SAEnum(TipoMovimientoIngrediente, name="tipo_movimiento_ingrediente_enum", native_enum=False),
            nullable=False,
        )
    )
    cantidad: Decimal = Field(
        sa_column=Column(Numeric(12, 3), nullable=False),
        description="Cantidad positiva del movimiento según la unidad del ingrediente",
    )
    stock_anterior: Decimal = Field(sa_column=Column(Numeric(12, 3), nullable=False))
    stock_posterior: Decimal = Field(sa_column=Column(Numeric(12, 3), nullable=False))
    observacion: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    ingrediente: Optional["Ingrediente"] = Relationship(back_populates="movimientos_stock")
