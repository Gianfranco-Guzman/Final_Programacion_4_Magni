from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select, func
from typing import Optional
from datetime import datetime

from app.db.base import get_session
from app.db.models import Producto, Categoria
from app.db.models.usuario import Usuario
from app.core.dependencies import get_current_user
from app.modules.productos.schemas import (
    ProductoRead,
    ProductoCreate,
    ProductoUpdate,
    PaginatedResponse,
    CategoriaRead,
)

router = APIRouter(tags=["productos"])


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Listar productos con paginación y filtros",
)
def listar_productos(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    categoria_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    disponible: Optional[bool] = Query(None),
    incluir_baja: bool = Query(False, description="Incluir productos dados de baja"),
    session: Session = Depends(get_session),
):
    query = select(Producto)
    count_query = select(func.count()).select_from(Producto)

    if not incluir_baja:
        query = query.where(Producto.deleted_at.is_(None))
        count_query = count_query.where(Producto.deleted_at.is_(None))

    if categoria_id is not None:
        query = query.where(Producto.categoria_id == categoria_id)
        count_query = count_query.where(Producto.categoria_id == categoria_id)

    if search:
        term = f"%{search.lower()}%"
        query = query.where(
            (Producto.nombre.ilike(term)) | (Producto.codigo.ilike(term))
        )
        count_query = count_query.where(
            (Producto.nombre.ilike(term)) | (Producto.codigo.ilike(term))
        )

    if disponible is True:
        query = query.where(Producto.stock_cantidad > 0)
        count_query = count_query.where(Producto.stock_cantidad > 0)
    elif disponible is False:
        query = query.where(Producto.stock_cantidad == 0)
        count_query = count_query.where(Producto.stock_cantidad == 0)

    total = session.exec(count_query).one()
    pages = (total + size - 1) // size
    query = query.offset((page - 1) * size).limit(size)
    productos = session.exec(query).all()

    return PaginatedResponse(
        items=[ProductoRead.from_orm(p) for p in productos],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/categorias/",
    response_model=list[CategoriaRead],
    summary="Listar todas las categorías",
)
def listar_categorias(session: Session = Depends(get_session)):
    categorias = session.exec(select(Categoria)).all()
    return [CategoriaRead.from_orm(c) for c in categorias]


@router.get(
    "/{producto_id}",
    response_model=ProductoRead,
    summary="Obtener producto por ID",
)
def obtener_producto(producto_id: int, session: Session = Depends(get_session)):
    producto = session.exec(
        select(Producto).where(
            (Producto.id == producto_id) & (Producto.deleted_at.is_(None))
        )
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return ProductoRead.from_orm(producto)


@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
)
def crear_producto(
    data: ProductoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
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

    now = datetime.utcnow()
    producto = Producto(
        **data.dict(),
        created_at=now,
        updated_at=now,
    )
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return ProductoRead.from_orm(producto)


@router.put(
    "/{producto_id}",
    response_model=ProductoRead,
    summary="Actualizar producto",
)
def actualizar_producto(
    producto_id: int,
    data: ProductoUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
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

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(producto, field, value)
    producto.updated_at = datetime.utcnow()

    session.add(producto)
    session.commit()
    session.refresh(producto)
    return ProductoRead.from_orm(producto)


@router.patch(
    "/{producto_id}/baja",
    response_model=ProductoRead,
    summary="Dar de baja producto (soft delete)",
)
def dar_de_baja(
    producto_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    producto = session.exec(
        select(Producto).where(Producto.id == producto_id)
    ).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if producto.deleted_at is not None:
        raise HTTPException(status_code=400, detail="El producto ya está dado de baja")

    producto.deleted_at = datetime.utcnow()
    producto.updated_at = datetime.utcnow()
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return ProductoRead.from_orm(producto)


@router.patch(
    "/{producto_id}/reactivar",
    response_model=ProductoRead,
    summary="Reactivar producto dado de baja",
)
def reactivar_producto(
    producto_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    producto = session.exec(
        select(Producto).where(Producto.id == producto_id)
    ).first()
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
    producto.updated_at = datetime.utcnow()
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return ProductoRead.from_orm(producto)
