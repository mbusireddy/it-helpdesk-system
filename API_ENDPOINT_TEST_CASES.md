# IT Helpdesk System - API Endpoint Test Cases

## Overview

This document provides comprehensive test cases for all API endpoints in the IT Helpdesk System. Each endpoint is tested for both positive and negative scenarios with detailed request/response validation.

## API Base URL: `http://localhost:8000`

---

## 1. Health Check Endpoint

### `GET /health`

#### Positive Test Cases

**Test Case**: `HEALTH_001_SUCCESS`
```bash
# Request
curl -X GET http://localhost:8000/health

# Expected Response (200 OK)
{
  "status": "healthy",
  "service": "IT Helpdesk System"
}
```

#### Negative Test Cases

**Test Case**: `HEALTH_002_INVALID_METHOD`
```bash
# Request
curl -X POST http://localhost:8000/health

# Expected Response (405 Method Not Allowed)
{
  "detail": "Method Not Allowed"
}
```

---

## 2. Authentication Endpoints

### `POST /login`

#### Positive Test Cases

**Test Case**: `LOGIN_001_REGULAR_USER_SUCCESS`
```bash
# Request
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "appuser",
    "password": "password123"
  }'

# Expected Response (200 OK)
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "username": "appuser",
    "full_name": "Application User",
    "role": "user",
    "email": "appuser@example.com"
  }
}
```

**Test Case**: `LOGIN_002_SUPPORT_USER_SUCCESS`
```bash
# Request
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "support-engineer",
    "password": "support123"
  }'

# Expected Response (200 OK)
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "username": "support-engineer",
    "full_name": "Support Engineer",
    "role": "support-engineer",
    "email": "support@example.com"
  }
}
```

#### Negative Test Cases

**Test Case**: `LOGIN_003_INVALID_CREDENTIALS`
```bash
# Request
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "invalid_user",
    "password": "wrong_password"
  }'

# Expected Response (401 Unauthorized)
{
  "detail": "Invalid username or password"
}
```

**Test Case**: `LOGIN_004_MISSING_PASSWORD`
```bash
# Request
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "appuser"
  }'

# Expected Response (422 Unprocessable Entity)
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "password"],
      "msg": "Field required"
    }
  ]
}
```

**Test Case**: `LOGIN_005_EMPTY_CREDENTIALS`
```bash
# Request
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "",
    "password": ""
  }'

# Expected Response (401 Unauthorized)
{
  "detail": "Invalid username or password"
}
```

**Test Case**: `LOGIN_006_INVALID_JSON`
```bash
# Request
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", invalid json'

# Expected Response (422 Unprocessable Entity)
{
  "detail": "Invalid JSON format"
}
```

---

## 3. User Profile Endpoint

### `GET /me`

#### Positive Test Cases

**Test Case**: `PROFILE_001_VALID_TOKEN`
```bash
# Request (requires valid token)
curl -X GET http://localhost:8000/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Expected Response (200 OK)
{
  "username": "appuser",
  "full_name": "Application User",
  "role": "user",
  "email": "appuser@example.com",
  "last_login": "2024-01-15T10:30:00"
}
```

#### Negative Test Cases

**Test Case**: `PROFILE_002_NO_TOKEN`
```bash
# Request
curl -X GET http://localhost:8000/me

# Expected Response (403 Forbidden)
{
  "detail": "Not authenticated"
}
```

**Test Case**: `PROFILE_003_INVALID_TOKEN`
```bash
# Request
curl -X GET http://localhost:8000/me \
  -H "Authorization: Bearer invalid_token"

# Expected Response (401 Unauthorized)
{
  "detail": "Invalid authentication token"
}
```

**Test Case**: `PROFILE_004_MALFORMED_HEADER`
```bash
# Request
curl -X GET http://localhost:8000/me \
  -H "Authorization: invalid_format"

# Expected Response (403 Forbidden)
{
  "detail": "Invalid authentication credentials"
}
```

---

## 4. Chat Endpoint

### `POST /chat`

#### Positive Test Cases

