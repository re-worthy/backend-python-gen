"""Schemas for authentication."""

from pydantic import BaseModel, Field, EmailStr


class Token(BaseModel):
    """Token schema."""
    
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""
    
    user_id: int = None


class UserCreate(BaseModel):
    """User creation schema."""
    
    username: str
    password: str
    image: str = None


class UserLogin(BaseModel):
    """User login schema."""
    
    username: str
    password: str