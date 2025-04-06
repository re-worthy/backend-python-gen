# Repository Pattern Implementation

This document describes the implementation of the Repository Pattern in the Financial Tracking API.

## Overview

The Repository Pattern provides an abstraction layer between the business logic and data access layers, making the application more maintainable, testable, and adaptable to future database changes.

## Directory Structure

```
src/ai_worthy_api_roo_1/
├── repositories/
│   ├── __init__.py
│   ├── base.py
│   ├── user_repository.py
│   ├── transaction_repository.py
│   ├── tag_repository.py
│   └── unit_of_work.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── user_service.py
│   └── transaction_service.py
└── ...
```

## Components

### Repository Interfaces

Repository interfaces define the contract for data access operations. They are implemented using Python's Protocol classes to provide type hints without requiring inheritance.

Example from `user_repository.py`:

```python
class UserRepositoryProtocol(Protocol):
    """Protocol defining the User repository interface."""
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        ...
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        ...
    
    # Other methods...
```

### Repository Implementations

Repository implementations provide concrete implementations of the repository interfaces for specific database technologies.

Example from `user_repository.py`:

```python
class SQLAlchemyUserRepository:
    """SQLAlchemy implementation of the User repository."""
    
    def __init__(self, session: AsyncSession):
        """Initialize the repository."""
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()
    
    # Other methods...
```

### Unit of Work Pattern

The Unit of Work pattern coordinates operations across multiple repositories and ensures they all succeed or fail together.

Example from `unit_of_work.py`:

```python
class SQLAlchemyUnitOfWork:
    """SQLAlchemy implementation of the Unit of Work pattern."""
    
    def __init__(self, session_factory):
        """Initialize the Unit of Work."""
        self.session_factory = session_factory
        
    async def __aenter__(self):
        """Enter the async context manager."""
        self.session = self.session_factory()
        self.user_repository = SQLAlchemyUserRepository(self.session)
        self.transaction_repository = SQLAlchemyTransactionRepository(self.session)
        self.tag_repository = SQLAlchemyTagRepository(self.session)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.session.close()
```

### Service Layer

The service layer implements business logic and uses repositories to access data.

Example from `transaction_service.py`:

```python
class TransactionService:
    """Service for transaction-related operations."""
    
    def __init__(self, unit_of_work: UnitOfWorkProtocol):
        """Initialize the service."""
        self.unit_of_work = unit_of_work
    
    async def create_transaction(self, transaction_data: TransactionCreate, user_id: int) -> bool:
        """Create a new transaction."""
        async with self.unit_of_work as uow:
            # Get user to check if exists and get current balance
            user = await uow.user_repository.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Create transaction
            new_transaction = await uow.transaction_repository.create(
                transaction_data, user_id
            )
            
            # Update user balance
            formatted_amount = int(transaction_data.amount * 100)
            if transaction_data.is_income:
                new_balance = user.balance + formatted_amount
            else:
                new_balance = user.balance - formatted_amount
            
            await uow.user_repository.update_balance(user_id, new_balance)
            
            # Create tags if provided
            if transaction_data.tags:
                for tag_text in transaction_data.tags:
                    await uow.tag_repository.create(
                        tag_text, user_id, new_transaction.id
                    )
            
            return True
```

### Dependency Injection

FastAPI's dependency injection system is used to provide repositories and services to API endpoints.

Example from `dependencies.py`:

```python
def get_transaction_service(
    unit_of_work: UnitOfWorkProtocol = Depends(get_unit_of_work)
) -> TransactionService:
    """Get a Transaction service instance."""
    return TransactionService(unit_of_work)
```

### API Endpoints

API endpoints use services to implement HTTP endpoints.

Example from `transactions.py`:

```python
@router.post("/", response_model=bool)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Any:
    """Create a new transaction."""
    return await transaction_service.create_transaction(transaction_data, current_user.id)
```

## Testing

The Repository Pattern makes testing easier by allowing repositories to be mocked for unit testing.

Example from `test_transaction_service.py`:

```python
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
    
    mock_unit_of_work.user_repository.get_by_id.return_value = mock_user
    mock_unit_of_work.transaction_repository.create.return_value = mock_transaction
    
    service = TransactionService(mock_unit_of_work)
    
    # Act
    result = await service.create_transaction(transaction_data, user_id)
    
    # Assert
    assert result is True
```

## Benefits

1. **Loose Coupling**: API endpoints depend on abstractions, not concrete implementations
2. **Code Reusability**: Common database operations are centralized in repositories
3. **Improved Testability**: Repositories can be mocked for unit testing
4. **Database Flexibility**: Switching database providers will only require new repository implementations
5. **Transaction Management**: The Unit of Work pattern ensures data consistency across multiple operations

## Running Tests

To run the tests, use the following command:

```bash
poetry run pytest
```

To run tests with coverage:

```bash
poetry run pytest --cov=src