from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.dispatcher import router as dispatcher_router
from app.db.database import engine
from app.db.models import Base
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Logistics AI Dispatcher MVP",
    description="Enterprise-grade zero trust API for automated cargo dispatching",
    version="0.1.0"
)

app.include_router(chat_router)
app.include_router(dispatcher_router)

@app.on_event("startup")
async def startup_event():
    # На етапі MVP створюємо таблиці автоматично
    # В продакшені це робитиме Alembic
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Розкоментувати для ресету БД
        await conn.run_sync(Base.metadata.create_all)
    logging.info("База даних успішно ініціалізована.")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Zero Trust Logistics API is running"}
