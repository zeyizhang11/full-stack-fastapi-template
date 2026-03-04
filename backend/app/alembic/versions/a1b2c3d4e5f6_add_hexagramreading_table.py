"""Add hexagramreading table

Revision ID: a1b2c3d4e5f6
Revises: 1a31ce608336
Create Date: 2026-02-25 02:40:00.000000

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "1a31ce608336"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "hexagramreading",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("reading_number", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("question", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("lines", sa.JSON(), nullable=True),
        sa.Column("hexagram_number", sa.Integer(), nullable=False),
        sa.Column("changed_hexagram_number", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_hexagramreading_reading_number"),
        "hexagramreading",
        ["reading_number"],
        unique=True,
    )


def downgrade():
    op.drop_index(
        op.f("ix_hexagramreading_reading_number"), table_name="hexagramreading"
    )
    op.drop_table("hexagramreading")
