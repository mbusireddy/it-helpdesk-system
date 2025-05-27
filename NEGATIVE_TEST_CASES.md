# IT Helpdesk System - Negative Test Cases

## 1. Authentication & Authorization - Negative Cases

### 1.1 Invalid Credentials
**Test Case ID**: AUTH_NEG_001
**Scenario**: User attempts login with incorrect credentials
**Test Steps**:
1. Send POST request to `/login` with invalid username/password
2. Verify 401 status code
3. Verify error message indicates invalid credentials
4. Verify no token is provided

**Test Data**:
```json
{
  "username": "invalid_user",
  "password": "wrong_password"
}
```

**Expected Result**: Authentication fails with appropriate error message

### 1.2 Missing Required Fields
**Test Case ID**: AUTH_NEG_002
**Scenario**: Login request with missing required fields
**Test Steps**:
1. Send POST request to `/login` with missing password field
2. Verify 422 status code (validation error)
3. Verify error details indicate missing field

**Test Data**:
```json
{
  "username": "appuser"
  // password field missing
}
```

### 1.3 Empty Credentials
**Test Case ID**: AUTH_NEG_003
**Scenario**: Login with empty username or password
**Test Steps**:
1. Send POST request with empty strings
2. Verify appropriate error response
3. Verify authentication fails

**Test Data**:
```json
{
  "username": "",
  "password": ""
}
```

### 1.4 Invalid Token Access
**Test Case ID**: AUTH_NEG_004
**Scenario**: Access protected endpoint with invalid token
**Test Steps**:
1. Send GET request to `/me` with malformed token
2. Verify 401 status code
3. Verify error message indicates invalid token

**Test Data**: `Authorization: Bearer invalid_token_format`

### 1.5 Expired Token Access
**Test Case ID**: AUTH_NEG_005
**Scenario**: Access endpoint with expired JWT token
**Test Steps**:
1. Create JWT token with very short expiration
2. Wait for token to expire
3. Attempt to access protected endpoint
4. Verify 401 status code

### 1.6 Missing Authorization Header
**Test Case ID**: AUTH_NEG_006
**Scenario**: Access protected endpoint without authorization header
**Test Steps**:
1. Send GET request to `/me` without Authorization header
2. Verify 403 status code
3. Verify appropriate error message

### 1.7 Malformed Authorization Header
**Test Case ID**: AUTH_NEG_007
**Scenario**: Authorization header with incorrect format
**Test Steps**:
1. Send request with malformed header (missing "Bearer" prefix)
2. Verify authentication fails
3. Verify appropriate error response

**Test Data**: `Authorization: invalid_header_format`

## 2. Role-Based Access Control - Negative Cases

### 2.1 Regular User Accessing Admin Endpoints
**Test Case ID**: RBAC_NEG_001
**Scenario**: Regular user attempts to access support engineer endpoints
**Test Steps**:
1. Login as regular user
2. Attempt GET request to `/tickets/all`
3. Verify 403 status code
4. Verify error message indicates insufficient privileges

### 2.2 Regular User Updating Tickets
**Test Case ID**: RBAC_NEG_002
**Scenario**: Regular user attempts to update ticket status
**Test Steps**:
1. Login as regular user
2. Send PUT request to `/ticket/update`
3. Verify 403 status code
4. Verify access denied message

**Test Data**:
```json
{
  "ticket_id": 1,
  "status": "resolved"
}
```

### 2.3 Cross-User Ticket Access
**Test Case ID**: RBAC_NEG_003
**Scenario**: User attempts to access another user's tickets
**Test Steps**:
1. Login as user A
2. Attempt to access user B's tickets
3. Verify access control prevents unauthorized access

## 3. Chat System - Negative Cases

### 3.1 Chat Without Authentication
**Test Case ID**: CHAT_NEG_001
**Scenario**: Attempt chat without valid authentication
**Test Steps**:
1. Send POST request to `/chat` without token
2. Verify 401 or 403 status code
3. Verify error message indicates authentication required

### 3.2 Invalid JSON Payload
**Test Case ID**: CHAT_NEG_002
**Scenario**: Send malformed JSON to chat endpoint
**Test Steps**:
1. Send POST request with malformed JSON
2. Verify 422 status code
3. Verify JSON parsing error response

**Test Data**: `{ "content": "test", "user_id": incomplete json`

