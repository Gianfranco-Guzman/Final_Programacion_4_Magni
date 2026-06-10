from sqlmodel import select

from app.core.repositories.base import BaseRepository
from app.db.models import Ingrediente, ProductoDetalle


class IngredienteRepository(BaseRepository):
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
