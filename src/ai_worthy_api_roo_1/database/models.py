"""SQLAlchemy models definition."""

import time
from typing import List, Optional

from sqlalchemy import (
    Boolean, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    image: Mapped[str] = mapped_column(String, nullable=False)
    balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    primary_currency: Mapped[str] = mapped_column(
        String, default="BYN", nullable=False
    )
    
    # Relationships
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="owner", cascade="all, delete-orphan"
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", back_populates="user", cascade="all, delete-orphan"
    )


class Transaction(Base):
    """Transaction model."""
    
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    is_income: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[int] = mapped_column(
        Integer, 
        default=lambda: int(time.time() * 1000),  # Current time in milliseconds
        nullable=False
    )
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="transactions")
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", back_populates="transaction", cascade="all, delete-orphan"
    )


class Tag(Base):
    """Tag model."""
    
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    transaction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tags")
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="tags")