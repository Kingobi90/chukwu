"""Authentication endpoint tests"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "StudyMaster API"


@pytest.mark.asyncio
async def test_login_invalid_token(client: AsyncClient):
    """Test login with invalid Moodle token"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"moodle_token": "invalid_token"}
    )
    # Should fail with 401 due to invalid Moodle token
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing protected endpoint without auth"""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 403  # No authorization header
