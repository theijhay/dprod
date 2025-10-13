FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./
COPY packages/shared packages/shared
COPY packages/api packages/api

# Install dependencies
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "packages.api.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
