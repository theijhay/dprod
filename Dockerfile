# Multi-stage build for dprod API
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
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv

ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

RUN useradd -m -u 1000 dprod && \
    chown -R dprod:dprod /app

COPY --chown=dprod:dprod services /app/services
COPY --chown=dprod:dprod alembic /app/alembic
COPY --chown=dprod:dprod alembic.ini /app/alembic.ini

USER dprod

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f -H "Host: localhost" http://localhost:8000/ || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "services.api.core.main:app", "--host", "0.0.0.0", "--port", "8000"]
