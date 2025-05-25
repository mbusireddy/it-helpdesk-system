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