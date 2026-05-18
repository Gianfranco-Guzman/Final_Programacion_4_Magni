from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, func, select
from sqlalchemy.orm import selectinload

from app.core.dependencies import (
    get_current_user,
    get_optional_current_user,
    require_role,
    user_has_any_role,
)
from app.db.base import get_session
from app.db.models import Categoria, Producto, ProductoIngrediente
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.modules.productos.schemas import (
    CategoriaRead,
    PaginatedResponse,
    ProductoCreate,
    ProductoIngredienteRead,
    ProductoRead,
    ProductoUpdate,
)
from app.modules.productos.service import ProductoService

router = APIRouter(tags=["productos"])


def _build_producto_read(producto: Producto) -> ProductoRead:
    """Build ProductoRead with ingredientes from ProductoIngrediente relations."""
    ingredientes = []
    if producto.ingredientes:
        for pi in producto.ingredientes:
            if pi.ingrediente:
                ingredientes.append(
                    ProductoIngredienteRead(
                        ingrediente_id=pi.ingrediente_id,
                        es_removible=pi.es_removible,
                        es_opcional=pi.es_opcional,
                        ingrediente=pi.ingrediente,
                    )
                )
    return ProductoRead(
        id=producto.id,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        stock_cantidad=producto.stock_cantidad,
        categoria_id=producto.categoria_id,
        codigo=producto.codigo,
        disponible=producto.disponible,
        deleted_at=producto.deleted_at,
        created_at=producto.created_at,
        updated_at=producto.updated_at,
        categoria=producto.categoria,
        ingredientes=ingredientes,
    )


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
    current_user: Usuario | None = Depends(get_optional_current_user),
):
    query = select(Producto).options(
        selectinload(Producto.categoria),
        selectinload(Producto.ingredientes).selectinload(
            ProductoIngrediente.ingrediente),
    )
    count_query = select(func.count()).select_from(Producto)

    if incluir_baja and not user_has_any_role(current_user, ["ADMIN", "STOCK"], session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo usuarios ADMIN o STOCK pueden incluir productos dados de baja",
        )

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
        query = query.where(Producto.disponible.is_(True))
        count_query = count_query.where(Producto.disponible.is_(True))
    elif disponible is False:
        query = query.where(Producto.disponible.is_(False))
        count_query = count_query.where(Producto.disponible.is_(False))

    total = session.exec(count_query).one()
    pages = (total + size - 1) // size
    query = query.offset((page - 1) * size).limit(size)
    productos = session.exec(query).unique().all()

    return PaginatedResponse(
        items=[_build_producto_read(p) for p in productos],
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
    query = (
        select(Producto)
        .options(
            selectinload(Producto.categoria),
            selectinload(Producto.ingredientes).selectinload(
                ProductoIngrediente.ingrediente),
        )
        .order_by(Producto.created_at.desc())
    )
    query = query.where(Producto.deleted_at.is_(None))

    if search:
        term = f"%{search.lower()}%"
        query = query.where(
            (Producto.nombre.ilike(term)) | (Producto.codigo.ilike(term))
        )

    query = query.limit(1000)
    productos = session.exec(query).unique().all()

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
        select(Producto)
        .options(
            selectinload(Producto.categoria),
            selectinload(Producto.ingredientes).selectinload(
                ProductoIngrediente.ingrediente),
        )
        .where(
            (Producto.id == producto_id) & (Producto.deleted_at.is_(None))
        )
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return _build_producto_read(producto)


@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
)
def crear_producto(
    data: ProductoCreate,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN", "STOCK"])),
):
    producto = ProductoService.crear_producto(data, uow)
    return _build_producto_read(producto)


@router.put(
    "/{producto_id}",
    response_model=ProductoRead,
    summary="Actualizar producto",
)
def actualizar_producto(
    producto_id: int,
    data: ProductoUpdate,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN", "STOCK"])),
):
    producto = ProductoService.actualizar_producto(producto_id, data, uow)
    return _build_producto_read(producto)


@router.patch(
    "/{producto_id}/baja",
    response_model=ProductoRead,
    summary="Dar de baja producto (soft delete)",
)
def dar_de_baja(
    producto_id: int,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN", "STOCK"])),
):
    producto = ProductoService.dar_de_baja(producto_id, uow)
    return _build_producto_read(producto)


@router.patch(
    "/{producto_id}/reactivar",
    response_model=ProductoRead,
    summary="Reactivar producto dado de baja",
)
def reactivar_producto(
    producto_id: int,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN", "STOCK"])),
):
    producto = ProductoService.reactivar_producto(producto_id, uow)
    return _build_producto_read(producto)
