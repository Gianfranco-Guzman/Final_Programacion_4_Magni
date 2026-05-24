from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class DetallePedido(SQLModel, table=True):

    __tablename__ = "detalle_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id", index=True)
    producto_id: int = Field(foreign_key="producto.id")
    cantidad: int = Field(gt=0)
    precio_unitario_snapshot: float = Field(ge=0)
    nombre_producto_snapshot: str = Field(max_length=150)
    subtotal: float = Field(ge=0)

    pedido: Optional["Pedido"] = Relationship(back_populates="detalles")

    def __repr__(self) -> str:
        return f"<DetallePedido pedido_id={self.pedido_id} producto='{self.nombre_producto_snapshot}' x{self.cantidad}>"
