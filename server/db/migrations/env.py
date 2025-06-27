"""Minimal Alembic environment for upgrade only."""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from sqlalchemy.ext.declarative import declarative_base

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Create a minimal base for migration purposes
Base = declarative_base()
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Get database URL from config or environment
    db_url = config.get_main_option("sqlalchemy.url")
    if not db_url:
        db_url = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///../../data/nfc_data.db")
    
    # Create engine
    engine = create_engine(db_url)
    
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
