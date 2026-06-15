from typing import Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status

from app.core.dependencies import get_current_user, get_current_websocket_user, get_user_role_names, require_role
from app.core.websocket import manager
from app.db.models.usuario import Usuario
from app.db.models.pedido import Pedido
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.modules.pedidos.schemas import (
    AvanzarEstadoRequest,
    CancelarPedidoRequest,
    HistorialEstadoPedidoRead,
    PedidoCreate,
    PedidoDetalle,
    PedidoRead,
)
from app.modules.pedidos.realtime import STAFF_ROLES
from app.modules.pedidos.service import PedidoService

router = APIRouter(tags=["pedidos"])


ADMIN_FEED_ACTIONS = {"subscribe-admin-feed", "unsubscribe-admin-feed"}


@router.post(
    "/",
    response_model=PedidoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear pedido desde carrito",
)
def crear_pedido(
    data: PedidoCreate,
    current_user: Usuario = Depends(get_current_user),
    uow: SqlModelUnitOfWork = Depends(get_uow),
):
    pedido = PedidoService.crear_pedido(data, current_user, uow)
    return PedidoRead.model_validate(pedido)


@router.get(
    "/",
    response_model=list[PedidoRead],
    summary="Listar pedidos (propios para CLIENT, todos para ADMIN/PEDIDOS)",
)
def listar_pedidos(
    estado: Optional[str] = Query(None, description="Filtrar por estado: PENDIENTE, CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO, CANCELADO"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    uow: SqlModelUnitOfWork = Depends(get_uow),
):
    pedidos = PedidoService.listar_pedidos(current_user, uow, estado, page, size)
    return [PedidoRead.model_validate(p) for p in pedidos]


@router.get(
    "/{pedido_id}",
    response_model=PedidoDetalle,
    summary="Obtener pedido con detalles e historial",
)
def obtener_pedido(
    pedido_id: int,
    current_user: Usuario = Depends(get_current_user),
    uow: SqlModelUnitOfWork = Depends(get_uow),
):
    pedido = PedidoService.obtener_pedido(pedido_id, current_user, uow)
    return PedidoDetalle.model_validate(pedido)


@router.get(
    "/{pedido_id}/historial",
    response_model=list[HistorialEstadoPedidoRead],
    summary="Obtener historial completo del pedido ordenado ascendente",
)
def obtener_historial_pedido(
    pedido_id: int,
    current_user: Usuario = Depends(get_current_user),
    uow: SqlModelUnitOfWork = Depends(get_uow),
):
    historial = PedidoService.obtener_historial_pedido(pedido_id, current_user, uow)
    return [HistorialEstadoPedidoRead.model_validate(item) for item in historial]


@router.patch(
    "/{pedido_id}/estado",
    response_model=PedidoRead,
    summary="Avanzar estado del pedido al siguiente en la secuencia",
)
def avanzar_estado(
    pedido_id: int,
    body: AvanzarEstadoRequest = AvanzarEstadoRequest(),
    current_user: Usuario = Depends(require_role(["ADMIN", "PEDIDOS"])),
    uow: SqlModelUnitOfWork = Depends(get_uow),
):
    pedido = PedidoService.avanzar_estado(pedido_id, current_user, uow, body.observacion)
    return PedidoRead.model_validate(pedido)


@router.patch(
    "/{pedido_id}/cancelar",
    response_model=PedidoRead,
    summary="Cancelar pedido (cliente: solo PENDIENTE/CONFIRMADO propios; ADMIN/PEDIDOS: cualquier estado cancelable)",
)
def cancelar_pedido(
    pedido_id: int,
    body: CancelarPedidoRequest,
    current_user: Usuario = Depends(get_current_user),
    uow: SqlModelUnitOfWork = Depends(get_uow),
):
    pedido = PedidoService.cancelar_pedido(pedido_id, current_user, uow, body.observacion)
    return PedidoRead.model_validate(pedido)


@router.websocket("/ws")
async def pedidos_websocket(
    websocket: WebSocket,
    current_user: Usuario = Depends(get_current_websocket_user),
    uow: SqlModelUnitOfWork = Depends(get_uow),
):
    user_roles = get_user_role_names(uow, current_user.id)
    await manager.connect(websocket, user_roles)

    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("action")
            order_id = message.get("order_id")

            if action in ADMIN_FEED_ACTIONS:
                is_staff = any(role in STAFF_ROLES for role in user_roles)
                if not is_staff:
                    await manager.send_json(websocket, "ERROR", {"detail": "No autorizado para feed admin"})
                    continue

                if action == "subscribe-admin-feed":
                    await manager.send_json(websocket, "SUBSCRIBED", {"room": "role-feed"})
                else:
                    await manager.send_json(websocket, "UNSUBSCRIBED", {"room": "role-feed"})
                continue

            if not isinstance(order_id, int):
                await manager.send_json(websocket, "ERROR", {"detail": "order_id inválido"})
                continue

            pedido = uow.pedidos.get_by_id(order_id)
            if pedido is None:
                await manager.send_json(websocket, "ERROR", {"detail": "Pedido no encontrado"})
                continue

            is_staff = any(role in STAFF_ROLES for role in user_roles)
            if not is_staff and pedido.usuario_id != current_user.id:
                await manager.send_json(websocket, "ERROR", {"detail": "No tenés acceso a este pedido"})
                continue

            if action == "subscribe-order":
                manager.join_order_room(websocket, order_id)
                await manager.send_json(websocket, "SUBSCRIBED", {"order_id": order_id})
                continue

            if action == "unsubscribe-order":
                manager.leave_order_room(websocket, order_id)
                await manager.send_json(websocket, "UNSUBSCRIBED", {"order_id": order_id})
                continue

            await manager.send_json(websocket, "ERROR", {"detail": "Acción no soportada"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
