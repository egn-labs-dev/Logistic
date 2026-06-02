from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.dispatcher import router as dispatcher_router
from app.db.database import engine
from app.db.models import Base
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

# Environment Validation
if not os.getenv("GEMINI_API_KEY") or not os.getenv("DATABASE_URL"):
    logging.critical("Critical Error: Configuration Missing (GEMINI_API_KEY or DATABASE_URL not set)")
    # Для MVP, якщо ми хочемо щоб тести та локальний запуск працював без падіння:
    if os.getenv("TESTING") != "True" and not os.getenv("BYPASS_ENV_CHECK"):
        sys.exit(1)

app = FastAPI(
    title="Logistics AI Dispatcher MVP",
    description="Enterprise-grade zero trust API for automated cargo dispatching",
    version="0.1.0"
)

from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.security.rate_limiter import limiter
from app.api.auth import router as auth_router

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,https://app.zt-dispatch.com").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
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
