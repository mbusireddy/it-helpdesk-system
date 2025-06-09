# ORM session and models
from sqlalchemy.orm import Session
from app.models.database import User, SessionLocal

# For timestamps and token expiry
from datetime import datetime, timedelta

# JWT encoding and decoding
import jwt

# For password hashing (SHA256 used in User model)
import hashlib

# Typing for clarity
from typing import Optional


# ------------- JWT Configuration -------------
SECRET_KEY = "helpdesk-secret-key-change-in-production"  # Replace with a strong secret in production
ALGORITHM = "HS256"  # JWT signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token validity duration


# ------------- AuthService Class -------------
class AuthService:
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[dict]:
        """
        Authenticates the user by verifying the username and hashed password.

        Returns:
            dict: Basic user info if authenticated.
            None: If authentication fails.
        """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user and user.check_password(password) and user.is_active:
                # Update last login timestamp
                user.last_login = datetime.utcnow()
                db.commit()
                
                # Return selected user info (avoid returning full SQLAlchemy object)
                return {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "full_name": user.full_name,
                    "email": user.email,
                    "last_login": user.last_login
                }
            return None
        finally:
            db.close()

    @staticmethod
    def create_access_token(user_data: dict) -> str:
        """
        Generates a JWT token for the authenticated user.

        Args:
            user_data (dict): User details (must include username, role, full_name)

        Returns:
            str: Encoded JWT token
        """
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": user_data["username"],        # Subject = username
            "role": user_data["role"],
            "full_name": user_data["full_name"],
            "exp": expire                        # Expiry claim
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Validates and decodes a JWT token.

        Returns:
            dict: Payload if valid
            None: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Fetch user from the database using their username.
        Useful for token validation and role checks.
        """
        db = SessionLocal()
        try:
            return db.query(User).filter(User.username == username).first()
        finally:
            db.close()

    @staticmethod
    def is_support_engineer(user: User) -> bool:
        """
        Utility to check if a user has the support engineer role.
        Useful for role-based authorization.
        """
        return user.role == "support-engineer"


# Singleton instance of AuthService
auth_service = AuthService()
