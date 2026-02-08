"""Hunter: The Reckoning character routes"""

import json
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.template_config import templates
from app.sanitize import sanitize_character_data
from app.audit import log_audit_event, AuditEvent, get_client_ip
from app.models_new import HTRCharacter, HTRTouchstone, HTRAdvantage, HTRFlaw, HTRXPLogEntry, UserPreferences
from app.auth import require_auth
from app.constants import CHARACTER_LIMIT_PER_USER
from app.logging_config import get_logger
from app.exceptions import (
    CharacterLimitReached,
    CharacterNotFound,
)
from app.utils import is_admin
from app.routes.common import (
    serialize_model_to_dict,
    delete_character_portraits,
    handle_portrait_upload,
    handle_export_png,
)

router = APIRouter(prefix="/htr", tags=["htr"])
logger = get_logger(__name__)


@router.get("/", response_class=HTMLResponse)
async def htr_character_list(request: Request, db: Session = Depends(get_db)):
    """Display user's HTR characters (up to 3 slots)"""
    user = require_auth(request)

    # Get user's characters
    characters = db.query(HTRCharacter).filter(
        HTRCharacter.user_id == user['id']
    ).order_by(HTRCharacter.created_at).all()

    # Calculate available slots (admins have unlimited)
    if is_admin(user):
        available_slots = 999  # Unlimited for admins
        can_create = True
    else:
        available_slots = CHARACTER_LIMIT_PER_USER - len(characters)
        can_create = available_slots > 0

    return templates.TemplateResponse(
        "htr/character_list.html",
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
    """Display form to create new HTR character"""
    user = require_auth(request)

    # Check character limit (admins are exempt)
    if not is_admin(user):
        character_count = db.query(HTRCharacter).filter(
            HTRCharacter.user_id == user['id']
        ).count()

        if character_count >= CHARACTER_LIMIT_PER_USER:
            return RedirectResponse(
                url="/htr?error=limit_reached",
                status_code=303
            )

    return templates.TemplateResponse(
        "htr/character_sheet.html",
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
    """View HTR character sheet"""
    user = require_auth(request)

    # Get character and verify ownership
    character = db.query(HTRCharacter).filter(
        HTRCharacter.id == character_id,
        HTRCharacter.user_id == user['id']
    ).first()

    if not character:
        raise CharacterNotFound(character_id)

    return templates.TemplateResponse(
        "htr/character_sheet.html",
        {
            "request": request,
            "user": user,
            "character": character,
            "edit_mode": False,
            "export_url": f"/htr/character/{character_id}/export/png"
        }
    )


@router.get("/character/{character_id}/edit", response_class=HTMLResponse)
async def edit_character_form(
    request: Request,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Display form to edit HTR character"""
    user = require_auth(request)

    # Get character and verify ownership
    character = db.query(HTRCharacter).filter(
        HTRCharacter.id == character_id,
        HTRCharacter.user_id == user['id']
    ).first()

    if not character:
        raise CharacterNotFound(character_id)

    return templates.TemplateResponse(
        "htr/character_sheet.html",
        {
            "request": request,
            "user": user,
            "character": character,
            "edit_mode": True,
            "export_url": f"/htr/character/{character_id}/export/png"
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

    # Eager load relationships to prevent N+1 queries
    character = db.query(HTRCharacter).options(
        joinedload(HTRCharacter.touchstones),
        joinedload(HTRCharacter.advantages),
        joinedload(HTRCharacter.flaws),
        joinedload(HTRCharacter.xp_log),
        joinedload(HTRCharacter.edges),
        joinedload(HTRCharacter.perks),
        joinedload(HTRCharacter.equipment)
    ).filter(
        HTRCharacter.id == character_id,
        HTRCharacter.user_id == user['id']
    ).first()

    if not character:
        raise CharacterNotFound(character_id)

    char_dict = serialize_model_to_dict(character)

    # Add relationships as arrays
    char_dict['touchstones'] = [
        {
            'name': ts.name,
            'description': ts.description
        }
        for ts in character.touchstones
    ]

    char_dict['advantages'] = [
        {
            'type': adv.type,
            'description': adv.description,
            'dots': adv.dots
        }
        for adv in character.advantages
    ]

    char_dict['flaws'] = [
        {
            'type': flaw.type,
            'description': flaw.description,
            'dots': flaw.dots
        }
        for flaw in character.flaws
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

    # Add edges and perks (NEW SYSTEM)
    char_dict['edges'] = [
        {
            'edge_id': edge.edge_id
        }
        for edge in character.edges
    ]

    char_dict['perks'] = [
        {
            'edge_id': perk.edge_id,
            'perk_id': perk.perk_id
        }
        for perk in character.perks
    ]

    char_dict['equipment'] = [
        {
            'name': item.name,
            'description': item.description
        }
        for item in character.equipment
    ]

    return JSONResponse(content=char_dict)


@router.post("/character/create")
async def create_character(
    request: Request,
    db: Session = Depends(get_db)
):
    """Create new HTR character"""
    user = require_auth(request)

    # Check character limit (admins are exempt)
    if not is_admin(user):
        character_count = db.query(HTRCharacter).filter(
            HTRCharacter.user_id == user['id']
        ).count()

        if character_count >= CHARACTER_LIMIT_PER_USER:
            raise CharacterLimitReached(CHARACTER_LIMIT_PER_USER)

    # Get data from request
    try:
        data = await request.json()
    except Exception:
        # Fallback to form data if JSON parsing fails
        form_data = await request.form()
        data = dict(form_data)

    # Sanitize all user input to prevent XSS attacks
    data = sanitize_character_data(data, game_type='htr')

    # Extract arrays
    touchstones_data = data.pop('touchstones', [])
    advantages_data = data.pop('advantages', [])
    flaws_data = data.pop('flaws', [])
    xp_log_data = data.pop('xp_log', '[]')

    # Parse XP log if it's a string
    if isinstance(xp_log_data, str):
        try:
            xp_log_data = json.loads(xp_log_data)
        except (json.JSONDecodeError, ValueError):
            xp_log_data = []

    # Use defaults if name not provided
    if 'name' not in data or not data['name']:
        data['name'] = 'Unnamed Hunter'

    # Create character
    character = HTRCharacter(
        user_id=user['id'],
        **{k: v for k, v in data.items() if hasattr(HTRCharacter, k)}
    )

    db.add(character)
    db.flush()  # Get character ID without committing

    # Create touchstones
    for i, ts_data in enumerate(touchstones_data):
        if ts_data.get('name'):  # Only create if has name
            touchstone = HTRTouchstone(
                character_id=character.id,
                name=ts_data['name'],
                description=ts_data.get('description', ''),
                display_order=i
            )
            db.add(touchstone)

    # Create advantages
    for i, adv_data in enumerate(advantages_data):
        if adv_data.get('type'):  # Only create if has type
            advantage = HTRAdvantage(
                character_id=character.id,
                type=adv_data['type'],
                description=adv_data.get('description', ''),
                dots=adv_data.get('dots', 1),
                display_order=i
            )
            db.add(advantage)

    # Create flaws
    for i, flaw_data in enumerate(flaws_data):
        if flaw_data.get('type'):  # Only create if has type
            flaw = HTRFlaw(
                character_id=character.id,
                type=flaw_data['type'],
                description=flaw_data.get('description', ''),
                dots=flaw_data.get('dots', 1),
                display_order=i
            )
            db.add(flaw)

    # Create XP log entries
    for entry_data in xp_log_data:
        xp_entry = HTRXPLogEntry(
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
    """Update existing HTR character - accepts JSON for auto-save"""
    user = require_auth(request)

    # Get character and verify ownership
    character = db.query(HTRCharacter).filter(
        HTRCharacter.id == character_id,
        HTRCharacter.user_id == user['id']
    ).first()

    if not character:
        raise CharacterNotFound(character_id)

    # Get data
    try:
        data = await request.json()
    except Exception:
        # Fallback to form data if JSON parsing fails
        form_data = await request.form()
        data = dict(form_data)

    # Sanitize all user input to prevent XSS attacks
    data = sanitize_character_data(data, game_type='htr')

    # Extract arrays
    touchstones_data = data.pop('touchstones', None)
    advantages_data = data.pop('advantages', None)
    flaws_data = data.pop('flaws', None)
    edges_data = data.pop('edges', None)
    perks_data = data.pop('perks', None)
    equipment_data = data.pop('equipment', None)
    xp_log_data = data.pop('xp_log', None)

    # Parse XP log if it's a string
    if isinstance(xp_log_data, str):
        try:
            xp_log_data = json.loads(xp_log_data)
        except (json.JSONDecodeError, ValueError):
            xp_log_data = None

    # Perform all database updates in an explicit transaction
    try:
        # Update character fields
        for key, value in data.items():
            if hasattr(character, key):
                setattr(character, key, value)

        # Update touchstones if provided
        if touchstones_data is not None:
            # Delete existing touchstones
            db.query(HTRTouchstone).filter(
                HTRTouchstone.character_id == character_id
            ).delete()

            # Create new touchstones
            for i, ts_data in enumerate(touchstones_data):
                if ts_data.get('name'):  # Only create if has name
                    touchstone = HTRTouchstone(
                        character_id=character.id,
                        name=ts_data['name'],
                        description=ts_data.get('description', ''),
                        display_order=i
                    )
                    db.add(touchstone)

        # Update advantages if provided
        if advantages_data is not None:
            # Delete existing advantages
            db.query(HTRAdvantage).filter(
                HTRAdvantage.character_id == character_id
            ).delete()

            # Create new advantages
            for i, adv_data in enumerate(advantages_data):
                if adv_data.get('type'):  # Only create if has type
                    advantage = HTRAdvantage(
                        character_id=character.id,
                        type=adv_data['type'],
                        description=adv_data.get('description', ''),
                        dots=adv_data.get('dots', 1),
                        display_order=i
                    )
                    db.add(advantage)

        # Update flaws if provided
        if flaws_data is not None:
            # Delete existing flaws
            db.query(HTRFlaw).filter(
                HTRFlaw.character_id == character_id
            ).delete()

            # Create new flaws
            for i, flaw_data in enumerate(flaws_data):
                if flaw_data.get('type'):  # Only create if has type
                    flaw = HTRFlaw(
                        character_id=character.id,
                        type=flaw_data['type'],
                        description=flaw_data.get('description', ''),
                        dots=flaw_data.get('dots', 1),
                        display_order=i
                    )
                    db.add(flaw)

        # Update XP log if provided
        if xp_log_data is not None:
            # Delete existing XP log entries
            db.query(HTRXPLogEntry).filter(
                HTRXPLogEntry.character_id == character_id
            ).delete()

            # Create new XP log entries
            for entry_data in xp_log_data:
                xp_entry = HTRXPLogEntry(
                    character_id=character.id,
                    date=entry_data['date'],
                    type=entry_data['type'],
                    amount=entry_data['amount'],
                    reason=entry_data['reason']
                )
                db.add(xp_entry)

        # Update edges if provided
        if edges_data is not None:
            from app.models_new import HTREdge
            # Delete existing edges
            db.query(HTREdge).filter(
                HTREdge.character_id == character_id
            ).delete()

            # Create new edges
            for i, edge_data in enumerate(edges_data):
                if edge_data.get('edge_id'):  # Only create if has edge_id
                    edge = HTREdge(
                        character_id=character.id,
                        edge_id=edge_data['edge_id'],
                        display_order=i
                    )
                    db.add(edge)

        # Update perks if provided
        if perks_data is not None:
            from app.models_new import HTRPerk
            # Delete existing perks
            db.query(HTRPerk).filter(
                HTRPerk.character_id == character_id
            ).delete()

            # Create new perks
            for i, perk_data in enumerate(perks_data):
                if perk_data.get('perk_id') and perk_data.get('edge_id'):  # Only create if has both IDs
                    perk = HTRPerk(
                        character_id=character.id,
                        edge_id=perk_data['edge_id'],
                        perk_id=perk_data['perk_id'],
                        display_order=i
                    )
                    db.add(perk)

        # Update equipment if provided
        if equipment_data is not None:
            from app.models_new import HTREquipment
            # Delete existing equipment
            db.query(HTREquipment).filter(
                HTREquipment.character_id == character_id
            ).delete()

            # Create new equipment
            for i, equip_data in enumerate(equipment_data):
                if equip_data.get('name'):  # Only create if has name
                    equipment = HTREquipment(
                        character_id=character.id,
                        name=equip_data['name'],
                        description=equip_data.get('description', ''),
                        display_order=i
                    )
                    db.add(equipment)

        # Commit all changes atomically
        db.commit()
        db.refresh(character)
    except Exception as e:
        # Rollback on any error to maintain data consistency
        db.rollback()
        logger.error(f"Error updating character {character_id}: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to update character", "details": str(e)}
        )

    # Log character update for audit trail
    log_audit_event(
        db=db,
        event_type=AuditEvent.CHARACTER_UPDATE,
        user_id=user['id'],
        target_id=character.id,
        target_type='htr_character',
        details={"name": character.name},
        ip_address=get_client_ip(request)
    )

    return JSONResponse(content={"success": True})


@router.post("/character/{character_id}/delete")
async def delete_character(
    request: Request,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Delete HTR character"""
    user = require_auth(request)

    # Get character and verify ownership
    character = db.query(HTRCharacter).filter(
        HTRCharacter.id == character_id,
        HTRCharacter.user_id == user['id']
    ).first()

    if not character:
        raise CharacterNotFound(character_id)

    delete_character_portraits(character)

    # Delete character (cascade will handle touchstones, advantages, flaws, xp_log)
    db.delete(character)
    db.commit()

    return RedirectResponse(url="/htr", status_code=303)


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

    character = db.query(HTRCharacter).filter(
        HTRCharacter.id == character_id,
        HTRCharacter.user_id == user['id']
    ).first()

    if not character:
        raise CharacterNotFound(character_id)

    return await handle_portrait_upload(character, file, box_type, db)


@router.get("/character/{character_id}/export/png")
async def export_character_png(
    character_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Export HTR character sheet as PNG image"""
    user = require_auth(request)

    character = db.query(HTRCharacter).filter(
        HTRCharacter.id == character_id,
        HTRCharacter.user_id == user['id']
    ).first()

    if not character:
        raise CharacterNotFound(character_id)

    try:
        return await handle_export_png(character, 'htr', request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export PNG: {str(e)}"
        )
