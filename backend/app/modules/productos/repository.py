from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.base_repository import BaseRepository
from app.modules.productos.model import Producto, ProductoCategoria, ProductoDetalle


class ProductoRepository(BaseRepository):
    def _base_with_relations(self):
        return select(Producto).options(
            selectinload(Producto.producto_categorias).selectinload(ProductoCategoria.categoria),
            selectinload(Producto.ingredientes).selectinload(ProductoDetalle.ingrediente),
        )

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

    def list_for_catalog(
        self,
        *,
        categoria_id: int | None = None,
        search: str | None = None,
        disponible: bool | None = None,
        incluir_baja: bool = False,
        page: int = 1,
        size: int = 20,
    ) -> list[Producto]:
        statement = self._base_with_relations()

        if not incluir_baja:
            statement = statement.where(Producto.deleted_at.is_(None))

        if categoria_id is not None:
            statement = statement.join(
                ProductoCategoria,
                ProductoCategoria.producto_id == Producto.id,
            ).where(ProductoCategoria.categoria_id == categoria_id)

        if search:
            term = f"%{search.lower()}%"
            statement = statement.where(
                (Producto.nombre.ilike(term)) | (Producto.codigo.ilike(term))
            )

        if disponible is True:
            statement = statement.where(Producto.disponible.is_(True))
        elif disponible is False:
            statement = statement.where(Producto.disponible.is_(False))

        statement = statement.order_by(Producto.id).offset((page - 1) * size).limit(size)
        return list(self.session.exec(statement).unique().all())

    def count_for_catalog(
        self,
        *,
        categoria_id: int | None = None,
        search: str | None = None,
        disponible: bool | None = None,
        incluir_baja: bool = False,
    ) -> int:
        return len(
            self.list_for_catalog(
                categoria_id=categoria_id,
                search=search,
                disponible=disponible,
                incluir_baja=incluir_baja,
                page=1,
                size=100000,
            )
        )

    def list_for_export(self, *, search: str | None = None, limit: int = 1000) -> list[Producto]:
        statement = self._base_with_relations().where(Producto.deleted_at.is_(None)).order_by(Producto.created_at.desc()).limit(limit)
        if search:
            term = f"%{search.lower()}%"
            statement = statement.where(
                (Producto.nombre.ilike(term)) | (Producto.codigo.ilike(term))
            )
        return list(self.session.exec(statement).unique().all())

    def get_by_id_with_relations(self, producto_id: int) -> Producto | None:
        statement = self._base_with_relations().where(Producto.id == producto_id)
        return self.session.exec(statement).first()

    def get_active_by_id_with_relations(self, producto_id: int) -> Producto | None:
        statement = self._base_with_relations().where(
            (Producto.id == producto_id) & (Producto.deleted_at.is_(None))
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

        if existing_relations:
            self.session.flush()

        for categoria_data in categorias_data:
            self.add(ProductoCategoria(producto_id=producto_id, **categoria_data))

    def replace_ingredientes(self, producto_id: int, ingredientes_data: list[dict]) -> None:
        existing_relations = self.session.exec(
            select(ProductoDetalle).where(ProductoDetalle.producto_id == producto_id)
        ).all()
        for relation in existing_relations:
            self.delete(relation)

        if existing_relations:
            self.session.flush()

        for ingrediente_data in ingredientes_data:
            self.add(ProductoDetalle(producto_id=producto_id, **ingrediente_data))

    def save(self, producto: Producto) -> Producto:
        return self.add(producto)
