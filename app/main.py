from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from app.agents.workflow import helpdesk_workflow, HelpDeskState
from app.services.ticket_service import ticket_service
from app.services.auth_service import auth_service
from app.models.database import get_db, Ticket, User, SessionLocal
from app.utils.logger import logger
from datetime import datetime

# Initialize FastAPI app with basic metadata
app = FastAPI(title="IT Helpdesk System", version="1.0.0")

# Enable CORS for all origins, methods, and headers (for development; tighten for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation and serialization

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class ChatMessage(BaseModel):
    content: str
    user_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    agent: str
    ticket_id: Optional[int] = None

class TicketStatusRequest(BaseModel):
    ticket_id: int

class TicketUpdateRequest(BaseModel):
    ticket_id: int
    status: str
    assigned_to: Optional[str] = None

class TicketResponse(BaseModel):
    id: int
    status: str
    category: str
    title: str
    description: str
    created_at: str
    updated_at: str
    assigned_to: Optional[str] = None

# Security setup: HTTP Bearer token scheme for authentication
security = HTTPBearer()

# Dependency to get current user from Bearer token, validate token, and fetch user from DB
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    payload = auth_service.verify_token(token)  # Validate JWT token
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    user = auth_service.get_user_by_username(payload.get("sub"))  # Get user by username from token payload
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Dependency to ensure user has support engineer privileges
async def get_support_engineer(current_user: User = Depends(get_current_user)) -> User:
    if not auth_service.is_support_engineer(current_user):
        raise HTTPException(status_code=403, detail="Support engineer access required")
    return current_user

# In-memory dictionary to track active chat sessions (replace with Redis for production)
active_sessions = {}

# User login endpoint - authenticates user and returns JWT token
@app.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """Authenticate user and return access token"""
    user_data = auth_service.authenticate_user(login_request.username, login_request.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = auth_service.create_access_token(user_data)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "username": user_data["username"],
            "full_name": user_data["full_name"],
            "role": user_data["role"],
            "email": user_data["email"]
        }
    )

