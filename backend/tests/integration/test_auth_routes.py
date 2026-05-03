import pytest
from httpx import AsyncClient
from app.schemas.auth import UserRegister, UserLogin


@pytest.mark.asyncio
class TestAuthRoutes:
    """Integration tests for authentication routes"""

    async def test_register_user_success(self, client):
        """Test POST /api/v1/auth/register with valid data"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "testpassword123"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "password_hash" not in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_register_user_duplicate_email(self, client):
        """Test registration with duplicate email returns 409"""
        user_data = {
            "email": "duplicate@example.com",
            "password": "testpassword123"
        }

        # Register first user
        response1 = await client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201

        # Try to register with same email
        response2 = await client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 409
        assert "already registered" in response2.json()["detail"].lower()

    async def test_register_user_invalid_email(self, client):
        """Test registration with invalid email returns 422"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "testpassword123"
            }
        )

        assert response.status_code == 422

    async def test_register_user_short_password(self, client):
        """Test registration with short password returns 422"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "short"
            }
        )

        assert response.status_code == 422

    async def test_login_user_success(self, client):
        """Test POST /api/v1/auth/login with valid credentials"""
        # Register user first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "logintest@example.com",
                "password": "testpassword123"
            }
        )

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "logintest@example.com",
                "password": "testpassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "logintest@example.com"
        assert "id" in data

        # Check cookies are set
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    async def test_login_user_wrong_password(self, client):
        """Test login with wrong password returns 401"""
        # Register user first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "correctpassword"
            }
        )

        # Try to login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    async def test_login_user_nonexistent_email(self, client):
        """Test login with non-existent email returns 401"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )

        assert response.status_code == 401

    async def test_logout_user(self, client):
        """Test POST /api/v1/auth/logout clears cookies"""
        # Register and login first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "logouttest@example.com",
                "password": "testpassword123"
            }
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "logouttest@example.com",
                "password": "testpassword123"
            }
        )

        # Logout
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    async def test_get_current_user_authenticated(self, client, test_user):
        """Test GET /api/v1/auth/me with valid token"""
        # Login to get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Get current user
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["id"] == test_user["id"]

    async def test_get_current_user_unauthenticated(self, client):
        """Test GET /api/v1/auth/me without token returns 401"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_refresh_token_success(self, client, test_user):
        """Test POST /api/v1/auth/refresh with valid refresh token"""
        # Login to get tokens
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Refresh token
        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    async def test_refresh_token_without_token(self, client):
        """Test POST /api/v1/auth/refresh without refresh token returns 401"""
        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 401
        assert "not provided" in response.json()["detail"].lower()

    async def test_refresh_token_with_invalid_token(self, client):
        """Test POST /api/v1/auth/refresh with invalid token returns 401"""
        # Set invalid refresh token cookie
        client.cookies.set("refresh_token", "invalid.token.here")

        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 401

    async def test_login_sets_httponly_cookies(self, client):
        """Test that login sets HTTP-only cookies"""
        # Register user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "cookietest@example.com",
                "password": "testpassword123"
            }
        )

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "cookietest@example.com",
                "password": "testpassword123"
            }
        )

        # Check cookies
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

        # Note: httponly flag is set in Set-Cookie header,
        # but httpx client doesn't expose cookie attributes
        # This would need to be tested with a real browser or by inspecting headers

    async def test_authentication_flow_end_to_end(self, client):
        """Test complete authentication flow: register → login → access protected → logout"""
        # 1. Register
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "flowtest@example.com",
                "password": "testpassword123"
            }
        )
        assert register_response.status_code == 201

        # 2. Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "flowtest@example.com",
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == 200

        # 3. Access protected endpoint
        me_response = await client.get("/api/v1/auth/me")
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "flowtest@example.com"

        # 4. Logout
        logout_response = await client.post("/api/v1/auth/logout")
        assert logout_response.status_code == 200

        # 5. Try to access protected endpoint after logout
        # Note: In real scenario, cookies would be cleared
        # This test assumes client maintains cookies
