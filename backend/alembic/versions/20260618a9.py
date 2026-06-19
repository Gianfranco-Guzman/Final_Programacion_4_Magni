"""add usuario_id y movimiento_referencia_id a movimiento_stock_ingrediente

Revision ID: 20260618a9
Revises: 20260610a8
Create Date: 2026-06-18
"""

from alembic import op
import sqlalchemy as sa

revision = "20260618a9"
down_revision = "20260610a8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "movimiento_stock_ingrediente",
        sa.Column("usuario_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_movimiento_stock_usuario",
        "movimiento_stock_ingrediente",
        "usuario",
        ["usuario_id"],
        ["id"],
    )
    op.add_column(
        "movimiento_stock_ingrediente",
        sa.Column("movimiento_referencia_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_movimiento_stock_referencia",
        "movimiento_stock_ingrediente",
        "movimiento_stock_ingrediente",
        ["movimiento_referencia_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_movimiento_stock_referencia", "movimiento_stock_ingrediente", type_="foreignkey")
    op.drop_column("movimiento_stock_ingrediente", "movimiento_referencia_id")
    op.drop_constraint("fk_movimiento_stock_usuario", "movimiento_stock_ingrediente", type_="foreignkey")
    op.drop_column("movimiento_stock_ingrediente", "usuario_id")
