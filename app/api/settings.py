import uuid
import secrets
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import ApiKey, OrganizationSetting
from app.security.auth import get_current_user_token_data, TokenData

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])

class SystemPromptRequest(BaseModel):
    system_prompt: Optional[str] = None

class SystemPromptResponse(BaseModel):
    system_prompt: Optional[str] = None

class ApiKeyResponse(BaseModel):
    id: str
    key: str
    created_at: str

@router.get("/prompt", response_model=SystemPromptResponse)
async def get_system_prompt(token_data: TokenData = Depends(get_current_user_token_data)):
    async with AsyncSessionLocal() as session:
        query = select(OrganizationSetting).where(OrganizationSetting.organization_id == token_data.organization_id)
        result = await session.execute(query)
        setting = result.scalar_one_or_none()
        
        return SystemPromptResponse(system_prompt=setting.system_prompt if setting else None)

@router.put("/prompt", response_model=SystemPromptResponse)
async def update_system_prompt(
    payload: SystemPromptRequest,
    token_data: TokenData = Depends(get_current_user_token_data)
):
    async with AsyncSessionLocal() as session:
        query = select(OrganizationSetting).where(OrganizationSetting.organization_id == token_data.organization_id)
        result = await session.execute(query)
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.system_prompt = payload.system_prompt
        else:
            setting = OrganizationSetting(
                organization_id=token_data.organization_id,
                system_prompt=payload.system_prompt
            )
            session.add(setting)
            
        await session.commit()
        return SystemPromptResponse(system_prompt=setting.system_prompt)

@router.get("/apikeys", response_model=List[ApiKeyResponse])
async def list_api_keys(token_data: TokenData = Depends(get_current_user_token_data)):
    async with AsyncSessionLocal() as session:
        query = select(ApiKey).where(ApiKey.organization_id == token_data.organization_id).order_by(ApiKey.created_at.desc())
        result = await session.execute(query)
        keys = result.scalars().all()
        
        return [
            ApiKeyResponse(
                id=str(k.id),
                key=k.key,
                created_at=k.created_at.isoformat()
            ) for k in keys
        ]

@router.post("/apikeys", response_model=ApiKeyResponse)
async def generate_api_key(token_data: TokenData = Depends(get_current_user_token_data)):
    # Simple generation: sk_live_ + 32 random characters
    raw_key = "sk_live_" + secrets.token_hex(16)
    
    async with AsyncSessionLocal() as session:
        new_key = ApiKey(
            organization_id=token_data.organization_id,
            key=raw_key
        )
        session.add(new_key)
        await session.commit()
        
        return ApiKeyResponse(
            id=str(new_key.id),
            key=new_key.key,
            created_at=new_key.created_at.isoformat()
        )

@router.delete("/apikeys/{key_id}")
async def delete_api_key(key_id: str, token_data: TokenData = Depends(get_current_user_token_data)):
    async with AsyncSessionLocal() as session:
        # Verify the key belongs to the user's organization
        try:
            key_uuid = uuid.UUID(key_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Key ID format")
            
        query = select(ApiKey).where(ApiKey.id == key_uuid, ApiKey.organization_id == token_data.organization_id)
        result = await session.execute(query)
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(status_code=404, detail="API Key not found")
            
        await session.delete(api_key)
        await session.commit()
        return {"status": "ok"}
