"""add refresh token persistence

Revision ID: 20260610a7
Revises: 20260610a6
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa


revision = "20260610a7"
down_revision = "20260610a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "refresh_token" not in inspector.get_table_names():
        op.create_table(
            "refresh_token",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False),
            sa.Column("token_hash", sa.String(length=128), nullable=False),
            sa.Column("jti", sa.String(length=100), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index("ix_refresh_token_usuario_id", "refresh_token", ["usuario_id"], unique=False)
        op.create_index("ix_refresh_token_token_hash", "refresh_token", ["token_hash"], unique=True)
        op.create_index("ix_refresh_token_jti", "refresh_token", ["jti"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_refresh_token_jti", table_name="refresh_token")
    op.drop_index("ix_refresh_token_token_hash", table_name="refresh_token")
    op.drop_index("ix_refresh_token_usuario_id", table_name="refresh_token")
    op.drop_table("refresh_token")
