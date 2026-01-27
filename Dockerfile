# PDF Translator Dockerfile
# Multi-stage build for optimized image size

FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .
COPY requirements-gpu.txt .

# Install Python dependencies (CPU version by default)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p models synthetic_data output translations

# Set Python path to include src directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Default command
CMD ["python", "src/translate_pdf.py", "--help"]

# GPU-enabled variant (use with docker-compose or build with --build-arg)
FROM base as gpu
RUN pip install --no-cache-dir -r requirements-gpu.txt
