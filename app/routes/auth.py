"""Authentication routes - Discord OAuth"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth import oauth, get_discord_user
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login")
async def login(request: Request):
    """Initiate Discord OAuth flow"""
    redirect_uri = request.url_for('auth_callback')
    return await oauth.discord.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Discord OAuth callback"""
    try:
        # Get access token from Discord
        token = await oauth.discord.authorize_access_token(request)
        
        # Fetch user info from Discord
        discord_user = await get_discord_user(token)
        
        if not discord_user:
            return RedirectResponse(url="/?error=auth_failed")
        
        # Check if user exists in database
        user = db.query(User).filter(User.discord_id == discord_user['id']).first()
        
        if not user:
            # Create new user
            user = User(
                discord_id=discord_user['id'],
                discord_username=f"{discord_user['username']}#{discord_user['discriminator']}",
                discord_avatar=discord_user.get('avatar')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user info
            user.discord_username = f"{discord_user['username']}#{discord_user['discriminator']}"
            user.discord_avatar = discord_user.get('avatar')
            db.commit()
        
        # Store user in session
        request.session['user'] = {
            'id': user.id,
            'discord_id': user.discord_id,
            'username': user.discord_username,
            'avatar': user.discord_avatar
        }
        
        # Redirect to main page
        return RedirectResponse(url="/")
        
    except Exception as e:
        print(f"Auth callback error: {e}")
        return RedirectResponse(url="/?error=auth_failed")


@router.get("/logout")
async def logout(request: Request):
    """Log out user"""
    request.session.clear()
    return RedirectResponse(url="/")
