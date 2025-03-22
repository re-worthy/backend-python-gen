"""Schemas for transaction-related operations."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """Base tag schema."""
    
    text: str


class TransactionBase(BaseModel):
    """Base transaction schema."""
    
    description: str
    currency: str
    amount: float
    is_income: bool


class TransactionCreate(TransactionBase):
    """Transaction creation schema."""
    
    tags: List[str] = []


class TransactionOut(TransactionBase):
    """Transaction output schema."""
    
    id: int
    created_at: int
    tags: List[str] = []
    
    class Config:
        """Pydantic config."""
        
        from_attributes = True


class TransactionFilter(BaseModel):
    """Transaction filter schema."""
    
    page: int = Field(ge=1, default=1)
    per_page: int = Field(ge=1, le=100, default=10)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None