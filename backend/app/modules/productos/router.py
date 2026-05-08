from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, func, select

from app.core.dependencies import get_current_user
from app.db.base import get_session
from app.db.models import Categoria, Producto
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.modules.productos.schemas import (
    CategoriaRead,
    PaginatedResponse,
    ProductoCreate,
    ProductoRead,
    ProductoUpdate,
)
from app.modules.productos.service import ProductoService

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
        items=[ProductoRead.model_validate(p) for p in productos],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/exportar",
    summary="Exportar productos a Excel",
)
def exportar_productos(
    search: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
):
    query = select(Producto).order_by(Producto.created_at.desc())
    query = query.where(Producto.deleted_at.is_(None))

    if search:
        term = f"%{search.lower()}%"
        query = query.where(
            (Producto.nombre.ilike(term)) | (Producto.codigo.ilike(term))
        )

    query = query.limit(1000)
    productos = session.exec(query).all()

    excel_file = ProductoService.exportar_a_excel(productos)

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=productos.xlsx"},
    )


@router.get(
    "/categorias/",
    response_model=list[CategoriaRead],
    summary="Listar todas las categorías",
)
def listar_categorias(session: Session = Depends(get_session)):
    categorias = session.exec(select(Categoria)).all()
    return [CategoriaRead.model_validate(c) for c in categorias]


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

    return ProductoRead.model_validate(producto)


@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
)
def crear_producto(
    data: ProductoCreate,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    current_user: Usuario = Depends(get_current_user),
):
    producto = ProductoService.crear_producto(data, uow)
    return ProductoRead.model_validate(producto)


@router.put(
    "/{producto_id}",
    response_model=ProductoRead,
    summary="Actualizar producto",
)
def actualizar_producto(
    producto_id: int,
    data: ProductoUpdate,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    current_user: Usuario = Depends(get_current_user),
):
    producto = ProductoService.actualizar_producto(producto_id, data, uow)
    return ProductoRead.model_validate(producto)


@router.patch(
    "/{producto_id}/baja",
    response_model=ProductoRead,
    summary="Dar de baja producto (soft delete)",
)
def dar_de_baja(
    producto_id: int,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    current_user: Usuario = Depends(get_current_user),
):
    producto = ProductoService.dar_de_baja(producto_id, uow)
    return ProductoRead.model_validate(producto)


@router.patch(
    "/{producto_id}/reactivar",
    response_model=ProductoRead,
    summary="Reactivar producto dado de baja",
)
def reactivar_producto(
    producto_id: int,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    current_user: Usuario = Depends(get_current_user),
):
    producto = ProductoService.reactivar_producto(producto_id, uow)
    return ProductoRead.model_validate(producto)
