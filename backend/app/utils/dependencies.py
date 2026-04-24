from fastapi import Depends, HTTPException, status, Cookie, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_session
from app.utils.security import verify_token
from app.models.user import User
from sqlmodel import select
from typing import AsyncGenerator

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for database session"""
    async for session in get_session():
        yield session


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    session: AsyncSession = Depends(get_db_session)
) -> User:
    """Dependency for getting current authenticated user from JWT token"""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(access_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Fetch user from database
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_user_ws(websocket: WebSocket) -> int:
    """Get current user ID from WebSocket connection cookies"""
    from app.database import get_session

    # Get access token from cookies
    access_token = websocket.cookies.get("access_token")

    if not access_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    payload = verify_token(access_token)
    if payload is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id: int = payload.get("user_id")
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Verify user exists
    async for session in get_session():
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()

        if user is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user_id
