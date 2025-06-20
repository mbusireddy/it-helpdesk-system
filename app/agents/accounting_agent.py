# Import necessary types and services

from typing import Dict, Any
from app.services.vector_service import vector_service
from app.services.llm_service import llm_service


class AccountingAgent:
    def __init__(self):
        # Define the type of agent, useful for logging or analytics
        self.agent_type = "accounting"

    async def handle_query(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """
        Handles accounting-related user queries.
        
        Args:
            message (str): The user input message or query.
            context (Dict, optional): Any additional context that might help in responding (not used here).
        
        Returns:
            Dict[str, Any]: A dictionary containing the response, source, and next action.
        """
        
        # Step 1: Try to retrieve relevant knowledge base entries for the accounting query
        knowledge_results = await vector_service.search_knowledge(
            message, category="ACCOUNTING", n_results=3
        )

        # Step 2: If a highly relevant knowledge base entry is found, return it as the response
        if knowledge_results and knowledge_results[0]["similarity"] > 0.7:
            return {
                "response": knowledge_results[0]["answer"],
                "source": "knowledge_base",         # Indicates the answer came from the preloaded knowledge
                "next_action": "complete"           # No further action required
            }

        # Step 3: If no suitable knowledge is found, fallback to generating a response using the LLM
        prompt = f"""
        You are an accounting assistant. Help with this finance-related query:
        {message}

        Provide helpful information about expenses, billing, or direct them to accounting team.
        Be accurate and professional.
        """

        # Generate a response from the LLM using the formatted prompt
        response = await llm_service.generate_response(prompt)

        # Step 4: Return the generated response
        return {
            "response": response,
            "source": "generated",                # Indicates the answer was generated by the language model
            "next_action": "complete"             # No further steps needed
        }


# Create an instance of the AccountingAgent for use in the application
accounting_agent = AccountingAgent()
