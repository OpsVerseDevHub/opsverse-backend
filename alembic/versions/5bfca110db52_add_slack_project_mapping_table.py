"""Add Slack Project Mapping Table

Revision ID: 5bfca110db52
Revises: 95b986e21345
Create Date: 2025-06-30 18:49:10.103713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bfca110db52'
down_revision: Union[str, Sequence[str], None] = '95b986e21345'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
