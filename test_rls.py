import asyncio
from app.db.database import AsyncSessionLocal
from sqlalchemy import text

async def test_rls():
    async with AsyncSessionLocal() as session:
        await session.execute(text("ALTER ROLE postgres NOBYPASSRLS"))
        # Встановлюємо ЧУЖИЙ organization_id
        await session.execute(text("SELECT set_config('app.current_organization_id', 'HACKER_ORG', true)"))
        
        # Спробуємо прочитати чужі замовлення
        result = await session.execute(text("SELECT * FROM cargo_orders"))
        rows = result.fetchall()
        print(f"HACKER_ORG found {len(rows)} rows.")
        
        # Тепер підключаємося як власник
        await session.execute(text("SELECT set_config('app.current_organization_id', 'org_alliance_logistic', true)"))
        result = await session.execute(text("SELECT * FROM cargo_orders"))
        rows = result.fetchall()
        print(f"org_alliance_logistic found {len(rows)} rows.")

if __name__ == "__main__":
    asyncio.run(test_rls())
