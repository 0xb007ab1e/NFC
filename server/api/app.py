"""
FastAPI application for the NFC Reader/Writer System PC Server.

This module defines the API endpoints and initializes the FastAPI application.
"""

import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from server import __version__

# Set up logger
logger = logging.getLogger("nfc-server.api")

# Create FastAPI app
app = FastAPI(
    title="NFC Reader/Writer System API",
    description="API for the NFC Reader/Writer System PC Server",
    version=__version__,
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json",
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

# Health check endpoint
@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# Import and include routers
from server.api.routes import nfc_data
# These will be implemented as part of Phase 1 development
# from server.api.routes import usb, wifi, auth

app.include_router(nfc_data.router, prefix="/api/nfc", tags=["NFC"])
# app.include_router(usb.router, prefix="/api/usb", tags=["USB"])
# app.include_router(wifi.router, prefix="/api/wifi", tags=["WiFi"])
# app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Execute code when the application starts up."""
    logger.info("API server starting up")
    # Initialize database
    from server.db.config import init_db
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Execute code when the application is shutting down."""
    logger.info("API server shutting down")
    # Clean up resources
    # This will be implemented as part of Phase 1 development

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
