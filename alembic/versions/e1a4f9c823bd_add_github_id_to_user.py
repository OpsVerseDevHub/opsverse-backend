"""add github_id to user

Revision ID: e1a4f9c823bd
Revises: d029cdbed8a7
Create Date: 2026-11-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "e1a4f9c823bd"
down_revision = "d029cdbed8a7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("github_id", sa.String(), nullable=True),
    )
    op.create_index(op.f("ix_users_github_id"), "users", ["github_id"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_users_github_id"), table_name="users")
    op.drop_column("users", "github_id")
