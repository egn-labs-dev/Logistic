import re
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from app.db.database import AsyncSessionLocal
from app.db.models import User
from app.security.auth import verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, create_reset_token, verify_reset_token, create_refresh_token, verify_refresh_token, get_current_user_token_data, TokenData
from app.services.email_service import send_password_reset_email

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    organization_id: str

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    organization_id: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new dispatcher and create/join an organization"""
    if len(user_data.password) < 8 or not re.search(r"\d", user_data.password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long, contain at least one digit and one special character."
        )
        
    if not re.match(r"^[a-z0-9_]{3,50}$", user_data.organization_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID format. Only lowercase letters, digits, and underscores allowed, 3-50 characters."
        )

    async with AsyncSessionLocal() as session:
        # Check if email already exists
        query = select(User).where(User.email == user_data.email)
        result = await session.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create a new user
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
    """Obtain JWT token via email and password"""
    # For authentication we open a standard session (without RLS) because the user is not yet authorized
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
        
        # Embed critical data into the token: ID, role, and organization (for RLS)
        token_payload = {"sub": str(user.id), "role": user.role, "org_id": user.organization_id}
        access_token = create_access_token(
            data=token_payload,
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data=token_payload)
        
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
async def refresh_access_token(request: RefreshTokenRequest):
    token_data = verify_refresh_token(request.refresh_token)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(token_data.user_id), "role": token_data.role, "org_id": token_data.organization_id},
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
    """Send an email for password reset"""
    async with AsyncSessionLocal() as session:
        query = select(User).where(User.email == request.email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        # We always return success (to avoid exposing email existence in the database)
        if user:
            token = create_reset_token(user.email)
            try:
                await send_password_reset_email(user.email, token)
            except Exception as e:
                # In a real production environment, log the email sending error
                pass
                
        return {"message": "If this email is registered, a password reset link has been sent."}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Set a new password using a token"""
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

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    token_data: TokenData = Depends(get_current_user_token_data)
):
    """Отримання повних даних профілю поточного користувача"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == token_data.user_id))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            organization_id=user.organization_id
        )

@router.put("/password")
async def update_user_password(
    payload: PasswordUpdate,
    token_data: TokenData = Depends(get_current_user_token_data)
):
    """Безпечна зміна пароля з перевіркою старого"""
    if len(payload.new_password) < 8 or not re.search(r"\d", payload.new_password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", payload.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long, contain at least one digit and one special character."
        )

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == token_data.user_id))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if not verify_password(payload.old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Невірний поточний пароль")
            
        user.hashed_password = get_password_hash(payload.new_password)
        await session.commit()
        
        return {"detail": "Password updated successfully"}
