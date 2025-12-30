"""Audit logging for security-relevant events

Tracks important user actions and security events for compliance and investigation.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.models_new import AuditLog

logger = get_logger(__name__)


class AuditEvent:
    """Audit event types"""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"

    # Character events
    CHARACTER_CREATE = "character_create"
    CHARACTER_UPDATE = "character_update"
    CHARACTER_DELETE = "character_delete"
    CHARACTER_VIEW = "character_view"

    # Administrative events
    STORYTELLER_DELETE_CHARACTER = "storyteller_delete_character"
    ROLE_CHANGE = "role_change"

    # Security events
    VALIDATION_FAILURE = "validation_failure"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


def log_audit_event(
    db: Session,
    event_type: str,
    user_id: Optional[int] = None,
    target_id: Optional[int] = None,
    target_type: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> None:
    """
    Log an audit event to the database

    Args:
        db: Database session
        event_type: Type of event (use AuditEvent constants)
        user_id: ID of user performing the action (if authenticated)
        target_id: ID of the resource being acted upon
        target_type: Type of resource (e.g., "character", "user")
        details: Additional context as JSON
        ip_address: IP address of the request
    """
    try:
        audit_entry = AuditLog(
            event_type=event_type,
            user_id=user_id,
            target_id=target_id,
            target_type=target_type,
            details=details or {},
            ip_address=ip_address,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(audit_entry)
        db.commit()

        logger.info(
            f"AUDIT: {event_type} | user_id={user_id} | "
            f"target={target_type}:{target_id} | ip={ip_address}"
        )
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}", exc_info=True)
        db.rollback()


def log_character_create(
    db: Session,
    user_id: int,
    character_id: int,
    character_type: str,
    character_name: str,
    ip_address: Optional[str] = None
) -> None:
    """Log character creation"""
    log_audit_event(
        db=db,
        event_type=AuditEvent.CHARACTER_CREATE,
        user_id=user_id,
        target_id=character_id,
        target_type=character_type,
        details={"name": character_name},
        ip_address=ip_address
    )


def log_character_delete(
    db: Session,
    user_id: int,
    character_id: int,
    character_type: str,
    character_name: str,
    deleted_by_storyteller: bool = False,
    ip_address: Optional[str] = None
) -> None:
    """Log character deletion"""
    event_type = (
        AuditEvent.STORYTELLER_DELETE_CHARACTER
        if deleted_by_storyteller
        else AuditEvent.CHARACTER_DELETE
    )

    log_audit_event(
        db=db,
        event_type=event_type,
        user_id=user_id,
        target_id=character_id,
        target_type=character_type,
        details={
            "name": character_name,
            "deleted_by_storyteller": deleted_by_storyteller
        },
        ip_address=ip_address
    )


def log_login(
    db: Session,
    user_id: int,
    username: str,
    success: bool,
    ip_address: Optional[str] = None,
    failure_reason: Optional[str] = None
) -> None:
    """Log login attempt"""
    event_type = AuditEvent.LOGIN_SUCCESS if success else AuditEvent.LOGIN_FAILURE

    details = {"username": username}
    if failure_reason:
        details["reason"] = failure_reason

    log_audit_event(
        db=db,
        event_type=event_type,
        user_id=user_id if success else None,
        details=details,
        ip_address=ip_address
    )


def log_unauthorized_access(
    db: Session,
    user_id: Optional[int],
    resource_type: str,
    resource_id: int,
    ip_address: Optional[str] = None
) -> None:
    """Log unauthorized access attempt"""
    log_audit_event(
        db=db,
        event_type=AuditEvent.UNAUTHORIZED_ACCESS,
        user_id=user_id,
        target_id=resource_id,
        target_type=resource_type,
        ip_address=ip_address
    )


def get_client_ip(request) -> Optional[str]:
    """
    Extract client IP address from request

    Handles proxied requests (X-Forwarded-For header)
    """
    # Try to get real IP from proxy headers
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can be comma-separated list, first is client
        return forwarded.split(",")[0].strip()

    # Fallback to direct connection
    if request.client:
        return request.client.host

    return None
