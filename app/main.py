"""Main FastAPI application"""

import os
import logging
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from app.logging_config import setup_logging, get_logger
from app.database import init_db, get_db
from app.routes import auth, vtm, htr, storyteller
from app.auth import get_current_user
from app.template_config import templates
from app.csrf import init_csrf, get_csrf_token
from app.export_utils import cleanup_browser
from app.exceptions import (
    wod_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    WoDException
)
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

# Initialize logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
setup_logging(LOG_LEVEL)
logger = get_logger(__name__)

# ✅ CRITICAL: Import new models so SQLAlchemy knows about them
# This ensures init_db() creates all tables properly
from app.models_new import (
    User,
    UserPreferences,
    AuditLog,
    VTMCharacter,
    HTRCharacter,
    Touchstone,
    Background,
    XPLogEntry
)

# Initialize FastAPI app
app = FastAPI(
    title="World of Darkness Character Sheets",
    description="Character sheet manager for World of Darkness games",
    version="0.1.0"
)

# Add exception handlers
app.add_exception_handler(WoDException, wod_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)

# Add session middleware for OAuth
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is required. "
        "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )

# Validate SECRET_KEY strength
if len(SECRET_KEY) < 32:
    raise ValueError(
        "SECRET_KEY must be at least 32 characters long for security. "
        "Generate a strong key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )

# Initialize CSRF protection
init_csrf(SECRET_KEY)

# Determine if we're in development mode
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"

# Add session middleware with explicit cookie settings
# Note: https_only is set to False because Railway proxy terminates SSL
# The actual client connection is HTTPS, but the proxy->app connection is HTTP
# With --proxy-headers flag, uvicorn will correctly understand the original protocol
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="wod_session",  # Explicit cookie name
    max_age=14 * 24 * 60 * 60,     # 14 days
    same_site="lax",                # Allow OAuth redirects
    https_only=False                # Set to False due to proxy SSL termination
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount character portraits from Railway Volume
# NOTE: Must be at /portraits (not /static/portraits) to avoid mount path conflicts
VOLUME_PATH = os.getenv("VOLUME_PATH", "/data")
PORTRAITS_DIR = os.path.join(VOLUME_PATH, "character_portraits")
os.makedirs(PORTRAITS_DIR, exist_ok=True)
app.mount("/portraits", StaticFiles(directory=PORTRAITS_DIR), name="portraits")

# Templates are configured in app/template_config.py and imported above

# Include routers
app.include_router(auth.router)
app.include_router(vtm.router)
app.include_router(htr.router)
app.include_router(storyteller.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info("Database initialized")
    logger.info("Models loaded: User, UserPreferences, AuditLog, VTMCharacter, HTRCharacter, Touchstone, Background, XPLogEntry")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    await cleanup_browser()
    logger.info("Browser resources cleaned up")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - landing or dashboard based on auth status"""
    # Debug session contents
    logger.debug(f"Session contents: {dict(request.session)}")

    user = get_current_user(request)
    logger.debug(f"Current user: {user}")

    if user:
        # Logged in - show dashboard
        logger.debug(f"Authenticated user {user.get('username')} - showing dashboard")
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user
            }
        )
    else:
        # Not logged in - showing landing page
        logger.debug("No authenticated user - showing landing page")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "user": None
            }
        )


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity test"""
    try:
        # Test database connectivity with a simple query
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.get("/csrf-token")
async def csrf_token_endpoint(request: Request):
    """Get CSRF token for the current session"""
    token = await get_csrf_token(request)
    return {"csrf_token": token}


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 page"""
    user = get_current_user(request)
    return templates.TemplateResponse(
        "404.html",
        {
            "request": request,
            "user": user
        },
        status_code=404
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Custom 500 page"""
    user = get_current_user(request)
    return templates.TemplateResponse(
        "500.html",
        {
            "request": request,
            "user": user
        },
        status_code=500
    )
