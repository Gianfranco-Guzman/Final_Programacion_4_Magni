from sqlmodel import select

from app.core.repositories.base import BaseRepository
from app.db.models import MovimientoStockIngrediente


class MovimientoStockIngredienteRepository(BaseRepository):
    def save(self, movimiento: MovimientoStockIngrediente) -> MovimientoStockIngrediente:
        return self.add(movimiento)

    def list_by_pedido_id(self, pedido_id: int) -> list[MovimientoStockIngrediente]:
        statement = select(MovimientoStockIngrediente).where(
            MovimientoStockIngrediente.pedido_id == pedido_id
        )
        return list(self.session.exec(statement).all())
