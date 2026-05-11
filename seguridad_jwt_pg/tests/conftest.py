"""
Configuración de pytest — fixtures compartidas.

Los tests usan SQLite en memoria: aislados, rápidos, sin
necesidad de levantar PostgreSQL. La app en producción usa PostgreSQL.

Se overridea get_uow para que el UnitOfWork use la sesión de test.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.core.uow import UnitOfWork, get_uow
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.categorias.repository import CategoriaRepository
from app.main import app


# ─── Motor SQLite en memoria ──────────────────────────────────────────────────
@pytest.fixture(name="engine_test")
def engine_test_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    import app.modules.usuarios.model     # noqa: F401
    import app.modules.categorias.model   # noqa: F401
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


# ─── Sesión de BD de test ─────────────────────────────────────────────────────
@pytest.fixture(name="session_test")
def session_test_fixture(engine_test):
    with Session(engine_test) as session:
        yield session


# ─── UoW de test que usa la sesión de SQLite ──────────────────────────────────
class TestUnitOfWork(UnitOfWork):
    """UoW que reutiliza una sesión de test en lugar de crear una nueva."""

    def __init__(self, session: Session):
        self._test_session = session

    def __enter__(self):
        self.session = self._test_session
        self.usuarios = UsuarioRepository(self.session)
        self.categorias = CategoriaRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        # No cerrar la sesión — la maneja la fixture


# ─── Cliente HTTP de test con UoW inyectado ───────────────────────────────────
@pytest.fixture(name="client")
def client_fixture(session_test):
    def get_uow_override():
        return TestUnitOfWork(session_test)

    app.dependency_overrides[get_uow] = get_uow_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# ─── Helpers reutilizables ────────────────────────────────────────────────────
@pytest.fixture(name="usuario_registrado")
def usuario_registrado_fixture(client: TestClient) -> dict:
    """Registra un usuario con role='user' y retorna sus datos."""
    response = client.post("/api/v1/auth/register", json={
        "username":  "juanperez",
        "full_name": "Juan Pérez",
        "email":     "juan@example.com",
        "password":  "Password123!",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture(name="admin_registrado")
def admin_registrado_fixture(client: TestClient, session_test: Session) -> dict:
    """
    Crea un admin directamente en BD.
    El endpoint /register siempre asigna role='user',
    así que para tests de admin se inserta directo.
    """
    from app.core.security import hash_password
    from app.modules.usuarios.model import Usuario

    admin = Usuario(
        username        = "admin",
        full_name       = "Administrador",
        email           = "admin@example.com",
        hashed_password = hash_password("Admin1234!"),
        role            = "admin",
    )
    session_test.add(admin)
    session_test.commit()
    session_test.refresh(admin)
    return {"username": "admin", "password": "Admin1234!", "role": "admin"}


@pytest.fixture(name="token_usuario")
def token_usuario_fixture(client: TestClient, usuario_registrado: dict) -> str:
    response = client.post("/api/v1/auth/token", data={
        "username": "juanperez",
        "password": "Password123!",
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(name="token_admin")
def token_admin_fixture(client: TestClient, admin_registrado: dict) -> str:
    response = client.post("/api/v1/auth/token", data={
        "username": "admin",
        "password": "Admin1234!",
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(name="headers_usuario")
def headers_usuario_fixture(token_usuario: str) -> dict:
    return {"Authorization": f"Bearer {token_usuario}"}


@pytest.fixture(name="headers_admin")
def headers_admin_fixture(token_admin: str) -> dict:
    return {"Authorization": f"Bearer {token_admin}"}
