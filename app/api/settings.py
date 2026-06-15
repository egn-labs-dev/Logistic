import secrets
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.db.models import ApiKey, OrganizationSetting
from app.security.auth import TokenData, get_current_user_token_data

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])

class SettingsUpdateRequest(BaseModel):
    system_prompt: Optional[str] = None
    telegram_bot_token: Optional[str] = None

class SettingsResponse(BaseModel):
    system_prompt: Optional[str] = None
    telegram_bot_token: Optional[str] = None

class ApiKeyResponse(BaseModel):
    id: str
    key: str
    created_at: str

@router.get("/", response_model=SettingsResponse)
async def get_organization_settings(token_data: TokenData = Depends(get_current_user_token_data)):
    async with AsyncSessionLocal() as session:
        query = select(OrganizationSetting).where(OrganizationSetting.organization_id == token_data.organization_id)
        result = await session.execute(query)
        setting = result.scalar_one_or_none()
        
        return SettingsResponse(
            system_prompt=setting.system_prompt if setting else None,
            telegram_bot_token=setting.telegram_bot_token if setting else None
        )

@router.put("/", response_model=SettingsResponse)
async def update_organization_settings(
    payload: SettingsUpdateRequest,
    token_data: TokenData = Depends(get_current_user_token_data)
):
    async with AsyncSessionLocal() as session:
        query = select(OrganizationSetting).where(OrganizationSetting.organization_id == token_data.organization_id)
        result = await session.execute(query)
        setting = result.scalar_one_or_none()
        
        if not setting:
            setting = OrganizationSetting(organization_id=token_data.organization_id)
            session.add(setting)
            
        if payload.system_prompt is not None:
            setting.system_prompt = payload.system_prompt
        if payload.telegram_bot_token is not None:
            setting.telegram_bot_token = payload.telegram_bot_token
            
        await session.commit()
        return SettingsResponse(
            system_prompt=setting.system_prompt,
            telegram_bot_token=setting.telegram_bot_token
        )

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
