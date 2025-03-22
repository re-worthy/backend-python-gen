"""Schemas for user-related operations."""

from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    """Base user schema."""
    
    username: str
    image: str


class UserOut(UserBase):
    """User output schema."""
    
    id: int
    primary_currency: str
    
    class Config:
        """Pydantic config."""
        
        from_attributes = True


class UserBalance(BaseModel):
    """User balance schema."""
    
    balance: float
    currency: str