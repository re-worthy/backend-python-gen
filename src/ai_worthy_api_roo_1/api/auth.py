"""Authentication-related API endpoints."""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_worthy_api_roo_1.core.config import settings
from ai_worthy_api_roo_1.core.security import (
    create_access_token, get_password_hash, verify_password
)
from ai_worthy_api_roo_1.database.database import get_db
from ai_worthy_api_roo_1.database.models import User
from ai_worthy_api_roo_1.schemas.auth import Token, UserCreate, UserLogin
from ai_worthy_api_roo_1.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login.
    
    Args:
        form_data: OAuth2 form data.
        db: Database session.
        
    Returns:
        Access token.
    """
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=UserOut)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    User login endpoint.
    
    Args:
        login_data: Login credentials.
        db: Database session.
        
    Returns:
        User information.
    """
    result = await db.execute(
        select(User).where(User.username == login_data.username)
    )
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
    
    return user


@router.post("/register", response_model=bool)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user.
    
    Args:
        user_data: User registration data.
        db: Database session.
        
    Returns:
        True if registration was successful.
    """
    # Check if username exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    
    # Set default image if not provided
    if not user_data.image:
        user_data.image = f"https://api.dicebear.com/7.x/identicon/svg?seed={user_data.username}"
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user
    new_user = User(
        username=user_data.username,
        password=hashed_password,
        image=user_data.image,
    )
    
    db.add(new_user)
    await db.commit()
    
    return True