# IT Helpdesk System - Agent Workflow Test Cases

## Overview

This document provides comprehensive test cases for the multi-agent workflow system built with LangGraph. Tests cover agent classification, routing, conversation management, and workflow state transitions.

---

## 1. Classifier Agent Test Cases

### 1.1 Positive Test Cases

**Test Case**: `CLASSIFIER_POS_001`
**Scenario**: IT Hardware Query Classification
**Input**: "My computer won't turn on and the power light isn't working"
**Expected Output**:
```json
{
  "category": "IT_HARDWARE",
  "confidence": 0.9,
  "next_agent": "it_support"
}
```
**Verification**:
- Category correctly identified as IT_HARDWARE
- High confidence score (>0.8)
- Proper agent routing to it_support

**Test Case**: `CLASSIFIER_POS_002`
**Scenario**: IT Software Query Classification  
**Input**: "I can't install the new software update, getting error messages"
**Expected Output**:
```json
{
  "category": "IT_SOFTWARE", 
  "confidence": 0.85,
  "next_agent": "it_support"
}
```

**Test Case**: `CLASSIFIER_POS_003`
**Scenario**: HR Query Classification
**Input**: "How do I request vacation time and what's the approval process?"
**Expected Output**:
```json
{
  "category": "HR",
  "confidence": 0.9,
  "next_agent": "hr"
}
```

**Test Case**: `CLASSIFIER_POS_004`
**Scenario**: Accounting Query Classification
**Input**: "I need help submitting my expense report for the business trip"
**Expected Output**:
```json
{
  "category": "ACCOUNTING",
  "confidence": 0.8,
  "next_agent": "accounting"
}
```

### 1.2 Negative Test Cases

**Test Case**: `CLASSIFIER_NEG_001`
**Scenario**: Ambiguous Query
**Input**: "Help me"
**Expected Behavior**:
- Low confidence score (<0.6)
- Default routing to IT support
- Request for clarification

**Test Case**: `CLASSIFIER_NEG_002`
**Scenario**: Empty Input
**Input**: ""
**Expected Behavior**:
- Graceful error handling
- Request for user input
- No system crash

**Test Case**: `CLASSIFIER_NEG_003`
**Scenario**: Nonsensical Input
**Input**: "asdfghjkl qwerty 123456"
**Expected Behavior**:
- Low confidence classification
- Default agent routing
- Polite clarification request

---

## 2. IT Support Agent Workflow Test Cases

### 2.1 Knowledge Base Integration Tests

**Test Case**: `IT_WORKFLOW_POS_001`
**Scenario**: Successful Knowledge Base Match
**Setup**:
```python
# Mock knowledge base response
mock_kb_result = [{
    "answer": "Try restarting your computer and checking power connections",
    "similarity": 0.9,
    "source": "knowledge_base"
}]
```
**Input**: "My computer won't start"
**Expected Workflow**:
1. Query classified as IT_HARDWARE
2. Routed to IT Support Agent
3. Knowledge base search performed
4. High similarity match found
5. Solution provided to user
6. Resolution confirmation requested

**Expected Response**:
```json
{
  "response": "I can help with your computer startup issue. Try restarting your computer and checking power connections...",
  "source": "knowledge_base",
  "next_action": "ask_resolution",
  "conversation_stage": "solution_provided"
}
```

**Test Case**: `IT_WORKFLOW_POS_002`
**Scenario**: Low Knowledge Base Match - Web Search Fallback
**Setup**:
```python
# Mock low similarity KB result
mock_kb_result = [{"similarity": 0.3}]
# Mock web search result
mock_web_result = [{
    "title": "Fix Computer Startup Issues",
    "snippet": "Check power supply and connections..."
}]
```
**Input**: "Computer making strange beeping sounds on startup"
**Expected Workflow**:
1. Knowledge base search returns low similarity
2. Web search triggered
3. Web results processed by LLM
4. Synthesized response provided
5. Detail gathering stage initiated

### 2.2 Multi-turn Conversation Tests

