"""Vampire: The Masquerade character routes - REFACTORED"""

import os
import json
from typing import Optional, List
from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.template_config import templates
from app.models_new import VTMCharacter, Touchstone, Background, Discipline, XPLogEntry, UserPreferences
from app.schemas import (
    VTMCharacterCreate,
    VTMCharacterUpdate,
    VTMCharacterResponse,
    TouchstoneCreate,
    BackgroundCreate,
    XPLogEntryCreate,
    ErrorResponse
)
from app.auth import require_auth
from app.constants import CHARACTER_LIMIT_PER_USER, MAX_UPLOAD_SIZE, ALLOWED_IMAGE_EXTENSIONS
from app.exceptions import (
    CharacterLimitReached,
    CharacterNotFound,
    ImageUploadError,
    validate_character_ownership,
    validate_file_size,
    validate_file_extension,
    validate_image_type
)
from app.utils import (
    process_and_save_portrait,
    delete_portrait,
    calculate_available_xp,
    get_current_date_string
)

router = APIRouter(prefix="/vtm", tags=["vtm"])


@router.get("/", response_class=HTMLResponse)
async def vtm_character_list(request: Request, db: Session = Depends(get_db)):
    """Display user's VTM characters (up to 3 slots)"""
    user = require_auth(request)

    # Get user's characters
    characters = db.query(VTMCharacter).filter(
        VTMCharacter.user_id == user['id']
    ).order_by(VTMCharacter.created_at).all()

    # DEBUG: Log portrait data
    for char in characters:
        print(f"[DEBUG CHARACTER LIST] Character {char.id} ({char.name}): portrait_face={char.portrait_face}, portrait_body={char.portrait_body}")

    # Calculate available slots
    available_slots = CHARACTER_LIMIT_PER_USER - len(characters)
    can_create = available_slots > 0

    return templates.TemplateResponse(
        "vtm/character_list.html",
        {
            "request": request,
            "user": user,
            "characters": characters,
            "available_slots": available_slots,
            "can_create": can_create,
            "character_limit": CHARACTER_LIMIT_PER_USER
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
    
    if character_count >= CHARACTER_LIMIT_PER_USER:
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
        raise CharacterNotFound(character_id)
    
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
        raise CharacterNotFound(character_id)
    
    return templates.TemplateResponse(
        "vtm/character_sheet.html",
        {
            "request": request,
            "user": user,
            "character": character,
            "edit_mode": True
        }
    )


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
        raise CharacterNotFound(character_id)
    
    # Convert SQLAlchemy object to dict with datetime handling
    char_dict = {}
    for c in character.__table__.columns:
        value = getattr(character, c.name)
        # Convert datetime to ISO string for JSON serialization
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        char_dict[c.name] = value
    
    # Add relationships as arrays
    char_dict['touchstones'] = [
        {
            'name': ts.name,
            'description': ts.description,
            'conviction': ts.conviction
        }
        for ts in character.touchstones
    ]
    
    char_dict['backgrounds'] = [
        {
            'category': bg.category or 'Background',
            'type': bg.type,
            'description': bg.description,
            'dots': bg.dots,
            'description_height': bg.description_height or 60
        }
        for bg in character.backgrounds
    ]

    char_dict['disciplines'] = [
        {
            'name': disc.name,
            'level': disc.level,
            'powers': json.loads(disc.powers) if disc.powers and disc.powers.startswith('[') else (disc.powers.split('\n') if disc.powers else [''])
        }
        for disc in character.disciplines
    ]

    char_dict['xp_log'] = [
        {
            'date': entry.date,
            'type': entry.type,
            'amount': entry.amount,
            'reason': entry.reason
        }
        for entry in character.xp_log
    ]
    
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
    
    if character_count >= CHARACTER_LIMIT_PER_USER:
        raise CharacterLimitReached(CHARACTER_LIMIT_PER_USER)
    
    # Get data from request
    try:
        data = await request.json()
    except:
        form_data = await request.form()
        data = dict(form_data)
    
    # Extract touchstones, backgrounds, disciplines arrays
    touchstones_data = data.pop('touchstones', [])
    backgrounds_data = data.pop('backgrounds', [])
    disciplines_data = data.pop('disciplines', [])
    xp_log_data = data.pop('xp_log', '[]')
    
    # Parse XP log if it's a string
    if isinstance(xp_log_data, str):
        try:
            xp_log_data = json.loads(xp_log_data)
        except:
            xp_log_data = []
    
    # Validate character data with Pydantic
    try:
        # Use defaults if name not provided
        if 'name' not in data or not data['name']:
            data['name'] = 'Unnamed'
        
        char_create = VTMCharacterCreate(**data)
    except Exception as e:
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "details": str(e)
            }
        )
    
    # Create character
    character = VTMCharacter(
        user_id=user['id'],
        **char_create.model_dump(exclude_none=True)
    )
    
    db.add(character)
    db.flush()  # Get character ID without committing
    
    # Create touchstones
    for i, ts_data in enumerate(touchstones_data):
        if ts_data.get('name'):  # Only create if has name
            touchstone = Touchstone(
                character_id=character.id,
                name=ts_data['name'],
                description=ts_data.get('description', ''),
                conviction=ts_data.get('conviction', ''),
                display_order=i
            )
            db.add(touchstone)
    
    # Create backgrounds
    for i, bg_data in enumerate(backgrounds_data):
        if bg_data.get('type'):  # Only create if has type
            background = Background(
                character_id=character.id,
                category=bg_data.get('category', 'Background'),
                type=bg_data['type'],
                description=bg_data.get('description', ''),
                dots=bg_data.get('dots', 0),
                description_height=bg_data.get('description_height', 60),
                display_order=i
            )
            db.add(background)

    # Create disciplines
    for i, disc_data in enumerate(disciplines_data):
        if disc_data.get('name'):  # Only create if has name
            # Convert powers array to JSON string
            powers_data = disc_data.get('powers', [''])
            if isinstance(powers_data, list):
                powers_str = json.dumps(powers_data)
            else:
                powers_str = powers_data

            discipline = Discipline(
                character_id=character.id,
                name=disc_data['name'],
                level=disc_data.get('level', 0),
                powers=powers_str,
                description='',  # No longer used
                display_order=i
            )
            db.add(discipline)

    # Create XP log entries
    for entry_data in xp_log_data:
        xp_entry = XPLogEntry(
            character_id=character.id,
            date=entry_data['date'],
            type=entry_data['type'],
            amount=entry_data['amount'],
            reason=entry_data['reason']
        )
        db.add(xp_entry)
    
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
        raise CharacterNotFound(character_id)
    
    # Get data
    try:
        data = await request.json()
    except:
        form_data = await request.form()
        data = dict(form_data)
    
    # Extract arrays
    touchstones_data = data.pop('touchstones', None)
    backgrounds_data = data.pop('backgrounds', None)
    disciplines_data = data.pop('disciplines', None)
    xp_log_data = data.pop('xp_log', None)
    
    # Parse XP log if it's a string
    if isinstance(xp_log_data, str):
        try:
            xp_log_data = json.loads(xp_log_data)
        except:
            xp_log_data = None
    
    # Update character fields with Pydantic validation
    try:
        char_update = VTMCharacterUpdate(**data)
        update_data = char_update.model_dump(exclude_none=True)
        
        for key, value in update_data.items():
            if hasattr(character, key):
                setattr(character, key, value)
    except Exception as e:
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "details": str(e)
            }
        )
    
    # Update touchstones if provided
    if touchstones_data is not None:
        # Delete existing touchstones
        db.query(Touchstone).filter(
            Touchstone.character_id == character_id
        ).delete()
        
        # Create new touchstones
        for i, ts_data in enumerate(touchstones_data):
            if ts_data.get('name'):  # Only create if has name
                touchstone = Touchstone(
                    character_id=character.id,
                    name=ts_data['name'],
                    description=ts_data.get('description', ''),
                    conviction=ts_data.get('conviction', ''),
                    display_order=i
                )
                db.add(touchstone)
    
    # Update backgrounds if provided
    if backgrounds_data is not None:
        # Delete existing backgrounds
        db.query(Background).filter(
            Background.character_id == character_id
        ).delete()
        
        # Create new backgrounds
        for i, bg_data in enumerate(backgrounds_data):
            if bg_data.get('type'):  # Only create if has type
                background = Background(
                    character_id=character.id,
                    category=bg_data.get('category', 'Background'),
                    type=bg_data['type'],
                    description=bg_data.get('description', ''),
                    dots=bg_data.get('dots', 0),
                    description_height=bg_data.get('description_height', 60),
                    display_order=i
                )
                db.add(background)

    # Update disciplines if provided
    if disciplines_data is not None:
        # Delete existing disciplines
        db.query(Discipline).filter(
            Discipline.character_id == character_id
        ).delete()

        # Create new disciplines
        for i, disc_data in enumerate(disciplines_data):
            if disc_data.get('name'):  # Only create if has name
                # Convert powers array to JSON string
                powers_data = disc_data.get('powers', [''])
                if isinstance(powers_data, list):
                    powers_str = json.dumps(powers_data)
                else:
                    powers_str = powers_data

                discipline = Discipline(
                    character_id=character.id,
                    name=disc_data['name'],
                    level=disc_data.get('level', 0),
                    powers=powers_str,
                    description='',  # No longer used
                    display_order=i
                )
                db.add(discipline)

    # Update XP log if provided
    if xp_log_data is not None:
        # Delete existing XP log entries
        db.query(XPLogEntry).filter(
            XPLogEntry.character_id == character_id
        ).delete()
        
        # Create new XP log entries
        for entry_data in xp_log_data:
            xp_entry = XPLogEntry(
                character_id=character.id,
                date=entry_data['date'],
                type=entry_data['type'],
                amount=entry_data['amount'],
                reason=entry_data['reason']
            )
            db.add(xp_entry)
    
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
        raise CharacterNotFound(character_id)
    
    # Delete character portraits if they exist
    portraits = [
        character.portrait_face,
        character.portrait_body,
        character.portrait_hobby_1,
        character.portrait_hobby_2,
        character.portrait_hobby_3,
        character.portrait_hobby_4
    ]
    
    for portrait_url in portraits:
        if portrait_url:
            delete_portrait(portrait_url)
    
    # Delete character (cascade will handle touchstones, backgrounds, xp_log)
    db.delete(character)
    db.commit()
    
    return RedirectResponse(url="/vtm", status_code=303)


