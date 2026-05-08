from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaRead(CategoriaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio: float = Field(..., gt=0)
    stock_cantidad: int = Field(default=0, ge=0)
    categoria_id: int
    codigo: str = Field(..., min_length=1, max_length=50)


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: Optional[float] = Field(None, gt=0)
    stock_cantidad: Optional[int] = Field(None, ge=0)
    categoria_id: Optional[int] = None
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)


class ProductoRead(ProductoBase):
    id: int
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    categoria: Optional[CategoriaRead] = None

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int

    model_config = {"from_attributes": True}
