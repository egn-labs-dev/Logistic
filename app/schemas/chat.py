from typing import Dict
from pydantic import BaseModel, Field

class IncomingMessage(BaseModel):
    organization_id: str = Field(..., description="Унікальний ID компанії-клієнта для RLS")
    session_id: str = Field(..., description="ID сесії діалогу")
    text: str = Field(..., min_length=1, max_length=2000, description="Текст запиту від клієнта")

class ScrubbedContext(BaseModel):
    original_text: str
    clean_text: str
    vault: Dict[str, str]

class ChatResponse(BaseModel):
    session_id: str
    response_text: str
