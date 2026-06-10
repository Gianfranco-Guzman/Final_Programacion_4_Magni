from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import require_role
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.modules.ingredientes.schemas import (
    IngredienteCreate,
    IngredienteRead,
    IngredienteUpdate,
)
from app.modules.ingredientes.service import IngredienteService

router = APIRouter(tags=["ingredientes"])


@router.get(
    "/",
    response_model=list[IngredienteRead],
    summary="Listar todos los ingredientes",
)
def listar_ingredientes(uow: SqlModelUnitOfWork = Depends(get_uow)):
    ingredientes = uow.ingredientes.list_all()
    return [IngredienteRead.model_validate(i) for i in ingredientes]


@router.get(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    summary="Obtener ingrediente por ID",
)
def obtener_ingrediente(ingrediente_id: int, uow: SqlModelUnitOfWork = Depends(get_uow)):
    ingrediente = uow.ingredientes.get_active_by_id(ingrediente_id)
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
    _user: Usuario = Depends(require_role(["ADMIN"])),
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
    _user: Usuario = Depends(require_role(["ADMIN"])),
):
    ingrediente = IngredienteService.actualizar_ingrediente(ingrediente_id, data, uow)
    return IngredienteRead.model_validate(ingrediente)


@router.patch(
    "/{ingrediente_id}/baja",
    response_model=IngredienteRead,
    summary="Dar de baja ingrediente (soft delete)",
)
def dar_de_baja_ingrediente(
    ingrediente_id: int,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN"])),
):
    ingrediente = IngredienteService.dar_de_baja(ingrediente_id, uow)
    return IngredienteRead.model_validate(ingrediente)


@router.patch(
    "/{ingrediente_id}/reactivar",
    response_model=IngredienteRead,
    summary="Reactivar ingrediente dado de baja",
)
def reactivar_ingrediente(
    ingrediente_id: int,
    uow: SqlModelUnitOfWork = Depends(get_uow),
    _user: Usuario = Depends(require_role(["ADMIN"])),
):
    ingrediente = IngredienteService.reactivar(ingrediente_id, uow)
    return IngredienteRead.model_validate(ingrediente)
