from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class ProductoCategoria(SQLModel, table=True):

    __tablename__ = "producto_categoria"

    producto_id: int = Field(
        foreign_key="producto.id",
        primary_key=True,
        description="ID del producto"
    )
    categoria_id: int = Field(
        foreign_key="categoria.id",
        primary_key=True,
        description="ID de la categoría"
    )
    es_principal: bool = Field(
        default=False,
        description="Indica si es la categoría principal del producto"
    )

    producto: Optional["Producto"] = Relationship(back_populates="producto_categorias")
    categoria: Optional["Categoria"] = Relationship(back_populates="producto_categorias")
