from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric
from sqlmodel import SQLModel, Field, Relationship


class Pedido(SQLModel, table=True):

    __tablename__ = "pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    tipo_entrega: str = Field(default="domicilio", max_length=10)
    direccion_entrega_id: Optional[int] = Field(default=None, foreign_key="direccion_entrega.id", nullable=True)
    forma_pago_id: int = Field(foreign_key="forma_pago.id")
    estado_actual: str = Field(default="PENDIENTE", max_length=20, index=True)
    subtotal: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 2), nullable=False, server_default="0"),
    )
    descuento: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 2), nullable=False, server_default="0"),
    )
    costo_envio: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 2), nullable=False, server_default="0"),
    )
    total: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 2), nullable=False, server_default="0"),
    )
    notas: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    detalles: list["DetallePedido"] = Relationship(back_populates="pedido")
    historial: list["HistorialEstadoPedido"] = Relationship(back_populates="pedido")

    def __repr__(self) -> str:
        return f"<Pedido id={self.id} estado={self.estado_actual} total={self.total}>"

    @property
    def estado_codigo(self) -> str:
        return self.estado_actual
