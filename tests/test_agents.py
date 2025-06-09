# Importing libraries

import pytest
import asyncio
from unittest.mock import Mock, patch

# Importing different agents that handle specific query categories
from app.agents.classifier_agent import classifier_agent
from app.agents.it_support_agent import it_support_agent
from app.agents.hr_agent import hr_agent
from app.agents.accounting_agent import accounting_agent

# Service to interact with the LLM (Large Language Model) for classification and generation
from app.services.llm_service import llm_service

# Database utility to initialize default users for tests
from app.models.database import init_default_users


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """
    Pytest fixture to setup the test environment before any tests run in this module.
    It initializes the default users in the test database to ensure a consistent state.
    The fixture is automatically applied to all tests in the module and runs once per module.
    """
    init_default_users()


class TestClassifierAgent:
    """
    Test suite for the Classifier Agent which classifies user queries
    into categories such as IT, HR, etc.
    """

    @pytest.mark.asyncio
    async def test_classify_it_query(self):
        """
        Test if the classifier correctly classifies an IT-related query.
        Uses mocking to simulate the LLM classification response.
        """
        # Patch the classify_intent method of llm_service to return a preset classification
        with patch.object(llm_service, 'classify_intent') as mock_classify:
            mock_classify.return_value = {"category": "IT_SOFTWARE", "confidence": 0.9}

            # Call the classifier_agent's classify_query asynchronously
            result = await classifier_agent.classify_query("My computer won't start")

            # Assert that the classification category and confidence match the mocked response
            assert result["category"] == "IT_SOFTWARE"
            assert result["confidence"] == 0.9

            # Assert that the next agent to handle this query is the IT support agent
            assert result["next_agent"] == "it_support"

    @pytest.mark.asyncio
    async def test_classify_hr_query(self):
        """
        Test if the classifier correctly classifies an HR-related query.
        Again, mocking the classification response to isolate the test.
        """
        with patch.object(llm_service, 'classify_intent') as mock_classify:
            mock_classify.return_value = {"category": "HR", "confidence": 0.8}

            result = await classifier_agent.classify_query("How do I request vacation time?")

            assert result["category"] == "HR"
            assert result["next_agent"] == "hr"


class TestITSupportAgent:
    """
    Test suite for the IT Support Agent which handles IT-related queries.
    Tests both knowledge base search and fallback to web search.
    """

    @pytest.mark.asyncio
    async def test_handle_query_with_knowledge_base_match(self):
        """
        Test scenario where the query matches an answer in the internal knowledge base.
        The agent should respond with the KB answer and suggest next action.
        """
        # Mock the search_knowledge method to return a high similarity KB answer
        with patch('app.services.vector_service.vector_service.search_knowledge') as mock_search:
            mock_search.return_value = [{
                "answer": "Try restarting your computer",
                "similarity": 0.9
            }]

            result = await it_support_agent.handle_query("Computer won't start")

            # Check if the response contains the KB answer and proper metadata
            assert "Try restarting your computer" in result["response"]
            assert result["source"] == "knowledge_base"
            assert result["next_action"] == "ask_resolution"

    @pytest.mark.asyncio
    async def test_handle_query_with_web_search(self):
        """
        Test scenario where the knowledge base does not have a good match (low similarity),
        so the agent uses web search and generates a response using the LLM.
        """
        with patch('app.services.vector_service.vector_service.search_knowledge') as mock_kb:
            with patch('app.services.web_search.web_search_service.search_web') as mock_web:
                with patch.object(llm_service, 'generate_response') as mock_llm:
                    # Simulate low similarity from KB search forcing fallback to web search
                    mock_kb.return_value = [{"similarity": 0.3}]  # Low similarity

                    # Simulate web search returning relevant snippets
                    mock_web.return_value = [{"title": "Fix Computer", "snippet": "Try these steps"}]

                    # Mock LLM generating a human-readable response from web data
                    mock_llm.return_value = "Here are the steps to fix your computer"

                    result = await it_support_agent.handle_query("Unusual computer problem")

                    # The response should indicate detailed gathering from external sources
                    assert result["source"] == "detail_gathering"
                    assert "steps" in result["response"].lower()


class TestHRAgent:
    """
    Test suite for the HR Agent handling HR related queries.
    """

    @pytest.mark.asyncio
    async def test_handle_hr_query(self):
        """
        Test HR agent generates correct response to a vacation request query,
        mocking the LLM's generate_response method.
        """
        with patch.object(llm_service, 'generate_response') as mock_llm:
            mock_llm.return_value = "To request vacation time, please submit a request through the HR portal"

            result = await hr_agent.handle_query("How do I request vacation time?")

            # Assert response contains relevant HR info and source is generated content
            assert "vacation time" in result["response"].lower()
            assert result["source"] == "generated"


class TestAccountingAgent:
    """
    Test suite for the Accounting Agent which handles finance/accounting queries.
    """

    @pytest.mark.asyncio
    async def test_handle_accounting_query(self):
        """
        Test accounting agent returns correct reimbursement info,
        using mocked LLM response.
        """
        with patch.object(llm_service, 'generate_response') as mock_llm:
            mock_llm.return_value = "For expense reimbursement, please submit receipts through the finance portal"

            result = await accounting_agent.handle_query("How do I get reimbursed for expenses?")

            assert "expense" in result["response"].lower()
            assert result["source"] == "generated"


class TestWorkflowIntegration:
    """
    Integration test for the full workflow: classification followed by
    handling the query in the appropriate agent (IT support in this case).
    """

    @pytest.mark.asyncio
    async def test_full_workflow_it_query(self):
        """
        Tests a full query lifecycle starting from intent classification,
        ensuring the classifier directs the query to IT support agent,
        and that IT support agent returns a knowledge base response.
        """
        with patch.object(llm_service, 'classify_intent') as mock_classify:
            with patch('app.services.vector_service.vector_service.search_knowledge') as mock_search:
                # Mock classification to IT category with high confidence
                mock_classify.return_value = {"category": "IT_SOFTWARE", "confidence": 0.9}

                # Mock KB search returning a relevant answer
                mock_search.return_value = [{
                    "answer": "Try restarting your computer and checking connections",
                    "similarity": 0.9
                }]

                # Classify the query first
                classification = await classifier_agent.classify_query("My computer won't start")

                # Assert classifier routes to IT support agent
                assert classification["next_agent"] == "it_support"

                # IT support agent handles query and should return KB answer
                result = await it_support_agent.handle_query("My computer won't start")
                assert "restart" in result["response"].lower()
                assert result["source"] == "knowledge_base"
