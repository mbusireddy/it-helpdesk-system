from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.database import Ticket, ChatLog, get_db
from app.utils.logger import logger
from datetime import datetime
import uuid


class TicketService:
    def __init__(self):
        pass

    def create_ticket(self,
                      user_id: str,
                      category: str,
                      title: str,
                      description: str,
                      priority: str = "medium") -> Ticket:
        db = next(get_db())
        try:
            ticket = Ticket(
                user_id=user_id,
                category=category,
                title=title,
                description=description,
                priority=priority,
                status="open"
            )
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            logger.info(f"Created ticket {ticket.id} for user {user_id}")
            return ticket
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating ticket: {e}")
            raise
        finally:
            db.close()

    def get_ticket_status(self, ticket_id: int) -> Optional[Ticket]:
        db = next(get_db())
        try:
            return db.query(Ticket).filter(Ticket.id == ticket_id).first()
        finally:
            db.close()

    def get_user_tickets(self, user_id: str) -> List[Ticket]:
        db = next(get_db())
        try:
            return db.query(Ticket).filter(Ticket.user_id == user_id).all()
        finally:
            db.close()

    def update_ticket_status(self, ticket_id: int, status: str, resolution: str = None):
        db = next(get_db())
        try:
            ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket:
                ticket.status = status
                ticket.updated_at = datetime.utcnow()
                if status == "resolved":
                    ticket.resolved_at = datetime.utcnow()
                db.commit()
                logger.info(f"Updated ticket {ticket_id} status to {status}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating ticket: {e}")
        finally:
            db.close()

    def log_chat(self, session_id: str, user_message: str, agent_response: str,
                 agent_type: str, ticket_id: int = None):
        db = next(get_db())
        try:
            chat_log = ChatLog(
                session_id=session_id,
                user_message=user_message,
                agent_response=agent_response,
                agent_type=agent_type,
                ticket_id=ticket_id
            )
            db.add(chat_log)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error logging chat: {e}")
        finally:
            db.close()


ticket_service = TicketService()
