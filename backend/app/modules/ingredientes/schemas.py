from decimal import Decimal
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.db.models.enums import UnidadMedida


class IngredienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    es_alergeno: bool = Field(default=False)
    unidad_medida: UnidadMedida = Field(default=UnidadMedida.UNIDAD)
    stock_actual: Decimal = Field(default=Decimal("0"), ge=0)
    stock_minimo: Decimal = Field(default=Decimal("0"), ge=0)
    costo_unitario: Decimal = Field(default=Decimal("0"), ge=0)
    permite_fraccion: bool = Field(default=False)


class IngredienteCreate(IngredienteBase):
    pass


class IngredienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    es_alergeno: Optional[bool] = None
    unidad_medida: Optional[UnidadMedida] = None
    stock_actual: Optional[Decimal] = Field(None, ge=0)
    stock_minimo: Optional[Decimal] = Field(None, ge=0)
    costo_unitario: Optional[Decimal] = Field(None, ge=0)
    permite_fraccion: Optional[bool] = None


class IngredienteRead(IngredienteBase):
    id: int
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
