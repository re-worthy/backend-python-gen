"""Tag repository implementation."""

from typing import List, Optional, Protocol

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_worthy_api_roo_1.database.models import Tag


class TagRepositoryProtocol(Protocol):
    """Protocol defining the Tag repository interface."""
    
    async def get_by_transaction(self, transaction_id: int) -> List[Tag]:
        """
        Get all tags for a transaction.
        
        Args:
            transaction_id: The transaction ID.
            
        Returns:
            List of tags.
        """
        ...
    
    async def create(self, tag_text: str, user_id: int, transaction_id: int) -> Tag:
        """
        Create a new tag.
        
        Args:
            tag_text: The tag text.
            user_id: The user ID.
            transaction_id: The transaction ID.
            
        Returns:
            The created tag.
        """
        ...
    
    async def delete_by_transaction(self, transaction_id: int) -> None:
        """
        Delete all tags for a transaction.
        
        Args:
            transaction_id: The transaction ID.
        """
        ...


class SQLAlchemyTagRepository:
    """SQLAlchemy implementation of the Tag repository."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository.
        
        Args:
            session: The database session.
        """
        self.session = session
    
    async def get_by_transaction(self, transaction_id: int) -> List[Tag]:
        """
        Get all tags for a transaction.
        
        Args:
            transaction_id: The transaction ID.
            
        Returns:
            List of tags.
        """
        result = await self.session.execute(
            select(Tag).where(Tag.transaction_id == transaction_id)
        )
        return result.scalars().all()
    
    async def create(self, tag_text: str, user_id: int, transaction_id: int) -> Tag:
        """
        Create a new tag.
        
        Args:
            tag_text: The tag text.
            user_id: The user ID.
            transaction_id: The transaction ID.
            
        Returns:
            The created tag.
        """
        new_tag = Tag(
            text=tag_text,
            user_id=user_id,
            transaction_id=transaction_id
        )
        
        self.session.add(new_tag)
        await self.session.flush()
        
        return new_tag
    
    async def delete_by_transaction(self, transaction_id: int) -> None:
        """
        Delete all tags for a transaction.
        
        Args:
            transaction_id: The transaction ID.
        """
        result = await self.session.execute(
            select(Tag).where(Tag.transaction_id == transaction_id)
        )
        tags = result.scalars().all()
        
        for tag in tags:
            await self.session.delete(tag)


def get_tag_repository(session: AsyncSession) -> TagRepositoryProtocol:
    """
    Factory function to create a new Tag repository.
    
    Args:
        session: The database session.
        
    Returns:
        A new Tag repository instance.
    """
    return SQLAlchemyTagRepository(session)