**Test Case**: `IT_WORKFLOW_POS_003`
**Scenario**: Multi-turn Problem Diagnosis
**Conversation Flow**:

**Turn 1**:
- User: "My computer is running very slowly"
- Agent: "I can help with performance issues. How long has this been happening?"
- Stage: "gathering_details"

**Turn 2**:
- User: "It started yesterday after I installed some new software"
- Agent: "That could be the cause. Can you tell me what software you installed?"
- Stage: "gathering_details"

**Turn 3**:
- User: "I installed a video editing program called VideoEditor Pro"
- Agent: "Video editing software can be resource-intensive. Let's check your system resources..."
- Stage: "solution_provided"

**Verification Points**:
- Context maintained across turns
- Progressive information gathering
- Appropriate stage transitions
- Relevant follow-up questions

**Test Case**: `IT_WORKFLOW_POS_004`
**Scenario**: Resolution Confirmation Flow
**Setup**: User has been provided a solution
**Input**: "Yes, that fixed the problem, thank you!"
**Expected Workflow**:
1. Resolution confirmed
2. Conversation marked as resolved
3. Positive closure message
4. No ticket creation needed

**Test Case**: `IT_WORKFLOW_POS_005`
**Scenario**: Escalation to Ticket Creation
**Setup**: Multiple solution attempts unsuccessful
**Input**: "No, none of those solutions worked"
**Expected Workflow**:
1. Escalation logic triggered
2. Ticket creation offered
3. Comprehensive ticket details gathered
4. Ticket created with conversation history

### 2.3 Error Handling Tests

**Test Case**: `IT_WORKFLOW_NEG_001`
**Scenario**: Knowledge Base Service Unavailable
**Setup**: Mock ChromaDB to return connection error
**Input**: "My printer won't print"
**Expected Behavior**:
- Graceful fallback to web search
- User receives helpful response
- No system crash
- Error logged appropriately

**Test Case**: `IT_WORKFLOW_NEG_002`
**Scenario**: Web Search Service Failure
**Setup**: Mock web search to return error
**Input**: "Need help with network configuration"
**Expected Behavior**:
- Fallback to general IT guidance
- Request for more specific details
- Offer to create ticket for specialized help

**Test Case**: `IT_WORKFLOW_NEG_003`
**Scenario**: LLM Service Timeout
**Setup**: Mock Ollama to timeout
**Input**: "Complex technical query requiring LLM processing"
**Expected Behavior**:
- Timeout handled gracefully
- User informed of temporary issue
- Alternative assistance offered

---

## 3. HR Agent Workflow Test Cases

### 3.1 Positive Test Cases

**Test Case**: `HR_WORKFLOW_POS_001`
**Scenario**: Standard HR Policy Query
**Input**: "What is our company's remote work policy?"
**Expected Workflow**:
1. Query routed to HR agent
2. LLM generates appropriate HR response
3. Professional, informative tone
4. Company policy referenced

**Expected Response Structure**:
```json
{
  "response": "Our company supports flexible remote work arrangements...",
  "source": "generated",
  "agent": "hr"
}
```

**Test Case**: `HR_WORKFLOW_POS_002`
**Scenario**: Benefits Inquiry
**Input**: "How do I enroll in the health insurance plan?"
**Expected Response**: Detailed enrollment process, deadlines, contact information

**Test Case**: `HR_WORKFLOW_POS_003`
**Scenario**: Leave Request Process
**Input**: "I need to take medical leave, what's the process?"
**Expected Response**: Step-by-step process, required documentation, approval workflow

### 3.2 Negative Test Cases

**Test Case**: `HR_WORKFLOW_NEG_001`
**Scenario**: Inappropriate HR Query
**Input**: "Can you help me with my tax return?"
**Expected Behavior**:
- Polite redirect to appropriate resource
- Clear boundary explanation
- Offer to help with work-related tax questions

---

## 4. Accounting Agent Workflow Test Cases

### 4.1 Positive Test Cases

