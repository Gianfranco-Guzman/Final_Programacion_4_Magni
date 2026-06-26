from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.modules.auth.model import Usuario
from app.core.security import hash_password
from app.db.unit_of_work import UnitOfWork
from app.modules.admin.schemas import (
    AdminUserActionResponse,
    AdminUserCreateRequest,
    AdminUserListResponse,
    AdminUserRead,
    AdminUserRolesRequest,
    AdminUserUpdateRequest,
)
from app.modules.auth.schemas import RolResponse


class AdminService:
    @staticmethod
    def crear_usuario(data: AdminUserCreateRequest, uow: UnitOfWork) -> AdminUserActionResponse:
        if uow.usuarios.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese email",
            )

        roles_requested = list(dict.fromkeys(r.upper() for r in data.roles if r.strip()))
        if not roles_requested:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Debés enviar al menos un rol",
            )

        available_roles = uow.roles.get_by_names(roles_requested)
        available_by_name = {r.nombre: r for r in available_roles}
        missing = [r for r in roles_requested if r not in available_by_name]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Roles inexistentes: {', '.join(missing)}",
            )

        nuevo = Usuario(
            email=data.email,
            password_hash=hash_password(data.password),
            nombre=data.nombre,
            apellido=data.apellido,
            celular=data.celular,
            is_active=True,
        )
        uow.usuarios.save(nuevo)
        uow.flush()

        for role in available_roles:
            uow.roles.assign_to_user(nuevo.id, role.id)
        uow.flush()
        uow.refresh(nuevo)

        roles_resp = AdminService._obtener_roles(nuevo.id, uow)
        return AdminUserActionResponse(
            message="Usuario creado correctamente",
            usuario=AdminService._build_admin_user(nuevo, roles_resp),
        )

    @staticmethod
    def listar_usuarios(
        uow: UnitOfWork,
        page: int = 1,
        size: int = 20,
        rol: str | None = None,
    ) -> AdminUserListResponse:
        usuarios = uow.usuarios.list_ordered_by_created_desc()

        if rol:
            rol = rol.upper()

        usuarios_con_roles: list[AdminUserRead] = []
        for usuario in usuarios:
            roles = AdminService._obtener_roles(usuario.id, uow)
            if rol and rol not in [role.nombre for role in roles]:
                continue
            usuarios_con_roles.append(AdminService._build_admin_user(usuario, roles))

        total = len(usuarios_con_roles)
        pages = (total + size - 1) // size if total else 0
        start = (page - 1) * size
        end = start + size

        return AdminUserListResponse(
            items=usuarios_con_roles[start:end],
            total=total,
            page=page,
            size=size,
            pages=pages,
        )

    @staticmethod
    def actualizar_usuario(
        usuario_id: int,
        data: AdminUserUpdateRequest,
        current_admin: Usuario,
        uow: UnitOfWork,
    ) -> AdminUserRead:
        usuario = AdminService._obtener_usuario(usuario_id, uow)
        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != usuario.email:
            existing_user = uow.usuarios.get_by_email_excluding_id(update_data["email"], usuario_id)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe otro usuario con ese email",
                )

        if current_admin.id == usuario_id and update_data.get("is_active") is False:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No podés desactivar tu propio usuario desde el panel admin",
            )

        for field, value in update_data.items():
            setattr(usuario, field, value)

        usuario.updated_at = datetime.now(timezone.utc)
        uow.usuarios.save(usuario)
        uow.flush()
        uow.refresh(usuario)
        return AdminService._build_admin_user(usuario, AdminService._obtener_roles(usuario.id, uow))

    @staticmethod
    def dar_de_baja_usuario(
        usuario_id: int,
        current_admin: Usuario,
        uow: UnitOfWork,
    ) -> AdminUserActionResponse:
        if current_admin.id == usuario_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No podés darte de baja a vos mismo",
            )

        usuario = AdminService._obtener_usuario(usuario_id, uow)
        if usuario.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya está dado de baja",
            )

        now = datetime.now(timezone.utc)
        usuario.is_active = False
        usuario.deleted_at = now
        usuario.updated_at = now
        uow.usuarios.save(usuario)
        uow.flush()
        uow.refresh(usuario)

        return AdminUserActionResponse(
            message="Usuario dado de baja correctamente",
            usuario=AdminService._build_admin_user(usuario, AdminService._obtener_roles(usuario.id, uow)),
        )

    @staticmethod
    def reactivar_usuario(usuario_id: int, uow: UnitOfWork) -> AdminUserActionResponse:
        usuario = AdminService._obtener_usuario(usuario_id, uow)
        if usuario.deleted_at is None and usuario.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya está activo",
            )

        usuario.is_active = True
        usuario.deleted_at = None
        usuario.updated_at = datetime.now(timezone.utc)
        uow.usuarios.save(usuario)
        uow.flush()
        uow.refresh(usuario)

        return AdminUserActionResponse(
            message="Usuario reactivado correctamente",
            usuario=AdminService._build_admin_user(usuario, AdminService._obtener_roles(usuario.id, uow)),
        )

    @staticmethod
    def actualizar_roles(
        usuario_id: int,
        data: AdminUserRolesRequest,
        current_admin: Usuario,
        uow: UnitOfWork,
    ) -> AdminUserActionResponse:
        usuario = AdminService._obtener_usuario(usuario_id, uow)
        requested_roles = list(dict.fromkeys(role.upper() for role in data.roles if role.strip()))

        if not requested_roles:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Debés enviar al menos un rol válido",
            )

        available_roles = uow.roles.get_by_names(requested_roles)
        available_roles_by_name = {role.nombre: role for role in available_roles}
        missing_roles = [role for role in requested_roles if role not in available_roles_by_name]
        if missing_roles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Roles inexistentes: {', '.join(missing_roles)}",
            )

        if current_admin.id == usuario_id and "ADMIN" not in requested_roles:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No podés quitarte el rol ADMIN a vos mismo",
            )

        uow.roles.replace_roles_for_user(
            usuario.id,
            [available_roles_by_name[role_name].id for role_name in requested_roles],
        )

        usuario.updated_at = datetime.now(timezone.utc)
        uow.usuarios.save(usuario)
        uow.flush()
        uow.refresh(usuario)

        return AdminUserActionResponse(
            message="Roles actualizados correctamente",
            usuario=AdminService._build_admin_user(usuario, AdminService._obtener_roles(usuario.id, uow)),
        )

    @staticmethod
    def _obtener_usuario(usuario_id: int, uow: UnitOfWork) -> Usuario:
        usuario = uow.usuarios.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        return usuario

    @staticmethod
    def _obtener_roles(usuario_id: int, uow: UnitOfWork) -> list[RolResponse]:
        rows = uow.roles.get_rows_for_user(usuario_id)
        return [RolResponse(id=role_id, nombre=role_name) for role_id, role_name in rows]

    @staticmethod
    def _build_admin_user(usuario: Usuario, roles: list[RolResponse]) -> AdminUserRead:
        return AdminUserRead(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            celular=usuario.celular,
            is_active=usuario.is_active,
            created_at=usuario.created_at,
            updated_at=usuario.updated_at,
            deleted_at=usuario.deleted_at,
            roles=roles,
        )
