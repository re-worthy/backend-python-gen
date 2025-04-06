"""User repository implementation."""

from typing import List, Optional, Protocol

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ai_worthy_api_roo_1.database.models import User
from ai_worthy_api_roo_1.schemas.auth import UserCreate
from ai_worthy_api_roo_1.core.security import get_password_hash


class UserRepositoryProtocol(Protocol):
    """Protocol defining the User repository interface."""
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: The user ID.
            
        Returns:
            The user if found, None otherwise.
        """
        ...
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: The username.
            
        Returns:
            The user if found, None otherwise.
        """
        ...
    
    async def create(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: The user data.
            
        Returns:
            The created user.
        """
        ...
    
    async def update_balance(self, user_id: int, new_balance: int) -> None:
        """
        Update a user's balance.
        
        Args:
            user_id: The user ID.
            new_balance: The new balance.
        """
        ...
    
    async def get_balance(self, user_id: int) -> Optional[tuple[int, str]]:
        """
        Get a user's balance and currency.
        
        Args:
            user_id: The user ID.
            
        Returns:
            A tuple of (balance, currency) if found, None otherwise.
        """
        ...


class SQLAlchemyUserRepository:
    """SQLAlchemy implementation of the User repository."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository.
        
        Args:
            session: The database session.
        """
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: The user ID.
            
        Returns:
            The user if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: The username.
            
        Returns:
            The user if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()
    
    async def create(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: The user data.
            
        Returns:
            The created user.
        """
        # Set default image if not provided
        image = user_data.image
        if not image:
            image = f"https://api.dicebear.com/7.x/identicon/svg?seed={user_data.username}"
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create new user
        new_user = User(
            username=user_data.username,
            password=hashed_password,
            image=image,
        )
        
        self.session.add(new_user)
        await self.session.flush()
        
        return new_user
    
    async def update_balance(self, user_id: int, new_balance: int) -> None:
        """
        Update a user's balance.
        
        Args:
            user_id: The user ID.
            new_balance: The new balance.
        """
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(balance=new_balance)
        )
    
    async def get_balance(self, user_id: int) -> Optional[tuple[int, str]]:
        """
        Get a user's balance and currency.
        
        Args:
            user_id: The user ID.
            
        Returns:
            A tuple of (balance, currency) if found, None otherwise.
        """
        result = await self.session.execute(
            select(User.balance, User.primary_currency)
            .where(User.id == user_id)
        )
        return result.first()


def get_user_repository(session: AsyncSession) -> UserRepositoryProtocol:
    """
    Factory function to create a new User repository.
    
    Args:
        session: The database session.
        
    Returns:
        A new User repository instance.
    """
    return SQLAlchemyUserRepository(session)