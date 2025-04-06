"""Authentication service implementation."""

from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status

from ai_worthy_api_roo_1.core.config import settings
from ai_worthy_api_roo_1.core.security import create_access_token, verify_password
from ai_worthy_api_roo_1.database.models import User
from ai_worthy_api_roo_1.repositories.unit_of_work import UnitOfWorkProtocol
from ai_worthy_api_roo_1.schemas.auth import Token, UserCreate, UserLogin


class AuthService:
    """Service for authentication-related operations."""
    
    def __init__(self, unit_of_work: UnitOfWorkProtocol):
        """
        Initialize the service.
        
        Args:
            unit_of_work: The unit of work.
        """
        self.unit_of_work = unit_of_work
    
    async def register_user(self, user_data: UserCreate) -> bool:
        """
        Register a new user.
        
        Args:
            user_data: The user registration data.
            
        Returns:
            True if registration was successful.
            
        Raises:
            HTTPException: If the username already exists.
        """
        async with self.unit_of_work as uow:
            # Check if username exists
            existing_user = await uow.user_repository.get_by_username(user_data.username)
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists",
                )
            
            # Create new user
            await uow.user_repository.create(user_data)
            
            return True
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            username: The username.
            password: The password.
            
        Returns:
            The authenticated user if successful, None otherwise.
        """
        async with self.unit_of_work as uow:
            user = await uow.user_repository.get_by_username(username)
            
            if not user or not verify_password(password, user.password):
                return None
            
            return user
    
    async def login(self, login_data: UserLogin) -> User:
        """
        Login a user.
        
        Args:
            login_data: The login data.
            
        Returns:
            The authenticated user.
            
        Raises:
            HTTPException: If authentication fails.
        """
        user = await self.authenticate_user(login_data.username, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        
        return user
    
    async def create_access_token_for_user(self, user_id: int) -> Token:
        """
        Create an access token for a user.
        
        Args:
            user_id: The user ID.
            
        Returns:
            The access token.
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user_id, expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")


def get_auth_service(unit_of_work: UnitOfWorkProtocol) -> AuthService:
    """
    Factory function to create a new Auth service.
    
    Args:
        unit_of_work: The unit of work.
        
    Returns:
        A new Auth service instance.
    """
    return AuthService(unit_of_work)