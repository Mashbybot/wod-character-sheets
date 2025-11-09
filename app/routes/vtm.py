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


# API endpoint for getting character data as JSON
@router.get("/api/character/{character_id}")
async def get_character_api(
    request: Request,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Get character data as JSON for Alpine.js"""
    user = require_auth(request)
    
    character = db.query(VTMCharacter).filter(
        VTMCharacter.id == character_id,
        VTMCharacter.user_id == user['id']
    ).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Convert SQLAlchemy object to dict with datetime handling
    char_dict = {}
    for c in character.__table__.columns:
        value = getattr(character, c.name)
        # Convert datetime to ISO string for JSON serialization
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        char_dict[c.name] = value
    
    return JSONResponse(content=char_dict)


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
    
    # Get form data (could be form or JSON)
    try:
        data = await request.json()
    except:
        form_data = await request.form()
        data = dict(form_data)
    
    # Create new character with data
    character = VTMCharacter(
        user_id=user['id'],
        name=data.get('name', 'Unnamed'),
        chronicle=data.get('chronicle', ''),
        concept=data.get('concept', ''),
        clan=data.get('clan', ''),
        # Add other fields as needed
    )
    
    db.add(character)
    db.commit()
    db.refresh(character)
    
    return JSONResponse(content={"id": character.id, "success": True})


@router.post("/character/{character_id}/update")
async def update_character(
    request: Request,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Update existing VTM character - accepts JSON for auto-save"""
    user = require_auth(request)
    
    # Get character and verify ownership
    character = db.query(VTMCharacter).filter(
        VTMCharacter.id == character_id,
        VTMCharacter.user_id == user['id']
    ).first()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get data (JSON from auto-save)
    try:
        data = await request.json()
    except:
        # Fallback to form data for non-AJAX requests
        form_data = await request.form()
        data = dict(form_data)
    
    # Update all provided fields
    for key, value in data.items():
        if hasattr(character, key):
            # Convert string 'None' to actual None
            if value == 'None' or value == '':
                value = None
            # Convert numeric strings to int for integer fields
            if value is not None:
                column = getattr(VTMCharacter, key, None)
                if column is not None and hasattr(column.property, 'columns'):
                    col_type = str(column.property.columns[0].type)
                    if 'INTEGER' in col_type and isinstance(value, str):
                        try:
                            value = int(value)
                        except ValueError:
                            value = None
            
            setattr(character, key, value)
    
    db.commit()
    db.refresh(character)
    
    return JSONResponse(content={"success": True})


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
