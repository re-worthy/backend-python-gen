"""User-related API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_worthy_api_roo_1.database.database import get_db
from ai_worthy_api_roo_1.database.models import User
from ai_worthy_api_roo_1.middleware.auth import get_current_user
from ai_worthy_api_roo_1.schemas.user import UserBalance, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user profile information.
    
    Args:
        current_user: The authenticated user.
        
    Returns:
        User information.
    """
    return current_user


@router.get("/balance", response_model=UserBalance)
async def get_user_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current user's balance.
    
    Args:
        current_user: The authenticated user.
        db: Database session.
        
    Returns:
        User balance and currency.
    """
    result = await db.execute(
        select(User.balance, User.primary_currency)
        .where(User.id == current_user.id)
    )
    user_data = result.first()
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    balance, currency = user_data
    
    return UserBalance(
        # Convert from integer cents to float dollars
        balance=balance / 100,
        currency=currency
    )