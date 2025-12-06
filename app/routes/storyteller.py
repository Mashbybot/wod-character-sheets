"""Storyteller view routes - read-only access to all characters"""

from typing import List, Dict, Any
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_new import VTMCharacter, HTRCharacter, User
from app.auth import require_auth
from app.utils import is_storyteller, group_characters_by_chronicle

router = APIRouter(prefix="/storyteller", tags=["storyteller"])
templates = Jinja2Templates(directory="templates")


def require_storyteller(request: Request) -> dict:
    """Require user to be authenticated AND be a storyteller"""
    user = require_auth(request)

    if not is_storyteller(user):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Storyteller privileges required"
        )

    return user


@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
async def storyteller_dashboard(request: Request, db: Session = Depends(get_db)):
    """Display all characters across all game types for storyteller"""
    user = require_storyteller(request)

    # Get all VTM characters with user info
    vtm_characters = db.query(VTMCharacter).join(User).order_by(
        VTMCharacter.chronicle,
        VTMCharacter.name
    ).all()

    # Get all HTR characters with user info
    htr_characters = db.query(HTRCharacter).join(User).order_by(
        HTRCharacter.chronicle,
        HTRCharacter.name
    ).all()

    # Combine all characters for grouping
    all_characters = []

    # Add VTM characters with game type tag
    for char in vtm_characters:
        all_characters.append({
            'id': char.id,
            'name': char.name,
            'chronicle': char.chronicle,
            'game_type': 'VTM',
            'player_name': char.user.discord_username,
            'player_id': char.user_id,
            'updated_at': char.updated_at,
            'character_obj': char  # Keep reference for grouping
        })

    # Add HTR characters with game type tag
    for char in htr_characters:
        all_characters.append({
            'id': char.id,
            'name': char.name,
            'chronicle': char.chronicle,
            'game_type': 'HTR',
            'player_name': char.user.discord_username,
            'player_id': char.user_id,
            'updated_at': char.updated_at,
            'character_obj': char  # Keep reference for grouping
        })

    # Group by chronicle (fuzzy matching)
    # Extract character objects for grouping function
    char_objects = [c['character_obj'] for c in all_characters]
    grouped_by_chronicle = group_characters_by_chronicle(char_objects)

    # Rebuild grouped structure with metadata
    grouped_display = {}
    for chronicle_key, char_objs in grouped_by_chronicle.items():
        grouped_display[chronicle_key] = []
        for char_obj in char_objs:
            # Find the matching character in all_characters
            matching_char = next(
                (c for c in all_characters if c['character_obj'] is char_obj),
                None
            )
            if matching_char:
                grouped_display[chronicle_key].append(matching_char)

    # Sort each group by name
    for chronicle_key in grouped_display:
        grouped_display[chronicle_key].sort(key=lambda x: x['name'].lower())

    # Get original chronicle names (before normalization) for display
    chronicle_display_names = {}
    for chronicle_key, chars in grouped_display.items():
        if chronicle_key == "uncategorized":
            chronicle_display_names[chronicle_key] = "Uncategorized"
        elif chars:
            # Use the first character's actual chronicle name
            original_name = chars[0].get('chronicle')
            chronicle_display_names[chronicle_key] = original_name if original_name else "Uncategorized"
        else:
            chronicle_display_names[chronicle_key] = chronicle_key.title()

    return templates.TemplateResponse(
        "storyteller_dashboard.html",
        {
            "request": request,
            "user": user,
            "all_characters": all_characters,
            "grouped_characters": grouped_display,
            "chronicle_display_names": chronicle_display_names,
            "vtm_count": len(vtm_characters),
            "htr_count": len(htr_characters),
            "total_count": len(all_characters)
        }
    )


@router.get("/vtm/character/{character_id}", response_class=HTMLResponse)
async def view_vtm_character(
    character_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """View a VTM character in read-only mode"""
    user = require_storyteller(request)

    # Get character (no ownership check - storyteller can see all)
    character = db.query(VTMCharacter).filter(
        VTMCharacter.id == character_id
    ).first()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Get user preferences (use storyteller's preferences for column widths)
    from app.models_new import UserPreferences
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == user['id']
    ).first()

    return templates.TemplateResponse(
        "vtm/character_sheet.html",
        {
            "request": request,
            "user": user,
            "character": character,
            "edit_mode": False,  # CRITICAL: Disable editing
            "view_mode": True,   # Enable storyteller view mode
            "character_owner": character.user.discord_username,  # Show who owns it
            "preferences": prefs
        }
    )


@router.get("/htr/character/{character_id}", response_class=HTMLResponse)
async def view_htr_character(
    character_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """View an HTR character in read-only mode"""
    user = require_storyteller(request)

    # Get character (no ownership check - storyteller can see all)
    character = db.query(HTRCharacter).filter(
        HTRCharacter.id == character_id
    ).first()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Get user preferences (use storyteller's preferences for column widths)
    from app.models_new import UserPreferences
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == user['id']
    ).first()

    return templates.TemplateResponse(
        "htr/character_sheet.html",
        {
            "request": request,
            "user": user,
            "character": character,
            "edit_mode": False,  # CRITICAL: Disable editing
            "view_mode": True,   # Enable storyteller view mode
            "character_owner": character.user.discord_username,  # Show who owns it
            "preferences": prefs
        }
    )
