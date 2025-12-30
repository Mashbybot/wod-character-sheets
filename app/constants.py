"""Application constants - centralized configuration values"""

import os

# ===== CHARACTER LIMITS =====
CHARACTER_LIMIT_PER_USER = 3
MAX_TOUCHSTONES = 3
MAX_BACKGROUNDS = 10
MAX_DISCIPLINES = 5
MAX_CHRONICLE_TENETS = 5

# ===== QUERY PAGINATION =====
STORYTELLER_DASHBOARD_LIMIT = 500  # Max characters to load in storyteller dashboard

# ===== EXPORT/PDF GENERATION =====
EXPORT_NAVIGATION_TIMEOUT = int(os.getenv("EXPORT_NAVIGATION_TIMEOUT", "60000"))  # Browser navigation timeout (ms)
EXPORT_SELECTOR_TIMEOUT = int(os.getenv("EXPORT_SELECTOR_TIMEOUT", "60000"))  # Wait for selector timeout (ms)

# ===== GAME MECHANICS =====
MIN_ATTRIBUTE = 1
MAX_ATTRIBUTE = 5
MIN_SKILL = 0
MAX_SKILL = 5
MIN_DISCIPLINE = 0
MAX_DISCIPLINE = 5

MIN_HUNGER = 0
MAX_HUNGER = 5

MIN_BLOOD_POTENCY = 0
MAX_BLOOD_POTENCY = 10

MIN_HEALTH = 1
MAX_HEALTH = 10
MIN_WILLPOWER = 1
MAX_WILLPOWER = 10

MIN_HUMANITY = 0
MAX_HUMANITY = 10

MIN_GENERATION = 1
MAX_GENERATION = 16

MIN_BACKGROUND_DOTS = 0
MAX_BACKGROUND_DOTS = 5

# ===== BLOOD POTENCY TABLE =====
BLOOD_POTENCY_VALUES = {
    0: {
        'surge': 1,
        'mend': 1,
        'power_bonus': 0,
        'rouse_reroll': 0,
        'feeding_penalty': 'No penalty',
        'bane_severity': 0
    },
    1: {
        'surge': 2,
        'mend': 1,
        'power_bonus': 0,
        'rouse_reroll': 0,
        'feeding_penalty': 'Animal/Bagged',
        'bane_severity': 1
    },
    2: {
        'surge': 2,
        'mend': 2,
        'power_bonus': 1,
        'rouse_reroll': 0,
        'feeding_penalty': 'Animal/Bagged',
        'bane_severity': 1
    },
    3: {
        'surge': 3,
        'mend': 2,
        'power_bonus': 1,
        'rouse_reroll': 1,
        'feeding_penalty': 'Cold blood',
        'bane_severity': 2
    },
    4: {
        'surge': 3,
        'mend': 3,
        'power_bonus': 2,
        'rouse_reroll': 1,
        'feeding_penalty': 'Cold blood',
        'bane_severity': 2
    },
    5: {
        'surge': 4,
        'mend': 3,
        'power_bonus': 2,
        'rouse_reroll': 2,
        'feeding_penalty': 'Resonance only',
        'bane_severity': 3
    },
    6: {
        'surge': 4,
        'mend': 3,
        'power_bonus': 3,
        'rouse_reroll': 2,
        'feeding_penalty': 'Resonance only',
        'bane_severity': 3
    },
    7: {
        'surge': 5,
        'mend': 3,
        'power_bonus': 3,
        'rouse_reroll': 3,
        'feeding_penalty': 'Slake 1 only',
        'bane_severity': 4
    },
    8: {
        'surge': 5,
        'mend': 4,
        'power_bonus': 4,
        'rouse_reroll': 3,
        'feeding_penalty': 'Slake 1 only',
        'bane_severity': 4
    },
    9: {
        'surge': 6,
        'mend': 4,
        'power_bonus': 4,
        'rouse_reroll': 4,
        'feeding_penalty': 'Slake 1 only',
        'bane_severity': 5
    },
    10: {
        'surge': 6,
        'mend': 5,
        'power_bonus': 5,
        'rouse_reroll': 4,
        'feeding_penalty': 'Slake 0 only',
        'bane_severity': 5
    }
}

# ===== CLAN DISCIPLINES =====
CLAN_DISCIPLINES = {
    'brujah': ['potence', 'presence', 'celerity'],
    'gangrel': ['animalism', 'fortitude', 'protean'],
    'malkavian': ['auspex', 'dominate', 'obfuscate'],
    'nosferatu': ['animalism', 'obfuscate', 'potence'],
    'toreador': ['auspex', 'celerity', 'presence'],
    'tremere': ['auspex', 'blood-sorcery', 'dominate'],
    'ventrue': ['dominate', 'fortitude', 'presence'],
    'banu-haqim': ['blood-sorcery', 'celerity', 'obfuscate'],
    'hecata': ['auspex', 'fortitude', 'oblivion'],
    'lasombra': ['dominate', 'oblivion', 'potence'],
    'ministry': ['obfuscate', 'presence', 'protean'],
    'ravnos': ['animalism', 'obfuscate', 'presence'],
    'salubri': ['auspex', 'dominate', 'fortitude'],
    'tzimisce': ['animalism', 'dominate', 'protean'],
    'caitiff': [],
    'thin-blood': []
}

# ===== VALID CLANS =====
VALID_CLANS = list(CLAN_DISCIPLINES.keys())

# ===== VALID DISCIPLINES =====
VALID_DISCIPLINES = [
    'animalism', 'auspex', 'blood-sorcery', 'celerity', 'dominate',
    'fortitude', 'obfuscate', 'oblivion', 'potence', 'presence',
    'protean', 'thin-blood-alchemy'
]

# ===== FILE UPLOAD =====
UPLOAD_FOLDER = os.getenv("VOLUME_PATH", "/data")
CHARACTER_IMAGE_DIR = os.path.join(UPLOAD_FOLDER, "character_portraits")
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Portrait sizes (width, height) in pixels
PORTRAIT_SIZES = {
    'face': (400, 400),      # Square
    'body': (300, 600),      # Tall
    'hobby': (150, 150)      # Small square
}

# Valid portrait box types
VALID_PORTRAIT_BOXES = ['face', 'body', 'hobby_1', 'hobby_2', 'hobby_3', 'hobby_4']

# ===== UI CONSTANTS =====
DEFAULT_COLUMN_WIDTHS_ABOVE = "30,35,35"
DEFAULT_COLUMN_WIDTHS_BELOW = "33,33,34"
DEFAULT_THEME = "dark"

# Divider width in pixels
COLUMN_DIVIDER_WIDTH = 8
TOTAL_DIVIDERS_WIDTH = COLUMN_DIVIDER_WIDTH * 2  # 2 dividers = 16px total

# ===== AUTO-SAVE =====
AUTOSAVE_DEBOUNCE_MS = 2000  # 2 seconds

# ===== SESSION =====
SESSION_MAX_AGE = 14 * 24 * 60 * 60  # 14 days in seconds

# ===== API RATE LIMITING =====
# Future implementation
RATE_LIMIT_PER_MINUTE = 60
UPLOAD_RATE_LIMIT_PER_HOUR = 20
