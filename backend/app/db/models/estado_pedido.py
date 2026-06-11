from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class EstadoPedido(SQLModel, table=True):

    __tablename__ = "estado_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: Optional[str] = Field(default=None, index=True, unique=True, max_length=20)
    nombre: str = Field(index=True, unique=True, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    orden: int = Field(default=0, description="Orden de visualización en la secuencia de estados")
    es_terminal: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<EstadoPedido id={self.id} nombre={self.nombre} orden={self.orden}>"
