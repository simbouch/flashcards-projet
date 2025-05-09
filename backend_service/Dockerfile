# backend_service/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p logs uploads data

# Create a non-root user and switch to it
RUN useradd -m backenduser && \
    chown -R backenduser:backenduser /app
USER backenduser

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///./data/flashcards.db

# Expose the port
EXPOSE 8002

# Command to run when container starts
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