# Get current authenticated user's profile info
@app.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Fetch profile details of the logged-in user"""
    return {
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "email": current_user.email,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

# Chat endpoint - handles user messages, manages session state, and invokes helpdesk workflow
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    try:
        # Use existing session_id or generate a new one for chat context
        session_id = message.session_id or str(uuid.uuid4())

        # Initialize session state if new session
        if session_id not in active_sessions:
            initial_state: HelpDeskState = {
                "messages": [],
                "current_agent": "classifier",
                "category": "",
                "user_id": message.user_id,
                "session_id": session_id,
                "context": {},
                "ticket_id": 0,
                "resolution_status": "",
                "conversation_stage": "initial",
                "needs_ticket": False
            }
            active_sessions[session_id] = initial_state

        state = active_sessions[session_id]

        # Add user's message to conversation state
        state["messages"].append({
            "role": "user",
            "content": message.content
        })

        # Process the message through the AI-powered helpdesk workflow
        result = await helpdesk_workflow.workflow.ainvoke(state)

        # Update session state with workflow output
        active_sessions[session_id] = result

        # Extract last assistant response message
        last_response = None
        for msg in reversed(result["messages"]):
            if msg["role"] == "assistant":
                last_response = msg
                break

        # Default response if assistant has no reply
        if not last_response:
            last_response = {
                "content": "I'm here to help! How can I assist you today?",
                "agent": "system"
            }

        # Return chat response with session context and optional ticket info
        return ChatResponse(
            response=last_response["content"],
            session_id=session_id,
            agent=last_response.get("agent", "system"),
            ticket_id=result.get("ticket_id")
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint to get status/details of a specific ticket by ticket ID
@app.post("/ticket/status", response_model=TicketResponse)
async def get_ticket_status(request: TicketStatusRequest):
    try:
        ticket = ticket_service.get_ticket_status(request.ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        # Serialize ticket data for response
        return TicketResponse(
            id=ticket.id,
            status=ticket.status,
            category=ticket.category,
            title=ticket.title,
            description=ticket.description,
            created_at=ticket.created_at.isoformat(),
            updated_at=ticket.updated_at.isoformat(),
            assigned_to=ticket.assigned_to
        )
    except Exception as e:
        logger.error(f"Error getting ticket status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get all tickets raised by a specific user
@app.get("/tickets/user/{user_id}")
async def get_user_tickets(user_id: str):
    try:
        tickets = ticket_service.get_user_tickets(user_id)
        # Return list of tickets with details
        return [
            TicketResponse(
                id=ticket.id,
                status=ticket.status,
                category=ticket.category,
                title=ticket.title,
                description=ticket.description,
                created_at=ticket.created_at.isoformat(),
                updated_at=ticket.updated_at.isoformat(),
                assigned_to=ticket.assigned_to
            )
            for ticket in tickets
        ]
    except Exception as e:
        logger.error(f"Error getting user tickets: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Support engineer only: Update ticket status and optionally assign engineer
@app.put("/ticket/update", response_model=TicketResponse)
async def update_ticket_status(
    request: TicketUpdateRequest, 
    support_engineer: User = Depends(get_support_engineer)
):
    """Update status and assignment of a ticket - only support engineers allowed"""
    try:
        db = SessionLocal()
        ticket = db.query(Ticket).filter(Ticket.id == request.ticket_id).first()
        
        if not ticket:
            db.close()
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Update ticket status and assignment
        ticket.status = request.status
        if request.assigned_to:
            ticket.assigned_to = request.assigned_to
        else:
            ticket.assigned_to = support_engineer.username
        
        ticket.updated_at = datetime.utcnow()
        
        # Mark resolved_at timestamp if ticket is resolved
        if request.status.lower() == "resolved":
            ticket.resolved_at = datetime.utcnow()
        
        db.commit()
        
        # Prepare response model
        result = TicketResponse(
            id=ticket.id,
            status=ticket.status,
            category=ticket.category,
            title=ticket.title,
            description=ticket.description,
            created_at=ticket.created_at.isoformat(),
            updated_at=ticket.updated_at.isoformat(),
            assigned_to=ticket.assigned_to
        )
        
        db.close()
        logger.info(f"Ticket {ticket.id} updated by support engineer {support_engineer.username}")
        return result
        
    except Exception as e:
        logger.error(f"Error updating ticket: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Support engineer only: Fetch all tickets in the system
@app.get("/tickets/all")
async def get_all_tickets(support_engineer: User = Depends(get_support_engineer)):
    """Retrieve all tickets - support engineers only"""
    try:
        db = SessionLocal()
        tickets = db.query(Ticket).all()
        db.close()
        
        # Return list of all tickets with details
        return [
            TicketResponse(
                id=ticket.id,
                status=ticket.status,
                category=ticket.category,
                title=ticket.title,
                description=ticket.description,
                created_at=ticket.created_at.isoformat(),
                updated_at=ticket.updated_at.isoformat(),
                assigned_to=ticket.assigned_to
            )
            for ticket in tickets
        ]
    except Exception as e:
        logger.error(f"Error getting all tickets: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Analytics dashboard endpoint to provide summary statistics on tickets
@app.get("/analytics/dashboard")
async def get_dashboard_analytics():
    try:
        from sqlalchemy import func
        from app.models.database import SessionLocal

        db = SessionLocal()

        # Count total, open, and resolved tickets
        total_tickets = db.query(Ticket).count()
        open_tickets = db.query(Ticket).filter(Ticket.status == 'open').count()
        resolved_tickets = db.query(Ticket).filter(Ticket.status == 'resolved').count()

        # Group tickets by category and count them
        category_stats = db.query(
            Ticket.category,
            func.count(Ticket.id).label('count')
        ).group_by(Ticket.category).all()

        db.close()

        # Calculate resolution rate and format category data
        return {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "resolved_tickets": resolved_tickets,
            "resolution_rate": (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0,
            "category_breakdown": [
                {"category": cat, "count": count}
                for cat, count in category_stats
            ]
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Simple health check endpoint to verify service status
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "IT Helpdesk System"}


# Run app with Uvicorn if executed as main program
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
