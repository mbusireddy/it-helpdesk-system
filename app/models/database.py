# Import necessary SQLAlchemy components for ORM modeling
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# Import standard datetime module for timestamps
from datetime import datetime

# Import application settings (e.g., database URL)
from app.utils.config import settings

# For hashing passwords securely
import hashlib

# Define base class for SQLAlchemy models
Base = declarative_base()


# -------------------- User Model --------------------
class User(Base):
    __tablename__ = "users"  # Table name in the database

    # Columns for the User table
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)  # Store hashed passwords only
    role = Column(String, nullable=False)  # 'user' or 'support-engineer'
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)  # Auto timestamp
    last_login = Column(DateTime, nullable=True)

    def check_password(self, password: str) -> bool:
        """
        Verify provided password against stored hash
        """
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Generate hash from plaintext password
        """
        return hashlib.sha256(password.encode()).hexdigest()


# -------------------- Ticket Model --------------------
class Ticket(Base):
    __tablename__ = "tickets"

    # Columns for the Ticket table
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)  # ForeignKey not used since user management is basic
    assigned_to = Column(String, nullable=True)  # Username of assigned support engineer
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default="medium")  # Can be 'low', 'medium', or 'high'
    status = Column(String, default="open")  # Can be 'open', 'in_progress', 'closed', etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # One-to-many relationship: Ticket has multiple ChatLogs
    chat_logs = relationship("ChatLog", back_populates="ticket")


# -------------------- ChatLog Model --------------------
class ChatLog(Base):
    __tablename__ = "chat_logs"

    # Columns for the ChatLog table
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)  # Session identifier
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    agent_type = Column(String, nullable=False)  # IT, HR, Accounting, etc.
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to ticket (many chat logs belong to one ticket)
    ticket = relationship("Ticket", back_populates="chat_logs")


# -------------------- Database Setup --------------------

# Create the SQLAlchemy database engine using settings
engine = create_engine(settings.database_url, echo=False)

# Create a session factory to generate DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all defined tables in the database
Base.metadata.create_all(bind=engine)


# -------------------- Default Users Initialization --------------------

def init_default_users():
    """
    Create default users (one normal user, one support engineer)
    if the users table is empty.
    """
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return  # Skip creation if users already exist

        default_users = [
            {
                "username": "appuser",
                "password": "password123",
                "role": "user",
                "full_name": "Application User",
                "email": "appuser@example.com"
            },
            {
                "username": "support-engineer", 
                "password": "support123",
                "role": "support-engineer",
                "full_name": "Support Engineer",
                "email": "support@example.com"
            }
        ]

        # Add each user to the DB with hashed password
        for user_data in default_users:
            user = User(
                username=user_data["username"],
                password_hash=User.hash_password(user_data["password"]),
                role=user_data["role"],
                full_name=user_data["full_name"],
                email=user_data["email"]
            )
            db.add(user)

        db.commit()
        print("Default users created successfully")
        
    except Exception as e:
        print(f"Error creating default users: {e}")
        db.rollback()
    finally:
        db.close()

# Run default user initializer on startup
init_default_users()


# -------------------- FastAPI Dependency --------------------

def get_db() -> Session:
    """
    Dependency for FastAPI endpoints to access a DB session.
    Automatically closes session after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
