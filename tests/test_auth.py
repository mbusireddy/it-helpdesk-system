# Importing Libraries

import pytest
import httpx
from app.main import app
from app.services.auth_service import auth_service
from app.models.database import User, SessionLocal

@pytest.fixture
def client():
    """
    Pytest fixture to create an HTTP client for testing the FastAPI app.
    Uses httpx.Client with ASGI app instance and a fake base URL for isolated tests.
    Yields the client for use in tests, then cleans up after.
    """
    with httpx.Client(app=app, base_url="http://testserver") as client:
        yield client


class TestAuthentication:
    """Tests related to authentication endpoints and behavior"""

    def test_login_success_regular_user(self, client):
        """
        Test that a regular user can successfully log in.
        Sends POST /login with valid username/password.
        Expects 200 OK and valid JWT token in response along with user info.
        """
        response = client.post(
            "/login",
            json={
                "username": "appuser",
                "password": "password123"
            }
        )
        assert response.status_code == 200  # HTTP success
        data = response.json()
        assert "access_token" in data  # JWT token included
        assert data["token_type"] == "bearer"  # Correct token type
        assert data["user"]["username"] == "appuser"  # User info correctness
        assert data["user"]["role"] == "user"  # Role is 'user'

    def test_login_success_support_engineer(self, client):
        """
        Test that a support engineer can successfully log in.
        Similar to regular user test but different username and role.
        """
        response = client.post(
            "/login",
            json={
                "username": "support-engineer",
                "password": "support123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "support-engineer"
        assert data["user"]["role"] == "support-engineer"

    def test_login_invalid_credentials(self, client):
        """
        Test login with invalid username/password.
        Should return 401 Unauthorized with appropriate error detail.
        """
        response = client.post(
            "/login",
            json={
                "username": "invalid_user",
                "password": "wrong_password"
            }
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    def test_login_missing_fields(self, client):
        """
        Test login request with missing required fields (password missing).
        Should return 422 Unprocessable Entity (validation error).
        """
        response = client.post(
            "/login",
            json={"username": "appuser"}  # no password
        )
        assert response.status_code == 422

    def test_me_endpoint_authenticated(self, client):
        """
        Test /me endpoint which returns current user info.
        Requires valid Bearer token obtained from login.
        """
        # Login first to get token
        login_response = client.post(
            "/login",
            json={
                "username": "appuser",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]

        # Use token to call /me endpoint
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "appuser"
        assert data["role"] == "user"
        assert "last_login" in data  # last login info should be present

    def test_me_endpoint_invalid_token(self, client):
        """
        Test /me endpoint with an invalid token.
        Should respond with 401 Unauthorized and an appropriate error message.
        """
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        assert "Invalid authentication token" in response.json()["detail"]

    def test_me_endpoint_no_token(self, client):
        """
        Test /me endpoint without any authentication token.
        Should respond with 403 Forbidden (access denied).
        """
        response = client.get("/me")
        assert response.status_code == 403


class TestRoleBasedAccess:
    """Tests for role-based access control enforcement"""

    def get_user_token(self, client):
        """Helper method to get JWT token for regular user."""
        response = client.post(
            "/login",
            json={"username": "appuser", "password": "password123"}
        )
        return response.json()["access_token"]

    def get_support_token(self, client):
        """Helper method to get JWT token for support engineer."""
        response = client.post(
            "/login",
            json={"username": "support-engineer", "password": "support123"}
        )
        return response.json()["access_token"]

    def test_regular_user_denied_support_endpoints(self, client):
        """
        Ensure regular users cannot access support engineer-only endpoints.
        Tries to access /tickets/all and expects 403 Forbidden with error detail.
        """
        token = self.get_user_token(client)

        response = client.get(
            "/tickets/all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        assert "Support engineer access required" in response.json()["detail"]

    def test_support_engineer_access_all_tickets(self, client):
        """
        Ensure support engineers can access /tickets/all endpoint.
        Should return 200 OK and a list of tickets (JSON array).
        """
        token = self.get_support_token(client)

        response = client.get(
            "/tickets/all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_support_engineer_update_ticket(self, client):
        """
        Test support engineers can update ticket status via /ticket/update.
        Acceptable response codes are 200 OK (success) or 404 Not Found (if ticket does not exist).
        """
        token = self.get_support_token(client)

        response = client.put(
            "/ticket/update",
            json={
                "ticket_id": 1,
                "status": "in_progress"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 404]

    def test_regular_user_denied_ticket_update(self, client):
        """
        Ensure regular users cannot update ticket status.
        Should return 403 Forbidden with access denied message.
        """
        token = self.get_user_token(client)

        response = client.put(
            "/ticket/update",
            json={
                "ticket_id": 1,
                "status": "resolved"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        assert "Support engineer access required" in response.json()["detail"]


class TestAuthService:
    """Tests for the authentication service methods directly (not through HTTP)"""

    def test_authenticate_user_valid(self):
        """
        Test authenticating with valid username and password.
        Should return user data dictionary.
        """
        user_data = auth_service.authenticate_user("appuser", "password123")
        assert user_data is not None
        assert user_data["username"] == "appuser"
        assert user_data["role"] == "user"

    def test_authenticate_user_invalid(self):
        """
        Test authenticating with invalid password.
        Should return None (authentication failed).
        """
        user_data = auth_service.authenticate_user("appuser", "wrong_password")
        assert user_data is None

    def test_create_access_token(self):
        """
        Test that the service can create a JWT access token.
        The token should be a string and sufficiently long.
        """
        user_data = {
            "username": "test_user",
            "role": "user",
            "full_name": "Test User"
        }
        token = auth_service.create_access_token(user_data)
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens tend to be long strings

    def test_verify_token_valid(self):
        """
        Test verifying a valid JWT token.
        Should return the payload containing expected claims like subject and role.
        """
        user_data = {
            "username": "test_user",
            "role": "user",
            "full_name": "Test User"
        }
        token = auth_service.create_access_token(user_data)
        payload = auth_service.verify_token(token)

        assert payload is not None
        assert payload["sub"] == "test_user"
        assert payload["role"] == "user"

    def test_verify_token_invalid(self):
        """
        Test verifying an invalid JWT token string.
        Should return None indicating token is invalid or expired.
        """
        payload = auth_service.verify_token("invalid_token")
        assert payload is None

    def test_is_support_engineer(self):
        """
        Test the helper method that checks if a User model instance is a support engineer.
        Queries the database for known users and checks their roles.
        """
        db = SessionLocal()
        try:
            support_user = db.query(User).filter(User.username == "support-engineer").first()
            regular_user = db.query(User).filter(User.username == "appuser").first()

            if support_user:
                assert auth_service.is_support_engineer(support_user) is True
            if regular_user:
                assert auth_service.is_support_engineer(regular_user) is False
        finally:
            db.close()


class TestUserModel:
    """Tests for User ORM model password handling"""

    def test_password_hashing(self):
        """
        Test that hashing a password produces a different string than original,
        and that the hash length matches SHA256 hex digest length (64 chars).
        """
        password = "test_password_123"
        hashed = User.hash_password(password)

        assert hashed != password
        assert len(hashed) == 64

    def test_password_verification(self):
        """
        Test password verification against stored password hash in the database.
        Checks that correct password verifies true, incorrect password false.
        """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "appuser").first()
            if user:
                assert user.check_password("password123") is True
                assert user.check_password("wrong_password") is False
        finally:
            db.close()
