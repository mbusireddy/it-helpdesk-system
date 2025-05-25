import pytest
import httpx
from app.main import app
from app.models.database import init_default_users

@pytest.fixture
def client():
    """Create test client"""
    with httpx.Client(app=app, base_url="http://testserver") as client:
        yield client

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Setup test database with default users"""
    init_default_users()

@pytest.fixture
def auth_headers(client):
    """Get authentication headers for regular user"""
    response = client.post("/login", json={
        "username": "appuser",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def support_auth_headers(client):
    """Get authentication headers for support engineer"""
    response = client.post("/login", json={
        "username": "support-engineer",
        "password": "support123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint(client, auth_headers):
    response = client.post(
        "/chat",
        json={
            "content": "My computer won't start",
            "user_id": "test_user_123"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data
    assert "agent" in data

def test_analytics_endpoint(client, auth_headers):
    response = client.get("/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_tickets" in data
    assert "open_tickets" in data
    assert "resolved_tickets" in data

def test_chat_without_auth(client):
    """Test that chat endpoint requires authentication"""
    response = client.post(
        "/chat",
        json={
            "content": "My computer won't start",
            "user_id": "test_user_123"
        }
    )
    assert response.status_code == 401

def test_analytics_without_auth(client):
    """Test that analytics endpoint requires authentication"""
    response = client.get("/analytics/dashboard")
    assert response.status_code == 401

def test_support_engineer_endpoints(client, support_auth_headers):
    """Test support engineer specific endpoints"""
    # Test getting all tickets
    response = client.get("/tickets/all", headers=support_auth_headers)
    assert response.status_code == 200
    
    # Test updating ticket status (create a ticket first)
    chat_response = client.post(
        "/chat",
        json={
            "content": "Test ticket for update",
            "user_id": "test_user_456"
        },
        headers=support_auth_headers
    )
    assert chat_response.status_code == 200
    
    # Get ticket ID from analytics
    analytics_response = client.get("/analytics/dashboard", headers=support_auth_headers)
    assert analytics_response.status_code == 200

def test_regular_user_cannot_access_support_endpoints(client, auth_headers):
    """Test that regular users cannot access support engineer endpoints"""
    # Regular user should not access all tickets
    response = client.get("/tickets/all", headers=auth_headers)
    assert response.status_code == 403
    
    # Regular user should not update ticket status
    response = client.put(
        "/ticket/update",
        json={"ticket_id": 1, "status": "resolved"},
        headers=auth_headers
    )
    assert response.status_code == 403