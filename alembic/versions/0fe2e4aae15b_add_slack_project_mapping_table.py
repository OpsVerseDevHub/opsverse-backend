"""Add Slack Project Mapping Table

Revision ID: 0fe2e4aae15b
Revises: 023049d8fad2
Create Date: 2025-06-30 18:21:54.386794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fe2e4aae15b'
down_revision: Union[str, Sequence[str], None] = '023049d8fad2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
