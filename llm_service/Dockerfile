# llm_service/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create log directory
RUN mkdir -p logs

# Create a non-root user and switch to it
RUN useradd -m llmuser && \
    chown -R llmuser:llmuser /app
USER llmuser

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_NAME="bigscience/bloom-560m"

# Expose the port
EXPOSE 8001

# Command to run when container starts
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
