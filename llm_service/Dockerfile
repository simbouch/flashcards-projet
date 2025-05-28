 # llm_service/Dockerfile

 FROM python:3.10-slim

WORKDIR /app

# 1) Install system deps + CA certs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2) Copy & install Python deps (make sure nltk is listed)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Pre-download the NLTK tokenizers
RUN python -m nltk.downloader punkt_tab || python -m nltk.downloader punkt

# Copy the rest of your app
COPY src/ ./src/

# …the rest remains the same…
RUN mkdir -p logs
RUN useradd -m llmuser && chown -R llmuser:llmuser /app
USER llmuser

ENV PYTHONPATH=/app
ENV MODEL_NAME="bigscience/bloom-560m"
EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
