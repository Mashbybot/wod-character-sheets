"""Utility functions for common operations"""

import os
import uuid
from typing import Dict, Any, Optional, Tuple
from PIL import Image
from datetime import datetime

from app.constants import (
    BLOOD_POTENCY_VALUES,
    CLAN_DISCIPLINES,
    PORTRAIT_SIZES,
    CHARACTER_IMAGE_DIR,
    MAX_UPLOAD_SIZE,
    ALLOWED_IMAGE_EXTENSIONS
)
from app.exceptions import ImageUploadError, validate_file_extension, validate_file_size


# ===== BLOOD POTENCY CALCULATIONS =====

def calculate_blood_potency_values(blood_potency: int) -> Dict[str, Any]:
    """Calculate all Blood Potency derived values"""
    bp = max(0, min(10, blood_potency))  # Clamp to 0-10
    return BLOOD_POTENCY_VALUES.get(bp, BLOOD_POTENCY_VALUES[0])


# ===== CLAN UTILITIES =====

def get_clan_disciplines(clan: str) -> list:
    """Get the disciplines for a given clan"""
    return CLAN_DISCIPLINES.get(clan.lower(), [])


def format_discipline_name(discipline: str) -> str:
    """Format discipline name for display (capitalize, replace hyphens)"""
    return discipline.replace('-', ' ').title()


# ===== GENERATION UTILITIES =====

def get_generation_ordinal(generation: int) -> str:
    """Get ordinal string for generation (e.g., 13 -> '13th')"""
    num = int(generation)
    last_digit = num % 10
    last_two_digits = num % 100
    
    if last_two_digits >= 11 and last_two_digits <= 13:
        return f"{num}th"
    
    if last_digit == 1:
        return f"{num}st"
    elif last_digit == 2:
        return f"{num}nd"
    elif last_digit == 3:
        return f"{num}rd"
    else:
        return f"{num}th"


# ===== IMAGE PROCESSING =====

def process_and_save_portrait(
    image_file,
    filename: str,
    box_type: str = 'face'
) -> str:
    """
    Process and save a portrait image
    
    Args:
        image_file: The uploaded file object
        filename: Original filename
        box_type: Type of portrait box ('face', 'body', or 'hobby')
    
    Returns:
        URL path to the saved image
    
    Raises:
        ImageUploadError: If processing fails
    """
    # Validate file
    validate_file_extension(filename, ALLOWED_IMAGE_EXTENSIONS)
    
    # Determine target size based on box type
    if box_type == 'body':
        target_size = PORTRAIT_SIZES['body']
    elif box_type.startswith('hobby'):
        target_size = PORTRAIT_SIZES['hobby']
    else:  # face or default
        target_size = PORTRAIT_SIZES['face']
    
    try:
        # Generate unique filename
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(CHARACTER_IMAGE_DIR, unique_filename)

        # Security: Verify path is within allowed directory (prevent path traversal)
        from pathlib import Path
        real_file_path = Path(file_path).resolve()
        real_image_dir = Path(CHARACTER_IMAGE_DIR).resolve()

        if not str(real_file_path).startswith(str(real_image_dir)):
            raise ImageUploadError("Invalid file path detected")

        # Ensure directory exists
        os.makedirs(CHARACTER_IMAGE_DIR, exist_ok=True)
        
        # Open and process image
        image = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary (for JPEG)
        if image.mode == 'RGBA' and file_extension in ['jpg', 'jpeg']:
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        
        # Resize image maintaining aspect ratio
        image.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Save optimized image
        image.save(file_path, optimize=True, quality=85)

        # Return URL path (mounted at /portraits in main.py)
        return f"/portraits/{unique_filename}"
        
    except Exception as e:
        raise ImageUploadError(f"Failed to process image: {str(e)}")


