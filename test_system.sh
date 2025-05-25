#!/bin/bash

echo "=== Testing IT Helpdesk System ==="

# Check if services are running
echo "1. Service Status Check:"
ss -tlnp | grep -E "(8000|8501|8502)" || echo "Some services may not be running"

echo -e "\n2. Health Check:"
health_response=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$health_response" ]; then
    echo "$health_response"
else
    echo "API not responding"
fi

echo -e "\n3. Chat Test:"
chat_response=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "My printer is not working", "user_id": "test_user"}' 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$chat_response" ]; then
    echo "Chat endpoint working - Response length: ${#chat_response} chars"
else
    echo "Chat endpoint not responding"
fi

echo -e "\n4. Analytics Test:"
analytics_response=$(curl -s http://localhost:8000/analytics/dashboard 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$analytics_response" ]; then
    echo "$analytics_response"
else
    echo "Analytics endpoint not responding"
fi

echo -e "\n5. UI Tests:"
chat_title=$(curl -s http://localhost:8501 2>/dev/null | grep -o '<title>[^<]*' | cut -d'>' -f2)
dashboard_title=$(curl -s http://localhost:8502 2>/dev/null | grep -o '<title>[^<]*' | cut -d'>' -f2)

echo "Chat Interface: ${chat_title:-'Not responding'}"
echo "Dashboard: ${dashboard_title:-'Not responding'}"

echo -e "\n6. Ollama Integration Test:"
ollama_response=$(curl -s http://localhost:11434/api/tags 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$ollama_response" ]; then
    echo "Ollama is running - Available models:"
    echo "$ollama_response" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 || echo "Could not parse model names"
else
    echo "Ollama not responding"
fi

echo -e "\n7. Authentication Test:"
auth_test_result=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "appuser", "password": "password123"}' 2>/dev/null)
if echo "$auth_test_result" | grep -q "access_token"; then
    echo "✅ Authentication system working"
    echo "   Login successful for appuser"
else
    echo "❌ Authentication system failed"
fi

echo -e "\n=== Test completed ==="
echo ""
echo "🔐 Authentication:"
echo "- Regular User: appuser / password123" 
echo "- Support Engineer: support-engineer / support123"
echo "- Test with: ./test_auth.sh"