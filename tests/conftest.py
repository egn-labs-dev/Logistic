import pytest
from app.db.database import engine
from app.db.models import Base

@pytest.fixture(autouse=True, scope="session")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
