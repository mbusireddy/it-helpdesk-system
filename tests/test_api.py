# Importing libraries

import pytest
import httpx
from app.main import app
from app.models.database import init_default_users

@pytest.fixture
def client():
    """
    Creates a test HTTP client for the FastAPI app using httpx.
    The client is used to send requests to API endpoints during tests.
    The base_url is set to a fake local server for isolated testing.
    """
    with httpx.Client(app=app, base_url="http://testserver") as client:
        yield client  # Provide the client to tests, clean up after test finishes

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """
    Sets up the test database once per test module before any tests run.
    It initializes the database with default users, ensuring consistent state for authentication tests.
    The fixture runs automatically for all tests due to autouse=True.
    """
    init_default_users()

@pytest.fixture
def auth_headers(client):
    """
    Logs in as a regular user and returns authorization headers with the bearer token.
    This fixture simulates a user login to authenticate API requests that require it.
    """
    response = client.post("/login", json={
        "username": "appuser",
        "password": "password123"
    })
    assert response.status_code == 200  # Ensure login succeeded

    token = response.json()["access_token"]  # Extract JWT token from login response
    return {"Authorization": f"Bearer {token}"}  # Return headers with token for authenticated requests

@pytest.fixture
def support_auth_headers(client):
    """
    Logs in as a support engineer user and returns authorization headers with bearer token.
    Used for testing endpoints restricted to support engineer role.
    """
    response = client.post("/login", json={
        "username": "support-engineer",
        "password": "support123"
    })
    assert response.status_code == 200

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_health_check(client):
    """
    Tests the /health endpoint to ensure the API is running and healthy.
    Verifies status code 200 and that response JSON contains 'status': 'healthy'.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint(client, auth_headers):
    """
    Tests the /chat endpoint with authenticated user headers.
    Sends a chat message and verifies the response contains expected fields like
    'response' (the chat reply), 'session_id', and 'agent' (which handled the query).
    """
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
    # Validate the response contains necessary fields to continue the chat session
    assert "response" in data
    assert "session_id" in data
    assert "agent" in data

def test_analytics_endpoint(client, auth_headers):
    """
    Tests the analytics dashboard endpoint for an authenticated user.
    Verifies that the response contains expected ticket-related summary stats.
    """
    response = client.get("/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    # Check that analytics data includes these key fields
    assert "total_tickets" in data
    assert "open_tickets" in data
    assert "resolved_tickets" in data

def test_chat_without_auth(client):
    """
    Tests that the /chat endpoint rejects unauthenticated requests.
    Sending a chat message without auth headers should return 401 Unauthorized.
    """
    response = client.post(
        "/chat",
        json={
            "content": "My computer won't start",
            "user_id": "test_user_123"
        }
    )
    assert response.status_code == 401

def test_analytics_without_auth(client):
    """
    Tests that the analytics dashboard endpoint rejects unauthenticated requests.
    """
    response = client.get("/analytics/dashboard")
    assert response.status_code == 401

def test_support_engineer_endpoints(client, support_auth_headers):
    """
    Tests support engineer specific endpoints that require special privileges:
    - Access to all tickets list
    - Ability to update ticket status (implicitly tested via chat and analytics)

    Verifies these endpoints return success for support engineer auth.
    """
    # Support engineer gets all tickets
    response = client.get("/tickets/all", headers=support_auth_headers)
    assert response.status_code == 200

    # Create a new ticket via chat to have a ticket to update later
    chat_response = client.post(
        "/chat",
        json={
            "content": "Test ticket for update",
            "user_id": "test_user_456"
        },
        headers=support_auth_headers
    )
    assert chat_response.status_code == 200

    # Fetch analytics dashboard to potentially get ticket info
    analytics_response = client.get("/analytics/dashboard", headers=support_auth_headers)
    assert analytics_response.status_code == 200

def test_regular_user_cannot_access_support_endpoints(client, auth_headers):
    """
    Ensures that a regular authenticated user cannot access support-engineer only endpoints,
    such as:
    - Getting all tickets
    - Updating ticket status

    These should return 403 Forbidden for regular users.
    """
    # Regular user should be forbidden from listing all tickets
    response = client.get("/tickets/all", headers=auth_headers)
    assert response.status_code == 403

    # Regular user should be forbidden from updating ticket status
    response = client.put(
        "/ticket/update",
        json={"ticket_id": 1, "status": "resolved"},
        headers=auth_headers
    )
    assert response.status_code == 403
