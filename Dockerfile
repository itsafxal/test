# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Keeps Python from generating .pyc files and enables stdout/stderr logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer-cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY main.py .

# ── Runtime ───────────────────────────────────────────────────────────────────
# Pass credentials as environment variables at runtime:
#   docker run -e API_ID=... -e API_HASH=... -e BOT_TOKEN=... my_bot
CMD ["python", "main.py"]
