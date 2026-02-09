# 🌑 World of Darkness Character Sheets

**Your chronicles, preserved.**

A web-based character sheet manager for World of Darkness 5th Edition tabletop RPGs. Create, manage, and export your characters with Discord authentication and persistent cloud storage.

> *"A Beast I am, lest a Beast I become."*

---

## 🌑 Supported Game Lines

- **Vampire: The Masquerade 5th Edition** — Full character sheet support
- **Hunter: The Reckoning 5th Edition** — Full character sheet support
- *Werewolf: The Apocalypse 5th Edition* — Planned

## 🌑 Features

- **Discord OAuth** — Log in with your Discord account
- **Multiple characters** — Up to 3 characters per game line
- **Character portraits** — Upload with automatic resizing
- **PDF & PNG export** — Print-ready character sheets via Playwright
- **Storyteller dashboard** — Campaign and player management
- **Mobile-friendly** — Responsive design for any device
- **Cloud storage** — PostgreSQL with Railway Volumes

## 🌑 Tech Stack

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Frontend:** HTML/CSS/JavaScript + Alpine.js
- **Auth:** Discord OAuth2
- **Export:** Playwright + Chromium
- **Deployment:** Railway

## 🌑 Quick Start

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure
6. Run migrations: `alembic upgrade head`
7. Start the server: `uvicorn app.main:app --reload`

See `.env.example` for required environment variables. For production, this project auto-deploys to [Railway](https://railway.app) on push to `main`.

## 🌑 Contributing

Contributions are welcome! Open an issue or submit a pull request.

## 🌑 License

MIT License — Free to use, modify, and distribute.

---

## Dark Pack

*This project is made under the [Dark Pack](https://www.paradoxinteractive.com/games/world-of-darkness/community/dark-pack-agreement) license agreement.*

Portions of the materials are the copyrights and trademarks of Paradox Interactive AB, and are used with permission. All rights reserved. For more information please visit [worldofdarkness.com](https://www.worldofdarkness.com).

**This is a community project and is not official World of Darkness material.**
