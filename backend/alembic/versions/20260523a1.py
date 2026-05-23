"""add deleted_at to ingrediente

Revision ID: 20260523a1
Revises:
Create Date: 2026-05-23
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260523a1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("ingrediente") as batch_op:
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index("ix_ingrediente_deleted_at", ["deleted_at"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("ingrediente") as batch_op:
        batch_op.drop_index("ix_ingrediente_deleted_at")
        batch_op.drop_column("deleted_at")
