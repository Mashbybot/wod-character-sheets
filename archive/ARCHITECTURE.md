# ARCHITECTURE OVERVIEW

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Browser)                       │
│                                                                  │
│  ┌────────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  character-    │  │   Alpine.js  │  │   Templates       │  │
│  │  sheet.js      │  │   Component  │  │   (Jinja2)        │  │
│  └────────────────┘  └──────────────┘  └───────────────────┘  │
│           │                  │                   │              │
│           └──────────────────┴───────────────────┘              │
│                              │                                  │
│                         HTTP/JSON                               │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                     Exception Handlers                      │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐  │ │
│  │  │ WoDException │ │ Validation   │ │ SQLAlchemy       │  │ │
│  │  │ Handler      │ │ Handler      │ │ Handler          │  │ │
│  │  └──────────────┘ └──────────────┘ └──────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                               │                                  │
│  ┌───────────────────────────┼──────────────────────────────┐  │
│  │                        Routes                              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │   Auth   │  │   VTM    │  │   HTR    │  │   API    │ │  │
│  │  │  Routes  │  │  Routes  │  │  Routes  │  │  Routes  │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  └────────┬──────────────────────────────────────────────────┘  │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Pydantic Schemas                        │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │  VTMCharacterCreate | VTMCharacterUpdate           │ │   │
│  │  │  TouchstoneCreate   | BackgroundCreate             │ │   │
│  │  │  XPLogEntryCreate   | UserPreferencesUpdate        │ │   │
│  │  │  ▼ VALIDATES ALL INPUTS ▼                          │ │   │
│  │  └────────────────────────────────────────────────────┘ │   │
│  └────────┬──────────────────────────────────────────────────┘   │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Business Logic Layer                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │   │
│  │  │  Utils   │  │Constants │  │   Exceptions         │  │   │
│  │  │          │  │          │  │   (Custom)           │  │   │
│  │  └──────────┘  └──────────┘  └──────────────────────┘  │   │
│  └────────┬──────────────────────────────────────────────────┘   │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  SQLAlchemy ORM                           │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │  User | VTMCharacter | HTRCharacter               │ │   │
│  │  │  Touchstone | Background | XPLogEntry             │ │   │
│  │  │  UserPreferences                                   │ │   │
│  │  └────────────────────────────────────────────────────┘ │   │
│  └────────┬──────────────────────────────────────────────────┘   │
└───────────┼──────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                         │
│                                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │  users   │  │vtm_characters│  │  htr_characters         │  │
│  └──────────┘  └──────────────┘  └─────────────────────────┘  │
│       │              │                                           │
│       │              ├─────────────┐                            │
│       │              │             │                            │
│  ┌────┴─────┐  ┌────▼──────┐ ┌───▼──────┐  ┌──────────────┐  │
│  │  user_   │  │touchstones│ │backgrounds│  │ xp_log_      │  │
│  │  prefs   │  └───────────┘ └───────────┘  │ entries      │  │
│  └──────────┘                                └──────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              alembic_version (migrations)                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Railway Volume (/data)                      │
│                                                                  │
│  character_portraits/                                            │
│  ├── uuid1.jpg  (face)                                          │
│  ├── uuid2.jpg  (body)                                          │
│  └── uuid3.jpg  (hobby)                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Flow Example

### Creating a Character

```
1. User fills form in browser
   ↓
2. Alpine.js sends POST to /vtm/character/create
   {
     "name": "Elena Cross",
     "clan": "brujah",
     "strength": 3,
     "hunger": 2
   }
   ↓
3. FastAPI receives request
   ↓
4. Pydantic validates (VTMCharacterCreate schema)
   - name: required, max 100 chars ✓
   - clan: must be valid clan ✓
   - strength: 1-5 ✓
   - hunger: 0-5 ✓
   ↓
5. Route handler processes
   - Check character limit
   - Create VTMCharacter instance
   ↓
6. SQLAlchemy ORM
   - INSERT into vtm_characters
   ↓
7. PostgreSQL
   - Stores data
   - Returns ID
   ↓
8. Response serialized (VTMCharacterResponse)
   ↓
9. JSON sent to browser
   {
     "id": 123,
     "name": "Elena Cross",
     "clan": "brujah",
     ...
   }
   ↓
10. Alpine.js updates UI
```

