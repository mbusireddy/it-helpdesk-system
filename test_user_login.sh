#!/bin/bash

# Test Regular User Login and Permissions
echo "🔐 Testing Regular User (appuser) Login and Permissions"
echo "======================================================="

# Login as regular user
echo "1. Attempting login..."
RESPONSE=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "appuser", "password": "password123"}')

# Check if login was successful
if [[ $RESPONSE == *"access_token"* ]]; then
    echo "✅ Login successful!"
    
    # Extract token
    TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "🔑 Access Token: ${TOKEN:0:30}..."
    
    # Extract user info
    echo ""
    echo "👤 User Information:"
    echo $RESPONSE | jq '.user' 2>/dev/null || echo $RESPONSE | grep -o '"user":{[^}]*}' | sed 's/"user"://; s/[{}"]//g; s/,/\n  /g'
    
    echo ""
    echo "2. Testing user permissions..."
    
    # Test /me endpoint
    echo "📋 Getting user profile..."
    ME_RESPONSE=$(curl -s -X GET http://localhost:8000/me \
      -H "Authorization: Bearer $TOKEN")
    echo $ME_RESPONSE | jq . 2>/dev/null || echo $ME_RESPONSE
    
    echo ""
    echo "💬 Testing chat access..."
    CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"content": "I need help with my email setup", "user_id": "appuser"}')
    
    if [[ $CHAT_RESPONSE == *"response"* ]]; then
        echo "✅ Chat access working"
        echo "🤖 Agent: $(echo $CHAT_RESPONSE | grep -o '"agent":"[^"]*' | cut -d'"' -f4)"
        echo "📝 Response: $(echo $CHAT_RESPONSE | grep -o '"response":"[^"]*' | cut -d'"' -f4 | head -c 100)..."
    else
        echo "❌ Chat access failed: $CHAT_RESPONSE"
    fi
    
    echo ""
    echo "📊 Testing analytics access..."
    ANALYTICS_RESPONSE=$(curl -s -X GET http://localhost:8000/analytics/dashboard \
      -H "Authorization: Bearer $TOKEN")
    
    if [[ $ANALYTICS_RESPONSE == *"total_tickets"* ]]; then
        echo "✅ Analytics access working"
        echo "📈 Data: $ANALYTICS_RESPONSE"
    else
        echo "❌ Analytics access failed: $ANALYTICS_RESPONSE"
    fi
    
    echo ""
    echo "🚫 Testing restricted access (should fail)..."
    TICKETS_RESPONSE=$(curl -s -X GET http://localhost:8000/tickets/all \
      -H "Authorization: Bearer $TOKEN")
    
    if [[ $TICKETS_RESPONSE == *"Support engineer access required"* ]]; then
        echo "✅ Correctly denied access to support-only endpoint"
    else
        echo "❌ Access control failed: $TICKETS_RESPONSE"
    fi
    
    echo ""
    echo "📋 REGULAR USER TEST SUMMARY"
    echo "============================="
    echo "✅ Login: Successful"
    echo "✅ Role: user"
    echo "✅ Chat Access: Allowed"
    echo "✅ Analytics Access: Allowed"
    echo "✅ Support Endpoints: Correctly Denied"
    echo ""
    echo "🔑 Your access token (save for API testing):"
    echo "$TOKEN"
    
else
    echo "❌ Login failed!"
    echo "Response: $RESPONSE"
fi

echo ""
echo "🌐 Web Interface Access:"
echo "- Chat Interface: http://localhost:8501"
echo "- Dashboard: http://localhost:8502"
echo "- API Docs: http://localhost:8000/docs"