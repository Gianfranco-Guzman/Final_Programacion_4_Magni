from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.repositories.base import BaseRepository
from app.db.models import Producto, ProductoCategoria, ProductoDetalle


class ProductoRepository(BaseRepository):
    def get_by_id(self, producto_id: int) -> Producto | None:
        statement = select(Producto).where(Producto.id == producto_id)
        return self.session.exec(statement).first()

    def get_active_by_id(self, producto_id: int) -> Producto | None:
        statement = select(Producto).where(
            (Producto.id == producto_id) & (Producto.deleted_at.is_(None))
        )
        return self.session.exec(statement).first()

    def get_active_by_codigo(self, codigo: str) -> Producto | None:
        statement = select(Producto).where(
            (Producto.codigo == codigo) & (Producto.deleted_at.is_(None))
        )
        return self.session.exec(statement).first()

    def get_active_by_codigo_excluding_id(self, codigo: str, producto_id: int) -> Producto | None:
        statement = select(Producto).where(
            (Producto.codigo == codigo)
            & (Producto.deleted_at.is_(None))
            & (Producto.id != producto_id)
        )
        return self.session.exec(statement).first()

    def list_by_ids_with_ingredientes(self, producto_ids: list[int]) -> list[Producto]:
        if not producto_ids:
            return []
        statement = (
            select(Producto)
            .options(selectinload(Producto.ingredientes).selectinload(ProductoDetalle.ingrediente))
            .where(Producto.id.in_(producto_ids))
        )
        return list(self.session.exec(statement).all())

    def list_available_by_ids_with_ingredientes(self, producto_ids: list[int]) -> list[Producto]:
        if not producto_ids:
            return []
        statement = (
            select(Producto)
            .options(selectinload(Producto.ingredientes).selectinload(ProductoDetalle.ingrediente))
            .where(
                Producto.id.in_(producto_ids),
                Producto.deleted_at.is_(None),
                Producto.disponible == True,
            )
        )
        return list(self.session.exec(statement).all())

    def get_by_id_with_relations(self, producto_id: int) -> Producto | None:
        statement = (
            select(Producto)
            .options(
                selectinload(Producto.producto_categorias).selectinload(ProductoCategoria.categoria),
                selectinload(Producto.ingredientes).selectinload(ProductoDetalle.ingrediente),
            )
            .where(Producto.id == producto_id)
        )
        return self.session.exec(statement).first()

    def list_detalles_by_producto_id(self, producto_id: int) -> list[ProductoDetalle]:
        statement = select(ProductoDetalle).where(ProductoDetalle.producto_id == producto_id)
        return list(self.session.exec(statement).all())

    def replace_categorias(self, producto_id: int, categorias_data: list[dict]) -> None:
        existing_relations = self.session.exec(
            select(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id)
        ).all()
        for relation in existing_relations:
            self.delete(relation)

        for categoria_data in categorias_data:
            self.add(ProductoCategoria(producto_id=producto_id, **categoria_data))

    def replace_ingredientes(self, producto_id: int, ingredientes_data: list[dict]) -> None:
        existing_relations = self.session.exec(
            select(ProductoDetalle).where(ProductoDetalle.producto_id == producto_id)
        ).all()
        for relation in existing_relations:
            self.delete(relation)

        for ingrediente_data in ingredientes_data:
            self.add(ProductoDetalle(producto_id=producto_id, **ingrediente_data))

    def save(self, producto: Producto) -> Producto:
        return self.add(producto)