### 3.3 Missing Required Chat Fields
**Test Case ID**: CHAT_NEG_003
**Scenario**: Chat request missing required fields
**Test Steps**:
1. Send POST request missing `content` field
2. Verify 422 status code
3. Verify validation error details

**Test Data**:
```json
{
  "user_id": "test_user"
  // content field missing
}
```

### 3.4 Empty Chat Message
**Test Case ID**: CHAT_NEG_004
**Scenario**: Send empty or whitespace-only message
**Test Steps**:
1. Send chat with empty content
2. Verify system handles gracefully
3. Verify appropriate response or error

**Test Data**:
```json
{
  "content": "",
  "user_id": "test_user"
}
```

### 3.5 Excessively Long Message
**Test Case ID**: CHAT_NEG_005
**Scenario**: Send message exceeding length limits
**Test Steps**:
1. Send chat with very long content (>10000 characters)
2. Verify system handles appropriately
3. Verify response or truncation

### 3.6 Special Characters and Injection
**Test Case ID**: CHAT_NEG_006
**Scenario**: Send message with SQL injection attempts
**Test Steps**:
1. Send chat with SQL injection patterns
2. Verify system sanitizes input
3. Verify no database compromise

**Test Data**: `'; DROP TABLE tickets; --`

### 3.7 Script Injection Attempts
**Test Case ID**: CHAT_NEG_007
**Scenario**: Send message with script injection attempts
**Test Steps**:
1. Send chat with HTML/JS injection
2. Verify system sanitizes input
3. Verify no script execution

**Test Data**: `<script>alert('xss')</script>`

## 4. Ticket Management - Negative Cases

### 4.1 Invalid Ticket ID
**Test Case ID**: TICKET_NEG_001
**Scenario**: Request status for non-existent ticket
**Test Steps**:
1. Send POST request to `/ticket/status` with invalid ID
2. Verify 404 status code
3. Verify "Ticket not found" error message

**Test Data**:
```json
{
  "ticket_id": 99999
}
```

### 4.2 Negative Ticket ID
**Test Case ID**: TICKET_NEG_002
**Scenario**: Request ticket with negative ID
**Test Steps**:
1. Send request with negative ticket ID
2. Verify appropriate error handling
3. Verify proper error response

**Test Data**:
```json
{
  "ticket_id": -1
}
```

### 4.3 Non-Numeric Ticket ID
**Test Case ID**: TICKET_NEG_003
**Scenario**: Request ticket with non-numeric ID
**Test Steps**:
1. Send request with string ticket ID
2. Verify 422 status code (validation error)
3. Verify type validation error

**Test Data**:
```json
{
  "ticket_id": "invalid_id"
}
```

### 4.4 Update Non-Existent Ticket
**Test Case ID**: TICKET_NEG_004
**Scenario**: Support engineer attempts to update non-existent ticket
**Test Steps**:
1. Login as support engineer
2. Send PUT request to `/ticket/update` with invalid ID
3. Verify 404 status code

### 4.5 Invalid Ticket Status
**Test Case ID**: TICKET_NEG_005
**Scenario**: Update ticket with invalid status value
**Test Steps**:
1. Attempt to update ticket with invalid status
2. Verify validation error
3. Verify ticket status unchanged

**Test Data**:
```json
{
  "ticket_id": 1,
  "status": "invalid_status"
}
```

### 4.6 Missing Ticket Update Fields
**Test Case ID**: TICKET_NEG_006
**Scenario**: Ticket update request missing required fields
**Test Steps**:
1. Send PUT request missing ticket_id
2. Verify 422 status code
3. Verify validation error details

## 5. Agent System - Negative Cases

### 5.1 LLM Service Unavailable
**Test Case ID**: AGENT_NEG_001
**Scenario**: Ollama service is down during chat
**Test Steps**:
1. Stop Ollama service
2. Send chat message requiring LLM
3. Verify graceful error handling
4. Verify appropriate error message to user

### 5.2 Vector Database Unavailable
**Test Case ID**: AGENT_NEG_002
**Scenario**: ChromaDB unavailable during knowledge search
**Test Steps**:
1. Make ChromaDB inaccessible
2. Send IT query requiring knowledge search
3. Verify fallback mechanism
4. Verify error handling

### 5.3 Web Search Service Failure
**Test Case ID**: AGENT_NEG_003
**Scenario**: Web search API returns error
**Test Steps**:
1. Mock web search to return error
2. Send query requiring web search
3. Verify graceful degradation
4. Verify user receives helpful response

