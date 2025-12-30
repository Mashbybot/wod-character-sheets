"""Error handling utilities and custom exceptions"""

from typing import Optional, List, Dict, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import traceback

from app.schemas import ErrorResponse, ErrorDetail
from app.logging_config import get_logger

logger = get_logger(__name__)


# ===== CUSTOM EXCEPTIONS =====

class WoDException(Exception):
    """Base exception for World of Darkness application"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[List[Dict[str, Any]]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or []
        super().__init__(self.message)


class CharacterLimitReached(WoDException):
    """Raised when user tries to create too many characters"""
    def __init__(self, limit: int):
        super().__init__(
            message=f"Character limit reached. You can have up to {limit} characters per game line.",
            status_code=400,
            details=[{
                "field": "character_count",
                "message": f"Maximum {limit} characters allowed",
                "type": "limit_exceeded"
            }]
        )


class CharacterNotFound(WoDException):
    """Raised when character doesn't exist or user doesn't own it"""
    def __init__(self, character_id: int):
        super().__init__(
            message=f"Character not found or you don't have permission to access it.",
            status_code=404,
            details=[{
                "field": "character_id",
                "message": f"Character {character_id} not found",
                "type": "not_found"
            }]
        )


class ImageUploadError(WoDException):
    """Raised when image upload fails"""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Image upload failed: {reason}",
            status_code=400,
            details=[{
                "field": "file",
                "message": reason,
                "type": "upload_error"
            }]
        )


class InvalidDataError(WoDException):
    """Raised when data validation fails"""
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Invalid data: {message}",
            status_code=400,
            details=[{
                "field": field,
                "message": message,
                "type": "validation_error"
            }]
        )


# ===== ERROR HANDLERS =====

async def wod_exception_handler(request: Request, exc: WoDException) -> JSONResponse:
    """Handle custom WoD exceptions"""
    error_details = [
        ErrorDetail(
            field=detail.get("field"),
            message=detail.get("message", ""),
            type=detail.get("type")
        )
        for detail in exc.details
    ]
    
    error_response = ErrorResponse(
        error=exc.message,
        details=error_details if error_details else None,
        status_code=exc.status_code
    )
    
    # Log the error
    logger.warning(f"WoD Exception: {exc.message} (status={exc.status_code})")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    error_details = []
    
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        error_details.append(
            ErrorDetail(
                field=field,
                message=error["msg"],
                type=error["type"]
            )
        )
    
    error_response = ErrorResponse(
        error="Validation error",
        details=error_details,
        status_code=422
    )
    
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors"""
    logger.error(f"Database error: {str(exc)}")
    logger.error(traceback.format_exc())
    
    # Check for specific error types
    if isinstance(exc, IntegrityError):
        error_message = "Database integrity error. This might be due to duplicate data or invalid relationships."
    else:
        error_message = "A database error occurred. Please try again later."
    
    error_response = ErrorResponse(
        error=error_message,
        status_code=500
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}")
    logger.error(traceback.format_exc())
    
    error_response = ErrorResponse(
        error="An unexpected error occurred. Please try again later.",
        status_code=500
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


# ===== USER-FRIENDLY ERROR MESSAGES =====

ERROR_MESSAGES = {
    # Character errors
    "character_limit_reached": "You've reached the maximum number of characters. Delete one to create a new character.",
    "character_not_found": "Character not found. It may have been deleted or you don't have permission to access it.",
    "character_save_failed": "Failed to save character. Please try again.",
    
    # Image upload errors
    "invalid_image_type": "Invalid image type. Please upload a PNG, JPG, GIF, or WebP file.",
    "image_too_large": "Image file is too large. Maximum size is 10MB.",
    "image_upload_failed": "Failed to upload image. Please try again.",
    
    # Auth errors
    "not_authenticated": "You need to log in to access this feature.",
    "session_expired": "Your session has expired. Please log in again.",
    
    # Data validation errors
    "invalid_attribute_value": "Attribute values must be between 1 and 5.",
    "invalid_skill_value": "Skill values must be between 0 and 5.",
    "invalid_blood_potency": "Blood Potency must be between 0 and 10.",
    "invalid_hunger": "Hunger must be between 0 and 5.",
    "invalid_health_damage": "Total health damage cannot exceed maximum health.",
    "invalid_willpower_damage": "Total willpower damage cannot exceed maximum willpower.",
    "invalid_column_widths": "Column widths must be three percentages that sum to 100.",
    
    # Generic errors
    "server_error": "An unexpected error occurred. Our team has been notified.",
    "database_error": "A database error occurred. Please try again later.",
}


def get_user_friendly_error(error_key: str, **kwargs) -> str:
    """Get a user-friendly error message with optional formatting"""
    message = ERROR_MESSAGES.get(error_key, ERROR_MESSAGES["server_error"])
    return message.format(**kwargs) if kwargs else message


# ===== VALIDATION HELPERS =====

def validate_character_ownership(character_user_id: int, current_user_id: int) -> None:
    """Validate that the current user owns the character"""
    if character_user_id != current_user_id:
        raise CharacterNotFound(character_id=0)  # Don't reveal actual ID


def validate_file_size(file_size: int, max_size: int) -> None:
    """Validate file size"""
    if file_size > max_size:
        raise ImageUploadError(get_user_friendly_error("image_too_large"))


def validate_file_extension(filename: str, allowed_extensions: set) -> None:
    """Validate file extension"""
    if '.' not in filename:
        raise ImageUploadError(get_user_friendly_error("invalid_image_type"))
    
    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        raise ImageUploadError(get_user_friendly_error("invalid_image_type"))


def validate_image_type(content_type: str) -> None:
    """Validate image content type"""
    if not content_type.startswith('image/'):
        raise ImageUploadError(get_user_friendly_error("invalid_image_type"))
