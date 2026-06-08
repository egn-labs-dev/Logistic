import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import User
from app.security.auth import get_password_hash

async def main():
    async with AsyncSessionLocal() as session:
        query = select(User).where(User.email == "dispatcher@zt-dispatch.com")
        user = (await session.execute(query)).scalar_one_or_none()
        if not user:
            user = User(
                email="dispatcher@zt-dispatch.com",
                hashed_password=get_password_hash("Secure123!"),
                role="dispatcher",
                organization_id="org_test"
            )
            session.add(user)
            await session.commit()
            print("Created dispatcher@zt-dispatch.com")
        else:
            user.hashed_password = get_password_hash("Secure123!")
            await session.commit()
            print("Updated dispatcher@zt-dispatch.com")

if __name__ == "__main__":
    asyncio.run(main())
