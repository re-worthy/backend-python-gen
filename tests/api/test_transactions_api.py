"""Tests for the transactions API endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from ai_worthy_api_roo_1.api.transactions import router
from ai_worthy_api_roo_1.database.models import User
from ai_worthy_api_roo_1.dependencies import get_transaction_service
from ai_worthy_api_roo_1.middleware.auth import get_current_user
from ai_worthy_api_roo_1.schemas.transaction import TransactionOut


# Create a test app
app = FastAPI()
app.include_router(router)


# Mock the dependencies
@pytest.fixture
def mock_transaction_service():
    """Create a mock transaction service."""
    return AsyncMock()


@pytest.fixture
def mock_current_user():
    """Create a mock current user."""
    return User(
        id=1,
        username="testuser",
        password="hashed_password",
        balance=5000,  # $50.00 in cents
        primary_currency="USD"
    )


@pytest.fixture
def client(mock_transaction_service, mock_current_user):
    """Create a test client with mocked dependencies."""
    # Override the dependencies
    app.dependency_overrides[get_transaction_service] = lambda: mock_transaction_service
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    
    # Create the test client
    client = TestClient(app)
    
    yield client
    
    # Clean up
    app.dependency_overrides.clear()


def test_get_recent_transactions(client, mock_transaction_service, mock_current_user):
    """Test getting recent transactions."""
    # Arrange
    mock_transactions = [
        TransactionOut(
            id=1,
            description="Test transaction 1",
            currency="USD",
            amount=10.00,
            is_income=True,
            created_at=1617235200000,
            tags=["tag1", "tag2"]
        ),
        TransactionOut(
            id=2,
            description="Test transaction 2",
            currency="USD",
            amount=20.00,
            is_income=False,
            created_at=1617235100000,
            tags=["tag3"]
        )
    ]
    mock_transaction_service.get_recent_transactions.return_value = mock_transactions
    
    # Act
    response = client.get("/transactions/recent")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "description": "Test transaction 1",
            "currency": "USD",
            "amount": 10.0,
            "is_income": True,
            "created_at": 1617235200000,
            "tags": ["tag1", "tag2"]
        },
        {
            "id": 2,
            "description": "Test transaction 2",
            "currency": "USD",
            "amount": 20.0,
            "is_income": False,
            "created_at": 1617235100000,
            "tags": ["tag3"]
        }
    ]
    mock_transaction_service.get_recent_transactions.assert_called_once_with(mock_current_user.id)


def test_get_transactions(client, mock_transaction_service, mock_current_user):
    """Test getting transactions with filters."""
    # Arrange
    mock_transactions = [
        TransactionOut(
            id=1,
            description="Test transaction 1",
            currency="USD",
            amount=10.00,
            is_income=True,
            created_at=1617235200000,
            tags=["tag1", "tag2"]
        )
    ]
    mock_transaction_service.get_transactions.return_value = mock_transactions
    
    # Act
    response = client.get("/transactions/?page=1&per_page=10&description=Test&start_date=1617235000000&end_date=1617235300000&tags=tag1")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "description": "Test transaction 1",
            "currency": "USD",
            "amount": 10.0,
            "is_income": True,
            "created_at": 1617235200000,
            "tags": ["tag1", "tag2"]
        }
    ]
    mock_transaction_service.get_transactions.assert_called_once()
    # Check that the user_id was passed correctly
    args, _ = mock_transaction_service.get_transactions.call_args
    assert args[0] == mock_current_user.id
    # We don't check the filters in detail since they're handled by FastAPI's dependency injection


def test_create_transaction(client, mock_transaction_service, mock_current_user):
    """Test creating a transaction."""
    # Arrange
    mock_transaction_service.create_transaction.return_value = True
    
    # Act
    response = client.post(
        "/transactions/",
        json={
            "description": "Test transaction",
            "currency": "USD",
            "amount": 10.0,
            "is_income": True,
            "tags": ["tag1", "tag2"]
        }
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json() is True
    mock_transaction_service.create_transaction.assert_called_once()
    # Check that the transaction data was passed correctly
    args, _ = mock_transaction_service.create_transaction.call_args
    assert args[1] == mock_current_user.id
    assert args[0].description == "Test transaction"
    assert args[0].currency == "USD"
    assert args[0].amount == 10.0
    assert args[0].is_income is True
    assert args[0].tags == ["tag1", "tag2"]


def test_get_transaction(client, mock_transaction_service, mock_current_user):
    """Test getting a transaction by ID."""
    # Arrange
    mock_transaction = TransactionOut(
        id=1,
        description="Test transaction",
        currency="USD",
        amount=10.00,
        is_income=True,
        created_at=1617235200000,
        tags=["tag1", "tag2"]
    )
    mock_transaction_service.get_transaction.return_value = mock_transaction
    
    # Act
    response = client.get("/transactions/1")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "description": "Test transaction",
        "currency": "USD",
        "amount": 10.0,
        "is_income": True,
        "created_at": 1617235200000,
        "tags": ["tag1", "tag2"]
    }
    mock_transaction_service.get_transaction.assert_called_once_with(1, mock_current_user.id)


def test_delete_transaction(client, mock_transaction_service, mock_current_user):
    """Test deleting a transaction."""
    # Arrange
    mock_transaction_service.delete_transaction.return_value = True
    
    # Act
    response = client.delete("/transactions/1")
    
    # Assert
    assert response.status_code == 200
    assert response.json() is True
    mock_transaction_service.delete_transaction.assert_called_once_with(1, mock_current_user.id)