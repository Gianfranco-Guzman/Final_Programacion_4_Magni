from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Integer, Numeric
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import SQLModel, Field, Relationship


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
