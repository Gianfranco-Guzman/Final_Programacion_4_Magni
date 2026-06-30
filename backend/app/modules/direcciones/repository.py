from datetime import datetime, timezone

from sqlmodel import select

from app.db.base_repository import BaseRepository
from app.modules.direcciones.model import DireccionEntrega


class DireccionRepository(BaseRepository):
    def list_active_for_user(self, usuario_id: int) -> list[DireccionEntrega]:
        statement = (
            select(DireccionEntrega)
            .where(
                (DireccionEntrega.usuario_id == usuario_id)
                & (DireccionEntrega.deleted_at.is_(None))
            )
            .order_by(DireccionEntrega.es_principal.desc(), DireccionEntrega.created_at.asc())
        )
        return list(self.session.exec(statement).all())

    def get_active_for_user(self, direccion_id: int, usuario_id: int) -> DireccionEntrega | None:
        statement = select(DireccionEntrega).where(
            (DireccionEntrega.id == direccion_id)
            & (DireccionEntrega.usuario_id == usuario_id)
            & (DireccionEntrega.deleted_at.is_(None))
        )
        return self.session.exec(statement).first()

    def unset_primary_for_user(self, usuario_id: int) -> None:
        statement = select(DireccionEntrega).where(
            (DireccionEntrega.usuario_id == usuario_id)
            & (DireccionEntrega.deleted_at.is_(None))
            & (DireccionEntrega.es_principal.is_(True))
        )
        for direccion in self.session.exec(statement).all():
            direccion.es_principal = False
            direccion.updated_at = datetime.now(timezone.utc)
            self.add(direccion)

    def user_has_active_address(self, usuario_id: int) -> bool:
        statement = select(DireccionEntrega).where(
            (DireccionEntrega.usuario_id == usuario_id)
            & (DireccionEntrega.deleted_at.is_(None))
        )
        return self.session.exec(statement).first() is not None

    def list_other_active_for_user(self, usuario_id: int, direccion_id: int) -> list[DireccionEntrega]:
        statement = select(DireccionEntrega).where(
            (DireccionEntrega.usuario_id == usuario_id)
            & (DireccionEntrega.id != direccion_id)
            & (DireccionEntrega.deleted_at.is_(None))
        )
        return list(self.session.exec(statement).all())
