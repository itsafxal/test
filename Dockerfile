# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Keeps Python from generating .pyc files and enables stdout/stderr logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer-cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and .env file
COPY main.py .
# Copy .env if present (the * makes it optional so build won't fail without it)
COPY .env* ./

# ── Runtime ───────────────────────────────────────────────────────────────────
# Option 1 — use .env file (copied above)
# Option 2 — pass vars at runtime:
#   docker run -e API_ID=... -e API_HASH=... -e BOT_TOKEN=... my_bot
CMD ["python", "main.py"]
