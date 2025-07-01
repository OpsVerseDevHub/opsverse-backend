"""Add Slack Project Mapping Table

Revision ID: 6f49b8a85ea5
Revises: 0fe2e4aae15b
Create Date: 2025-06-30 18:30:44.160206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f49b8a85ea5'
down_revision: Union[str, Sequence[str], None] = '0fe2e4aae15b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
