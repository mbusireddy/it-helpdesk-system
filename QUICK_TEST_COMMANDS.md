# 🚀 Quick Test Commands - IT Helpdesk System

## Essential Commands

### Start & Test Everything
```bash
# Complete system test (recommended)
./test_everything.sh

# Quick system verification  
./test_system.sh

# Start services if not running
./start_services.sh
```

### Run Specific Tests
```bash
# Authentication tests only
./test_auth.sh

# Unit tests only
./run_tests.sh

# Individual test files
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python -m pytest tests/test_auth.py -v
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python -m pytest tests/test_agents.py -v
```

### Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# User login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "appuser", "password": "password123"}'

# Chat with authentication (replace TOKEN)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"content": "My computer wont start", "user_id": "test"}'
```

## Web Interfaces

| Interface | URL | Purpose |
|-----------|-----|---------|
| Chat Interface | http://localhost:8501 | Interactive chat with AI agents |
| Dashboard | http://localhost:8502 | Analytics and ticket management |
| API Documentation | http://localhost:8000/docs | Interactive API docs |

## Test User Accounts

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `appuser` | `password123` | Regular User | Chat, view own tickets |
| `support-engineer` | `support123` | Support Engineer | All tickets, status updates |

## Quick Verification Checklist

✅ **Services Running**
```bash
# Should show 3 processes on ports 8000, 8501, 8502
lsof -i:8000,8501,8502
```

✅ **Authentication Working**
```bash
# Should return access_token
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "appuser", "password": "password123"}'
```

✅ **Agents Responding**
```bash
# Test with your token from login
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"content": "Help with email", "user_id": "test"}'
```

✅ **Database Active**
```bash
# Should show users and tickets
sqlite3 helpdesk.db "SELECT username, role FROM users;"
sqlite3 helpdesk.db "SELECT id, category, status FROM tickets LIMIT 3;"
```

## Troubleshooting

### If Services Won't Start
```bash
./stop_services.sh
./start_services.sh
```

### If Tests Fail
```bash
# Set environment variable
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Check logs
tail -f app.log
```

### If Authentication Fails
```bash
# Check users exist
sqlite3 helpdesk.db "SELECT * FROM users;"

# Test auth endpoint
./test_auth.sh
```

## Performance Testing

```bash
# Test concurrent requests
for i in {1..5}; do
  curl -s http://localhost:8000/health &
done
wait

# Check memory usage
ps aux | grep -E "(python|streamlit)" | grep -v grep
```

## 🎯 Complete Test Coverage

Run `./test_everything.sh` for comprehensive testing of:
- ✅ All 3 services (API, Chat UI, Dashboard)
- ✅ Authentication system (both user types)  
- ✅ Role-based access control
- ✅ Multi-agent chat system
- ✅ Database connectivity
- ✅ Unit tests (15 tests total)
- ✅ End-to-end workflow
- ✅ Ollama integration
- ✅ Performance check

**Expected Result:** All core functionality working with detailed status report.