import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.pool import NullPool

# Беремо URL бази з середовища (за замовчуванням для docker-compose)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgres@localhost:5434/logistics_db"
)

# Використовуємо NullPool для тестів, щоб уникнути конфліктів event loop'ів (InterfaceError)
is_testing = os.getenv("TESTING") == "True"
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    poolclass=NullPool if is_testing else None
)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@asynccontextmanager
async def get_db_session_with_rls(organization_id: str):
    """
    Генерує сесію бази даних з увімкненим RLS (Row Level Security).
    Гарантує ізоляцію клієнтів на рівні ядра PostgreSQL.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Важливий крок: встановлюємо локальну змінну для транзакції
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
