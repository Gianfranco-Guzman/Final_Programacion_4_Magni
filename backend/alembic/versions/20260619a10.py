"""add tipo_entrega to pedido and make direccion_entrega_id nullable

Revision ID: 20260619a10
Revises: 20260618a9
Create Date: 2026-06-19
"""

from alembic import op
import sqlalchemy as sa

revision = "20260619a10"
down_revision = "20260618a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pedido",
        sa.Column("tipo_entrega", sa.String(length=10), nullable=False, server_default="domicilio"),
    )
    op.alter_column(
        "pedido",
        "direccion_entrega_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.execute("UPDATE pedido SET direccion_entrega_id = 0 WHERE direccion_entrega_id IS NULL")
    op.alter_column(
        "pedido",
        "direccion_entrega_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("pedido", "tipo_entrega")
