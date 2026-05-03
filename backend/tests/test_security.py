import pytest
from httpx import AsyncClient
from app.main import app
from app.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_sql_injection_in_login():
    """Test that SQL injection attempts in login are prevented"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Attempt SQL injection in email field
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin' OR '1'='1",
                "password": "password"
            }
        )
        # Should return 401 (invalid credentials), not 500 (SQL error)
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_sql_injection_in_registration():
    """Test that SQL injection attempts in registration are prevented"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test'; DROP TABLE users; --",
                "password": "Password123!"
            }
        )
        # Should either succeed (creating user with that email) or fail validation
        # But should NOT cause SQL error
        assert response.status_code in [201, 400, 409]


@pytest.mark.asyncio
async def test_sql_injection_in_task_title():
    """Test that SQL injection attempts in task title are prevented"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First register and login
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "testuser@example.com",
                "password": "Password123!"
            }
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "Password123!"
            }
        )

        csrf_token = login_response.headers.get("X-CSRF-Token")

        # Attempt SQL injection in task title
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test'; DROP TABLE tasks; --",
                "description": "Test description"
            },
            headers={"X-CSRF-Token": csrf_token}
        )

        # Should succeed (creating task with that title) or fail validation
        # But should NOT cause SQL error
        assert response.status_code in [201, 400, 403]


@pytest.mark.asyncio
async def test_xss_in_task_title():
    """Test that XSS attempts in task title are sanitized"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "xsstest@example.com",
                "password": "Password123!"
            }
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "xsstest@example.com",
                "password": "Password123!"
            }
        )

        csrf_token = login_response.headers.get("X-CSRF-Token")

        # Attempt XSS in task title
        xss_payload = "<script>alert('XSS')</script>"
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": xss_payload,
                "description": "Test description"
            },
            headers={"X-CSRF-Token": csrf_token}
        )

        if response.status_code == 201:
            task_data = response.json()
            # Verify that the script tag is escaped/sanitized
            assert "<script>" not in task_data["title"]
            assert "alert" not in task_data["title"] or "&lt;script&gt;" in task_data["title"]


@pytest.mark.asyncio
async def test_xss_in_task_description():
    """Test that XSS attempts in task description are sanitized"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "xsstest2@example.com",
                "password": "Password123!"
            }
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "xsstest2@example.com",
                "password": "Password123!"
            }
        )

        csrf_token = login_response.headers.get("X-CSRF-Token")

        # Attempt XSS in task description
        xss_payload = '<img src=x onerror="alert(\'XSS\')">'
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": xss_payload
            },
            headers={"X-CSRF-Token": csrf_token}
        )

        if response.status_code == 201:
            task_data = response.json()
            # Verify that the onerror handler is removed/sanitized
            assert "onerror" not in task_data["description"]
            assert "alert" not in task_data["description"] or "onerror" not in task_data["description"]


@pytest.mark.asyncio
async def test_csrf_protection_on_task_creation():
    """Test that CSRF protection is enforced on task creation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "csrftest@example.com",
                "password": "Password123!"
            }
        )

        await client.post(
            "/api/v1/auth/login",
            json={
                "email": "csrftest@example.com",
                "password": "Password123!"
            }
        )

        # Attempt to create task WITHOUT CSRF token
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Test description"
            }
        )

        # Should be rejected with 403 Forbidden
        assert response.status_code == 403
        assert "CSRF" in response.json()["detail"]
