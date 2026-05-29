from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlmodel import select

from app.db.models import Ingrediente
from app.db.models.enums import TipoMovimientoIngrediente, UnidadMedida
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.ingredientes.schemas import IngredienteCreate, IngredienteUpdate
from app.modules.ingredientes.stock_service import IngredienteStockService


class IngredienteService:

    @staticmethod
    def _validar_reglas_unidad_y_fraccion(data: IngredienteCreate | IngredienteUpdate) -> None:
        unidad = getattr(data, "unidad_medida", None)
        permite_fraccion = getattr(data, "permite_fraccion", None)

        if unidad == UnidadMedida.UNIDAD and permite_fraccion is True:
            raise HTTPException(
                status_code=400,
                detail="Un ingrediente medido en UNIDAD no puede permitir fracciones",
            )

    @staticmethod
    def _validar_reglas_unidad_y_fraccion_combinadas(
        ingrediente: Ingrediente,
        data: IngredienteUpdate,
    ) -> None:
        unidad = data.unidad_medida if data.unidad_medida is not None else ingrediente.unidad_medida
        permite_fraccion = (
            data.permite_fraccion if data.permite_fraccion is not None else ingrediente.permite_fraccion
        )
        if unidad == UnidadMedida.UNIDAD and permite_fraccion:
            raise HTTPException(
                status_code=400,
                detail="Un ingrediente medido en UNIDAD no puede permitir fracciones",
            )

    @staticmethod
    def crear_ingrediente(data: IngredienteCreate, uow: SqlModelUnitOfWork) -> Ingrediente:
        session = uow.session
        IngredienteService._validar_reglas_unidad_y_fraccion(data)
        existing = session.exec(
            select(Ingrediente).where(
                (Ingrediente.nombre == data.nombre) & (Ingrediente.deleted_at.is_(None))
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un ingrediente activo con el nombre '{data.nombre}'",
            )

        now = datetime.now(timezone.utc)
        ingrediente = Ingrediente(
            **data.model_dump(),
            created_at=now,
            updated_at=now,
        )
        session.add(ingrediente)
        uow.flush()

        if Decimal(str(ingrediente.stock_actual)) > 0:
            IngredienteStockService.registrar_movimiento(
                ingrediente,
                Decimal(str(ingrediente.stock_actual)),
                TipoMovimientoIngrediente.ALTA_MANUAL,
                uow,
                observacion="Stock inicial al crear ingrediente",
                aplicar_cambio=False,
                stock_anterior_override=Decimal("0"),
                stock_posterior_override=Decimal(str(ingrediente.stock_actual)),
            )
        return ingrediente

    @staticmethod
    def actualizar_ingrediente(
        ingrediente_id: int,
        data: IngredienteUpdate,
        uow: SqlModelUnitOfWork,
    ) -> Ingrediente:
        session = uow.session
        ingrediente = session.exec(
            select(Ingrediente).where(
                (Ingrediente.id == ingrediente_id) & (Ingrediente.deleted_at.is_(None))
            )
        ).first()
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

        if data.nombre is not None and data.nombre != ingrediente.nombre:
            conflict = session.exec(
                select(Ingrediente).where(
                    (Ingrediente.nombre == data.nombre)
                    & (Ingrediente.deleted_at.is_(None))
                    & (Ingrediente.id != ingrediente_id)
                )
            ).first()
            if conflict:
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe un ingrediente activo con el nombre '{data.nombre}'",
                )

        IngredienteService._validar_reglas_unidad_y_fraccion_combinadas(ingrediente, data)
        stock_anterior = Decimal(str(ingrediente.stock_actual))
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ingrediente, field, value)
        ingrediente.updated_at = datetime.now(timezone.utc)

        session.add(ingrediente)
        uow.flush()

        if "stock_actual" in update_data:
            stock_posterior = Decimal(str(ingrediente.stock_actual))
            diferencia = stock_posterior - stock_anterior
            if diferencia != 0:
                IngredienteStockService.registrar_movimiento(
                    ingrediente,
                    abs(diferencia),
                    TipoMovimientoIngrediente.AJUSTE_MANUAL,
                    uow,
                    observacion="Ajuste manual de stock desde administración",
                    aplicar_cambio=False,
                    stock_anterior_override=stock_anterior,
                    stock_posterior_override=stock_posterior,
                )
        return ingrediente

    @staticmethod
    def dar_de_baja(ingrediente_id: int, uow: SqlModelUnitOfWork) -> Ingrediente:
        session = uow.session
        ingrediente = session.exec(select(Ingrediente).where(Ingrediente.id == ingrediente_id)).first()
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        if ingrediente.deleted_at is not None:
            raise HTTPException(status_code=400, detail="El ingrediente ya está dado de baja")

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

        ingrediente.deleted_at = datetime.now(timezone.utc)
        ingrediente.updated_at = datetime.now(timezone.utc)
        session.add(ingrediente)
        uow.flush()
        return ingrediente

    @staticmethod
    def reactivar(ingrediente_id: int, uow: SqlModelUnitOfWork) -> Ingrediente:
        session = uow.session
        ingrediente = session.exec(select(Ingrediente).where(Ingrediente.id == ingrediente_id)).first()
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        if ingrediente.deleted_at is None:
            raise HTTPException(status_code=400, detail="El ingrediente no está dado de baja")

        conflict = session.exec(
            select(Ingrediente).where(
                (Ingrediente.nombre == ingrediente.nombre)
                & (Ingrediente.deleted_at.is_(None))
                & (Ingrediente.id != ingrediente_id)
            )
        ).first()
        if conflict:
            raise HTTPException(
                status_code=409,
                detail=f"No se puede reactivar: ya existe otro ingrediente activo con el nombre '{ingrediente.nombre}'",
            )

        ingrediente.deleted_at = None
        ingrediente.updated_at = datetime.now(timezone.utc)
        session.add(ingrediente)
        uow.flush()
        return ingrediente
