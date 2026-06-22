from sqlalchemy import text
from sqlmodel import SQLModel, Session, create_engine

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
)


def create_all_tables() -> None:
    SQLModel.metadata.create_all(engine)
    _ensure_identity_schema()
    _ensure_roles_schema()
    _ensure_category_schema()
    _ensure_product_schema()
    _ensure_pedido_schema()
    _backfill_producto_categoria()


def _ensure_identity_schema() -> None:
    statements = [
        "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS apellido VARCHAR(80) NOT NULL DEFAULT ''",
        "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS celular VARCHAR(20)",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def _ensure_roles_schema() -> None:
    statements = [
        "ALTER TABLE usuario_rol ADD COLUMN IF NOT EXISTS asignado_por_id INTEGER REFERENCES usuario(id)",
        "ALTER TABLE usuario_rol ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE",
    ]
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def _ensure_category_schema() -> None:
    statements = [
        "ALTER TABLE categoria ADD COLUMN IF NOT EXISTS parent_id INTEGER REFERENCES categoria(id)",
        "ALTER TABLE categoria ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE",
        "CREATE INDEX IF NOT EXISTS ix_categoria_parent_id ON categoria(parent_id)",
        "CREATE INDEX IF NOT EXISTS ix_categoria_deleted_at ON categoria(deleted_at)",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def _ensure_product_schema() -> None:
    statements = [
        "ALTER TABLE forma_pago ADD COLUMN IF NOT EXISTS codigo VARCHAR(20)",
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_forma_pago_codigo ON forma_pago(codigo) WHERE codigo IS NOT NULL",
        "ALTER TABLE producto ADD COLUMN IF NOT EXISTS disponible BOOLEAN NOT NULL DEFAULT true",
        "ALTER TABLE producto ADD COLUMN IF NOT EXISTS precio_costo_calculado NUMERIC(12,2) NOT NULL DEFAULT 0",
        "ALTER TABLE producto ADD COLUMN IF NOT EXISTS descuento_porcentaje NUMERIC(5,2) NOT NULL DEFAULT 0",
        "ALTER TABLE producto ADD COLUMN IF NOT EXISTS tipo_producto VARCHAR(20) NOT NULL DEFAULT 'FABRICADO'",
        "ALTER TABLE producto ADD COLUMN IF NOT EXISTS imagenes_url TEXT[]",
        "ALTER TABLE producto ADD COLUMN IF NOT EXISTS unidad_venta_id INTEGER REFERENCES unidad_medida(id)",
        "ALTER TABLE ingrediente ADD COLUMN IF NOT EXISTS unidad_medida VARCHAR(20) NOT NULL DEFAULT 'UNIDAD'",
        "ALTER TABLE ingrediente ADD COLUMN IF NOT EXISTS stock_actual NUMERIC(12,3) NOT NULL DEFAULT 0",
        "ALTER TABLE ingrediente ADD COLUMN IF NOT EXISTS stock_minimo NUMERIC(12,3) NOT NULL DEFAULT 0",
        "ALTER TABLE ingrediente ADD COLUMN IF NOT EXISTS costo_unitario NUMERIC(12,2) NOT NULL DEFAULT 0",
        "ALTER TABLE ingrediente ADD COLUMN IF NOT EXISTS permite_fraccion BOOLEAN NOT NULL DEFAULT false",
        "ALTER TABLE producto_ingrediente ADD COLUMN IF NOT EXISTS id INTEGER",
        "ALTER TABLE producto_ingrediente ADD COLUMN IF NOT EXISTS cantidad NUMERIC(12,3) NOT NULL DEFAULT 1",
        "ALTER TABLE producto_ingrediente ADD COLUMN IF NOT EXISTS unidad_medida VARCHAR(20) NOT NULL DEFAULT 'UNIDAD'",
        "ALTER TABLE producto_ingrediente ADD COLUMN IF NOT EXISTS orden INTEGER NOT NULL DEFAULT 1",
        "ALTER TABLE producto_ingrediente ADD COLUMN IF NOT EXISTS es_removible BOOLEAN NOT NULL DEFAULT true",
        "ALTER TABLE producto_ingrediente ADD COLUMN IF NOT EXISTS es_opcional BOOLEAN NOT NULL DEFAULT false",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def _ensure_pedido_schema() -> None:
    statements = [
        "ALTER TABLE estado_pedido ADD COLUMN IF NOT EXISTS codigo VARCHAR(20)",
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_estado_pedido_codigo ON estado_pedido(codigo) WHERE codigo IS NOT NULL",
        "ALTER TABLE estado_pedido ADD COLUMN IF NOT EXISTS es_terminal BOOLEAN NOT NULL DEFAULT false",
        "ALTER TABLE pedido ADD COLUMN IF NOT EXISTS subtotal NUMERIC(12,2) NOT NULL DEFAULT 0",
        "ALTER TABLE pedido ADD COLUMN IF NOT EXISTS descuento NUMERIC(12,2) NOT NULL DEFAULT 0",
        "ALTER TABLE pedido ADD COLUMN IF NOT EXISTS costo_envio NUMERIC(12,2) NOT NULL DEFAULT 0",
        "ALTER TABLE detalle_pedido ADD COLUMN IF NOT EXISTS personalizacion INTEGER[]",
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


def get_session():
    with Session(engine) as session:
        yield session
