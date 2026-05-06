from sqlmodel import create_engine, SQLModel, Session
from app.core.config import get_settings

settings = get_settings()

# Crear engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,  # Verifica conexiones antes de usar
)


def create_all_tables() -> None:
    """Crea todas las tablas en la base de datos"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """
    Generador de sesiones para inyección de dependencias.
    Cada request obtiene una sesión nueva y es cerrada al terminar.
    """
    with Session(engine) as session:
        yield session
