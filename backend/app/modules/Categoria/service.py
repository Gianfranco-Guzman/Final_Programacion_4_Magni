from datetime import datetime, timezone

from fastapi import HTTPException, status
from app.db.models import Categoria
from app.db.unit_of_work import UnitOfWork
from app.modules.Categoria.schemas import CategoriaCreate, CategoriaUpdate


class CategoriaService:
    @staticmethod
    def _get_categoria(categoria_id: int, uow: UnitOfWork) -> Categoria:
        categoria = uow.categorias.get_by_id(categoria_id)

        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        return categoria

    @staticmethod
    def _validar_nombre_unico(
        nombre: str,
        uow: UnitOfWork,
        categoria_id: int | None = None,
    ) -> None:
        if categoria_id is None:
            existing = uow.categorias.get_active_by_name(nombre)
        else:
            existing = uow.categorias.get_active_by_name_excluding_id(nombre, categoria_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una categoría activa con el nombre '{nombre}'",
            )

    @staticmethod
    def _validar_parent(
        parent_id: int | None,
        uow: UnitOfWork,
        categoria_id: int | None = None,
    ) -> None:
        if parent_id is None:
            return

        if categoria_id is not None and parent_id == categoria_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Una categoría no puede ser padre de sí misma",
            )

        parent = uow.categorias.get_active_parent(parent_id)

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría padre no encontrada",
            )

        if categoria_id is None:
            return

        if uow.categorias.parent_creates_cycle(categoria_id, parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría padre generaría un ciclo jerárquico",
            )

    @staticmethod
    def crear_categoria(data: CategoriaCreate, uow: UnitOfWork) -> Categoria:
        CategoriaService._validar_nombre_unico(data.nombre, uow)
        CategoriaService._validar_parent(data.parent_id, uow)

        now = datetime.now(timezone.utc)
        categoria = Categoria(
            **data.model_dump(),
            created_at=now,
            updated_at=now,
        )
        uow.categorias.add(categoria)
        uow.flush()
        uow.refresh(categoria)
        return categoria

    @staticmethod
    def actualizar_categoria(
        categoria_id: int,
        data: CategoriaUpdate,
        uow: UnitOfWork,
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

        uow.categorias.add(categoria)
        uow.flush()
        uow.refresh(categoria)
        return categoria

    @staticmethod
    def dar_de_baja(categoria_id: int, uow: UnitOfWork) -> Categoria:
        categoria = CategoriaService._get_categoria(categoria_id, uow)
        if categoria.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría ya está dada de baja",
            )

        if uow.categorias.has_active_products(categoria_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede dar de baja la categoría porque tiene productos activos",
            )

        if uow.categorias.has_active_children(categoria_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede dar de baja la categoría porque tiene subcategorías activas",
            )

        now = datetime.now(timezone.utc)
        categoria.deleted_at = now
        categoria.updated_at = now
        uow.categorias.add(categoria)
        uow.flush()
        uow.refresh(categoria)
        return categoria

    @staticmethod
    def reactivar_categoria(categoria_id: int, uow: UnitOfWork) -> Categoria:
        categoria = CategoriaService._get_categoria(categoria_id, uow)
        if categoria.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría no está dada de baja",
            )

        if categoria.parent_id is not None:
            parent = uow.categorias.get_by_id(categoria.parent_id)
            if not parent or parent.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No se puede reactivar si la categoría padre está dada de baja",
                )

        CategoriaService._validar_nombre_unico(categoria.nombre, uow, categoria_id)

        categoria.deleted_at = None
        categoria.updated_at = datetime.now(timezone.utc)
        uow.categorias.add(categoria)
        uow.flush()
        uow.refresh(categoria)
        return categoria

    @staticmethod
    def eliminar_categoria(categoria_id: int, uow: UnitOfWork) -> Categoria:
        return CategoriaService.dar_de_baja(categoria_id, uow)
