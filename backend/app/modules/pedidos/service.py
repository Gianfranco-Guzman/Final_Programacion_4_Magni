from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException

from app.db.models import Ingrediente
from app.db.models.enums import TipoMovimientoIngrediente
from app.db.models.pedido import Pedido
from app.db.models.detalle_pedido import DetallePedido
from app.db.models.historial_estado_pedido import HistorialEstadoPedido
from app.db.models.producto import Producto
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.ingredientes.stock_service import IngredienteStockService
from app.modules.pedidos.realtime import PedidoRealtimePublisher
from app.modules.pedidos.schemas import PedidoCreate
from app.modules.productos.service import ProductoService

VALID_TRANSITIONS: dict[str, list[str]] = {
    "PENDIENTE": ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP", "CANCELADO"],
    "EN_PREP": ["EN_CAMINO"],
    "EN_CAMINO": ["ENTREGADO"],
    "ENTREGADO": [],
    "CANCELADO": [],
}

NEXT_STATE: dict[str, str] = {
    "PENDIENTE": "CONFIRMADO",
    "CONFIRMADO": "EN_PREP",
    "EN_PREP": "EN_CAMINO",
    "EN_CAMINO": "ENTREGADO",
}

PRIVILEGED_ROLES = ["ADMIN", "PEDIDOS"]


