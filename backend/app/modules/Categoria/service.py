from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import select

from app.db.models import Categoria, Producto, ProductoCategoria
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.Categoria.schemas import CategoriaCreate, CategoriaUpdate


class CategoriaService:
    @staticmethod
    def _get_categoria(categoria_id: int, uow: SqlModelUnitOfWork) -> Categoria:
        categoria = uow.session.exec(
            select(Categoria).where(Categoria.id == categoria_id)
        ).first()

        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        return categoria

    @staticmethod
    def _validar_nombre_unico(
        nombre: str,
        uow: SqlModelUnitOfWork,
        categoria_id: int | None = None,
    ) -> None:
        statement = select(Categoria).where(
            (Categoria.nombre == nombre) & (Categoria.deleted_at.is_(None))
        )

        if categoria_id is not None:
            statement = statement.where(Categoria.id != categoria_id)

        existing = uow.session.exec(statement).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una categoría activa con el nombre '{nombre}'",
            )

    @staticmethod
    def _validar_parent(
        parent_id: int | None,
        uow: SqlModelUnitOfWork,
        categoria_id: int | None = None,
    ) -> None:
        if parent_id is None:
            return

        if categoria_id is not None and parent_id == categoria_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Una categoría no puede ser padre de sí misma",
            )

        parent = uow.session.exec(
            select(Categoria).where(
                (Categoria.id == parent_id) & (Categoria.deleted_at.is_(None))
            )
        ).first()

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría padre no encontrada",
            )

        if categoria_id is None:
            return

        current_parent_id = parent.parent_id
        visited: set[int] = set()
        while current_parent_id is not None:
            if current_parent_id == categoria_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La categoría padre generaría un ciclo jerárquico",
                )
            if current_parent_id in visited:
                break
            visited.add(current_parent_id)
            current_parent = uow.session.exec(
                select(Categoria).where(Categoria.id == current_parent_id)
            ).first()
            current_parent_id = current_parent.parent_id if current_parent else None

    @staticmethod
    def crear_categoria(data: CategoriaCreate, uow: SqlModelUnitOfWork) -> Categoria:
        CategoriaService._validar_nombre_unico(data.nombre, uow)
        CategoriaService._validar_parent(data.parent_id, uow)

        now = datetime.now(timezone.utc)
        categoria = Categoria(
            **data.model_dump(),
            created_at=now,
            updated_at=now,
        )
        uow.session.add(categoria)
        uow.flush()
        uow.refresh(categoria)
        return categoria

    @staticmethod
    def actualizar_categoria(
        categoria_id: int,
        data: CategoriaUpdate,
        uow: SqlModelUnitOfWork,
    ) -> Categoria:
        categoria = CategoriaService._get_categoria(categoria_id, uow)

        if categoria.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede actualizar una categoría dada de baja",
            )

        if data.nombre is not None and data.nombre != categoria.nombre:
            CategoriaService._validar_nombre_unico(data.nombre, uow, categoria_id)

        update_data = data.model_dump(exclude_unset=True)
        if "parent_id" in update_data:
            CategoriaService._validar_parent(update_data["parent_id"], uow, categoria_id)

        for field, value in update_data.items():
            setattr(categoria, field, value)
        categoria.updated_at = datetime.now(timezone.utc)

        uow.session.add(categoria)
        uow.flush()
        uow.refresh(categoria)
        return categoria

    @staticmethod
    def dar_de_baja(categoria_id: int, uow: SqlModelUnitOfWork) -> Categoria:
        categoria = CategoriaService._get_categoria(categoria_id, uow)
        if categoria.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría ya está dada de baja",
            )

        producto_activo = uow.session.exec(
            select(Producto)
            .join(ProductoCategoria, ProductoCategoria.producto_id == Producto.id)
            .where(
                (ProductoCategoria.categoria_id == categoria_id)
                & (Producto.deleted_at.is_(None))
            )
        ).first()
        if producto_activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede dar de baja la categoría porque tiene productos activos",
            )

        subcategoria_activa = uow.session.exec(
            select(Categoria).where(
                (Categoria.parent_id == categoria_id) & (Categoria.deleted_at.is_(None))
            )
        ).first()
        if subcategoria_activa:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede dar de baja la categoría porque tiene subcategorías activas",
            )

        now = datetime.now(timezone.utc)
        categoria.deleted_at = now
        categoria.updated_at = now
        uow.session.add(categoria)
        uow.flush()
        uow.refresh(categoria)
        return categoria

    @staticmethod
    def reactivar_categoria(categoria_id: int, uow: SqlModelUnitOfWork) -> Categoria:
        categoria = CategoriaService._get_categoria(categoria_id, uow)
        if categoria.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría no está dada de baja",
            )

        if categoria.parent_id is not None:
            parent = uow.session.exec(
                select(Categoria).where(Categoria.id == categoria.parent_id)
            ).first()
            if not parent or parent.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No se puede reactivar si la categoría padre está dada de baja",
                )

        CategoriaService._validar_nombre_unico(categoria.nombre, uow, categoria_id)

        categoria.deleted_at = None
        categoria.updated_at = datetime.now(timezone.utc)
        uow.session.add(categoria)
        uow.flush()
        uow.refresh(categoria)
        return categoria

    @staticmethod
    def eliminar_categoria(categoria_id: int, uow: SqlModelUnitOfWork) -> Categoria:
        """Alias retrocompatible: eliminar significa soft delete."""
        return CategoriaService.dar_de_baja(categoria_id, uow)
