"""Force RLS

Revision ID: 1875f50e5a36
Revises: 163c29d2df47
Create Date: 2026-06-01 10:10:44.933103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1875f50e5a36'
down_revision: Union[str, None] = '163c29d2df47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE cargo_orders FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE audit_logs FORCE ROW LEVEL SECURITY;")


def downgrade() -> None:
    pass
