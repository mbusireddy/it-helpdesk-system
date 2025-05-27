# IT Helpdesk System - Positive Test Cases

## 1. Authentication & Authorization - Positive Cases

### 1.1 User Authentication Success
**Test Case ID**: AUTH_POS_001
**Scenario**: Valid user login with correct credentials
**Test Steps**:
1. Send POST request to `/login` with valid username/password
2. Verify 200 status code
3. Verify response contains access_token, token_type, and user info
4. Verify token_type is "bearer"
5. Verify user information matches expected values

**Expected Result**: User successfully authenticates and receives valid JWT token

**Test Data**:
```json
{
  "username": "appuser",
  "password": "password123"
}
```

### 1.2 Support Engineer Authentication Success
**Test Case ID**: AUTH_POS_002
**Scenario**: Support engineer login with correct credentials
**Test Steps**:
1. Send POST request to `/login` with support engineer credentials
2. Verify 200 status code
3. Verify user role is "support-engineer"
4. Verify access to support-only endpoints

**Test Data**:
```json
{
  "username": "support-engineer",
  "password": "support123"
}
```

### 1.3 User Profile Access
**Test Case ID**: AUTH_POS_003
**Scenario**: Authenticated user accesses profile information
**Test Steps**:
1. Login with valid credentials
2. Send GET request to `/me` with valid token
3. Verify 200 status code
4. Verify response contains user details

**Expected Result**: User profile information returned successfully

## 2. Chat System - Positive Cases

### 2.1 Basic Chat Interaction
**Test Case ID**: CHAT_POS_001
**Scenario**: User sends a simple IT query and receives response
**Test Steps**:
1. Send POST request to `/chat` with IT-related query
2. Verify 200 status code
3. Verify response contains response, session_id, and agent fields
4. Verify agent field indicates correct agent type

**Test Data**:
```json
{
  "content": "My computer won't start",
  "user_id": "test_user_123"
}
```

### 2.2 Multi-turn Conversation
**Test Case ID**: CHAT_POS_002
**Scenario**: User engages in multi-turn conversation with context preservation
**Test Steps**:
1. Send initial query and capture session_id
2. Send follow-up query with same session_id
3. Verify conversation context is maintained
4. Verify agent provides contextually relevant responses

**Test Data**:
```json
// First message
{
  "content": "I'm having printer issues",
  "user_id": "test_user_456"
}

// Follow-up message
{
  "content": "It's printing blank pages",
  "user_id": "test_user_456",
  "session_id": "captured_session_id"
}
```

### 2.3 Category Classification
**Test Case ID**: CHAT_POS_003
**Scenario**: Different query types are correctly classified and routed
**Test Steps**:
1. Send IT hardware query - verify IT agent response
2. Send HR query - verify HR agent response
3. Send accounting query - verify accounting agent response

**Test Cases**:
- IT: "My monitor is flickering"
- HR: "How do I request vacation time?"
- Accounting: "How do I submit expense reports?"

### 2.4 Knowledge Base Integration
**Test Case ID**: CHAT_POS_004
**Scenario**: System successfully retrieves and uses knowledge base information
**Test Steps**:
1. Send query matching knowledge base content
2. Verify response includes relevant knowledge base information
3. Verify response source indicates knowledge_base

**Expected Result**: Accurate information retrieved from vector database

## 3. Ticket Management - Positive Cases

### 3.1 Ticket Creation
**Test Case ID**: TICKET_POS_001
**Scenario**: Automatic ticket creation for unresolved issues
**Test Steps**:
1. Engage in conversation that leads to ticket creation
2. Verify ticket is created with proper details
3. Verify ticket ID is returned to user
4. Verify ticket appears in user's ticket list

**Expected Result**: Ticket created successfully with all relevant information

### 3.2 Ticket Status Retrieval
**Test Case ID**: TICKET_POS_002
**Scenario**: User checks status of existing ticket
**Test Steps**:
1. Create a ticket through chat
2. Send POST request to `/ticket/status` with ticket ID
3. Verify 200 status code
4. Verify ticket details are returned correctly

