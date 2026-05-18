from datetime import datetime, timezone
from io import BytesIO

from fastapi import HTTPException
from openpyxl import Workbook
from sqlmodel import select

from app.db.models import Categoria, Producto, ProductoCategoria, Ingrediente, ProductoIngrediente
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.productos.schemas import (
    ProductoCategoriaPayload,
    ProductoCreate,
    ProductoIngredientePayload,
    ProductoUpdate,
)


class ProductoService:

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
        ingredientes_payload: list[ProductoIngredientePayload],
        uow: SqlModelUnitOfWork,
    ) -> list[ProductoIngredientePayload]:
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

        now = datetime.now(timezone.utc)
        categoria_principal_id = next(
            item.categoria_id for item in categorias_payload if item.es_principal
        )
        producto_data = data.model_dump(exclude={"categorias", "ingredientes"})
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

        # Crear las relaciones producto-ingrediente
        for ingrediente_data in ingredientes_payload:
            pi = ProductoIngrediente(
                producto_id=producto.id,
                ingrediente_id=ingrediente_data.ingrediente_id,
                es_removible=ingrediente_data.es_removible,
                es_opcional=ingrediente_data.es_opcional,
            )
            session.add(pi)
        uow.flush()

        # Refrescar para cargar las relaciones
        uow.refresh(producto)
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

        # Actualizar ingredientes si se proporcionan
        if data.ingredientes is not None:
            ingredientes_payload = ProductoService._validar_ingredientes(data.ingredientes, uow)

            # Eliminar relaciones existentes
            existing_relations = session.exec(
                select(ProductoIngrediente).where(
                    ProductoIngrediente.producto_id == producto_id
                )
            ).all()
            for rel in existing_relations:
                session.delete(rel)

            # Crear nuevas relaciones
            for ingrediente_data in ingredientes_payload:
                pi = ProductoIngrediente(
                    producto_id=producto_id,
                    ingrediente_id=ingrediente_data.ingrediente_id,
                    es_removible=ingrediente_data.es_removible,
                    es_opcional=ingrediente_data.es_opcional,
                )
                session.add(pi)

        # Actualizar campos del producto (excluyendo ingredientes)
        update_data = data.model_dump(exclude_unset=True, exclude={"categorias", "ingredientes"})
        for field, value in update_data.items():
            setattr(producto, field, value)
        producto.updated_at = datetime.now(timezone.utc)

        session.add(producto)
        uow.flush()
        uow.refresh(producto)
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
        return producto

    @staticmethod
    def exportar_a_excel(productos: list[Producto]) -> BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.title = "Productos"

        headers = [
            "ID",
            "Código",
            "Nombre",
            "Descripción",
            "Precio",
            "Stock",
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
                    prod.precio,
                    prod.stock_cantidad,
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
