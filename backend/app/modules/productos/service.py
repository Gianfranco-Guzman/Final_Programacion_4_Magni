from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import select

from app.db.models import Producto
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.productos.schemas import ProductoCreate, ProductoUpdate


class ProductoService:
    """Lógica de aplicación para productos."""

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
                detail=f"Ya existe un producto activo con el código '{data.codigo}'",
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
                    detail=f"Ya existe un producto activo con el código '{data.codigo}'",
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
                detail=f"No se puede reactivar: ya existe otro producto activo con el código '{producto.codigo}'",
            )

        producto.deleted_at = None
        producto.updated_at = datetime.now(timezone.utc)
        session.add(producto)
        uow.flush()
        return producto
