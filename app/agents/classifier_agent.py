from typing import Dict, Any
from app.services.llm_service import llm_service
from app.utils.logger import logger


class ClassifierAgent:
    def __init__(self):
        self.agent_type = "classifier"

    async def classify_query(self, message: str, context: str = "") -> Dict[str, Any]:
        try:
            classification = await llm_service.classify_intent(message)

            logger.info(f"Classified message as: {classification}")

            return {
                "category": classification["category"],
                "confidence": classification["confidence"],
                "next_agent": self._get_next_agent(classification["category"]),
                "requires_routing": True
            }
        except Exception as e:
            logger.error(f"Error in classification: {e}")
            return {
                "category": "GENERAL",
                "confidence": 0.5,
                "next_agent": "general",
                "requires_routing": True
            }

    def _get_next_agent(self, category: str) -> str:
        agent_mapping = {
            "IT_HARDWARE": "it_support",
            "IT_SOFTWARE": "it_support",
            "HR": "hr",
            "ACCOUNTING": "accounting",
            "GENERAL": "general"
        }
        return agent_mapping.get(category, "general")


classifier_agent = ClassifierAgent()