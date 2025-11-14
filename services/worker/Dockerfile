FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create worker directory
WORKDIR /app

# Copy worker code
COPY services/worker /app/worker
COPY services/shared /app/shared

# Install Python dependencies
RUN pip install --no-cache-dir -r worker/requirements.txt

# Create log directory
RUN mkdir -p /var/log && chmod 777 /var/log

# Run as non-root user
RUN useradd -m -u 1000 worker && \
    chown -R worker:worker /app /var/log
USER worker

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Start worker
CMD ["python", "-m", "worker.core.main"]
