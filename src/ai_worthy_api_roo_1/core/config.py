"""Configuration settings for the application."""

import os
from typing import Any, Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Financial Tracking API"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = Field(
        default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./financial_tracker.db"
    )

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # Extra settings
    SALT_ROUNDS: int = 12  # For bcrypt

    # Static directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


settings = Settings()