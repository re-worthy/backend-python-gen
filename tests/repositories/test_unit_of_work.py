"""Tests for the Unit of Work pattern."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai_worthy_api_roo_1.repositories.unit_of_work import SQLAlchemyUnitOfWork


@pytest.fixture
def mock_session_factory():
    """Create a mock session factory."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    
    def factory():
        return session
    
    return factory, session


@pytest.mark.asyncio
async def test_unit_of_work_enter(mock_session_factory):
    """Test entering the Unit of Work context manager."""
    # Arrange
    factory, session = mock_session_factory
    
    # Mock the repository classes
    mock_user_repo = AsyncMock()
    mock_transaction_repo = AsyncMock()
    mock_tag_repo = AsyncMock()
    
    # Patch the imports inside the __aenter__ method
    with patch("ai_worthy_api_roo_1.repositories.user_repository.SQLAlchemyUserRepository", return_value=mock_user_repo), \
         patch("ai_worthy_api_roo_1.repositories.transaction_repository.SQLAlchemyTransactionRepository", return_value=mock_transaction_repo), \
         patch("ai_worthy_api_roo_1.repositories.tag_repository.SQLAlchemyTagRepository", return_value=mock_tag_repo):
        
        # Create the Unit of Work
        uow = SQLAlchemyUnitOfWork(factory)
        
        # Act
        result = await uow.__aenter__()
        
        # Assert
        assert result == uow
        assert uow.session == session


@pytest.mark.asyncio
async def test_unit_of_work_exit_success(mock_session_factory):
    """Test exiting the Unit of Work context manager successfully."""
    # Arrange
    factory, session = mock_session_factory
    
    # Mock the repository classes
    mock_user_repo = AsyncMock()
    mock_transaction_repo = AsyncMock()
    mock_tag_repo = AsyncMock()
    
    # Patch the imports inside the __aenter__ method
    with patch("ai_worthy_api_roo_1.repositories.user_repository.SQLAlchemyUserRepository", return_value=mock_user_repo), \
         patch("ai_worthy_api_roo_1.repositories.transaction_repository.SQLAlchemyTransactionRepository", return_value=mock_transaction_repo), \
         patch("ai_worthy_api_roo_1.repositories.tag_repository.SQLAlchemyTagRepository", return_value=mock_tag_repo):
        
        # Create the Unit of Work
        uow = SQLAlchemyUnitOfWork(factory)
        await uow.__aenter__()
        
        # Act
        await uow.__aexit__(None, None, None)
        
        # Assert
        session.commit.assert_called_once()
        session.rollback.assert_not_called()
        session.close.assert_called_once()


@pytest.mark.asyncio
async def test_unit_of_work_exit_exception(mock_session_factory):
    """Test exiting the Unit of Work context manager with an exception."""
    # Arrange
    factory, session = mock_session_factory
    
    # Mock the repository classes
    mock_user_repo = AsyncMock()
    mock_transaction_repo = AsyncMock()
    mock_tag_repo = AsyncMock()
    
    # Patch the imports inside the __aenter__ method
    with patch("ai_worthy_api_roo_1.repositories.user_repository.SQLAlchemyUserRepository", return_value=mock_user_repo), \
         patch("ai_worthy_api_roo_1.repositories.transaction_repository.SQLAlchemyTransactionRepository", return_value=mock_transaction_repo), \
         patch("ai_worthy_api_roo_1.repositories.tag_repository.SQLAlchemyTagRepository", return_value=mock_tag_repo):
        
        # Create the Unit of Work
        uow = SQLAlchemyUnitOfWork(factory)
        await uow.__aenter__()
        
        # Act
        await uow.__aexit__(Exception, Exception("Test exception"), None)
        
        # Assert
        session.commit.assert_not_called()
        session.rollback.assert_called_once()
        session.close.assert_called_once()


@pytest.mark.asyncio
async def test_unit_of_work_commit(mock_session_factory):
    """Test committing the Unit of Work."""
    # Arrange
    factory, session = mock_session_factory
    
    # Create the Unit of Work
    uow = SQLAlchemyUnitOfWork(factory)
    uow.session = session
    
    # Act
    await uow.commit()
    
    # Assert
    session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_unit_of_work_rollback(mock_session_factory):
    """Test rolling back the Unit of Work."""
    # Arrange
    factory, session = mock_session_factory
    
    # Create the Unit of Work
    uow = SQLAlchemyUnitOfWork(factory)
    uow.session = session
    
    # Act
    await uow.rollback()
    
    # Assert
    session.rollback.assert_called_once()