from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from fastapi import HTTPException, status
from app.config import settings


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    async def register_user(session: AsyncSession, user_data: UserRegister) -> User:
        """Register a new user"""
        # Check if user already exists
        statement = select(User).where(User.email == user_data.email.lower())
        result = await session.execute(statement)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Create new user - clear password from memory after hashing
        password = user_data.password
        hashed_password = hash_password(password)

        # Clear password from memory for security
        del password

        new_user = User(
            email=user_data.email.lower(),
            password_hash=hashed_password
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user

    @staticmethod
    async def authenticate_user(session: AsyncSession, login_data: UserLogin) -> User:
        """Authenticate user and return user object"""
        statement = select(User).where(User.email == login_data.email.lower())
        result = await session.execute(statement)
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        return user

    @staticmethod
    def create_tokens(user: User) -> dict:
        """Create access and refresh tokens for user"""
        token_data = {"user_id": user.id, "email": user.email}

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
