from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class UnidadMedidaCatalogo(SQLModel, table=True):

    __tablename__ = "unidad_medida"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True, max_length=50)
    simbolo: str = Field(index=True, unique=True, max_length=10)
    tipo: str = Field(max_length=20)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
