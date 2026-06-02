from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from app.db.database import AsyncSessionLocal
from app.db.models import User
from app.security.auth import verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, create_reset_token, verify_reset_token
from app.services.email_service import send_password_reset_email

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    organization_id: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Реєстрація нового диспетчера та створення/приєднання до організації"""
    async with AsyncSessionLocal() as session:
        # Перевірка чи існує такий email
        query = select(User).where(User.email == user_data.email)
        result = await session.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Створення нового користувача
        new_user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            role="dispatcher",
            organization_id=user_data.organization_id
        )
        session.add(new_user)
        await session.commit()
        
        return {"message": "User successfully registered", "email": new_user.email}

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Отримання JWT токена за email та паролем"""
    # Для автентифікації ми відкриваємо звичайну сесію (без RLS), бо користувач ще не авторизований
    async with AsyncSessionLocal() as session:
        query = select(User).where(User.email == form_data.username)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Зашиваємо у токен критичні дані: ID, роль та організацію (для RLS)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role, "org_id": user.organization_id},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Відправка email для скидання паролю"""
    async with AsyncSessionLocal() as session:
        query = select(User).where(User.email == request.email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        # Ми завжди повертаємо успіх (щоб не розкривати наявність email в базі)
        if user:
            token = create_reset_token(user.email)
            try:
                await send_password_reset_email(user.email, token)
            except Exception as e:
                # В реальному продакшені логуємо помилку відправки листа
                pass
                
        return {"message": "If this email is registered, a password reset link has been sent."}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Встановлення нового паролю за допомогою токена"""
    email = verify_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
        
    async with AsyncSessionLocal() as session:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        user.hashed_password = get_password_hash(request.new_password)
        await session.commit()
        
        return {"message": "Password has been reset successfully"}
