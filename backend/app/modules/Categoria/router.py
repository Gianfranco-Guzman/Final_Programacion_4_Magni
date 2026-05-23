from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from app.core.dependencies import require_role
from app.db.base import get_session
from app.db.models import Categoria
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.modules.Categoria.schemas import (
    CategoriaCreate,
    CategoriaListResponse,
    CategoriaRead,
    CategoriaUpdate,
)
from app.modules.Categoria.service import CategoriaService

router = APIRouter(tags=["categorias"])


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
    session: Session = Depends(get_session),
) -> CategoriaListResponse:
    query = select(Categoria).options(selectinload(Categoria.subcategorias))
    count_query = select(func.count()).select_from(Categoria)

    if not incluir_baja:
        query = query.where(Categoria.deleted_at.is_(None))
        count_query = count_query.where(Categoria.deleted_at.is_(None))

    if parent_id is not None:
        query = query.where(Categoria.parent_id == parent_id)
        count_query = count_query.where(Categoria.parent_id == parent_id)

    total = session.exec(count_query).one()
    pages = (total + size - 1) // size
    categorias = session.exec(
        query.order_by(Categoria.nombre).offset((page - 1) * size).limit(size)
    ).all()

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
def listar_arbol_categorias(session: Session = Depends(get_session)) -> list[CategoriaRead]:
    categorias = session.exec(
        select(Categoria)
        .options(selectinload(Categoria.subcategorias))
        .where((Categoria.parent_id.is_(None)) & (Categoria.deleted_at.is_(None)))
        .order_by(Categoria.nombre)
    ).all()
    return [CategoriaRead.model_validate(c) for c in categorias]


@router.get(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Obtener categoría por ID",
)
def obtener_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = session.exec(
        select(Categoria)
        .options(selectinload(Categoria.subcategorias))
        .where(Categoria.id == categoria_id)
    ).first()
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
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _admin: Usuario = Depends(require_role("ADMIN")),
):
    categoria = CategoriaService.crear_categoria(data, uow)
    return CategoriaRead.model_validate(categoria)


@router.put(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Actualizar categoría",
)
def actualizar_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _admin: Usuario = Depends(require_role("ADMIN")),
):
    categoria = CategoriaService.actualizar_categoria(categoria_id, data, uow)
    return CategoriaRead.model_validate(categoria)


@router.patch(
    "/{categoria_id}/baja",
    response_model=CategoriaRead,
    summary="Dar de baja categoría (soft delete)",
)
def dar_de_baja_categoria(
    categoria_id: int,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _admin: Usuario = Depends(require_role("ADMIN")),
):
    categoria = CategoriaService.dar_de_baja(categoria_id, uow)
    return CategoriaRead.model_validate(categoria)


@router.patch(
    "/{categoria_id}/reactivar",
    response_model=CategoriaRead,
    summary="Reactivar categoría dada de baja",
)
def reactivar_categoria(
    categoria_id: int,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _admin: Usuario = Depends(require_role("ADMIN")),
):
    categoria = CategoriaService.reactivar_categoria(categoria_id, uow)
    return CategoriaRead.model_validate(categoria)


@router.delete(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Eliminar categoría (alias de baja lógica)",
)
def eliminar_categoria(
    categoria_id: int,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _admin: Usuario = Depends(require_role("ADMIN")),
):
    categoria = CategoriaService.eliminar_categoria(categoria_id, uow)
    return CategoriaRead.model_validate(categoria)
