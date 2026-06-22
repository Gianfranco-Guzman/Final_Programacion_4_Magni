from anyio import from_thread
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import require_role
from app.core.websocket import manager
from app.db.models import Categoria
from app.db.models.usuario import Usuario
from app.db.unit_of_work import UnitOfWork, get_uow
from app.modules.Categoria.schemas import (
    CategoriaCreate,
    CategoriaListResponse,
    CategoriaRead,
    CategoriaUpdate,
)
from app.modules.Categoria.service import CategoriaService

router = APIRouter(tags=["categorias"])

_ADMIN_ROLES = ["ADMIN"]


def _queue_categorias_broadcast(uow: UnitOfWork) -> None:
    uow.add_after_commit(
        lambda: from_thread.run(manager.broadcast_to_roles, _ADMIN_ROLES, "categorias_actualizadas", {})
    )


@router.get(
    "/",
    response_model=CategoriaListResponse,
    summary="Listar categorías con paginación y filtro por padre",
)
def listar_categorias(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    parent_id: int | None = Query(None),
    incluir_baja: bool = Query(False),
    uow: UnitOfWork = Depends(get_uow),
) -> CategoriaListResponse:
    total = uow.categorias.count_filtered(parent_id=parent_id, incluir_baja=incluir_baja)
    pages = (total + size - 1) // size
    categorias = uow.categorias.list_filtered(parent_id=parent_id, incluir_baja=incluir_baja)
    categorias = categorias[(page - 1) * size : page * size]

    return CategoriaListResponse(
        items=[CategoriaRead.model_validate(c) for c in categorias],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/tree",
    response_model=list[CategoriaRead],
    summary="Listar árbol de categorías activas",
)
def listar_arbol_categorias(uow: UnitOfWork = Depends(get_uow)) -> list[CategoriaRead]:
    categorias = uow.categorias.list_root_active_ordered()
    return [CategoriaRead.model_validate(c) for c in categorias]


@router.get(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Obtener categoría por ID",
)
def obtener_categoria(categoria_id: int, uow: UnitOfWork = Depends(get_uow)):
    categoria = uow.categorias.get_by_id(categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return CategoriaRead.model_validate(categoria)


@router.post(
    "/",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría",
)
def crear_categoria(
    data: CategoriaCreate,
    uow: UnitOfWork = Depends(get_uow),
    _admin: Usuario = Depends(require_role("ADMIN")),
):
    categoria = CategoriaService.crear_categoria(data, uow)
    _queue_categorias_broadcast(uow)
    return CategoriaRead.model_validate(categoria)


@router.put(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Actualizar categoría",
)
def actualizar_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    uow: UnitOfWork = Depends(get_uow),
    _admin: Usuario = Depends(require_role("ADMIN")),
):
    categoria = CategoriaService.actualizar_categoria(categoria_id, data, uow)
    _queue_categorias_broadcast(uow)
    return CategoriaRead.model_validate(categoria)


@router.patch(
    "/{categoria_id}/baja",
    response_model=CategoriaRead,
    summary="Dar de baja categoría (soft delete)",
)
def dar_de_baja_categoria(
    categoria_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _admin: Usuario = Depends(require_role("ADMIN")),
):
    categoria = CategoriaService.dar_de_baja(categoria_id, uow)
    _queue_categorias_broadcast(uow)
    return CategoriaRead.model_validate(categoria)


@router.patch(
    "/{categoria_id}/reactivar",
    response_model=CategoriaRead,
    summary="Reactivar categoría dada de baja",
)
def reactivar_categoria(
    categoria_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _admin: Usuario = Depends(require_role("ADMIN")),
):
    categoria = CategoriaService.reactivar_categoria(categoria_id, uow)
    _queue_categorias_broadcast(uow)
    return CategoriaRead.model_validate(categoria)


@router.delete(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Eliminar categoría (alias de baja lógica)",
)
def eliminar_categoria(
    categoria_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _admin: Usuario = Depends(require_role("ADMIN")),
):
    categoria = CategoriaService.eliminar_categoria(categoria_id, uow)
    return CategoriaRead.model_validate(categoria)
