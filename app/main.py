"""Main FastAPI application"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.database import init_db
from app.routes import auth, vtm, htr
from app.auth import get_current_user

# Initialize FastAPI app
app = FastAPI(
    title="World of Darkness Character Sheets",
    description="Character sheet manager for World of Darkness games",
    version="0.1.0"
)

# Add session middleware for OAuth
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
print(f"[STARTUP] Using SECRET_KEY: {SECRET_KEY[:10]}... (length: {len(SECRET_KEY)})")

# Add session middleware with explicit cookie settings
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    session_cookie="wod_session",  # Explicit cookie name
    max_age=14 * 24 * 60 * 60,     # 14 days
    same_site="lax",                # Allow OAuth redirects
    https_only=False                # Set to True in production with HTTPS
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount character portraits from Railway Volume
VOLUME_PATH = os.getenv("VOLUME_PATH", "/data")
PORTRAITS_DIR = os.path.join(VOLUME_PATH, "character_portraits")
os.makedirs(PORTRAITS_DIR, exist_ok=True)
app.mount("/static/portraits", StaticFiles(directory=PORTRAITS_DIR), name="portraits")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth.router)
app.include_router(vtm.router)
app.include_router(htr.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("[STARTUP] Database initialized")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - landing or dashboard based on auth status"""
    # Debug session contents
    print(f"[HOME] Session contents: {dict(request.session)}")
    
    user = get_current_user(request)
    print(f"[HOME] Current user: {user}")
    
    if user:
        # Logged in - show dashboard
        print(f"[HOME] Authenticated user {user.get('username')} - showing dashboard")
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user
            }
        )
    else:
        # Not logged in - show landing page
        print("[HOME] No authenticated user - showing landing page")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "user": None
            }
        )


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy"}


@app.get("/debug-session")
async def debug_session(request: Request):
    """Debug endpoint to check session contents"""
    return {
        "session": dict(request.session),
        "user": get_current_user(request),
        "cookies": dict(request.cookies)
    }


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
