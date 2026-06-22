from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    parent_id: Optional[int] = Field(default=None, ge=1)


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = Field(default=None, ge=1)


class CategoriaRead(CategoriaBase):
    id: int
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    subcategorias: list["CategoriaRead"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class CategoriaListResponse(BaseModel):
    items: list[CategoriaRead]
    total: int
    page: int
    size: int
    pages: int

    model_config = {"from_attributes": True}
