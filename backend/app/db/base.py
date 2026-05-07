from sqlmodel import create_engine, SQLModel, Session
from app.core.config import get_settings

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


def get_session() -> Session:

    with Session(engine) as session:
        yield session
