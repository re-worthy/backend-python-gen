"""Unit of Work pattern implementation for transaction management."""

from typing import AsyncContextManager, Callable, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from ai_worthy_api_roo_1.database.database import async_session


class UnitOfWorkProtocol(Protocol):
    """Protocol defining the Unit of Work interface."""
    
    # Repository properties will be defined in concrete implementations
    
    async def __aenter__(self) -> "UnitOfWorkProtocol":
        """Enter the async context manager."""
        ...
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager."""
        ...
    
    async def commit(self) -> None:
        """Commit the current transaction."""
        ...
    
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        ...


class SQLAlchemyUnitOfWork:
    """SQLAlchemy implementation of the Unit of Work pattern."""
    
    def __init__(self, session_factory: Callable[[], AsyncSession] = async_session):
        """
        Initialize the Unit of Work.
        
        Args:
            session_factory: Factory function to create a new database session.
        """
        self.session_factory = session_factory
        self.session = None
        
        # Repositories will be initialized in __aenter__
        self.user_repository = None
        self.transaction_repository = None
        self.tag_repository = None
    
    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        """
        Enter the async context manager.
        
        Returns:
            The Unit of Work instance with initialized repositories.
        """
        # Import here to avoid circular imports
        from ai_worthy_api_roo_1.repositories.user_repository import SQLAlchemyUserRepository
        from ai_worthy_api_roo_1.repositories.transaction_repository import SQLAlchemyTransactionRepository
        from ai_worthy_api_roo_1.repositories.tag_repository import SQLAlchemyTagRepository
        
        self.session = self.session_factory()
        
        # Initialize repositories with the session
        self.user_repository = SQLAlchemyUserRepository(self.session)
        self.transaction_repository = SQLAlchemyTransactionRepository(self.session)
        self.tag_repository = SQLAlchemyTagRepository(self.session)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the async context manager.
        
        Args:
            exc_type: Exception type if an exception was raised, None otherwise.
            exc_val: Exception value if an exception was raised, None otherwise.
            exc_tb: Exception traceback if an exception was raised, None otherwise.
        """
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.session.close()
    
    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.session.commit()
    
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        await self.session.rollback()


def get_unit_of_work() -> SQLAlchemyUnitOfWork:
    """
    Factory function to create a new Unit of Work.
    
    Returns:
        A new Unit of Work instance.
    """
    return SQLAlchemyUnitOfWork()