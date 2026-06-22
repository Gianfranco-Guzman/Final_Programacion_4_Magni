from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException

from app.modules.ingredientes.model import Ingrediente
from app.db.enums import TipoMovimientoIngrediente, UnidadMedida
from app.db.unit_of_work import UnitOfWork
from app.modules.ingredientes.schemas import IngredienteCreate, IngredienteUpdate, MovimientoEntradaRead, StockCargaInput, StockCorreccionInput
from app.modules.ingredientes.stock_service import IngredienteStockService


class IngredienteService:

    @staticmethod
    def _validar_reglas_unidad_y_fraccion(data: IngredienteCreate | IngredienteUpdate) -> None:
        unidad = getattr(data, "unidad_medida", None)
        permite_fraccion = getattr(data, "permite_fraccion", None)

        if unidad == UnidadMedida.UNIDAD and permite_fraccion is True:
            raise HTTPException(
                status_code=400,
                detail="Un ingrediente medido en UNIDAD no puede permitir fracciones",
            )

    @staticmethod
    def _validar_reglas_unidad_y_fraccion_combinadas(
        ingrediente: Ingrediente,
        data: IngredienteUpdate,
    ) -> None:
        unidad = data.unidad_medida if data.unidad_medida is not None else ingrediente.unidad_medida
        permite_fraccion = (
            data.permite_fraccion if data.permite_fraccion is not None else ingrediente.permite_fraccion
        )
        if unidad == UnidadMedida.UNIDAD and permite_fraccion:
            raise HTTPException(
                status_code=400,
                detail="Un ingrediente medido en UNIDAD no puede permitir fracciones",
            )

    @staticmethod
    def crear_ingrediente(data: IngredienteCreate, uow: UnitOfWork) -> Ingrediente:
        IngredienteService._validar_reglas_unidad_y_fraccion(data)
        existing = uow.ingredientes.get_active_by_name(data.nombre)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un ingrediente activo con el nombre '{data.nombre}'",
            )

        now = datetime.now(timezone.utc)
        ingrediente = Ingrediente(
            **data.model_dump(),
            created_at=now,
            updated_at=now,
        )
        uow.ingredientes.save(ingrediente)
        uow.flush()

        if Decimal(str(ingrediente.stock_actual)) > 0:
            IngredienteStockService.registrar_movimiento(
                ingrediente,
                Decimal(str(ingrediente.stock_actual)),
                TipoMovimientoIngrediente.ALTA_MANUAL,
                uow,
                observacion="Stock inicial al crear ingrediente",
                aplicar_cambio=False,
                stock_anterior_override=Decimal("0"),
                stock_posterior_override=Decimal(str(ingrediente.stock_actual)),
            )
        return ingrediente

    @staticmethod
    def actualizar_ingrediente(
        ingrediente_id: int,
        data: IngredienteUpdate,
        uow: UnitOfWork,
    ) -> Ingrediente:
        ingrediente = uow.ingredientes.get_active_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

        if data.nombre is not None and data.nombre != ingrediente.nombre:
            conflict = uow.ingredientes.get_active_by_name_excluding_id(data.nombre, ingrediente_id)
            if conflict:
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe un ingrediente activo con el nombre '{data.nombre}'",
                )

        IngredienteService._validar_reglas_unidad_y_fraccion_combinadas(ingrediente, data)
        stock_anterior = Decimal(str(ingrediente.stock_actual))
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ingrediente, field, value)
        ingrediente.updated_at = datetime.now(timezone.utc)

        uow.ingredientes.save(ingrediente)
        uow.flush()

        if "stock_actual" in update_data:
            stock_posterior = Decimal(str(ingrediente.stock_actual))
            diferencia = stock_posterior - stock_anterior
            if diferencia != 0:
                IngredienteStockService.registrar_movimiento(
                    ingrediente,
                    abs(diferencia),
                    TipoMovimientoIngrediente.AJUSTE_MANUAL,
                    uow,
                    observacion="Ajuste manual de stock desde administración",
                    aplicar_cambio=False,
                    stock_anterior_override=stock_anterior,
                    stock_posterior_override=stock_posterior,
                )
        return ingrediente

    _CONVERSIONES: dict[UnidadMedida, dict[str, Decimal]] = {
        UnidadMedida.GRAMO: {"mg": Decimal("0.001"), "g": Decimal("1"), "kg": Decimal("1000")},
        UnidadMedida.MILILITRO: {"ml": Decimal("1"), "L": Decimal("1000")},
        UnidadMedida.UNIDAD: {"unidad": Decimal("1")},
        UnidadMedida.KILOGRAMO: {"g": Decimal("0.001"), "kg": Decimal("1"), "t": Decimal("1000")},
        UnidadMedida.LITRO: {"ml": Decimal("0.001"), "L": Decimal("1")},
    }

    @staticmethod
    def _resolver_factor(ingrediente: Ingrediente, unidad_entrada: str) -> Decimal:
        conversiones = IngredienteService._CONVERSIONES.get(ingrediente.unidad_medida, {})
        factor = conversiones.get(unidad_entrada)
        if factor is None:
            opciones = list(conversiones.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Unidad '{unidad_entrada}' no válida para {ingrediente.unidad_medida}. Opciones: {opciones}",
            )
        return factor

    @staticmethod
    def cargar_stock(ingrediente_id: int, data: StockCargaInput, uow: UnitOfWork, usuario_id: int | None = None) -> Ingrediente:
        ingrediente = uow.ingredientes.get_active_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

        factor = IngredienteService._resolver_factor(ingrediente, data.unidad_entrada)
        cantidad_base = Decimal(str(data.cantidad)) * factor
        IngredienteStockService.registrar_movimiento(
            ingrediente,
            cantidad_base,
            TipoMovimientoIngrediente.ENTRADA_STOCK,
            uow,
            usuario_id=usuario_id,
            observacion=f"Carga: {data.cantidad} {data.unidad_entrada}",
            aplicar_cambio=True,
            signo=1,
        )
        return ingrediente

    @staticmethod
    def mis_cargas(usuario_id: int, uow: UnitOfWork) -> list[MovimientoEntradaRead]:
        movimientos = uow.movimientos_stock_ingredientes.list_entradas_by_usuario(usuario_id)
        result = []
        for m in movimientos:
            ya_corregido = (
                uow.movimientos_stock_ingredientes.total_corregido(m.id)
                if m.tipo_movimiento == TipoMovimientoIngrediente.ENTRADA_STOCK
                else Decimal("0")
            )
            result.append(MovimientoEntradaRead(
                id=m.id,
                ingrediente_id=m.ingrediente_id,
                tipo_movimiento=m.tipo_movimiento,
                cantidad=m.cantidad,
                stock_anterior=m.stock_anterior,
                stock_posterior=m.stock_posterior,
                observacion=m.observacion,
                created_at=m.created_at,
                movimiento_referencia_id=m.movimiento_referencia_id,
                ya_corregido_total=ya_corregido,
            ))
        return result

    @staticmethod
    def corregir_entrada(data: StockCorreccionInput, usuario_id: int, uow: UnitOfWork) -> MovimientoEntradaRead:
        movimiento = uow.movimientos_stock_ingredientes.get_by_id(data.movimiento_id)
        if not movimiento or movimiento.tipo_movimiento != TipoMovimientoIngrediente.ENTRADA_STOCK:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        if movimiento.usuario_id != usuario_id:
            raise HTTPException(status_code=403, detail="Solo podés corregir tus propias cargas")

        ingrediente = uow.ingredientes.get_active_by_id(movimiento.ingrediente_id)
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

        factor = IngredienteService._resolver_factor(ingrediente, data.unidad_entrada)
        cantidad_base = Decimal(str(data.cantidad)) * factor

        ya_corregido = uow.movimientos_stock_ingredientes.total_corregido(data.movimiento_id)
        disponible = movimiento.cantidad - ya_corregido
        if cantidad_base > disponible:
            raise HTTPException(
                status_code=400,
                detail=f"La corrección supera lo disponible. Máximo corregible: {disponible} (unidad base)",
            )

        nuevo = IngredienteStockService.registrar_movimiento(
            ingrediente,
            cantidad_base,
            TipoMovimientoIngrediente.CORRECCION_ENTRADA,
            uow,
            usuario_id=usuario_id,
            movimiento_referencia_id=data.movimiento_id,
            observacion=data.motivo,
            aplicar_cambio=True,
            signo=-1,
        )
        return MovimientoEntradaRead(
            id=nuevo.id,
            ingrediente_id=nuevo.ingrediente_id,
            tipo_movimiento=nuevo.tipo_movimiento,
            cantidad=nuevo.cantidad,
            stock_anterior=nuevo.stock_anterior,
            stock_posterior=nuevo.stock_posterior,
            observacion=nuevo.observacion,
            created_at=nuevo.created_at,
            movimiento_referencia_id=nuevo.movimiento_referencia_id,
            ya_corregido_total=Decimal("0"),
        )

    @staticmethod
    def dar_de_baja(ingrediente_id: int, uow: UnitOfWork) -> Ingrediente:
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        if ingrediente.deleted_at is not None:
            raise HTTPException(status_code=400, detail="El ingrediente ya está dado de baja")

        if uow.ingredientes.has_product_associations(ingrediente_id):
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el ingrediente porque está asociado a productos",
            )

        ingrediente.deleted_at = datetime.now(timezone.utc)
        ingrediente.updated_at = datetime.now(timezone.utc)
        uow.ingredientes.save(ingrediente)
        uow.flush()
        return ingrediente

    @staticmethod
    def reactivar(ingrediente_id: int, uow: UnitOfWork) -> Ingrediente:
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        if ingrediente.deleted_at is None:
            raise HTTPException(status_code=400, detail="El ingrediente no está dado de baja")

        conflict = uow.ingredientes.get_active_by_name_excluding_id(ingrediente.nombre, ingrediente_id)
        if conflict:
            raise HTTPException(
                status_code=409,
                detail=f"No se puede reactivar: ya existe otro ingrediente activo con el nombre '{ingrediente.nombre}'",
            )

        ingrediente.deleted_at = None
        ingrediente.updated_at = datetime.now(timezone.utc)
        uow.ingredientes.save(ingrediente)
        uow.flush()
        return ingrediente
