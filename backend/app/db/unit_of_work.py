from sqlmodel import Session

from app.core.repositories import (
    CategoriaRepository,
    DireccionRepository,
    FormaPagoRepository,
    IngredienteRepository,
    MovimientoStockIngredienteRepository,
    PedidoRepository,
    ProductoRepository,
    RolRepository,
    UsuarioRepository,
)
from app.db.base import engine


class SqlModelUnitOfWork:

    def __init__(self, session: Session):
        self.session = session
        self.formas_pago = FormaPagoRepository(session)
        self.direcciones = DireccionRepository(session)
        self.categorias = CategoriaRepository(session)
        self.usuarios = UsuarioRepository(session)
        self.roles = RolRepository(session)
        self.ingredientes = IngredienteRepository(session)
        self.movimientos_stock_ingredientes = MovimientoStockIngredienteRepository(session)
        self.productos = ProductoRepository(session)
        self.pedidos = PedidoRepository(session)
        self._after_commit_callbacks: list[callable] = []

    def commit(self) -> None:
        self.session.commit()
        callbacks = list(self._after_commit_callbacks)
        self._after_commit_callbacks.clear()
        for callback in callbacks:
            try:
                callback()
            except Exception as exc:
                print(f"[WARN] Realtime callback failed after commit: {exc}")

    def rollback(self) -> None:
        self._after_commit_callbacks.clear()
        self.session.rollback()

    def flush(self) -> None:
        self.session.flush()

    def refresh(self, instance: object) -> None:
        self.session.refresh(instance)

    def add_after_commit(self, callback: callable) -> None:
        self._after_commit_callbacks.append(callback)


def get_uow():
    session = Session(engine)
    uow = SqlModelUnitOfWork(session)
    try:
        yield uow
        uow.commit()
    except Exception:
        uow.rollback()
        raise
    finally:
        session.close()
