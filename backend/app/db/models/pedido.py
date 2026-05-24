from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Pedido(SQLModel, table=True):

    __tablename__ = "pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    direccion_entrega_id: int = Field(foreign_key="direccion_entrega.id")
    forma_pago_id: int = Field(foreign_key="forma_pago.id")
    estado_actual: str = Field(default="PENDIENTE", max_length=20, index=True)
    total: float = Field(default=0.0, ge=0)
    notas: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    detalles: list["DetallePedido"] = Relationship(back_populates="pedido")
    historial: list["HistorialEstadoPedido"] = Relationship(back_populates="pedido")

    def __repr__(self) -> str:
        return f"<Pedido id={self.id} estado={self.estado_actual} total={self.total}>"
