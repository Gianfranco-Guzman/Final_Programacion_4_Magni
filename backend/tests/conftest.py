import os
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from app.core.Config.config import get_settings
from app.core.Security.security import create_access_token, hash_password
import app.modules.auth.model  # noqa: F401
import app.modules.categorias.model  # noqa: F401
import app.modules.direcciones.model  # noqa: F401
import app.modules.formas_pago.model  # noqa: F401
import app.modules.ingredientes.model  # noqa: F401
import app.modules.pagos.model  # noqa: F401
import app.modules.pedidos.model  # noqa: F401
import app.modules.productos.model  # noqa: F401
from app.modules.auth.model import Rol, Usuario, UsuarioRol
from app.modules.categorias.model import Categoria
from app.modules.direcciones.model import DireccionEntrega
from app.modules.formas_pago.model import FormaPago
from app.modules.ingredientes.model import Ingrediente
from app.modules.productos.model import Producto, ProductoDetalle
from app.core.enums import TipoProducto, UnidadMedida
from app.db.unit_of_work import UnitOfWork, get_uow
from app.main import app


@asynccontextmanager
async def _noop_lifespan(_app: FastAPI):
    yield


app.router.lifespan_context = _noop_lifespan
app.router._startup = []
app.router._shutdown = []

settings = get_settings()

_test_db_url = os.environ.get("TEST_DATABASE_URL", settings.database_url)
_test_engine = create_engine(_test_db_url, echo=False, future=True, pool_pre_ping=True)

_TRUNCATE_SQL = text(
    "TRUNCATE TABLE "
    "historial_estado_pedido, detalle_pedido, pago, "
    "movimiento_stock_ingrediente, pedido, refresh_token, "
    "usuario_rol, direccion_entrega, usuario, "
    "producto_ingrediente, producto_categoria, producto, "
    "ingrediente, unidad_medida, categoria, forma_pago, "
    "estado_pedido, rol "
    "RESTART IDENTITY CASCADE"
)


_ENSURE_SCHEMA_SQL = [
    "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS apellido VARCHAR(80) NOT NULL DEFAULT ''",
    "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS celular VARCHAR(20)",
    "ALTER TABLE usuario_rol ADD COLUMN IF NOT EXISTS asignado_por_id INTEGER REFERENCES usuario(id)",
    "ALTER TABLE usuario_rol ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE",
    "ALTER TABLE forma_pago ADD COLUMN IF NOT EXISTS codigo VARCHAR(20)",
    "CREATE UNIQUE INDEX IF NOT EXISTS ix_forma_pago_codigo ON forma_pago(codigo) WHERE codigo IS NOT NULL",
    "ALTER TABLE producto ADD COLUMN IF NOT EXISTS imagenes_url TEXT[]",
    "ALTER TABLE producto ADD COLUMN IF NOT EXISTS unidad_venta_id INTEGER REFERENCES unidad_medida(id)",
    "ALTER TABLE estado_pedido ADD COLUMN IF NOT EXISTS codigo VARCHAR(20)",
    "CREATE UNIQUE INDEX IF NOT EXISTS ix_estado_pedido_codigo ON estado_pedido(codigo) WHERE codigo IS NOT NULL",
    "ALTER TABLE estado_pedido ADD COLUMN IF NOT EXISTS es_terminal BOOLEAN NOT NULL DEFAULT false",
    "ALTER TABLE pedido ADD COLUMN IF NOT EXISTS subtotal NUMERIC(12,2) NOT NULL DEFAULT 0",
    "ALTER TABLE pedido ADD COLUMN IF NOT EXISTS descuento NUMERIC(12,2) NOT NULL DEFAULT 0",
    "ALTER TABLE pedido ADD COLUMN IF NOT EXISTS costo_envio NUMERIC(12,2) NOT NULL DEFAULT 0",
    "ALTER TABLE detalle_pedido ADD COLUMN IF NOT EXISTS personalizacion INTEGER[]",
]


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    SQLModel.metadata.create_all(_test_engine)
    with _test_engine.begin() as conn:
        for stmt in _ENSURE_SCHEMA_SQL:
            conn.execute(text(stmt))
    with _test_engine.connect() as conn:
        conn.execute(_TRUNCATE_SQL)
        conn.commit()


