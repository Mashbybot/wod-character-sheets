"""Authentication routes - Discord OAuth"""

import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.auth import oauth, get_discord_user
from app.database import get_db
from app.models_new import User
from app.audit import log_login, get_client_ip

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login")
async def login(request: Request):
    """Initiate Discord OAuth flow"""
    redirect_uri = os.getenv("DISCORD_REDIRECT_URI")
    logger.info(f"Starting login flow with redirect_uri: {redirect_uri}")
    return await oauth.discord.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Discord OAuth callback"""
    try:
        logger.info("OAuth callback received, getting token")

        # Get access token from Discord
        token = await oauth.discord.authorize_access_token(request)
        logger.info(f"Token received: {bool(token)}")

        # Fetch user info from Discord
        discord_user = await get_discord_user(token)
        logger.debug(f"Discord user data: {discord_user}")

        if not discord_user:
            logger.error("Failed to get Discord user data")
            return RedirectResponse(url="/?error=auth_failed")

        # Discord deprecated discriminators - handle both old and new format
        # New format: discriminator is "0" or might not exist
        # Old format: discriminator is "1234"
        discriminator = discord_user.get('discriminator', '0')
        if discriminator == '0':
            # New Discord username system (no discriminator)
            username = discord_user['username']
        else:
            # Old Discord username system (with discriminator)
            username = f"{discord_user['username']}#{discriminator}"

        logger.info(f"Processing user: {username} (Discord ID: {discord_user['id']})")

        # Check if user exists in database
        user = db.query(User).filter(User.discord_id == discord_user['id']).first()

        if not user:
            # Create new user
            logger.info(f"Creating new user: {username}")
            user = User(
                discord_id=discord_user['id'],
                discord_username=username,
                discord_avatar=discord_user.get('avatar')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User created with ID: {user.id}")
        else:
            # Update existing user info
            logger.info(f"Updating existing user ID: {user.id}")
            user.discord_username = username
            user.discord_avatar = discord_user.get('avatar')
            db.commit()

        # Store user in session (including role for authorization)
        session_data = {
            'id': user.id,
            'discord_id': user.discord_id,
            'username': user.discord_username,
            'avatar': user.discord_avatar,
            'role': user.role
        }
        request.session['user'] = session_data

        # Log successful login
        log_login(
            db=db,
            user_id=user.id,
            username=username,
            success=True,
            ip_address=get_client_ip(request)
        )

        # Redirect to main page
        logger.info("Authentication successful, redirecting to home page")
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        logger.error(f"Auth callback error: {type(e).__name__}: {e}", exc_info=True)
        return RedirectResponse(url="/?error=auth_failed", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    """Log out user"""
    logger.info("Logging out user")
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
