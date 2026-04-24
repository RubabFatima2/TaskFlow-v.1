from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.utils.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.middleware.rate_limit import auth_rate_limit
from typing import Optional

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(auth_rate_limit)
):
    """Register a new user"""
    user = await AuthService.register_user(session, user_data)
    return user


@router.post("/login", response_model=UserResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(auth_rate_limit)
):
    """Login user and set JWT token in HTTP-only cookie"""
    from app.config import settings

    user = await AuthService.authenticate_user(session, login_data)
    tokens = AuthService.create_tokens(user)

    # Set access token in HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=settings.ENVIRONMENT == "production",  # Only secure in production
        samesite="lax",  # Changed from strict to lax for cross-origin (different ports)
        max_age=tokens["expires_in"],
        path="/"
    )

    # Set refresh token in HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=settings.ENVIRONMENT == "production",  # Only secure in production
        samesite="lax",  # Changed from strict to lax for cross-origin (different ports)
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/"
    )

    return user


@router.post("/logout")
async def logout(
    response: Response
):
    """Logout user by clearing cookies"""
    # Delete cookies with matching parameters
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite="lax"
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite="lax"
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    session: AsyncSession = Depends(get_db_session)
):
    """Refresh access token using refresh token"""
    from app.config import settings
    from app.utils.security import verify_token, create_access_token
    from sqlmodel import select

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )

    # Verify refresh token
    payload = verify_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Fetch user from database
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Create new access token
    token_data = {"user_id": user.id, "email": user.email}
    new_access_token = create_access_token(token_data)

    # Set new access token in cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",  # Changed from strict to lax for cross-origin (different ports)
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )

    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
