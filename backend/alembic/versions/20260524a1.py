"""initial identity and catalog schema

Revision ID: 20260524a1
Revises:
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa


revision = "20260524a1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rol",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("nombre", sa.String(length=50), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("nombre", name="uq_rol_nombre"),
    )
    op.create_index("ix_rol_nombre", "rol", ["nombre"], unique=False)

    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("celular", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_usuario_email"),
    )
    op.create_index("ix_usuario_email", "usuario", ["email"], unique=False)

    op.create_table(
        "usuario_rol",
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id"), primary_key=True, nullable=False),
        sa.Column("rol_id", sa.Integer(), sa.ForeignKey("rol.id"), primary_key=True, nullable=False),
    )

    op.create_table(
        "categoria",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.String(length=500), nullable=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("categoria.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("nombre", name="uq_categoria_nombre"),
    )
    op.create_index("ix_categoria_nombre", "categoria", ["nombre"], unique=False)
    op.create_index("ix_categoria_parent_id", "categoria", ["parent_id"], unique=False)
    op.create_index("ix_categoria_deleted_at", "categoria", ["deleted_at"], unique=False)

    op.create_table(
        "ingrediente",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.String(length=500), nullable=True),
        sa.Column("es_alergeno", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("nombre", name="uq_ingrediente_nombre"),
    )
    op.create_index("ix_ingrediente_nombre", "ingrediente", ["nombre"], unique=False)
    op.create_index("ix_ingrediente_deleted_at", "ingrediente", ["deleted_at"], unique=False)

    op.create_table(
        "producto",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("descripcion", sa.String(length=500), nullable=True),
        sa.Column("precio", sa.Float(), nullable=False),
        sa.Column("stock_cantidad", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("categoria_id", sa.Integer(), sa.ForeignKey("categoria.id"), nullable=False),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("disponible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("precio > 0", name="ck_producto_precio_gt_zero"),
        sa.CheckConstraint("stock_cantidad >= 0", name="ck_producto_stock_ge_zero"),
    )
    op.create_index("ix_producto_nombre", "producto", ["nombre"], unique=False)
    op.create_index("ix_producto_codigo", "producto", ["codigo"], unique=False)
    op.create_index("ix_producto_deleted_at", "producto", ["deleted_at"], unique=False)

    op.create_table(
        "producto_categoria",
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("producto.id"), primary_key=True, nullable=False),
        sa.Column("categoria_id", sa.Integer(), sa.ForeignKey("categoria.id"), primary_key=True, nullable=False),
        sa.Column("es_principal", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "producto_ingrediente",
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("producto.id"), primary_key=True, nullable=False),
        sa.Column("ingrediente_id", sa.Integer(), sa.ForeignKey("ingrediente.id"), primary_key=True, nullable=False),
        sa.Column("es_removible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("es_opcional", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_table("producto_ingrediente")
    op.drop_table("producto_categoria")
    op.drop_index("ix_producto_deleted_at", table_name="producto")
    op.drop_index("ix_producto_codigo", table_name="producto")
    op.drop_index("ix_producto_nombre", table_name="producto")
    op.drop_table("producto")
    op.drop_index("ix_ingrediente_deleted_at", table_name="ingrediente")
    op.drop_index("ix_ingrediente_nombre", table_name="ingrediente")
    op.drop_table("ingrediente")
    op.drop_index("ix_categoria_deleted_at", table_name="categoria")
    op.drop_index("ix_categoria_parent_id", table_name="categoria")
    op.drop_index("ix_categoria_nombre", table_name="categoria")
    op.drop_table("categoria")
    op.drop_table("usuario_rol")
    op.drop_index("ix_usuario_email", table_name="usuario")
    op.drop_table("usuario")
    op.drop_index("ix_rol_nombre", table_name="rol")
    op.drop_table("rol")
