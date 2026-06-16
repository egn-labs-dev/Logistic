import os
import logging

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.chat import process_secure_message
from app.db.database import AsyncSessionLocal
from app.db.models import ApiKey, OrganizationSetting
from app.schemas.chat import IncomingMessage
from app.security.injection_shield import validate_against_injection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])

# ==========================================
# TELEGRAM INTEGRATION
# ==========================================
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
            logger.error(f"Chat processing failed for tenant {tenant_id}: {str(e)}")
            fallback_text = "Хвилинку, з'єдную з живим диспетчером..."
            background_tasks.add_task(send_telegram_message, secret_bot_token, chat_id, fallback_text)

    return {"ok": True}

# ==========================================
# VIBER INTEGRATION
# ==========================================
async def send_viber_message(bot_token: str, receiver_id: str, text: str):
    """Відправка відповіді через Viber API"""
    url = "https://chatapi.viber.com/pa/send_message"
    headers = {"X-Viber-Auth-Token": bot_token}
    payload = {
        "receiver": receiver_id,
        "type": "text",
        "text": text
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=payload)

@router.post("/viber/{secret_bot_token}")
async def viber_webhook(
    secret_bot_token: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Мультитенантний вебхук для Viber"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(OrganizationSetting.organization_id)
            .where(OrganizationSetting.viber_bot_token == secret_bot_token)
        )
        tenant_id = result.scalar_one_or_none()

    if not tenant_id:
        raise HTTPException(status_code=403, detail="Invalid Viber token")

    update = await request.json()
    
    # Viber надсилає подію "webhook" при підключенні, маємо відповісти 200 OK
    if update.get("event") == "webhook":
        return Response(status_code=200)

    if update.get("event") == "message" and "message" in update and update["message"].get("type") == "text":
        sender_id = update["sender"]["id"]
        driver_text = update["message"]["text"]
        
        incoming_msg = IncomingMessage(
            session_id=f"vb_{sender_id}",
            text=driver_text
        )
        
        try:
            response = await process_secure_message(
                request=request,
                payload=incoming_msg,
                organization_id=tenant_id
            )
            background_tasks.add_task(send_viber_message, secret_bot_token, sender_id, response.response_text)
        except Exception as e:
            logger.error(f"Viber processing failed: {str(e)}")
            background_tasks.add_task(send_viber_message, secret_bot_token, sender_id, "З'єдную з диспетчером...")

    return Response(status_code=200)

# ==========================================
# WHATSAPP INTEGRATION (Meta Cloud API)
# ==========================================
async def send_whatsapp_message(api_token: str, phone_number_id: str, to_number: str, text: str):
    """Відправка відповіді через WhatsApp Business API"""
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=payload)

@router.get("/whatsapp/{secret_api_token}")
async def whatsapp_verify_webhook(
    secret_api_token: str,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Meta вимагає GET-запит для перевірки вебхуку під час налаштування"""
    # secret_api_token тут слугує як verify_token для простоти
    if hub_mode == "subscribe" and hub_verify_token == secret_api_token:
        return Response(content=hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/whatsapp/{secret_api_token}")
async def whatsapp_webhook(
    secret_api_token: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Мультитенантний вебхук для WhatsApp"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(OrganizationSetting.organization_id)
            .where(OrganizationSetting.whatsapp_api_token == secret_api_token)
        )
        tenant_id = result.scalar_one_or_none()

    if not tenant_id:
        raise HTTPException(status_code=403, detail="Invalid WhatsApp token")

    update = await request.json()
    
    try:
        # Парсинг складної структури WhatsApp JSON
        entry = update.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        
        if "messages" in value:
            message = value["messages"][0]
            if message.get("type") == "text":
                from_number = message["from"]
                driver_text = message["text"]["body"]
                phone_number_id = value["metadata"]["phone_number_id"]
                
                incoming_msg = IncomingMessage(
                    session_id=f"wa_{from_number}",
                    text=driver_text
                )
                
                response = await process_secure_message(
                    request=request,
                    payload=incoming_msg,
                    organization_id=tenant_id
                )
                background_tasks.add_task(send_whatsapp_message, secret_api_token, phone_number_id, from_number, response.response_text)
                
    except Exception as e:
        logger.error(f"WhatsApp processing failed: {str(e)}")
        # У разі критичної помилки можемо спробувати відправити fallback, якщо маємо phone_number_id
        
    return Response(status_code=200)
