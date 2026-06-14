from datetime import date

from fastapi import HTTPException, status

from app.db.unit_of_work import SqlModelUnitOfWork


class EstadisticasService:
    @staticmethod
    def _validar_rango(desde: date, hasta: date) -> None:
        if desde > hasta:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El rango de fechas es inválido: 'desde' no puede ser mayor que 'hasta'",
            )

    @staticmethod
    def _validar_agrupacion(agrupacion: str) -> None:
        if agrupacion not in {"day", "week", "month"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Agrupación inválida. Valores permitidos: day, week, month",
            )

    @staticmethod
    def resumen(uow: SqlModelUnitOfWork):
        return uow.estadisticas.get_resumen_kpis()

    @staticmethod
    def ventas_periodo(desde: date, hasta: date, agrupacion: str, uow: SqlModelUnitOfWork):
        EstadisticasService._validar_rango(desde, hasta)
        EstadisticasService._validar_agrupacion(agrupacion)
        return uow.estadisticas.get_ventas_periodo(desde, hasta, agrupacion)

    @staticmethod
    def productos_top(limit: int, uow: SqlModelUnitOfWork):
        return uow.estadisticas.get_productos_top(limit)

    @staticmethod
    def pedidos_por_estado(uow: SqlModelUnitOfWork):
        return uow.estadisticas.get_pedidos_por_estado()

    @staticmethod
    def ingresos(desde: date, hasta: date, uow: SqlModelUnitOfWork):
        EstadisticasService._validar_rango(desde, hasta)
        return uow.estadisticas.get_ingresos_por_forma_pago(desde, hasta)