### 5.4 Invalid Agent State
**Test Case ID**: AGENT_NEG_004
**Scenario**: Agent workflow reaches invalid state
**Test Steps**:
1. Manipulate agent state to invalid condition
2. Attempt to continue conversation
3. Verify error recovery mechanism
4. Verify user experience maintained

### 5.5 Classification Failure
**Test Case ID**: AGENT_NEG_005
**Scenario**: Classifier agent fails to categorize query
**Test Steps**:
1. Send ambiguous or unclear query
2. Verify default routing behavior
3. Verify user receives helpful response

**Test Data**: Random characters or extremely ambiguous text

### 5.6 Memory Exhaustion
**Test Case ID**: AGENT_NEG_006
**Scenario**: Agent conversation exceeds memory limits
**Test Steps**:
1. Create very long conversation history
2. Attempt to continue conversation
3. Verify memory management
4. Verify system stability

## 6. Database - Negative Cases

### 6.1 Database Connection Failure
**Test Case ID**: DB_NEG_001
**Scenario**: Database becomes unavailable
**Test Steps**:
1. Simulate database connection failure
2. Attempt various operations
3. Verify error handling
4. Verify service degradation

### 6.2 Database Corruption
**Test Case ID**: DB_NEG_002
**Scenario**: Database file corruption
**Test Steps**:
1. Corrupt database file
2. Attempt to start services
3. Verify error detection
4. Verify recovery procedures

### 6.3 Concurrent Write Conflicts
**Test Case ID**: DB_NEG_003
**Scenario**: Multiple simultaneous database writes
**Test Steps**:
1. Simulate concurrent ticket updates
2. Verify transaction handling
3. Verify data consistency
4. Verify no data loss

### 6.4 SQL Injection Attempts
**Test Case ID**: DB_NEG_004
**Scenario**: Malicious SQL injection through input fields
**Test Steps**:
1. Send SQL injection patterns in various inputs
2. Verify parameterized queries prevent injection
3. Verify database integrity maintained

## 7. API Validation - Negative Cases

### 7.1 Invalid HTTP Methods
**Test Case ID**: API_NEG_001
**Scenario**: Use incorrect HTTP method for endpoints
**Test Steps**:
1. Send GET request to POST-only endpoint
2. Verify 405 status code (Method Not Allowed)
3. Verify proper error response

### 7.2 Invalid Content-Type
**Test Case ID**: API_NEG_002
**Scenario**: Send request with wrong Content-Type header
**Test Steps**:
1. Send JSON data with text/plain Content-Type
2. Verify 422 or 400 status code
3. Verify content type validation error

### 7.3 Malformed Request Headers
**Test Case ID**: API_NEG_003
**Scenario**: Send requests with malformed headers
**Test Steps**:
1. Send request with invalid header format
2. Verify appropriate error handling
3. Verify service stability

### 7.4 Request Size Limits
**Test Case ID**: API_NEG_004
**Scenario**: Send extremely large request payload
**Test Steps**:
1. Send request exceeding size limits
2. Verify 413 status code (Payload Too Large)
3. Verify service handles gracefully

### 7.5 Invalid JSON Structure
**Test Case ID**: API_NEG_005
**Scenario**: Send syntactically invalid JSON
**Test Steps**:
1. Send request with malformed JSON syntax
2. Verify 400 status code
3. Verify JSON parsing error message

## 8. Performance & Load - Negative Cases

### 8.1 High Concurrent Load
**Test Case ID**: PERF_NEG_001
**Scenario**: System under extreme concurrent load
**Test Steps**:
1. Simulate 100+ concurrent chat sessions
2. Monitor system performance
3. Verify graceful degradation
4. Verify no complete service failure

### 8.2 Memory Exhaustion
**Test Case ID**: PERF_NEG_002
**Scenario**: System runs out of available memory
**Test Steps**:
1. Create memory-intensive scenarios
2. Monitor system behavior
3. Verify error handling
4. Verify service recovery

### 8.3 Network Timeouts
**Test Case ID**: PERF_NEG_003
**Scenario**: Network timeouts during external service calls
**Test Steps**:
1. Simulate network delays for Ollama/web search
2. Verify timeout handling
3. Verify user receives appropriate response

