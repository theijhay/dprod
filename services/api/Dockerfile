FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true && \
    poetry install --only=main --no-root --no-interaction --no-ansi


FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
COPY services/shared /app/services/shared
COPY services/api /app/services/api
COPY services/detector /app/services/detector
COPY services/orchestrator /app/services/orchestrator

# Copy alembic files for migrations
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini

ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

RUN useradd -m -u 1000 dprod && \
    chown -R dprod:dprod /app
USER dprod

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "services.api.core.main:app", "--host", "0.0.0.0", "--port", "8000"]
