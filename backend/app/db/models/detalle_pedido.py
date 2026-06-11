from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Integer, Numeric
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import SQLModel, Field, Relationship


class DetallePedido(SQLModel, table=True):

    __tablename__ = "detalle_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id", index=True)
    producto_id: int = Field(foreign_key="producto.id")
    cantidad: int = Field(gt=0)
    precio_unitario_snapshot: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    nombre_producto_snapshot: str = Field(max_length=150)
    subtotal: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    personalizacion: Optional[list[int]] = Field(default=None, sa_column=Column(ARRAY(Integer()), nullable=True))

    pedido: Optional["Pedido"] = Relationship(back_populates="detalles")

    def __repr__(self) -> str:
        return f"<DetallePedido pedido_id={self.pedido_id} producto='{self.nombre_producto_snapshot}' x{self.cantidad}>"

    @property
    def precio_snapshot(self) -> Decimal:
        return self.precio_unitario_snapshot

    @property
    def nombre_snapshot(self) -> str:
        return self.nombre_producto_snapshot

    @property
    def subtotal_snap(self) -> Decimal:
        return self.subtotal
