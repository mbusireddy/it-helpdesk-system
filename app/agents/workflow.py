from langgraph.graph import StateGraph, END
from typing import Dict, Any, List
from typing_extensions import TypedDict
from app.agents.classifier_agent import classifier_agent
from app.agents.it_support_agent import it_support_agent
from app.agents.hr_agent import hr_agent
from app.agents.accounting_agent import accounting_agent
from app.services.ticket_service import ticket_service
from app.utils.logger import logger


class HelpDeskState(TypedDict):
    messages: List[Dict[str, str]]
    current_agent: str
    category: str
    user_id: str
    session_id: str
    context: Dict[str, Any]
    ticket_id: int
    resolution_status: str
    conversation_stage: str
    needs_ticket: bool


class HelpDeskWorkflow:
    def __init__(self):
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(HelpDeskState)

        # Add nodes
        workflow.add_node("classify", self._classify_node)
        workflow.add_node("it_support", self._it_support_node)
        workflow.add_node("hr_support", self._hr_support_node)
        workflow.add_node("accounting_support", self._accounting_support_node)
        workflow.add_node("create_ticket", self._create_ticket_node)
        workflow.add_node("check_resolution", self._check_resolution_node)

        # Set entry point
        workflow.set_entry_point("classify")

        # Add edges
        workflow.add_conditional_edges(
            "classify",
            self._route_to_agent,
            {
                "it_support": "it_support",
                "hr_support": "hr_support",
                "accounting_support": "accounting_support"
            }
        )

        workflow.add_conditional_edges(
            "it_support",
            self._check_next_action,
            {
                "ask_resolution": "check_resolution",
                "create_ticket": "create_ticket",
                END: END
            }
        )

        workflow.add_edge("hr_support", END)
        workflow.add_edge("accounting_support", END)
        workflow.add_edge("create_ticket", END)
        workflow.add_edge("check_resolution", END)

        return workflow.compile()

    async def _classify_node(self, state: HelpDeskState) -> HelpDeskState:
        last_message = state["messages"][-1]["content"]

        classification = await classifier_agent.classify_query(last_message)

        state["category"] = classification["category"]
        state["current_agent"] = classification["next_agent"]

        return state

    async def _it_support_node(self, state: HelpDeskState) -> HelpDeskState:
        last_message = state["messages"][-1]["content"]

        # Pass current context including conversation stage
        current_context = state["context"].copy()
        current_context["conversation_stage"] = state.get("conversation_stage", "initial")
        
        result = await it_support_agent.handle_query(last_message, current_context)

        response_message = {
            "role": "assistant",
            "content": result["response"],
            "agent": "it_support"
        }

        state["messages"].append(response_message)
        state["context"]["last_action"] = result.get("next_action")
        state["context"]["source"] = result.get("source")
        state["conversation_stage"] = result.get("conversation_stage", "initial")
        state["resolution_status"] = result.get("resolution_status", "")
        
        # Update context with any new information
        for key in ["original_query", "conversation_stage"]:
            if key in result:
                state["context"][key] = result[key]
        
        # Set ticket creation flag if needed
        if result.get("next_action") == "create_ticket":
            state["needs_ticket"] = True

        # Log the interaction
        ticket_service.log_chat(
            state["session_id"],
            last_message,
            result["response"],
            "it_support",
            state.get("ticket_id")
        )

        return state

    async def _hr_support_node(self, state: HelpDeskState) -> HelpDeskState:
        last_message = state["messages"][-1]["content"]

        result = await hr_agent.handle_query(last_message, state["context"])

        response_message = {
            "role": "assistant",
            "content": result["response"],
            "agent": "hr"
        }

        state["messages"].append(response_message)

        ticket_service.log_chat(
            state["session_id"],
            last_message,
            result["response"],
            "hr"
        )

        return state

    async def _accounting_support_node(self, state: HelpDeskState) -> HelpDeskState:
        last_message = state["messages"][-1]["content"]

        result = await accounting_agent.handle_query(last_message, state["context"])

        response_message = {
            "role": "assistant",
            "content": result["response"],
            "agent": "accounting"
        }

        state["messages"].append(response_message)

        ticket_service.log_chat(
            state["session_id"],
            last_message,
            result["response"],
            "accounting"
        )

        return state

    async def _create_ticket_node(self, state: HelpDeskState) -> HelpDeskState:
        # Gather all user messages for comprehensive ticket description
        user_messages = []
        for msg in state["messages"]:
            if msg["role"] == "user":
                user_messages.append(msg["content"])
        
        # Create comprehensive description
        if len(user_messages) > 1:
            description = f"Initial issue: {user_messages[0]}\n\nAdditional details: {' '.join(user_messages[1:])}"
        else:
            description = user_messages[0] if user_messages else "No description provided"
        
        # Determine priority based on conversation
        priority = "medium"
        if any(word in description.lower() for word in ['urgent', 'critical', 'down', 'broken', 'emergency']):
            priority = "high"
        elif any(word in description.lower() for word in ['minor', 'low', 'whenever']):
            priority = "low"
        
        # Create ticket with detailed information
        if user_messages:
            ticket = ticket_service.create_ticket(
                user_id=state["user_id"],
                category=state["category"],
                title=self._generate_ticket_title(user_messages[0], state["category"]),
                description=description,
                priority=priority
            )

            state["ticket_id"] = ticket.id
            state["needs_ticket"] = False
            
            resolution_info = ""
            if state["resolution_status"] == "partially_resolved":
                resolution_info = " Our team will build on the progress we've made together."
            elif state["resolution_status"] == "unresolved":
                resolution_info = " They'll have access to advanced tools and can provide hands-on assistance."

            response = f"🎫 **Support Ticket Created!**\n\n• **Ticket ID**: #{ticket.id}\n• **Priority**: {priority.title()}\n• **Category**: {state['category']}\n\nOur technical team will review your case and contact you within 2-4 hours.{resolution_info}\n\n📞 You can always check your ticket status by mentioning ticket #{ticket.id} in a future conversation."

            state["messages"].append({
                "role": "assistant",
                "content": response,
                "agent": "ticket_system"
            })

        return state
    
    def _generate_ticket_title(self, message: str, category: str) -> str:
        """Generate a descriptive ticket title from the user's message"""
        # Extract key words from the message
        key_words = []
        common_issues = {
            'printer': 'Printer Issue',
            'wifi': 'WiFi Connection Problem', 
            'password': 'Password/Login Issue',
            'email': 'Email Problem',
            'computer': 'Computer Performance Issue',
            'laptop': 'Laptop Issue',
            'software': 'Software Problem',
            'network': 'Network Issue',
            'screen': 'Display Issue',
            'mouse': 'Mouse/Input Device Issue',
            'keyboard': 'Keyboard Issue'
        }
        
        message_lower = message.lower()
        for keyword, title in common_issues.items():
            if keyword in message_lower:
                return title
        
        # Fallback to category-based title
        return f"{category} Support Request"

    async def _check_resolution_node(self, state: HelpDeskState) -> HelpDeskState:
        resolution_prompt = await it_support_agent.ask_for_resolution(state["context"])

        state["messages"].append({
            "role": "assistant",
            "content": resolution_prompt,
            "agent": "it_support"
        })

        return state

    def _route_to_agent(self, state: HelpDeskState) -> str:
        category = state["category"]

        if category in ["IT_HARDWARE", "IT_SOFTWARE"]:
            return "it_support"
        elif category == "HR":
            return "hr_support"
        elif category == "ACCOUNTING":
            return "accounting_support"
        else:
            return "it_support"  # Default fallback

    def _check_next_action(self, state: HelpDeskState) -> str:
        last_action = state["context"].get("last_action")
        conversation_stage = state.get("conversation_stage", "initial")
        
        # Check if ticket creation is needed
        if last_action == "create_ticket" or state.get("needs_ticket", False):
            return "create_ticket"
        
        # If in middle of conversation, continue
        if conversation_stage in ["gathering_details", "awaiting_resolution_feedback", "offering_ticket"]:
            return END  # Continue conversation in same agent
        
        if last_action == "ask_resolution":
            return "ask_resolution"
        
        return END


helpdesk_workflow = HelpDeskWorkflow()
