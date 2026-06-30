from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import col, select

from app.db.base_repository import BaseRepository
from app.modules.pedidos.model import DetallePedido, HistorialEstadoPedido, Pedido


class PedidoRepository(BaseRepository):
    def get_by_id(self, pedido_id: int) -> Pedido | None:
        return self.get(Pedido, pedido_id)

    def get_by_id_with_detalles(self, pedido_id: int) -> Pedido | None:
        statement = (
            select(Pedido)
            .options(selectinload(Pedido.detalles))
            .where(Pedido.id == pedido_id)
        )
        return self.session.exec(statement).first()

    def get_by_id_with_detalles_historial(self, pedido_id: int) -> Pedido | None:
        statement = (
            select(Pedido)
            .options(selectinload(Pedido.detalles), selectinload(Pedido.historial))
            .where(Pedido.id == pedido_id)
        )
        return self.session.exec(statement).first()

    def list_pedidos(
        self,
        *,
        usuario_id: Optional[int] = None,
        estado: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Pedido]:
        statement = select(Pedido)
        if usuario_id is not None:
            statement = statement.where(Pedido.usuario_id == usuario_id)
        if estado:
            statement = statement.where(Pedido.estado_actual == estado)

        offset = (page - 1) * size
        statement = statement.order_by(col(Pedido.created_at).desc()).offset(offset).limit(size)
        return list(self.session.exec(statement).all())

    def save(self, pedido: Pedido) -> Pedido:
        return self.add(pedido)

    def add_detalle(self, detalle: DetallePedido) -> DetallePedido:
        return self.add(detalle)

    def add_historial(self, historial: HistorialEstadoPedido) -> HistorialEstadoPedido:
        return self.add(historial)

    def list_historial_ordered_by_fecha(self, pedido_id: int) -> list[HistorialEstadoPedido]:
        statement = (
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.fecha.asc(), HistorialEstadoPedido.id.asc())
        )
        return list(self.session.exec(statement).all())
