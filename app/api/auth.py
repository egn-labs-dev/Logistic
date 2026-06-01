from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import User
from app.security.auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

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
