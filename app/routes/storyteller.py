"""Storyteller view routes - read-only access to all characters

This module provides storyteller-only routes for viewing all player characters
in read-only mode across all game types.

Currently supported:
- VTM (Vampire: The Masquerade)
- HTR (Hunter: The Reckoning)

To add support for future game types (e.g., WTA - Werewolf: The Apocalypse):
1. Import the character model (e.g., from app.models_new import WTACharacter)
2. Add character query to storyteller_dashboard() function
3. Create HTML view route: @router.get("/wta/character/{character_id}")
4. Create API endpoint: @router.get("/wta/api/character/{character_id}")
5. Update character sheet template to include storyteller_mode flag
6. Update JavaScript to use storyteller API when STORYTELLER_MODE=true
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.template_config import templates
from app.models_new import VTMCharacter, HTRCharacter, User
from app.auth import require_auth
from app.utils import is_storyteller, group_characters_by_chronicle, delete_portrait
from app.exceptions import CharacterNotFound
from app.constants import STORYTELLER_DASHBOARD_LIMIT

router = APIRouter(prefix="/storyteller", tags=["storyteller"])


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

    # Get total counts before pagination
    vtm_total = db.query(VTMCharacter).count()
    htr_total = db.query(HTRCharacter).count()
    total_characters = vtm_total + htr_total

    # Get VTM characters with pagination limit (eager load to prevent N+1 queries)
    vtm_characters = db.query(VTMCharacter).options(
        joinedload(VTMCharacter.user)
    ).order_by(
        VTMCharacter.chronicle,
        VTMCharacter.name
    ).limit(STORYTELLER_DASHBOARD_LIMIT).all()

    # Get HTR characters with pagination limit (eager load to prevent N+1 queries)
    # Calculate remaining limit for HTR after VTM
    remaining_limit = max(0, STORYTELLER_DASHBOARD_LIMIT - len(vtm_characters))
    htr_characters = db.query(HTRCharacter).options(
        joinedload(HTRCharacter.user)
    ).order_by(
        HTRCharacter.chronicle,
        HTRCharacter.name
    ).limit(remaining_limit).all() if remaining_limit > 0 else []

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

    # Check if results were truncated
    truncated = total_characters > STORYTELLER_DASHBOARD_LIMIT

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
            "total_count": len(all_characters),
            "vtm_total": vtm_total,
            "htr_total": htr_total,
            "total_characters": total_characters,
            "truncated": truncated,
            "limit": STORYTELLER_DASHBOARD_LIMIT
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
            "storyteller_mode": True,  # Use storyteller API endpoints
            "character_owner": character.user.discord_username,  # Show who owns it
            "preferences": prefs
        }
    )


@router.get("/vtm/api/character/{character_id}")
async def get_vtm_character_api(
    character_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """API endpoint to get VTM character data - storyteller access"""
    user = require_storyteller(request)

    # Get character with all related data (eager load to prevent N+1 queries)
    character = db.query(VTMCharacter).options(
        joinedload(VTMCharacter.touchstones),
        joinedload(VTMCharacter.backgrounds),
        joinedload(VTMCharacter.xp_log),
        joinedload(VTMCharacter.equipment)
    ).filter(
        VTMCharacter.id == character_id
    ).first()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Build response with all character data
    from app.schemas import VTMCharacterResponse

    # Convert to dict for JSON response
    char_dict = {
        "id": character.id,
        "user_id": character.user_id,
        "name": character.name,
        "chronicle": character.chronicle,
        "concept": character.concept,
        "predator": character.predator,
        "ambition": character.ambition,
        "desire": character.desire,
        "apparent_age": character.apparent_age,
        "true_age": character.true_age,
        "date_of_birth": character.date_of_birth,
        "date_of_death": character.date_of_death,
        "appearance": character.appearance,
        "distinguishing_features": character.distinguishing_features,
        "pronouns": character.pronouns,
        "ethnicity": character.ethnicity,
        "languages": character.languages,
        "birthplace": character.birthplace,

        # Attributes
        "strength": character.strength,
        "dexterity": character.dexterity,
        "stamina": character.stamina,
        "charisma": character.charisma,
        "manipulation": character.manipulation,
        "composure": character.composure,
        "intelligence": character.intelligence,
        "wits": character.wits,
        "resolve": character.resolve,

        # Skills - Physical
        "athletics": character.athletics,
        "brawl": character.brawl,
        "craft": character.craft,
        "drive": character.drive,
        "firearms": character.firearms,
        "larceny": character.larceny,
        "melee": character.melee,
        "stealth": character.stealth,
        "survival": character.survival,

        # Skills - Social
        "animal_ken": character.animal_ken,
        "etiquette": character.etiquette,
        "insight": character.insight,
        "intimidation": character.intimidation,
        "leadership": character.leadership,
        "performance": character.performance,
        "persuasion": character.persuasion,
        "streetwise": character.streetwise,
        "subterfuge": character.subterfuge,

        # Skills - Mental
        "academics": character.academics,
        "awareness": character.awareness,
        "finance": character.finance,
        "investigation": character.investigation,
        "medicine": character.medicine,
        "occult": character.occult,
        "politics": character.politics,
        "science": character.science,
        "technology": character.technology,

        "skill_specialties": character.skill_specialties,

        # Vampire traits
        "clan": character.clan,
        "sire": character.sire,
        "generation": character.generation,
        "bane_type": character.bane_type,
        "bane_custom": character.bane_custom,
        "compulsion": character.compulsion,
        "compulsion_custom": character.compulsion_custom,

        # Trackers
        "hunger": character.hunger,
        "resonance": character.resonance,
        "blood_potency": character.blood_potency,
        "health_max": character.health_max,
        "health_superficial": character.health_superficial,
        "health_aggravated": character.health_aggravated,
        "willpower_max": character.willpower_max,
        "willpower_superficial": character.willpower_superficial,
        "willpower_aggravated": character.willpower_aggravated,
        "humanity_current": character.humanity_current,
        "humanity_stained": character.humanity_stained,

        # Disciplines
        "discipline_1_name": character.discipline_1_name,
        "discipline_1_level": character.discipline_1_level,
        "discipline_1_powers": character.discipline_1_powers,
        "discipline_1_description": character.discipline_1_description,
        "discipline_2_name": character.discipline_2_name,
        "discipline_2_level": character.discipline_2_level,
        "discipline_2_powers": character.discipline_2_powers,
        "discipline_2_description": character.discipline_2_description,
        "discipline_3_name": character.discipline_3_name,
        "discipline_3_level": character.discipline_3_level,
        "discipline_3_powers": character.discipline_3_powers,
        "discipline_3_description": character.discipline_3_description,
        "discipline_4_name": character.discipline_4_name,
        "discipline_4_level": character.discipline_4_level,
        "discipline_4_powers": character.discipline_4_powers,
        "discipline_4_description": character.discipline_4_description,
        "discipline_5_name": character.discipline_5_name,
        "discipline_5_level": character.discipline_5_level,
        "discipline_5_powers": character.discipline_5_powers,
        "discipline_5_description": character.discipline_5_description,

        # Chronicle tenets
        "chronicle_tenet_1": character.chronicle_tenet_1,
        "chronicle_tenet_2": character.chronicle_tenet_2,
        "chronicle_tenet_3": character.chronicle_tenet_3,
        "chronicle_tenet_4": character.chronicle_tenet_4,
        "chronicle_tenet_5": character.chronicle_tenet_5,

        # Experience
        "exp_total": character.exp_total,
        "exp_spent": character.exp_spent,

        # Text fields
        "notes": character.notes,
        "history_in_life": character.history_in_life,
        "after_death": character.after_death,

        # Portraits
        "portrait_face": character.portrait_face,
        "portrait_body": character.portrait_body,
        "portrait_hobby_1": character.portrait_hobby_1,
        "portrait_hobby_2": character.portrait_hobby_2,
        "portrait_hobby_3": character.portrait_hobby_3,
        "portrait_hobby_4": character.portrait_hobby_4,

        # Related data
        "touchstones": [
            {
                "name": ts.name,
                "description": ts.description,
                "conviction": ts.conviction
            }
            for ts in character.touchstones
        ],
        "backgrounds": [
            {
                "type": bg.type,
                "description": bg.description,
                "dots": bg.dots
            }
            for bg in character.backgrounds
        ],
        "xp_log": [
            {
                "date": entry.date,
                "type": entry.type,
                "amount": entry.amount,
                "reason": entry.reason
            }
            for entry in character.xp_log
        ],
        "equipment": [
            {
                "name": item.name,
                "description": item.description
            }
            for item in character.equipment
        ]
    }

    return JSONResponse(content=char_dict)


@router.get("/htr/api/character/{character_id}")
async def get_htr_character_api(
    character_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """API endpoint to get HTR character data - storyteller access"""
    user = require_storyteller(request)

    # Get character with all related data (eager load to prevent N+1 queries)
    character = db.query(HTRCharacter).options(
        joinedload(HTRCharacter.touchstones),
        joinedload(HTRCharacter.advantages),
        joinedload(HTRCharacter.flaws),
        joinedload(HTRCharacter.edges),
        joinedload(HTRCharacter.perks),
        joinedload(HTRCharacter.xp_log),
        joinedload(HTRCharacter.equipment)
    ).filter(
        HTRCharacter.id == character_id
    ).first()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Build response with all character data
    char_dict = {
        "id": character.id,
        "user_id": character.user_id,
        "name": character.name,
        "cell": character.cell,
        "chronicle": character.chronicle,

        # Identity
        "creed": character.creed,
        "drive": character.drive,
        "age": character.age,
        "blood_type": character.blood_type,
        "pronouns": character.pronouns,
        "origin": character.origin,
        "alias": character.alias,

        # Attributes
        "strength": character.strength,
        "dexterity": character.dexterity,
        "stamina": character.stamina,
        "charisma": character.charisma,
        "manipulation": character.manipulation,
        "composure": character.composure,
        "intelligence": character.intelligence,
        "wits": character.wits,
        "resolve": character.resolve,

        # Skills - Physical
        "athletics": character.athletics,
        "brawl": character.brawl,
        "craft": character.craft,
        "drive_skill": character.drive_skill,
        "firearms": character.firearms,
        "larceny": character.larceny,
        "melee": character.melee,
        "stealth": character.stealth,
        "survival": character.survival,

        # Skills - Social
        "animal_ken": character.animal_ken,
        "etiquette": character.etiquette,
        "insight": character.insight,
        "intimidation": character.intimidation,
        "leadership": character.leadership,
        "performance": character.performance,
        "persuasion": character.persuasion,
        "streetwise": character.streetwise,
        "subterfuge": character.subterfuge,

        # Skills - Mental
        "academics": character.academics,
        "awareness": character.awareness,
        "finance": character.finance,
        "investigation": character.investigation,
        "medicine": character.medicine,
        "occult": character.occult,
        "politics": character.politics,
        "science": character.science,
        "technology": character.technology,

        "skill_specialties": character.skill_specialties,

        # Trackers
        "danger_current": character.danger_current,
        "desperation_current": character.desperation_current,
        "health_max": character.health_max,
        "health_superficial": character.health_superficial,
        "health_aggravated": character.health_aggravated,
        "willpower_max": character.willpower_max,
        "willpower_superficial": character.willpower_superficial,
        "willpower_aggravated": character.willpower_aggravated,
        "in_despair": character.in_despair,

        # Edges & Perks (NEW SYSTEM)
        "edges": [
            {
                "edge_id": edge.edge_id
            }
            for edge in character.edges
        ],
        "perks": [
            {
                "edge_id": perk.edge_id,
                "perk_id": perk.perk_id
            }
            for perk in character.perks
        ],

        # Equipment
        "equipment_weapon": character.equipment_weapon,
        "equipment_weapon_damage": character.equipment_weapon_damage,
        "equipment_armor_rating": character.equipment_armor_rating,
        "equipment_notes": character.equipment_notes,

        # Experience
        "exp_total": character.exp_total,
        "exp_available": character.exp_available,
        "exp_spent": character.exp_spent,

        # History & Notes
        "first_encounter": character.first_encounter,
        "history": character.history,
        "notes": character.notes,
        "current_mission": character.current_mission,

        # Portraits
        "portrait_face": character.portrait_face,
        "portrait_body": character.portrait_body,
        "portrait_hobby_1": character.portrait_hobby_1,
        "portrait_hobby_2": character.portrait_hobby_2,
        "portrait_hobby_3": character.portrait_hobby_3,
        "portrait_hobby_4": character.portrait_hobby_4,

        # Character creation
        "creation_complete": character.creation_complete,

        # Related data
        "touchstones": [
            {
                "name": ts.name,
                "description": ts.description
            }
            for ts in character.touchstones
        ],
        "advantages": [
            {
                "name": adv.name,
                "description": adv.description,
                "dots": adv.dots
            }
            for adv in character.advantages
        ],
        "flaws": [
            {
                "name": flaw.name,
                "description": flaw.description,
                "dots": flaw.dots
            }
            for flaw in character.flaws
        ],
        "xp_log": [
            {
                "date": entry.date,
                "type": entry.type,
                "amount": entry.amount,
                "reason": entry.reason
            }
            for entry in character.xp_log
        ],
        "equipment": [
            {
                "name": item.name,
                "description": item.description
            }
            for item in character.equipment
        ]
    }

    return JSONResponse(content=char_dict)


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
            "storyteller_mode": True,  # Use storyteller API endpoints
            "character_owner": character.user.discord_username,  # Show who owns it
            "preferences": prefs
        }
    )


@router.post("/vtm/character/{character_id}/delete")
async def delete_vtm_character(
    request: Request,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Delete a VTM character - Storyteller only"""
    user = require_storyteller(request)

    # Get character (no ownership check - storyteller can delete any character)
    character = db.query(VTMCharacter).filter(
        VTMCharacter.id == character_id
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

    # Delete character (cascade will handle touchstones, backgrounds, disciplines, xp_log)
    db.delete(character)
    db.commit()

    return RedirectResponse(url="/storyteller/dashboard", status_code=303)


@router.post("/htr/character/{character_id}/delete")
async def delete_htr_character(
    request: Request,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Delete an HTR character - Storyteller only"""
    user = require_storyteller(request)

    # Get character (no ownership check - storyteller can delete any character)
    character = db.query(HTRCharacter).filter(
        HTRCharacter.id == character_id
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

    # Delete character (cascade will handle touchstones, advantages, flaws, edges, perks, xp_log)
    db.delete(character)
    db.commit()

    return RedirectResponse(url="/storyteller/dashboard", status_code=303)
