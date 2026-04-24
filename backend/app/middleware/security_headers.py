from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection in browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy - strict policy to prevent XSS
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

        # Referrer Policy - control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy - disable unnecessary browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

        # Strict Transport Security - enforce HTTPS (only in production)
        # Note: This should only be enabled when using HTTPS
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
