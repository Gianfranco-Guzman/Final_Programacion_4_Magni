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


def _ensure_identity_schema() -> None:
    statements = [
        "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS apellido VARCHAR(80) NOT NULL DEFAULT ''",
        "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS celular VARCHAR(20)",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def get_session() -> Session:

    with Session(engine) as session:
        yield session