### 3.3 User Ticket History
**Test Case ID**: TICKET_POS_003
**Scenario**: User retrieves list of their tickets
**Test Steps**:
1. Create multiple tickets for user
2. Send GET request to `/tickets/user/{user_id}`
3. Verify 200 status code
4. Verify all user tickets are returned

### 3.4 Support Engineer Ticket Management
**Test Case ID**: TICKET_POS_004
**Scenario**: Support engineer updates ticket status
**Test Steps**:
1. Login as support engineer
2. Retrieve all tickets via `/tickets/all`
3. Update ticket status via `/ticket/update`
4. Verify ticket is updated successfully

**Test Data**:
```json
{
  "ticket_id": 1,
  "status": "in_progress",
  "assigned_to": "support-engineer"
}
```

## 4. Agent Workflow - Positive Cases

### 4.1 IT Support Agent Knowledge Search
**Test Case ID**: AGENT_POS_001
**Scenario**: IT agent successfully finds solution in knowledge base
**Test Steps**:
1. Send IT query that matches knowledge base
2. Verify agent searches knowledge base
3. Verify relevant solution is returned
4. Verify agent asks for resolution confirmation

**Expected Result**: User receives helpful solution from knowledge base

### 4.2 IT Support Agent Web Search
**Test Case ID**: AGENT_POS_002
**Scenario**: IT agent performs web search for unknown issues
**Test Steps**:
1. Send unique IT query not in knowledge base
2. Verify agent performs web search
3. Verify relevant web results are processed
4. Verify synthesized response is provided

**Expected Result**: Agent provides helpful information from web search

### 4.3 HR Agent Query Handling
**Test Case ID**: AGENT_POS_003
**Scenario**: HR agent handles policy and procedure questions
**Test Steps**:
1. Send HR-related query
2. Verify query is routed to HR agent
3. Verify appropriate HR response is generated
4. Verify professional and helpful tone

**Test Data**: "What is the company policy on remote work?"

### 4.4 Accounting Agent Query Handling
**Test Case ID**: AGENT_POS_004
**Scenario**: Accounting agent handles financial queries
**Test Steps**:
1. Send accounting-related query
2. Verify query is routed to accounting agent
3. Verify appropriate financial guidance is provided

**Test Data**: "How do I set up direct deposit?"

### 4.5 Agent Escalation Flow
**Test Case ID**: AGENT_POS_005
**Scenario**: Proper escalation when agent cannot resolve issue
**Test Steps**:
1. Engage in conversation that cannot be resolved
2. Verify agent offers ticket creation
3. Verify ticket is created with proper escalation
4. Verify handoff information is preserved

## 5. Analytics & Dashboard - Positive Cases

### 5.1 Dashboard Analytics Retrieval
**Test Case ID**: ANALYTICS_POS_001
**Scenario**: Authenticated user accesses dashboard analytics
**Test Steps**:
1. Login with valid credentials
2. Send GET request to `/analytics/dashboard`
3. Verify 200 status code
4. Verify analytics data structure

**Expected Response**:
```json
{
  "total_tickets": 10,
  "open_tickets": 5,
  "resolved_tickets": 5,
  "resolution_rate": 50.0,
  "category_breakdown": [
    {"category": "IT_HARDWARE", "count": 3},
    {"category": "IT_SOFTWARE", "count": 7}
  ]
}
```

### 5.2 Real-time Metrics Update
**Test Case ID**: ANALYTICS_POS_002
**Scenario**: Analytics update after ticket operations
**Test Steps**:
1. Capture initial analytics
2. Create new ticket through chat
3. Retrieve analytics again
4. Verify metrics have updated correctly

## 6. System Integration - Positive Cases

