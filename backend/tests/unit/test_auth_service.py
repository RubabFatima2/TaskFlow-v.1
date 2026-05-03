import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister, UserLogin
from fastapi import HTTPException


@pytest.mark.asyncio
class TestAuthService:
    """Test authentication service operations"""

    async def test_register_user_success(self, test_db, client):
        """Test successful user registration"""
        from app.database import get_session

        async for session in get_session():
            user_data = UserRegister(
                email="newuser@example.com",
                password="testpassword123"
            )

            user = await AuthService.register_user(session, user_data)

            assert user is not None
            assert user.id is not None
            assert user.email == "newuser@example.com"
            assert user.password_hash != "testpassword123"
            assert len(user.password_hash) > 0
            break

    async def test_register_user_duplicate_email(self, test_db, client):
        """Test registration with duplicate email raises conflict"""
        from app.database import get_session

        async for session in get_session():
            user_data = UserRegister(
                email="duplicate@example.com",
                password="testpassword123"
            )

            # Register first user
            await AuthService.register_user(session, user_data)

            # Try to register with same email
            with pytest.raises(HTTPException) as exc_info:
                await AuthService.register_user(session, user_data)

            assert exc_info.value.status_code == 409
            assert "already registered" in exc_info.value.detail.lower()
            break

    async def test_register_user_email_case_insensitive(self, test_db, client):
        """Test that email registration is case-insensitive"""
        from app.database import get_session

        async for session in get_session():
            user_data1 = UserRegister(
                email="CaseSensitive@example.com",
                password="testpassword123"
            )
            user_data2 = UserRegister(
                email="casesensitive@example.com",
                password="testpassword456"
            )

            # Register first user
            user1 = await AuthService.register_user(session, user_data1)
            assert user1.email == "casesensitive@example.com"  # Stored as lowercase

            # Try to register with different case
            with pytest.raises(HTTPException) as exc_info:
                await AuthService.register_user(session, user_data2)

            assert exc_info.value.status_code == 409
            break

    async def test_authenticate_user_success(self, test_db, client):
        """Test successful user authentication"""
        from app.database import get_session

        async for session in get_session():
            # Register user
            register_data = UserRegister(
                email="authtest@example.com",
                password="testpassword123"
            )
            await AuthService.register_user(session, register_data)

            # Authenticate user
            login_data = UserLogin(
                email="authtest@example.com",
                password="testpassword123"
            )
            user = await AuthService.authenticate_user(session, login_data)

            assert user is not None
            assert user.email == "authtest@example.com"
            break

    async def test_authenticate_user_wrong_password(self, test_db, client):
        """Test authentication with wrong password"""
        from app.database import get_session

        async for session in get_session():
            # Register user
            register_data = UserRegister(
                email="wrongpass@example.com",
                password="correctpassword"
            )
            await AuthService.register_user(session, register_data)

            # Try to authenticate with wrong password
            login_data = UserLogin(
                email="wrongpass@example.com",
                password="wrongpassword"
            )

            with pytest.raises(HTTPException) as exc_info:
                await AuthService.authenticate_user(session, login_data)

            assert exc_info.value.status_code == 401
            assert "incorrect" in exc_info.value.detail.lower()
            break

    async def test_authenticate_user_nonexistent_email(self, test_db, client):
        """Test authentication with non-existent email"""
        from app.database import get_session

        async for session in get_session():
            login_data = UserLogin(
                email="nonexistent@example.com",
                password="anypassword"
            )

            with pytest.raises(HTTPException) as exc_info:
                await AuthService.authenticate_user(session, login_data)

            assert exc_info.value.status_code == 401
            break

    async def test_authenticate_user_case_insensitive_email(self, test_db, client):
        """Test authentication with different email case"""
        from app.database import get_session

        async for session in get_session():
            # Register user
            register_data = UserRegister(
                email="CaseTest@example.com",
                password="testpassword123"
            )
            await AuthService.register_user(session, register_data)

            # Authenticate with different case
            login_data = UserLogin(
                email="casetest@EXAMPLE.com",
                password="testpassword123"
            )
            user = await AuthService.authenticate_user(session, login_data)

            assert user is not None
            assert user.email == "casetest@example.com"
            break

    async def test_create_tokens(self, test_db, client):
        """Test token creation for user"""
        from app.database import get_session

        async for session in get_session():
            # Register user
            register_data = UserRegister(
                email="tokentest@example.com",
                password="testpassword123"
            )
            user = await AuthService.register_user(session, register_data)

            # Create tokens
            tokens = AuthService.create_tokens(user)

            assert "access_token" in tokens
            assert "refresh_token" in tokens
            assert "token_type" in tokens
            assert "expires_in" in tokens
            assert tokens["token_type"] == "bearer"
            assert tokens["expires_in"] > 0
            assert len(tokens["access_token"]) > 0
            assert len(tokens["refresh_token"]) > 0
            break

    async def test_create_tokens_contains_user_data(self, test_db, client):
        """Test that tokens contain user data"""
        from app.database import get_session
        from app.utils.security import verify_token

        async for session in get_session():
            # Register user
            register_data = UserRegister(
                email="tokendata@example.com",
                password="testpassword123"
            )
            user = await AuthService.register_user(session, register_data)

            # Create tokens
            tokens = AuthService.create_tokens(user)

            # Verify access token contains user data
            access_payload = verify_token(tokens["access_token"])
            assert access_payload["user_id"] == user.id
            assert access_payload["email"] == user.email

            # Verify refresh token contains user data
            refresh_payload = verify_token(tokens["refresh_token"])
            assert refresh_payload["user_id"] == user.id
            assert refresh_payload["email"] == user.email
            break
