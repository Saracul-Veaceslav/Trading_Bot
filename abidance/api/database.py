"""
Database connection utilities for the API.

This module provides database connection utilities for the FastAPI application,
including dependency injection for database sessions.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from abidance.core.configuration import Configuration

# Get database URL from configuration
config = Configuration()
try:
    config.load_from_yaml("config.yaml")
except Exception as e:
    # Fallback to default SQLite database
    pass

DATABASE_URL = config.get("database", {}).get("url", "sqlite:///abidance.db")

# Create SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for database session.
    
    This function creates a new database session for each request and ensures
    it is closed when the request is complete.
    
    Returns:
        Generator[Session, None, None]: A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 