### 8.4 Rate Limiting
**Test Case ID**: PERF_NEG_004
**Scenario**: Excessive requests from single user
**Test Steps**:
1. Send rapid consecutive requests
2. Verify rate limiting (if implemented)
3. Verify system stability

## 9. File System - Negative Cases

### 9.1 Disk Space Exhaustion
**Test Case ID**: FS_NEG_001
**Scenario**: System runs out of disk space
**Test Steps**:
1. Fill disk space to capacity
2. Attempt logging and database operations
3. Verify error handling
4. Verify service behavior

### 9.2 Log File Permission Issues
**Test Case ID**: FS_NEG_002
**Scenario**: Log directory becomes write-protected
**Test Steps**:
1. Remove write permissions from log directory
2. Attempt system operations
3. Verify logging error handling
4. Verify core functionality maintained

### 9.3 Database File Permissions
**Test Case ID**: FS_NEG_003
**Scenario**: Database file becomes read-only
**Test Steps**:
1. Change database file to read-only
2. Attempt write operations
3. Verify error handling
4. Verify appropriate error messages

## 10. Configuration - Negative Cases

### 10.1 Invalid Configuration Values
**Test Case ID**: CONFIG_NEG_001
**Scenario**: Start system with invalid configuration
**Test Steps**:
1. Set invalid Ollama URL in config
2. Attempt to start services
3. Verify startup error handling
4. Verify clear error messages

### 10.2 Missing Configuration Files
**Test Case ID**: CONFIG_NEG_002
**Scenario**: Required configuration files missing
**Test Steps**:
1. Remove or rename config files
2. Attempt to start services
3. Verify default value handling
4. Verify service startup behavior

### 10.3 Environment Variable Conflicts
**Test Case ID**: CONFIG_NEG_003
**Scenario**: Conflicting environment variables
**Test Steps**:
1. Set conflicting environment variables
2. Start services
3. Verify configuration precedence
4. Verify predictable behavior

## 11. Security - Negative Cases

### 11.1 Password Brute Force
**Test Case ID**: SEC_NEG_001
**Scenario**: Repeated failed login attempts
**Test Steps**:
1. Attempt multiple failed logins rapidly
2. Verify account lockout (if implemented)
3. Verify rate limiting protection
4. Verify security logging

### 11.2 Token Manipulation
**Test Case ID**: SEC_NEG_002
**Scenario**: Attempt to manipulate JWT token contents
**Test Steps**:
1. Modify JWT token payload
2. Attempt to access protected resources
3. Verify token validation fails
4. Verify access denied

### 11.3 Session Hijacking Attempts
**Test Case ID**: SEC_NEG_003
**Scenario**: Attempt to use another user's session
**Test Steps**:
1. Capture valid session token
2. Attempt to use from different context
3. Verify session validation
4. Verify access control

### 11.4 CORS Violations
**Test Case ID**: SEC_NEG_004
**Scenario**: Attempt requests from unauthorized origins
**Test Steps**:
1. Send requests from blocked origins
2. Verify CORS policy enforcement
3. Verify requests are blocked

## 12. Integration - Negative Cases

### 12.1 External Service Dependencies
**Test Case ID**: INT_NEG_001
**Scenario**: All external services unavailable
**Test Steps**:
1. Disable Ollama, web search, etc.
2. Attempt normal operations
3. Verify fallback mechanisms
4. Verify degraded service provision

### 12.2 Partial Service Failures
**Test Case ID**: INT_NEG_002
**Scenario**: Some but not all services available
**Test Steps**:
1. Disable specific services selectively
2. Verify selective feature degradation
3. Verify error communication to users

### 12.3 Service Recovery
**Test Case ID**: INT_NEG_003
**Scenario**: Services recover after failure
**Test Steps**:
1. Simulate service failure
2. Restore services
3. Verify automatic recovery
4. Verify service resumption

## Expected Outcomes for Negative Test Cases

**Security**: All unauthorized access attempts should be blocked with appropriate error messages
**Stability**: System should remain stable and not crash under any negative conditions
**Error Handling**: All errors should be caught and handled gracefully with informative messages
**Data Integrity**: No data corruption or loss should occur during any failure scenarios
**User Experience**: Users should receive helpful error messages and alternative options when possible
**Recovery**: System should be able to recover from failures automatically where possible
**Logging**: All errors and security events should be properly logged for analysis