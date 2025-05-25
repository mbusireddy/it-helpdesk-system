# IT Helpdesk System - Setup Guide

This guide provides step-by-step instructions to set up and run the IT Helpdesk System with local Ollama.

## Prerequisites

1. **Python 3.12+** installed
2. **Ollama** installed and running locally
3. **Poetry** or **pip** for package management
4. **Git** for version control

## Quick Start Commands

### 1. Install Dependencies

```bash
# Navigate to project directory
cd /home/reddy/it-helpdesk-system

# Install dependencies using pip
pip install -r requirements.txt

# OR using Poetry (if preferred)
poetry install
```

### 2. Setup Ollama Model

```bash
# Check if Ollama is running
curl -s http://localhost:11434/api/tags

# Pull required model (if not already available)
ollama pull qwen2.5:14b

# Verify model is available
ollama list
```

### 3. Initialize Database

```bash
# Create necessary directories
mkdir -p data logs chroma_db

# Initialize the knowledge base (optional - runs automatically on first start)
python setup_knowledge_base.py

# Run database migration to add authentication tables (if upgrading)
python migrate_db.py
```

## Starting the Application

### Method 1: Manual Start (Recommended for Development)

#### Terminal 1: Start FastAPI Server
```bash
cd /home/reddy/it-helpdesk-system
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python PYTHONPATH=/home/reddy/it-helpdesk-system nohup python app/main.py > server.log 2>&1 &
```

#### Terminal 2: Start Chat Interface
```bash
cd /home/reddy/it-helpdesk-system
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python streamlit run app/ui/chat_interface.py --server.port=8501 --server.address=0.0.0.0 &
```

#### Terminal 3: Start Dashboard
```bash
cd /home/reddy/it-helpdesk-system
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python streamlit run app/ui/dashboard.py --server.port=8502 --server.address=0.0.0.0 &
```

### Method 2: Start All Services with Script

Create a startup script:

```bash
# Create start_services.sh
cat > start_services.sh << 'EOF'
#!/bin/bash

echo "Starting IT Helpdesk System..."

# Set environment variables
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export PYTHONPATH=/home/reddy/it-helpdesk-system

# Create directories
mkdir -p data logs chroma_db

# Start FastAPI server
cd /home/reddy/it-helpdesk-system
nohup python app/main.py > server.log 2>&1 &
echo "FastAPI server started (PID: $!)" 
echo $! > server.pid

# Wait for server to start
sleep 5

# Start Chat Interface
nohup streamlit run app/ui/chat_interface.py --server.port=8501 --server.address=0.0.0.0 > chat_ui.log 2>&1 &
echo "Chat Interface started (PID: $!)"
echo $! > chat_ui.pid

# Start Dashboard
nohup streamlit run app/ui/dashboard.py --server.port=8502 --server.address=0.0.0.0 > dashboard.log 2>&1 &
echo "Dashboard started (PID: $!)"
echo $! > dashboard.pid

echo ""
echo "All services started successfully!"
echo "Access the application at:"
echo "- API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- Chat Interface: http://localhost:8501"
echo "- Dashboard: http://localhost:8502"
EOF

# Make executable and run
chmod +x start_services.sh
./start_services.sh
```

## Verification Commands

### 1. Check Service Status

```bash
# Check if all ports are listening
ss -tlnp | grep -E "(8000|8501|8502)"

# Check running processes
ps aux | grep -E "(python|streamlit)" | grep -v grep
```

### 2. Test API Endpoints

```bash
# Health check
curl -s http://localhost:8000/health

# Test chat endpoint
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, I need help with my computer", "user_id": "test_user"}'

# Test analytics endpoint
curl -s http://localhost:8000/analytics/dashboard

# Test ticket status (use actual ticket ID)
curl -s -X POST http://localhost:8000/ticket/status \
  -H "Content-Type: application/json" \
  -d '{"ticket_id": 1}'

# Get user tickets
curl -s http://localhost:8000/tickets/user/test_user
```

### 3. Test Streamlit Interfaces

```bash
# Test chat interface
curl -s http://localhost:8501 | grep -o "<title>.*</title>"

# Test dashboard
curl -s http://localhost:8502 | grep -o "<title>.*</title>"
```

### 4. Test Ollama Integration

```bash
# Check Ollama is accessible
curl -s http://localhost:11434/api/tags | jq '.models[].name'

# Test direct Ollama query
curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:14b",
    "prompt": "Hello, can you help me?",
    "stream": false
  }'
```

## Stopping Services

### Stop Individual Services

