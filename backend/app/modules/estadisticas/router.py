from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import require_role
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.modules.estadisticas.schemas import (
    IngresosFormaPagoItem,
    PedidosEstadoItem,
    ProductoTopItem,
    ResumenResponse,
    VentasPeriodoItem,
)
from app.modules.estadisticas.service import EstadisticasService

router = APIRouter(prefix="/estadisticas", tags=["estadisticas"])


def _default_desde() -> date:
    return date.today() - timedelta(days=30)


def _default_hasta() -> date:
    return date.today()


@router.get("/resumen", response_model=ResumenResponse, status_code=status.HTTP_200_OK)
def resumen(
    _admin: Usuario = Depends(require_role("ADMIN")),
    uow: SqlModelUnitOfWork = Depends(get_uow),
) -> ResumenResponse:
    return ResumenResponse.model_validate(EstadisticasService.resumen(uow))


@router.get("/ventas", response_model=list[VentasPeriodoItem], status_code=status.HTTP_200_OK)
def ventas_periodo(
    desde: date = Query(default_factory=_default_desde),
    hasta: date = Query(default_factory=_default_hasta),
    agrupacion: str = Query(default="day"),
    _admin: Usuario = Depends(require_role("ADMIN")),
    uow: SqlModelUnitOfWork = Depends(get_uow),
) -> list[VentasPeriodoItem]:
    return [VentasPeriodoItem.model_validate(item) for item in EstadisticasService.ventas_periodo(desde, hasta, agrupacion, uow)]


@router.get("/productos-top", response_model=list[ProductoTopItem], status_code=status.HTTP_200_OK)
def productos_top(
    limit: int = Query(default=10, ge=1, le=50),
    _admin: Usuario = Depends(require_role("ADMIN")),
    uow: SqlModelUnitOfWork = Depends(get_uow),
) -> list[ProductoTopItem]:
    return [ProductoTopItem.model_validate(item) for item in EstadisticasService.productos_top(limit, uow)]


@router.get("/pedidos-por-estado", response_model=list[PedidosEstadoItem], status_code=status.HTTP_200_OK)
def pedidos_por_estado(
    _admin: Usuario = Depends(require_role("ADMIN")),
    uow: SqlModelUnitOfWork = Depends(get_uow),
) -> list[PedidosEstadoItem]:
    return [PedidosEstadoItem.model_validate(item) for item in EstadisticasService.pedidos_por_estado(uow)]


@router.get("/ingresos", response_model=list[IngresosFormaPagoItem], status_code=status.HTTP_200_OK)
def ingresos_por_forma_pago(
    desde: date = Query(default_factory=_default_desde),
    hasta: date = Query(default_factory=_default_hasta),
    _admin: Usuario = Depends(require_role("ADMIN")),
    uow: SqlModelUnitOfWork = Depends(get_uow),
) -> list[IngresosFormaPagoItem]:
    return [IngresosFormaPagoItem.model_validate(item) for item in EstadisticasService.ingresos(desde, hasta, uow)]
