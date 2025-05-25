#!/bin/bash

echo "=== IT Helpdesk Authentication System Test ==="
echo ""

# Test 1: Login as regular user
echo "1. Testing Regular User Login:"
USER_TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "appuser", "password": "password123"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$USER_TOKEN" ]; then
    echo "✅ Regular user login successful"
else
    echo "❌ Regular user login failed"
fi

# Test 2: Login as support engineer
echo ""
echo "2. Testing Support Engineer Login:"
SUPPORT_TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "support-engineer", "password": "support123"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$SUPPORT_TOKEN" ]; then
    echo "✅ Support engineer login successful"
else
    echo "❌ Support engineer login failed"
fi

# Test 3: Get current user info
echo ""
echo "3. Testing User Info Endpoint:"
USER_INFO=$(curl -s -H "Authorization: Bearer $USER_TOKEN" http://localhost:8000/me)
if echo "$USER_INFO" | grep -q "appuser"; then
    echo "✅ User info endpoint working"
    echo "   User: $(echo $USER_INFO | grep -o '"username":"[^"]*"' | cut -d'"' -f4)"
else
    echo "❌ User info endpoint failed"
fi

# Test 4: Test role-based access control
echo ""
echo "4. Testing Role-Based Access Control:"

# Regular user trying to access support endpoint (should fail)
FORBIDDEN_RESPONSE=$(curl -s -H "Authorization: Bearer $USER_TOKEN" http://localhost:8000/tickets/all)
if echo "$FORBIDDEN_RESPONSE" | grep -q "Support engineer access required"; then
    echo "✅ Regular user correctly denied access to support endpoints"
else
    echo "❌ Role-based access control not working"
fi

# Support engineer accessing support endpoint (should work)
ALL_TICKETS=$(curl -s -H "Authorization: Bearer $SUPPORT_TOKEN" http://localhost:8000/tickets/all)
if echo "$ALL_TICKETS" | grep -q '"id"'; then
    echo "✅ Support engineer can access all tickets"
else
    echo "❌ Support engineer access failed"
fi

# Test 5: Test ticket update by support engineer
echo ""
echo "5. Testing Ticket Update by Support Engineer:"
UPDATE_RESULT=$(curl -s -X PUT http://localhost:8000/ticket/update \
  -H "Authorization: Bearer $SUPPORT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ticket_id": 1, "status": "resolved"}')

if echo "$UPDATE_RESULT" | grep -q '"status":"resolved"'; then
    echo "✅ Support engineer can update ticket status"
    echo "   Ticket 1 marked as resolved"
else
    echo "❌ Ticket update failed"
fi

# Test 6: Test invalid credentials
echo ""
echo "6. Testing Invalid Credentials:"
INVALID_LOGIN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "invalid", "password": "wrong"}')

if echo "$INVALID_LOGIN" | grep -q "Invalid username or password"; then
    echo "✅ Invalid credentials correctly rejected"
else
    echo "❌ Invalid credential handling failed"
fi

# Test 7: Test invalid token
echo ""
echo "7. Testing Invalid Token:"
INVALID_TOKEN_RESPONSE=$(curl -s -H "Authorization: Bearer invalid_token" http://localhost:8000/me)
if echo "$INVALID_TOKEN_RESPONSE" | grep -q "Invalid authentication token"; then
    echo "✅ Invalid token correctly rejected"
else
    echo "❌ Invalid token handling failed"
fi

echo ""
echo "=== Authentication Test Complete ==="
echo ""
echo "User Credentials:"
echo "- Regular User: appuser / password123"
echo "- Support Engineer: support-engineer / support123"
echo ""
echo "API Endpoints:"
echo "- POST /login - User authentication"
echo "- GET /me - Get current user info"
echo "- PUT /ticket/update - Update ticket (support only)"
echo "- GET /tickets/all - Get all tickets (support only)"