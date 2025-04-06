"""Tests for the user service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from ai_worthy_api_roo_1.database.models import User
from ai_worthy_api_roo_1.services.user_service import UserService
from ai_worthy_api_roo_1.schemas.user import UserBalance


@pytest.fixture
def mock_unit_of_work():
    """Create a mock unit of work."""
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    uow.user_repository = AsyncMock()
    return uow


@pytest.mark.asyncio
async def test_get_user_by_id(mock_unit_of_work):
    """Test getting a user by ID."""
    # Arrange
    user_id = 1
    mock_user = User(id=user_id, username="testuser", password="hashed_password")
    mock_unit_of_work.user_repository.get_by_id.return_value = mock_user
    
    service = UserService(mock_unit_of_work)
    
    # Act
    result = await service.get_user_by_id(user_id)
    
    # Assert
    assert result == mock_user
    mock_unit_of_work.user_repository.get_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(mock_unit_of_work):
    """Test getting a user by ID when the user doesn't exist."""
    # Arrange
    user_id = 1
    mock_unit_of_work.user_repository.get_by_id.return_value = None
    
    service = UserService(mock_unit_of_work)
    
    # Act
    result = await service.get_user_by_id(user_id)
    
    # Assert
    assert result is None
    mock_unit_of_work.user_repository.get_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_balance(mock_unit_of_work):
    """Test getting a user's balance."""
    # Arrange
    user_id = 1
    balance = 1000
    currency = "USD"
    mock_unit_of_work.user_repository.get_balance.return_value = (balance, currency)
    
    service = UserService(mock_unit_of_work)
    
    # Act
    result = await service.get_user_balance(user_id)
    
    # Assert
    assert isinstance(result, UserBalance)
    assert result.balance == balance / 100  # Check conversion from cents to dollars
    assert result.currency == currency
    mock_unit_of_work.user_repository.get_balance.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_balance_not_found(mock_unit_of_work):
    """Test getting a user's balance when the user doesn't exist."""
    # Arrange
    user_id = 1
    mock_unit_of_work.user_repository.get_balance.return_value = None
    
    service = UserService(mock_unit_of_work)
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.get_user_balance(user_id)
    
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "User not found"
    mock_unit_of_work.user_repository.get_balance.assert_called_once_with(user_id)