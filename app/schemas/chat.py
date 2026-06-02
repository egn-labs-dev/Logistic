from typing import Dict
from pydantic import BaseModel, Field

class IncomingMessage(BaseModel):
    organization_id: str = Field(..., description="Unique client company ID for RLS")
    session_id: str = Field(..., description="Dialogue session ID")
    text: str = Field(..., min_length=1, max_length=2000, description="Client request text")

class ScrubbedContext(BaseModel):
    original_text: str
    clean_text: str
    vault: Dict[str, str]

class ChatResponse(BaseModel):
    session_id: str
    response_text: str
