from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.dependencies import get_current_user
from app.db.base import get_session
from app.db.models import Categoria
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.modules.Categoria.schemas import (
    CategoriaCreate,
    CategoriaRead,
    CategoriaUpdate,
)
from app.modules.Categoria.service import CategoriaService

router = APIRouter(tags=["categorias"])


@router.get(
    "/",
    response_model=list[CategoriaRead],
    summary="Listar todas las categorías",
)
def listar_categorias(session: Session = Depends(get_session)):
    categorias = session.exec(select(Categoria)).all()
    return [CategoriaRead.model_validate(c) for c in categorias]


@router.get(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Obtener categoría por ID",
)
def obtener_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = session.exec(
        select(Categoria).where(Categoria.id == categoria_id)
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
    current_user: Usuario = Depends(get_current_user),
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
    current_user: Usuario = Depends(get_current_user),
):
    categoria = CategoriaService.actualizar_categoria(categoria_id, data, uow)
    return CategoriaRead.model_validate(categoria)


@router.delete(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Eliminar categoría",
)
def eliminar_categoria(
    categoria_id: int,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    current_user: Usuario = Depends(get_current_user),
):
    categoria = CategoriaService.eliminar_categoria(categoria_id, uow)
    return CategoriaRead.model_validate(categoria)
