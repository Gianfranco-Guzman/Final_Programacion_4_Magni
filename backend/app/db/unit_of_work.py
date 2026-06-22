from sqlmodel import Session

from app.core.repositories import (
    CategoriaRepository,
    DireccionRepository,
    EstadisticaRepository,
    FormaPagoRepository,
    IngredienteRepository,
    MovimientoStockIngredienteRepository,
    PagoRepository,
    PedidoRepository,
    ProductoRepository,
    RefreshTokenRepository,
    RolRepository,
    UsuarioRepository,
)
from app.db.base import engine


class UnitOfWork:

    def __init__(self):
        self.session = Session(engine)
        self.formas_pago = FormaPagoRepository(self.session)
        self.direcciones = DireccionRepository(self.session)
        self.estadisticas = EstadisticaRepository(self.session)
        self.categorias = CategoriaRepository(self.session)
        self.usuarios = UsuarioRepository(self.session)
        self.roles = RolRepository(self.session)
        self.ingredientes = IngredienteRepository(self.session)
        self.movimientos_stock_ingredientes = MovimientoStockIngredienteRepository(self.session)
        self.pagos = PagoRepository(self.session)
        self.productos = ProductoRepository(self.session)
        self.pedidos = PedidoRepository(self.session)
        self.refresh_tokens = RefreshTokenRepository(self.session)
        self._after_commit_callbacks: list[callable] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._after_commit_callbacks.clear()
            self.session.rollback()
        else:
            self.session.commit()
            callbacks = list(self._after_commit_callbacks)
            self._after_commit_callbacks.clear()
            for callback in callbacks:
                try:
                    callback()
                except Exception as exc:
                    print(f"[WARN] Realtime callback failed after commit: {exc}")
        self.session.close()

    def flush(self) -> None:
        self.session.flush()

    def refresh(self, instance: object) -> None:
        self.session.refresh(instance)

    def add_after_commit(self, callback: callable) -> None:
        self._after_commit_callbacks.append(callback)


def get_uow():
    with UnitOfWork() as uow:
        yield uow
