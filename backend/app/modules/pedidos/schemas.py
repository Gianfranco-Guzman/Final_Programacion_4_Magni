from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ItemCarrito(BaseModel):
    producto_id: int = Field(ge=1, description="ID de producto válido")
    cantidad: int = Field(gt=0, description="Cantidad debe ser mayor a 0")


class PedidoCreate(BaseModel):
    direccion_entrega_id: int = Field(ge=1, description="Dirección de entrega requerida")
    forma_pago_id: int = Field(ge=1, description="Forma de pago requerida")
    items: list[ItemCarrito] = Field(min_length=1, description="Al menos un ítem requerido")
    notas: Optional[str] = Field(None, max_length=500)


class DetallePedidoRead(BaseModel):
    id: int
    pedido_id: int
    producto_id: int
    cantidad: int
    precio_unitario_snapshot: float
    nombre_producto_snapshot: str
    subtotal: float
    personalizacion: Optional[list[int]] = None

    model_config = {"from_attributes": True}


class HistorialEstadoPedidoRead(BaseModel):
    id: int
    pedido_id: int
    estado_anterior: Optional[str]
    estado_nuevo: str
    fecha: datetime
    usuario_id: int
    observacion: Optional[str]

    model_config = {"from_attributes": True}


class PedidoRead(BaseModel):
    id: int
    usuario_id: int
    direccion_entrega_id: int
    forma_pago_id: int
    estado_actual: str
    subtotal: float = 0
    descuento: float = 0
    costo_envio: float = 0
    total: float
    notas: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PedidoDetalle(PedidoRead):
    detalles: list[DetallePedidoRead] = []
    historial: list[HistorialEstadoPedidoRead] = []


class AvanzarEstadoRequest(BaseModel):
    observacion: Optional[str] = Field(None, max_length=255)


class CancelarPedidoRequest(BaseModel):
    observacion: str = Field(..., min_length=1, max_length=255)
