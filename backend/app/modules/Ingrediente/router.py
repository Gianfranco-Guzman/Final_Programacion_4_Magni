from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.dependencies import get_current_user
from app.db.base import get_session
from app.db.models import Ingrediente
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.modules.Ingrediente.schemas import (
    IngredienteCreate,
    IngredienteRead,
    IngredienteUpdate,
)
from app.modules.Ingrediente.service import IngredienteService

router = APIRouter(tags=["ingredientes"])


@router.get(
    "/",
    response_model=list[IngredienteRead],
    summary="Listar todos los ingredientes",
)
def listar_ingredientes(session: Session = Depends(get_session)):
    ingredientes = session.exec(select(Ingrediente)).all()
    return [IngredienteRead.model_validate(i) for i in ingredientes]


@router.get(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    summary="Obtener ingrediente por ID",
)
def obtener_ingrediente(ingrediente_id: int, session: Session = Depends(get_session)):
    ingrediente = session.exec(
        select(Ingrediente).where(Ingrediente.id == ingrediente_id)
    ).first()
    if not ingrediente:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    return IngredienteRead.model_validate(ingrediente)


@router.post(
    "/",
    response_model=IngredienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear ingrediente",
)
def crear_ingrediente(
    data: IngredienteCreate,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    current_user: Usuario = Depends(get_current_user),
):
    ingrediente = IngredienteService.crear_ingrediente(data, uow)
    return IngredienteRead.model_validate(ingrediente)


@router.put(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    summary="Actualizar ingrediente",
)
def actualizar_ingrediente(
    ingrediente_id: int,
    data: IngredienteUpdate,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    current_user: Usuario = Depends(get_current_user),
):
    ingrediente = IngredienteService.actualizar_ingrediente(ingrediente_id, data, uow)
    return IngredienteRead.model_validate(ingrediente)


@router.delete(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    summary="Eliminar ingrediente",
)
def eliminar_ingrediente(
    ingrediente_id: int,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    current_user: Usuario = Depends(get_current_user),
):
    ingrediente = IngredienteService.eliminar_ingrediente(ingrediente_id, uow)
    return IngredienteRead.model_validate(ingrediente)
