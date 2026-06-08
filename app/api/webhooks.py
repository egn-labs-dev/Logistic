import os

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from sqlalchemy import select

from app.api.chat import process_secure_message
from app.db.database import AsyncSessionLocal
from app.db.models import ApiKey
from app.schemas.chat import IncomingMessage

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
# Тенант за замовчуванням для бота (або логіка визначення по клієнту)
DEFAULT_TENANT_API_KEY = os.getenv("DEFAULT_TENANT_API_KEY", "test-api-key-123") 

async def send_telegram_message(chat_id: int, text: str):
    """Відправка відповіді назад у Telegram"""
    async with httpx.AsyncClient() as client:
        payload = {"chat_id": chat_id, "text": text}
        await client.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Обробка вхідних повідомлень від Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Telegram integration not configured")

    try:
        update = await request.json()
    except Exception:
        return {"ok": True}
    
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        driver_text = update["message"]["text"]
        
        # Формуємо об'єкт повідомлення для нашого існуючого пайплайну
        incoming_msg = IncomingMessage(
            session_id=f"tg_{chat_id}",
            text=driver_text
        )
        
        try:
            # Знаходимо org_id за допомогою дефолтного ключа
            async with AsyncSessionLocal() as session:
                query = select(ApiKey).where(ApiKey.key == DEFAULT_TENANT_API_KEY)
                api_key_obj = (await session.execute(query)).scalar_one_or_none()
                org_id = api_key_obj.organization_id if api_key_obj else "org_test"
            
            # Викликаємо нашу захищену логіку чату
            response = await process_secure_message(
                request=request,
                payload=incoming_msg,
                organization_id=org_id
            )
            
            # Відправляємо відповідь водію у фоні, щоб швидко закрити Webhook
            background_tasks.add_task(send_telegram_message, chat_id, response.response_text)
            
        except Exception as e:
            # Якщо система просить покликати людину (Fail-Safe)
            fallback_text = "Хвилинку, з'єдную з живим диспетчером..."
            background_tasks.add_task(send_telegram_message, chat_id, fallback_text)

    return {"ok": True}
