from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from typing import Optional
from datetime import datetime

from app.db.base import get_session
from app.db.models import Producto, Categoria
from app.modules.productos.schemas import (
    ProductoRead,
    PaginatedResponse,
    CategoriaRead,
)

router = APIRouter(tags=["productos"])


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Listar productos con paginación y filtros",
    description="Obtiene una lista paginada de productos con filtros opcionales por categoría, búsqueda y disponibilidad"
)
def listar_productos(
    page: int = Query(1, ge=1, description="Número de página (comienza en 1)"),
    size: int = Query(20, ge=1, le=100, description="Cantidad de items por página"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por ID de categoría"),
    search: Optional[str] = Query(None, description="Búsqueda por nombre o código"),
    disponible: Optional[bool] = Query(None, description="Filtrar solo productos con stock > 0"),
    session: Session = Depends(get_session),
):
    """
    Retorna una lista paginada de productos activos (no eliminados).

    **Filtros disponibles:**
    - `categoria_id`: Filtra por categoría
    - `search`: Busca en nombre o código del producto
    - `disponible`: Si es true, solo muestra productos con stock > 0

    **Respuesta:**
    - `items`: Lista de productos
    - `total`: Total de productos que coinciden
    - `page`: Página actual
    - `size`: Tamaño de página
    - `pages`: Total de páginas
    """

    # Query base: solo productos no eliminados
    query = select(Producto).where(Producto.deleted_at.is_(None))

    # Aplicar filtro de categoría
    if categoria_id is not None:
        query = query.where(Producto.categoria_id == categoria_id)

    # Aplicar búsqueda
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            (Producto.nombre.ilike(search_term)) |
            (Producto.codigo.ilike(search_term))
        )

    # Aplicar filtro de disponibilidad
    if disponible is True:
        query = query.where(Producto.stock_cantidad > 0)
    elif disponible is False:
        query = query.where(Producto.stock_cantidad == 0)

    # Contar total antes de paginar
    count_query = select(func.count()).select_from(Producto).where(
        Producto.deleted_at.is_(None)
    )

    # Aplicar mismo filtro de búsqueda
    if search:
        search_term = f"%{search.lower()}%"
        count_query = count_query.where(
            (Producto.nombre.ilike(search_term)) |
            (Producto.codigo.ilike(search_term))
        )

    # Aplicar filtro de categoría al count
    if categoria_id is not None:
        count_query = count_query.where(Producto.categoria_id == categoria_id)

    # Aplicar filtro de disponibilidad al count
    if disponible is True:
        count_query = count_query.where(Producto.stock_cantidad > 0)
    elif disponible is False:
        count_query = count_query.where(Producto.stock_cantidad == 0)

    total = session.exec(count_query).one()

    # Calcular paginación
    skip = (page - 1) * size
    pages = (total + size - 1) // size

    # Ejecutar query con paginación
    query = query.offset(skip).limit(size)
    productos = session.exec(query).all()

    # Convertir a schemas de lectura
    productos_read = [
        ProductoRead.from_orm(p) for p in productos
    ]

    return PaginatedResponse(
        items=productos_read,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/{producto_id}",
    response_model=ProductoRead,
    summary="Obtener producto por ID",
)
def obtener_producto(
    producto_id: int,
    session: Session = Depends(get_session),
):
    """Obtiene un producto específico por su ID (si no está eliminado)"""

    producto = session.exec(
        select(Producto).where(
            (Producto.id == producto_id) &
            (Producto.deleted_at.is_(None))
        )
    ).first()

    if not producto:
        raise ValueError(f"Producto con ID {producto_id} no encontrado")

    return ProductoRead.from_orm(producto)


@router.get(
    "/categorias/",
    response_model=list[CategoriaRead],
    summary="Listar todas las categorías",
)
def listar_categorias(
    session: Session = Depends(get_session),
):
    """Retorna lista de todas las categorías disponibles"""

    categorias = session.exec(select(Categoria)).all()
    return [CategoriaRead.from_orm(c) for c in categorias]
