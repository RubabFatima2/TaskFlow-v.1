import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthCheck:
    """Integration tests for health check endpoint"""

    async def test_health_check_success(self, client):
        """Test GET /api/v1/health returns healthy status"""
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["environment"] == "testing"  # Tests run in testing environment

    async def test_health_check_no_authentication_required(self, client):
        """Test that health check doesn't require authentication"""
        # Don't login, just call health check
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        assert "status" in response.json()
