"""Input sanitization to prevent XSS attacks

This module provides utilities to sanitize user input before storing in database.
Prevents stored XSS vulnerabilities from malicious scripts in character data.
"""

import html
import re
from typing import Any, Dict, List, Optional, Union


# Fields that allow limited HTML (currently none, but extensible)
RICH_TEXT_FIELDS = set()

# Fields that should preserve newlines (converted to <br> for display)
MULTILINE_FIELDS = {
    'history', 'notes', 'current_mission', 'first_encounter',
    'description', 'desire', 'ambition', 'background',
    'history_in_life', 'after_death'
}

# Maximum lengths for different field types (prevent DOS via large inputs)
MAX_LENGTHS = {
    'name': 100,
    'chronicle': 100,
    'concept': 200,
    'predator': 100,
    'clan': 50,
    'sire': 100,
    'generation': 20,
    'description': 5000,
    'history': 10000,
    'notes': 10000,
    'ambition': 1000,
    'desire': 1000,
    'blood_type': 10,
    'pronouns': 50,
    'origin': 100,
    'cell': 100,
    'creed': 50,
    'drive': 50,
}


def sanitize_string(value: str, field_name: Optional[str] = None) -> str:
    """
    Sanitize a string value to prevent XSS attacks

    NOTE: We do NOT html.escape here because:
    1. Jinja2 auto-escapes all template variables by default
    2. Escaping on storage causes double-escaping on every save cycle
    3. We only need to remove dangerous characters, not escape HTML entities

    Args:
        value: The string to sanitize
        field_name: Optional field name for context-aware sanitization

    Returns:
        Sanitized string safe for storage
    """
    if not isinstance(value, str):
        return str(value)

    sanitized = value

    # Apply max length if defined for this field
    if field_name and field_name in MAX_LENGTHS:
        max_len = MAX_LENGTHS[field_name]
        if len(sanitized) > max_len:
            sanitized = sanitized[:max_len]

    # Remove dangerous characters for XSS prevention
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')

    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)

    # Remove script tags (case-insensitive) to prevent XSS
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'<iframe[^>]*>.*?</iframe>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)

    # Remove javascript: and data: protocols from potential URLs
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'data:text/html', '', sanitized, flags=re.IGNORECASE)

    # Remove on* event handlers (onclick, onerror, etc.)
    sanitized = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)

    return sanitized


def sanitize_dict(data: Dict[str, Any], allowed_fields: Optional[set] = None) -> Dict[str, Any]:
    """
    Recursively sanitize a dictionary of user input

    Args:
        data: Dictionary to sanitize
        allowed_fields: If provided, only these fields are kept (whitelist)

    Returns:
        Sanitized dictionary
    """
    sanitized = {}

    for key, value in data.items():
        # Skip if field not in whitelist
        if allowed_fields is not None and key not in allowed_fields:
            continue

        # Sanitize based on type
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value, field_name=key)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, allowed_fields=None)
        elif isinstance(value, list):
            sanitized[key] = sanitize_list(value)
        elif isinstance(value, (int, float, bool)) or value is None:
            # Numbers, booleans, and None are safe
            sanitized[key] = value
        else:
            # Convert to string and sanitize for safety
            sanitized[key] = sanitize_string(str(value), field_name=key)

    return sanitized


def sanitize_list(data: List[Any]) -> List[Any]:
    """
    Sanitize a list of values

    Args:
        data: List to sanitize

    Returns:
        Sanitized list
    """
    sanitized = []

    for item in data:
        if isinstance(item, str):
            sanitized.append(sanitize_string(item))
        elif isinstance(item, dict):
            sanitized.append(sanitize_dict(item))
        elif isinstance(item, list):
            sanitized.append(sanitize_list(item))
        elif isinstance(item, (int, float, bool)) or item is None:
            sanitized.append(item)
        else:
            sanitized.append(sanitize_string(str(item)))

    return sanitized