@router.post("/character/{character_id}/upload-portrait")
async def upload_portrait(
    character_id: int,
    request: Request,
    file: Optional[UploadFile] = File(None),
    box_type: Optional[str] = Form('face'),
    db: Session = Depends(get_db)
):
    """Upload character portrait (file or URL) to specific box"""
    user = require_auth(request)
    
    # Get character and verify ownership
    character = db.query(VTMCharacter).filter(
        VTMCharacter.id == character_id,
        VTMCharacter.user_id == user['id']
    ).first()
    
    if not character:
        raise CharacterNotFound(character_id)
    
    # Validate box_type
    valid_boxes = ['face', 'body', 'hobby_1', 'hobby_2', 'hobby_3', 'hobby_4']
    if box_type not in valid_boxes:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid box type"}
        )
    
    if not file:
        return JSONResponse(
            status_code=400,
            content={"error": "No file provided"}
        )
    
    # Validate file type
    validate_image_type(file.content_type)
    validate_file_extension(file.filename, ALLOWED_IMAGE_EXTENSIONS)
    
    # Read file
    file_content = await file.read()
    validate_file_size(len(file_content), MAX_UPLOAD_SIZE)
    
    # Process and save image
    try:
        # Delete old portrait if exists
        old_portrait = getattr(character, f'portrait_{box_type}', None)
        if old_portrait:
            delete_portrait(old_portrait)
        
        # Save new portrait
        from io import BytesIO
        portrait_url = process_and_save_portrait(
            BytesIO(file_content),
            file.filename,
            box_type
        )
        
        # Update character
        setattr(character, f'portrait_{box_type}', portrait_url)
        db.commit()

        # DEBUG: Log what was saved
        print(f"[DEBUG UPLOAD] Character {character.id}: Set portrait_{box_type} = {portrait_url}")

        return JSONResponse(content={
            "success": True,
            "portrait_url": portrait_url
        })
        
    except ImageUploadError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to upload portrait: {str(e)}"}
        )


