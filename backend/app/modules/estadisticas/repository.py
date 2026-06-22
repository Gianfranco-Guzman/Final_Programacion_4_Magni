from datetime import date, datetime, time, timezone
from decimal import Decimal

from sqlalchemy import func
from sqlmodel import select

from app.core.base_repository import BaseRepository
from app.modules.formas_pago.model import FormaPago
from app.modules.pagos.model import Pago
from app.modules.pedidos.model import DetallePedido, Pedido


class EstadisticaRepository(BaseRepository):
    @staticmethod
    def _day_range(target_date: date) -> tuple[datetime, datetime]:
        start = datetime.combine(target_date, time.min, tzinfo=timezone.utc)
        end = datetime.combine(target_date, time.max, tzinfo=timezone.utc)
        return start, end

    def get_resumen_kpis(self) -> dict:
        today = datetime.now(timezone.utc).date()
        month_start = today.replace(day=1)
        today_start, today_end = self._day_range(today)
        month_start_dt, _ = self._day_range(month_start)
        month_end_dt = datetime.now(timezone.utc)

        ventas_hoy_stmt = (
            select(func.coalesce(func.sum(Pago.transaction_amount), 0))
            .join(Pedido, Pedido.id == Pago.pedido_id)
            .where(
                Pago.mp_status == "approved",
                Pedido.estado_actual != "CANCELADO",
                Pago.updated_at >= today_start,
                Pago.updated_at <= today_end,
            )
        )
        ingresos_mes_stmt = (
            select(func.coalesce(func.sum(Pago.transaction_amount), 0))
            .join(Pedido, Pedido.id == Pago.pedido_id)
            .where(
                Pago.mp_status == "approved",
                Pedido.estado_actual != "CANCELADO",
                Pago.updated_at >= month_start_dt,
                Pago.updated_at <= month_end_dt,
            )
        )
        ticket_stmt = (
            select(func.coalesce(func.avg(Pedido.total), 0))
            .where(Pedido.estado_actual != "CANCELADO")
        )
        pedidos_activos_stmt = select(func.count()).select_from(Pedido).where(
            Pedido.estado_actual.in_(["PENDIENTE", "CONFIRMADO", "EN_PREP", "EN_CAMINO"])
        )

        return {
            "ventas_hoy": Decimal(str(self.session.exec(ventas_hoy_stmt).one() or 0)),
            "ticket_promedio": Decimal(str(self.session.exec(ticket_stmt).one() or 0)),
            "pedidos_activos": int(self.session.exec(pedidos_activos_stmt).one() or 0),
            "ingresos_mes_actual": Decimal(str(self.session.exec(ingresos_mes_stmt).one() or 0)),
        }

    def get_ventas_periodo(self, desde: date, hasta: date, agrupacion: str) -> list[dict]:
        trunc_map = {"day": "day", "week": "week", "month": "month"}
        start, _ = self._day_range(desde)
        _, end = self._day_range(hasta)

        stmt = (
            select(
                func.date_trunc(trunc_map[agrupacion], Pedido.created_at).label("periodo"),
                func.coalesce(func.sum(Pedido.total), 0).label("total_ventas"),
                func.count(Pedido.id).label("cantidad_pedidos"),
            )
            .where(
                Pedido.created_at >= start,
                Pedido.created_at <= end,
                Pedido.estado_actual != "CANCELADO",
            )
            .group_by("periodo")
            .order_by("periodo")
        )
        rows = self.session.exec(stmt).all()
        return [
            {
                "periodo": row.periodo.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if row.periodo else "",
                "total_ventas": Decimal(str(row.total_ventas or 0)),
                "cantidad_pedidos": int(row.cantidad_pedidos or 0),
            }
            for row in rows
        ]

    def get_productos_top(self, limit: int) -> list[dict]:
        stmt = (
            select(
                DetallePedido.producto_id,
                DetallePedido.nombre_producto_snapshot.label("nombre"),
                func.coalesce(func.sum(DetallePedido.cantidad), 0).label("cantidad_vendida"),
                func.coalesce(func.sum(DetallePedido.subtotal), 0).label("ingresos"),
            )
            .join(Pedido, Pedido.id == DetallePedido.pedido_id)
            .where(Pedido.estado_actual != "CANCELADO")
            .group_by(DetallePedido.producto_id, DetallePedido.nombre_producto_snapshot)
            .order_by(func.sum(DetallePedido.subtotal).desc())
            .limit(limit)
        )
        rows = self.session.exec(stmt).all()
        return [
            {
                "producto_id": int(row.producto_id),
                "nombre": row.nombre,
                "cantidad_vendida": int(row.cantidad_vendida or 0),
                "ingresos": Decimal(str(row.ingresos or 0)),
            }
            for row in rows
        ]

    def get_pedidos_por_estado(self) -> list[dict]:
        stmt = (
            select(Pedido.estado_actual.label("estado_codigo"), func.count(Pedido.id).label("cantidad"))
            .group_by(Pedido.estado_actual)
            .order_by(Pedido.estado_actual)
        )
        rows = self.session.exec(stmt).all()
        return [{"estado_codigo": row.estado_codigo, "cantidad": int(row.cantidad or 0)} for row in rows]

    def get_ingresos_por_forma_pago(self, desde: date, hasta: date) -> list[dict]:
        start, _ = self._day_range(desde)
        _, end = self._day_range(hasta)
        stmt = (
            select(
                func.coalesce(FormaPago.codigo, FormaPago.nombre).label("forma_pago_codigo"),
                func.coalesce(func.sum(Pago.transaction_amount), 0).label("total"),
                func.count(Pago.id).label("cantidad"),
            )
            .join(Pedido, Pedido.forma_pago_id == FormaPago.id)
            .join(Pago, Pago.pedido_id == Pedido.id)
            .where(
                Pago.mp_status == "approved",
                Pedido.estado_actual != "CANCELADO",
                Pago.updated_at >= start,
                Pago.updated_at <= end,
            )
            .group_by(func.coalesce(FormaPago.codigo, FormaPago.nombre))
            .order_by(func.sum(Pago.transaction_amount).desc())
        )
        rows = self.session.exec(stmt).all()
        return [
            {
                "forma_pago_codigo": row.forma_pago_codigo,
                "total": Decimal(str(row.total or 0)),
                "cantidad": int(row.cantidad or 0),
            }
            for row in rows
        ]
