# CSRF Protection Implementation

## Status: Partially Implemented ⚠️

CSRF protection infrastructure is in place but **NOT YET ENFORCED** on all routes.

## What's Implemented ✅

1. **CSRF Token Generation & Validation** (`app/csrf.py`)
   - Token generation using `itsdangerous`
   - Token validation with expiry (1 hour default)
   - Session-based token storage

2. **CSRF Endpoint** (`/csrf-token`)
   - GET endpoint to fetch CSRF token for current session
   - Automatically creates token if none exists

3. **Frontend Integration** (`templates/base.html`)
   - JavaScript automatically fetches CSRF token on page load
   - Global `window.csrfToken` variable available
   - Helper function `getCsrfHeaders()` for fetch requests

4. **FastAPI Dependency** (`app/csrf.py:require_csrf`)
   - Ready-to-use dependency for protecting routes
   - Usage: `@app.post("/route", dependencies=[Depends(require_csrf)])`

## What's NOT Yet Protected ❌

The following routes still need CSRF protection added:

### VTM Routes (`app/routes/vtm.py`)
- [ ] POST `/vtm/character/create`
- [ ] POST `/vtm/character/{character_id}/update`
- [ ] POST `/vtm/character/{character_id}/delete`
- [ ] POST `/vtm/character/{character_id}/upload-portrait`

### HTR Routes (`app/routes/htr.py`)
- [ ] POST `/htr/character/create`
- [ ] POST `/htr/character/{character_id}/update`
- [ ] POST `/htr/character/{character_id}/delete`
- [ ] POST `/htr/character/{character_id}/upload-portrait`

### Storyteller Routes (`app/routes/storyteller.py`)
- [ ] POST `/storyteller/{game}/character/{character_id}/delete`

## How to Protect a Route

### Step 1: Update the Route Definition

```python
from fastapi import Depends
from app.csrf import require_csrf

# Before:
@router.post("/vtm/character/create")
async def create_character(request: Request):
    ...

# After:
@router.post("/vtm/character/create", dependencies=[Depends(require_csrf)])
async def create_character(request: Request):
    ...
```

### Step 2: Update Frontend JavaScript

Ensure all fetch requests include the CSRF token header:

```javascript
// Before:
const response = await fetch('/vtm/character/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
});

// After:
const response = await fetch('/vtm/character/create', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        ...getCsrfHeaders()  // Adds X-CSRF-Token header
    },
    body: JSON.stringify(data)
});
```

### Step 3: Test

1. Load the page (CSRF token fetched automatically)
2. Submit a form/API request
3. Verify request succeeds with token
4. Verify request fails without token (test in DevTools)

## Token Behavior

- **Lifetime**: 1 hour (configurable in `validate_csrf_token` max_age parameter)
- **Storage**: HTTP session (secure, httpOnly cookie in production)
- **Rotation**: New token generated if missing or expired
- **Validation**: Must match session token AND have valid signature

## Security Notes

⚠️ **CRITICAL**: Until all routes are protected, the application remains vulnerable to CSRF attacks.

**Priority**: Add CSRF protection to all character creation, update, and deletion endpoints ASAP.

## Testing CSRF Protection

```bash
# Test token endpoint
curl http://localhost:8000/csrf-token

# Test protected route (should fail without token)
curl -X POST http://localhost:8000/vtm/character/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Test"}'

# Test protected route (should succeed with token)
# First get token, then:
curl -X POST http://localhost:8000/vtm/character/create \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: YOUR_TOKEN_HERE" \
  -d '{"name": "Test"}'
```

## Implementation Checklist

- [x] Create CSRF module
- [x] Initialize CSRF in main.py
- [x] Add /csrf-token endpoint
- [x] Add JavaScript to fetch token
- [x] Create FastAPI dependency
- [ ] Protect all POST/PUT/DELETE routes
- [ ] Update all JavaScript fetch calls
- [ ] Add integration tests
- [ ] Document in main README.md
