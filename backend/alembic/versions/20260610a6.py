"""align core domain with erd v7 base

Revision ID: 20260610a6
Revises: 20260529a5
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260610a6"
down_revision = "20260529a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_tables = set(inspector.get_table_names())

    if "unidad_medida" not in existing_tables:
        op.create_table(
            "unidad_medida",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("nombre", sa.String(length=50), nullable=False),
            sa.Column("simbolo", sa.String(length=10), nullable=False),
            sa.Column("tipo", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_unidad_medida_nombre", "unidad_medida", ["nombre"], unique=True)
        op.create_index("ix_unidad_medida_simbolo", "unidad_medida", ["simbolo"], unique=True)

    if "pago" not in existing_tables:
        op.create_table(
            "pago",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("pedido_id", sa.Integer(), sa.ForeignKey("pedido.id"), nullable=False),
            sa.Column("mp_payment_id", sa.BigInteger(), nullable=True),
            sa.Column("mp_status", sa.String(length=30), nullable=False),
            sa.Column("mp_status_detail", sa.String(length=100), nullable=True),
            sa.Column("transaction_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("payment_method_id", sa.String(length=50), nullable=True),
            sa.Column("external_reference", sa.String(length=100), nullable=False),
            sa.Column("idempotency_key", sa.String(length=100), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_pago_pedido_id", "pago", ["pedido_id"], unique=False)
        op.create_index("ix_pago_mp_payment_id", "pago", ["mp_payment_id"], unique=True)
        op.create_index("ix_pago_external_reference", "pago", ["external_reference"], unique=True)
        op.create_index("ix_pago_idempotency_key", "pago", ["idempotency_key"], unique=True)

    usuario_rol_columns = {column["name"] for column in inspector.get_columns("usuario_rol")}
    if "asignado_por_id" not in usuario_rol_columns:
        op.add_column("usuario_rol", sa.Column("asignado_por_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_usuario_rol_asignado_por_id_usuario",
            "usuario_rol",
            "usuario",
            ["asignado_por_id"],
            ["id"],
        )
    if "expires_at" not in usuario_rol_columns:
        op.add_column("usuario_rol", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))

    forma_pago_columns = {column["name"] for column in inspector.get_columns("forma_pago")}
    if "codigo" not in forma_pago_columns:
        op.add_column("forma_pago", sa.Column("codigo", sa.String(length=20), nullable=True))
        op.create_index("ix_forma_pago_codigo", "forma_pago", ["codigo"], unique=True)
    op.execute("UPDATE forma_pago SET codigo = nombre WHERE codigo IS NULL")

    estado_pedido_columns = {column["name"] for column in inspector.get_columns("estado_pedido")}
    if "codigo" not in estado_pedido_columns:
        op.add_column("estado_pedido", sa.Column("codigo", sa.String(length=20), nullable=True))
        op.create_index("ix_estado_pedido_codigo", "estado_pedido", ["codigo"], unique=True)
    if "es_terminal" not in estado_pedido_columns:
        op.add_column("estado_pedido", sa.Column("es_terminal", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("UPDATE estado_pedido SET codigo = nombre WHERE codigo IS NULL")
    op.execute("UPDATE estado_pedido SET es_terminal = true WHERE nombre IN ('ENTREGADO', 'CANCELADO')")

    producto_columns = {column["name"] for column in inspector.get_columns("producto")}
    if "imagenes_url" not in producto_columns:
        op.add_column("producto", sa.Column("imagenes_url", postgresql.ARRAY(sa.Text()), nullable=True))
    if "unidad_venta_id" not in producto_columns:
        op.add_column("producto", sa.Column("unidad_venta_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_producto_unidad_venta_id_unidad_medida",
            "producto",
            "unidad_medida",
            ["unidad_venta_id"],
            ["id"],
        )

    pedido_columns = {column["name"] for column in inspector.get_columns("pedido")}
    if "subtotal" not in pedido_columns:
        op.add_column("pedido", sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default="0"))
    if "descuento" not in pedido_columns:
        op.add_column("pedido", sa.Column("descuento", sa.Numeric(12, 2), nullable=False, server_default="0"))
    if "costo_envio" not in pedido_columns:
        op.add_column("pedido", sa.Column("costo_envio", sa.Numeric(12, 2), nullable=False, server_default="0"))
    op.alter_column("pedido", "total", type_=sa.Numeric(12, 2), existing_nullable=False)
    op.execute("UPDATE pedido SET subtotal = total WHERE subtotal = 0")

    op.alter_column("detalle_pedido", "precio_unitario_snapshot", type_=sa.Numeric(12, 2), existing_nullable=False)
    op.alter_column("detalle_pedido", "subtotal", type_=sa.Numeric(12, 2), existing_nullable=False)
    detalle_columns = {column["name"] for column in inspector.get_columns("detalle_pedido")}
    if "personalizacion" not in detalle_columns:
        op.add_column("detalle_pedido", sa.Column("personalizacion", postgresql.ARRAY(sa.Integer()), nullable=True))


def downgrade() -> None:
    op.drop_column("detalle_pedido", "personalizacion")
    op.alter_column("detalle_pedido", "subtotal", type_=sa.Float(), existing_nullable=False)
    op.alter_column("detalle_pedido", "precio_unitario_snapshot", type_=sa.Float(), existing_nullable=False)

    op.alter_column("pedido", "total", type_=sa.Float(), existing_nullable=False)
    op.drop_column("pedido", "costo_envio")
    op.drop_column("pedido", "descuento")
    op.drop_column("pedido", "subtotal")

    op.drop_constraint("fk_producto_unidad_venta_id_unidad_medida", "producto", type_="foreignkey")
    op.drop_column("producto", "unidad_venta_id")
    op.drop_column("producto", "imagenes_url")

    op.drop_index("ix_estado_pedido_codigo", table_name="estado_pedido")
    op.drop_column("estado_pedido", "es_terminal")
    op.drop_column("estado_pedido", "codigo")

    op.drop_index("ix_forma_pago_codigo", table_name="forma_pago")
    op.drop_column("forma_pago", "codigo")

    op.drop_constraint("fk_usuario_rol_asignado_por_id_usuario", "usuario_rol", type_="foreignkey")
    op.drop_column("usuario_rol", "expires_at")
    op.drop_column("usuario_rol", "asignado_por_id")

    op.drop_index("ix_pago_idempotency_key", table_name="pago")
    op.drop_index("ix_pago_external_reference", table_name="pago")
    op.drop_index("ix_pago_mp_payment_id", table_name="pago")
    op.drop_index("ix_pago_pedido_id", table_name="pago")
    op.drop_table("pago")

    op.drop_index("ix_unidad_medida_simbolo", table_name="unidad_medida")
    op.drop_index("ix_unidad_medida_nombre", table_name="unidad_medida")
    op.drop_table("unidad_medida")
