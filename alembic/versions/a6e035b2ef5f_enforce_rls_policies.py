"""enforce rls policies

Revision ID: a6e035b2ef5f
Revises: 5a3c008eaf02
Create Date: 2026-06-15 14:15:48.152248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6e035b2ef5f'
down_revision: Union[str, None] = '5a3c008eaf02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Примусово вмикаємо RLS на критичних таблицях
    op.execute("ALTER TABLE cargo_orders ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;")

    # Видаляємо старі політики, якщо вони раптом існували (ідемпотентність)
    op.execute("DROP POLICY IF EXISTS tenant_isolation_orders ON cargo_orders;")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_audit ON audit_logs;")

    # Створюємо жорсткі політики ізоляції
    op.execute("""
        CREATE POLICY tenant_isolation_orders ON cargo_orders
        FOR ALL
        USING (organization_id = current_setting('app.current_organization_id', true));
    """)
    op.execute("""
        CREATE POLICY tenant_isolation_audit ON audit_logs
        FOR ALL
        USING (organization_id = current_setting('app.current_organization_id', true));
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_orders ON cargo_orders;")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_audit ON audit_logs;")
    op.execute("ALTER TABLE cargo_orders DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;")
