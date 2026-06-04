import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from pydantic import BaseModel
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import ApiKey
import logging

# Налаштування безпеки (в продакшені SECRET_KEY береться з .env)
SECRET_KEY = os.getenv("JWT_SECRET_KEY") or ("test-secret-key-do-not-use-in-production" if os.getenv("TESTING") == "True" else "")
if not SECRET_KEY:
    logging.critical("FATAL: JWT_SECRET_KEY is not set!")
    import sys
    sys.exit(1)
    
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Диспетчери часто працюють позмінно

# Налаштування passlib для Bcrypt хешування
# FastAPI залежність для витягування токена з заголовка Authorization: Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[str] = None

async def get_current_user_token_data(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_exception
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        org_id: str = payload.get("org_id")
        if user_id is None or org_id is None:
            raise credentials_exception
        return TokenData(user_id=user_id, role=role, organization_id=org_id)
    except jwt.PyJWTError:
        raise credentials_exception

async def require_dispatcher_role(token_data: TokenData = Depends(get_current_user_token_data)) -> TokenData:
    if token_data.role not in ["dispatcher", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return token_data

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {"sub": email, "exp": expire, "type": "reset"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_refresh_token(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        org_id: str = payload.get("org_id")
        if user_id is None or org_id is None:
            raise credentials_exception
        return TokenData(user_id=user_id, role=role, organization_id=org_id)
    except jwt.PyJWTError:
        raise credentials_exception

def verify_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_token.get("type") != "reset":
            return None
        return decoded_token.get("sub")
    except jwt.PyJWTError:
        return None

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_organization_from_api_key(api_key: str = Depends(api_key_header)) -> str:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ApiKey).where(ApiKey.key == api_key))
        api_key_obj = result.scalar_one_or_none()
        if not api_key_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key",
            )
        return api_key_obj.organization_id
