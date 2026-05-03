import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set test environment BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["BETTER_AUTH_SECRET"] = "155125933e275be470192de9d9bcd7203137c1150afe89cc81e7bdbea15ee1e3"
os.environ["ENVIRONMENT"] = "testing"

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

# Create test session factory
test_session_maker = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_test_session():
    """Override database session for tests"""
    async with test_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def test_db():
    """Create test database tables before each test and drop after"""
    # Import models to ensure they're registered
    from app.models.user import User
    from app.models.task import Task

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(test_db):
    """Create test client with test database"""
    # Import app after environment is set
    from app.main import app
    from app.database import get_session
    from app import database

    # Override the engine and session maker in the database module
    original_engine = database.engine
    original_session_maker = database.async_session_maker

    database.engine = test_engine
    database.async_session_maker = test_session_maker

    # Override the dependency
    app.dependency_overrides[get_session] = get_test_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    # Restore original engine and session maker
    database.engine = original_engine
    database.async_session_maker = original_session_maker
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(client):
    """Create a test user and return user data"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    user_response = response.json()
    # Add password to returned data for login tests
    user_response["password"] = user_data["password"]

    return user_response


@pytest.fixture
async def authenticated_client(client, test_user):
    """Create an authenticated test client"""
    # Login to get authentication cookies
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert login_response.status_code == 200

    return client
