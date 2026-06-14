from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FormaPagoBase(BaseModel):
    codigo: Optional[str] = Field(default=None, max_length=20)
    nombre: str = Field(..., min_length=1, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    activo: bool = Field(default=True)


class FormaPagoCreate(FormaPagoBase):
    pass


class FormaPagoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class FormaPagoRead(FormaPagoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
