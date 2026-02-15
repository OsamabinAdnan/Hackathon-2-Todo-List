# ================================
# FastAPI Backend (Production)
# Phase 5: Dapr-compatible Configuration
# ================================

# Use slim Python base image to reduce final image size
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs are flushed immediately (important for Docker/K8s)
ENV PYTHONUNBUFFERED=1

# Set Python path for imports
ENV PYTHONPATH=/app

# Install system-level dependencies required by some Python packages
# curl is needed for health checks
# --no-install-recommends avoids unnecessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies without cache
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code
# NOTE: .env files are intentionally NOT copied into the image
# Environment variables must be injected at runtime
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Health check for Kubernetes readiness/liveness probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# IMPORTANT:
# - Do NOT COPY .env into the image
# - Secrets are injected at runtime via Kubernetes Secrets (Helm deployment)
# - ConfigMaps used for non-sensitive configuration
# - This keeps images secure, reusable, and environment-agnostic
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
