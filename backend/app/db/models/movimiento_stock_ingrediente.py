from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Enum as SAEnum, Numeric
from sqlmodel import SQLModel, Field, Relationship

from app.db.models.enums import TipoMovimientoIngrediente


class MovimientoStockIngrediente(SQLModel, table=True):
    __tablename__ = "movimiento_stock_ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    ingrediente_id: int = Field(foreign_key="ingrediente.id", index=True)
    pedido_id: Optional[int] = Field(default=None, foreign_key="pedido.id", index=True)
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
