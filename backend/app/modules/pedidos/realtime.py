from anyio import from_thread
from sqlmodel import Session

from app.core.websocket import manager
from app.db.models.pedido import Pedido
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.pedidos.schemas import PedidoDetalle

STAFF_ROLES = ["ADMIN", "PEDIDOS"]


class PedidoRealtimePublisher:

    @staticmethod
    def queue_event(uow: SqlModelUnitOfWork, event: str, pedido_id: int) -> None:
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

        payload = {
            "pedido": PedidoDetalle.model_validate(pedido).model_dump(mode="json")
        }
        await manager.broadcast_to_roles(STAFF_ROLES, event, payload)
        await manager.broadcast_to_order(pedido_id, event, payload)