### 6.1 Health Check
**Test Case ID**: SYSTEM_POS_001
**Scenario**: System health check returns positive status
**Test Steps**:
1. Send GET request to `/health`
2. Verify 200 status code
3. Verify response indicates healthy status

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "IT Helpdesk System"
}
```

### 6.2 CORS Configuration
**Test Case ID**: SYSTEM_POS_002
**Scenario**: Cross-origin requests are properly handled
**Test Steps**:
1. Send requests from different origins
2. Verify CORS headers are present
3. Verify requests are processed successfully

### 6.3 LLM Integration
**Test Case ID**: SYSTEM_POS_003
**Scenario**: System successfully integrates with Ollama LLM
**Test Steps**:
1. Send query requiring LLM processing
2. Verify successful communication with Ollama
3. Verify quality response generation

### 6.4 Vector Database Integration
**Test Case ID**: SYSTEM_POS_004
**Scenario**: ChromaDB vector search functions correctly
**Test Steps**:
1. Perform semantic search query
2. Verify relevant results are returned
3. Verify similarity scoring works correctly

## 7. User Interface - Positive Cases

### 7.1 Chat Interface Login
**Test Case ID**: UI_POS_001
**Scenario**: User successfully logs into chat interface
**Test Steps**:
1. Access chat interface at localhost:8501
2. Enter valid credentials
3. Verify successful login
4. Verify chat functionality is available

### 7.2 Dashboard Interface Access
**Test Case ID**: UI_POS_002
**Scenario**: Support engineer accesses dashboard interface
**Test Steps**:
1. Access dashboard at localhost:8502
2. Login with support engineer credentials
3. Verify dashboard loads successfully
4. Verify support engineer features are available

### 7.3 Quick Login Buttons
**Test Case ID**: UI_POS_003
**Scenario**: Quick login buttons work correctly
**Test Steps**:
1. Access web interface
2. Click "Login as Regular User" button
3. Verify automatic login as appuser
4. Click "Login as Support Engineer" button
5. Verify automatic login as support engineer

## 8. Performance - Positive Cases

### 8.1 Response Time
**Test Case ID**: PERF_POS_001
**Scenario**: System responds within acceptable time limits
**Test Steps**:
1. Send multiple chat requests
2. Measure response times
3. Verify average response time < 2 seconds

### 8.2 Concurrent Users
**Test Case ID**: PERF_POS_002
**Scenario**: System handles multiple concurrent users
**Test Steps**:
1. Simulate 10 concurrent chat sessions
2. Verify all sessions receive responses
3. Verify session isolation is maintained

### 8.3 Knowledge Base Performance
**Test Case ID**: PERF_POS_003
**Scenario**: Vector search performs efficiently
**Test Steps**:
1. Perform complex semantic searches
2. Measure search response times
3. Verify search accuracy

## 9. Data Persistence - Positive Cases

### 9.1 Session Persistence
**Test Case ID**: DATA_POS_001
**Scenario**: Conversation sessions are properly maintained
**Test Steps**:
1. Start conversation and capture session_id
2. Continue conversation with same session_id
3. Verify context is maintained across messages

### 9.2 Database Persistence
**Test Case ID**: DATA_POS_002
**Scenario**: Tickets and user data persist correctly
**Test Steps**:
1. Create tickets and user interactions
2. Restart system services
3. Verify data persistence after restart

### 9.3 Log Persistence
**Test Case ID**: DATA_POS_003
**Scenario**: All interactions are properly logged
**Test Steps**:
1. Perform various system operations
2. Check log files for corresponding entries
3. Verify log completeness and accuracy

## 10. Security - Positive Cases

### 10.1 JWT Token Validation
**Test Case ID**: SEC_POS_001
**Scenario**: Valid JWT tokens provide proper access
**Test Steps**:
1. Generate valid JWT token
2. Access protected endpoints with token
3. Verify successful authentication
4. Verify token expiration handling

### 10.2 Role-Based Access
**Test Case ID**: SEC_POS_002
**Scenario**: Users access only authorized resources
**Test Steps**:
1. Login as regular user
2. Verify access to user-level resources
3. Login as support engineer
4. Verify access to admin-level resources

### 10.3 Password Security
**Test Case ID**: SEC_POS_003
**Scenario**: Passwords are properly hashed and validated
**Test Steps**:
1. Create user with password
2. Verify password is hashed in database
3. Verify password validation works correctly
4. Verify failed login attempts are handled

**Success Criteria for All Positive Test Cases**:
- All API responses return expected status codes
- Response data matches expected schemas
- System functionality works as designed
- Performance meets specified requirements
- Security measures function correctly
- User experience is smooth and intuitive