def sanitize_character_data(data: Dict[str, Any], game_type: str = 'vtm') -> Dict[str, Any]:
    """
    Sanitize character creation/update data

    This is the main function to use for character data sanitization.
    Whitelists allowed fields and sanitizes values.

    Args:
        data: Raw character data from user
        game_type: 'vtm' or 'htr' for game-specific field validation

    Returns:
        Sanitized character data safe for database storage
    """
    # Define allowed fields per game type
    vtm_fields = {
        # Basic Info
        'name', 'concept', 'chronicle', 'predator', 'clan', 'generation',
        'sire', 'ambition', 'desire', 'alias',

        # Identity & Appearance
        'pronouns', 'ethnicity', 'languages', 'birthplace',
        'apparent_age', 'true_age', 'date_of_birth', 'date_of_death',
        'appearance', 'distinguishing_features',

        # Bane & Compulsion
        'bane_type', 'bane_custom', 'compulsion', 'compulsion_custom',

        # Attributes
        'strength', 'dexterity', 'stamina',
        'charisma', 'manipulation', 'composure',
        'intelligence', 'wits', 'resolve',

        # Skills
        'athletics', 'brawl', 'craft', 'drive', 'firearms', 'larceny',
        'melee', 'stealth', 'survival', 'animal_ken', 'etiquette', 'insight',
        'intimidation', 'leadership', 'performance', 'persuasion', 'streetwise',
        'subterfuge', 'academics', 'awareness', 'finance', 'investigation',
        'medicine', 'occult', 'politics', 'science', 'technology',

        # Skills data
        'skill_specialties',

        # Trackers
        'health_max', 'health_superficial', 'health_aggravated',
        'willpower_max', 'willpower_superficial', 'willpower_aggravated',
        'humanity_current', 'humanity_stained', 'hunger',

        # Blood Potency
        'blood_potency',

        # Disciplines (relationships handled separately)
        'discipline_1_name', 'discipline_1_level', 'discipline_1_powers', 'discipline_1_description',
        'discipline_2_name', 'discipline_2_level', 'discipline_2_powers', 'discipline_2_description',
        'discipline_3_name', 'discipline_3_level', 'discipline_3_powers', 'discipline_3_description',
        'discipline_4_name', 'discipline_4_level', 'discipline_4_powers', 'discipline_4_description',
        'discipline_5_name', 'discipline_5_level', 'discipline_5_powers', 'discipline_5_description',

        # Chronicle Tenets
        'chronicle_tenet_1', 'chronicle_tenet_2', 'chronicle_tenet_3',
        'chronicle_tenet_4', 'chronicle_tenet_5',

        # Portraits
        'portrait_face', 'portrait_body',
        'portrait_hobby_1', 'portrait_hobby_2', 'portrait_hobby_3', 'portrait_hobby_4',

        # Text fields
        'history_in_life', 'after_death', 'notes',

        # Experience
        'exp_total', 'exp_available', 'exp_spent',

        # Relationships (handled separately but fields for reference)
        'touchstones', 'backgrounds', 'disciplines', 'xp_log',

        # Resonance
        'resonance',
    }

    htr_fields = {
        # Basic Info
        'name', 'chronicle', 'cell', 'creed', 'drive', 'desire', 'ambition',

        # Identity
        'age', 'blood_type', 'pronouns', 'origin', 'alias',

        # Attributes
        'strength', 'dexterity', 'stamina',
        'charisma', 'manipulation', 'composure',
        'intelligence', 'wits', 'resolve',

        # Skills
        'athletics', 'brawl', 'craft', 'drive_skill', 'firearms', 'larceny',
        'melee', 'stealth', 'survival', 'animal_ken', 'etiquette', 'insight',
        'intimidation', 'leadership', 'performance', 'persuasion', 'streetwise',
        'subterfuge', 'academics', 'awareness', 'finance', 'investigation',
        'medicine', 'occult', 'politics', 'science', 'technology',

        # Skills data
        'skill_specialties',

        # Trackers
        'danger_current', 'desperation_current', 'in_despair',
        'health_max', 'health_superficial', 'health_aggravated',
        'willpower_max', 'willpower_superficial', 'willpower_aggravated',

        # Portraits
        'portrait_face', 'portrait_body',
        'portrait_hobby_1', 'portrait_hobby_2', 'portrait_hobby_3', 'portrait_hobby_4',

        # Text fields
        'first_encounter', 'history', 'notes', 'current_mission',

        # Experience
        'exp_total', 'exp_available', 'exp_spent',

        # Relationships
        'touchstones', 'advantages', 'flaws', 'equipment', 'xp_log', 'edges', 'perks',

        # Equipment
        'equipment_weapon', 'equipment_weapon_damage', 'equipment_armor_rating', 'equipment_notes',
    }

    allowed_fields = vtm_fields if game_type == 'vtm' else htr_fields

    # Sanitize with whitelist
    return sanitize_dict(data, allowed_fields=allowed_fields)


# Convenience function for API routes
def sanitize_input(data: Union[Dict, List, str], field_name: Optional[str] = None) -> Any:
    """
    General-purpose sanitization for any input type

    Args:
        data: Input data to sanitize
        field_name: Optional field name for context

    Returns:
        Sanitized data
    """
    if isinstance(data, dict):
        return sanitize_dict(data)
    elif isinstance(data, list):
        return sanitize_list(data)
    elif isinstance(data, str):
        return sanitize_string(data, field_name=field_name)
    else:
        return data
