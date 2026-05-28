"""add compatibility indexes and product category backfill

Revision ID: 20260524a3
Revises: 20260524a2
Create Date: 2026-05-24
"""

from alembic import op


revision = "20260524a3"
down_revision = "20260524a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO producto_categoria (producto_id, categoria_id, es_principal)
        SELECT p.id, p.categoria_id, TRUE
        FROM producto p
        WHERE p.categoria_id IS NOT NULL
          AND NOT EXISTS (
            SELECT 1
            FROM producto_categoria pc
            WHERE pc.producto_id = p.id
              AND pc.categoria_id = p.categoria_id
          )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM producto_categoria pc
        WHERE pc.es_principal = TRUE
          AND EXISTS (
            SELECT 1
            FROM producto p
            WHERE p.id = pc.producto_id
              AND p.categoria_id = pc.categoria_id
          )
        """
    )
