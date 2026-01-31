#!/bin/bash

# AI-assisted Kubernetes deployment script for Todo Chatbot
# This script uses kubectl-ai and kagent for intelligent Kubernetes operations

set -e  # Exit on any error

echo "Starting AI-assisted Kubernetes deployment for Todo Chatbot..."

# Load images into minikube
echo "Loading images into minikube..."
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Install Helm chart
echo "Installing Helm chart..."
cd ../helm/todo-chatbot
helm install todo-chatbot . --wait

echo "Verifying deployment..."
kubectl get pods
kubectl get svc

echo "Kubernetes deployment completed successfully!"