def delete_portrait(portrait_url: Optional[str], db=None, character_id: Optional[int] = None) -> None:
    """
    Delete a portrait image file if it exists

    Args:
        portrait_url: URL of the portrait to delete
        db: Database session (optional, for ownership verification)
        character_id: Character ID that should own this portrait (optional, for ownership verification)

    Note:
        If db and character_id are provided, ownership verification is performed.
        This provides defense-in-depth against unauthorized deletions.
    """
    if not portrait_url:
        return

    # Optional ownership verification (defense-in-depth)
    if db is not None and character_id is not None:
        from app.models_new import VTMCharacter, HTRCharacter

        # Check if this portrait belongs to the specified character
        portrait_found = False

        # Check VTM characters
        vtm_char = db.query(VTMCharacter).filter(VTMCharacter.id == character_id).first()
        if vtm_char:
            portrait_fields = ['portrait_face', 'portrait_body', 'portrait_hobby_1',
                             'portrait_hobby_2', 'portrait_hobby_3', 'portrait_hobby_4']
            for field in portrait_fields:
                if getattr(vtm_char, field, None) == portrait_url:
                    portrait_found = True
                    break

        # Check HTR characters if not found
        if not portrait_found:
            htr_char = db.query(HTRCharacter).filter(HTRCharacter.id == character_id).first()
            if htr_char:
                portrait_fields = ['portrait_face', 'portrait_body', 'portrait_hobby_1',
                                 'portrait_hobby_2', 'portrait_hobby_3', 'portrait_hobby_4']
                for field in portrait_fields:
                    if getattr(htr_char, field, None) == portrait_url:
                        portrait_found = True
                        break

        # If ownership verification was requested but failed, don't delete
        if not portrait_found:
            print(f"Warning: Portrait ownership verification failed for {portrait_url}, character {character_id}")
            return

    try:
        # Extract filename from URL
        filename = portrait_url.split('/')[-1]
        file_path = os.path.join(CHARACTER_IMAGE_DIR, filename)

        # Additional security: ensure the path is within CHARACTER_IMAGE_DIR
        # Prevent path traversal attacks
        real_file_path = os.path.realpath(file_path)
        real_image_dir = os.path.realpath(CHARACTER_IMAGE_DIR)

        if not real_file_path.startswith(real_image_dir):
            print(f"Security: Attempted path traversal detected in portrait deletion: {portrait_url}")
            return

        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log but don't raise - file cleanup is not critical
        print(f"Warning: Failed to delete portrait {portrait_url}: {e}")


# ===== SKILL SPECIALTY UTILITIES =====

def parse_skill_specialties(specialties_str: Optional[str]) -> Dict[str, list]:
    """
    Parse skill specialties string into dictionary
    
    Args:
        specialties_str: Comma-separated string like "athletics:running,academics:history"
    
    Returns:
        Dict mapping skill names to lists of specialties
    """
    if not specialties_str:
        return {}
    
    result = {}
    for spec in specialties_str.split(','):
        spec = spec.strip()
        if ':' in spec:
            skill, specialty = spec.split(':', 1)
            if skill not in result:
                result[skill] = []
            result[skill].append(specialty)
    
    return result


def format_skill_specialties(specialties_dict: Dict[str, list]) -> str:
    """
    Format skill specialties dictionary into string
    
    Args:
        specialties_dict: Dict mapping skill names to lists of specialties
    
    Returns:
        Comma-separated string like "athletics:running,academics:history"
    """
    if not specialties_dict:
        return ""
    
    parts = []
    for skill, specs in specialties_dict.items():
        for spec in specs:
            parts.append(f"{skill}:{spec}")
    
    return ','.join(parts)


def get_skill_specialties(specialties_str: Optional[str], skill: str) -> list:
    """Get specialties for a specific skill"""
    all_specs = parse_skill_specialties(specialties_str)
    return all_specs.get(skill, [])


def add_skill_specialty(specialties_str: Optional[str], skill: str, specialty: str) -> str:
    """Add a specialty to a skill"""
    all_specs = parse_skill_specialties(specialties_str)
    if skill not in all_specs:
        all_specs[skill] = []
    if specialty not in all_specs[skill]:
        all_specs[skill].append(specialty)
    return format_skill_specialties(all_specs)


def remove_skill_specialty(specialties_str: Optional[str], skill: str, specialty: str) -> str:
    """Remove a specialty from a skill"""
    all_specs = parse_skill_specialties(specialties_str)
    if skill in all_specs and specialty in all_specs[skill]:
        all_specs[skill].remove(specialty)
        if not all_specs[skill]:
            del all_specs[skill]
    return format_skill_specialties(all_specs)


# ===== EXPERIENCE UTILITIES =====

def calculate_available_xp(total: int, spent: int) -> int:
    """Calculate available XP from total and spent"""
    return max(0, total - spent)


