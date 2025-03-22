"""Transaction-related API endpoints."""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ai_worthy_api_roo_1.database.database import get_db
from ai_worthy_api_roo_1.database.models import Tag, Transaction, User
from ai_worthy_api_roo_1.middleware.auth import get_current_user
from ai_worthy_api_roo_1.schemas.transaction import TransactionCreate, TransactionOut

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/recent", response_model=List[TransactionOut])
async def get_recent_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get the three most recent transactions.
    
    Args:
        current_user: The authenticated user.
        db: Database session.
        
    Returns:
        List of recent transactions.
    """
    result = await db.execute(
        select(Transaction)
        .where(Transaction.owner_id == current_user.id)
        .order_by(desc(Transaction.created_at))
        .limit(3)
    )
    transactions = result.scalars().all()
    
    transaction_list = []
    for transaction in transactions:
        # Get tags for this transaction
        tag_result = await db.execute(
            select(Tag.text)
            .where(Tag.transaction_id == transaction.id)
        )
        tags = tag_result.scalars().all()
        
        transaction_list.append({
            "id": transaction.id,
            "description": transaction.description,
            "currency": transaction.currency,
            "amount": transaction.amount / 100,
            "is_income": transaction.is_income,
            "created_at": transaction.created_at,
            "tags": tags
        })
    
    return transaction_list


@router.get("/", response_model=List[TransactionOut])
async def get_transactions(
    page: int = 1,
    per_page: int = 10,
    description: Optional[str] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    tags: List[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
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
        db: Database session.
        
    Returns:
        List of transactions.
    """
    # Base query conditions
    conditions = [Transaction.owner_id == current_user.id]
    
    # Add description filter if provided
    if description:
        conditions.append(
            Transaction.description.like(f"%{description}%")
        )
    
    # Add date filters if provided
    if start_date:
        conditions.append(Transaction.created_at >= start_date)
    
    if end_date and end_date != -1:
        conditions.append(Transaction.created_at <= end_date)
    
    # Base query
    query = (
        select(Transaction)
        .where(and_(*conditions))
        .order_by(desc(Transaction.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    
    # Execute query
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    # Process transactions
    transaction_list = []
    for transaction in transactions:
        # Get tags for this transaction
        tag_result = await db.execute(
            select(Tag.text)
            .where(Tag.transaction_id == transaction.id)
        )
        transaction_tags = tag_result.scalars().all()
        
        # If tags filter is provided, skip transactions that don't have all the required tags
        if tags and not all(tag in transaction_tags for tag in tags):
            continue
            
        transaction_list.append({
            "id": transaction.id,
            "description": transaction.description,
            "currency": transaction.currency,
            "amount": transaction.amount / 100,
            "is_income": transaction.is_income,
            "created_at": transaction.created_at,
            "tags": transaction_tags
        })
    
    return transaction_list


@router.post("/", response_model=bool)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new transaction.
    
    Args:
        transaction_data: Transaction information.
        current_user: The authenticated user.
        db: Database session.
        
    Returns:
        True if transaction was created successfully.
    """
    # Convert amount to cents (integer) for storage
    formatted_amount = int(transaction_data.amount * 100)
    
    # Create new transaction
    new_transaction = Transaction(
        description=transaction_data.description,
        currency=transaction_data.currency,
        amount=formatted_amount,
        is_income=transaction_data.is_income,
        owner_id=current_user.id
    )
    
    db.add(new_transaction)
    await db.flush()  # Flush to get the transaction ID
    
    # Add tags if provided
    if transaction_data.tags:
        for tag_text in transaction_data.tags:
            new_tag = Tag(
                text=tag_text,
                user_id=current_user.id,
                transaction_id=new_transaction.id
            )
            db.add(new_tag)
    
    # Update user balance
    if transaction_data.is_income:
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(balance=User.balance + formatted_amount)
        )
    else:
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(balance=User.balance - formatted_amount)
        )
    
    await db.commit()
    
    return True


@router.get("/{transaction_id}", response_model=Optional[TransactionOut])
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a single transaction by ID.
    
    Args:
        transaction_id: The ID of the transaction.
        current_user: The authenticated user.
        db: Database session.
        
    Returns:
        Transaction information or None if not found.
    """
    result = await db.execute(
        select(Transaction)
        .options(joinedload(Transaction.tags))
        .where(
            and_(
                Transaction.id == transaction_id,
                Transaction.owner_id == current_user.id
            )
        )
    )
    transaction = result.scalars().first()
    
    if not transaction:
        return None
    
    # Convert amount from cents to dollars
    transaction_dict = {
        "id": transaction.id,
        "description": transaction.description,
        "currency": transaction.currency,
        "amount": transaction.amount / 100,
        "is_income": transaction.is_income,
        "created_at": transaction.created_at,
        "tags": [tag.text for tag in transaction.tags]
    }
    
    return transaction_dict


@router.delete("/{transaction_id}", response_model=bool)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete a transaction by ID.
    
    Args:
        transaction_id: The ID of the transaction.
        current_user: The authenticated user.
        db: Database session.
        
    Returns:
        True if transaction was deleted, False otherwise.
    """
    # Get transaction to verify ownership and get amount details
    result = await db.execute(
        select(Transaction)
        .where(
            and_(
                Transaction.id == transaction_id,
                Transaction.owner_id == current_user.id
            )
        )
    )
    transaction = result.scalars().first()
    
    if not transaction:
        return False
    
    # Update user balance based on transaction type
    formatted_amount = transaction.amount
    if transaction.is_income:
        # If income is deleted, decrease balance
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(balance=User.balance - formatted_amount)
        )
    else:
        # If expense is deleted, increase balance
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(balance=User.balance + formatted_amount)
        )
    
    # Delete transaction
    await db.delete(transaction)
    await db.commit()
    
    return True
async def get_recent_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get the three most recent transactions.
    
    Args:
        current_user: The authenticated user.
        db: Database session.
        
    Returns:
        List of recent transactions.
    """
    result = await db.execute(
        select(Transaction)
        .where(Transaction.owner_id == current_user.id)
        .order_by(desc(Transaction.created_at))
        .limit(3)
    )
    transactions = result.scalars().all()
    
    transaction_list = []
    for transaction in transactions:
        # Get tags for this transaction
        tag_result = await db.execute(
            select(Tag.text)
            .where(Tag.transaction_id == transaction.id)
        )
        tags = tag_result.scalars().all()
        
        transaction_list.append({
            "id": transaction.id,
            "description": transaction.description,
            "currency": transaction.currency,
            "amount": transaction.amount / 100,
            "is_income": transaction.is_income,
            "created_at": transaction.created_at,
            "tags": tags
        })
    
    return transaction_list


@router.get("/", response_model=List[TransactionOut])
async def get_transactions(
    page: int = 1,
    per_page: int = 10,
    description: Optional[str] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    tags: List[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
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
        db: Database session.
        
    Returns:
        List of transactions.
    """
    # Base query conditions
    conditions = [Transaction.owner_id == current_user.id]
    
    # Add description filter if provided
    if description:
        conditions.append(
            like(Transaction.description, f"%{description}%")
        )
    
    # Add date filters if provided
    if start_date:
        conditions.append(Transaction.created_at >= start_date)
    
    if end_date and end_date != -1:
        conditions.append(Transaction.created_at <= end_date)
    
    # Base query
    query = (
        select(Transaction)
        .where(and_(*conditions))
        .order_by(desc(Transaction.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    
    # Execute query
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    # Process transactions
    transaction_list = []
    for transaction in transactions:
        # Get tags for this transaction
        tag_result = await db.execute(
            select(Tag.text)
            .where(Tag.transaction_id == transaction.id)
        )
        transaction_tags = tag_result.scalars().all()
        
        # If tags filter is provided, skip transactions that don't have all the required tags
        if tags and not all(tag in transaction_tags for tag in tags):
            continue
            
        transaction_list.append({
            "id": transaction.id,
            "description": transaction.description,
            "currency": transaction.currency,
            "amount": transaction.amount / 100,
            "is_income": transaction.is_income,
            "created_at": transaction.created_at,
            "tags": transaction_tags
        })
    
    return transaction_list


@router.post("/", response_model=bool)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new transaction.
    
    Args:
        transaction_data: Transaction information.
        current_user: The authenticated user.
        db: Database session.
        
    Returns:
        True if transaction was created successfully.
    """
    # Convert amount to cents (integer) for storage
    formatted_amount = int(transaction_data.amount * 100)
    
    # Create new transaction
    new_transaction = Transaction(
        description=transaction_data.description,
        currency=transaction_data.currency,
        amount=formatted_amount,
        is_income=transaction_data.is_income,
        owner_id=current_user.id
    )
    
    db.add(new_transaction)
    await db.flush()  # Flush to get the transaction ID
    
    # Add tags if provided
    if transaction_data.tags:
        for tag_text in transaction_data.tags:
            new_tag = Tag(
                text=tag_text,
                user_id=current_user.id,
                transaction_id=new_transaction.id
            )
            db.add(new_tag)
    
    # Update user balance
    if transaction_data.is_income:
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(balance=User.balance + formatted_amount)
        )
    else:
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(balance=User.balance - formatted_amount)
        )
    
    await db.commit()
    
    return True