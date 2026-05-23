from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Categoria(SQLModel, table=True):

    __tablename__ = "categoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(
        index=True,
        unique=True,
        max_length=100,
        description="Nombre único de la categoría"
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Descripción de la categoría"
    )
    parent_id: Optional[int] = Field(
        default=None,
        foreign_key="categoria.id",
        index=True,
        description="ID de la categoría padre para jerarquías"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Fecha de eliminación lógica (soft delete)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de creación"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de última actualización"
    )

    producto_categorias: list["ProductoCategoria"] = Relationship(back_populates="categoria")
    parent: Optional["Categoria"] = Relationship(
        back_populates="subcategorias",
        sa_relationship_kwargs={"remote_side": "Categoria.id"},
    )
    subcategorias: list["Categoria"] = Relationship(back_populates="parent")

    def __repr__(self) -> str:
        return f"<Categoria id={self.id} nombre={self.nombre}>"
