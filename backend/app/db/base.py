from sqlalchemy import text
from sqlmodel import create_engine, SQLModel, Session
from app.core.config import get_settings

from app.db import models as db_models  # noqa: F401

settings = get_settings()

# crear engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True, 
)


def create_all_tables() -> None:
    SQLModel.metadata.create_all(engine)
    _ensure_identity_schema()
    _ensure_product_schema()
    _backfill_producto_categoria()


def _ensure_identity_schema() -> None:
    statements = [
        "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS apellido VARCHAR(80) NOT NULL DEFAULT ''",
        "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS celular VARCHAR(20)",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def _ensure_product_schema() -> None:
    statements = [
        "ALTER TABLE producto ADD COLUMN IF NOT EXISTS disponible BOOLEAN NOT NULL DEFAULT true",
        "ALTER TABLE producto_ingrediente ADD COLUMN IF NOT EXISTS es_removible BOOLEAN NOT NULL DEFAULT true",
        "ALTER TABLE producto_ingrediente ADD COLUMN IF NOT EXISTS es_opcional BOOLEAN NOT NULL DEFAULT false",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def _backfill_producto_categoria() -> None:
    statement = """
    INSERT INTO producto_categoria (producto_id, categoria_id, es_principal)
    SELECT p.id, p.categoria_id, TRUE
    FROM producto p
    WHERE p.categoria_id IS NOT NULL
      AND NOT EXISTS (
        SELECT 1
        FROM producto_categoria pc
        WHERE pc.producto_id = p.id AND pc.categoria_id = p.categoria_id
      )
    """

    with engine.begin() as connection:
        connection.execute(text(statement))


def get_session() -> Session:

    with Session(engine) as session:
        yield session
