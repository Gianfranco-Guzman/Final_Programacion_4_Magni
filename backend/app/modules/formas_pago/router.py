from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.core.dependencies import require_role
from app.db.base import get_session
from app.db.models.forma_pago import FormaPago
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.modules.formas_pago.schemas import FormaPagoCreate, FormaPagoRead, FormaPagoUpdate
from app.modules.formas_pago.service import FormaPagoService

router = APIRouter(tags=["formas_pago"])


@router.get(
    "/",
    response_model=list[FormaPagoRead],
    summary="Listar formas de pago activas",
)
def listar_formas_pago(session: Session = Depends(get_session)):
    formas = session.exec(
        select(FormaPago).where(FormaPago.activo == True).order_by(FormaPago.nombre)
    ).all()
    return [FormaPagoRead.model_validate(f) for f in formas]


@router.get(
    "/{forma_pago_id}",
    response_model=FormaPagoRead,
    summary="Obtener forma de pago por ID",
)
def obtener_forma_pago(forma_pago_id: int, session: Session = Depends(get_session)):
    forma_pago = session.get(FormaPago, forma_pago_id)
    if not forma_pago:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Forma de pago no encontrada")
    return FormaPagoRead.model_validate(forma_pago)


@router.post(
    "/",
    response_model=FormaPagoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear forma de pago",
)
def crear_forma_pago(
    data: FormaPagoCreate,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN"])),
):
    forma_pago = FormaPagoService.crear(data, uow)
    return FormaPagoRead.model_validate(forma_pago)


@router.put(
    "/{forma_pago_id}",
    response_model=FormaPagoRead,
    summary="Actualizar forma de pago",
)
def actualizar_forma_pago(
    forma_pago_id: int,
    data: FormaPagoUpdate,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN"])),
):
    forma_pago = FormaPagoService.actualizar(forma_pago_id, data, uow)
    return FormaPagoRead.model_validate(forma_pago)
