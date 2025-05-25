import ollama
from typing import List, Dict, Any
from app.utils.config import settings
from app.utils.logger import logger


class OllamaService:
    def __init__(self):
        self.client = ollama.Client(host=settings.ollama_base_url)
        self.model = settings.ollama_model

    async def generate_response(self, prompt: str, context: str = "") -> str:
        try:
            full_prompt = f"{context}\n\nUser Query: {prompt}" if context else prompt

            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )

            return response['message']['content']
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble processing your request right now."

    async def generate_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings(
                model=self.model,
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    async def classify_intent(self, message: str) -> Dict[str, Any]:
        prompt = f"""
        Classify the following user message into one of these categories:
        - IT_HARDWARE: Hardware issues, computer problems, printer issues
        - IT_SOFTWARE: Software problems, application errors, system issues
        - HR: Human resources, payroll, benefits, policies
        - ACCOUNTING: Finance, expenses, billing, invoicing
        - GENERAL: General inquiries, other topics

        Message: "{message}"

        Respond with only the category name and confidence (0-1):
        Format: CATEGORY|CONFIDENCE
        """

        response = await self.generate_response(prompt)
        try:
            parts = response.strip().split('|')
            category = parts[0].strip()
            confidence = float(parts[1].strip()) if len(parts) > 1 else 0.8
            return {"category": category, "confidence": confidence}
        except:
            return {"category": "GENERAL", "confidence": 0.5}


llm_service = OllamaService()