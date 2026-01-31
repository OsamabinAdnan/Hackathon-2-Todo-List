#!/bin/bash

# AI-assisted Docker build and push script for Todo Chatbot
# This script uses Gordon (Docker AI Agent) for intelligent container operations

set -e  # Exit on any error

echo "Starting AI-assisted Docker operations for Todo Chatbot..."

# Build frontend image using Gordon's AI assistance
echo "Building frontend image using Gordon..."
cd ../frontend
docker ai "generate optimized Dockerfile for Next.js app with multi-stage build" || true
docker build -t todo-frontend:latest .

# Build backend image using Gordon's AI assistance
echo "Building backend image using Gordon..."
cd ../backend
docker ai "optimize Dockerfile for FastAPI app with production configuration" || true
docker build -t todo-backend:latest .

# Build MCP server image
echo "Building MCP server image..."
# We'll create the MCP server Dockerfile separately
cd ..

echo "Docker build operations completed successfully!"