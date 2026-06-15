import os

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from sqlalchemy import select

from app.api.chat import process_secure_message
from app.db.database import AsyncSessionLocal
from app.db.models import ApiKey
from app.schemas.chat import IncomingMessage
from app.security.injection_shield import validate_against_injection

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])

async def send_telegram_message(bot_token: str, chat_id: int, text: str):
    """Відправка відповіді через специфічного бота компанії"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": text})

@router.post("/telegram/{secret_bot_token}")
async def telegram_webhook(
    secret_bot_token: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Мультитенантний вебхук: визначає компанію за токеном її бота"""
    
    # Шукаємо організацію, якій належить цей бот
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(OrganizationSetting.organization_id)
            .where(OrganizationSetting.telegram_bot_token == secret_bot_token)
        )
        tenant_id = result.scalar_one_or_none()

    if not tenant_id:
        raise HTTPException(status_code=403, detail="Invalid or unregistered bot token")

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
            # Викликаємо захищену логіку чату з правильним tenant_id
            response = await process_secure_message(
                request=request,
                payload=incoming_msg,
                organization_id=tenant_id
            )
            
            # Відправляємо відповідь водію у фоні, щоб швидко закрити Webhook
            background_tasks.add_task(send_telegram_message, secret_bot_token, chat_id, response.response_text)
            
        except Exception as e:
            import logging
            logging.error(f"Chat processing failed for tenant {tenant_id}: {str(e)}")
            fallback_text = "Хвилинку, з'єдную з живим диспетчером..."
            background_tasks.add_task(send_telegram_message, secret_bot_token, chat_id, fallback_text)

    return {"ok": True}
