FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r helpdesk && useradd -r -g helpdesk helpdesk

# Copy requirements and install Python dependencies
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper permissions
RUN mkdir -p logs data chroma_db \
    && chown -R helpdesk:helpdesk /app

# Copy application code
COPY --chown=helpdesk:helpdesk . .

# Switch to non-root user
USER helpdesk

# Expose ports
EXPOSE 8000 8501 8502

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]