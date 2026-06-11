"""drop producto stock_cantidad

Revision ID: 20260610a8
Revises: 20260610a7
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa


revision = "20260610a8"
down_revision = "20260610a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    producto_columns = {column["name"] for column in inspector.get_columns("producto")}
    if "stock_cantidad" in producto_columns:
        op.drop_column("producto", "stock_cantidad")


def downgrade() -> None:
    op.add_column(
        "producto",
        sa.Column("stock_cantidad", sa.Integer(), nullable=False, server_default="0"),
    )
