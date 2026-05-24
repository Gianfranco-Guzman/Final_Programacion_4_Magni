from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class HistorialEstadoPedido(SQLModel, table=True):

    __tablename__ = "historial_estado_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id", index=True)
    estado_anterior: Optional[str] = Field(default=None, max_length=20)
    estado_nuevo: str = Field(max_length=20)
    fecha: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    usuario_id: int = Field(foreign_key="usuario.id")
    observacion: Optional[str] = Field(default=None, max_length=255)

    pedido: Optional["Pedido"] = Relationship(back_populates="historial")

    def __repr__(self) -> str:
        return f"<HistorialEstadoPedido pedido_id={self.pedido_id} {self.estado_anterior}→{self.estado_nuevo}>"
