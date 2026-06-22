from datetime import datetime, timezone

from sqlmodel import select

from app.core.base_repository import BaseRepository
from app.modules.auth.model import RefreshToken, Rol, Usuario, UsuarioRol


class UsuarioRepository(BaseRepository):
    def get_by_id(self, usuario_id: int) -> Usuario | None:
        statement = select(Usuario).where(Usuario.id == usuario_id)
        return self.session.exec(statement).first()

    def get_by_email(self, email: str) -> Usuario | None:
        statement = select(Usuario).where(Usuario.email == email)
        return self.session.exec(statement).first()

    def get_by_email_excluding_id(self, email: str, usuario_id: int) -> Usuario | None:
        statement = select(Usuario).where(
            (Usuario.email == email) & (Usuario.id != usuario_id)
        )
        return self.session.exec(statement).first()

    def list_all(self) -> list[Usuario]:
        statement = select(Usuario)
        return list(self.session.exec(statement).all())

    def list_ordered_by_created_desc(self) -> list[Usuario]:
        statement = select(Usuario).order_by(Usuario.created_at.desc())
        return list(self.session.exec(statement).all())

    def save(self, usuario: Usuario) -> Usuario:
        return self.add(usuario)


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


class RefreshTokenRepository(BaseRepository):
    def save(self, refresh_token: RefreshToken) -> RefreshToken:
        return self.add(refresh_token)

    def get_active_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(
            (RefreshToken.token_hash == token_hash)
            & (RefreshToken.revoked_at.is_(None))
        )
        token = self.session.exec(statement).first()
        if token and token.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
            return None
        return token

    def revoke(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked_at = datetime.now(timezone.utc)
        self.add(refresh_token)
