"""CSRF Protection for WoD Character Sheets"""
import os
import json
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

# CSRF token serializer
csrf_serializer = None


def init_csrf(secret_key: str):
    """Initialize CSRF protection with the application's secret key"""
    global csrf_serializer
    csrf_serializer = URLSafeTimedSerializer(secret_key, salt="csrf-token")


def generate_csrf_token() -> str:
    """Generate a new CSRF token"""
    if csrf_serializer is None:
        raise RuntimeError("CSRF protection not initialized. Call init_csrf() first.")
    # Use a simple random value - the signature provides the security
    import secrets
    token_data = secrets.token_urlsafe(32)
    return csrf_serializer.dumps(token_data)


def validate_csrf_token(token: str, max_age: int = 3600) -> bool:
    """
    Validate a CSRF token

    Args:
        token: The CSRF token to validate
        max_age: Maximum age of token in seconds (default 1 hour)

    Returns:
        True if token is valid, False otherwise
    """
    if csrf_serializer is None:
        raise RuntimeError("CSRF protection not initialized. Call init_csrf() first.")

    try:
        csrf_serializer.loads(token, max_age=max_age)
        return True
    except (BadSignature, SignatureExpired):
        return False


async def get_csrf_token(request: Request) -> str:
    """
    Get CSRF token from request session, creating one if it doesn't exist

    Args:
        request: The FastAPI request object

    Returns:
        The CSRF token
    """
    csrf_token = request.session.get("csrf_token")

    if not csrf_token or not validate_csrf_token(csrf_token):
        csrf_token = generate_csrf_token()
        request.session["csrf_token"] = csrf_token

    return csrf_token


async def validate_csrf(request: Request, exempt: bool = False) -> None:
    """
    Validate CSRF token from request

    Args:
        request: The FastAPI request object
        exempt: If True, skip CSRF validation (for exempt endpoints)

    Raises:
        HTTPException: If CSRF validation fails
    """
    if exempt:
        return

    # Skip CSRF for safe methods
    if request.method in ["GET", "HEAD", "OPTIONS", "TRACE"]:
        return

    # Get token from session
    session_token = request.session.get("csrf_token")
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing from session"
        )

    # Get token from request (header or form data)
    request_token = None

    # Try to get from header first
    request_token = request.headers.get("X-CSRF-Token")

    # If not in header, try form data
    if not request_token:
        try:
            form_data = await request.form()
            request_token = form_data.get("csrf_token")
        except:
            pass

    # If still not found, try JSON body (for API requests)
    if not request_token:
        try:
            # We need to be careful here to not consume the body
            # This is a simplified version - in production, consider middleware
            body = await request.body()
            if body:
                import json
                try:
                    json_data = json.loads(body)
                    request_token = json_data.get("csrf_token")
                except:
                    pass
        except:
            pass

    if not request_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing from request"
        )

    # Validate the token
    if session_token != request_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token validation failed"
        )

    # Validate token signature and expiry
    if not validate_csrf_token(request_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token expired or invalid"
        )


# FastAPI dependency for CSRF protection
async def require_csrf(request: Request) -> None:
    """
    FastAPI dependency to require CSRF validation on a route.

    Usage:
        @app.post("/some-route", dependencies=[Depends(require_csrf)])
        async def protected_route():
            ...

    Raises:
        HTTPException: If CSRF validation fails
    """
    await validate_csrf(request, exempt=False)
