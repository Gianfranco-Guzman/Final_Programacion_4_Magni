from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import select

from app.db.models.forma_pago import FormaPago
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.formas_pago.schemas import FormaPagoCreate, FormaPagoUpdate


class FormaPagoService:

    @staticmethod
    def crear(data: FormaPagoCreate, uow: SqlModelUnitOfWork) -> FormaPago:
        session = uow.session
        existing = session.exec(
            select(FormaPago).where(FormaPago.nombre == data.nombre)
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe una forma de pago con el nombre '{data.nombre}'",
            )

        now = datetime.now(timezone.utc)
        forma_pago = FormaPago(**data.model_dump(), created_at=now, updated_at=now)
        session.add(forma_pago)
        uow.flush()
        return forma_pago

    @staticmethod
    def actualizar(forma_pago_id: int, data: FormaPagoUpdate, uow: SqlModelUnitOfWork) -> FormaPago:
        session = uow.session
        forma_pago = session.get(FormaPago, forma_pago_id)
        if not forma_pago:
            raise HTTPException(status_code=404, detail="Forma de pago no encontrada")

        if data.nombre is not None and data.nombre != forma_pago.nombre:
            conflict = session.exec(
                select(FormaPago).where(
                    (FormaPago.nombre == data.nombre) & (FormaPago.id != forma_pago_id)
                )
            ).first()
            if conflict:
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe una forma de pago con el nombre '{data.nombre}'",
                )

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(forma_pago, field, value)
        forma_pago.updated_at = datetime.now(timezone.utc)

        session.add(forma_pago)
        uow.flush()
        return forma_pago
