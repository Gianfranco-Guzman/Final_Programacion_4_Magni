from typing import Any

from fastapi import APIRouter, Depends, Query, Request, status

from app.core.dependencies import get_current_user
from app.modules.auth.model import Usuario
from app.db.unit_of_work import UnitOfWork, get_uow
from app.modules.pagos.schemas import PagoCreateRequest, PagoResponse, WebhookResponse
from app.modules.pagos.service import PagosService

router = APIRouter(prefix="/pagos", tags=["pagos"])


@router.post(
    "/crear",
    response_model=PagoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear pago MercadoPago para un pedido",
)
def crear_pago(
    data: PagoCreateRequest,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> PagoResponse:
    pago = PagosService.crear_pago(data, current_user, uow)
    return PagoResponse.model_validate(pago)


@router.get(
    "/{pedido_id}",
    response_model=PagoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener pago asociado a un pedido",
)
def obtener_pago(
    pedido_id: int,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> PagoResponse:
    pago = PagosService.obtener_pago(pedido_id, current_user, uow)
    return PagoResponse.model_validate(pago)


@router.post(
    "/webhook",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Webhook/IPN de MercadoPago",
)
async def webhook_mercadopago(
    request: Request,
    topic: str | None = Query(default=None),
    type: str | None = Query(default=None),
    id: str | None = Query(default=None),
    uow: UnitOfWork = Depends(get_uow),
) -> WebhookResponse:
    body: dict[str, Any] = {}
    try:
        body = await request.json()
    except Exception:
        body = {}

    data_id = None
    if isinstance(body.get("data"), dict):
        data_id = body["data"].get("id")

    resolved_topic = topic or type
    if resolved_topic and resolved_topic != "payment":
        return WebhookResponse(status="ignored")

    PagosService.procesar_webhook(topic=resolved_topic, data_id=data_id, query_id=id, uow=uow)
    return WebhookResponse(status="ok")
