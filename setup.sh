#!/bin/bash

echo "Setting up IT Helpdesk System..."

# Create directories
mkdir -p data logs chroma_db

# Copy environment file
cp .env.example .env

echo "Please edit .env file with your configuration"

# Pull Ollama model
echo "Pulling Ollama model..."
docker-compose up -d ollama
sleep 10
docker-compose exec ollama ollama pull qwen2:14b

# Start all services
echo "Starting all services..."
docker-compose up -d

echo "Setup complete!"
echo "Access the application at:"
echo "- API: http://localhost:8000"
echo "- Chat UI: http://localhost:8501"
echo "- Dashboard: http://localhost:8502"
echo "- Ollama: http://localhost:11434"
