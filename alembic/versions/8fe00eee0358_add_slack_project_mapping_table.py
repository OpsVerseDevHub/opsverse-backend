"""Add Slack Project Mapping Table

Revision ID: 8fe00eee0358
Revises: b048fca9c721
Create Date: 2025-06-30 17:49:31.099393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fe00eee0358'
down_revision: Union[str, Sequence[str], None] = 'b048fca9c721'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
