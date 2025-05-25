from sqlalchemy.orm import Session
from app.models.database import User, SessionLocal
from datetime import datetime, timedelta
import jwt
import hashlib
from typing import Optional

SECRET_KEY = "helpdesk-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[dict]:
        """Authenticate user with username and password"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user and user.check_password(password) and user.is_active:
                # Update last login
                user.last_login = datetime.utcnow()
                db.commit()
                # Return user data as dict to avoid detached instance issues
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
        """Create JWT access token for user"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": user_data["username"],
            "role": user_data["role"],
            "full_name": user_data["full_name"],
            "exp": expire
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify JWT token and return user data"""
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
        """Get user by username"""
        db = SessionLocal()
        try:
            return db.query(User).filter(User.username == username).first()
        finally:
            db.close()
    
    @staticmethod
    def is_support_engineer(user: User) -> bool:
        """Check if user has support engineer role"""
        return user.role == "support-engineer"


auth_service = AuthService()