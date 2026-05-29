from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal

from sqlalchemy import Column, Enum as SAEnum, Numeric
from sqlmodel import SQLModel, Field, Relationship

from app.db.models.enums import UnidadMedida


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
