from sqlmodel import Session

from app.core.database import engine
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.categorias.repository import CategoriaRepository


class UnitOfWork:

    def __init__(self):
        self.session: Session | None = None

    def __enter__(self):
        self.session = Session(engine)
        self.usuarios = UsuarioRepository(self.session)
        self.categorias = CategoriaRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

    def commit(self):

        self.session.commit()

    def rollback(self):

        self.session.rollback()


def get_uow() -> UnitOfWork:
    return UnitOfWork()