@pytest.fixture(autouse=True)
def _limpia_tablas():
    yield
    with _test_engine.connect() as conn:
        conn.execute(_TRUNCATE_SQL)
        conn.commit()


@pytest.fixture
def db():
    with Session(_test_engine) as session:
        yield session


@pytest.fixture
def client(db):
    def _get_uow():
        with UnitOfWork() as uow:
            yield uow

    app.dependency_overrides[get_uow] = _get_uow
    try:
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


def crear_rol(db: Session, nombre: str) -> Rol:
    rol = Rol(nombre=nombre, descripcion=nombre)
    db.add(rol)
    db.flush()
    return rol


def crear_usuario(
    db: Session,
    email: str,
    password: str,
    nombre: str,
    apellido: str,
    roles: list[Rol],
) -> Usuario:
    usuario = Usuario(
        email=email,
        password_hash=hash_password(password),
        nombre=nombre,
        apellido=apellido,
        celular="3510000000",
        is_active=True,
    )
    db.add(usuario)
    db.flush()
    for rol in roles:
        db.add(UsuarioRol(usuario_id=usuario.id, rol_id=rol.id))
    db.flush()
    return usuario


@pytest.fixture
def roles(db):
    admin = crear_rol(db, "ADMIN")
    client_rol = crear_rol(db, "CLIENT")
    crear_rol(db, "PEDIDOS")
    db.commit()
    return {"ADMIN": admin, "CLIENT": client_rol}


@pytest.fixture
def usuario_admin(db, roles):
    user = crear_usuario(db, "admin@test.com", "Admin1234!", "Admin", "Test", [roles["ADMIN"]])
    db.commit()
    return user


@pytest.fixture
def usuario_cliente(db, roles):
    user = crear_usuario(db, "cliente@test.com", "Cliente123!", "Cliente", "Test", [roles["CLIENT"]])
    db.commit()
    return user


@pytest.fixture
def admin_headers(usuario_admin):
    token = create_access_token({"sub": str(usuario_admin.id), "roles": ["ADMIN"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def cliente_headers(usuario_cliente):
    token = create_access_token({"sub": str(usuario_cliente.id), "roles": ["CLIENT"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def forma_pago_efectivo(db):
    fp = FormaPago(codigo="EFECTIVO", nombre="EFECTIVO", descripcion="Efectivo", activo=True)
    db.add(fp)
    db.commit()
    return fp


@pytest.fixture
def forma_pago_mp(db):
    fp = FormaPago(codigo="MERCADOPAGO", nombre="MERCADOPAGO", descripcion="MercadoPago", activo=True)
    db.add(fp)
    db.commit()
    return fp


@pytest.fixture
def categoria(db):
    cat = Categoria(nombre="Pizzas Test", descripcion="Pizzas")
    db.add(cat)
    db.commit()
    return cat


@pytest.fixture
def ingrediente(db):
    ing = Ingrediente(
        nombre="Queso Test",
        unidad_medida=UnidadMedida.GRAMO,
        stock_actual=5000,
        stock_minimo=100,
        costo_unitario=10,
        permite_fraccion=True,
    )
    db.add(ing)
    db.commit()
    return ing


@pytest.fixture
def producto(db, categoria, ingrediente):
    prod = Producto(
        nombre="Pizza Test",
        codigo="TEST-001",
        precio_venta=299,
        categoria_id=categoria.id,
        disponible=True,
        tipo_producto=TipoProducto.FABRICADO,
    )
    db.add(prod)
    db.flush()
    db.add(
        ProductoDetalle(
            producto_id=prod.id,
            ingrediente_id=ingrediente.id,
            cantidad=100,
            unidad_medida=UnidadMedida.GRAMO,
        )
    )
    db.commit()
    return prod


@pytest.fixture
def direccion(db, usuario_cliente):
    dir_ = DireccionEntrega(
        usuario_id=usuario_cliente.id,
        etiqueta="Casa",
        linea1="Av. Test 123",
        ciudad="Córdoba",
        es_principal=True,
    )
    db.add(dir_)
    db.commit()
    return dir_
