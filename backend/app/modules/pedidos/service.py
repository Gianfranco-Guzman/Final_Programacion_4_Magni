from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import select, col

from app.core.dependencies import user_has_any_role
from app.db.models import ProductoIngrediente, MovimientoStockIngrediente, Ingrediente
from app.db.models.enums import TipoMovimientoIngrediente
from app.db.models.direccion_entrega import DireccionEntrega
from app.db.models.forma_pago import FormaPago
from app.db.models.pedido import Pedido
from app.db.models.detalle_pedido import DetallePedido
from app.db.models.historial_estado_pedido import HistorialEstadoPedido
from app.db.models.producto import Producto
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.ingredientes.stock_service import IngredienteStockService
from app.modules.pedidos.schemas import PedidoCreate

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
    def _consolidar_consumo_ingredientes_desde_detalles(
        detalles: list[DetallePedido],
        uow: SqlModelUnitOfWork,
    ) -> dict[int, Decimal]:
        session = uow.session
        consumo_por_ingrediente: dict[int, Decimal] = {}

        for detalle in detalles:
            producto = session.exec(
                select(Producto)
                .options(selectinload(Producto.ingredientes).selectinload(ProductoIngrediente.ingrediente))
                .where(Producto.id == detalle.producto_id)
            ).first()
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
        session = uow.session
        ingrediente_ids = list(consumo_por_ingrediente.keys())
        ingredientes = session.exec(
            select(Ingrediente).where(Ingrediente.id.in_(ingrediente_ids))
        ).all()
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
        session = uow.session
        movimientos = session.exec(
            select(MovimientoStockIngrediente).where(MovimientoStockIngrediente.pedido_id == pedido.id)
        ).all()

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

        ingredientes = session.exec(
            select(Ingrediente).where(Ingrediente.id.in_(list(pendientes.keys())))
        ).all()
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
        session = uow.session

        direccion = session.exec(
            select(DireccionEntrega).where(
                (DireccionEntrega.id == data.direccion_entrega_id)
                & (DireccionEntrega.usuario_id == current_user.id)
                & (DireccionEntrega.deleted_at.is_(None))
            )
        ).first()
        if not direccion:
            raise HTTPException(
                status_code=404,
                detail="Dirección de entrega no encontrada o no pertenece al usuario",
            )

        forma_pago = session.exec(
            select(FormaPago).where(
                (FormaPago.id == data.forma_pago_id) & (FormaPago.activo == True)
            )
        ).first()
        if not forma_pago:
            raise HTTPException(status_code=404, detail="Forma de pago no encontrada o inactiva")

        now = datetime.now(timezone.utc)
        total = Decimal("0")
        detalles_data = []

        for item in data.items:
            producto = session.exec(
                select(Producto).where(
                    (Producto.id == item.producto_id)
                    & (Producto.deleted_at.is_(None))
                    & (Producto.disponible == True)
                )
            ).first()
            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto con id {item.producto_id} no encontrado o no disponible",
                )
            if producto.stock_cantidad < item.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Stock insuficiente para '{producto.nombre}': "
                        f"disponible {producto.stock_cantidad}, solicitado {item.cantidad}"
                    ),
                )
            subtotal = (Decimal(str(producto.precio)) * Decimal(str(item.cantidad))).quantize(Decimal("0.01"))
            total += subtotal
            detalles_data.append({
                "producto_id": producto.id,
                "cantidad": item.cantidad,
                "precio_unitario_snapshot": producto.precio,
                "nombre_producto_snapshot": producto.nombre,
                "subtotal": subtotal,
            })

        total = total.quantize(Decimal("0.01"))

        pedido = Pedido(
            usuario_id=current_user.id,
            direccion_entrega_id=data.direccion_entrega_id,
            forma_pago_id=data.forma_pago_id,
            estado_actual="PENDIENTE",
            total=total,
            notas=data.notas,
            created_at=now,
            updated_at=now,
        )
        session.add(pedido)
        uow.flush()

        for detalle_data in detalles_data:
            detalle = DetallePedido(pedido_id=pedido.id, **detalle_data)
            session.add(detalle)

        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_anterior=None,
            estado_nuevo="PENDIENTE",
            fecha=now,
            usuario_id=current_user.id,
        )
        session.add(historial)
        uow.flush()

        return pedido

    @staticmethod
    def listar_pedidos(
        current_user: Usuario,
        uow: SqlModelUnitOfWork,
        estado: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Pedido]:
        session = uow.session
        es_privilegiado = user_has_any_role(current_user, PRIVILEGED_ROLES, session)

        stmt = select(Pedido)
        if not es_privilegiado:
            stmt = stmt.where(Pedido.usuario_id == current_user.id)
        if estado:
            stmt = stmt.where(Pedido.estado_actual == estado)

        offset = (page - 1) * size
        stmt = stmt.order_by(col(Pedido.created_at).desc()).offset(offset).limit(size)

        return list(session.exec(stmt).all())

    @staticmethod
    def obtener_pedido(pedido_id: int, current_user: Usuario, uow: SqlModelUnitOfWork) -> Pedido:
        session = uow.session
        pedido = session.get(Pedido, pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        es_privilegiado = user_has_any_role(current_user, PRIVILEGED_ROLES, session)
        if not es_privilegiado and pedido.usuario_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tenés acceso a este pedido")

        # Trigger lazy loads while session is open
        _ = list(pedido.detalles)
        _ = list(pedido.historial)

        return pedido

    @staticmethod
    def avanzar_estado(
        pedido_id: int,
        current_user: Usuario,
        uow: SqlModelUnitOfWork,
        observacion: Optional[str] = None,
    ) -> Pedido:
        session = uow.session
        pedido = session.get(Pedido, pedido_id)
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
        session.add(historial)

        if estado_actual == "PENDIENTE" and siguiente == "CONFIRMADO":
            _ = list(pedido.detalles)
            PedidoService._descontar_stock_por_confirmacion(pedido, uow)

        pedido.estado_actual = siguiente
        pedido.updated_at = datetime.now(timezone.utc)
        session.add(pedido)
        uow.flush()

        return pedido

    @staticmethod
    def cancelar_pedido(
        pedido_id: int,
        current_user: Usuario,
        uow: SqlModelUnitOfWork,
        observacion: Optional[str] = None,
    ) -> Pedido:
        session = uow.session
        pedido = session.get(Pedido, pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        es_privilegiado = user_has_any_role(current_user, PRIVILEGED_ROLES, session)
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
        session.add(historial)

        PedidoService._revertir_stock_por_cancelacion(pedido, uow)

        pedido.estado_actual = "CANCELADO"
        pedido.updated_at = datetime.now(timezone.utc)
        session.add(pedido)
        uow.flush()

        return pedido
