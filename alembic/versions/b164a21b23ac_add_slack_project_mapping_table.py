"""Add Slack Project Mapping Table

Revision ID: b164a21b23ac
Revises: 8fe00eee0358
Create Date: 2025-06-30 17:52:56.301164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b164a21b23ac'
down_revision: Union[str, Sequence[str], None] = '8fe00eee0358'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
