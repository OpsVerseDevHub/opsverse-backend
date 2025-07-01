"""Add SLack Project Mapping Table

Revision ID: 023049d8fad2
Revises: b164a21b23ac
Create Date: 2025-06-30 17:53:35.467106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '023049d8fad2'
down_revision: Union[str, Sequence[str], None] = 'b164a21b23ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
