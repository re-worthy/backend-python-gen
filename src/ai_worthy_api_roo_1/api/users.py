"""User-related API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends

from ai_worthy_api_roo_1.dependencies import get_user_service
from ai_worthy_api_roo_1.database.models import User
from ai_worthy_api_roo_1.middleware.auth import get_current_user
from ai_worthy_api_roo_1.schemas.user import UserBalance, UserOut
from ai_worthy_api_roo_1.services.user_service import UserService

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
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Get current user's balance.
    
    Args:
        current_user: The authenticated user.
        user_service: User service.
        
    Returns:
        User balance and currency.
    """
    return await user_service.get_user_balance(current_user.id)