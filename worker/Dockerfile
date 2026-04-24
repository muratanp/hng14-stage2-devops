# Stage 1: Install dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --user --upgrade pip==23.3.1 \
    && pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Lean production image
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --no-create-home --shell /bin/false --uid 1001 appuser

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source
COPY worker.py .

RUN chown -R appuser:appuser /app /home/appuser/.local

USER appuser

ENV PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Health check: verify connectivity to Redis
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import redis, os; r=redis.Redis(host=os.getenv('REDIS_HOST','redis'), port=int(os.getenv('REDIS_PORT','6379')), password=os.getenv('REDIS_PASSWORD') or None); r.ping()" || exit 1

CMD ["python", "worker.py"]
