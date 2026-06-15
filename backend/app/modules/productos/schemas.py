from decimal import Decimal
from datetime import datetime
from typing import Optional

from pydantic import AliasChoices, BaseModel, Field, field_validator

from app.db.models.enums import TipoProducto, UnidadMedida


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
    unidad_medida: UnidadMedida = Field(default=UnidadMedida.UNIDAD)
    stock_actual: Decimal = Field(default=Decimal("0"), ge=0)
    stock_minimo: Decimal = Field(default=Decimal("0"), ge=0)
    costo_unitario: Decimal = Field(default=Decimal("0"), ge=0)
    permite_fraccion: bool = Field(default=False)


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


class ProductoDetallePayload(BaseModel):
    ingrediente_id: int = Field(..., ge=1)
    cantidad: Decimal = Field(..., gt=0)
    unidad_medida: UnidadMedida
    orden: int = Field(default=1, ge=1)
    es_removible: bool = Field(default=True)
    es_opcional: bool = Field(default=False)


class ProductoDetalleRead(BaseModel):
    id: Optional[int] = None
    ingrediente_id: int
    cantidad: Decimal
    unidad_medida: UnidadMedida
    orden: int
    es_removible: bool
    es_opcional: bool
    ingrediente: IngredienteRead

    model_config = {"from_attributes": True}


class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio_venta: Decimal = Field(
        ...,
        gt=0,
        validation_alias=AliasChoices("precio_venta", "precio"),
    )
    codigo: str = Field(..., min_length=1, max_length=50)
    disponible: bool = Field(default=True)
    tipo_producto: TipoProducto = Field(default=TipoProducto.FABRICADO)
    descuento_porcentaje: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    imagenes_url: Optional[list[str]] = None
    unidad_venta_id: Optional[int] = Field(default=None, ge=1)

    @property
    def precio(self) -> Decimal:
        return self.precio_venta


class ProductoCreate(ProductoBase):
    categorias: list[ProductoCategoriaPayload] = Field(..., min_length=1, description="Clasificación del producto en categorías")
    ingredientes: list[ProductoDetallePayload] = Field(..., min_length=1, description="Detalle de receta o stock base del producto")

    @field_validator("ingredientes")
    @classmethod
    def validar_ingredientes_para_tipo(cls, value: list[ProductoDetallePayload], info):
        tipo_producto = info.data.get("tipo_producto", TipoProducto.FABRICADO)
        if tipo_producto == TipoProducto.REVENTA and len(value) != 1:
            raise ValueError("Un producto de reventa debe tener exactamente 1 ingrediente asociado")
        return value


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio_venta: Optional[Decimal] = Field(
        None,
        gt=0,
        validation_alias=AliasChoices("precio_venta", "precio"),
    )
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    disponible: Optional[bool] = None
    tipo_producto: Optional[TipoProducto] = None
    descuento_porcentaje: Optional[Decimal] = Field(None, ge=0, le=100)
    imagenes_url: Optional[list[str]] = None
    unidad_venta_id: Optional[int] = Field(default=None, ge=1)
    categorias: Optional[list[ProductoCategoriaPayload]] = None
    ingredientes: Optional[list[ProductoDetallePayload]] = None

    @property
    def precio(self) -> Optional[Decimal]:
        return self.precio_venta


class ProductoRead(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio_venta: Decimal = Field(validation_alias=AliasChoices("precio_venta", "precio"))
    precio_costo_calculado: Decimal = Field(default=Decimal("0"))
    descuento_porcentaje: Decimal = Field(default=Decimal("0"))
    precio_final: Decimal = Field(default=Decimal("0"))
    tipo_producto: TipoProducto = Field(default=TipoProducto.FABRICADO)
    stock_disponible_calculado: int = 0
    puede_fabricarse: bool = False
    categoria_principal_id: Optional[int] = None
    codigo: str
    disponible: bool
    imagenes_url: Optional[list[str]] = None
    unidad_venta_id: Optional[int] = None
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    categorias: list[ProductoCategoriaRead] = Field(default_factory=list)
    ingredientes: list[ProductoDetalleRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}

    @property
    def precio(self) -> Decimal:
        return self.precio_venta


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int

    model_config = {"from_attributes": True}
