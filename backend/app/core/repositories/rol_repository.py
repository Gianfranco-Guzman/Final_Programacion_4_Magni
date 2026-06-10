from sqlmodel import select

from app.core.repositories.base import BaseRepository
from app.db.models.rol import Rol
from app.db.models.usuario import UsuarioRol


class RolRepository(BaseRepository):
    def get_by_name(self, nombre: str) -> Rol | None:
        statement = select(Rol).where(Rol.nombre == nombre)
        return self.session.exec(statement).first()

    def get_by_names(self, nombres: list[str]) -> list[Rol]:
        if not nombres:
            return []
        statement = select(Rol).where(Rol.nombre.in_(nombres))
        return list(self.session.exec(statement).all())

    def get_names_for_user(self, usuario_id: int) -> list[str]:
        statement = (
            select(Rol.nombre)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .where(UsuarioRol.usuario_id == usuario_id)
        )
        return list(self.session.exec(statement).all())

    def get_rows_for_user(self, usuario_id: int) -> list[tuple[int, str]]:
        statement = (
            select(Rol.id, Rol.nombre)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .where(UsuarioRol.usuario_id == usuario_id)
        )
        return list(self.session.exec(statement).all())

    def assign_to_user(self, usuario_id: int, rol_id: int) -> UsuarioRol:
        return self.add(UsuarioRol(usuario_id=usuario_id, rol_id=rol_id))

    def replace_roles_for_user(self, usuario_id: int, rol_ids: list[int]) -> None:
        existing_relations = self.session.exec(
            select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
        ).all()
        for relation in existing_relations:
            self.delete(relation)

        for rol_id in rol_ids:
            self.assign_to_user(usuario_id, rol_id)

    def user_has_any_role(self, usuario_id: int, roles: list[str]) -> bool:
        user_roles = self.get_names_for_user(usuario_id)
        return any(role in roles for role in user_roles)
