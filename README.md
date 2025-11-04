# World of Darkness Character Sheets

A web application for managing World of Darkness character sheets across multiple game lines.

## Currently Supported
- **Vampire: The Masquerade 5th Edition** (VTM5e)

## Planned Support
- Hunter: The Reckoning 5th Edition (HTR5e)
- Werewolf: The Apocalypse 5th Edition (WTA5e)
- Additional WoD splats

## Features
- Discord OAuth authentication
- Up to 3 characters per user per game line
- Character portrait uploads with automatic resizing
- Persistent storage via PostgreSQL + Railway Volumes
- Mobile-friendly responsive design
- Prepared for Discord bot webhook integration (Inconnu, Herald)

## Tech Stack
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Frontend:** HTML/CSS/JavaScript + Alpine.js
- **Auth:** Discord OAuth
- **Storage:** Railway Volumes (character portraits)
- **Deployment:** Railway (auto-deploy on push to main)

## Environment Variables

Required environment variables (set in Railway):

```
DATABASE_URL=postgresql://...          # Auto-provided by Railway PostgreSQL
DISCORD_CLIENT_ID=your_client_id       # From Discord Developer Portal
DISCORD_CLIENT_SECRET=your_secret      # From Discord Developer Portal
DISCORD_REDIRECT_URI=https://your-app.up.railway.app/auth/callback
SECRET_KEY=your_random_secret_key      # Generate with: openssl rand -hex 32
VOLUME_PATH=/data                      # Railway Volume mount point
```

## Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables in `.env` file
6. Run migrations: `alembic upgrade head`
7. Start the server: `uvicorn app.main:app --reload`

## Deployment

This project auto-deploys to Railway on push to `main` branch.

1. Connect GitHub repository to Railway project
2. Add PostgreSQL database in Railway
3. Add Railway Volume (5GB) mounted at `/data`
4. Set environment variables in Railway dashboard
5. Push to `main` branch

## Project Structure

```
wod-character-sheets/
├── app/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connection and session management
│   ├── models.py            # SQLAlchemy models
│   ├── auth.py              # Discord OAuth implementation
│   ├── routes/
│   │   ├── auth.py          # Authentication routes
│   │   ├── vtm.py           # VTM character routes
│   │   └── htr.py           # HTR character routes (future)
│   └── static/              # CSS, JS, images
├── templates/               # Jinja2 templates
├── alembic/                 # Database migrations
├── requirements.txt
├── Procfile                 # Railway deployment
└── README.md
```

## Discord OAuth Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to OAuth2 settings
4. Add redirect URL: `https://your-app.up.railway.app/auth/callback`
5. Copy Client ID and Client Secret to Railway environment variables
6. Enable OAuth2 scopes: `identify`

## License

This is a personal project for World of Darkness gameplay. All World of Darkness content is owned by Paradox Interactive.

## Author

Built with love for the World of Darkness community.
