from sqlmodel import select

from app.core.repositories.base import BaseRepository
from app.db.models.usuario import Usuario


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
