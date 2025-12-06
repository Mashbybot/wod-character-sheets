"""Shared Jinja2 templates configuration with globals"""

import os
import time
from fastapi.templating import Jinja2Templates
from app.utils import is_storyteller

# Static version for cache-busting
STATIC_VERSION = os.getenv("STATIC_VERSION", str(int(time.time())))

# Create templates instance
templates = Jinja2Templates(directory="templates")

# Register global functions and variables
templates.env.globals["static_version"] = STATIC_VERSION
templates.env.globals["is_storyteller"] = is_storyteller
