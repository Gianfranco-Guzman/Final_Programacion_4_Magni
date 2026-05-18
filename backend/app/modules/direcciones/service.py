from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import select

from app.db.models import DireccionEntrega
from app.db.models.usuario import Usuario
from app.db.unit_of_work import SqlModelUnitOfWork
from app.modules.direcciones.schemas import DireccionEntregaCreate, DireccionEntregaUpdate


class DireccionEntregaService:
    @staticmethod
    def listar_direcciones(usuario: Usuario, uow: SqlModelUnitOfWork) -> list[DireccionEntrega]:
        session = uow.session
        statement = (
            select(DireccionEntrega)
            .where(
                (DireccionEntrega.usuario_id == usuario.id)
                & (DireccionEntrega.deleted_at.is_(None))
            )
            .order_by(DireccionEntrega.es_principal.desc(), DireccionEntrega.created_at.asc())
        )
        return list(session.exec(statement).all())

    @staticmethod
    def obtener_direccion(direccion_id: int, usuario: Usuario, uow: SqlModelUnitOfWork) -> DireccionEntrega:
        direccion = DireccionEntregaService._obtener_direccion_activa(direccion_id, usuario, uow)
        if not direccion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dirección no encontrada")
        return direccion

    @staticmethod
    def crear_direccion(data: DireccionEntregaCreate, usuario: Usuario, uow: SqlModelUnitOfWork) -> DireccionEntrega:
        session = uow.session
        now = datetime.now(timezone.utc)
        debe_ser_principal = data.es_principal or not DireccionEntregaService._usuario_tiene_direccion_activa(usuario.id, uow)

        if debe_ser_principal:
            DireccionEntregaService._limpiar_principal(usuario.id, uow)

        direccion = DireccionEntrega(
            usuario_id=usuario.id,
            etiqueta=data.etiqueta,
            linea1=data.linea1,
            linea2=data.linea2,
            ciudad=data.ciudad,
            latitud=data.latitud,
            longitud=data.longitud,
            es_principal=debe_ser_principal,
            created_at=now,
            updated_at=now,
        )
        session.add(direccion)
        uow.flush()
        uow.refresh(direccion)
        return direccion

    @staticmethod
    def actualizar_direccion(
        direccion_id: int,
        data: DireccionEntregaUpdate,
        usuario: Usuario,
        uow: SqlModelUnitOfWork,
    ) -> DireccionEntrega:
        session = uow.session
        direccion = DireccionEntregaService.obtener_direccion(direccion_id, usuario, uow)
        update_data = data.model_dump(exclude_unset=True)
        es_principal = update_data.pop("es_principal", None)

        for field, value in update_data.items():
            setattr(direccion, field, value)

        if es_principal is True:
            DireccionEntregaService._limpiar_principal(usuario.id, uow)
            direccion.es_principal = True
        elif es_principal is False:
            otras_activas = DireccionEntregaService._otras_direcciones_activas(usuario.id, direccion.id, uow)
            if not otras_activas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debes conservar al menos una dirección principal activa",
                )
            direccion.es_principal = False

        direccion.updated_at = datetime.now(timezone.utc)
        session.add(direccion)
        uow.flush()
        uow.refresh(direccion)
        return direccion

    @staticmethod
    def marcar_principal(direccion_id: int, usuario: Usuario, uow: SqlModelUnitOfWork) -> DireccionEntrega:
        session = uow.session
        direccion = DireccionEntregaService.obtener_direccion(direccion_id, usuario, uow)
        DireccionEntregaService._limpiar_principal(usuario.id, uow)
        direccion.es_principal = True
        direccion.updated_at = datetime.now(timezone.utc)
        session.add(direccion)
        uow.flush()
        uow.refresh(direccion)
        return direccion

    @staticmethod
    def eliminar_direccion(direccion_id: int, usuario: Usuario, uow: SqlModelUnitOfWork) -> DireccionEntrega:
        session = uow.session
        direccion = DireccionEntregaService.obtener_direccion(direccion_id, usuario, uow)
        direccion.deleted_at = datetime.now(timezone.utc)
        direccion.updated_at = direccion.deleted_at
        direccion.es_principal = False
        session.add(direccion)
        uow.flush()

        activa_restante = DireccionEntregaService.listar_direcciones(usuario, uow)
        if activa_restante and not any(item.es_principal for item in activa_restante):
            primera = activa_restante[0]
            primera.es_principal = True
            primera.updated_at = datetime.now(timezone.utc)
            session.add(primera)
            uow.flush()

        return direccion

    @staticmethod
    def _obtener_direccion_activa(direccion_id: int, usuario: Usuario, uow: SqlModelUnitOfWork) -> DireccionEntrega | None:
        session = uow.session
        statement = select(DireccionEntrega).where(
            (DireccionEntrega.id == direccion_id)
            & (DireccionEntrega.usuario_id == usuario.id)
            & (DireccionEntrega.deleted_at.is_(None))
        )
        return session.exec(statement).first()

    @staticmethod
    def _limpiar_principal(usuario_id: int, uow: SqlModelUnitOfWork) -> None:
        session = uow.session
        statement = select(DireccionEntrega).where(
            (DireccionEntrega.usuario_id == usuario_id)
            & (DireccionEntrega.deleted_at.is_(None))
            & (DireccionEntrega.es_principal.is_(True))
        )
        for direccion in session.exec(statement).all():
            direccion.es_principal = False
            direccion.updated_at = datetime.now(timezone.utc)
            session.add(direccion)

    @staticmethod
    def _usuario_tiene_direccion_activa(usuario_id: int, uow: SqlModelUnitOfWork) -> bool:
        session = uow.session
        statement = select(DireccionEntrega).where(
            (DireccionEntrega.usuario_id == usuario_id)
            & (DireccionEntrega.deleted_at.is_(None))
        )
        return session.exec(statement).first() is not None

    @staticmethod
    def _otras_direcciones_activas(usuario_id: int, direccion_id: int, uow: SqlModelUnitOfWork) -> list[DireccionEntrega]:
        session = uow.session
        statement = select(DireccionEntrega).where(
            (DireccionEntrega.usuario_id == usuario_id)
            & (DireccionEntrega.id != direccion_id)
            & (DireccionEntrega.deleted_at.is_(None))
        )
        return list(session.exec(statement).all())
