# Import necessary modules and classes for graph-based workflow and typing
from langgraph.graph import StateGraph, END
from typing import Dict, Any, List
from typing_extensions import TypedDict

# Import individual agents for different departments
from app.agents.classifier_agent import classifier_agent
from app.agents.it_support_agent import it_support_agent
from app.agents.hr_agent import hr_agent
from app.agents.accounting_agent import accounting_agent

# Import ticket service to log and create support tickets
from app.services.ticket_service import ticket_service
from app.utils.logger import logger

# Define the structure of the state dictionary passed between workflow nodes
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

# Define the HelpDesk workflow class using LangGraph
class HelpDeskWorkflow:
    def __init__(self):
        # Build and compile the workflow on initialization
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        # Create a stateful graph with HelpDeskState as the data model
        workflow = StateGraph(HelpDeskState)

        # Define the nodes (steps) in the workflow
        workflow.add_node("classify", self._classify_node)
        workflow.add_node("it_support", self._it_support_node)
        workflow.add_node("hr_support", self._hr_support_node)
        workflow.add_node("accounting_support", self._accounting_support_node)
        workflow.add_node("create_ticket", self._create_ticket_node)
        workflow.add_node("check_resolution", self._check_resolution_node)

        # Define the entry point for the graph
        workflow.set_entry_point("classify")

        # Define conditional routing from classifier to correct support team
        workflow.add_conditional_edges(
            "classify",
            self._route_to_agent,
            {
                "it_support": "it_support",
                "hr_support": "hr_support",
                "accounting_support": "accounting_support"
            }
        )

        # Define follow-up actions from IT support based on resolution or ticket needs
        workflow.add_conditional_edges(
            "it_support",
            self._check_next_action,
            {
                "ask_resolution": "check_resolution",
                "create_ticket": "create_ticket",
                END: END
            }
        )

        # All other department support nodes end the conversation
        workflow.add_edge("hr_support", END)
        workflow.add_edge("accounting_support", END)
        workflow.add_edge("create_ticket", END)
        workflow.add_edge("check_resolution", END)

        # Return the compiled workflow
        return workflow.compile()

    # Node: Classify the user's query and assign appropriate agent
    async def _classify_node(self, state: HelpDeskState) -> HelpDeskState:
        last_message = state["messages"][-1]["content"]
        classification = await classifier_agent.classify_query(last_message)

        state["category"] = classification["category"]
        state["current_agent"] = classification["next_agent"]

        return state

    # Node: Handle IT support related queries
    async def _it_support_node(self, state: HelpDeskState) -> HelpDeskState:
        last_message = state["messages"][-1]["content"]

        # Pass the existing conversation context
        current_context = state["context"].copy()
        current_context["conversation_stage"] = state.get("conversation_stage", "initial")
        
        # Process the query through IT support agent
        result = await it_support_agent.handle_query(last_message, current_context)

        # Append assistant response to conversation
        response_message = {
            "role": "assistant",
            "content": result["response"],
            "agent": "it_support"
        }

        # Update state with the result
        state["messages"].append(response_message)
        state["context"]["last_action"] = result.get("next_action")
        state["context"]["source"] = result.get("source")
        state["conversation_stage"] = result.get("conversation_stage", "initial")
        state["resolution_status"] = result.get("resolution_status", "")

        # Include additional data in context if available
        for key in ["original_query", "conversation_stage"]:
            if key in result:
                state["context"][key] = result[key]

        # Determine if ticket creation is required
        if result.get("next_action") == "create_ticket":
            state["needs_ticket"] = True

        # Log the chat to the ticketing system
        ticket_service.log_chat(
            state["session_id"],
            last_message,
            result["response"],
            "it_support",
            state.get("ticket_id")
        )

        return state

    # Node: Handle HR queries
    async def _hr_support_node(self, state: HelpDeskState) -> HelpDeskState:
        last_message = state["messages"][-1]["content"]
        result = await hr_agent.handle_query(last_message, state["context"])

        state["messages"].append({
            "role": "assistant",
            "content": result["response"],
            "agent": "hr"
        })

        ticket_service.log_chat(
            state["session_id"],
            last_message,
            result["response"],
            "hr"
        )

        return state

    # Node: Handle Accounting queries
    async def _accounting_support_node(self, state: HelpDeskState) -> HelpDeskState:
        last_message = state["messages"][-1]["content"]
        result = await accounting_agent.handle_query(last_message, state["context"])

        state["messages"].append({
            "role": "assistant",
            "content": result["response"],
            "agent": "accounting"
        })

        ticket_service.log_chat(
            state["session_id"],
            last_message,
            result["response"],
            "accounting"
        )

        return state

    # Node: Create a support ticket based on conversation history
    async def _create_ticket_node(self, state: HelpDeskState) -> HelpDeskState:
        # Collect user messages for description
        user_messages = [msg["content"] for msg in state["messages"] if msg["role"] == "user"]
        
        # Format the ticket description
        if len(user_messages) > 1:
            description = f"Initial issue: {user_messages[0]}\n\nAdditional details: {' '.join(user_messages[1:])}"
        else:
            description = user_messages[0] if user_messages else "No description provided"

        # Set ticket priority using simple keyword-based rules
        priority = "medium"
        if any(word in description.lower() for word in ['urgent', 'critical', 'down', 'broken', 'emergency']):
            priority = "high"
        elif any(word in description.lower() for word in ['minor', 'low', 'whenever']):
            priority = "low"

        # Create the support ticket using service
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

            # Add additional context based on previous resolution stage
            resolution_info = ""
            if state["resolution_status"] == "partially_resolved":
                resolution_info = " Our team will build on the progress we've made together."
            elif state["resolution_status"] == "unresolved":
                resolution_info = " They'll have access to advanced tools and can provide hands-on assistance."

            # Construct the final response message with ticket details
            response = f"🎫 **Support Ticket Created!**\n\n• **Ticket ID**: #{ticket.id}\n• **Priority**: {priority.title()}\n• **Category**: {state['category']}\n\nOur technical team will review your case and contact you within 2-4 hours.{resolution_info}\n\n📞 You can always check your ticket status by mentioning ticket #{ticket.id} in a future conversation."

            state["messages"].append({
                "role": "assistant",
                "content": response,
                "agent": "ticket_system"
            })

        return state

    # Utility: Generate a short and relevant title for the ticket
    def _generate_ticket_title(self, message: str, category: str) -> str:
        """Generate a descriptive ticket title from the user's message"""
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

        return f"{category} Support Request"  # Default title

    # Node: Ask user if their issue has been resolved
    async def _check_resolution_node(self, state: HelpDeskState) -> HelpDeskState:
        resolution_prompt = await it_support_agent.ask_for_resolution(state["context"])

        state["messages"].append({
            "role": "assistant",
            "content": resolution_prompt,
            "agent": "it_support"
        })

        return state

    # Decision point: Route query to the correct agent based on classified category
    def _route_to_agent(self, state: HelpDeskState) -> str:
        category = state["category"]

        if category in ["IT_HARDWARE", "IT_SOFTWARE"]:
            return "it_support"
        elif category == "HR":
            return "hr_support"
        elif category == "ACCOUNTING":
            return "accounting_support"
        else:
            return "it_support"  # Fallback for unknown category

    # Decision point: Determine next step after IT agent response
    def _check_next_action(self, state: HelpDeskState) -> str:
        last_action = state["context"].get("last_action")
        conversation_stage = state.get("conversation_stage", "initial")

        if last_action == "create_ticket" or state.get("needs_ticket", False):
            return "create_ticket"

        if conversation_stage in ["gathering_details", "awaiting_resolution_feedback", "offering_ticket"]:
            return END  # Stay in the same node

        if last_action == "ask_resolution":
            return "ask_resolution"

        return END  # Default: end the interaction


# Create an instance of the workflow ready to be used
helpdesk_workflow = HelpDeskWorkflow()
