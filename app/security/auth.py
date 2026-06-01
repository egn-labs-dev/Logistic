import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Налаштування безпеки (в продакшені SECRET_KEY береться з .env)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_ENTERPRISE_KEY_FOR_JWT_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Диспетчери часто працюють позмінно

# Налаштування passlib для Bcrypt хешування
# FastAPI залежність для витягування токена з заголовка Authorization: Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[str] = None

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
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
