"""phase 1-3 domain redesign foundations

Revision ID: 20260529a4
Revises: 20260524a3
Create Date: 2026-05-29
"""

from alembic import op
import sqlalchemy as sa


revision = "20260529a4"
down_revision = "20260524a3"
branch_labels = None
depends_on = None


unidad_medida_enum = sa.Enum(
    "UNIDAD",
    "GRAMO",
    "KILOGRAMO",
    "MILILITRO",
    "LITRO",
    name="unidad_medida_enum",
    native_enum=False,
)

tipo_producto_enum = sa.Enum(
    "FABRICADO",
    "REVENTA",
    name="tipo_producto_enum",
    native_enum=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    unidad_medida_enum.create(bind, checkfirst=True)
    tipo_producto_enum.create(bind, checkfirst=True)

    op.add_column(
        "ingrediente",
        sa.Column("unidad_medida", unidad_medida_enum, nullable=False, server_default="UNIDAD"),
    )
    op.add_column(
        "ingrediente",
        sa.Column("stock_actual", sa.Numeric(12, 3), nullable=False, server_default="0"),
    )
    op.add_column(
        "ingrediente",
        sa.Column("stock_minimo", sa.Numeric(12, 3), nullable=False, server_default="0"),
    )
    op.add_column(
        "ingrediente",
        sa.Column("costo_unitario", sa.Numeric(12, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "ingrediente",
        sa.Column("permite_fraccion", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.add_column(
        "producto",
        sa.Column("precio_costo_calculado", sa.Numeric(12, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "producto",
        sa.Column("descuento_porcentaje", sa.Numeric(5, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "producto",
        sa.Column("tipo_producto", tipo_producto_enum, nullable=False, server_default="FABRICADO"),
    )

    op.execute("CREATE SEQUENCE IF NOT EXISTS producto_ingrediente_id_seq")
    op.add_column("producto_ingrediente", sa.Column("id", sa.Integer(), nullable=True))
    op.execute(
        "ALTER TABLE producto_ingrediente ALTER COLUMN id SET DEFAULT nextval('producto_ingrediente_id_seq')"
    )
    op.execute("UPDATE producto_ingrediente SET id = nextval('producto_ingrediente_id_seq') WHERE id IS NULL")
    op.alter_column("producto_ingrediente", "id", nullable=False)
    op.add_column(
        "producto_ingrediente",
        sa.Column("cantidad", sa.Numeric(12, 3), nullable=False, server_default="1"),
    )
    op.add_column(
        "producto_ingrediente",
        sa.Column("unidad_medida", unidad_medida_enum, nullable=False, server_default="UNIDAD"),
    )
    op.add_column(
        "producto_ingrediente",
        sa.Column("orden", sa.Integer(), nullable=False, server_default="1"),
    )
    op.drop_constraint("producto_ingrediente_pkey", "producto_ingrediente", type_="primary")
    op.create_primary_key("pk_producto_ingrediente", "producto_ingrediente", ["id"])
    op.create_unique_constraint(
        "uq_producto_ingrediente_producto_ingrediente",
        "producto_ingrediente",
        ["producto_id", "ingrediente_id"],
    )

    op.create_check_constraint(
        "ck_ingrediente_stock_actual_ge_zero",
        "ingrediente",
        "stock_actual >= 0",
    )
    op.create_check_constraint(
        "ck_ingrediente_stock_minimo_ge_zero",
        "ingrediente",
        "stock_minimo >= 0",
    )
    op.create_check_constraint(
        "ck_ingrediente_costo_unitario_ge_zero",
        "ingrediente",
        "costo_unitario >= 0",
    )
    op.create_check_constraint(
        "ck_producto_precio_costo_calculado_ge_zero",
        "producto",
        "precio_costo_calculado >= 0",
    )
    op.create_check_constraint(
        "ck_producto_descuento_porcentaje_range",
        "producto",
        "descuento_porcentaje >= 0 AND descuento_porcentaje <= 100",
    )
    op.create_check_constraint(
        "ck_producto_ingrediente_cantidad_gt_zero",
        "producto_ingrediente",
        "cantidad > 0",
    )
    op.create_check_constraint(
        "ck_producto_ingrediente_orden_ge_one",
        "producto_ingrediente",
        "orden >= 1",
    )


def downgrade() -> None:
    op.drop_constraint("ck_producto_ingrediente_orden_ge_one", "producto_ingrediente", type_="check")
    op.drop_constraint("ck_producto_ingrediente_cantidad_gt_zero", "producto_ingrediente", type_="check")
    op.drop_constraint("ck_producto_descuento_porcentaje_range", "producto", type_="check")
    op.drop_constraint("ck_producto_precio_costo_calculado_ge_zero", "producto", type_="check")
    op.drop_constraint("ck_ingrediente_costo_unitario_ge_zero", "ingrediente", type_="check")
    op.drop_constraint("ck_ingrediente_stock_minimo_ge_zero", "ingrediente", type_="check")
    op.drop_constraint("ck_ingrediente_stock_actual_ge_zero", "ingrediente", type_="check")

    op.drop_constraint(
        "uq_producto_ingrediente_producto_ingrediente",
        "producto_ingrediente",
        type_="unique",
    )
    op.drop_constraint("pk_producto_ingrediente", "producto_ingrediente", type_="primary")
    op.create_primary_key(
        "producto_ingrediente_pkey",
        "producto_ingrediente",
        ["producto_id", "ingrediente_id"],
    )
    op.drop_column("producto_ingrediente", "orden")
    op.drop_column("producto_ingrediente", "unidad_medida")
    op.drop_column("producto_ingrediente", "cantidad")
    op.drop_column("producto_ingrediente", "id")
    op.execute("DROP SEQUENCE IF EXISTS producto_ingrediente_id_seq")

    op.drop_column("producto", "tipo_producto")
    op.drop_column("producto", "descuento_porcentaje")
    op.drop_column("producto", "precio_costo_calculado")

    op.drop_column("ingrediente", "permite_fraccion")
    op.drop_column("ingrediente", "costo_unitario")
    op.drop_column("ingrediente", "stock_minimo")
    op.drop_column("ingrediente", "stock_actual")
    op.drop_column("ingrediente", "unidad_medida")

    bind = op.get_bind()
    tipo_producto_enum.drop(bind, checkfirst=True)
    unidad_medida_enum.drop(bind, checkfirst=True)
