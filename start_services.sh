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