```bash
# Stop FastAPI server
kill $(cat server.pid) 2>/dev/null || pkill -f "python app/main.py"

# Stop Chat Interface  
kill $(cat chat_ui.pid) 2>/dev/null || pkill -f "streamlit run app/ui/chat_interface.py"

# Stop Dashboard
kill $(cat dashboard.pid) 2>/dev/null || pkill -f "streamlit run app/ui/dashboard.py"
```

### Stop All Services Script

```bash
# Create stop_services.sh
cat > stop_services.sh << 'EOF'
#!/bin/bash

echo "Stopping IT Helpdesk System..."

# Stop services using PID files
for service in server chat_ui dashboard; do
    if [ -f "${service}.pid" ]; then
        pid=$(cat "${service}.pid")
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            echo "Stopped ${service} (PID: $pid)"
        fi
        rm -f "${service}.pid"
    fi
done

# Fallback: kill by process name
pkill -f "python app/main.py" 2>/dev/null
pkill -f "streamlit run app/ui" 2>/dev/null

echo "All services stopped."
EOF

chmod +x stop_services.sh
./stop_services.sh
```

## Troubleshooting

### Common Issues

1. **Port already in use**
```bash
# Check what's using the port
ss -tlnp | grep 8000
# Kill the process if needed
sudo kill -9 $(ss -tlnp | grep 8000 | awk '{print $7}' | cut -d',' -f2 | cut -d'=' -f2)
```

2. **Module import errors**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/home/reddy/it-helpdesk-system
```

3. **Protobuf errors**
```bash
# Set environment variable
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
```

4. **Database issues**
```bash
# Reset database
rm -f helpdesk.db
rm -rf chroma_db
mkdir -p chroma_db
python setup_knowledge_base.py
```

### Log Files

Check application logs for debugging:

```bash
# API server logs
tail -f server.log

# Chat interface logs  
tail -f chat_ui.log

# Dashboard logs
tail -f dashboard.log

# Application logs
tail -f logs/helpdesk.log
```

## Configuration

### Environment Variables

Create `.env` file (optional):
```bash
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./helpdesk.db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b
CHROMA_PERSIST_DIRECTORY=./chroma_db
LOG_LEVEL=INFO
EOF
```

### Default Configuration

The application uses these default settings (from `app/utils/config.py`):
- Database: SQLite (`./helpdesk.db`)
- Ollama URL: `http://localhost:11434`
- Model: `qwen2.5:14b`
- ChromaDB: `./chroma_db`

## Testing the Complete Workflow

```bash
# 1. Start all services
./start_services.sh

# 2. Wait for services to start
sleep 10

# 3. Run complete test
echo "=== Testing IT Helpdesk System ==="

echo "1. Health Check:"
curl -s http://localhost:8000/health | jq

echo -e "\n2. Chat Test:"
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "My printer is not working", "user_id": "test_user"}' | jq

echo -e "\n3. Analytics Test:"
curl -s http://localhost:8000/analytics/dashboard | jq

echo -e "\n4. UI Tests:"
echo "Chat Interface: $(curl -s http://localhost:8501 | grep -o '<title>[^<]*' | cut -d'>' -f2)"
echo "Dashboard: $(curl -s http://localhost:8502 | grep -o '<title>[^<]*' | cut -d'>' -f2)"

echo -e "\n=== All tests completed ==="
```

## Production Deployment Notes

For production deployment:

1. Use PostgreSQL instead of SQLite
2. Set up Redis for session management
3. Use a process manager (PM2, supervisord)
4. Configure reverse proxy (nginx)
5. Set up SSL certificates
6. Implement authentication
7. Configure monitoring and logging

## Access URLs

The application is using your local Ollama instance with the `qwen2.5:14b` model for AI responses.

## Authentication System

The system includes a complete user authentication system with role-based access control:

### Default User Accounts

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `appuser` | `password123` | User | Chat access, view own tickets |
| `support-engineer` | `support123` | Support Engineer | Full access, ticket management |

### Testing Authentication

```bash
# Test user login
curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "appuser", "password": "password123"}'

# Test support engineer login  
curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "support-engineer", "password": "support123"}'

# Run comprehensive authentication tests
./test_auth.sh
```

### Role-Based Features

**Regular Users:**
- Login and logout
- Chat with AI agents
- View their own tickets
- Check ticket status

**Support Engineers:**
- All user features plus:
- View all tickets in the system
- Update ticket status (open → in_progress → resolved)
- Assign tickets to themselves or other engineers
- Access administrative endpoints

## Access URLs

Once started, access the application at:
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Chat Interface**: http://localhost:8501
- **Analytics Dashboard**: http://localhost:8502