from datetime import datetime, timezone

from fastapi import HTTPException
from app.db.models.forma_pago import FormaPago
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.formas_pago.schemas import FormaPagoCreate, FormaPagoUpdate


class FormaPagoService:

    @staticmethod
    def crear(data: FormaPagoCreate, uow: SqlModelUnitOfWork) -> FormaPago:
        existing = uow.formas_pago.get_by_name(data.nombre)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe una forma de pago con el nombre '{data.nombre}'",
            )

        now = datetime.now(timezone.utc)
        forma_pago = FormaPago(**data.model_dump(), created_at=now, updated_at=now)
        uow.formas_pago.add(forma_pago)
        uow.flush()
        return forma_pago

    @staticmethod
    def actualizar(forma_pago_id: int, data: FormaPagoUpdate, uow: SqlModelUnitOfWork) -> FormaPago:
        forma_pago = uow.formas_pago.get_by_id(forma_pago_id)
        if not forma_pago:
            raise HTTPException(status_code=404, detail="Forma de pago no encontrada")

        if data.nombre is not None and data.nombre != forma_pago.nombre:
            conflict = uow.formas_pago.get_by_name_excluding_id(data.nombre, forma_pago_id)
            if conflict:
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe una forma de pago con el nombre '{data.nombre}'",
                )

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(forma_pago, field, value)
        forma_pago.updated_at = datetime.now(timezone.utc)

        uow.formas_pago.add(forma_pago)
        uow.flush()
        return forma_pago
