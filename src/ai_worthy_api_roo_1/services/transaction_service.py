"""Transaction service implementation."""

from typing import List, Optional

from fastapi import HTTPException, status

from ai_worthy_api_roo_1.database.models import Transaction
from ai_worthy_api_roo_1.repositories.unit_of_work import UnitOfWorkProtocol
from ai_worthy_api_roo_1.schemas.transaction import TransactionCreate, TransactionFilter, TransactionOut


class TransactionService:
    """Service for transaction-related operations."""
    
    def __init__(self, unit_of_work: UnitOfWorkProtocol):
        """
        Initialize the service.
        
        Args:
            unit_of_work: The unit of work.
        """
        self.unit_of_work = unit_of_work
    
    async def get_transaction(self, transaction_id: int, user_id: int) -> Optional[TransactionOut]:
        """
        Get a transaction by ID.
        
        Args:
            transaction_id: The transaction ID.
            user_id: The user ID.
            
        Returns:
            The transaction if found, None otherwise.
        """
        async with self.unit_of_work as uow:
            transaction = await uow.transaction_repository.get_by_id(transaction_id, user_id)
            
            if not transaction:
                return None
            
            # Get tags for this transaction
            tags = await uow.tag_repository.get_by_transaction(transaction.id)
            
            # Convert to output schema
            return TransactionOut(
                id=transaction.id,
                description=transaction.description,
                currency=transaction.currency,
                amount=transaction.amount / 100,  # Convert from cents to dollars
                is_income=transaction.is_income,
                created_at=transaction.created_at,
                tags=[tag.text for tag in tags]
            )
    
    async def get_transactions(
        self, 
        user_id: int, 
        filters: Optional[TransactionFilter] = None
    ) -> List[TransactionOut]:
        """
        Get transactions for a user with optional filters.
        
        Args:
            user_id: The user ID.
            filters: Optional filters.
            
        Returns:
            List of transactions.
        """
        async with self.unit_of_work as uow:
            transactions = await uow.transaction_repository.get_multi(user_id, filters)
            
            # Convert to output schema
            transaction_list = []
            for transaction in transactions:
                # Get tags for this transaction
                tags = await uow.tag_repository.get_by_transaction(transaction.id)
                
                transaction_list.append(
                    TransactionOut(
                        id=transaction.id,
                        description=transaction.description,
                        currency=transaction.currency,
                        amount=transaction.amount / 100,  # Convert from cents to dollars
                        is_income=transaction.is_income,
                        created_at=transaction.created_at,
                        tags=[tag.text for tag in tags]
                    )
                )
            
            return transaction_list
    
    async def get_recent_transactions(self, user_id: int, limit: int = 3) -> List[TransactionOut]:
        """
        Get recent transactions for a user.
        
        Args:
            user_id: The user ID.
            limit: Maximum number of transactions to return.
            
        Returns:
            List of recent transactions.
        """
        async with self.unit_of_work as uow:
            transactions = await uow.transaction_repository.get_recent(user_id, limit)
            
            # Convert to output schema
            transaction_list = []
            for transaction in transactions:
                # Get tags for this transaction
                tags = await uow.tag_repository.get_by_transaction(transaction.id)
                
                transaction_list.append(
                    TransactionOut(
                        id=transaction.id,
                        description=transaction.description,
                        currency=transaction.currency,
                        amount=transaction.amount / 100,  # Convert from cents to dollars
                        is_income=transaction.is_income,
                        created_at=transaction.created_at,
                        tags=[tag.text for tag in tags]
                    )
                )
            
            return transaction_list
    
    async def create_transaction(self, transaction_data: TransactionCreate, user_id: int) -> bool:
        """
        Create a new transaction.
        
        Args:
            transaction_data: The transaction data.
            user_id: The user ID.
            
        Returns:
            True if the transaction was created successfully.
        """
        async with self.unit_of_work as uow:
            # Get user to check if exists and get current balance
            user = await uow.user_repository.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            
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
    
    async def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        """
        Delete a transaction.
        
        Args:
            transaction_id: The transaction ID.
            user_id: The user ID.
            
        Returns:
            True if the transaction was deleted successfully, False otherwise.
        """
        async with self.unit_of_work as uow:
            # Get transaction to verify ownership and get amount details
            transaction = await uow.transaction_repository.get_by_id(transaction_id, user_id)
            
            if not transaction:
                return False
            
            # Get user to update balance
            user = await uow.user_repository.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            
            # Update user balance based on transaction type
            formatted_amount = transaction.amount
            if transaction.is_income:
                # If income is deleted, decrease balance
                new_balance = user.balance - formatted_amount
            else:
                # If expense is deleted, increase balance
                new_balance = user.balance + formatted_amount
            
            await uow.user_repository.update_balance(user_id, new_balance)
            
            # Delete transaction
            await uow.transaction_repository.delete(transaction_id, user_id)
            
            return True


def get_transaction_service(unit_of_work: UnitOfWorkProtocol) -> TransactionService:
    """
    Factory function to create a new Transaction service.
    
    Args:
        unit_of_work: The unit of work.
        
    Returns:
        A new Transaction service instance.
    """
    return TransactionService(unit_of_work)