from fastapi import Request, HTTPException, status, Response
from typing import Optional
import secrets
import hmac
import hashlib
from app.config import settings


class CSRFProtection:
    """CSRF protection middleware for cookie-based authentication"""

    @staticmethod
    def generate_csrf_token() -> str:
        """Generate a secure CSRF token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_csrf_token_hash(token: str) -> str:
        """Create HMAC hash of CSRF token"""
        return hmac.new(
            settings.BETTER_AUTH_SECRET.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def verify_csrf_token(token: str, token_hash: str) -> bool:
        """Verify CSRF token against its hash"""
        expected_hash = CSRFProtection.create_csrf_token_hash(token)
        return hmac.compare_digest(expected_hash, token_hash)

    @staticmethod
    def set_csrf_cookie(response: Response) -> str:
        """Set CSRF token in cookie and return the token"""
        csrf_token = CSRFProtection.generate_csrf_token()
        csrf_hash = CSRFProtection.create_csrf_token_hash(csrf_token)

        # Set CSRF token hash in HTTP-only cookie
        response.set_cookie(
            key="csrf_token",
            value=csrf_hash,
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            samesite="lax",  # Changed from strict to lax for cross-origin (different ports)
            max_age=3600,  # 1 hour
            path="/"
        )

        return csrf_token

    @staticmethod
    async def validate_csrf(request: Request) -> None:
        """
        Validate CSRF token for state-changing operations

        Raises:
            HTTPException: If CSRF validation fails
        """
        # Skip CSRF for safe methods
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return

        # Get CSRF token from header
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing in request header"
            )

        # Get CSRF hash from cookie
        csrf_hash = request.cookies.get("csrf_token")
        if not csrf_hash:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing in cookie"
            )

        # Verify token
        if not CSRFProtection.verify_csrf_token(csrf_token, csrf_hash):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token"
            )


csrf_protection = CSRFProtection()
