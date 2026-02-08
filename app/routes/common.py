"""Shared route helpers for all game types.

Extracts common patterns (portrait upload, delete, export, serialization)
to avoid duplication across VTM, HTR, and future game type routes.
"""

import json
from io import BytesIO
from typing import Optional, List
from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.constants import MAX_UPLOAD_SIZE, ALLOWED_IMAGE_EXTENSIONS, VALID_PORTRAIT_BOXES
from app.exceptions import (
    CharacterNotFound,
    ImageUploadError,
    validate_file_size,
    validate_file_extension,
    validate_image_type
)
from app.utils import process_and_save_portrait, delete_portrait
from app.export_utils import export_character_sheet, sanitize_filename

logger = get_logger(__name__)


def serialize_model_to_dict(model_instance) -> dict:
    """Convert a SQLAlchemy model instance to a dict with datetime handling.

    Iterates over the model's columns and converts datetime values
    to ISO format strings for JSON serialization.
    """
    result = {}
    for c in model_instance.__table__.columns:
        value = getattr(model_instance, c.name)
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        result[c.name] = value
    return result


def delete_character_portraits(character) -> None:
    """Delete all portrait files associated with a character."""
    portrait_fields = [
        'portrait_face', 'portrait_body',
        'portrait_hobby_1', 'portrait_hobby_2',
        'portrait_hobby_3', 'portrait_hobby_4'
    ]
    for field in portrait_fields:
        url = getattr(character, field, None)
        if url:
            delete_portrait(url)


async def handle_portrait_upload(
    character,
    file: Optional[UploadFile],
    box_type: str,
    db: Session
) -> JSONResponse:
    """Process a portrait upload for any character type.

    Validates the file, processes the image, saves it, and updates the
    character model. Returns a JSONResponse.
    """
    if box_type not in VALID_PORTRAIT_BOXES:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid box type"}
        )

    if not file:
        return JSONResponse(
            status_code=400,
            content={"error": "No file provided"}
        )

    validate_image_type(file.content_type)
    validate_file_extension(file.filename, ALLOWED_IMAGE_EXTENSIONS)

    file_content = await file.read()
    validate_file_size(len(file_content), MAX_UPLOAD_SIZE)

    try:
        old_portrait = getattr(character, f'portrait_{box_type}', None)
        if old_portrait:
            delete_portrait(old_portrait)

        portrait_url = process_and_save_portrait(
            BytesIO(file_content),
            file.filename,
            box_type
        )

        setattr(character, f'portrait_{box_type}', portrait_url)
        db.commit()

        logger.debug(f"Character {character.id}: Set portrait_{box_type} = {portrait_url}")

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


async def handle_export_png(
    character,
    game_type: str,
    request: Request
) -> Response:
    """Export a character sheet as PNG for any game type.

    Uses Playwright to render the character sheet page and capture a screenshot.
    """
    base_url = str(request.base_url).rstrip('/')
    character_url = f"{base_url}/{game_type}/character/{character.id}"

    cookies = []
    for cookie_name, cookie_value in request.cookies.items():
        cookies.append({
            'name': cookie_name,
            'value': cookie_value,
            'domain': request.url.hostname or 'localhost',
            'path': '/'
        })

    png_bytes = await export_character_sheet(
        url=character_url,
        format='png',
        character_name=character.name or "Unnamed Character",
        cookies=cookies
    )

    safe_name = sanitize_filename(character.name or "character")
    filename = f"{safe_name}_{game_type}_sheet.png"

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


def parse_request_data(data: dict) -> dict:
    """Parse XP log data from string to list if needed.

    Common pattern used by both create and update routes.
    """
    xp_log_data = data.get('xp_log', '[]')
    if isinstance(xp_log_data, str):
        try:
            data['xp_log'] = json.loads(xp_log_data)
        except (json.JSONDecodeError, ValueError):
            data['xp_log'] = []
    return data
