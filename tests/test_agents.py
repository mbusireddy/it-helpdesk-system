import pytest
import asyncio
from unittest.mock import Mock, patch
from app.agents.classifier_agent import classifier_agent
from app.agents.it_support_agent import it_support_agent
from app.agents.hr_agent import hr_agent
from app.agents.accounting_agent import accounting_agent
from app.services.llm_service import llm_service
from app.models.database import init_default_users

@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Setup test environment with database"""
    init_default_users()


class TestClassifierAgent:
    @pytest.mark.asyncio
    async def test_classify_it_query(self):
        with patch.object(llm_service, 'classify_intent') as mock_classify:
            mock_classify.return_value = {"category": "IT_SOFTWARE", "confidence": 0.9}

            result = await classifier_agent.classify_query("My computer won't start")

            assert result["category"] == "IT_SOFTWARE"
            assert result["confidence"] == 0.9
            assert result["next_agent"] == "it_support"

    @pytest.mark.asyncio
    async def test_classify_hr_query(self):
        with patch.object(llm_service, 'classify_intent') as mock_classify:
            mock_classify.return_value = {"category": "HR", "confidence": 0.8}

            result = await classifier_agent.classify_query("How do I request vacation time?")

            assert result["category"] == "HR"
            assert result["next_agent"] == "hr"


class TestITSupportAgent:
    @pytest.mark.asyncio
    async def test_handle_query_with_knowledge_base_match(self):
        with patch('app.services.vector_service.vector_service.search_knowledge') as mock_search:
            mock_search.return_value = [{
                "answer": "Try restarting your computer",
                "similarity": 0.9
            }]

            result = await it_support_agent.handle_query("Computer won't start")

            assert "Try restarting your computer" in result["response"]
            assert result["source"] == "knowledge_base"
            assert result["next_action"] == "ask_resolution"

    @pytest.mark.asyncio
    async def test_handle_query_with_web_search(self):
        with patch('app.services.vector_service.vector_service.search_knowledge') as mock_kb:
            with patch('app.services.web_search.web_search_service.search_web') as mock_web:
                with patch.object(llm_service, 'generate_response') as mock_llm:
                    mock_kb.return_value = [{"similarity": 0.3}]  # Low similarity
                    mock_web.return_value = [{"title": "Fix Computer", "snippet": "Try these steps"}]
                    mock_llm.return_value = "Here are the steps to fix your computer"

                    result = await it_support_agent.handle_query("Unusual computer problem")

                    assert result["source"] == "detail_gathering"
                    assert "steps" in result["response"].lower()


class TestHRAgent:
    @pytest.mark.asyncio
    async def test_handle_hr_query(self):
        with patch.object(llm_service, 'generate_response') as mock_llm:
            mock_llm.return_value = "To request vacation time, please submit a request through the HR portal"
            
            result = await hr_agent.handle_query("How do I request vacation time?")
            
            assert "vacation time" in result["response"].lower()
            assert result["source"] == "generated"


class TestAccountingAgent:
    @pytest.mark.asyncio
    async def test_handle_accounting_query(self):
        with patch.object(llm_service, 'generate_response') as mock_llm:
            mock_llm.return_value = "For expense reimbursement, please submit receipts through the finance portal"
            
            result = await accounting_agent.handle_query("How do I get reimbursed for expenses?")
            
            assert "expense" in result["response"].lower()
            assert result["source"] == "generated"


class TestWorkflowIntegration:
    @pytest.mark.asyncio
    async def test_full_workflow_it_query(self):
        """Test complete workflow from classification to IT support resolution"""
        with patch.object(llm_service, 'classify_intent') as mock_classify:
            with patch('app.services.vector_service.vector_service.search_knowledge') as mock_search:
                mock_classify.return_value = {"category": "IT_SOFTWARE", "confidence": 0.9}
                mock_search.return_value = [{
                    "answer": "Try restarting your computer and checking connections",
                    "similarity": 0.9
                }]
                
                # First classify the query
                classification = await classifier_agent.classify_query("My computer won't start")
                assert classification["next_agent"] == "it_support"
                
                # Then handle with IT support agent
                result = await it_support_agent.handle_query("My computer won't start")
                assert "restart" in result["response"].lower()
                assert result["source"] == "knowledge_base"