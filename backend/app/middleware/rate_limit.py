from fastapi import Request, HTTPException, status
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple
import asyncio


class RateLimiter:
    """Simple in-memory rate limiter for API endpoints"""

    def __init__(self):
        # Store: {ip_address: {endpoint: [(timestamp, count)]}}
        self.requests: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self.lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        request: Request,
        max_requests: int,
        window_seconds: int
    ) -> None:
        """
        Check if request exceeds rate limit

        Args:
            request: FastAPI request object
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Raises:
            HTTPException: If rate limit exceeded
        """
        client_ip = request.client.host if request.client else "unknown"
        endpoint = request.url.path
        now = datetime.now(timezone.utc)

        async with self.lock:
            # Clean old entries
            cutoff_time = now - timedelta(seconds=window_seconds)
            self.requests[client_ip][endpoint] = [
                ts for ts in self.requests[client_ip][endpoint]
                if ts > cutoff_time
            ]

            # Check current count
            current_count = len(self.requests[client_ip][endpoint])

            if current_count >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds.",
                    headers={"Retry-After": str(window_seconds)}
                )

            # Add current request
            self.requests[client_ip][endpoint].append(now)

    async def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """Periodically clean up old entries to prevent memory bloat"""
        async with self.lock:
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)

            # Remove old IPs
            ips_to_remove = []
            for ip, endpoints in self.requests.items():
                for endpoint, timestamps in list(endpoints.items()):
                    endpoints[endpoint] = [ts for ts in timestamps if ts > cutoff_time]
                    if not endpoints[endpoint]:
                        del endpoints[endpoint]

                if not endpoints:
                    ips_to_remove.append(ip)

            for ip in ips_to_remove:
                del self.requests[ip]


# Global rate limiter instance
rate_limiter = RateLimiter()


async def auth_rate_limit(request: Request):
    """Rate limit for authentication endpoints: 5 requests per minute"""
    await rate_limiter.check_rate_limit(request, max_requests=5, window_seconds=60)


async def tasks_rate_limit(request: Request):
    """Rate limit for task endpoints: 30 requests per minute"""
    await rate_limiter.check_rate_limit(request, max_requests=30, window_seconds=60)
