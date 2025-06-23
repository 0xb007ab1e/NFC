"""
Main entry point for the NFC Reader/Writer System PC Server.

This module initializes and starts the server application.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

import typer
import uvicorn
from rich.console import Console
from rich.logging import RichHandler
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("nfc-server")

# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Create typer app
app = typer.Typer()
console = Console()

@app.command()
def run(
    host: str = os.getenv("NFC_SERVER_HOST", "127.0.0.1"),
    port: int = int(os.getenv("NFC_SERVER_PORT", "8000")),
    log_level: str = os.getenv("NFC_SERVER_LOG_LEVEL", "info"),
    reload: bool = False,
):
    """Run the NFC Reader/Writer server."""
    # Configure logging
    log_level = log_level.upper()
    logging.getLogger("nfc-server").setLevel(log_level)
    
    console.print(f"[bold green]Starting NFC Reader/Writer Server[/bold green]")
    console.print(f"Host: [cyan]{host}[/cyan]")
    console.print(f"Port: [cyan]{port}[/cyan]")
    console.print(f"Log level: [cyan]{log_level}[/cyan]")
    
    # Start the server
    uvicorn.run(
        "server.api.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level.lower(),
    )

@app.command()
def version():
    """Show the server version."""
    from server import __version__
    console.print(f"[bold]NFC Reader/Writer Server[/bold] version: [cyan]{__version__}[/cyan]")

def main():
    """Main entry point for the application."""
    try:
        app()
    except Exception as e:
        logger.exception("An unexpected error occurred")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
