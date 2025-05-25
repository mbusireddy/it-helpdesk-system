# IT Helpdesk System - Quick Start

## ⚡ One-Command Setup

```bash
# Start all services
./start_services.sh

# Test system
./test_system.sh

# Stop all services  
./stop_services.sh
```

## 🎯 Manual Commands

### Start Services
```bash
# 1. FastAPI Server (Terminal 1)
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export PYTHONPATH=/home/reddy/it-helpdesk-system
cd /home/reddy/it-helpdesk-system
python app/main.py

# 2. Chat Interface (Terminal 2)  
streamlit run app/ui/chat_interface.py --server.port=8501 --server.address=0.0.0.0

# 3. Dashboard (Terminal 3)
streamlit run app/ui/dashboard.py --server.port=8502 --server.address=0.0.0.0
```

### Authentication
```bash
# Test user login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "appuser", "password": "password123"}'

# Test support engineer access
TOKEN="your_jwt_token_here"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/tickets/all
```

### Verify System
```bash
# Check services
ss -tlnp | grep -E "(8000|8501|8502)"

# Test API
curl -s http://localhost:8000/health

# Test authentication
./test_auth.sh

# Test chat
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello", "user_id": "test"}'
```

## 🌐 Access URLs

- **Chat**: http://localhost:8501
- **Dashboard**: http://localhost:8502  
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Prerequisites

1. **Ollama running** with `qwen2.5:14b` model
2. **Python dependencies** installed (including PyJWT)
3. **Required environment variables** set

Check: `curl -s http://localhost:11434/api/tags`

## 👥 User Accounts

| Username | Password | Role |
|----------|----------|------|
| `appuser` | `password123` | User |
| `support-engineer` | `support123` | Support Engineer |

## 📋 Common Commands

```bash
# Check Ollama models
ollama list

# View logs
tail -f server.log
tail -f chat_ui.log  
tail -f dashboard.log

# Kill services
pkill -f "python app/main.py"
pkill -f "streamlit run"
```