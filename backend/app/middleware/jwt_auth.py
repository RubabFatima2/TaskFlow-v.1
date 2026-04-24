from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import verify_token


security = HTTPBearer()


async def jwt_auth_middleware(request: Request, call_next):
    """Middleware to verify JWT tokens on protected routes"""
    # Skip authentication for public routes
    public_routes = ["/health", "/api/v1/auth/register", "/api/v1/auth/login", "/docs", "/openapi.json"]

    if request.url.path in public_routes:
        return await call_next(request)

    # For protected routes, token verification is handled by dependencies
    response = await call_next(request)
    return response
