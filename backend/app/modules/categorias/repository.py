from sqlmodel import select

from app.core.base_repository import BaseRepository
from app.modules.categorias.model import Categoria
from app.modules.productos.model import Producto, ProductoCategoria


class CategoriaRepository(BaseRepository):
    def get_by_id(self, categoria_id: int) -> Categoria | None:
        statement = select(Categoria).where(Categoria.id == categoria_id)
        return self.session.exec(statement).first()

    def list_all_ordered(self) -> list[Categoria]:
        statement = select(Categoria).order_by(Categoria.nombre)
        return list(self.session.exec(statement).all())

    def list_root_active_ordered(self) -> list[Categoria]:
        statement = select(Categoria).where(
            (Categoria.parent_id.is_(None)) & (Categoria.deleted_at.is_(None))
        ).order_by(Categoria.nombre)
        return list(self.session.exec(statement).all())

    def list_filtered(self, *, parent_id: int | None = None, incluir_baja: bool = False) -> list[Categoria]:
        statement = select(Categoria)
        if not incluir_baja:
            statement = statement.where(Categoria.deleted_at.is_(None))
        if parent_id is not None:
            statement = statement.where(Categoria.parent_id == parent_id)
        statement = statement.order_by(Categoria.nombre)
        return list(self.session.exec(statement).all())

    def count_filtered(self, *, parent_id: int | None = None, incluir_baja: bool = False) -> int:
        return len(self.list_filtered(parent_id=parent_id, incluir_baja=incluir_baja))

    def list_by_ids(self, categoria_ids: list[int]) -> list[Categoria]:
        if not categoria_ids:
            return []
        statement = select(Categoria).where(Categoria.id.in_(categoria_ids))
        return list(self.session.exec(statement).all())

    def get_active_by_name(self, nombre: str) -> Categoria | None:
        statement = select(Categoria).where(
            (Categoria.nombre == nombre) & (Categoria.deleted_at.is_(None))
        )
        return self.session.exec(statement).first()

    def get_active_by_name_excluding_id(self, nombre: str, categoria_id: int) -> Categoria | None:
        statement = select(Categoria).where(
            (Categoria.nombre == nombre)
            & (Categoria.deleted_at.is_(None))
            & (Categoria.id != categoria_id)
        )
        return self.session.exec(statement).first()

    def get_active_parent(self, parent_id: int) -> Categoria | None:
        statement = select(Categoria).where(
            (Categoria.id == parent_id) & (Categoria.deleted_at.is_(None))
        )
        return self.session.exec(statement).first()

    def parent_creates_cycle(self, categoria_id: int, parent_id: int) -> bool:
        current_parent = self.get_by_id(parent_id)
        current_parent_id = current_parent.parent_id if current_parent else None
        visited: set[int] = set()

        while current_parent_id is not None:
            if current_parent_id == categoria_id:
                return True
            if current_parent_id in visited:
                return False
            visited.add(current_parent_id)
            current_parent = self.get_by_id(current_parent_id)
            current_parent_id = current_parent.parent_id if current_parent else None

        return False

    def has_active_products(self, categoria_id: int) -> bool:
        statement = (
            select(Producto)
            .join(ProductoCategoria, ProductoCategoria.producto_id == Producto.id)
            .where(
                (ProductoCategoria.categoria_id == categoria_id)
                & (Producto.deleted_at.is_(None))
            )
        )
        return self.session.exec(statement).first() is not None

    def has_active_children(self, categoria_id: int) -> bool:
        statement = select(Categoria).where(
            (Categoria.parent_id == categoria_id) & (Categoria.deleted_at.is_(None))
        )
        return self.session.exec(statement).first() is not None
