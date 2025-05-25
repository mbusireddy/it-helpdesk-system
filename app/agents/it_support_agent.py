from typing import Dict, Any, List
from app.services.llm_service import llm_service
from app.services.vector_service import vector_service
from app.services.web_search import web_search_service
from app.utils.logger import logger


class ITSupportAgent:
    def __init__(self):
        self.agent_type = "it_support"

    async def handle_query(self, message: str, context: Dict = None) -> Dict[str, Any]:
        if context is None:
            context = {}
        
        conversation_stage = context.get('conversation_stage', 'initial')
        
        try:
            # Handle different conversation stages
            if conversation_stage == 'awaiting_resolution_feedback':
                return await self._handle_resolution_feedback(message, context)
            elif conversation_stage == 'gathering_details':
                return await self._handle_detail_gathering(message, context)
            else:
                return await self._handle_initial_query(message, context)
                
        except Exception as e:
            logger.error(f"Error in IT support agent: {e}")
            return {
                "response": "I'm experiencing some technical difficulties. Let me create a support ticket for you so our IT team can assist you directly.",
                "source": "error",
                "next_action": "create_ticket"
            }
    
    async def _handle_initial_query(self, message: str, context: Dict) -> Dict[str, Any]:
        # First, search knowledge base
        knowledge_results = await vector_service.search_knowledge(
            message,
            category="IT",
            n_results=3
        )

        if knowledge_results and knowledge_results[0]["similarity"] > 0.7:
            # High confidence match in knowledge base
            best_result = knowledge_results[0]
            response = f"I found a solution in our knowledge base:\n\n{best_result['answer']}\n\n✅ **Did this help solve your problem?**\n\nPlease respond with:\n• 'Yes' - if the issue is resolved\n• 'No' - if you need more help\n• 'Partial' - if it helped but you need additional assistance"

            return {
                "response": response,
                "source": "knowledge_base",
                "confidence": best_result["similarity"],
                "next_action": "ask_resolution",
                "conversation_stage": "awaiting_resolution_feedback"
            }

        # If no good match, try to gather more details
        return await self._ask_for_details(message)
    
    async def _ask_for_details(self, message: str) -> Dict[str, Any]:
        prompt = f"""
        A user has an IT issue: "{message}"
        
        Generate 2-3 specific follow-up questions to better understand their problem.
        Focus on:
        - What device/system they're using
        - When the problem started
        - Any error messages
        - What they were trying to do
        
        Format as a friendly response asking for more details.
        """
        
        response = await llm_service.generate_response(prompt)
        
        return {
            "response": f"I'd like to help you with that IT issue. To provide the best solution, I need a few more details:\n\n{response}\n\nPlease provide as much information as you can.",
            "source": "detail_gathering",
            "next_action": "gather_details",
            "conversation_stage": "gathering_details",
            "original_query": message
        }
    
    async def _handle_detail_gathering(self, message: str, context: Dict) -> Dict[str, Any]:
        original_query = context.get('original_query', '')
        full_context = f"Original issue: {original_query}\nAdditional details: {message}"
        
        # Search knowledge base with enhanced context
        knowledge_results = await vector_service.search_knowledge(
            full_context,
            category="IT",
            n_results=3
        )

        if knowledge_results and knowledge_results[0]["similarity"] > 0.6:
            best_result = knowledge_results[0]
            response = f"Based on the details you provided, here's a solution:\n\n{best_result['answer']}\n\n✅ **Please let me know if this resolves your issue:**\n\n• 'Yes' - Problem solved!\n• 'No' - Still need help\n• 'Partial' - Helped but need more assistance"

            return {
                "response": response,
                "source": "knowledge_base",
                "confidence": best_result["similarity"],
                "next_action": "ask_resolution",
                "conversation_stage": "awaiting_resolution_feedback"
            }
        
        # Try web search with full context
        web_results = await web_search_service.search_web(f"fix {full_context}", 3)
        
        if web_results:
            search_context = "\n".join([
                f"- {result['title']}: {result['snippet']}"
                for result in web_results[:3]
            ])

            prompt = f"""
            Based on these search results, provide a step-by-step solution for this IT issue:

            Problem: {full_context}

            Search Results:
            {search_context}

            Provide a clear, numbered step-by-step solution. Be specific and helpful.
            """

            response = await llm_service.generate_response(prompt)
            
            # Add to knowledge base
            await vector_service.add_knowledge(
                question=full_context,
                answer=response,
                category="IT"
            )

            final_response = f"Here's a step-by-step solution based on your details:\n\n{response}\n\n✅ **Did this solve your problem?**\n\n• 'Yes' - Issue resolved\n• 'No' - Need more help\n• 'Partial' - Helped but need additional support"

            return {
                "response": final_response,
                "source": "web_search",
                "search_results": web_results,
                "next_action": "ask_resolution",
                "conversation_stage": "awaiting_resolution_feedback"
            }
        
        # If no solution found, offer ticket creation
        return {
            "response": "I've gathered your details but couldn't find a definitive solution in our resources. Let me create a support ticket for you so our specialized IT team can assist you directly. They'll have access to more advanced troubleshooting tools.\n\n**Would you like me to create a support ticket?** (Yes/No)",
            "source": "no_solution",
            "next_action": "offer_ticket",
            "conversation_stage": "offering_ticket"
        }
    
    async def _handle_resolution_feedback(self, message: str, context: Dict) -> Dict[str, Any]:
        response_lower = message.lower().strip()
        
        if any(word in response_lower for word in ['yes', 'solved', 'fixed', 'resolved', 'good', 'worked']):
            return {
                "response": "🎉 Great! I'm glad I could help resolve your IT issue. If you have any other problems in the future, feel free to ask. Have a great day!",
                "source": "resolution_success",
                "next_action": "complete",
                "resolution_status": "resolved"
            }
        
        elif any(word in response_lower for word in ['no', 'not', 'still', 'doesnt', "doesn't", 'failed']):
            return {
                "response": "I understand the solution didn't work for you. Let me create a support ticket so our technical specialists can provide personalized assistance. They'll be able to remote in or schedule a time to help you directly.\n\n**Creating your support ticket now...**",
                "source": "resolution_failed",
                "next_action": "create_ticket",
                "resolution_status": "unresolved"
            }
        
        elif any(word in response_lower for word in ['partial', 'some', 'bit', 'little']):
            return {
                "response": "I'm glad it helped partially! Let me create a support ticket to ensure you get complete resolution. Our technical team can build on what we've accomplished and get everything working perfectly.\n\n**Creating your support ticket now...**",
                "source": "partial_resolution",
                "next_action": "create_ticket",
                "resolution_status": "partially_resolved"
            }
        
        else:
            # User provided different response, try to understand
            return {
                "response": "I want to make sure I understand correctly. Is your issue:\n\n• **Completely resolved** (say 'Yes')\n• **Still not working** (say 'No')\n• **Partially fixed** (say 'Partial')\n\nThis helps me provide the best next steps for you.",
                "source": "clarification",
                "next_action": "ask_resolution",
                "conversation_stage": "awaiting_resolution_feedback"
            }

    async def ask_for_resolution(self, context: Dict) -> str:
        return """
        Did this solution help resolve your issue? Please respond with:
        - "Yes" if the issue is resolved
        - "No" if you need additional help
        - "Partial" if it helped but you need more assistance

        If the issue isn't resolved, I can create a support ticket for you.
        """


it_support_agent = ITSupportAgent()