**Test Case**: `ACCOUNTING_WORKFLOW_POS_001`
**Scenario**: Expense Reimbursement Query
**Input**: "How do I submit receipts for business travel expenses?"
**Expected Workflow**:
1. Query routed to accounting agent
2. Detailed expense submission process provided
3. Required documentation explained
4. Timeline for reimbursement given

**Test Case**: `ACCOUNTING_WORKFLOW_POS_002`
**Scenario**: Purchase Order Process
**Input**: "I need to order office supplies, what's the process?"
**Expected Response**: PO process, approval requirements, vendor information

### 4.2 Negative Test Cases

**Test Case**: `ACCOUNTING_NEG_001`
**Scenario**: Personal Financial Advice
**Input**: "Should I invest in stocks?"
**Expected Behavior**:
- Polite decline to provide personal financial advice
- Redirect to work-related financial questions

---

## 5. Workflow State Management Test Cases

### 5.1 Session State Persistence

**Test Case**: `STATE_POS_001`
**Scenario**: Session State Maintained Across Interactions
**Setup**:
```python
initial_state = {
    "messages": [],
    "current_agent": "classifier",
    "user_id": "test_user",
    "session_id": "test_session_123",
    "context": {},
    "conversation_stage": "initial"
}
```
**Test Steps**:
1. Send initial message, capture session_id
2. Send follow-up with same session_id
3. Verify context preservation
4. Check conversation stage progression

**Test Case**: `STATE_POS_002`
**Scenario**: Agent Handoff State Transfer
**Flow**: Classifier → IT Support → Ticket Creation
**Verification Points**:
- Context transferred between agents
- No information loss during handoffs
- Appropriate state transitions

### 5.2 Error Recovery Tests

**Test Case**: `STATE_NEG_001`
**Scenario**: Invalid State Recovery
**Setup**: Corrupt session state
**Expected Behavior**:
- State reset to safe default
- User informed of session restart
- Graceful degradation

**Test Case**: `STATE_NEG_002`
**Scenario**: Memory Limit Exceeded
**Setup**: Very long conversation history
**Expected Behavior**:
- Older messages summarized or archived
- Recent context maintained
- Performance maintained

---

## 6. Ticket Creation Workflow Test Cases

### 6.1 Positive Test Cases

**Test Case**: `TICKET_WORKFLOW_POS_001`
**Scenario**: Automatic Ticket Creation After Failed Resolution
**Setup**: Multi-turn conversation with unsuccessful resolution
**Expected Workflow**:
1. IT agent exhausts solution options
2. Ticket creation offered and accepted
3. Comprehensive ticket created with:
   - User messages compilation
   - Solution attempts history
   - Priority determination
   - Category assignment

**Expected Ticket Structure**:
```json
{
  "user_id": "test_user",
  "category": "IT_HARDWARE",
  "title": "Computer Performance Issue",
  "description": "Initial issue: Computer running slowly...\nAdditional details: Started after software installation...",
  "priority": "medium"
}
```

**Test Case**: `TICKET_WORKFLOW_POS_002`
**Scenario**: High Priority Ticket Auto-Detection
**Input**: "URGENT: Server is down and affecting entire department"
**Expected Behavior**:
- Priority automatically set to "high"
- Immediate escalation markers
- Expedited ticket creation

### 6.2 Negative Test Cases

**Test Case**: `TICKET_WORKFLOW_NEG_001`
**Scenario**: Ticket Creation Failure
**Setup**: Database unavailable during ticket creation
**Expected Behavior**:
- User informed of temporary issue
- Alternative contact methods provided
- Retry mechanism offered

---

## 7. Integration Workflow Test Cases

### 7.1 End-to-End Workflow Tests

**Test Case**: `E2E_WORKFLOW_001`
**Scenario**: Complete IT Support Resolution Flow
**Steps**:
1. User submits IT query
2. Classifier routes to IT support
3. Knowledge base search performed
4. Solution provided and confirmed
5. Conversation closed successfully

