from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException

from app.modules.ingredientes.model import Ingrediente, MovimientoStockIngrediente
from app.core.enums import TipoMovimientoIngrediente
from app.db.unit_of_work import UnitOfWork

#service solo para el manejo de stock de los ingredientes

class IngredienteStockService:
    @staticmethod
    def registrar_movimiento(
        ingrediente: Ingrediente,
        cantidad: Decimal,
        tipo_movimiento: TipoMovimientoIngrediente,
        uow: UnitOfWork,
        *,
        pedido_id: int | None = None,
        usuario_id: int | None = None,
        movimiento_referencia_id: int | None = None,
        observacion: str | None = None,
        aplicar_cambio: bool = False,
        signo: int = 1,
        stock_anterior_override: Decimal | None = None,
        stock_posterior_override: Decimal | None = None,
    ) -> MovimientoStockIngrediente:
        cantidad_decimal = Decimal(str(cantidad))
        if cantidad_decimal <= 0:
            raise HTTPException(status_code=400, detail="La cantidad del movimiento debe ser mayor a 0")

        stock_anterior = (
            Decimal(str(stock_anterior_override))
            if stock_anterior_override is not None
            else Decimal(str(ingrediente.stock_actual))
        )
        stock_posterior = (
            Decimal(str(stock_posterior_override))
            if stock_posterior_override is not None
            else stock_anterior
        )

        if aplicar_cambio:
            stock_posterior = stock_anterior + (cantidad_decimal * Decimal(signo))
            if stock_posterior < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para '{ingrediente.nombre}'",
                )
            ingrediente.stock_actual = stock_posterior
            ingrediente.updated_at = datetime.now(timezone.utc)
            uow.ingredientes.save(ingrediente)

        movimiento = MovimientoStockIngrediente(
            ingrediente_id=ingrediente.id,
            pedido_id=pedido_id,
            usuario_id=usuario_id,
            movimiento_referencia_id=movimiento_referencia_id,
            tipo_movimiento=tipo_movimiento,
            cantidad=cantidad_decimal,
            stock_anterior=stock_anterior,
            stock_posterior=stock_posterior,
            observacion=observacion,
            created_at=datetime.now(timezone.utc),
        )
        uow.movimientos_stock_ingredientes.save(movimiento)
        uow.flush()
        return movimiento

    @staticmethod
    def consumir_por_pedido(
        ingrediente: Ingrediente,
        cantidad: Decimal,
        pedido_id: int,
        uow: UnitOfWork,
        observacion: str | None = None,
    ) -> MovimientoStockIngrediente:
        return IngredienteStockService.registrar_movimiento(
            ingrediente,
            cantidad,
            TipoMovimientoIngrediente.CONSUMO_PEDIDO,
            uow,
            pedido_id=pedido_id,
            observacion=observacion,
            aplicar_cambio=True,
            signo=-1,
        )

    @staticmethod
    def revertir_por_cancelacion(
        ingrediente: Ingrediente,
        cantidad: Decimal,
        pedido_id: int,
        uow: UnitOfWork,
        observacion: str | None = None,
    ) -> MovimientoStockIngrediente:
        return IngredienteStockService.registrar_movimiento(
            ingrediente,
            cantidad,
            TipoMovimientoIngrediente.REVERSA_CANCELACION,
            uow,
            pedido_id=pedido_id,
            observacion=observacion,
            aplicar_cambio=True,
            signo=1,
        )
