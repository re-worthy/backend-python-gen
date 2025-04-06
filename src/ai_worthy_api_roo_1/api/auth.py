"""Authentication-related API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from ai_worthy_api_roo_1.dependencies import get_auth_service
from ai_worthy_api_roo_1.schemas.auth import Token, UserCreate, UserLogin
from ai_worthy_api_roo_1.schemas.user import UserOut
from ai_worthy_api_roo_1.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """
    OAuth2 compatible token login.
    
    Args:
        form_data: OAuth2 form data.
        auth_service: Authentication service.
        
    Returns:
        Access token.
    """
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        # The exception is raised in the service
        pass
    
    return await auth_service.create_access_token_for_user(user.id)


@router.post("/login", response_model=UserOut)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """
    User login endpoint.
    
    Args:
        login_data: Login credentials.
        auth_service: Authentication service.
        
    Returns:
        User information.
    """
    return await auth_service.login(login_data)


@router.post("/register", response_model=bool)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """
    Register a new user.
    
    Args:
        user_data: User registration data.
        auth_service: Authentication service.
        
    Returns:
        True if registration was successful.
    """
    return await auth_service.register_user(user_data)