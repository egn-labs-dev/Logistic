import os
import sys
import logging
from contextlib import asynccontextmanager
from pythonjsonlogger import jsonlogger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.dispatcher import router as dispatcher_router
from app.api.settings import router as settings_router
from app.api.webhooks import router as webhooks_router
from app.api.waitlist import router as waitlist_router
from app.db.database import engine
from app.db.models import Base
from app.core.config import settings
from app.security.rate_limiter import limiter
from app.core.telemetry import setup_telemetry

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s'
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# Environment Validation
if not settings.gemini_api_key or not settings.database_url:
    logging.critical("Critical Error: Configuration Missing (GEMINI_API_KEY or DATABASE_URL not set)")
    if os.getenv("TESTING") != "True" and not os.getenv("BYPASS_ENV_CHECK"):
        sys.exit(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Zero Trust Logistics API starting up...")
    yield

app = FastAPI(
    title="Logistics AI Dispatcher MVP",
    description="Enterprise-grade zero trust API for automated cargo dispatching",
    version="0.1.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,https://app.zt-dispatch.com").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(dispatcher_router)
app.include_router(settings_router)
app.include_router(webhooks_router)
app.include_router(waitlist_router, prefix="/api/v1/waitlist", tags=["Waitlist CRM"])

setup_telemetry(app)



@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Zero Trust Logistics API is running"}