---

## Validation Layer

```
┌─────────────────────────────────────────────────────────┐
│                 Incoming Request                         │
│             (potentially malicious data)                 │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                Pydantic Schema                           │
│  ┌────────────────────────────────────────────────┐    │
│  │ VTMCharacterUpdate(                            │    │
│  │   strength: Optional[int] = Field(ge=1, le=5)  │    │
│  │   hunger: Optional[int] = Field(ge=0, le=5)    │    │
│  │   ...                                          │    │
│  │ )                                              │    │
│  └────────────────────────────────────────────────┘    │
│                       │                                  │
│         ┌─────────────┴──────────────┐                 │
│         │                            │                  │
│    ✓ VALID                      ✗ INVALID              │
│         │                            │                  │
└─────────┼────────────────────────────┼─────────────────┘
          │                            │
          ▼                            ▼
┌──────────────────┐        ┌──────────────────────────┐
│  Continue to     │        │  ValidationError         │
│  business logic  │        │  ↓                       │
│                  │        │  422 Response            │
│                  │        │  {                       │
│                  │        │    "error": "...",       │
│                  │        │    "details": [...]      │
│                  │        │  }                       │
└──────────────────┘        └──────────────────────────┘
```

---

## Database Relationships

```
┌──────────────┐
│     User     │
│──────────────│
│ id           │
│ discord_id   │
│ username     │
└──────┬───────┘
       │
       │ 1:1
       ├───────────────────────┐
       │                       │
       ▼                       ▼
┌──────────────────┐    ┌─────────────┐
│ UserPreferences  │    │   VTM       │
│──────────────────│    │ Character   │
│ id               │    │─────────────│
│ user_id (FK)     │    │ id          │
│ column_widths    │    │ user_id(FK) │
│ theme            │    │ name        │
└──────────────────┘    │ clan        │
                        │ ...         │
                        └──────┬──────┘
                               │
                               │ 1:N
                 ┌─────────────┼─────────────┐
                 │             │             │
                 ▼             ▼             ▼
          ┌────────────┐ ┌──────────┐ ┌──────────┐
          │ Touchstone │ │Background│ │ XPLog    │
          │────────────│ │──────────│ │Entry     │
          │ id         │ │ id       │ │──────────│
          │ char_id(FK)│ │char_id   │ │ id       │
          │ name       │ │ type     │ │char_id   │
          │ conviction │ │ dots     │ │ amount   │
          └────────────┘ └──────────┘ └──────────┘
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────┐
│                   Request Received                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
                  TRY BLOCK
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    Business      Validation      Database
      Logic         Error          Error
        │              │              │
        │         CATCHES:            │
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌────────────┐
│WoDException  │ │Validation│ │SQLAlchemy  │
│  Handler     │ │ Handler  │ │  Handler   │
└──────┬───────┘ └────┬─────┘ └─────┬──────┘
       │              │              │
       └──────────────┼──────────────┘
                      │
                      ▼
           ┌────────────────────┐
           │  ErrorResponse     │
           │  Schema            │
           │────────────────────│
           │ error: str         │
           │ status_code: int   │
           │ details: List      │
           └─────────┬──────────┘
                     │
                     ▼
           ┌────────────────────┐
           │  JSON Response     │
           │────────────────────│
           │ {                  │
           │   "error": "...",  │
           │   "status_code":.. │
           │   "details": [     │
           │     {              │
           │       "field": "." │
           │       "message":.  │
           │     }              │
           │   ]                │
           │ }                  │
           └────────────────────┘
```

---

## Migration System

