from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DireccionEntregaBase(BaseModel):
    etiqueta: Optional[str] = Field(default=None, max_length=80)
    linea1: str = Field(..., min_length=3, max_length=255)
    linea2: Optional[str] = Field(default=None, max_length=255)
    ciudad: str = Field(..., min_length=2, max_length=100)
    latitud: Optional[float] = Field(default=None, ge=-90, le=90)
    longitud: Optional[float] = Field(default=None, ge=-180, le=180)
    es_principal: bool = Field(default=False)


class DireccionEntregaCreate(DireccionEntregaBase):
    pass


class DireccionEntregaUpdate(BaseModel):
    etiqueta: Optional[str] = Field(default=None, max_length=80)
    linea1: Optional[str] = Field(default=None, min_length=3, max_length=255)
    linea2: Optional[str] = Field(default=None, max_length=255)
    ciudad: Optional[str] = Field(default=None, min_length=2, max_length=100)
    latitud: Optional[float] = Field(default=None, ge=-90, le=90)
    longitud: Optional[float] = Field(default=None, ge=-180, le=180)
    es_principal: Optional[bool] = None


class DireccionEntregaRead(DireccionEntregaBase):
    id: int
    usuario_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
