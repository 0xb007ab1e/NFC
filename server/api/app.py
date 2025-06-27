"""
FastAPI application for the NFC Reader/Writer System PC Server.

This module defines the API endpoints and initializes the FastAPI application.
"""

import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from pydantic import ValidationError
from contextlib import asynccontextmanager

from server import __version__
from server.api.exceptions import HTTPExceptionFactory, ValidationExceptionHandler

# Set up logger
logger = logging.getLogger("nfc-server.api")

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("API server starting up")
    # Initialize database
    from server.db.config import init_db
    init_db()
    
    yield
    
    # Shutdown event
    logger.info("API server shutting down")
    # Clean up resources
    # This will be implemented as part of Phase 1 development

# Create FastAPI app with lifespan context manager
app = FastAPI(
    title="NFC Reader/Writer System API",
    description="API for the NFC Reader/Writer System PC Server",
    version=__version__,
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom documentation routes
@app.get("/api/docs", include_in_schema=False)
async def get_documentation():
    """Serve Swagger UI documentation."""
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title="NFC Reader/Writer System API",
    )

@app.get("/api/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    """Serve OpenAPI schema."""
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

# Health check endpoints
@app.get("/health", include_in_schema=False)
async def simple_health_check():
    """Simple health check endpoint for Docker/monitoring."""
    return {"status": "healthy"}

@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# Import and include routers
from server.api.routes import nfc_data, device, connection, user
# These will be implemented as part of Phase 1 development
# from server.api.routes import usb, wifi, auth

# Mount routers with versioned prefixes and proper tags
app.include_router(nfc_data.router, prefix="/api/v1/nfc", tags=["NFC Data"])
app.include_router(device.router, prefix="/api/v1/devices", tags=["Devices"])
app.include_router(connection.router, prefix="/api/v1/connections", tags=["Connections"])
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(usb.router, prefix="/api/v1/usb", tags=["USB"])
# app.include_router(wifi.router, prefix="/api/v1/wifi", tags=["WiFi"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with standardized format."""
    # If detail is already a dict (from our factory), use it directly
    if isinstance(exc.detail, dict):
        content = exc.detail
    else:
        # Legacy format - convert to standardized format
        content = {
            "detail": str(exc.detail),
            "code": "HTTP_EXCEPTION",
            "status_code": exc.status_code
        }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=getattr(exc, 'headers', None)
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    http_exc = ValidationExceptionHandler.handle_validation_error(exc)
    return await http_exception_handler(request, http_exc)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.exception("Unhandled exception occurred")
    http_exc = HTTPExceptionFactory.internal_server_error(
        detail="An unexpected error occurred",
        log_exception=False  # Already logged above
    )
    return await http_exception_handler(request, http_exc)
