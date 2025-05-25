# IT Helpdesk System - Complete Testing Guide

## 🚀 Quick Start - Test Everything

### 1. Start the System
```bash
# Start all services
./start_services.sh

# Verify all services are running
./test_system.sh
```

### 2. Run All Tests
```bash
# Run comprehensive test suite
./run_tests.sh

# Or run specific test categories
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python -m pytest tests/ -v
```

## 🧪 Testing Components

### A. Authentication System Testing
```bash
# Test authentication endpoints
./test_auth.sh

# Run authentication unit tests
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python -m pytest tests/test_auth.py -v
```

**Test Coverage:**
- ✅ User login (appuser/password123, support-engineer/support123)
- ✅ JWT token creation and verification
- ✅ Role-based access control
- ✅ Password hashing and verification
- ✅ Support engineer permissions

### B. Multi-Agent System Testing
```bash
# Run agent workflow tests
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python -m pytest tests/test_agents.py -v
```

**Test Coverage:**
- ✅ Classifier Agent (IT/HR/Accounting routing)
- ✅ IT Support Agent (knowledge base + web search)
- ✅ HR Agent (vacation, policies)
- ✅ Accounting Agent (expenses, reimbursements)
- ✅ Complete workflow integration

### C. API Endpoint Testing
```bash
# Test API endpoints manually
curl -X GET http://localhost:8000/health

# Test with authentication
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "appuser", "password": "password123"}'
```

### D. UI Interface Testing
```bash
# Access web interfaces
echo "Chat Interface: http://localhost:8501"
echo "Dashboard: http://localhost:8502"
echo "API Docs: http://localhost:8000/docs"
```

## 🔍 Manual Functionality Testing

### 1. Authentication Flow
1. **Login as Regular User:**
   - Username: `appuser`
   - Password: `password123`
   - Should get JWT token and access to chat/analytics

2. **Login as Support Engineer:**
   - Username: `support-engineer`
   - Password: `support123`
   - Should get additional permissions for ticket management

### 2. Chat System Testing
1. **Open Chat Interface:** http://localhost:8501
2. **Test IT Support Queries:**
   ```
   "My computer won't start"
   "Email is not working"
   "WiFi connection issues"
   ```
3. **Test HR Queries:**
   ```
   "How do I request vacation time?"
   "What are the company policies?"
   "Need help with payroll"
   ```
4. **Test Accounting Queries:**
   ```
   "How do I submit expenses?"
   "Need help with reimbursement"
   "Invoice processing question"
   ```

### 3. Dashboard Testing
1. **Open Dashboard:** http://localhost:8502
2. **Verify Analytics:**
   - Total tickets count
   - Open vs resolved tickets
   - Category breakdown
   - Resolution rate

### 4. Support Engineer Features
1. **Login as support engineer**
2. **Test Ticket Management:**
   - View all tickets: `GET /tickets/all`
   - Update ticket status: `PUT /ticket/update`
   - Assign tickets to engineers

## 📊 Expected Test Results

### Unit Tests (15 total)
```
✅ Authentication Service: 6 tests
✅ User Model: 2 tests  
✅ Agent Workflows: 7 tests
```

### Integration Tests
```
✅ Health check endpoint
✅ Chat endpoint with authentication
✅ Analytics endpoint
✅ Role-based access control
✅ Multi-agent workflow
```

### System Tests
```
✅ All services running (ports 8000, 8501, 8502)
✅ Database connectivity
✅ Ollama integration (7 models available)
✅ Authentication system
✅ Vector database (ChromaDB)
```

## 🛠️ Test Commands Reference

### Start/Stop System
```bash
./start_services.sh    # Start all services
./stop_services.sh     # Stop all services
./test_system.sh       # Verify system status
```

### Run Tests
```bash
./run_tests.sh                    # Run all working tests
./test_auth.sh                    # Test authentication only
python -m pytest tests/ -v       # Run pytest with verbose output
```

### Check Logs
```bash
tail -f app.log                   # Main application logs
tail -f chat_ui.log              # Chat interface logs  
tail -f dashboard.log            # Dashboard logs
tail -f logs/helpdesk.log        # System logs
```

### Database Testing
```bash
# Check database
sqlite3 helpdesk.db "SELECT * FROM users;"
sqlite3 helpdesk.db "SELECT * FROM tickets LIMIT 5;"
```

### Ollama Testing
```bash
# Check available models
ollama list

# Test model directly
ollama run qwen2.5:14b "Hello, how can you help with IT support?"
```

## 🚨 Troubleshooting

### If Tests Fail
1. **Check services are running:** `./test_system.sh`
2. **Check environment variable:** `export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`
3. **Restart services:** `./stop_services.sh && ./start_services.sh`
4. **Check logs:** `tail -f app.log`

### If Authentication Fails
1. **Verify users exist:** `sqlite3 helpdesk.db "SELECT username, role FROM users;"`
2. **Test login:** `./test_auth.sh`
3. **Check JWT secret:** Verify `JWT_SECRET_KEY` in config

### If Agents Don't Respond
1. **Check Ollama:** `ollama list`
2. **Test model:** `ollama run qwen2.5:14b "test"`
3. **Check ChromaDB:** Verify `chroma_db/` directory exists
4. **Check vector service:** Look for embedding errors in logs

## 📈 Performance Testing

### Load Testing
```bash
# Test concurrent requests
for i in {1..10}; do
  curl -X GET http://localhost:8000/health &
done
wait
```

### Memory Usage
```bash
# Check process memory
ps aux | grep -E "(python|streamlit)" | grep -v grep
```

## ✅ Success Criteria

Your system is working correctly if:
- ✅ All 15 unit tests pass
- ✅ All 3 services respond (8000, 8501, 8502)
- ✅ Authentication works for both user types
- ✅ Chat interface responds to queries
- ✅ Dashboard shows analytics
- ✅ Agents route queries correctly
- ✅ Support engineer features work
- ✅ Database stores tickets and users
- ✅ Ollama integration functions

Run `./test_system.sh` for a complete system verification!