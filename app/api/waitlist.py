import os

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.webhooks import send_telegram_message
from app.db.database import get_db
from app.db.models import WaitlistLead

router = APIRouter()

# ID твого особистого чату або закритої групи для сповіщень
ADMIN_CHAT_ID = os.getenv("ADMIN_TELEGRAM_CHAT_ID")

class WaitlistRequest(BaseModel):
    email: EmailStr

@router.post("/")
async def join_waitlist(
    payload: WaitlistRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Збір лідів з Landing Page та миттєве сповіщення в Telegram"""
    # 1. Перевіряємо дублікати
    result = await db.execute(select(WaitlistLead).where(WaitlistLead.email == payload.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Цей email вже є у списку очікування!")
    
    # 2. Зберігаємо в базу
    new_lead = WaitlistLead(email=payload.email)
    db.add(new_lead)
    await db.commit()
    
    # 3. Відправляємо миттєве сповіщення у фоні
    if ADMIN_CHAT_ID:
        notification_text = (
            "🔥 Новий гарячий лід на Zero Trust Dispatch!\n"
            f"📧 Email: {payload.email}\n"
            "⏳ Зв'яжіться з ним якнайшвидше!"
        )
        background_tasks.add_task(send_telegram_message, ADMIN_CHAT_ID, notification_text)
    
    return {"detail": "Успішно додано до списку очікування!"}
