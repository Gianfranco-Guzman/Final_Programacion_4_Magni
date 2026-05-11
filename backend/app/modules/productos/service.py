from datetime import datetime, timezone
from io import BytesIO

from fastapi import HTTPException
from openpyxl import Workbook
from sqlmodel import select

from app.db.models import Producto, Ingrediente, ProductoIngrediente
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.productos.schemas import ProductoCreate, ProductoUpdate


class ProductoService:

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

        # Validar que la categoría existe
        from app.db.models import Categoria
        categoria = session.exec(
            select(Categoria).where(Categoria.id == data.categoria_id)
        ).first()
        if not categoria:
            raise HTTPException(
                status_code=404,
                detail=f"Categoría con id {data.categoria_id} no encontrada",
            )

        # Validar que los ingredientes existen
        ingredientes = session.exec(
            select(Ingrediente).where(Ingrediente.id.in_(data.ingredientes_ids))
        ).all()
        if len(ingredientes) != len(data.ingredientes_ids):
            found_ids = {i.id for i in ingredientes}
            missing = [id for id in data.ingredientes_ids if id not in found_ids]
            raise HTTPException(
                status_code=404,
                detail=f"Ingredientes no encontrados: {missing}",
            )

        # Validar ingredientes duplicados en la request
        if len(data.ingredientes_ids) != len(set(data.ingredientes_ids)):
            raise HTTPException(
                status_code=400,
                detail="No se permiten ingredientes duplicados",
            )

        now = datetime.now(timezone.utc)
        producto_data = data.model_dump(exclude={"ingredientes_ids"})
        producto = Producto(
            **producto_data,
            created_at=now,
            updated_at=now,
        )
        session.add(producto)
        uow.flush()

        # Crear las relaciones producto-ingrediente
        for ingrediente_id in data.ingredientes_ids:
            pi = ProductoIngrediente(
                producto_id=producto.id,
                ingrediente_id=ingrediente_id,
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

        # Validar categoría si se actualiza
        if data.categoria_id is not None:
            from app.db.models import Categoria
            categoria = session.exec(
                select(Categoria).where(Categoria.id == data.categoria_id)
            ).first()
            if not categoria:
                raise HTTPException(
                    status_code=404,
                    detail=f"Categoría con id {data.categoria_id} no encontrada",
                )

        # Actualizar ingredientes si se proporcionan
        if data.ingredientes_ids is not None:
            # Validar ingredientes duplicados
            if len(data.ingredientes_ids) != len(set(data.ingredientes_ids)):
                raise HTTPException(
                    status_code=400,
                    detail="No se permiten ingredientes duplicados",
                )

            # Validar que los ingredientes existen
            ingredientes = session.exec(
                select(Ingrediente).where(Ingrediente.id.in_(data.ingredientes_ids))
            ).all()
            if len(ingredientes) != len(data.ingredientes_ids):
                found_ids = {i.id for i in ingredientes}
                missing = [id for id in data.ingredientes_ids if id not in found_ids]
                raise HTTPException(
                    status_code=404,
                    detail=f"Ingredientes no encontrados: {missing}",
                )

            # Eliminar relaciones existentes
            existing_relations = session.exec(
                select(ProductoIngrediente).where(
                    ProductoIngrediente.producto_id == producto_id
                )
            ).all()
            for rel in existing_relations:
                session.delete(rel)

            # Crear nuevas relaciones
            for ingrediente_id in data.ingredientes_ids:
                pi = ProductoIngrediente(
                    producto_id=producto_id,
                    ingrediente_id=ingrediente_id,
                )
                session.add(pi)

        # Actualizar campos del producto (excluyendo ingredientes_ids)
        update_data = data.model_dump(exclude_unset=True, exclude={"ingredientes_ids"})
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
            "Categoría",
            "Ingredientes",
            "Estado",
            "Fecha Creación",
            "Fecha Actualización",
        ]
        ws.append(headers)

        for prod in productos:
            estado = "Baja" if prod.deleted_at else "Activo"
            categoria_nombre = prod.categoria.nombre if prod.categoria else "Sin categoría"
            ingredientes_nombres = ", ".join(
                [pi.ingrediente.nombre for pi in prod.ingredientes] if prod.ingredientes else []
            )
            ws.append(
                [
                    prod.id,
                    prod.codigo,
                    prod.nombre,
                    prod.descripcion or "",
                    prod.precio,
                    prod.stock_cantidad,
                    categoria_nombre,
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
