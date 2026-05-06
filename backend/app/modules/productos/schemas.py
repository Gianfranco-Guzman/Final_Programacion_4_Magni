from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CategoriaBase(BaseModel):
    """Base schema para Categoría"""
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)


class CategoriaCreate(CategoriaBase):
    """Schema para crear categoría"""
    pass


class CategoriaRead(CategoriaBase):
    """Schema para leer categoría"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductoBase(BaseModel):
    """Base schema para Producto"""
    nombre: str = Field(..., min_length=1, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio: float = Field(..., gt=0)
    stock_cantidad: int = Field(default=0, ge=0)
    categoria_id: int
    codigo: str = Field(..., min_length=1, max_length=50)


class ProductoCreate(ProductoBase):
    """Schema para crear producto"""
    pass


class ProductoUpdate(BaseModel):
    """Schema para actualizar producto"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: Optional[float] = Field(None, gt=0)
    stock_cantidad: Optional[int] = Field(None, ge=0)
    categoria_id: Optional[int] = None
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)


class ProductoRead(ProductoBase):
    """Schema para leer producto"""
    id: int
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    categoria: Optional[CategoriaRead] = None

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Schema para respuestas paginadas"""
    items: list
    total: int
    page: int
    size: int
    pages: int

    class Config:
        from_attributes = True
