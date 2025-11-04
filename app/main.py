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
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

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
    print("Database initialized")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - landing or dashboard based on auth status"""
    user = get_current_user(request)
    
    if user:
        # Logged in - show dashboard
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user
            }
        )
    else:
        # Not logged in - show landing page
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
