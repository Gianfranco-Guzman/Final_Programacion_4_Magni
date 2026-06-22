from sqlmodel import select

from app.core.base_repository import BaseRepository
from app.modules.pagos.model import Pago


class PagoRepository(BaseRepository):
    def get_by_id(self, pago_id: int) -> Pago | None:
        return self.get(Pago, pago_id)

    def get_by_pedido_id(self, pedido_id: int) -> Pago | None:
        statement = select(Pago).where(Pago.pedido_id == pedido_id)
        return self.session.exec(statement).first()

    def get_by_mp_payment_id(self, mp_payment_id: int) -> Pago | None:
        statement = select(Pago).where(Pago.mp_payment_id == mp_payment_id)
        return self.session.exec(statement).first()

    def get_by_external_reference(self, external_reference: str) -> Pago | None:
        statement = select(Pago).where(Pago.external_reference == external_reference)
        return self.session.exec(statement).first()

    def save(self, pago: Pago) -> Pago:
        return self.add(pago)
