"""Rename user_id to owner_id in hexagramreading table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-25 09:00:00.000000

"""
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    # Only rename if user_id still exists (legacy databases).
    # Fresh databases created by a1b2c3d4e5f6 already use owner_id directly.
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns("hexagramreading")]
    if "user_id" in columns:
        op.alter_column(
            "hexagramreading",
            "user_id",
            new_column_name="owner_id",
        )


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns("hexagramreading")]
    if "owner_id" in columns:
        op.alter_column(
            "hexagramreading",
            "owner_id",
            new_column_name="user_id",
        )
