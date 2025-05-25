import pytest
import httpx
from app.main import app
from app.services.auth_service import auth_service
from app.models.database import User, SessionLocal

@pytest.fixture
def client():
    """Create test client"""
    with httpx.Client(app=app, base_url="http://testserver") as client:
        yield client


class TestAuthentication:
    """Test authentication system functionality"""
    
    def test_login_success_regular_user(self, client):
        """Test successful login for regular user"""
        response = client.post(
            "/login",
            json={
                "username": "appuser",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "appuser"
        assert data["user"]["role"] == "user"
        
    def test_login_success_support_engineer(self, client):
        """Test successful login for support engineer"""
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
        """Test login with invalid credentials"""
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
        """Test login with missing fields"""
        response = client.post(
            "/login",
            json={"username": "appuser"}
        )
        assert response.status_code == 422  # Validation error
        
    def test_me_endpoint_authenticated(self, client):
        """Test /me endpoint with valid token"""
        # First login to get token
        login_response = client.post(
            "/login",
            json={
                "username": "appuser",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Use token to access /me endpoint
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "appuser"
        assert data["role"] == "user"
        assert "last_login" in data
        
    def test_me_endpoint_invalid_token(self, client):
        """Test /me endpoint with invalid token"""
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        assert "Invalid authentication token" in response.json()["detail"]
        
    def test_me_endpoint_no_token(self, client):
        """Test /me endpoint without token"""
        response = client.get("/me")
        assert response.status_code == 403  # No authentication provided


class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def get_user_token(self, client):
        """Helper: Get token for regular user"""
        response = client.post(
            "/login",
            json={"username": "appuser", "password": "password123"}
        )
        return response.json()["access_token"]
        
    def get_support_token(self, client):
        """Helper: Get token for support engineer"""
        response = client.post(
            "/login", 
            json={"username": "support-engineer", "password": "support123"}
        )
        return response.json()["access_token"]
        
    def test_regular_user_denied_support_endpoints(self, client):
        """Test that regular users cannot access support-only endpoints"""
        token = self.get_user_token(client)
        
        # Try to access all tickets (support only)
        response = client.get(
            "/tickets/all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        assert "Support engineer access required" in response.json()["detail"]
        
    def test_support_engineer_access_all_tickets(self, client):
        """Test that support engineers can access all tickets"""
        token = self.get_support_token(client)
        
        response = client.get(
            "/tickets/all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        
    def test_support_engineer_update_ticket(self, client):
        """Test that support engineers can update tickets"""
        token = self.get_support_token(client)
        
        response = client.put(
            "/ticket/update",
            json={
                "ticket_id": 1,
                "status": "in_progress"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should succeed or return 404 if ticket doesn't exist
        assert response.status_code in [200, 404]
        
    def test_regular_user_denied_ticket_update(self, client):
        """Test that regular users cannot update tickets"""
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
    """Test authentication service methods"""
    
    def test_authenticate_user_valid(self):
        """Test user authentication with valid credentials"""
        user_data = auth_service.authenticate_user("appuser", "password123")
        assert user_data is not None
        assert user_data["username"] == "appuser"
        assert user_data["role"] == "user"
        
    def test_authenticate_user_invalid(self):
        """Test user authentication with invalid credentials"""
        user_data = auth_service.authenticate_user("appuser", "wrong_password")
        assert user_data is None
        
    def test_create_access_token(self):
        """Test JWT token creation"""
        user_data = {
            "username": "test_user",
            "role": "user",
            "full_name": "Test User"
        }
        token = auth_service.create_access_token(user_data)
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long strings
        
    def test_verify_token_valid(self):
        """Test JWT token verification with valid token"""
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
        """Test JWT token verification with invalid token"""
        payload = auth_service.verify_token("invalid_token")
        assert payload is None
        
    def test_is_support_engineer(self):
        """Test support engineer role checking"""
        db = SessionLocal()
        try:
            # Get support engineer user
            support_user = db.query(User).filter(User.username == "support-engineer").first()
            regular_user = db.query(User).filter(User.username == "appuser").first()
            
            if support_user:
                assert auth_service.is_support_engineer(support_user) == True
            if regular_user:
                assert auth_service.is_support_engineer(regular_user) == False
        finally:
            db.close()


class TestUserModel:
    """Test User model functionality"""
    
    def test_password_hashing(self):
        """Test password hashing functionality"""
        password = "test_password_123"
        hashed = User.hash_password(password)
        
        assert hashed != password  # Should be hashed
        assert len(hashed) == 64   # SHA256 produces 64-character hex string
        
    def test_password_verification(self):
        """Test password verification"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "appuser").first()
            if user:
                assert user.check_password("password123") == True
                assert user.check_password("wrong_password") == False
        finally:
            db.close()