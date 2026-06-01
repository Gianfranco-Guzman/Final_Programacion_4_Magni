from datetime import datetime, timezone
from io import BytesIO
from decimal import Decimal, ROUND_FLOOR

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.db.models import Categoria, Producto, ProductoCategoria, Ingrediente, ProductoDetalle
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.productos.schemas import (
    ProductoCategoriaPayload,
    ProductoCreate,
    ProductoDetallePayload,
    ProductoUpdate,
)


class ProductoService:

    @staticmethod
    def calcular_precio_final(producto: Producto) -> Decimal:
        precio_venta = Decimal(str(producto.precio_venta))
        descuento = Decimal(str(producto.descuento_porcentaje))
        if descuento <= 0:
            return precio_venta.quantize(Decimal("0.01"))
        return (precio_venta * (Decimal("1") - (descuento / Decimal("100")))).quantize(Decimal("0.01"))

    @staticmethod
    def calcular_stock_disponible(producto: Producto) -> int:
        if not producto.ingredientes:
            return 0

        disponibilidades: list[int] = []
        for detalle in producto.ingredientes:
            cantidad_requerida = Decimal(str(detalle.cantidad))
            if cantidad_requerida <= 0 or not detalle.ingrediente:
                return 0
            stock_actual = Decimal(str(detalle.ingrediente.stock_actual))
            disponible = int((stock_actual / cantidad_requerida).to_integral_value(rounding=ROUND_FLOOR))
            disponibilidades.append(max(disponible, 0))

        return min(disponibilidades) if disponibilidades else 0

    @staticmethod
    def puede_fabricarse(producto: Producto) -> bool:
        return ProductoService.calcular_stock_disponible(producto) > 0

    @staticmethod
    def _validar_reglas_tipo_producto(
        tipo_producto,
        ingredientes_payload: list[ProductoDetallePayload],
    ) -> None:
        if tipo_producto.value == "REVENTA" and len(ingredientes_payload) != 1:
            raise HTTPException(
                status_code=400,
                detail="Un producto de reventa debe tener exactamente 1 ingrediente asociado",
            )

        if tipo_producto.value == "FABRICADO" and len(ingredientes_payload) < 1:
            raise HTTPException(
                status_code=400,
                detail="Un producto fabricado debe tener al menos 1 ingrediente en su detalle",
            )

    @staticmethod
    def _calcular_precio_costo(
        ingredientes_payload: list[ProductoDetallePayload],
        uow: SqlModelUnitOfWork,
    ) -> Decimal:
        session = uow.session
        ingrediente_ids = [item.ingrediente_id for item in ingredientes_payload]
        ingredientes = session.exec(
            select(Ingrediente).where(Ingrediente.id.in_(ingrediente_ids))
        ).all()
        ingredientes_map = {ingrediente.id: ingrediente for ingrediente in ingredientes}

        total = Decimal("0")
        for item in ingredientes_payload:
            ingrediente = ingredientes_map[item.ingrediente_id]
            total += Decimal(str(ingrediente.costo_unitario)) * Decimal(str(item.cantidad))

        return total.quantize(Decimal("0.01"))

    @staticmethod
    def _validar_categorias(
        categorias_payload: list[ProductoCategoriaPayload],
        uow: SqlModelUnitOfWork,
    ) -> list[ProductoCategoriaPayload]:
        session = uow.session
        categoria_ids = [item.categoria_id for item in categorias_payload]

        if len(categoria_ids) != len(set(categoria_ids)):
            raise HTTPException(status_code=400, detail="No se permiten categorías duplicadas")

        categorias = session.exec(select(Categoria).where(Categoria.id.in_(categoria_ids))).all()
        if len(categorias) != len(categoria_ids):
            found_ids = {categoria.id for categoria in categorias}
            missing = [item_id for item_id in categoria_ids if item_id not in found_ids]
            raise HTTPException(status_code=404, detail=f"Categorías no encontradas: {missing}")

        principales = [item for item in categorias_payload if item.es_principal]
        if len(principales) > 1:
            raise HTTPException(status_code=400, detail="Solo una categoría puede ser principal")

        if not principales and categorias_payload:
            primera = categorias_payload[0]
            categorias_payload = [
                ProductoCategoriaPayload(
                    categoria_id=item.categoria_id,
                    es_principal=item.categoria_id == primera.categoria_id,
                )
                for item in categorias_payload
            ]

        return categorias_payload

    @staticmethod
    def _validar_ingredientes(
        ingredientes_payload: list[ProductoDetallePayload],
        uow: SqlModelUnitOfWork,
    ) -> list[ProductoDetallePayload]:
        session = uow.session
        ingrediente_ids = [item.ingrediente_id for item in ingredientes_payload]

        if len(ingrediente_ids) != len(set(ingrediente_ids)):
            raise HTTPException(
                status_code=400,
                detail="No se permiten ingredientes duplicados",
            )

        ingredientes = session.exec(
            select(Ingrediente).where(Ingrediente.id.in_(ingrediente_ids))
        ).all()
        if len(ingredientes) != len(ingrediente_ids):
            found_ids = {i.id for i in ingredientes}
            missing = [item_id for item_id in ingrediente_ids if item_id not in found_ids]
            raise HTTPException(
                status_code=404,
                detail=f"Ingredientes no encontrados: {missing}",
            )

        ingredientes_map = {ingrediente.id: ingrediente for ingrediente in ingredientes}
        for item in ingredientes_payload:
            ingrediente = ingredientes_map[item.ingrediente_id]
            if item.unidad_medida != ingrediente.unidad_medida:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"La unidad del detalle para '{ingrediente.nombre}' debe coincidir con "
                        f"la unidad del ingrediente ({ingrediente.unidad_medida.value})"
                    ),
                )
            if not ingrediente.permite_fraccion and Decimal(str(item.cantidad)) % 1 != 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"El ingrediente '{ingrediente.nombre}' no permite cantidades fraccionadas",
                )

        return ingredientes_payload

    @staticmethod
    def crear_producto(data: ProductoCreate, uow: SqlModelUnitOfWork) -> Producto:
        session = uow.session
        existing = session.exec(
            select(Producto).where(
                (Producto.codigo == data.codigo) & (Producto.deleted_at.is_(None))
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un producto activo con el codigo '{data.codigo}'",
            )

        categorias_payload = ProductoService._validar_categorias(data.categorias, uow)
        ingredientes_payload = ProductoService._validar_ingredientes(data.ingredientes, uow)
        ProductoService._validar_reglas_tipo_producto(data.tipo_producto, ingredientes_payload)

        now = datetime.now(timezone.utc)
        categoria_principal_id = next(
            item.categoria_id for item in categorias_payload if item.es_principal
        )
        producto_data = data.model_dump(exclude={"categorias", "ingredientes"})
        producto_data["precio_costo_calculado"] = ProductoService._calcular_precio_costo(
            ingredientes_payload,
            uow,
        )
        producto = Producto(
            **producto_data,
            categoria_id=categoria_principal_id,
            created_at=now,
            updated_at=now,
        )
        session.add(producto)
        uow.flush()

        for categoria_data in categorias_payload:
            session.add(
                ProductoCategoria(
                    producto_id=producto.id,
                    categoria_id=categoria_data.categoria_id,
                    es_principal=categoria_data.es_principal,
                )
            )

        for ingrediente_data in ingredientes_payload:
            pi = ProductoDetalle(
                producto_id=producto.id,
                ingrediente_id=ingrediente_data.ingrediente_id,
                cantidad=ingrediente_data.cantidad,
                unidad_medida=ingrediente_data.unidad_medida,
                orden=ingrediente_data.orden,
                es_removible=ingrediente_data.es_removible,
                es_opcional=ingrediente_data.es_opcional,
            )
            session.add(pi)
        uow.flush()

        # Recargar el producto CON las relaciones eagerly loaded
        producto = session.exec(
            select(Producto)
            .options(
                selectinload(Producto.producto_categorias).selectinload(ProductoCategoria.categoria),
                selectinload(Producto.ingredientes).selectinload(ProductoDetalle.ingrediente),
            )
            .where(Producto.id == producto.id)
        ).one()

        return producto

    @staticmethod
    def actualizar_producto(
        producto_id: int,
        data: ProductoUpdate,
        uow: SqlModelUnitOfWork,
    ) -> Producto:
        session = uow.session
        producto = session.exec(
            select(Producto).where(
                (Producto.id == producto_id) & (Producto.deleted_at.is_(None))
            )
        ).first()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        if data.codigo is not None and data.codigo != producto.codigo:
            conflict = session.exec(
                select(Producto).where(
                    (Producto.codigo == data.codigo)
                    & (Producto.deleted_at.is_(None))
                    & (Producto.id != producto_id)
                )
            ).first()
            if conflict:
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe un producto activo con el codigo '{data.codigo}'",
                )

        categorias_payload: list[ProductoCategoriaPayload] | None = None
        ingredientes_payload: list[ProductoDetallePayload] | None = None
        if data.categorias is not None:
            categorias_payload = ProductoService._validar_categorias(data.categorias, uow)

            existing_category_relations = session.exec(
                select(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id)
            ).all()
            for rel in existing_category_relations:
                session.delete(rel)

            for categoria_data in categorias_payload:
                session.add(
                    ProductoCategoria(
                        producto_id=producto_id,
                        categoria_id=categoria_data.categoria_id,
                        es_principal=categoria_data.es_principal,
                    )
                )

            producto.categoria_id = next(
                item.categoria_id for item in categorias_payload if item.es_principal
            )

        if data.ingredientes is not None:
            ingredientes_payload = ProductoService._validar_ingredientes(data.ingredientes, uow)
            tipo_producto = data.tipo_producto or producto.tipo_producto
            ProductoService._validar_reglas_tipo_producto(tipo_producto, ingredientes_payload)

            existing_relations = session.exec(
                select(ProductoDetalle).where(
                    ProductoDetalle.producto_id == producto_id
                )
            ).all()
            for rel in existing_relations:
                session.delete(rel)
            uow.flush()

            for ingrediente_data in ingredientes_payload:
                pi = ProductoDetalle(
                    producto_id=producto_id,
                    ingrediente_id=ingrediente_data.ingrediente_id,
                    cantidad=ingrediente_data.cantidad,
                    unidad_medida=ingrediente_data.unidad_medida,
                    orden=ingrediente_data.orden,
                    es_removible=ingrediente_data.es_removible,
                    es_opcional=ingrediente_data.es_opcional,
                )
                session.add(pi)

            producto.precio_costo_calculado = ProductoService._calcular_precio_costo(
                ingredientes_payload,
                uow,
            )

        if data.tipo_producto is not None and ingredientes_payload is None:
            existing_relations = session.exec(
                select(ProductoDetalle).where(ProductoDetalle.producto_id == producto_id)
            ).all()
            dummy_payload = [
                ProductoDetallePayload(
                    ingrediente_id=rel.ingrediente_id,
                    cantidad=rel.cantidad,
                    unidad_medida=rel.unidad_medida,
                    orden=rel.orden,
                    es_removible=rel.es_removible,
                    es_opcional=rel.es_opcional,
                )
                for rel in existing_relations
            ]
            ProductoService._validar_reglas_tipo_producto(data.tipo_producto, dummy_payload)

        update_data = data.model_dump(exclude_unset=True, exclude={"categorias", "ingredientes"})
        for field, value in update_data.items():
            setattr(producto, field, value)
        producto.updated_at = datetime.now(timezone.utc)

        session.add(producto)
        uow.flush()

        # Recargar el producto CON las relaciones eagerly loaded
        # (refresh() solo refresca campos escalares, no relationships)
        producto = session.exec(
            select(Producto)
            .options(
                selectinload(Producto.producto_categorias).selectinload(ProductoCategoria.categoria),
                selectinload(Producto.ingredientes).selectinload(ProductoDetalle.ingrediente),
            )
            .where(Producto.id == producto_id)
        ).one()

        return producto

    @staticmethod
    def dar_de_baja(producto_id: int, uow: SqlModelUnitOfWork) -> Producto:
        session = uow.session
        producto = session.exec(select(Producto).where(Producto.id == producto_id)).first()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        if producto.deleted_at is not None:
            raise HTTPException(status_code=400, detail="El producto ya está dado de baja")

        producto.deleted_at = datetime.now(timezone.utc)
        producto.updated_at = datetime.now(timezone.utc)
        session.add(producto)
        uow.flush()

        producto = session.exec(
            select(Producto)
            .options(
                selectinload(Producto.producto_categorias).selectinload(ProductoCategoria.categoria),
                selectinload(Producto.ingredientes).selectinload(ProductoDetalle.ingrediente),
            )
            .where(Producto.id == producto_id)
        ).one()
        return producto

    @staticmethod
    def reactivar_producto(producto_id: int, uow: SqlModelUnitOfWork) -> Producto:
        session = uow.session
        producto = session.exec(select(Producto).where(Producto.id == producto_id)).first()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        if producto.deleted_at is None:
            raise HTTPException(status_code=400, detail="El producto no está dado de baja")

        conflict = session.exec(
            select(Producto).where(
                (Producto.codigo == producto.codigo)
                & (Producto.deleted_at.is_(None))
                & (Producto.id != producto_id)
            )
        ).first()
        if conflict:
            raise HTTPException(
                status_code=409,
                detail=f"No se puede reactivar: ya existe otro producto activo con el codigo '{producto.codigo}'",
            )

        producto.deleted_at = None
        producto.updated_at = datetime.now(timezone.utc)
        session.add(producto)
        uow.flush()

        producto = session.exec(
            select(Producto)
            .options(
                selectinload(Producto.producto_categorias).selectinload(ProductoCategoria.categoria),
                selectinload(Producto.ingredientes).selectinload(ProductoDetalle.ingrediente),
            )
            .where(Producto.id == producto_id)
        ).one()
        return producto

    @staticmethod
    def toggle_disponible(producto_id: int, uow: SqlModelUnitOfWork) -> Producto:
        session = uow.session
        producto = session.exec(select(Producto).where(Producto.id == producto_id)).first()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        producto.disponible = not producto.disponible
        producto.updated_at = datetime.now(timezone.utc)
        session.add(producto)
        uow.flush()

        producto = session.exec(
            select(Producto)
            .options(
                selectinload(Producto.producto_categorias).selectinload(ProductoCategoria.categoria),
                selectinload(Producto.ingredientes).selectinload(ProductoDetalle.ingrediente),
            )
            .where(Producto.id == producto_id)
        ).one()
        return producto

    @staticmethod
    def exportar_a_excel(productos: list[Producto]) -> BytesIO:
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Productos"

        headers = [
            "ID",
            "Código",
            "Nombre",
            "Descripción",
            "Precio Venta",
            "Descuento %",
            "Precio Final",
            "Costo Calculado",
            "Stock Calculado",
            "Disponible",
            "Categoría",
            "Ingredientes",
            "Estado",
            "Fecha Creación",
            "Fecha Actualización",
        ]
        ws.append(headers)

        for prod in productos:
            estado = "Baja" if prod.deleted_at else "Activo"
            stock_calculado = ProductoService.calcular_stock_disponible(prod)
            precio_final = ProductoService.calcular_precio_final(prod)
            categorias_nombres = ", ".join(
                [
                    f"{pc.categoria.nombre}{' *' if pc.es_principal else ''}"
                    for pc in prod.producto_categorias
                    if pc.categoria
                ]
            ) or "Sin categoría"
            ingredientes_nombres = ", ".join(
                [
                    f"{pi.ingrediente.nombre}"
                    f" ({'opcional' if pi.es_opcional else 'base'}"
                    f" / {'removible' if pi.es_removible else 'fijo'})"
                    for pi in prod.ingredientes
                    if pi.ingrediente
                ] if prod.ingredientes else []
            )
            ws.append(
                [
                    prod.id,
                    prod.codigo,
                    prod.nombre,
                    prod.descripcion or "",
                    float(prod.precio_venta),
                    float(prod.descuento_porcentaje),
                    float(precio_final),
                    float(prod.precio_costo_calculado),
                    stock_calculado,
                    "Sí" if prod.disponible else "No",
                    categorias_nombres,
                    ingredientes_nombres,
                    estado,
                    prod.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    prod.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column].width = adjusted_width

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output
