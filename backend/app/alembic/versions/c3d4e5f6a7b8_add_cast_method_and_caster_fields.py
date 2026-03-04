"""Add cast_method, caster_name, caster_gender to hexagramreading

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-25 10:00:00.000000

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "hexagramreading",
        sa.Column(
            "cast_method",
            sqlmodel.sql.sqltypes.AutoString(length=20),
            nullable=False,
            server_default="coin",
        ),
    )
    op.add_column(
        "hexagramreading",
        sa.Column(
            "caster_name",
            sqlmodel.sql.sqltypes.AutoString(length=100),
            nullable=True,
        ),
    )
    op.add_column(
        "hexagramreading",
        sa.Column(
            "caster_gender",
            sqlmodel.sql.sqltypes.AutoString(length=10),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("hexagramreading", "caster_gender")
    op.drop_column("hexagramreading", "caster_name")
    op.drop_column("hexagramreading", "cast_method")
