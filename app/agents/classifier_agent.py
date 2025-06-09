# Import necessary types and services

from typing import Dict, Any
from app.services.llm_service import llm_service
from app.utils.logger import logger


class ClassifierAgent:
    def __init__(self):
        # Defines the type of agent, useful for agent-based routing logic
        self.agent_type = "classifier"

    async def classify_query(self, message: str, context: str = "") -> Dict[str, Any]:
        """
        Classifies the user's query to determine which department or agent should handle it.

        Args:
            message (str): The user's input message that needs classification.
            context (str, optional): Additional context if available (currently unused).

        Returns:
            Dict[str, Any]: Classification result including category, confidence score,
                            next agent, and routing flag.
        """
        try:
            # Use LLM service to classify the user's message
            classification = await llm_service.classify_intent(message)

            # Log the classification result
            logger.info(f"Classified message as: {classification}")

            # Return the classification details
            return {
                "category": classification["category"],                   # Classified topic (e.g., HR, IT)
                "confidence": classification["confidence"],               # LLM confidence score
                "next_agent": self._get_next_agent(classification["category"]),  # Map category to next agent
                "requires_routing": True                                   # Indicates the message needs routing
            }

        except Exception as e:
            # Log the error and return a default fallback classification
            logger.error(f"Error in classification: {e}")
            return {
                "category": "GENERAL",
                "confidence": 0.5,
                "next_agent": "general",
                "requires_routing": True
            }

    def _get_next_agent(self, category: str) -> str:
        """
        Maps the classified category to the corresponding agent name.

        Args:
            category (str): The classified category from the LLM.

        Returns:
            str: The internal agent name responsible for handling the category.
        """
        agent_mapping = {
            "IT_HARDWARE": "it_support",
            "IT_SOFTWARE": "it_support",
            "HR": "hr",
            "ACCOUNTING": "accounting",
            "GENERAL": "general"
        }
        # Return the mapped agent, or default to "general"
        return agent_mapping.get(category, "general")


# Create a singleton instance of the classifier agent
classifier_agent = ClassifierAgent()