# ===== USER PREFERENCES ENDPOINTS =====

@router.get("/api/preferences")
async def get_user_preferences(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get user UI preferences"""
    user = require_auth(request)
    
    # Get or create preferences
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == user['id']
    ).first()
    
    if not prefs:
        prefs = UserPreferences(
            user_id=user['id'],
            column_widths_above="30,35,35",
            column_widths_below="33,33,34",
            theme="dark"
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return JSONResponse(content={
        "column_widths_above": prefs.column_widths_above,
        "column_widths_below": prefs.column_widths_below,
        "history_in_life_height": prefs.history_in_life_height,
        "after_death_height": prefs.after_death_height,
        "notes_height": prefs.notes_height,
        "theme": prefs.theme
    })


@router.post("/api/preferences")
async def update_user_preferences(
    request: Request,
    db: Session = Depends(get_db)
):
    """Update user UI preferences"""
    user = require_auth(request)
    
    data = await request.json()
    
    # Get or create preferences
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == user['id']
    ).first()
    
    if not prefs:
        prefs = UserPreferences(user_id=user['id'])
        db.add(prefs)
    
    # Update fields
    if 'column_widths_above' in data:
        prefs.column_widths_above = data['column_widths_above']
    if 'column_widths_below' in data:
        prefs.column_widths_below = data['column_widths_below']
    if 'history_in_life_height' in data:
        prefs.history_in_life_height = data['history_in_life_height']
    if 'after_death_height' in data:
        prefs.after_death_height = data['after_death_height']
    if 'notes_height' in data:
        prefs.notes_height = data['notes_height']
    if 'theme' in data:
        prefs.theme = data['theme']
    
    db.commit()
    
    return JSONResponse(content={"success": True})
