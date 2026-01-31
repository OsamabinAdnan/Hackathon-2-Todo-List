# ================================
# FastAPI Backend (Production)
# ================================

# Use slim Python base image to reduce final image size
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs are flushed immediately (important for Docker/K8s)
ENV PYTHONUNBUFFERED=1

# Install system-level dependencies required by some Python packages
# --no-install-recommends avoids unnecessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
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

# Expose FastAPI port
EXPOSE 8000

# IMPORTANT:
# - Do NOT COPY .env into the image
# - Recommended approaches:
#   1) Local Docker:
#        docker run --env-file .env backend:latest
#   2) Kubernetes:
#        Use Secrets / ConfigMaps (env or envFrom)
#   3) Helm:
#        Define env values in values.yaml
#
# This keeps images secure, reusable, and environment-agnostic
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
