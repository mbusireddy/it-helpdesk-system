from typing import Dict, Any
from app.services.vector_service import vector_service
from app.services.llm_service import llm_service


class AccountingAgent:
    def __init__(self):
        self.agent_type = "accounting"

    async def handle_query(self, message: str, context: Dict = None) -> Dict[str, Any]:
        knowledge_results = await vector_service.search_knowledge(
            message, category="ACCOUNTING", n_results=3
        )

        if knowledge_results and knowledge_results[0]["similarity"] > 0.7:
            return {
                "response": knowledge_results[0]["answer"],
                "source": "knowledge_base",
                "next_action": "complete"
            }

        prompt = f"""
        You are an accounting assistant. Help with this finance-related query:
        {message}

        Provide helpful information about expenses, billing, or direct them to accounting team.
        Be accurate and professional.
        """

        response = await llm_service.generate_response(prompt)

        return {
            "response": response,
            "source": "generated",
            "next_action": "complete"
        }

accounting_agent = AccountingAgent()