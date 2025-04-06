"""Transaction repository implementation."""

from typing import List, Optional, Protocol

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ai_worthy_api_roo_1.database.models import Transaction, Tag
from ai_worthy_api_roo_1.schemas.transaction import TransactionCreate, TransactionFilter


class TransactionRepositoryProtocol(Protocol):
    """Protocol defining the Transaction repository interface."""
    
    async def get_by_id(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        """
        Get a transaction by ID for a specific user.
        
        Args:
            transaction_id: The transaction ID.
            user_id: The user ID.
            
        Returns:
            The transaction if found, None otherwise.
        """
        ...
    
    async def get_multi(
        self, 
        user_id: int, 
        filters: Optional[TransactionFilter] = None
    ) -> List[Transaction]:
        """
        Get multiple transactions for a user with optional filters.
        
        Args:
            user_id: The user ID.
            filters: Optional filters.
            
        Returns:
            List of transactions.
        """
        ...
    
    async def get_recent(self, user_id: int, limit: int = 3) -> List[Transaction]:
        """
        Get recent transactions for a user.
        
        Args:
            user_id: The user ID.
            limit: Maximum number of transactions to return.
            
        Returns:
            List of recent transactions.
        """
        ...
    
    async def create(self, transaction_data: TransactionCreate, user_id: int) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            transaction_data: The transaction data.
            user_id: The user ID.
            
        Returns:
            The created transaction.
        """
        ...
    
    async def delete(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        """
        Delete a transaction.
        
        Args:
            transaction_id: The transaction ID.
            user_id: The user ID.
            
        Returns:
            The deleted transaction if found, None otherwise.
        """
        ...


class SQLAlchemyTransactionRepository:
    """SQLAlchemy implementation of the Transaction repository."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository.
        
        Args:
            session: The database session.
        """
        self.session = session
    
    async def get_by_id(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        """
        Get a transaction by ID for a specific user.
        
        Args:
            transaction_id: The transaction ID.
            user_id: The user ID.
            
        Returns:
            The transaction if found, None otherwise.
        """
        result = await self.session.execute(
            select(Transaction)
            .options(joinedload(Transaction.tags))
            .where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.owner_id == user_id
                )
            )
        )
        return result.scalars().first()
    
    async def get_multi(
        self, 
        user_id: int, 
        filters: Optional[TransactionFilter] = None
    ) -> List[Transaction]:
        """
        Get multiple transactions for a user with optional filters.
        
        Args:
            user_id: The user ID.
            filters: Optional filters.
            
        Returns:
            List of transactions.
        """
        # Default filter values
        if filters is None:
            filters = TransactionFilter()
        
        # Base query conditions
        conditions = [Transaction.owner_id == user_id]
        
        # Add description filter if provided
        if filters.description:
            conditions.append(
                Transaction.description.like(f"%{filters.description}%")
            )
        
        # Add date filters if provided
        if filters.start_date:
            conditions.append(Transaction.created_at >= filters.start_date)
        
        if filters.end_date and filters.end_date != -1:
            conditions.append(Transaction.created_at <= filters.end_date)
        
        # Base query
        query = (
            select(Transaction)
            .where(and_(*conditions))
            .order_by(desc(Transaction.created_at))
            .offset((filters.page - 1) * filters.per_page)
            .limit(filters.per_page)
        )
        
        # Execute query
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        
        # If tags filter is provided, we need to filter in Python
        # since SQLAlchemy doesn't have a good way to filter by all tags
        if filters.tags:
            filtered_transactions = []
            for transaction in transactions:
                # Get tags for this transaction
                tag_result = await self.session.execute(
                    select(Tag.text)
                    .where(Tag.transaction_id == transaction.id)
                )
                transaction_tags = tag_result.scalars().all()
                
                # Skip transactions that don't have all the required tags
                if all(tag in transaction_tags for tag in filters.tags):
                    filtered_transactions.append(transaction)
            
            return filtered_transactions
        
        return transactions
    
    async def get_recent(self, user_id: int, limit: int = 3) -> List[Transaction]:
        """
        Get recent transactions for a user.
        
        Args:
            user_id: The user ID.
            limit: Maximum number of transactions to return.
            
        Returns:
            List of recent transactions.
        """
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.owner_id == user_id)
            .order_by(desc(Transaction.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, transaction_data: TransactionCreate, user_id: int) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            transaction_data: The transaction data.
            user_id: The user ID.
            
        Returns:
            The created transaction.
        """
        # Convert amount to cents (integer) for storage
        formatted_amount = int(transaction_data.amount * 100)
        
        # Create new transaction
        new_transaction = Transaction(
            description=transaction_data.description,
            currency=transaction_data.currency,
            amount=formatted_amount,
            is_income=transaction_data.is_income,
            owner_id=user_id
        )
        
        self.session.add(new_transaction)
        await self.session.flush()  # Flush to get the transaction ID
        
        return new_transaction
    
    async def delete(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        """
        Delete a transaction.
        
        Args:
            transaction_id: The transaction ID.
            user_id: The user ID.
            
        Returns:
            The deleted transaction if found, None otherwise.
        """
        # Get transaction to verify ownership
        transaction = await self.get_by_id(transaction_id, user_id)
        
        if not transaction:
            return None
        
        # Delete transaction
        await self.session.delete(transaction)
        
        return transaction


def get_transaction_repository(session: AsyncSession) -> TransactionRepositoryProtocol:
    """
    Factory function to create a new Transaction repository.
    
    Args:
        session: The database session.
        
    Returns:
        A new Transaction repository instance.
    """
    return SQLAlchemyTransactionRepository(session)