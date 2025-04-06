"""User service implementation."""

from typing import Optional

from fastapi import HTTPException, status

from ai_worthy_api_roo_1.database.models import User
from ai_worthy_api_roo_1.repositories.unit_of_work import UnitOfWorkProtocol
from ai_worthy_api_roo_1.schemas.user import UserBalance


class UserService:
    """Service for user-related operations."""
    
    def __init__(self, unit_of_work: UnitOfWorkProtocol):
        """
        Initialize the service.
        
        Args:
            unit_of_work: The unit of work.
        """
        self.unit_of_work = unit_of_work
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: The user ID.
            
        Returns:
            The user if found, None otherwise.
        """
        async with self.unit_of_work as uow:
            return await uow.user_repository.get_by_id(user_id)
    
    async def get_user_balance(self, user_id: int) -> UserBalance:
        """
        Get a user's balance.
        
        Args:
            user_id: The user ID.
            
        Returns:
            The user's balance.
            
        Raises:
            HTTPException: If the user is not found.
        """
        async with self.unit_of_work as uow:
            balance_data = await uow.user_repository.get_balance(user_id)
            
            if not balance_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            
            balance, currency = balance_data
            
            return UserBalance(
                # Convert from integer cents to float dollars
                balance=balance / 100,
                currency=currency
            )


def get_user_service(unit_of_work: UnitOfWorkProtocol) -> UserService:
    """
    Factory function to create a new User service.
    
    Args:
        unit_of_work: The unit of work.
        
    Returns:
        A new User service instance.
    """
    return UserService(unit_of_work)