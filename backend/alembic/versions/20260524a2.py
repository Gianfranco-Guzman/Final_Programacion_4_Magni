"""add delivery, payment and order schema

Revision ID: 20260524a2
Revises: 20260524a1
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa


revision = "20260524a2"
down_revision = "20260524a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "direccion_entrega",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("etiqueta", sa.String(length=80), nullable=True),
        sa.Column("linea1", sa.String(length=255), nullable=False),
        sa.Column("linea2", sa.String(length=255), nullable=True),
        sa.Column("ciudad", sa.String(length=100), nullable=False),
        sa.Column("latitud", sa.Float(), nullable=True),
        sa.Column("longitud", sa.Float(), nullable=True),
        sa.Column("es_principal", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_direccion_entrega_usuario_id", "direccion_entrega", ["usuario_id"], unique=False)

    op.create_table(
        "forma_pago",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("nombre", sa.String(length=50), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("nombre", name="uq_forma_pago_nombre"),
    )
    op.create_index("ix_forma_pago_nombre", "forma_pago", ["nombre"], unique=False)

    op.create_table(
        "estado_pedido",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("nombre", sa.String(length=50), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("nombre", name="uq_estado_pedido_nombre"),
    )
    op.create_index("ix_estado_pedido_nombre", "estado_pedido", ["nombre"], unique=False)

    op.create_table(
        "pedido",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("direccion_entrega_id", sa.Integer(), sa.ForeignKey("direccion_entrega.id"), nullable=False),
        sa.Column("forma_pago_id", sa.Integer(), sa.ForeignKey("forma_pago.id"), nullable=False),
        sa.Column("estado_actual", sa.String(length=20), nullable=False, server_default="PENDIENTE"),
        sa.Column("total", sa.Float(), nullable=False, server_default="0"),
        sa.Column("notas", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("total >= 0", name="ck_pedido_total_ge_zero"),
    )
    op.create_index("ix_pedido_usuario_id", "pedido", ["usuario_id"], unique=False)
    op.create_index("ix_pedido_estado_actual", "pedido", ["estado_actual"], unique=False)

    op.create_table(
        "detalle_pedido",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("pedido_id", sa.Integer(), sa.ForeignKey("pedido.id"), nullable=False),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("producto.id"), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("precio_unitario_snapshot", sa.Float(), nullable=False),
        sa.Column("nombre_producto_snapshot", sa.String(length=150), nullable=False),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.CheckConstraint("cantidad > 0", name="ck_detalle_pedido_cantidad_gt_zero"),
        sa.CheckConstraint("precio_unitario_snapshot >= 0", name="ck_detalle_pedido_precio_ge_zero"),
        sa.CheckConstraint("subtotal >= 0", name="ck_detalle_pedido_subtotal_ge_zero"),
    )
    op.create_index("ix_detalle_pedido_pedido_id", "detalle_pedido", ["pedido_id"], unique=False)

    op.create_table(
        "historial_estado_pedido",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("pedido_id", sa.Integer(), sa.ForeignKey("pedido.id"), nullable=False),
        sa.Column("estado_anterior", sa.String(length=20), nullable=True),
        sa.Column("estado_nuevo", sa.String(length=20), nullable=False),
        sa.Column("fecha", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("observacion", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_historial_estado_pedido_pedido_id", "historial_estado_pedido", ["pedido_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_historial_estado_pedido_pedido_id", table_name="historial_estado_pedido")
    op.drop_table("historial_estado_pedido")
    op.drop_index("ix_detalle_pedido_pedido_id", table_name="detalle_pedido")
    op.drop_table("detalle_pedido")
    op.drop_index("ix_pedido_estado_actual", table_name="pedido")
    op.drop_index("ix_pedido_usuario_id", table_name="pedido")
    op.drop_table("pedido")
    op.drop_index("ix_estado_pedido_nombre", table_name="estado_pedido")
    op.drop_table("estado_pedido")
    op.drop_index("ix_forma_pago_nombre", table_name="forma_pago")
    op.drop_table("forma_pago")
    op.drop_index("ix_direccion_entrega_usuario_id", table_name="direccion_entrega")
    op.drop_table("direccion_entrega")
