from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import select

from app.db.models import Categoria
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.Categoria.schemas import CategoriaCreate, CategoriaUpdate


class CategoriaService:

    @staticmethod
    def crear_categoria(data: CategoriaCreate, uow: SqlModelUnitOfWork) -> Categoria:
        session = uow.session
        existing = session.exec(
            select(Categoria).where(Categoria.nombre == data.nombre)
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe una categoría con el nombre '{data.nombre}'",
            )

        now = datetime.now(timezone.utc)
        categoria = Categoria(
            **data.model_dump(),
            created_at=now,
            updated_at=now,
        )
        session.add(categoria)
        uow.flush()
        return categoria

    @staticmethod
    def actualizar_categoria(
        categoria_id: int,
        data: CategoriaUpdate,
        uow: SqlModelUnitOfWork,
    ) -> Categoria:
        session = uow.session
        categoria = session.exec(
            select(Categoria).where(Categoria.id == categoria_id)
        ).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        if data.nombre is not None and data.nombre != categoria.nombre:
            conflict = session.exec(
                select(Categoria).where(
                    (Categoria.nombre == data.nombre) & (Categoria.id != categoria_id)
                )
            ).first()
            if conflict:
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe una categoría con el nombre '{data.nombre}'",
                )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(categoria, field, value)
        categoria.updated_at = datetime.now(timezone.utc)

        session.add(categoria)
        uow.flush()
        return categoria

    @staticmethod
    def eliminar_categoria(categoria_id: int, uow: SqlModelUnitOfWork) -> Categoria:
        session = uow.session
        categoria = session.exec(
            select(Categoria).where(Categoria.id == categoria_id)
        ).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        # Verificar si tiene productos asociados
        from app.db.models import Producto
        productos = session.exec(
            select(Producto).where(
                (Producto.categoria_id == categoria_id) & (Producto.deleted_at.is_(None))
            )
        ).all()
        if productos:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar la categoría porque tiene productos asociados",
            )

        session.delete(categoria)
        uow.flush()
        return categoria
