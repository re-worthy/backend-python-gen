"""Tests for the user repository."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai_worthy_api_roo_1.database.models import User
from ai_worthy_api_roo_1.repositories.user_repository import SQLAlchemyUserRepository
from ai_worthy_api_roo_1.schemas.auth import UserCreate


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.add = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_get_by_id(mock_session):
    """Test getting a user by ID."""
    # Arrange
    user_id = 1
    mock_user = User(id=user_id, username="testuser", password="hashed_password")
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_user
    mock_session.execute.return_value = mock_result
    
    repository = SQLAlchemyUserRepository(mock_session)
    
    # Act
    result = await repository.get_by_id(user_id)
    
    # Assert
    assert result == mock_user
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_username(mock_session):
    """Test getting a user by username."""
    # Arrange
    username = "testuser"
    mock_user = User(id=1, username=username, password="hashed_password")
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_user
    mock_session.execute.return_value = mock_result
    
    repository = SQLAlchemyUserRepository(mock_session)
    
    # Act
    result = await repository.get_by_username(username)
    
    # Assert
    assert result == mock_user
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create(mock_session):
    """Test creating a user."""
    # Arrange
    user_data = UserCreate(
        username="testuser",
        password="password123",
        image="https://example.com/image.png"
    )
    
    repository = SQLAlchemyUserRepository(mock_session)
    
    # Mock the password hashing function
    with patch("ai_worthy_api_roo_1.repositories.user_repository.get_password_hash") as mock_hash:
        mock_hash.return_value = "hashed_password"
        
        # Act
        result = await repository.create(user_data)
        
        # Assert
        assert result.username == user_data.username
        assert result.password == "hashed_password"
        assert result.image == user_data.image
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_update_balance(mock_session):
    """Test updating a user's balance."""
    # Arrange
    user_id = 1
    new_balance = 1000
    
    repository = SQLAlchemyUserRepository(mock_session)
    
    # Act
    await repository.update_balance(user_id, new_balance)
    
    # Assert
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_balance(mock_session):
    """Test getting a user's balance."""
    # Arrange
    user_id = 1
    balance = 1000
    currency = "USD"
    
    # Configure the mock to return the expected value
    mock_result = MagicMock()
    mock_result.first.return_value = (balance, currency)
    mock_session.execute.return_value = mock_result
    
    repository = SQLAlchemyUserRepository(mock_session)
    
    # Act
    result = await repository.get_balance(user_id)
    
    # Assert
    assert result == (balance, currency)
    mock_session.execute.assert_called_once()