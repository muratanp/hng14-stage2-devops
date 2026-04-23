# syntax=docker/dockerfile:1
# ── Stage 1: Install dependencies ─────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --user --upgrade pip==23.3.1 \
    && pip install --no-cache-dir --user -r requirements.txt


# ── Stage 2: Lean production image ────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN useradd --no-create-home --shell /bin/false --uid 1001 appuser

# Copy only the installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source (no .env files — those are injected at runtime)
COPY main.py .

RUN chown -R appuser:appuser /app /home/appuser/.local

USER appuser

ENV PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