**Test Case**: `CHAT_001_BASIC_MESSAGE`
```bash
# Request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "content": "My computer won'\''t start",
    "user_id": "test_user_123"
  }'

# Expected Response (200 OK)
{
  "response": "I understand you're having trouble with your computer not starting...",
  "session_id": "abc123-def456-ghi789",
  "agent": "it_support",
  "ticket_id": null
}
```

**Test Case**: `CHAT_002_WITH_SESSION_ID`
```bash
# Request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "content": "It shows a blue screen",
    "user_id": "test_user_123",
    "session_id": "abc123-def456-ghi789"
  }'

# Expected Response (200 OK)
{
  "response": "A blue screen error typically indicates...",
  "session_id": "abc123-def456-ghi789",
  "agent": "it_support",
  "ticket_id": null
}
```

**Test Case**: `CHAT_003_HR_QUERY`
```bash
# Request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "content": "How do I request vacation time?",
    "user_id": "test_user_456"
  }'

# Expected Response (200 OK)
{
  "response": "To request vacation time, you can...",
  "session_id": "def456-ghi789-jkl012",
  "agent": "hr",
  "ticket_id": null
}
```

#### Negative Test Cases

**Test Case**: `CHAT_004_MISSING_CONTENT`
```bash
# Request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123"
  }'

# Expected Response (422 Unprocessable Entity)
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "content"],
      "msg": "Field required"
    }
  ]
}
```

**Test Case**: `CHAT_005_MISSING_USER_ID`
```bash
# Request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Help me"
  }'

# Expected Response (422 Unprocessable Entity)
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "user_id"],
      "msg": "Field required"
    }
  ]
}
```

**Test Case**: `CHAT_006_EMPTY_CONTENT`
```bash
# Request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "content": "",
    "user_id": "test_user_123"
  }'

# Expected Response (200 OK - should handle gracefully)
{
  "response": "I'm here to help! Could you please provide more details about your issue?",
  "session_id": "generated_session_id",
  "agent": "classifier"
}
```

**Test Case**: `CHAT_007_VERY_LONG_MESSAGE`
```bash
# Request with 10000+ character message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "content": "'$(python3 -c "print('x' * 10000)")'",
    "user_id": "test_user_123"
  }'

# Expected Response (413 or handled gracefully)
```

---

## 5. Ticket Status Endpoint

### `POST /ticket/status`

#### Positive Test Cases

**Test Case**: `TICKET_STATUS_001_VALID_ID`
```bash
# Request
curl -X POST http://localhost:8000/ticket/status \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 1
  }'

# Expected Response (200 OK)
{
  "id": 1,
  "status": "open",
  "category": "IT_HARDWARE",
  "title": "Computer startup issue",
  "description": "User reported computer won't start",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "assigned_to": null
}
```

#### Negative Test Cases

**Test Case**: `TICKET_STATUS_002_INVALID_ID`
```bash
# Request
curl -X POST http://localhost:8000/ticket/status \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 99999
  }'

# Expected Response (404 Not Found)
{
  "detail": "Ticket not found"
}
```

**Test Case**: `TICKET_STATUS_003_NEGATIVE_ID`
```bash
# Request
curl -X POST http://localhost:8000/ticket/status \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": -1
  }'

# Expected Response (422 Unprocessable Entity)
{
  "detail": "Ticket ID must be positive"
}
```

**Test Case**: `TICKET_STATUS_004_STRING_ID`
```bash
# Request
curl -X POST http://localhost:8000/ticket/status \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "invalid"
  }'

# Expected Response (422 Unprocessable Entity)
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["body", "ticket_id"],
      "msg": "Input should be a valid integer"
    }
  ]
}
```

---

## 6. User Tickets Endpoint

### `GET /tickets/user/{user_id}`

#### Positive Test Cases

**Test Case**: `USER_TICKETS_001_WITH_TICKETS`
```bash
# Request
curl -X GET http://localhost:8000/tickets/user/test_user_123

# Expected Response (200 OK)
[
  {
    "id": 1,
    "status": "open",
    "category": "IT_HARDWARE",
    "title": "Computer startup issue",
    "description": "User reported computer won't start",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "assigned_to": null
  },
  {
    "id": 2,
    "status": "resolved",
    "category": "IT_SOFTWARE",
    "title": "Email configuration",
    "description": "Help with email setup",
    "created_at": "2024-01-14T09:15:00",
    "updated_at": "2024-01-14T11:30:00",
    "assigned_to": "support-engineer"
  }
]
```

