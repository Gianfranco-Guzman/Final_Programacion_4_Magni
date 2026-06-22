from anyio import from_thread
from datetime import timezone
from sqlmodel import Session

from app.core.websocket import manager
from app.db.models.pedido import Pedido
from app.db.unit_of_work import UnitOfWork
from app.modules.pedidos.schemas import HistorialEstadoPedidoRead, PedidoDetalle

STAFF_ROLES = ["ADMIN", "PEDIDOS"]


class PedidoRealtimePublisher:
    EVENT_MAP = {
        "PEDIDO_CREATED": "pedido_creado",
        "PEDIDO_UPDATED": "estado_cambiado",
        "PEDIDO_CANCELLED": "pedido_cancelado",
        "PAGO_CONFIRMED": "pago_confirmado",
    }


    @staticmethod
    def queue_event(uow: UnitOfWork, event: str, pedido_id: int) -> None:
        uow.add_after_commit(lambda: PedidoRealtimePublisher._emit_from_request_thread(uow.session, event, pedido_id))

    @staticmethod
    def _emit_from_request_thread(session: Session, event: str, pedido_id: int) -> None:
        from_thread.run(PedidoRealtimePublisher.emit_event, session, event, pedido_id)

    @staticmethod
    async def emit_event(session: Session, event: str, pedido_id: int) -> None:
        pedido = session.get(Pedido, pedido_id)
        if pedido is None:
            return

        session.refresh(pedido)
        _ = list(pedido.detalles)
        _ = list(pedido.historial)

        historial_ordenado = sorted(list(pedido.historial), key=lambda item: (item.fecha, item.id or 0))
        ultimo_historial = historial_ordenado[-1] if historial_ordenado else None
        payload_event = PedidoRealtimePublisher.EVENT_MAP.get(event, event.lower())
        timestamp = None
        if ultimo_historial is not None:
            timestamp = ultimo_historial.fecha.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

        payload = {
            "pedido": PedidoDetalle.model_validate(pedido).model_dump(mode="json"),
            "pedido_id": pedido.id,
            "estado_anterior": ultimo_historial.estado_anterior if ultimo_historial else None,
            "estado_nuevo": ultimo_historial.estado_nuevo if ultimo_historial else pedido.estado_actual,
            "usuario_id": ultimo_historial.usuario_id if ultimo_historial else pedido.usuario_id,
            "motivo": ultimo_historial.observacion if ultimo_historial else None,
            "timestamp": timestamp,
        }
        await manager.broadcast_to_roles(STAFF_ROLES, payload_event, payload)
        await manager.broadcast_to_order(pedido_id, payload_event, payload)
