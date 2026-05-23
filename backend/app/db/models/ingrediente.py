from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Ingrediente(SQLModel, table=True):

    __tablename__ = "ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(
        index=True,
        unique=True,
        max_length=100,
        description="Nombre único del ingrediente"
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Descripción del ingrediente"
    )
    es_alergeno: bool = Field(
        default=False,
        description="Indica si el ingrediente es un alérgeno común"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de creación"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de última actualización"
    )

    productos: list["ProductoIngrediente"] = Relationship(back_populates="ingrediente")

    def __repr__(self) -> str:
        return f"<Ingrediente id={self.id} nombre={self.nombre}>"