**Test Case**: `USER_TICKETS_002_NO_TICKETS`
```bash
# Request
curl -X GET http://localhost:8000/tickets/user/new_user

# Expected Response (200 OK)
[]
```

#### Negative Test Cases

**Test Case**: `USER_TICKETS_003_INVALID_USER_ID`
```bash
# Request with special characters
curl -X GET "http://localhost:8000/tickets/user/user@#$%"

# Expected Response (422 or handled gracefully)
```

---

## 7. Ticket Update Endpoint (Support Engineer Only)

### `PUT /ticket/update`

#### Positive Test Cases

**Test Case**: `TICKET_UPDATE_001_STATUS_CHANGE`
```bash
# Request (requires support engineer token)
curl -X PUT http://localhost:8000/ticket/update \
  -H "Authorization: Bearer support_engineer_token" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 1,
    "status": "in_progress"
  }'

# Expected Response (200 OK)
{
  "id": 1,
  "status": "in_progress",
  "category": "IT_HARDWARE",
  "title": "Computer startup issue",
  "description": "User reported computer won't start",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:45:00",
  "assigned_to": "support-engineer"
}
```

**Test Case**: `TICKET_UPDATE_002_WITH_ASSIGNMENT`
```bash
# Request
curl -X PUT http://localhost:8000/ticket/update \
  -H "Authorization: Bearer support_engineer_token" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 1,
    "status": "resolved",
    "assigned_to": "senior-support"
  }'

# Expected Response (200 OK)
{
  "id": 1,
  "status": "resolved",
  "category": "IT_HARDWARE",
  "title": "Computer startup issue",
  "description": "User reported computer won't start",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T11:00:00",
  "assigned_to": "senior-support"
}
```

#### Negative Test Cases

**Test Case**: `TICKET_UPDATE_003_REGULAR_USER_DENIED`
```bash
# Request with regular user token
curl -X PUT http://localhost:8000/ticket/update \
  -H "Authorization: Bearer regular_user_token" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 1,
    "status": "resolved"
  }'

# Expected Response (403 Forbidden)
{
  "detail": "Support engineer access required"
}
```

**Test Case**: `TICKET_UPDATE_004_INVALID_TICKET`
```bash
# Request
curl -X PUT http://localhost:8000/ticket/update \
  -H "Authorization: Bearer support_engineer_token" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 99999,
    "status": "resolved"
  }'

# Expected Response (404 Not Found)
{
  "detail": "Ticket not found"
}
```

**Test Case**: `TICKET_UPDATE_005_INVALID_STATUS`
```bash
# Request
curl -X PUT http://localhost:8000/ticket/update \
  -H "Authorization: Bearer support_engineer_token" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": 1,
    "status": "invalid_status"
  }'

# Expected Response (422 Unprocessable Entity)
{
  "detail": "Invalid status value"
}
```

---

## 8. All Tickets Endpoint (Support Engineer Only)

### `GET /tickets/all`

#### Positive Test Cases

**Test Case**: `ALL_TICKETS_001_SUCCESS`
```bash
# Request (requires support engineer token)
curl -X GET http://localhost:8000/tickets/all \
  -H "Authorization: Bearer support_engineer_token"

# Expected Response (200 OK)
[
  {
    "id": 1,
    "status": "open",
    "category": "IT_HARDWARE",
    "title": "Computer startup issue",
    "description": "User reported computer won't start",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "assigned_to": null
  },
  {
    "id": 2,
    "status": "resolved",
    "category": "IT_SOFTWARE",
    "title": "Email configuration",
    "description": "Help with email setup",
    "created_at": "2024-01-14T09:15:00",
    "updated_at": "2024-01-14T11:30:00",
    "assigned_to": "support-engineer"
  }
]
```

#### Negative Test Cases

