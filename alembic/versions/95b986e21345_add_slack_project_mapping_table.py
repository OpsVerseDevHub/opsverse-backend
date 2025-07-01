"""Add Slack Project Mapping Table

Revision ID: 95b986e21345
Revises: 6f49b8a85ea5
Create Date: 2025-06-30 18:33:17.283945

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95b986e21345'
down_revision: Union[str, Sequence[str], None] = '6f49b8a85ea5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
