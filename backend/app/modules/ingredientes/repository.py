from decimal import Decimal

from sqlmodel import select, func

from app.db.base_repository import BaseRepository
from app.core.enums import TipoMovimientoIngrediente
from app.modules.ingredientes.model import Ingrediente, MovimientoStockIngrediente
from app.modules.productos.model import ProductoDetalle


class IngredienteRepository(BaseRepository):
    def list_all(self) -> list[Ingrediente]:
        statement = select(Ingrediente)
        return list(self.session.exec(statement).all())

    def get_by_id(self, ingrediente_id: int) -> Ingrediente | None:
        statement = select(Ingrediente).where(Ingrediente.id == ingrediente_id)
        return self.session.exec(statement).first()

    def get_active_by_id(self, ingrediente_id: int) -> Ingrediente | None:
        statement = select(Ingrediente).where(
            (Ingrediente.id == ingrediente_id) & (Ingrediente.deleted_at.is_(None))
        )
        return self.session.exec(statement).first()

    def get_active_by_name(self, nombre: str) -> Ingrediente | None:
        statement = select(Ingrediente).where(
            (Ingrediente.nombre == nombre) & (Ingrediente.deleted_at.is_(None))
        )
        return self.session.exec(statement).first()

    def get_active_by_name_excluding_id(self, nombre: str, ingrediente_id: int) -> Ingrediente | None:
        statement = select(Ingrediente).where(
            (Ingrediente.nombre == nombre)
            & (Ingrediente.deleted_at.is_(None))
            & (Ingrediente.id != ingrediente_id)
        )
        return self.session.exec(statement).first()

    def list_by_ids(self, ingrediente_ids: list[int]) -> list[Ingrediente]:
        if not ingrediente_ids:
            return []
        statement = select(Ingrediente).where(Ingrediente.id.in_(ingrediente_ids))
        return list(self.session.exec(statement).all())

    def has_product_associations(self, ingrediente_id: int) -> bool:
        statement = select(ProductoDetalle).where(ProductoDetalle.ingrediente_id == ingrediente_id)
        return self.session.exec(statement).first() is not None

    def save(self, ingrediente: Ingrediente) -> Ingrediente:
        return self.add(ingrediente)


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
