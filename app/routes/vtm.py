"""Vampire: The Masquerade character routes"""

import os
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from PIL import Image
import uuid

from app.database import get_db
from app.models import VTMCharacter
from app.auth import require_auth

router = APIRouter(prefix="/vtm", tags=["vtm"])
templates = Jinja2Templates(directory="templates")

# Volume path for image storage
VOLUME_PATH = os.getenv("VOLUME_PATH", "/data")
CHARACTER_IMAGE_DIR = os.path.join(VOLUME_PATH, "character_portraits")

# Ensure directory exists
os.makedirs(CHARACTER_IMAGE_DIR, exist_ok=True)

# Character limit per user
CHARACTER_LIMIT = 3


@router.get("/", response_class=HTMLResponse)
async def vtm_character_list(request: Request, db: Session = Depends(get_db)):
    """Display user's VTM characters (up to 3 slots)"""
    user = require_auth(request)
    
    # Get user's characters
    characters = db.query(VTMCharacter).filter(
        VTMCharacter.user_id == user['id']
    ).order_by(VTMCharacter.created_at).all()
    
    # Calculate available slots
    available_slots = CHARACTER_LIMIT - len(characters)
    can_create = available_slots > 0
    
    return templates.TemplateResponse(
        "vtm/character_list.html",
        {
            "request": request,
            "user": user,
            "characters": characters,
            "available_slots": available_slots,
            "can_create": can_create,
            "character_limit": CHARACTER_LIMIT
        }
    )


@router.get("/character/new", response_class=HTMLResponse)
async def new_character_form(request: Request, db: Session = Depends(get_db)):
    """Display form to create new VTM character"""
    user = require_auth(request)
    
    # Check character limit
    character_count = db.query(VTMCharacter).filter(
        VTMCharacter.user_id == user['id']
    ).count()
    
    if character_count >= CHARACTER_LIMIT:
        return RedirectResponse(
            url="/vtm?error=limit_reached",
            status_code=303
        )
    
    return templates.TemplateResponse(
        "vtm/character_sheet.html",
        {
            "request": request,
            "user": user,
            "character": None,  # New character
            "edit_mode": True
        }
    )


@router.get("/character/{character_id}", response_class=HTMLResponse)
async def view_character(
    request: Request,
    character_id: int,
    db: Session = Depends(get_db)
):
    """View VTM character sheet"""
    user = require_auth(request)
    
    # Get character and verify ownership
    character = db.query(VTMCharacter).filter(
        VTMCharacter.id == character_id,
        VTMCharacter.user_id == user['id']
    ).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return templates.TemplateResponse(
        "vtm/character_sheet.html",
        {
            "request": request,
            "user": user,
            "character": character,
            "edit_mode": False
        }
    )


@router.get("/character/{character_id}/edit", response_class=HTMLResponse)
async def edit_character_form(
    request: Request,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Display form to edit VTM character"""
    user = require_auth(request)
    
    # Get character and verify ownership
    character = db.query(VTMCharacter).filter(
        VTMCharacter.id == character_id,
        VTMCharacter.user_id == user['id']
    ).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return templates.TemplateResponse(
        "vtm/character_sheet.html",
        {
            "request": request,
            "user": user,
            "character": character,
            "edit_mode": True
        }
    )


@router.post("/character/create")
async def create_character(
    request: Request,
    db: Session = Depends(get_db)
):
    """Create new VTM character"""
    user = require_auth(request)
    
    # Check character limit
    character_count = db.query(VTMCharacter).filter(
        VTMCharacter.user_id == user['id']
    ).count()
    
    if character_count >= CHARACTER_LIMIT:
        return JSONResponse(
            status_code=400,
            content={"error": "Character limit reached. Delete a character to create a new one."}
        )
    
    # Get form data
    form_data = await request.form()
    
    # Create new character with form data
    character = VTMCharacter(
        user_id=user['id'],
        name=form_data.get('name', 'Unnamed'),
        # Add all other fields from form_data
        # This will be expanded when we build the actual form
    )
    
    db.add(character)
    db.commit()
    db.refresh(character)
    
    return RedirectResponse(
        url=f"/vtm/character/{character.id}",
        status_code=303
    )


@router.post("/character/{character_id}/update")
async def update_character(
    request: Request,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Update existing VTM character"""
    user = require_auth(request)
    
    # Get character and verify ownership
    character = db.query(VTMCharacter).filter(
        VTMCharacter.id == character_id,
        VTMCharacter.user_id == user['id']
    ).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get form data and update character
    form_data = await request.form()
    
    # Update all fields from form_data
    # This will be expanded when we build the actual form
    for key, value in form_data.items():
        if hasattr(character, key):
            setattr(character, key, value)
    
    db.commit()
    
    return RedirectResponse(
        url=f"/vtm/character/{character.id}",
        status_code=303
    )


@router.post("/character/{character_id}/delete")
async def delete_character(
    request: Request,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Delete VTM character"""
    user = require_auth(request)
    
    # Get character and verify ownership
    character = db.query(VTMCharacter).filter(
        VTMCharacter.id == character_id,
        VTMCharacter.user_id == user['id']
    ).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Delete character portrait if exists
    if character.portrait_url:
        try:
            portrait_path = os.path.join(VOLUME_PATH, character.portrait_url.lstrip('/'))
            if os.path.exists(portrait_path):
                os.remove(portrait_path)
        except Exception as e:
            print(f"Error deleting portrait: {e}")
    
    # Delete character
    db.delete(character)
    db.commit()
    
    return RedirectResponse(url="/vtm", status_code=303)


@router.post("/character/{character_id}/upload-portrait")
async def upload_portrait(
    character_id: int,
    request: Request,
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload character portrait (file or URL)"""
    user = require_auth(request)
    
    # Get character and verify ownership
    character = db.query(VTMCharacter).filter(
        VTMCharacter.id == character_id,
        VTMCharacter.user_id == user['id']
    ).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    try:
        # Handle file upload
        if file:
            # Validate file type
            if not file.content_type.startswith('image/'):
                return JSONResponse(
                    status_code=400,
                    content={"error": "File must be an image"}
                )
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(CHARACTER_IMAGE_DIR, unique_filename)
            
            # Save and resize image
            image = Image.open(file.file)
            
            # Resize to standard portrait size (400x600 max, maintain aspect ratio)
            image.thumbnail((400, 600), Image.Resampling.LANCZOS)
            image.save(file_path, optimize=True, quality=85)
            
            # Update character portrait URL
            character.portrait_url = f"/static/portraits/{unique_filename}"
            
        # Handle URL (future implementation)
        elif url:
            # TODO: Implement URL fetching and processing
            return JSONResponse(
                status_code=400,
                content={"error": "URL upload not yet implemented"}
            )
        
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "No file or URL provided"}
            )
        
        db.commit()
        
        return JSONResponse(content={"success": True, "portrait_url": character.portrait_url})
        
    except Exception as e:
        print(f"Error uploading portrait: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to upload portrait"}
        )