**Test Case**: `E2E_WORKFLOW_002`
**Scenario**: Complex Multi-Agent Escalation
**Steps**:
1. Initial IT query
2. Partial resolution attempt
3. Escalation to ticket creation
4. Support engineer assignment
5. Resolution and closure

### 7.2 Concurrent Session Tests

**Test Case**: `CONCURRENT_001`
**Scenario**: Multiple Simultaneous Sessions
**Setup**: 10 concurrent user sessions
**Verification**:
- Session isolation maintained
- No cross-session data bleeding
- Performance degradation acceptable
- All sessions complete successfully

---

## 8. Performance Workflow Tests

### 8.1 Response Time Tests

**Test Case**: `PERF_WORKFLOW_001`
**Scenario**: Agent Response Time Under Load
**Metrics**:
- Classification: <500ms
- Knowledge search: <1000ms
- LLM generation: <2000ms
- Total response: <3000ms

**Test Case**: `PERF_WORKFLOW_002`
**Scenario**: Memory Usage During Long Conversations
**Setup**: 50+ message conversation
**Verification**:
- Memory usage remains stable
- Response time doesn't degrade
- Context quality maintained

---

## 9. Security Workflow Tests

### 9.1 Input Sanitization Tests

**Test Case**: `SECURITY_WORKFLOW_001`
**Scenario**: Malicious Input Handling
**Inputs**:
- SQL injection attempts
- Script injection
- Command injection
- Buffer overflow attempts

**Expected Behavior**:
- All malicious input sanitized
- No system compromise
- Appropriate logging of attempts

---

## 10. Monitoring and Logging Workflow Tests

### 10.1 Audit Trail Tests

**Test Case**: `AUDIT_WORKFLOW_001`
**Scenario**: Complete Conversation Logging
**Verification Points**:
- All user inputs logged
- All agent responses logged
- State transitions recorded
- Error events captured
- Performance metrics collected

**Test Case**: `AUDIT_WORKFLOW_002`
**Scenario**: Chat Log Association with Tickets
**Verification**:
- Chat logs linked to created tickets
- Complete conversation history preserved
- Support engineer access to full context

---

## Test Execution Framework

### Automated Test Runner

```python
import pytest
import asyncio
from unittest.mock import Mock, patch

class TestAgentWorkflow:
    
    @pytest.mark.asyncio
    async def test_complete_it_workflow(self):
        """Test complete IT support workflow"""
        # Setup mocks
        with patch('app.services.vector_service.vector_service.search_knowledge') as mock_kb:
            mock_kb.return_value = [{"answer": "Solution", "similarity": 0.9}]
            
            # Execute workflow
            result = await self.execute_workflow("My computer won't start")
            
            # Verify results
            assert result["agent"] == "it_support"
            assert "solution" in result["response"].lower()
            assert result["next_action"] == "ask_resolution"
    
    async def execute_workflow(self, user_input):
        """Helper method to execute complete workflow"""
        # Implementation of workflow execution
        pass
```

### Performance Test Suite

```python
class TestWorkflowPerformance:
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self):
        """Test multiple concurrent workflow sessions"""
        tasks = []
        for i in range(10):
            task = self.simulate_user_session(f"user_{i}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Verify all sessions completed successfully
        assert all(result["success"] for result in results)
    
    async def simulate_user_session(self, user_id):
        """Simulate a complete user interaction session"""
        # Implementation of session simulation
        pass
```

### Test Validation Criteria

**Functional Requirements**:
- All agents respond appropriately to their domain queries
- Workflow state transitions occur correctly
- Context is maintained across conversation turns
- Error handling prevents system crashes

**Performance Requirements**:
- Response times meet specified thresholds
- System handles concurrent users efficiently
- Memory usage remains within acceptable bounds

**Security Requirements**:
- All inputs are properly sanitized
- No injection attacks succeed
- Sensitive information is protected

**Reliability Requirements**:
- System recovers gracefully from errors
- Fallback mechanisms work correctly
- Data integrity is maintained

**Usability Requirements**:
- User experience remains smooth during agent transitions
- Error messages are helpful and actionable
- Conversation flow feels natural and intuitive