from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import require_role
from app.db.models.usuario import Usuario
from app.db.unit_of_work import UnitOfWork, get_uow
from app.modules.admin.schemas import (
    AdminUserActionResponse,
    AdminUserListResponse,
    AdminUserRolesRequest,
    AdminUserUpdateRequest,
)
from app.modules.admin.service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/usuarios/",
    response_model=AdminUserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios para administración",
)
def listar_usuarios(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    rol: str | None = Query(default=None, description="Filtrar por rol"),
    _admin: Usuario = Depends(require_role("ADMIN")),
    uow: UnitOfWork = Depends(get_uow),
) -> AdminUserListResponse:
    return AdminService.listar_usuarios(uow, page, size, rol)


@router.put(
    "/usuarios/{usuario_id}",
    response_model=AdminUserActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar datos básicos de usuario",
)
def actualizar_usuario(
    usuario_id: int,
    data: AdminUserUpdateRequest,
    current_admin: Usuario = Depends(require_role("ADMIN")),
    uow: UnitOfWork = Depends(get_uow),
) -> AdminUserActionResponse:
    usuario = AdminService.actualizar_usuario(usuario_id, data, current_admin, uow)
    return AdminUserActionResponse(message="Usuario actualizado correctamente", usuario=usuario)


@router.patch(
    "/usuarios/{usuario_id}/baja",
    response_model=AdminUserActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Dar de baja un usuario",
)
def dar_de_baja_usuario(
    usuario_id: int,
    current_admin: Usuario = Depends(require_role("ADMIN")),
    uow: UnitOfWork = Depends(get_uow),
) -> AdminUserActionResponse:
    return AdminService.dar_de_baja_usuario(usuario_id, current_admin, uow)


@router.patch(
    "/usuarios/{usuario_id}/reactivar",
    response_model=AdminUserActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Reactivar un usuario dado de baja",
)
def reactivar_usuario(
    usuario_id: int,
    _admin: Usuario = Depends(require_role("ADMIN")),
    uow: UnitOfWork = Depends(get_uow),
) -> AdminUserActionResponse:
    return AdminService.reactivar_usuario(usuario_id, uow)


@router.put(
    "/usuarios/{usuario_id}/roles",
    response_model=AdminUserActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Asignar roles a un usuario",
)
def actualizar_roles(
    usuario_id: int,
    data: AdminUserRolesRequest,
    current_admin: Usuario = Depends(require_role("ADMIN")),
    uow: UnitOfWork = Depends(get_uow),
) -> AdminUserActionResponse:
    return AdminService.actualizar_roles(usuario_id, data, current_admin, uow)
