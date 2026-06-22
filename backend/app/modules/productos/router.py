from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.core.dependencies import (
    get_optional_current_user,
    require_role,
    user_has_any_role,
)
from app.modules.productos.model import Producto
from app.modules.auth.model import Usuario
from app.db.unit_of_work import UnitOfWork, get_uow
from app.modules.productos.schemas import (
    CategoriaRead,
    IngredienteRead,
    PaginatedResponse,
    ProductoCategoriaRead,
    ProductoCreate,
    ProductoDetalleRead,
    ProductoRead,
    ProductoUpdate,
)
from app.modules.productos.service import ProductoService

router = APIRouter(tags=["productos"])


def _build_producto_read(producto: Producto) -> ProductoRead:
    """Build ProductoRead with categorias and ingredientes relations."""
    categorias = []
    categoria_principal_id = None

    if producto.producto_categorias:
        for pc in producto.producto_categorias:
            if pc.categoria:
                categorias.append(
                    ProductoCategoriaRead(
                        categoria_id=pc.categoria_id,
                        es_principal=pc.es_principal,
                        categoria=pc.categoria,
                    )
                )
                if pc.es_principal:
                    categoria_principal_id = pc.categoria_id

    ingredientes = []
    if producto.ingredientes:
        for pi in producto.ingredientes:
            if pi is not None and pi.ingrediente:
                ingredientes.append(
                    ProductoDetalleRead(
                        id=pi.id,
                        ingrediente_id=pi.ingrediente_id,
                        cantidad=pi.cantidad,
                        unidad_medida=pi.unidad_medida,
                        orden=pi.orden,
                        es_removible=pi.es_removible,
                        es_opcional=pi.es_opcional,
                        ingrediente=pi.ingrediente,
                    )
                )

    stock_disponible_calculado = ProductoService.calcular_stock_disponible(producto)
    precio_final = ProductoService.calcular_precio_final(producto)

    return ProductoRead(
        id=producto.id,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio_venta=producto.precio_venta,
        precio_costo_calculado=producto.precio_costo_calculado,
        descuento_porcentaje=producto.descuento_porcentaje,
        precio_final=precio_final,
        tipo_producto=producto.tipo_producto,
        stock_disponible_calculado=stock_disponible_calculado,
        puede_fabricarse=stock_disponible_calculado > 0,
        categoria_principal_id=categoria_principal_id,
        codigo=producto.codigo,
        disponible=producto.disponible,
        imagenes_url=producto.imagenes_url,
        unidad_venta_id=producto.unidad_venta_id,
        deleted_at=producto.deleted_at,
        created_at=producto.created_at,
        updated_at=producto.updated_at,
        categorias=categorias,
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
    uow: UnitOfWork = Depends(get_uow),
    current_user: Usuario | None = Depends(get_optional_current_user),
):
    if incluir_baja and not user_has_any_role(current_user, ["ADMIN", "STOCK"], uow):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo usuarios ADMIN o STOCK pueden incluir productos dados de baja",
        )

    total = uow.productos.count_for_catalog(
        categoria_id=categoria_id,
        search=search,
        disponible=disponible,
        incluir_baja=incluir_baja,
    )
    pages = (total + size - 1) // size
    productos = uow.productos.list_for_catalog(
        categoria_id=categoria_id,
        search=search,
        disponible=disponible,
        incluir_baja=incluir_baja,
        page=page,
        size=size,
    )

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
    uow: UnitOfWork = Depends(get_uow),
):
    productos = uow.productos.list_for_export(search=search, limit=1000)
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
def listar_categorias(uow: UnitOfWork = Depends(get_uow)):
    categorias = uow.categorias.list_all_ordered()
    return [CategoriaRead.model_validate(c) for c in categorias]


@router.get(
    "/{producto_id}",
    response_model=ProductoRead,
    summary="Obtener producto por ID",
)
def obtener_producto(producto_id: int, uow: UnitOfWork = Depends(get_uow)):
    producto = uow.productos.get_active_by_id_with_relations(producto_id)

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return _build_producto_read(producto)


@router.get(
    "/{producto_id}/ingredientes",
    response_model=list[IngredienteRead],
    summary="Listar ingredientes del producto",
)
def listar_ingredientes_producto(producto_id: int, uow: UnitOfWork = Depends(get_uow)):
    producto = uow.productos.get_active_by_id_with_relations(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    ingredientes = [detalle.ingrediente for detalle in producto.ingredientes if detalle.ingrediente is not None]
    return [IngredienteRead.model_validate(ingrediente) for ingrediente in ingredientes]


@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
)
def crear_producto(
    data: ProductoCreate,
    uow: UnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN"])),
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
    uow: UnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN"])),
):
    producto = ProductoService.actualizar_producto(producto_id, data, uow)
    return _build_producto_read(producto)


@router.patch(
    "/{producto_id}/imagenes",
    response_model=ProductoRead,
    summary="Actualizar imágenes del producto",
)
def actualizar_imagenes_producto(
    producto_id: int,
    data: ProductoUpdate,
    uow: UnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN"])),
):
    producto = ProductoService.actualizar_producto(
        producto_id,
        ProductoUpdate(imagenes_url=data.imagenes_url),
        uow,
    )
    return _build_producto_read(producto)


@router.patch(
    "/{producto_id}/baja",
    response_model=ProductoRead,
    summary="Dar de baja producto (soft delete)",
)
def dar_de_baja(
    producto_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN"])),
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
    uow: UnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN"])),
):
    producto = ProductoService.reactivar_producto(producto_id, uow)
    return _build_producto_read(producto)


@router.patch(
    "/{producto_id}/disponibilidad",
    response_model=ProductoRead,
    summary="Alternar disponibilidad de producto",
)
def alternar_disponibilidad(
    producto_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN", "STOCK"])),
):
    producto = ProductoService.toggle_disponible(producto_id, uow)
    return _build_producto_read(producto)
