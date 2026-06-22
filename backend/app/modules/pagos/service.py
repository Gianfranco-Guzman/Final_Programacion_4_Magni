from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.db.models.pago import Pago
from app.db.models.usuario import Usuario
from app.db.unit_of_work import UnitOfWork
from app.modules.pagos.schemas import PagoCreateRequest
from app.modules.pedidos.realtime import PedidoRealtimePublisher
from app.modules.pedidos.service import PedidoService


class PagosService:
    @staticmethod
    def _get_sdk():
        settings = get_settings()
        if not settings.mp_access_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="MercadoPago no configurado en el backend",
            )

        try:
            import mercadopago
        except ImportError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SDK de MercadoPago no instalado en el backend",
            ) from exc

        return mercadopago.SDK(settings.mp_access_token)

    @staticmethod
    def _get_payment_request_options(idempotency_key: str):
        import mercadopago

        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {"x-idempotency-key": idempotency_key}
        return request_options

    @staticmethod
    def _ensure_pedido_can_be_paid(pedido_id: int, current_user: Usuario, uow: UnitOfWork):
        pedido = PedidoService.obtener_pedido(pedido_id, current_user, uow)
        if pedido.estado_actual != "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se puede iniciar un pago para pedidos en estado PENDIENTE",
            )

        forma_pago = uow.formas_pago.get_by_id(pedido.forma_pago_id)
        if not forma_pago or forma_pago.codigo != "MERCADOPAGO":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El pedido no tiene configurada la forma de pago MERCADOPAGO",
            )
        return pedido

    @staticmethod
    def crear_pago(data: PagoCreateRequest, current_user: Usuario, uow: UnitOfWork) -> Pago:
        pedido = PagosService._ensure_pedido_can_be_paid(data.pedido_id, current_user, uow)

        existing_pago = uow.pagos.get_by_pedido_id(pedido.id)
        if existing_pago and existing_pago.mp_status in {"pending", "approved", "in_process", "authorized"}:
            return existing_pago

        idempotency_key = str(uuid4())
        external_reference = f"pedido-{pedido.id}"
        sdk = PagosService._get_sdk()

        payment_data = {
            "transaction_amount": float(pedido.total),
            "token": data.token,
            "description": f"Pedido #{pedido.id}",
            "installments": data.installments,
            "payment_method_id": data.payment_method_id,
            "issuer_id": data.issuer_id,
            "payer": {
                "email": data.payer_email or current_user.email,
            },
            "external_reference": external_reference,
            "notification_url": get_settings().mp_notification_url or None,
        }

        request_options = PagosService._get_payment_request_options(idempotency_key)
        payment_response = sdk.payment().create(payment_data, request_options)
        response_data = payment_response.get("response", {})
        status_code = payment_response.get("status")
        if status_code not in {200, 201}:
            detail = response_data.get("message") or response_data.get("error") or "No se pudo crear el pago"
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

        pago = existing_pago or Pago(
            pedido_id=pedido.id,
            external_reference=external_reference,
            idempotency_key=idempotency_key,
            mp_status="pending",
            transaction_amount=Decimal("0"),
        )
        pago.mp_payment_id = response_data.get("id")
        pago.mp_status = response_data.get("status", "pending")
        pago.mp_status_detail = response_data.get("status_detail")
        pago.transaction_amount = Decimal(str(response_data.get("transaction_amount", pedido.total)))
        pago.payment_method_id = response_data.get("payment_method_id")
        pago.external_reference = response_data.get("external_reference") or external_reference
        pago.idempotency_key = idempotency_key
        pago.updated_at = datetime.now(timezone.utc)
        uow.pagos.save(pago)
        uow.flush()
        return pago

    @staticmethod
    def obtener_pago(pedido_id: int, current_user: Usuario, uow: UnitOfWork) -> Pago:
        PedidoService.obtener_pedido(pedido_id, current_user, uow)
        pago = uow.pagos.get_by_pedido_id(pedido_id)
        if not pago:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado para el pedido")
        return pago

    @staticmethod
    def _resolve_mp_payment_id(*, topic: str | None, data_id: str | None, query_id: str | None) -> int:
        raw_id = data_id or query_id
        if not raw_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Webhook sin payment id")
        try:
            return int(raw_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="payment id inválido") from exc

    @staticmethod
    def procesar_webhook(*, topic: str | None, data_id: str | None, query_id: str | None, uow: UnitOfWork) -> Pago:
        mp_payment_id = PagosService._resolve_mp_payment_id(topic=topic, data_id=data_id, query_id=query_id)
        sdk = PagosService._get_sdk()
        payment_response = sdk.payment().get(mp_payment_id)
        response_data = payment_response.get("response", {})
        if payment_response.get("status") != 200:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="No se pudo consultar el pago en MercadoPago")

        external_reference = response_data.get("external_reference")
        if not external_reference:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pago sin external_reference")

        pago = uow.pagos.get_by_external_reference(external_reference)
        if pago is None:
            pedido_id = int(external_reference.replace("pedido-", ""))
            pago = Pago(
                pedido_id=pedido_id,
                external_reference=external_reference,
                idempotency_key=str(uuid4()),
                mp_status="pending",
                transaction_amount=Decimal("0"),
            )

        pago.mp_payment_id = response_data.get("id")
        pago.mp_status = response_data.get("status", "pending")
        pago.mp_status_detail = response_data.get("status_detail")
        pago.transaction_amount = Decimal(str(response_data.get("transaction_amount", 0)))
        pago.payment_method_id = response_data.get("payment_method_id")
        pago.updated_at = datetime.now(timezone.utc)
        uow.pagos.save(pago)
        uow.flush()

        pedido = uow.pedidos.get_by_id_with_detalles(pago.pedido_id)
        if pedido and pago.mp_status == "approved" and pedido.estado_actual == "PENDIENTE":
            actor = uow.usuarios.get_by_email("admin@foodstore.com") or uow.usuarios.get_by_id(pedido.usuario_id)
            if actor is not None:
                PedidoService.avanzar_estado(
                    pedido.id,
                    actor,
                    uow,
                    observacion="Confirmado automáticamente por webhook de MercadoPago",
                )

        PedidoRealtimePublisher.queue_event(uow, "PAGO_CONFIRMED", pago.pedido_id)

        return pago
