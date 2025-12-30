"""Rate Limiting for WoD Character Sheets

Simple in-memory rate limiting. For production with multiple workers,
consider using Redis-backed rate limiting (slowapi with Redis backend).
"""

import time
from typing import Dict, Tuple
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from app.constants import RATE_LIMIT_PER_MINUTE, UPLOAD_RATE_LIMIT_PER_HOUR


class RateLimiter:
    """In-memory rate limiter using token bucket algorithm"""

    def __init__(self):
        # Format: {identifier: deque([(timestamp, action)])}
        self.requests: Dict[str, deque] = defaultdict(deque)

    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting (IP + user ID if authenticated)"""
        # Try to get real IP from headers (if behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        # Include user ID if authenticated
        user = request.session.get("user")
        if user:
            user_id = user.get("id", "")
            return f"{ip}:{user_id}"

        return ip

    def _clean_old_requests(self, requests: deque, window_seconds: int) -> None:
        """Remove requests older than the time window"""
        current_time = time.time()
        cutoff = current_time - window_seconds

        while requests and requests[0][0] < cutoff:
            requests.popleft()

    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int,
        action: str = "request"
    ) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limit

        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            action: Action type for tracking

        Returns:
            Tuple of (allowed: bool, remaining: int, reset_time: int)
        """
        current_time = time.time()
        requests = self.requests[identifier]

        # Clean old requests
        self._clean_old_requests(requests, window_seconds)

        # Check if limit exceeded
        if len(requests) >= max_requests:
            oldest_request = requests[0][0]
            reset_time = int(oldest_request + window_seconds)
            return False, 0, reset_time

        # Add current request
        requests.append((current_time, action))

        # Calculate remaining requests
        remaining = max_requests - len(requests)
        reset_time = int(current_time + window_seconds)

        return True, remaining, reset_time

    async def limit_request(
        self,
        request: Request,
        max_requests: int,
        window_seconds: int,
        action: str = "request"
    ) -> None:
        """
        Rate limit middleware for FastAPI routes

        Args:
            request: FastAPI request
            max_requests: Max requests in window
            window_seconds: Time window in seconds
            action: Action type for logging

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        identifier = self._get_identifier(request)
        allowed, remaining, reset_time = self.check_rate_limit(
            identifier, max_requests, window_seconds, action
        )

        # Add rate limit headers to response (will be added by middleware)
        if hasattr(request.state, "rate_limit_headers"):
            request.state.rate_limit_headers.update({
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time)
            })
        else:
            request.state.rate_limit_headers = {
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time)
            }

        if not allowed:
            retry_after = reset_time - int(time.time())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time)
                }
            )


# Global rate limiter instance
_rate_limiter = RateLimiter()


# FastAPI dependencies for different rate limits

async def rate_limit_general(request: Request) -> None:
    """General API rate limit: 60 requests per minute"""
    await _rate_limiter.limit_request(
        request,
        max_requests=RATE_LIMIT_PER_MINUTE,
        window_seconds=60,
        action="general"
    )


async def rate_limit_upload(request: Request) -> None:
    """File upload rate limit: 20 uploads per hour"""
    await _rate_limiter.limit_request(
        request,
        max_requests=UPLOAD_RATE_LIMIT_PER_HOUR,
        window_seconds=3600,
        action="upload"
    )


async def rate_limit_auth(request: Request) -> None:
    """Authentication rate limit: 10 attempts per 15 minutes"""
    await _rate_limiter.limit_request(
        request,
        max_requests=10,
        window_seconds=900,
        action="auth"
    )


async def rate_limit_strict(request: Request) -> None:
    """Strict rate limit for sensitive operations: 10 per hour"""
    await _rate_limiter.limit_request(
        request,
        max_requests=10,
        window_seconds=3600,
        action="strict"
    )