class PedidoService:

    @staticmethod
    def _consolidar_items(items) -> dict[int, int]:
        items_consolidados: dict[int, int] = {}
        for item in items:
            items_consolidados[item.producto_id] = items_consolidados.get(item.producto_id, 0) + item.cantidad
        return items_consolidados

    @staticmethod
    def _cargar_productos_para_pedido(
        producto_ids: list[int],
        uow: SqlModelUnitOfWork,
    ) -> dict[int, Producto]:
        productos = uow.productos.list_available_by_ids_with_ingredientes(producto_ids)
        return {producto.id: producto for producto in productos}

    @staticmethod
    def _preparar_detalles_y_consumo(
        items_consolidados: dict[int, int],
        uow: SqlModelUnitOfWork,
    ) -> tuple[list[dict], dict[int, Decimal], Decimal]:
        productos_map = PedidoService._cargar_productos_para_pedido(list(items_consolidados.keys()), uow)
        detalles_data: list[dict] = []
        consumo_por_ingrediente: dict[int, Decimal] = {}
        total = Decimal("0")

        for producto_id, cantidad_solicitada in items_consolidados.items():
            producto = productos_map.get(producto_id)
            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto con id {producto_id} no encontrado o no disponible",
                )

            if not producto.ingredientes:
                raise HTTPException(
                    status_code=400,
                    detail=f"El producto '{producto.nombre}' no tiene detalle de ingredientes configurado",
                )

            precio_unitario = ProductoService.calcular_precio_final(producto)
            subtotal = (precio_unitario * Decimal(str(cantidad_solicitada))).quantize(Decimal("0.01"))
            total += subtotal
            detalles_data.append(
                {
                    "producto_id": producto.id,
                    "cantidad": cantidad_solicitada,
                    "precio_unitario_snapshot": precio_unitario,
                    "nombre_producto_snapshot": producto.nombre,
                    "subtotal": subtotal,
                }
            )

            for receta_detalle in producto.ingredientes:
                cantidad_total = Decimal(str(receta_detalle.cantidad)) * Decimal(str(cantidad_solicitada))
                consumo_por_ingrediente[receta_detalle.ingrediente_id] = (
                    consumo_por_ingrediente.get(receta_detalle.ingrediente_id, Decimal("0")) + cantidad_total
                )

        return detalles_data, consumo_por_ingrediente, total.quantize(Decimal("0.01"))

    @staticmethod
    def _consolidar_consumo_ingredientes_desde_detalles(
        detalles: list[DetallePedido],
        uow: SqlModelUnitOfWork,
    ) -> dict[int, Decimal]:
        consumo_por_ingrediente: dict[int, Decimal] = {}

        for detalle in detalles:
            producto = uow.productos.get_by_id_with_relations(detalle.producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail=f"Producto con id {detalle.producto_id} no encontrado")

            for receta_detalle in producto.ingredientes:
                cantidad_total = Decimal(str(receta_detalle.cantidad)) * Decimal(str(detalle.cantidad))
                consumo_por_ingrediente[receta_detalle.ingrediente_id] = (
                    consumo_por_ingrediente.get(receta_detalle.ingrediente_id, Decimal("0")) + cantidad_total
                )

        return consumo_por_ingrediente

    @staticmethod
    def _validar_stock_para_consumo(
        consumo_por_ingrediente: dict[int, Decimal],
        uow: SqlModelUnitOfWork,
    ) -> dict[int, Ingrediente]:
        ingrediente_ids = list(consumo_por_ingrediente.keys())
        ingredientes = uow.ingredientes.list_by_ids(ingrediente_ids)
        ingredientes_map = {ingrediente.id: ingrediente for ingrediente in ingredientes}

        for ingrediente_id, cantidad_requerida in consumo_por_ingrediente.items():
            ingrediente = ingredientes_map.get(ingrediente_id)
            if not ingrediente:
                raise HTTPException(status_code=404, detail=f"Ingrediente con id {ingrediente_id} no encontrado")
            if Decimal(str(ingrediente.stock_actual)) < cantidad_requerida:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Stock insuficiente para '{ingrediente.nombre}': "
                        f"disponible {ingrediente.stock_actual}, requerido {cantidad_requerida}"
                    ),
                )

        return ingredientes_map

    @staticmethod
    def _descontar_stock_por_confirmacion(pedido: Pedido, uow: SqlModelUnitOfWork) -> None:
        detalles = list(pedido.detalles)
        consumo_por_ingrediente = PedidoService._consolidar_consumo_ingredientes_desde_detalles(detalles, uow)
        ingredientes_map = PedidoService._validar_stock_para_consumo(consumo_por_ingrediente, uow)

        for ingrediente_id, cantidad_requerida in consumo_por_ingrediente.items():
            ingrediente = ingredientes_map[ingrediente_id]
            IngredienteStockService.consumir_por_pedido(
                ingrediente,
                cantidad_requerida,
                pedido.id,
                uow,
                observacion=f"Consumo por confirmación del pedido #{pedido.id}",
            )

    @staticmethod
    def _revertir_stock_por_cancelacion(pedido: Pedido, uow: SqlModelUnitOfWork) -> None:
        movimientos = uow.movimientos_stock_ingredientes.list_by_pedido_id(pedido.id)

        consumos: dict[int, Decimal] = {}
        reversas: dict[int, Decimal] = {}
        for movimiento in movimientos:
            if movimiento.tipo_movimiento == TipoMovimientoIngrediente.CONSUMO_PEDIDO:
                consumos[movimiento.ingrediente_id] = consumos.get(movimiento.ingrediente_id, Decimal("0")) + Decimal(str(movimiento.cantidad))
            elif movimiento.tipo_movimiento == TipoMovimientoIngrediente.REVERSA_CANCELACION:
                reversas[movimiento.ingrediente_id] = reversas.get(movimiento.ingrediente_id, Decimal("0")) + Decimal(str(movimiento.cantidad))

        pendientes = {
            ingrediente_id: cantidad_consumida - reversas.get(ingrediente_id, Decimal("0"))
            for ingrediente_id, cantidad_consumida in consumos.items()
            if cantidad_consumida - reversas.get(ingrediente_id, Decimal("0")) > 0
        }
        if not pendientes:
            return

        ingredientes = uow.ingredientes.list_by_ids(list(pendientes.keys()))
        ingredientes_map = {ingrediente.id: ingrediente for ingrediente in ingredientes}

        for ingrediente_id, cantidad in pendientes.items():
            ingrediente = ingredientes_map[ingrediente_id]
            IngredienteStockService.revertir_por_cancelacion(
                ingrediente,
                cantidad,
                pedido.id,
                uow,
                observacion=f"Reversa por cancelación del pedido #{pedido.id}",
            )

    @staticmethod
    def crear_pedido(data: PedidoCreate, current_user: Usuario, uow: SqlModelUnitOfWork) -> Pedido:
        direccion = uow.direcciones.get_active_for_user(data.direccion_entrega_id, current_user.id)
        if not direccion:
            raise HTTPException(
                status_code=404,
                detail="Dirección de entrega no encontrada o no pertenece al usuario",
            )

        forma_pago = uow.formas_pago.get_active_by_id(data.forma_pago_id)
        if not forma_pago:
            raise HTTPException(status_code=404, detail="Forma de pago no encontrada o inactiva")

        now = datetime.now(timezone.utc)
        items_consolidados = PedidoService._consolidar_items(data.items)
        detalles_data, consumo_por_ingrediente, subtotal = PedidoService._preparar_detalles_y_consumo(
            items_consolidados,
            uow,
        )
        PedidoService._validar_stock_para_consumo(consumo_por_ingrediente, uow)
        descuento = Decimal("0.00")
        costo_envio = Decimal("0.00")
        total = (subtotal - descuento + costo_envio).quantize(Decimal("0.01"))

        pedido = Pedido(
            usuario_id=current_user.id,
            direccion_entrega_id=data.direccion_entrega_id,
            forma_pago_id=data.forma_pago_id,
            estado_actual="PENDIENTE",
            subtotal=subtotal,
            descuento=descuento,
            costo_envio=costo_envio,
            total=total,
            notas=data.notas,
            created_at=now,
            updated_at=now,
        )
        uow.pedidos.save(pedido)
        uow.flush()

        for detalle_data in detalles_data:
            detalle = DetallePedido(pedido_id=pedido.id, **detalle_data)
            uow.pedidos.add_detalle(detalle)

        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_anterior=None,
            estado_nuevo="PENDIENTE",
            fecha=now,
            usuario_id=current_user.id,
        )
        uow.pedidos.add_historial(historial)
        uow.flush()
        PedidoRealtimePublisher.queue_event(uow, "PEDIDO_CREATED", pedido.id)

        return pedido

    @staticmethod
    def listar_pedidos(
        current_user: Usuario,
        uow: SqlModelUnitOfWork,
        estado: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Pedido]:
        es_privilegiado = uow.roles.user_has_any_role(current_user.id, PRIVILEGED_ROLES)
        return uow.pedidos.list_pedidos(
            usuario_id=None if es_privilegiado else current_user.id,
            estado=estado,
            page=page,
            size=size,
        )

    @staticmethod
    def obtener_pedido(pedido_id: int, current_user: Usuario, uow: SqlModelUnitOfWork) -> Pedido:
        pedido = uow.pedidos.get_by_id_with_detalles_historial(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        es_privilegiado = uow.roles.user_has_any_role(current_user.id, PRIVILEGED_ROLES)
        if not es_privilegiado and pedido.usuario_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tenés acceso a este pedido")

        return pedido

    @staticmethod
    def avanzar_estado(
        pedido_id: int,
        current_user: Usuario,
        uow: SqlModelUnitOfWork,
        observacion: Optional[str] = None,
    ) -> Pedido:
        pedido = uow.pedidos.get_by_id_with_detalles(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        estado_actual = pedido.estado_actual
        if estado_actual not in NEXT_STATE:
            raise HTTPException(
                status_code=422,
                detail=f"El pedido en estado '{estado_actual}' no puede avanzar de estado",
            )

        siguiente = NEXT_STATE[estado_actual]

        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_anterior=estado_actual,
            estado_nuevo=siguiente,
            fecha=datetime.now(timezone.utc),
            usuario_id=current_user.id,
            observacion=observacion,
        )
        uow.pedidos.add_historial(historial)

        if estado_actual == "PENDIENTE" and siguiente == "CONFIRMADO":
            PedidoService._descontar_stock_por_confirmacion(pedido, uow)

        pedido.estado_actual = siguiente
        pedido.updated_at = datetime.now(timezone.utc)
        uow.pedidos.save(pedido)
        uow.flush()
        PedidoRealtimePublisher.queue_event(uow, "PEDIDO_UPDATED", pedido.id)

        return pedido

    @staticmethod
    def cancelar_pedido(
        pedido_id: int,
        current_user: Usuario,
        uow: SqlModelUnitOfWork,
        observacion: Optional[str] = None,
    ) -> Pedido:
        pedido = uow.pedidos.get_by_id_with_detalles(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        es_privilegiado = uow.roles.user_has_any_role(current_user.id, PRIVILEGED_ROLES)
        if not es_privilegiado and pedido.usuario_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tenés acceso a este pedido")

        if "CANCELADO" not in VALID_TRANSITIONS.get(pedido.estado_actual, []):
            raise HTTPException(
                status_code=422,
                detail=f"El pedido en estado '{pedido.estado_actual}' no puede cancelarse",
            )

        estado_anterior = pedido.estado_actual
        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_anterior=estado_anterior,
            estado_nuevo="CANCELADO",
            fecha=datetime.now(timezone.utc),
            usuario_id=current_user.id,
            observacion=observacion,
        )
        uow.pedidos.add_historial(historial)

        PedidoService._revertir_stock_por_cancelacion(pedido, uow)

        pedido.estado_actual = "CANCELADO"
        pedido.updated_at = datetime.now(timezone.utc)
        uow.pedidos.save(pedido)
        uow.flush()
        PedidoRealtimePublisher.queue_event(uow, "PEDIDO_CANCELLED", pedido.id)

        return pedido
