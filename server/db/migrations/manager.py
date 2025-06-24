"""
Migration manager for the NFC Reader/Writer System PC Server.

This module provides tools to manage database migrations.
"""

import os
import logging
import importlib
from pathlib import Path
from typing import List, Optional

import typer
from alembic import command
from alembic.config import Config
from rich.console import Console
from rich.table import Table

from server.db.config import get_engine, init_db

# Set up logger
logger = logging.getLogger("nfc-server.db.migrations")

# Create typer app
app = typer.Typer()
console = Console()

def get_alembic_config() -> Config:
    """
    Get Alembic configuration.
    
    Returns:
        Config: Alembic configuration.
    """
    # Get the directory of this file
    base_dir = Path(__file__).parent
    
    # Create Alembic config
    config = Config(str(base_dir / "alembic.ini"))
    config.set_main_option("script_location", str(base_dir))
    config.set_main_option("sqlalchemy.url", os.environ.get("SQLALCHEMY_DATABASE_URL", ""))
    
    return config

@app.command()
def init():
    """Initialize Alembic migrations."""
    console.print("[bold blue]Initializing Alembic migrations...[/bold blue]")
    
    try:
        config = get_alembic_config()
        command.init(config, "migrations")
        console.print("[bold green]Alembic migrations initialized successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error initializing Alembic migrations: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command()
def create(message: str):
    """
    Create a new migration.
    
    Args:
        message: Migration message.
    """
    console.print(f"[bold blue]Creating migration: {message}...[/bold blue]")
    
    try:
        config = get_alembic_config()
        command.revision(config, message=message, autogenerate=True)
        console.print("[bold green]Migration created successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error creating migration: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command()
def upgrade(revision: str = "head"):
    """
    Upgrade the database to a revision.
    
    Args:
        revision: Revision to upgrade to.
    """
    console.print(f"[bold blue]Upgrading database to {revision}...[/bold blue]")
    
    try:
        config = get_alembic_config()
        command.upgrade(config, revision)
        console.print("[bold green]Database upgraded successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error upgrading database: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command()
def downgrade(revision: str):
    """
    Downgrade the database to a revision.
    
    Args:
        revision: Revision to downgrade to.
    """
    console.print(f"[bold blue]Downgrading database to {revision}...[/bold blue]")
    
    try:
        config = get_alembic_config()
        command.downgrade(config, revision)
        console.print("[bold green]Database downgraded successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error downgrading database: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command()
def show(revision: str = "head"):
    """
    Show the revision.
    
    Args:
        revision: Revision to show.
    """
    console.print(f"[bold blue]Showing revision {revision}...[/bold blue]")
    
    try:
        config = get_alembic_config()
        command.show(config, revision)
    except Exception as e:
        console.print(f"[bold red]Error showing revision: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command()
def history():
    """Show the revision history."""
    console.print("[bold blue]Showing revision history...[/bold blue]")
    
    try:
        config = get_alembic_config()
        command.history(config)
    except Exception as e:
        console.print(f"[bold red]Error showing revision history: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command()
def current():
    """Show the current revision."""
    console.print("[bold blue]Showing current revision...[/bold blue]")
    
    try:
        config = get_alembic_config()
        command.current(config)
    except Exception as e:
        console.print(f"[bold red]Error showing current revision: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command()
def run():
    """Run all migrations."""
    console.print("[bold blue]Running all migrations...[/bold blue]")
    
    try:
        # Initialize the database
        init_db()
        
        # Upgrade to the latest revision
        config = get_alembic_config()
        command.upgrade(config, "head")
        
        console.print("[bold green]All migrations applied successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error running migrations: {e}[/bold red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
