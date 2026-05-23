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


class IngredienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    es_alergeno: bool = Field(default=False)


class IngredienteRead(IngredienteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductoCategoriaPayload(BaseModel):
    categoria_id: int = Field(..., ge=1)
    es_principal: bool = Field(default=False)


class ProductoCategoriaRead(BaseModel):
    categoria_id: int
    es_principal: bool
    categoria: CategoriaRead

    model_config = {"from_attributes": True}


class ProductoIngredientePayload(BaseModel):
    ingrediente_id: int = Field(..., ge=1)
    es_removible: bool = Field(default=True)
    es_opcional: bool = Field(default=False)


class ProductoIngredienteRead(BaseModel):
    ingrediente_id: int
    es_removible: bool
    es_opcional: bool
    ingrediente: IngredienteRead

    model_config = {"from_attributes": True}


class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio: float = Field(..., gt=0)
    stock_cantidad: int = Field(default=0, ge=0)
    codigo: str = Field(..., min_length=1, max_length=50)
    disponible: bool = Field(default=True)


class ProductoCreate(ProductoBase):
    categorias: list[ProductoCategoriaPayload] = Field(..., min_length=1, description="Clasificación del producto en categorías")
    ingredientes: list[ProductoIngredientePayload] = Field(..., min_length=1, description="Configuración de ingredientes del producto")


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: Optional[float] = Field(None, gt=0)
    stock_cantidad: Optional[int] = Field(None, ge=0)
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    disponible: Optional[bool] = None
    categorias: Optional[list[ProductoCategoriaPayload]] = None
    ingredientes: Optional[list[ProductoIngredientePayload]] = None


class ProductoRead(ProductoBase):
    id: int
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    categoria_principal_id: Optional[int] = None
    categorias: list[ProductoCategoriaRead] = Field(default_factory=list)
    ingredientes: list[ProductoIngredienteRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int

    model_config = {"from_attributes": True}
