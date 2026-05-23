from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class DireccionEntrega(SQLModel, table=True):

    __tablename__ = "direccion_entrega"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(
        foreign_key="usuario.id",
        index=True,
        description="Usuario propietario de la dirección"
    )
    etiqueta: Optional[str] = Field(
        default=None,
        max_length=80,
        description="Alias de la dirección: Casa, Trabajo, etc."
    )
    linea1: str = Field(
        max_length=255,
        description="Línea principal de la dirección"
    )
    linea2: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Detalles adicionales de la dirección"
    )
    ciudad: str = Field(
        max_length=100,
        description="Ciudad de entrega"
    )
    latitud: Optional[float] = Field(
        default=None,
        description="Latitud de la dirección"
    )
    longitud: Optional[float] = Field(
        default=None,
        description="Longitud de la dirección"
    )
    es_principal: bool = Field(
        default=False,
        description="Indica si es la dirección principal del usuario"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de creación"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de actualización"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Fecha de eliminación lógica"
    )

    usuario: Optional["Usuario"] = Relationship(back_populates="direcciones")
