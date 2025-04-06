"""Transaction-related API endpoints."""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Query

from ai_worthy_api_roo_1.database.models import User
from ai_worthy_api_roo_1.dependencies import get_transaction_service
from ai_worthy_api_roo_1.middleware.auth import get_current_user
from ai_worthy_api_roo_1.schemas.transaction import TransactionCreate, TransactionFilter, TransactionOut
from ai_worthy_api_roo_1.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/recent", response_model=List[TransactionOut])
async def get_recent_transactions(
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Any:
    """
    Get the three most recent transactions.
    
    Args:
        current_user: The authenticated user.
        transaction_service: Transaction service.
        
    Returns:
        List of recent transactions.
    """
    return await transaction_service.get_recent_transactions(current_user.id)


@router.get("/", response_model=List[TransactionOut])
async def get_transactions(
    page: int = 1,
    per_page: int = 10,
    description: Optional[str] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    tags: List[str] = Query(None),
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Any:
    """
    Get a paginated list of transactions with optional filters.
    
    Args:
        page: The page number (1-indexed).
        per_page: Number of items per page.
        description: Optional filter for transaction description.
        start_date: Optional filter for minimum creation date (unix timestamp ms).
        end_date: Optional filter for maximum creation date (unix timestamp ms).
        tags: Optional list of tags to filter by.
        current_user: The authenticated user.
        transaction_service: Transaction service.
        
    Returns:
        List of transactions.
    """
    filters = TransactionFilter(
        page=page,
        per_page=per_page,
        description=description,
        start_date=start_date,
        end_date=end_date,
        tags=tags
    )
    
    return await transaction_service.get_transactions(current_user.id, filters)


@router.post("/", response_model=bool)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Any:
    """
    Create a new transaction.
    
    Args:
        transaction_data: Transaction information.
        current_user: The authenticated user.
        transaction_service: Transaction service.
        
    Returns:
        True if transaction was created successfully.
    """
    return await transaction_service.create_transaction(transaction_data, current_user.id)


@router.get("/{transaction_id}", response_model=Optional[TransactionOut])
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Any:
    """
    Get a single transaction by ID.
    
    Args:
        transaction_id: The ID of the transaction.
        current_user: The authenticated user.
        transaction_service: Transaction service.
        
    Returns:
        Transaction information or None if not found.
    """
    return await transaction_service.get_transaction(transaction_id, current_user.id)


@router.delete("/{transaction_id}", response_model=bool)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> Any:
    """
    Delete a transaction by ID.
    
    Args:
        transaction_id: The ID of the transaction.
        current_user: The authenticated user.
        transaction_service: Transaction service.
        
    Returns:
        True if transaction was deleted, False otherwise.
    """
    return await transaction_service.delete_transaction(transaction_id, current_user.id)