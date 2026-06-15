"""add telegram_bot_token

Revision ID: 7a4d7261f3a8
Revises: a6e035b2ef5f
Create Date: 2026-06-15 14:17:04.892342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a4d7261f3a8'
down_revision: Union[str, None] = 'a6e035b2ef5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('organization_settings', sa.Column('telegram_bot_token', sa.String(), nullable=True))
    op.create_index(op.f('ix_organization_settings_telegram_bot_token'), 'organization_settings', ['telegram_bot_token'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_organization_settings_telegram_bot_token'), table_name='organization_settings')
    op.drop_column('organization_settings', 'telegram_bot_token')
