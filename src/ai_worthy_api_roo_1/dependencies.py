"""Dependency injection for FastAPI."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai_worthy_api_roo_1.database.database import get_db
from ai_worthy_api_roo_1.repositories.unit_of_work import SQLAlchemyUnitOfWork, UnitOfWorkProtocol
from ai_worthy_api_roo_1.repositories.user_repository import SQLAlchemyUserRepository, UserRepositoryProtocol
from ai_worthy_api_roo_1.repositories.transaction_repository import SQLAlchemyTransactionRepository, TransactionRepositoryProtocol
from ai_worthy_api_roo_1.repositories.tag_repository import SQLAlchemyTagRepository, TagRepositoryProtocol
from ai_worthy_api_roo_1.services.auth_service import AuthService
from ai_worthy_api_roo_1.services.user_service import UserService
from ai_worthy_api_roo_1.services.transaction_service import TransactionService


# Repository dependencies
def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepositoryProtocol:
    """
    Get a User repository instance.
    
    Args:
        db: The database session.
        
    Returns:
        A User repository instance.
    """
    return SQLAlchemyUserRepository(db)


def get_transaction_repository(db: AsyncSession = Depends(get_db)) -> TransactionRepositoryProtocol:
    """
    Get a Transaction repository instance.
    
    Args:
        db: The database session.
        
    Returns:
        A Transaction repository instance.
    """
    return SQLAlchemyTransactionRepository(db)


def get_tag_repository(db: AsyncSession = Depends(get_db)) -> TagRepositoryProtocol:
    """
    Get a Tag repository instance.
    
    Args:
        db: The database session.
        
    Returns:
        A Tag repository instance.
    """
    return SQLAlchemyTagRepository(db)


# Unit of Work dependency
def get_unit_of_work() -> UnitOfWorkProtocol:
    """
    Get a Unit of Work instance.
    
    Returns:
        A Unit of Work instance.
    """
    return SQLAlchemyUnitOfWork()


# Service dependencies
def get_auth_service(
    unit_of_work: UnitOfWorkProtocol = Depends(get_unit_of_work)
) -> AuthService:
    """
    Get an Auth service instance.
    
    Args:
        unit_of_work: The unit of work.
        
    Returns:
        An Auth service instance.
    """
    return AuthService(unit_of_work)


def get_user_service(
    unit_of_work: UnitOfWorkProtocol = Depends(get_unit_of_work)
) -> UserService:
    """
    Get a User service instance.
    
    Args:
        unit_of_work: The unit of work.
        
    Returns:
        A User service instance.
    """
    return UserService(unit_of_work)


def get_transaction_service(
    unit_of_work: UnitOfWorkProtocol = Depends(get_unit_of_work)
) -> TransactionService:
    """
    Get a Transaction service instance.
    
    Args:
        unit_of_work: The unit of work.
        
    Returns:
        A Transaction service instance.
    """
    return TransactionService(unit_of_work)