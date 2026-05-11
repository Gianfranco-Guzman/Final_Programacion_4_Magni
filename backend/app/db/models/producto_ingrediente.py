from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class ProductoIngrediente(SQLModel, table=True):

    __tablename__ = "producto_ingrediente"

    producto_id: int = Field(
        foreign_key="producto.id",
        primary_key=True,
        description="ID del producto"
    )
    ingrediente_id: int = Field(
        foreign_key="ingrediente.id",
        primary_key=True,
        description="ID del ingrediente"
    )

    producto: Optional["Producto"] = Relationship(back_populates="ingredientes")
    ingrediente: Optional["Ingrediente"] = Relationship(back_populates="productos")
