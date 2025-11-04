"""Hunter: The Reckoning character routes (placeholder for future implementation)"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import require_auth

router = APIRouter(prefix="/htr", tags=["htr"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def htr_character_list(request: Request, db: Session = Depends(get_db)):
    """HTR character list - placeholder"""
    user = require_auth(request)
    
    return templates.TemplateResponse(
        "htr/coming_soon.html",
        {
            "request": request,
            "user": user,
            "message": "Hunter: The Reckoning character sheets coming soon!"
        }
    )
