from sqlmodel import select

from app.core.repositories.base import BaseRepository
from app.db.models.forma_pago import FormaPago


class FormaPagoRepository(BaseRepository):
    def get_by_id(self, forma_pago_id: int) -> FormaPago | None:
        return self.get(FormaPago, forma_pago_id)

    def get_active_by_id(self, forma_pago_id: int) -> FormaPago | None:
        statement = select(FormaPago).where(
            (FormaPago.id == forma_pago_id) & (FormaPago.activo == True)
        )
        return self.session.exec(statement).first()

    def get_by_name(self, nombre: str) -> FormaPago | None:
        statement = select(FormaPago).where(FormaPago.nombre == nombre)
        return self.session.exec(statement).first()

    def get_by_name_excluding_id(self, nombre: str, forma_pago_id: int) -> FormaPago | None:
        statement = select(FormaPago).where(
            (FormaPago.nombre == nombre) & (FormaPago.id != forma_pago_id)
        )
        return self.session.exec(statement).first()

    def list_active_ordered(self) -> list[FormaPago]:
        statement = select(FormaPago).where(FormaPago.activo == True).order_by(FormaPago.nombre)
        return list(self.session.exec(statement).all())