def validate_xp_spend(available: int, amount: int) -> bool:
    """Validate that there's enough XP to spend"""
    return amount <= available and amount > 0


# ===== DATE/TIME UTILITIES =====

def get_current_date_string() -> str:
    """Get current date as ISO format string"""
    return datetime.now().strftime('%Y-%m-%d')


def get_current_datetime_string() -> str:
    """Get current datetime as ISO format string"""
    return datetime.now().isoformat()


# ===== VALIDATION UTILITIES =====

def validate_damage_total(max_value: int, superficial: int, aggravated: int) -> bool:
    """Validate that total damage doesn't exceed maximum"""
    return (superficial + aggravated) <= max_value


def clamp_value(value: int, min_val: int, max_val: int) -> int:
    """Clamp a value between min and max"""
    return max(min_val, min(max_val, value))


# ===== STRING UTILITIES =====

def capitalize_skill_name(skill: str) -> str:
    """Capitalize skill name (handles underscores)"""
    return skill.replace('_', ' ').title()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove any path components
    filename = os.path.basename(filename)
    # Replace spaces and special chars
    filename = filename.replace(' ', '_')
    return filename


# ===== COLUMN WIDTH UTILITIES =====

def parse_column_widths(widths_str: str) -> Tuple[int, int, int]:
    """
    Parse column widths string into tuple of integers
    
    Args:
        widths_str: String like "30,35,35"
    
    Returns:
        Tuple of three integers
    
    Raises:
        ValueError: If format is invalid
    """
    try:
        widths = [int(w.strip()) for w in widths_str.split(',')]
        if len(widths) != 3:
            raise ValueError("Must have exactly 3 column widths")
        if sum(widths) != 100:
            raise ValueError("Column widths must sum to 100")
        if any(w < 10 or w > 70 for w in widths):
            raise ValueError("Each column must be between 10% and 70%")
        return tuple(widths)
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid column width format: {e}")


def format_column_widths(width1: int, width2: int, width3: int) -> str:
    """Format column widths as string"""
    # Ensure they sum to 100
    total = width1 + width2 + width3
    if total != 100:
        # Adjust the third column to make it 100
        width3 = 100 - width1 - width2

    return f"{width1},{width2},{width3}"


# ===== STORYTELLER UTILITIES =====

def is_storyteller(user: Optional[Dict[str, Any]]) -> bool:
    """
    Check if the current user is a storyteller

    Args:
        user: User dict from session (contains discord_id and role)

    Returns:
        True if user is a storyteller or admin, False otherwise
    """
    if not user:
        return False

    # Check database role (preferred method)
    user_role = user.get("role", "player")
    if user_role in ["storyteller", "admin"]:
        return True

    # Fallback: Check environment variable for backward compatibility
    # This allows migration period where roles aren't set yet
    storyteller_id = os.getenv("STORYTELLER_DISCORD_ID", "")
    if storyteller_id:
        user_discord_id = str(user.get("discord_id", ""))
        return user_discord_id == storyteller_id

    return False


def normalize_chronicle_name(chronicle: Optional[str]) -> str:
    """
    Normalize chronicle name for fuzzy matching

    Args:
        chronicle: Chronicle name string

    Returns:
        Normalized lowercase string with extra whitespace removed
    """
    if not chronicle:
        return "uncategorized"

    # Convert to lowercase, strip whitespace, collapse multiple spaces
    normalized = ' '.join(chronicle.lower().strip().split())
    return normalized if normalized else "uncategorized"


def group_characters_by_chronicle(characters: list) -> Dict[str, list]:
    """
    Group characters by normalized chronicle name

    Args:
        characters: List of character objects (VTM or HTR)

    Returns:
        Dict mapping normalized chronicle names to lists of characters
    """
    grouped = {}

    for char in characters:
        # Get chronicle name (works for both VTM and HTR)
        chronicle = getattr(char, 'chronicle', None)
        normalized = normalize_chronicle_name(chronicle)

        if normalized not in grouped:
            grouped[normalized] = []

        grouped[normalized].append(char)

    # Sort chronicles alphabetically, but put "uncategorized" last
    sorted_groups = {}
    for key in sorted(grouped.keys()):
        if key != "uncategorized":
            sorted_groups[key] = grouped[key]

    if "uncategorized" in grouped:
        sorted_groups["uncategorized"] = grouped["uncategorized"]

    return sorted_groups
