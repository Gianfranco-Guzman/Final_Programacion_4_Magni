from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings


engine = create_engine(settings.DATABASE_URL, echo=False)


def get_session():
    with Session(engine) as session:
        yield session


def create_all_tables() -> None:
    """Crea las tablas registradas en SQLModel.metadata al arrancar la app."""
    import app.modules.usuarios.model 
    import app.modules.categorias.model   
    SQLModel.metadata.create_all(engine)
