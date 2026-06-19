from decimal import Decimal

from sqlmodel import select, func

from app.core.repositories.base import BaseRepository
from app.db.models import MovimientoStockIngrediente
from app.db.models.enums import TipoMovimientoIngrediente


class MovimientoStockIngredienteRepository(BaseRepository):
    def save(self, movimiento: MovimientoStockIngrediente) -> MovimientoStockIngrediente:
        return self.add(movimiento)

    def get_by_id(self, movimiento_id: int) -> MovimientoStockIngrediente | None:
        return self.session.get(MovimientoStockIngrediente, movimiento_id)

    def list_by_pedido_id(self, pedido_id: int) -> list[MovimientoStockIngrediente]:
        statement = select(MovimientoStockIngrediente).where(
            MovimientoStockIngrediente.pedido_id == pedido_id
        )
        return list(self.session.exec(statement).all())

    def list_entradas_by_usuario(self, usuario_id: int) -> list[MovimientoStockIngrediente]:
        statement = (
            select(MovimientoStockIngrediente)
            .where(
                MovimientoStockIngrediente.usuario_id == usuario_id,
                MovimientoStockIngrediente.tipo_movimiento.in_([
                    TipoMovimientoIngrediente.ENTRADA_STOCK,
                    TipoMovimientoIngrediente.CORRECCION_ENTRADA,
                ]),
            )
            .order_by(MovimientoStockIngrediente.created_at.desc())
            .limit(100)
        )
        return list(self.session.exec(statement).all())

    def total_corregido(self, movimiento_referencia_id: int) -> Decimal:
        statement = select(func.coalesce(func.sum(MovimientoStockIngrediente.cantidad), 0)).where(
            MovimientoStockIngrediente.movimiento_referencia_id == movimiento_referencia_id,
            MovimientoStockIngrediente.tipo_movimiento == TipoMovimientoIngrediente.CORRECCION_ENTRADA,
        )
        return Decimal(str(self.session.exec(statement).one()))