```
┌─────────────────────────────────────────────────────────┐
│                  Development                             │
│                                                          │
│  1. Modify models.py                                    │
│     ↓                                                    │
│  2. alembic revision --autogenerate                     │
│     ↓                                                    │
│  3. Review/edit migration                               │
│     ↓                                                    │
│  4. Test on local DB                                    │
│     ↓                                                    │
│  5. Commit migration file                               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Production                              │
│                                                          │
│  1. Pull latest code                                    │
│     ↓                                                    │
│  2. alembic upgrade head                                │
│     ↓                                                    │
│     ┌──────────────────────────────────┐               │
│     │  Alembic checks current version  │               │
│     │  in alembic_version table        │               │
│     └──────────────┬───────────────────┘               │
│                    │                                     │
│                    ▼                                     │
│     ┌──────────────────────────────────┐               │
│     │  Runs upgrade() function in      │               │
│     │  each pending migration           │               │
│     └──────────────┬───────────────────┘               │
│                    │                                     │
│                    ▼                                     │
│     ┌──────────────────────────────────┐               │
│     │  Updates alembic_version table   │               │
│     │  to latest revision               │               │
│     └───────────────────────────────────┘               │
│                                                          │
│  3. Application uses new schema                         │
└─────────────────────────────────────────────────────────┘
```

---

## Component Dependencies

```
routes/vtm.py
    │
    ├── Depends on: schemas.py (validation)
    ├── Depends on: models_new.py (ORM)
    ├── Depends on: exceptions.py (error handling)
    ├── Depends on: utils.py (helpers)
    └── Depends on: constants.py (config)

schemas.py
    │
    ├── Depends on: constants.py (validation limits)
    └── Depends on: pydantic (framework)

models_new.py
    │
    ├── Depends on: database.py (Base, session)
    └── Depends on: sqlalchemy (ORM)

utils.py
    │
    ├── Depends on: constants.py (config)
    ├── Depends on: exceptions.py (error raising)
    └── Depends on: PIL (image processing)

exceptions.py
    │
    ├── Depends on: schemas.py (ErrorResponse)
    └── Depends on: fastapi (HTTPException)

constants.py
    │
    └── No dependencies (pure config)
```

---

## Deployment Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                  Developer Machine                       │
│                                                          │
│  1. Write code                                          │
│  2. Run tests locally                                   │
│  3. git commit -m "Feature X"                          │
│  4. git push origin main                                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                      GitHub                              │
│                                                          │
│  1. Receives push                                       │
│  2. Triggers webhook to Railway                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                      Railway                             │
│                                                          │
│  1. Pull latest code                                    │
│  2. Install dependencies (pip install -r requirements)  │
│  3. Build application                                   │
│  4. Deploy to production                                │
│  5. Restart server                                      │
│                                                          │
│  ** YOU MUST RUN MANUALLY: **                           │
│     railway run alembic upgrade head                    │
└─────────────────────────────────────────────────────────┘
```

---

## Key Design Patterns

### 1. Repository Pattern
```
Routes → ORM Models → Database
(API)    (SQLAlchemy)  (PostgreSQL)
```

### 2. DTO Pattern (Data Transfer Objects)
```
Request → Pydantic Schema → ORM Model
Database → ORM Model → Pydantic Schema → Response
```

### 3. Dependency Injection
```python
def route_handler(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth)
):
    # db and user injected automatically
```

### 4. Exception Handling
```
Try → Business Logic
Except → Custom Exception
Handler → ErrorResponse Schema → JSON
```

---

## Security Layers

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Discord OAuth                                 │
│  - Verifies user identity                               │
│  - No password storage                                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Session Management                            │
│  - Encrypted session cookie                             │
│  - 14-day expiration                                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Ownership Validation                          │
│  - Verify user owns character before operations         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 4: Input Validation                              │
│  - Pydantic schemas prevent injection                   │
│  - Type checking, length limits, range validation       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 5: File Upload Validation                        │
│  - Type checking, size limits                           │
│  - Image processing sanitization                        │
└─────────────────────────────────────────────────────────┘
```

---

This architecture is:
- ✅ Scalable
- ✅ Maintainable
- ✅ Testable
- ✅ Secure
- ✅ Production-ready
