from anyio import from_thread

from app.core.websocket import manager
from app.db.unit_of_work import UnitOfWork


class IngredienteRealtimePublisher:

    @staticmethod
    def queue_productos_updated(uow: UnitOfWork) -> None:
        uow.add_after_commit(IngredienteRealtimePublisher._emit_from_request_thread)

    @staticmethod
    def _emit_from_request_thread() -> None:
        from_thread.run(IngredienteRealtimePublisher.emit_productos_updated)

    @staticmethod
    async def emit_productos_updated() -> None:
        await manager.broadcast_to_roles(["ADMIN"], "productos_updated", {})
