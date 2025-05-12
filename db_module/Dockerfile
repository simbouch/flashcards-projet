# db_module/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy module files
COPY . .

# Create log directory
RUN mkdir -p logs

# Create a non-root user and switch to it
RUN useradd -m dbuser && \
    chown -R dbuser:dbuser /app
USER dbuser

# Set environment variables
ENV PYTHONPATH=/app

# Command to run when container starts
CMD ["python", "-c", "from database import init_db; init_db()"]
