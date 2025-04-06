"""Tests for the transaction service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai_worthy_api_roo_1.database.models import Transaction, User, Tag
from ai_worthy_api_roo_1.services.transaction_service import TransactionService
from ai_worthy_api_roo_1.schemas.transaction import TransactionCreate, TransactionFilter, TransactionOut


@pytest.fixture
def mock_unit_of_work():
    """Create a mock unit of work."""
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    uow.transaction_repository = AsyncMock()
    uow.user_repository = AsyncMock()
    uow.tag_repository = AsyncMock()
    return uow


@pytest.fixture
def mock_transaction():
    """Create a mock transaction."""
    return Transaction(
        id=1,
        description="Test transaction",
        currency="USD",
        amount=1000,  # $10.00 in cents
        is_income=True,
        created_at=1617235200000,  # April 1, 2021
        owner_id=1
    )


@pytest.fixture
def mock_user():
    """Create a mock user."""
    return User(
        id=1,
        username="testuser",
        password="hashed_password",
        balance=5000,  # $50.00 in cents
        primary_currency="USD"
    )


@pytest.mark.asyncio
async def test_get_transaction(mock_unit_of_work, mock_transaction):
    """Test getting a transaction by ID."""
    # Arrange
    transaction_id = 1
    user_id = 1
    mock_unit_of_work.transaction_repository.get_by_id.return_value = mock_transaction
    
    # Mock tags
    mock_tags = [Tag(id=1, text="tag1", user_id=user_id, transaction_id=transaction_id)]
    mock_unit_of_work.tag_repository.get_by_transaction.return_value = mock_tags
    
    service = TransactionService(mock_unit_of_work)
    
    # Act
    result = await service.get_transaction(transaction_id, user_id)
    
    # Assert
    assert isinstance(result, TransactionOut)
    assert result.id == mock_transaction.id
    assert result.description == mock_transaction.description
    assert result.currency == mock_transaction.currency
    assert result.amount == mock_transaction.amount / 100  # Check conversion from cents to dollars
    assert result.is_income == mock_transaction.is_income
    assert result.created_at == mock_transaction.created_at
    assert result.tags == ["tag1"]
    
    mock_unit_of_work.transaction_repository.get_by_id.assert_called_once_with(transaction_id, user_id)
    mock_unit_of_work.tag_repository.get_by_transaction.assert_called_once_with(transaction_id)


@pytest.mark.asyncio
async def test_get_transaction_not_found(mock_unit_of_work):
    """Test getting a transaction by ID when the transaction doesn't exist."""
    # Arrange
    transaction_id = 1
    user_id = 1
    mock_unit_of_work.transaction_repository.get_by_id.return_value = None
    
    service = TransactionService(mock_unit_of_work)
    
    # Act
    result = await service.get_transaction(transaction_id, user_id)
    
    # Assert
    assert result is None
    mock_unit_of_work.transaction_repository.get_by_id.assert_called_once_with(transaction_id, user_id)
    mock_unit_of_work.tag_repository.get_by_transaction.assert_not_called()


@pytest.mark.asyncio
async def test_get_transactions(mock_unit_of_work, mock_transaction):
    """Test getting transactions with filters."""
    # Arrange
    user_id = 1
    filters = TransactionFilter(page=1, per_page=10)
    mock_unit_of_work.transaction_repository.get_multi.return_value = [mock_transaction]
    
    # Mock tags
    mock_tags = [Tag(id=1, text="tag1", user_id=user_id, transaction_id=mock_transaction.id)]
    mock_unit_of_work.tag_repository.get_by_transaction.return_value = mock_tags
    
    service = TransactionService(mock_unit_of_work)
    
    # Act
    result = await service.get_transactions(user_id, filters)
    
    # Assert
    assert len(result) == 1
    assert isinstance(result[0], TransactionOut)
    assert result[0].id == mock_transaction.id
    assert result[0].tags == ["tag1"]
    
    mock_unit_of_work.transaction_repository.get_multi.assert_called_once_with(user_id, filters)
    mock_unit_of_work.tag_repository.get_by_transaction.assert_called_once_with(mock_transaction.id)


@pytest.mark.asyncio
async def test_create_transaction(mock_unit_of_work, mock_user):
    """Test creating a transaction."""
    # Arrange
    user_id = 1
    transaction_data = TransactionCreate(
        description="Test transaction",
        currency="USD",
        amount=10.00,
        is_income=True,
        tags=["tag1", "tag2"]
    )
    
    mock_transaction = Transaction(
        id=1,
        description=transaction_data.description,
        currency=transaction_data.currency,
        amount=1000,  # $10.00 in cents
        is_income=transaction_data.is_income,
        owner_id=user_id
    )
    
    mock_unit_of_work.user_repository.get_by_id.return_value = mock_user
    mock_unit_of_work.transaction_repository.create.return_value = mock_transaction
    
    service = TransactionService(mock_unit_of_work)
    
    # Act
    result = await service.create_transaction(transaction_data, user_id)
    
    # Assert
    assert result is True
    
    mock_unit_of_work.user_repository.get_by_id.assert_called_once_with(user_id)
    mock_unit_of_work.transaction_repository.create.assert_called_once()
    mock_unit_of_work.user_repository.update_balance.assert_called_once()
    assert mock_unit_of_work.tag_repository.create.call_count == 2  # Two tags


@pytest.mark.asyncio
async def test_delete_transaction(mock_unit_of_work, mock_transaction, mock_user):
    """Test deleting a transaction."""
    # Arrange
    transaction_id = 1
    user_id = 1
    
    mock_unit_of_work.transaction_repository.get_by_id.return_value = mock_transaction
    mock_unit_of_work.user_repository.get_by_id.return_value = mock_user
    
    service = TransactionService(mock_unit_of_work)
    
    # Act
    result = await service.delete_transaction(transaction_id, user_id)
    
    # Assert
    assert result is True
    
    mock_unit_of_work.transaction_repository.get_by_id.assert_called_once_with(transaction_id, user_id)
    mock_unit_of_work.user_repository.get_by_id.assert_called_once_with(user_id)
    mock_unit_of_work.user_repository.update_balance.assert_called_once()
    mock_unit_of_work.transaction_repository.delete.assert_called_once_with(transaction_id, user_id)