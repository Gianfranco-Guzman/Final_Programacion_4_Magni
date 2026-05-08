from datetime import datetime, timezone
from io import BytesIO

from fastapi import HTTPException
from openpyxl import Workbook
from sqlmodel import select

from app.db.models import Producto
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

        now = datetime.now(timezone.utc)
        producto = Producto(
            **data.model_dump(),
            created_at=now,
            updated_at=now,
        )
        session.add(producto)
        uow.flush()
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

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(producto, field, value)
        producto.updated_at = datetime.now(timezone.utc)

        session.add(producto)
        uow.flush()
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
            "Estado",
            "Fecha Creación",
            "Fecha Actualización",
        ]
        ws.append(headers)

        for prod in productos:
            estado = "Baja" if prod.deleted_at else "Activo"
            categoria_nombre = prod.categoria.nombre if prod.categoria else "Sin categoría"
            ws.append(
                [
                    prod.id,
                    prod.codigo,
                    prod.nombre,
                    prod.descripcion or "",
                    prod.precio,
                    prod.stock_cantidad,
                    categoria_nombre,
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