**Test Case**: `ALL_TICKETS_002_REGULAR_USER_DENIED`
```bash
# Request with regular user token
curl -X GET http://localhost:8000/tickets/all \
  -H "Authorization: Bearer regular_user_token"

# Expected Response (403 Forbidden)
{
  "detail": "Support engineer access required"
}
```

**Test Case**: `ALL_TICKETS_003_NO_AUTH`
```bash
# Request without authentication
curl -X GET http://localhost:8000/tickets/all

# Expected Response (403 Forbidden)
{
  "detail": "Not authenticated"
}
```

---

## 9. Analytics Dashboard Endpoint

### `GET /analytics/dashboard`

#### Positive Test Cases

**Test Case**: `ANALYTICS_001_SUCCESS`
```bash
# Request (requires authentication)
curl -X GET http://localhost:8000/analytics/dashboard \
  -H "Authorization: Bearer valid_token"

# Expected Response (200 OK)
{
  "total_tickets": 15,
  "open_tickets": 5,
  "resolved_tickets": 10,
  "resolution_rate": 66.67,
  "category_breakdown": [
    {
      "category": "IT_HARDWARE",
      "count": 7
    },
    {
      "category": "IT_SOFTWARE",
      "count": 5
    },
    {
      "category": "HR",
      "count": 2
    },
    {
      "category": "ACCOUNTING",
      "count": 1
    }
  ]
}
```

#### Negative Test Cases

**Test Case**: `ANALYTICS_002_NO_AUTH`
```bash
# Request without authentication
curl -X GET http://localhost:8000/analytics/dashboard

# Expected Response (403 Forbidden)
{
  "detail": "Not authenticated"
}
```

**Test Case**: `ANALYTICS_003_INVALID_TOKEN`
```bash
# Request with invalid token
curl -X GET http://localhost:8000/analytics/dashboard \
  -H "Authorization: Bearer invalid_token"

# Expected Response (401 Unauthorized)
{
  "detail": "Invalid authentication token"
}
```

---

## 10. Error Handling Test Cases

### General Error Scenarios

**Test Case**: `ERROR_001_INTERNAL_SERVER_ERROR`
```bash
# Simulate server error condition
# Expected Response (500 Internal Server Error)
{
  "detail": "Internal server error"
}
```

**Test Case**: `ERROR_002_INVALID_ENDPOINT`
```bash
# Request
curl -X GET http://localhost:8000/nonexistent

# Expected Response (404 Not Found)
{
  "detail": "Not Found"
}
```

**Test Case**: `ERROR_003_INVALID_CONTENT_TYPE`
```bash
# Request
curl -X POST http://localhost:8000/login \
  -H "Content-Type: text/plain" \
  -d "username=test&password=test"

# Expected Response (422 Unprocessable Entity)
{
  "detail": "Invalid content type. Expected application/json"
}
```

---

## Test Execution Scripts

### Automated Test Runner

```bash
#!/bin/bash
# run_api_tests.sh

echo "Starting API endpoint tests..."

BASE_URL="http://localhost:8000"

# Test health endpoint
echo "Testing health endpoint..."
curl -s "$BASE_URL/health" | jq .

# Test authentication
echo "Testing authentication..."
TOKEN=$(curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "appuser", "password": "password123"}' | jq -r .access_token)

# Test authenticated endpoints
echo "Testing chat endpoint..."
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message", "user_id": "test_user"}' | jq .

# Test analytics
echo "Testing analytics..."
curl -s -X GET "$BASE_URL/analytics/dashboard" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo "API tests completed."
```

### Performance Test Script

```bash
#!/bin/bash
# performance_test.sh

echo "Running performance tests..."

# Test concurrent requests
for i in {1..10}; do
  curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"content\": \"Test message $i\", \"user_id\": \"perf_test_$i\"}" &
done

wait
echo "Concurrent test completed."
```

### Validation Criteria

**Response Time**: All endpoints should respond within 2 seconds under normal load
**Status Codes**: Correct HTTP status codes for all scenarios
**Response Format**: All responses should be valid JSON with expected structure
**Error Handling**: Appropriate error messages for all failure scenarios
**Security**: Proper authentication and authorization enforcement
**Data Validation**: Input validation working correctly for all endpoints