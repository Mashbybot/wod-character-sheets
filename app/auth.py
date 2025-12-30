"""Discord OAuth authentication"""

import os
from typing import Optional
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request

from app.logging_config import get_logger

logger = get_logger(__name__)

# OAuth configuration
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "")

# Validate all OAuth credentials are set
if not all([DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_REDIRECT_URI]):
    raise ValueError(
        "Discord OAuth configuration incomplete. Required environment variables: "
        "DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_REDIRECT_URI"
    )

config = Config(environ={
    "DISCORD_CLIENT_ID": DISCORD_CLIENT_ID,
    "DISCORD_CLIENT_SECRET": DISCORD_CLIENT_SECRET,
    "DISCORD_REDIRECT_URI": DISCORD_REDIRECT_URI,
})

oauth = OAuth(config)

# Register Discord OAuth
oauth.register(
    name='discord',
    client_id=config('DISCORD_CLIENT_ID'),
    client_secret=config('DISCORD_CLIENT_SECRET'),
    authorize_url='https://discord.com/api/oauth2/authorize',
    authorize_params={'scope': 'identify'},  # Just need basic identity
    access_token_url='https://discord.com/api/oauth2/token',
    access_token_params=None,
    userinfo_endpoint='https://discord.com/api/users/@me',
    client_kwargs={'scope': 'identify'},
)


async def get_discord_user(token: dict) -> Optional[dict]:
    """Fetch Discord user information using access token"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token['access_token']}"
            }
            response = await client.get(
                "https://discord.com/api/users/@me",
                headers=headers
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logger.error(f"Error fetching Discord user: {e}")
    return None


def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session"""
    return request.session.get('user')


def require_auth(request: Request) -> dict:
    """Require authentication, raise 401 if not authenticated"""
    user = get_current_user(request)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
