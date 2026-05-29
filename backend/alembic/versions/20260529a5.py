"""add ingredient stock movement table

Revision ID: 20260529a5
Revises: 20260529a4
Create Date: 2026-05-29
"""

from alembic import op
import sqlalchemy as sa


revision = "20260529a5"
down_revision = "20260529a4"
branch_labels = None
depends_on = None


tipo_movimiento_ingrediente_enum = sa.Enum(
    "ALTA_MANUAL",
    "AJUSTE_MANUAL",
    "CONSUMO_PEDIDO",
    "REVERSA_CANCELACION",
    name="tipo_movimiento_ingrediente_enum",
    native_enum=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    tipo_movimiento_ingrediente_enum.create(bind, checkfirst=True)

    op.create_table(
        "movimiento_stock_ingrediente",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("ingrediente_id", sa.Integer(), sa.ForeignKey("ingrediente.id"), nullable=False),
        sa.Column("pedido_id", sa.Integer(), sa.ForeignKey("pedido.id"), nullable=True),
        sa.Column("tipo_movimiento", tipo_movimiento_ingrediente_enum, nullable=False),
        sa.Column("cantidad", sa.Numeric(12, 3), nullable=False),
        sa.Column("stock_anterior", sa.Numeric(12, 3), nullable=False),
        sa.Column("stock_posterior", sa.Numeric(12, 3), nullable=False),
        sa.Column("observacion", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_movimiento_stock_ingrediente_ingrediente_id",
        "movimiento_stock_ingrediente",
        ["ingrediente_id"],
        unique=False,
    )
    op.create_index(
        "ix_movimiento_stock_ingrediente_pedido_id",
        "movimiento_stock_ingrediente",
        ["pedido_id"],
        unique=False,
    )
    op.create_check_constraint(
        "ck_movimiento_stock_ingrediente_cantidad_gt_zero",
        "movimiento_stock_ingrediente",
        "cantidad > 0",
    )
    op.create_check_constraint(
        "ck_movimiento_stock_ingrediente_stock_anterior_ge_zero",
        "movimiento_stock_ingrediente",
        "stock_anterior >= 0",
    )
    op.create_check_constraint(
        "ck_movimiento_stock_ingrediente_stock_posterior_ge_zero",
        "movimiento_stock_ingrediente",
        "stock_posterior >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_movimiento_stock_ingrediente_stock_posterior_ge_zero",
        "movimiento_stock_ingrediente",
        type_="check",
    )
    op.drop_constraint(
        "ck_movimiento_stock_ingrediente_stock_anterior_ge_zero",
        "movimiento_stock_ingrediente",
        type_="check",
    )
    op.drop_constraint(
        "ck_movimiento_stock_ingrediente_cantidad_gt_zero",
        "movimiento_stock_ingrediente",
        type_="check",
    )
    op.drop_index("ix_movimiento_stock_ingrediente_pedido_id", table_name="movimiento_stock_ingrediente")
    op.drop_index("ix_movimiento_stock_ingrediente_ingrediente_id", table_name="movimiento_stock_ingrediente")
    op.drop_table("movimiento_stock_ingrediente")

    bind = op.get_bind()
    tipo_movimiento_ingrediente_enum.drop(bind, checkfirst=True)
