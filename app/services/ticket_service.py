from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.database import Ticket, ChatLog, get_db  # Importing ORM models and DB session generator
from app.utils.logger import logger  # Logger for tracking info and errors
from datetime import datetime  # To handle timestamps
import uuid  # Imported but unused in current code


class TicketService:
    def __init__(self):
        """
        Initialize the TicketService.
        Currently, no instance variables or setup required here.
        """
        pass

    def create_ticket(self,
                      user_id: str,
                      category: str,
                      title: str,
                      description: str,
                      priority: str = "medium") -> Ticket:
        """
        Creates a new ticket record in the database.

        Args:
            user_id (str): The ID of the user submitting the ticket.
            category (str): The ticket category (e.g., IT_HARDWARE, HR).
            title (str): Brief title describing the issue.
            description (str): Detailed explanation of the issue.
            priority (str, optional): Urgency of the ticket; defaults to "medium".

        Returns:
            Ticket: The Ticket object created with database-generated attributes like `id`.

        Process:
            - Gets a new DB session from the `get_db` generator.
            - Creates a Ticket object and sets default status to "open".
            - Adds the ticket to the session and commits the transaction.
            - Refreshes the ticket instance to load DB-generated values (like auto-incremented ID).
            - Logs successful ticket creation.
            - Rolls back and logs if any exception occurs.
            - Ensures DB session is closed to free resources.
        """
        db = next(get_db())  # Acquire a new database session
        try:
            ticket = Ticket(
                user_id=user_id,
                category=category,
                title=title,
                description=description,
                priority=priority,
                status="open"  # Default status for a new ticket
            )
            db.add(ticket)    # Add ticket to the current DB transaction
            db.commit()       # Commit transaction to persist ticket in DB
            db.refresh(ticket)  # Refresh to get updated fields like `id`
            logger.info(f"Created ticket {ticket.id} for user {user_id}")
            return ticket
        except Exception as e:
            db.rollback()  # Undo any DB changes on error to maintain integrity
            logger.error(f"Error creating ticket: {e}")
            raise  # Propagate exception to calling code
        finally:
            db.close()  # Always release DB connection

    def get_ticket_status(self, ticket_id: int) -> Optional[Ticket]:
        """
        Fetch the details of a ticket by its ID.

        Args:
            ticket_id (int): Unique identifier of the ticket.

        Returns:
            Optional[Ticket]: Ticket object if found; otherwise None.

        Notes:
            - Uses a fresh DB session to query by ticket ID.
            - Closes session after query to avoid connection leaks.
        """
        db = next(get_db())  # Start DB session
        try:
            return db.query(Ticket).filter(Ticket.id == ticket_id).first()
        finally:
            db.close()  # Clean up DB session

    def get_user_tickets(self, user_id: str) -> List[Ticket]:
        """
        Retrieve all tickets submitted by a specific user.

        Args:
            user_id (str): Unique identifier of the user.

        Returns:
            List[Ticket]: List containing all tickets for the user.

        Purpose:
            - Helps in showing ticket history or managing tickets per user.
            - Closes DB session to release resources.
        """
        db = next(get_db())  # Open DB session
        try:
            return db.query(Ticket).filter(Ticket.user_id == user_id).all()
        finally:
            db.close()  # Close DB session

    def update_ticket_status(self, ticket_id: int, status: str, resolution: str = None):
        """
        Update the status of an existing ticket, optionally including resolution details.

        Args:
            ticket_id (int): ID of the ticket to update.
            status (str): New status value (e.g., "open", "resolved", "in-progress").
            resolution (str, optional): Details on how the ticket was resolved.

        Workflow:
            - Fetch the ticket from DB by ID.
            - Update its status and the `updated_at` timestamp.
            - If status is "resolved", set `resolved_at` timestamp.
            - Optionally, store resolution notes (if provided).
            - Commit changes to DB.
            - Log the update action.
            - On exception, rollback and log error.
            - Close DB session to free resources.
        """
        db = next(get_db())  # Get DB session
        try:
            ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket:
                ticket.status = status
                ticket.updated_at = datetime.utcnow()

                if status == "resolved":
                    ticket.resolved_at = datetime.utcnow()
                    if resolution:
                        ticket.resolution = resolution  # Add resolution details

                db.commit()  # Persist changes
                logger.info(f"Updated ticket {ticket_id} status to {status}")
        except Exception as e:
            db.rollback()  # Rollback changes on error
            logger.error(f"Error updating ticket: {e}")
        finally:
            db.close()  # Always close DB session

    def log_chat(self, session_id: str, user_message: str, agent_response: str,
                 agent_type: str, ticket_id: int = None):
        """
        Log a chat interaction between user and support system (bot or agent).

        Args:
            session_id (str): Unique session ID for this chat conversation.
            user_message (str): Message sent by the user.
            agent_response (str): Reply from the agent or bot.
            agent_type (str): Type of agent ("bot", "human", etc.).
            ticket_id (int, optional): Related ticket ID if chat is associated.

        Functionality:
            - Creates a ChatLog record in DB with all provided details.
            - Commits transaction to save chat log.
            - Rollbacks and logs any exceptions.
            - Closes DB session after operation.
        """
        db = next(get_db())  # Start DB session
        try:
            chat_log = ChatLog(
                session_id=session_id,
                user_message=user_message,
                agent_response=agent_response,
                agent_type=agent_type,
                ticket_id=ticket_id
            )
            db.add(chat_log)  # Add chat log entry
            db.commit()       # Commit transaction
        except Exception as e:
            db.rollback()  # Undo partial changes on error
            logger.error(f"Error logging chat: {e}")
        finally:
            db.close()  # Release DB connection


# Singleton instance for reuse across the app to avoid multiple initializations
ticket_service = TicketService()
