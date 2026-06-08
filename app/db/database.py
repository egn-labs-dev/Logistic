import os
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Get Database URL from central config (which checks Vault Agent)
DATABASE_URL = settings.database_url

# Use NullPool for tests to avoid event loop conflicts (InterfaceError)
is_testing = os.getenv("TESTING") == "True"
engine_kwargs = {
    "echo": False,
    "connect_args": {
        "server_settings": {"jit": "off"},
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }
}

if is_testing:
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

import os

from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
    try:
        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to instrument sqlalchemy: {e}")

@asynccontextmanager
async def get_db_session_with_rls(organization_id: str):
    """
    Generates a database session with Row Level Security (RLS) enabled.
    Ensures client isolation at the PostgreSQL core level.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Critical step: set local variable for the transaction
            await session.execute(
                text("SELECT set_config('app.current_organization_id', :org_id, true)"),
                {"org_id": organization_id}
            )
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
