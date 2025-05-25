#!/bin/bash

# IT Helpdesk System Startup Script - With Login-Enabled Interfaces
echo "Starting IT Helpdesk System with Login-Enabled Interfaces..."

# Set environment variable for protobuf compatibility
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Kill existing processes
echo "Stopping any existing services..."
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "streamlit run" 2>/dev/null
sleep 2

# Start FastAPI server
echo "Starting FastAPI server..."
cd /home/reddy/it-helpdesk-system
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
echo $! > app.pid

# Wait for API to start
sleep 3

# Start Login-Enabled Chat Interface
echo "Starting Login-Enabled Chat Interface..."
nohup streamlit run app/ui/login_chat_interface.py --server.port 8501 --server.address 0.0.0.0 > chat_ui.log 2>&1 &
echo $! > chat_ui.pid

# Start Login-Enabled Dashboard
echo "Starting Login-Enabled Dashboard..."
nohup streamlit run app/ui/login_dashboard.py --server.port 8502 --server.address 0.0.0.0 > dashboard.log 2>&1 &
echo $! > dashboard.pid

# Wait for services to fully start
sleep 5

echo ""
echo "All services started successfully!"
echo ""
echo "🔐 LOGIN-ENABLED WEB INTERFACES:"
echo "================================="
echo "• Chat Interface:  http://localhost:8501"
echo "• Dashboard:       http://localhost:8502"
echo "• API:            http://localhost:8000"
echo "• API Docs:       http://localhost:8000/docs"
echo ""
echo "👥 LOGIN ACCOUNTS:"
echo "=================="
echo "• Regular User:      appuser / password123"
echo "• Support Engineer:  support-engineer / support123"
echo ""
echo "📋 FEATURES BY ROLE:"
echo "===================="
echo "Regular User:"
echo "  ✅ Chat with AI agents"
echo "  ✅ View analytics dashboard"
echo "  ✅ Track own tickets"
echo ""
echo "Support Engineer:"
echo "  ✅ All regular user features"
echo "  ✅ View ALL tickets"
echo "  ✅ Update ticket status"
echo "  ✅ Assign tickets"
echo "  ✅ Admin analytics"
echo ""
echo "🚀 Ready to use! Login required for web interfaces."
echo "   API authentication uses JWT tokens from /login endpoint."