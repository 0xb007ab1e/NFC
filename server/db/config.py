"""
Database configuration for the NFC Reader/Writer System PC Server.

This module handles database connection setup and configuration.
"""

import os
import logging
from typing import Optional
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Set up logger
logger = logging.getLogger("nfc-server.db")

# Database configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "nfc_data")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
SQLITE_PATH = os.getenv("SQLITE_PATH", "./data/nfc_data.db")

# Create SQLAlchemy Base
Base = declarative_base()

# Configure database connection
if DB_TYPE == "sqlite":
    # Ensure data directory exists
    data_dir = Path(SQLITE_PATH).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create SQLite database URL
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
    
    # Create engine with SQLite-specific configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
else:
    # Create PostgreSQL database URL
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Create engine with PostgreSQL-specific configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """
    Get a database session.
    
    This function should be used as a dependency in FastAPI route functions.
    
    Returns:
        Session: A SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Initialize the database.
    
    This function creates all tables in the database.
    """
    logger.info(f"Initializing database with connection: {SQLALCHEMY_DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete")

def get_engine():
    """
    Get the SQLAlchemy engine.
    
    Returns:
        Engine: The SQLAlchemy engine.
    """
    return engine
