from typing import Dict, Any
from app.services.llm_service import llm_service
from app.services.vector_service import vector_service


class HRAgent:
    def __init__(self):
        self.agent_type = "hr"

    async def handle_query(self, message: str, context: Dict = None) -> Dict[str, Any]:
        # Search HR knowledge base
        knowledge_results = await vector_service.search_knowledge(
            message, category="HR", n_results=3
        )

        if knowledge_results and knowledge_results[0]["similarity"] > 0.7:
            return {
                "response": knowledge_results[0]["answer"],
                "source": "knowledge_base",
                "next_action": "complete"
            }

        # Generate HR response
        prompt = f"""
        You are an HR assistant. Help with this HR-related query:
        {message}

        Provide helpful information about policies, procedures, or direct them to appropriate HR contacts.
        Be professional and empathetic.
        """

        response = await llm_service.generate_response(prompt)

        return {
            "response": response,
            "source": "generated",
            "next_action": "complete"
        }

hr_agent = HRAgent()