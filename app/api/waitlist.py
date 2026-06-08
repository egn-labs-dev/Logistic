from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import WaitlistLead

router = APIRouter()

class WaitlistRequest(BaseModel):
    email: EmailStr

@router.post("/")
async def join_waitlist(payload: WaitlistRequest, db: AsyncSession = Depends(get_db)):
    """Збір лідів з Landing Page"""
    # Перевіряємо, чи немає вже такого email
    result = await db.execute(select(WaitlistLead).where(WaitlistLead.email == payload.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Цей email вже є у списку очікування!")
    
    new_lead = WaitlistLead(email=payload.email)
    db.add(new_lead)
    await db.commit()
    
    return {"detail": "Успішно додано до списку очікування!"}
