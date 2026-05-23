from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import select

from app.db.models import Ingrediente
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.Ingrediente.schemas import IngredienteCreate, IngredienteUpdate


class IngredienteService:

    @staticmethod
    def crear_ingrediente(data: IngredienteCreate, uow: SqlModelUnitOfWork) -> Ingrediente:
        session = uow.session
        existing = session.exec(
            select(Ingrediente).where(Ingrediente.nombre == data.nombre)
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un ingrediente con el nombre '{data.nombre}'",
            )

        now = datetime.now(timezone.utc)
        ingrediente = Ingrediente(
            **data.model_dump(),
            created_at=now,
            updated_at=now,
        )
        session.add(ingrediente)
        uow.flush()
        return ingrediente

    @staticmethod
    def actualizar_ingrediente(
        ingrediente_id: int,
        data: IngredienteUpdate,
        uow: SqlModelUnitOfWork,
    ) -> Ingrediente:
        session = uow.session
        ingrediente = session.exec(
            select(Ingrediente).where(Ingrediente.id == ingrediente_id)
        ).first()
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

        if data.nombre is not None and data.nombre != ingrediente.nombre:
            conflict = session.exec(
                select(Ingrediente).where(
                    (Ingrediente.nombre == data.nombre) & (Ingrediente.id != ingrediente_id)
                )
            ).first()
            if conflict:
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe un ingrediente con el nombre '{data.nombre}'",
                )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ingrediente, field, value)
        ingrediente.updated_at = datetime.now(timezone.utc)

        session.add(ingrediente)
        uow.flush()
        return ingrediente

    @staticmethod
    def eliminar_ingrediente(ingrediente_id: int, uow: SqlModelUnitOfWork) -> Ingrediente:
        session = uow.session
        ingrediente = session.exec(
            select(Ingrediente).where(Ingrediente.id == ingrediente_id)
        ).first()
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

        # Verificar si está asociado a algún producto
        from app.db.models import ProductoIngrediente
        asociaciones = session.exec(
            select(ProductoIngrediente).where(
                ProductoIngrediente.ingrediente_id == ingrediente_id
            )
        ).all()
        if asociaciones:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el ingrediente porque está asociado a productos",
            )

        session.delete(ingrediente)
        uow.flush()
        return ingrediente
