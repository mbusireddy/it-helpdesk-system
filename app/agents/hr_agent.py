# Import necessary types and services
from typing import Dict, Any
from app.services.llm_service import llm_service
from app.services.vector_service import vector_service
 
 
class HRAgent:
    def __init__(self):
        # Agent type identifier for routing or analytics
        self.agent_type = "hr"
 
    async def handle_query(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """
        Handles HR-related queries by first checking a vector-based knowledge base.
        If a high-confidence match is found, uses it. Otherwise, falls back to LLM-generated response.
 
        Args:
            message (str): The user's input query.
            context (Dict, optional): Additional metadata/context (unused here).
 
        Returns:
            Dict[str, Any]: Contains the response, the response source, and the next action.
        """
 
        # Step 1: Search HR-related knowledge from the vector store
        knowledge_results = await vector_service.search_knowledge(
            message, category="HR", n_results=3
        )
 
        # Step 2: If a confident match is found in the knowledge base, return it
        if knowledge_results and knowledge_results[0]["similarity"] > 0.7:
            return {
                "response": knowledge_results[0]["answer"],   # Return the most relevant answer
                "source": "knowledge_base",                   # Source is the knowledge base
                "next_action": "complete"                     # No further steps required
            }
 
        # Step 3: If no relevant KB answer, generate a response using LLM
        prompt = f"""
        You are an HR assistant. Help with this HR-related query:
        {message}
 
        Provide helpful information about policies, procedures, or direct them to appropriate HR contacts.
        Be professional and empathetic.
        """
 
        # Generate the response from the LLM
        response = await llm_service.generate_response(prompt)
 
        # Step 4: Return the generated response
        return {
            "response": response,               # LLM-generated answer
            "source": "generated",              # Indicates fallback to LLM
            "next_action": "complete"           # Response is ready to be returned
        }
 
 
# Instantiate the HR agent for use across the system
hr_agent = HRAgent()
