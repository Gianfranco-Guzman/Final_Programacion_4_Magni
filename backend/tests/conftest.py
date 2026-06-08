from collections.abc import Iterator
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.base import get_session
from app.db.models import (
    Categoria,
    DetallePedido,
    DireccionEntrega,
    FormaPago,
    HistorialEstadoPedido,
    Ingrediente,
    Pedido,
    Producto,
    ProductoDetalle,
    Rol,
    Usuario,
    UsuarioRol,
)
from app.db.models.enums import TipoProducto, UnidadMedida
from app.db.unit_of_work import SqlModelUnitOfWork, get_uow
from app.main import app


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(name="session")
def session_fixture() -> Iterator[Session]:
    SQLModel.metadata.create_all(TEST_ENGINE)
    with Session(TEST_ENGINE) as session:
        yield session
    SQLModel.metadata.drop_all(TEST_ENGINE)


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Iterator[TestClient]:
    def override_get_session() -> Iterator[Session]:
        test_session = Session(TEST_ENGINE)
        try:
            yield test_session
        finally:
            test_session.close()

    def override_get_uow() -> Iterator[SqlModelUnitOfWork]:
        test_session = Session(TEST_ENGINE)
        uow = SqlModelUnitOfWork(test_session)
        try:
            yield uow
            uow.commit()
        except Exception:
            uow.rollback()
            raise
        finally:
            test_session.close()

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_uow] = override_get_uow
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _ensure_role(session: Session, nombre: str) -> Rol:
    role = session.exec(select(Rol).where(Rol.nombre == nombre)).first()
    if role:
        return role
    role = Rol(nombre=nombre, descripcion=nombre)
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


def _create_user(session: Session, *, email: str, roles: list[str]) -> Usuario:
    user = Usuario(
        email=email,
        password_hash=hash_password("password123"),
        nombre=email.split("@")[0],
        apellido="Test",
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    for role_name in roles:
        role = _ensure_role(session, role_name)
        session.add(UsuarioRol(usuario_id=user.id, rol_id=role.id))
    session.commit()
    session.refresh(user)
    return user


def auth_cookie_for(user: Usuario, roles: list[str]) -> dict[str, str]:
    token = create_access_token({"sub": str(user.id), "roles": roles})
    return {"access_token": token}


@pytest.fixture(name="client_user")
def client_user_fixture(session: Session) -> Usuario:
    return _create_user(session, email="cliente@test.com", roles=["CLIENT"])


@pytest.fixture(name="other_client_user")
def other_client_user_fixture(session: Session) -> Usuario:
    return _create_user(session, email="otro@test.com", roles=["CLIENT"])


@pytest.fixture(name="staff_user")
def staff_user_fixture(session: Session) -> Usuario:
    return _create_user(session, email="pedidos@test.com", roles=["PEDIDOS"])


@pytest.fixture(name="catalog_setup")
def catalog_setup_fixture(session: Session) -> dict[str, int]:
    categoria = Categoria(nombre="Pizzas", descripcion="Pizzas")
    session.add(categoria)
    session.commit()
    session.refresh(categoria)

    ingrediente = Ingrediente(
        nombre=f"Muzza-{categoria.id}",
        descripcion="Queso",
        es_alergeno=False,
        unidad_medida=UnidadMedida.GRAMO,
        stock_actual=Decimal("5000"),
        stock_minimo=Decimal("100"),
        costo_unitario=Decimal("10"),
        permite_fraccion=True,
    )
    session.add(ingrediente)
    session.commit()
    session.refresh(ingrediente)

    producto = Producto(
        nombre="Pizza muzza",
        descripcion="Pizza",
        precio_venta=Decimal("1000"),
        precio_costo_calculado=Decimal("300"),
        descuento_porcentaje=Decimal("0"),
        tipo_producto=TipoProducto.FABRICADO,
        categoria_id=categoria.id,
        codigo="PIZZA-1",
        disponible=True,
    )
    session.add(producto)
    session.commit()
    session.refresh(producto)

    detalle = ProductoDetalle(
        producto_id=producto.id,
        ingrediente_id=ingrediente.id,
        cantidad=Decimal("100"),
        unidad_medida=UnidadMedida.GRAMO,
        orden=1,
        es_removible=True,
        es_opcional=False,
    )
    session.add(detalle)

    forma_pago = FormaPago(nombre=f"EFECTIVO-{categoria.id}", descripcion="Cash", activo=True)
    session.add(forma_pago)
    session.commit()
    session.refresh(forma_pago)

    return {"producto_id": producto.id, "forma_pago_id": forma_pago.id}


def create_address(session: Session, user_id: int) -> DireccionEntrega:
    direccion = DireccionEntrega(
        usuario_id=user_id,
        etiqueta="Casa",
        linea1="Siempre Viva 123",
        ciudad="Cordoba",
        es_principal=True,
    )
    session.add(direccion)
    session.commit()
    session.refresh(direccion)
    return direccion


def create_order(
    session: Session,
    *,
    user_id: int,
    direccion_entrega_id: int,
    forma_pago_id: int,
    estado_actual: str = "PENDIENTE",
) -> Pedido:
    pedido = Pedido(
        usuario_id=user_id,
        direccion_entrega_id=direccion_entrega_id,
        forma_pago_id=forma_pago_id,
        estado_actual=estado_actual,
        total=1500.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(pedido)
    session.commit()
    session.refresh(pedido)

    detalle = DetallePedido(
        pedido_id=pedido.id,
        producto_id=1,
        cantidad=1,
        precio_unitario_snapshot=1500.0,
        nombre_producto_snapshot="Pizza muzza",
        subtotal=1500.0,
    )
    historial = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_anterior=None,
        estado_nuevo=estado_actual,
        fecha=datetime.now(timezone.utc),
        usuario_id=user_id,
    )
    session.add(detalle)
    session.add(historial)
    session.commit()
    session.refresh(pedido)
    return pedido
