# ==============================================================================
# FraudLens / AI-DIDSS: Production Multi-Modal Backend Container
# Target Deployment: Render / Fly.io / Google Cloud Run / AWS ECS / Self-Hosted
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    TORCH_HOME=/tmp/.cache/torch \
    EASYOCR_MODULE_PATH=/tmp/.EasyOCR

WORKDIR /app

# Install essential OS-level runtime libraries for OpenCV headless & networking
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy production requirements first for efficient layer caching
COPY requirements.txt .

# Install production Python dependencies (FastAPI + Modules 1-7 Deep Learning Stack)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy complete application modules and source code
COPY . .

# Expose backend API port
EXPOSE 8000

# Container Healthcheck against Module 8 health route
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

# Start production FastAPI ASGI server
CMD ["sh", "-c", "uvicorn module8_backend_api.src.main:app --host 0.0.0.0 --port ${PORT}"]
