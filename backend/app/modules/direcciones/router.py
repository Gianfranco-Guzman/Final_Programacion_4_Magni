from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.db.models.usuario import Usuario
from app.db.unit_of_work import UnitOfWork, get_uow
from app.modules.direcciones.schemas import (
    DireccionEntregaCreate,
    DireccionEntregaRead,
    DireccionEntregaUpdate,
)
from app.modules.direcciones.service import DireccionEntregaService

router = APIRouter(prefix="/direcciones", tags=["direcciones"])


@router.get("/", response_model=list[DireccionEntregaRead], summary="Listar direcciones del usuario")
def listar_direcciones(
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    direcciones = DireccionEntregaService.listar_direcciones(current_user, uow)
    return [DireccionEntregaRead.model_validate(direccion) for direccion in direcciones]


@router.get("/{direccion_id}", response_model=DireccionEntregaRead, summary="Obtener dirección por ID")
def obtener_direccion(
    direccion_id: int,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    direccion = DireccionEntregaService.obtener_direccion(direccion_id, current_user, uow)
    return DireccionEntregaRead.model_validate(direccion)


@router.post("/", response_model=DireccionEntregaRead, status_code=status.HTTP_201_CREATED, summary="Crear dirección")
def crear_direccion(
    data: DireccionEntregaCreate,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    direccion = DireccionEntregaService.crear_direccion(data, current_user, uow)
    return DireccionEntregaRead.model_validate(direccion)


@router.put("/{direccion_id}", response_model=DireccionEntregaRead, summary="Actualizar dirección")
def actualizar_direccion(
    direccion_id: int,
    data: DireccionEntregaUpdate,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    direccion = DireccionEntregaService.actualizar_direccion(direccion_id, data, current_user, uow)
    return DireccionEntregaRead.model_validate(direccion)


@router.patch("/{direccion_id}/principal", response_model=DireccionEntregaRead, summary="Marcar dirección como principal")
def marcar_principal(
    direccion_id: int,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    direccion = DireccionEntregaService.marcar_principal(direccion_id, current_user, uow)
    return DireccionEntregaRead.model_validate(direccion)


@router.delete("/{direccion_id}", response_model=DireccionEntregaRead, summary="Eliminar dirección")
def eliminar_direccion(
    direccion_id: int,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    direccion = DireccionEntregaService.eliminar_direccion(direccion_id, current_user, uow)
    return DireccionEntregaRead.model_validate(direccion)
