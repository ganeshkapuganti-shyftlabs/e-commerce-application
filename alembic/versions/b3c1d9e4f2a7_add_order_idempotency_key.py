"""add idempotency_key to orders

Revision ID: b3c1d9e4f2a7
Revises: 730f1c7ec670
Create Date: 2026-10-09 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c1d9e4f2a7'
down_revision: Union[str, Sequence[str], None] = '730f1c7ec670'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('orders', sa.Column('idempotency_key', sa.String(length=64), nullable=True))
    op.create_unique_constraint('uq_orders_user_idempotency_key', 'orders', ['user_id', 'idempotency_key'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_orders_user_idempotency_key', 'orders', type_='unique')
    op.drop_column('orders', 'idempotency_key')
