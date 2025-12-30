# Rate Limiting Implementation

## Status: Implemented ✅ (Infrastructure Ready)

Rate limiting infrastructure is in place but **NOT YET APPLIED** to all routes.

## Available Rate Limiters

### 1. General API Rate Limit
- **Limit**: 60 requests per minute
- **Use for**: Most API endpoints
- **Dependency**: `rate_limit_general`

### 2. File Upload Rate Limit
- **Limit**: 20 uploads per hour
- **Use for**: Portrait/file upload endpoints
- **Dependency**: `rate_limit_upload`

### 3. Authentication Rate Limit
- **Limit**: 10 attempts per 15 minutes
- **Use for**: Login, OAuth callbacks
- **Dependency**: `rate_limit_auth`

### 4. Strict Rate Limit
- **Limit**: 10 requests per hour
- **Use for**: Sensitive operations (character deletion, etc.)
- **Dependency**: `rate_limit_strict`

## How to Apply Rate Limiting

### Method 1: Route Dependency (Recommended)

```python
from fastapi import Depends
from app.rate_limit import rate_limit_general, rate_limit_upload, rate_limit_strict

# General API endpoint
@router.post("/vtm/character/create", dependencies=[Depends(rate_limit_general)])
async def create_character(request: Request):
    ...

# File upload endpoint
@router.post("/vtm/character/{character_id}/upload-portrait", dependencies=[Depends(rate_limit_upload)])
async def upload_portrait(request: Request):
    ...

# Sensitive operation
@router.post("/vtm/character/{character_id}/delete", dependencies=[Depends(rate_limit_strict)])
async def delete_character(request: Request):
    ...
```

### Method 2: Multiple Dependencies

Combine with CSRF protection:

```python
from app.csrf import require_csrf
from app.rate_limit import rate_limit_general

@router.post(
    "/vtm/character/create",
    dependencies=[
        Depends(rate_limit_general),
        Depends(require_csrf)
    ]
)
async def create_character(request: Request):
    ...
```

## Response Headers

Rate limited endpoints automatically include headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1704123456
```

## Rate Limit Exceeded Response

```json
HTTP 429 Too Many Requests
Retry-After: 45
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704123456

{
  "detail": "Rate limit exceeded. Try again in 45 seconds."
}
```

## Routes That Need Rate Limiting

### High Priority (Sensitive/Expensive Operations)

#### File Uploads (Use `rate_limit_upload`)
- [ ] `/vtm/character/{id}/upload-portrait`
- [ ] `/htr/character/{id}/upload-portrait`

#### Character Deletion (Use `rate_limit_strict`)
- [ ] `/vtm/character/{id}/delete`
- [ ] `/htr/character/{id}/delete`
- [ ] `/storyteller/{game}/character/{id}/delete`

### Medium Priority (API Endpoints)

#### Character Operations (Use `rate_limit_general`)
- [ ] `/vtm/character/create`
- [ ] `/vtm/character/{id}/update`
- [ ] `/htr/character/create`
- [ ] `/htr/character/{id}/update`

#### Export Operations (Use `rate_limit_upload`)
- [ ] `/export/{game}/character/{id}`

### Low Priority (Already Rate-Limited by OAuth)

#### Authentication (Use `rate_limit_auth`)
- `/auth/login` - OAuth provider handles rate limiting
- `/auth/callback` - OAuth provider handles rate limiting

## Identifier Strategy

Rate limits are applied per:
1. **IP Address** (from `X-Forwarded-For` if behind proxy, else `client.host`)
2. **User ID** (if authenticated, format: `{ip}:{user_id}`)

This prevents:
- Anonymous abuse from single IP
- Authenticated users bypassing limits by logging out
- Shared IPs (offices, NAT) from being overly restricted

## Implementation Notes

### Current Implementation
- ✅ In-memory storage using Python `deque`
- ✅ Token bucket algorithm
- ✅ Per-user and per-IP tracking
- ✅ Automatic cleanup of old requests
- ✅ Standard HTTP 429 responses

### Limitations
⚠️ **Single-Instance Only**: This implementation uses in-memory storage, which means:
- Rate limits don't sync across multiple app instances
- Limits reset on app restart
- Not suitable for scaled deployments

### Production Upgrade Path

For production with multiple workers/instances, upgrade to Redis-backed rate limiting:

```bash
pip install slowapi redis
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/some-route")
@limiter.limit("60/minute")
async def some_route():
    ...
```

## Testing Rate Limits

```bash
# Test rate limit (repeat until 429)
for i in {1..70}; do
  curl -w "HTTP %{http_code}\n" http://localhost:8000/vtm/character/create
  sleep 0.1
done

# Check rate limit headers
curl -i http://localhost:8000/csrf-token | grep X-RateLimit

# Test with authentication
curl -b "wod_session=YOUR_SESSION" \
  http://localhost:8000/vtm/character/create
```

## Monitoring

Consider adding monitoring for:
- Rate limit hit rate (429 responses)
- Top rate-limited IPs
- Average requests per user
- Rate limit effectiveness (blocked attacks)

## Configuration

Rate limits are defined in `app/constants.py`:

```python
RATE_LIMIT_PER_MINUTE = 60              # General API
UPLOAD_RATE_LIMIT_PER_HOUR = 20         # File uploads
# Add more as needed
```

## Implementation Checklist

- [x] Create rate limiting module
- [x] Add rate limit dependencies
- [x] Configure rate limit constants
- [x] Add response headers
- [ ] Apply to all POST/PUT/DELETE routes
- [ ] Apply to file upload routes
- [ ] Apply to sensitive operations
- [ ] Add monitoring/logging
- [ ] Consider Redis upgrade for production
