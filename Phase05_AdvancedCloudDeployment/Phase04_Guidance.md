# Phase 4: Local Kubernetes Deployment - Complete Step-by-Step Guide

This document provides a comprehensive step-by-step guide for deploying the Todo AI Chatbot application to a local Kubernetes cluster using Minikube.

## Prerequisites
- Docker Desktop with Gordon AI enabled
- Minikube installed
- Helm 3.x installed
- kubectl installed
- kubectl-ai plugin installed
- kagent installed

## AI-Assisted DevOps Tools Overview
This deployment leverages AI-assisted DevOps operations using specialized tools:
- **Gordon**: AI-powered Docker assistant for containerization
- **kubectl-ai**: AI-powered kubectl commands for Kubernetes operations
- **kagent**: AI-powered Kubernetes operations agent
- **Docker Desktop**: Containerization platform with AI features

## Step 1: Start Minikube with Docker Driver
```bash
minikube start --driver=docker
```
**Functionality**: Initializes a local Kubernetes cluster using Docker as the container runtime. This creates a single-node Kubernetes cluster inside a Docker container.

## Important: After PC Shutdown/Restart - Complete Workflow

When you shut down your PC and restart later, here's the complete workflow to get your application running again:

### What Happens When You Shut Down:
- **Docker images persist**: Your built images (todo-backend:latest, todo-frontend:latest) remain in Docker Desktop
- **Minikube cluster stops**: The Kubernetes cluster inside the Docker container stops
- **Kubernetes resources may be lost**: Deployments, services, and pods may not persist
- **Cluster data is fresh**: When restarted, you get a fresh Kubernetes cluster environment

### What Actually Happens When You Run `minikube start --driver=docker`:
- **Creates new cluster**: Starts a fresh Kubernetes cluster inside a Docker container
- **Does NOT pull images again**: Uses existing images in Docker but they're not automatically available to the cluster
- **Your images stay put**: Built images remain in Docker Desktop but need to be loaded into Minikube
- **No automatic deployment**: Previous Helm releases and Kubernetes resources need to be recreated

### Complete Restart Workflow:
```bash
# 1. Start Minikube
minikube start --driver=docker

# 2. Load your existing images into the cluster
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# 3. Check if previous deployment exists
kubectl get pods
helm list

# 4. If no deployment exists, reinstall
helm install todo-app ./helm/todo-chatbot -f values.yaml -f values-secret.yaml

# 5. Verify everything is running
kubectl get pods
kubectl get services

# 6. Access your application
kubectl port-forward svc/todo-app-todo-chatbot-backend 8000:8000
kubectl port-forward svc/todo-app-todo-chatbot-frontend 3000:3000
```

**Key Point**: Even though your Docker images exist in Docker Desktop, they must be explicitly loaded into Minikube using `minikube image load` command after each restart.

## Step 2: Build Docker Images
Build the backend Docker image:
```bash
cd backend
docker build -t todo-backend:latest .
```

Build the frontend Docker image:
```bash
cd ../frontend
docker build -t todo-frontend:latest .
```

Docker Desktop CLI Commands for Container Management:
```bash
# List all Docker images
docker images

# Check running containers
docker ps

# Check all containers (including stopped)
docker ps -a

# Remove unused images, containers, and networks
docker system prune

# Remove specific image
docker rmi todo-backend:latest

# Check Docker disk usage
docker system df

# View container logs
docker logs <container-id>

# Execute commands in running container
docker exec -it <container-id> /bin/bash
```

Alternative using Gordon AI (Docker Desktop):
```bash
# Gordon can help optimize Dockerfiles and build processes
gordon create dockerfile --app-type=fastapi  # For backend
gordon create dockerfile --app-type=nextjs   # For frontend
gordon optimize image --name todo-backend:latest
gordon analyze security --image todo-frontend:latest
gordon suggest improvements --dockerfile Dockerfile
```
**Functionality**: Creates container images for both frontend and backend applications that will run in Kubernetes pods. Docker Desktop CLI provides comprehensive container management capabilities, while Gordon AI can assist with Dockerfile optimization and best practices.

## Step 3: Load Images into Minikube
```bash
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```
**Functionality**: Loads the Docker images into the Minikube cluster so they can be used by Kubernetes deployments.

## Step 4: Create Helm Chart Structure
Create the Helm chart directory structure with proper templates:
- `Chart.yaml` - Chart metadata
- `values.yaml` - Configuration values
- `templates/` - Kubernetes resource templates

**Functionality**: Helm provides package management for Kubernetes, allowing for configurable and repeatable deployments.

## Step 5: Configure Helm Chart with Real Secrets
Create `values-secret.yaml` containing your real environment variables:
```yaml
secrets:
  JWT_SECRET: "your-real-jwt-secret"
  NEON_DB_URL: "your-real-neon-db-url"
  OPENROUTER_API_KEY: "your-real-openrouter-key"
  QWEN_API_KEY: "your-real-qwen-key"
  COHERE_API_KEY: "your-real-cohere-key"
```
**Functionality**: Separates sensitive values from public configuration, following security best practices.

## Step 6: Create Secret Templates
Create `templates/secret.yaml` to properly handle sensitive data:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-chatbot.fullname" . }}-db-secret
type: Opaque
stringData:
  NEON_DB_URL: {{ required "NEON_DB_URL is required" .Values.secrets.NEON_DB_URL }}
```
**Functionality**: Uses `stringData` for cleaner secret handling and `required` for critical values.

## Step 7: Configure Services and Deployments
Create proper templates for:
- `backend-deployment.yaml` - Backend application deployment
- `frontend-deployment.yaml` - Frontend application deployment
- `backend-service.yaml` - Backend service (NodePort)
- `frontend-service.yaml` - Frontend service (NodePort)

**Functionality**: Defines how applications run and how they're exposed within and outside the cluster.

## Step 8: Install Helm Chart
```bash
helm install todo-app ./helm/todo-chatbot -f values.yaml -f values-secret.yaml
```
**Functionality**: Deploys the entire application stack with all configurations and secrets.

## Step 9: Verify Pod Status
```bash
kubectl get pods
```

Alternative using kubectl-ai:
```bash
kubectl-ai "show me all pods"
kubectl-ai "check pod status"
kubectl-ai "are all pods running?"
```

Alternative using kagent:
```bash
kagent "analyze pod health"
kagent "show pod status with details"
```
**Functionality**: Checks that all application pods are running successfully (status: Running, ready: 1/1). AI-assisted tools provide natural language interaction with Kubernetes.

## Step 10: Check Services
```bash
kubectl get services
```

Alternative using kubectl-ai:
```bash
kubectl-ai "show me all services"
kubectl-ai "describe the backend service"
kubectl-ai "check if services are running properly"
```

Alternative using kagent:
```bash
kagent "analyze service status"
kagent "show service connectivity"
```
**Functionality**: Verifies that services are created and exposing the correct ports. kubectl-ai and kagent provide AI-powered alternatives for Kubernetes operations.

Expected output:
- `todo-app-todo-chatbot-backend` - NodePort service on port 8000 (e.g., 31415)
- `todo-app-todo-chatbot-frontend` - NodePort service on port 3000 (e.g., 32560)

## Step 11: Get Minikube IP
```bash
minikube ip
```
**Functionality**: Gets the IP address of the Minikube cluster, needed to access NodePort services from the browser.

## Step 12: Establish Port Forwarding for Development
```bash
kubectl port-forward svc/todo-app-todo-chatbot-backend 8000:8000
kubectl port-forward svc/todo-app-todo-chatbot-frontend 3000:3000
```
**Functionality**: Creates direct connections from localhost to services in the cluster, bypassing NodePort limitations and IP changes.

## Alternative: Access via Minikube Service URLs
If you don't want to use port forwarding, you can access services directly using Minikube service URLs:
```bash
minikube service todo-app-todo-chatbot-backend --url
minikube service todo-app-todo-chatbot-frontend --url
```

**Functionality**: This command provides external access URLs for the services, which can be used directly in the browser. The URLs will be something like:
- Backend: `http://192.168.49.2:31415`
- Frontend: `http://192.168.49.2:32560`

**Important**: When using this approach, you'll need to update your frontend configuration to use the actual NodePort URL for API calls instead of localhost. This is because the frontend running in browser needs to know the actual backend service address.

## Step 13: Access the Application
### With Port Forwarding (Recommended for Development):
- **Frontend**: `http://localhost:3000` - Main application UI
- **Backend**: `http://localhost:8000` - API endpoints

### With Minikube Service URLs (For External Access):
- **Frontend**: `http://<minikube-ip>:<frontend-nodeport>` (e.g., `http://192.168.49.2:32560`)
- **Backend**: `http://<minikube-ip>:<backend-nodeport>` (e.g., `http://192.168.49.2:31415`)

**Functionality**: Both approaches allow browser-based access to the application. Port forwarding provides stable localhost addresses, while service URLs provide direct access but may change IP addresses and ports between sessions.

## Step 14: Test Application Functionality
- Access the frontend at `http://localhost:3000`
- Verify login functionality works
- Test chatbot functionality
- Verify task management operations
- Confirm AI agent integration works

**Functionality**: Validates that all application features work correctly in the Kubernetes environment.

## Key Networking Concepts

### NodePort Services
- Backend: Available at `http://<minikube-ip>:<nodeport>` (e.g., `http://192.168.49.2:31415`)
- Frontend: Available at `http://<minikube-ip>:<nodeport>` (e.g., `http://192.168.49.2:32560`)
- **Issue**: IP addresses and ports can change between sessions

### Port Forwarding (Recommended for Development)
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- **Advantage**: Stable addresses, no IP changes to track

## Troubleshooting Common Issues

### Connection Refused Error
**Cause**: Browser trying to reach service on wrong address
**Solution**: Use port-forwarding or correct NodePort address

**AI-Assisted Troubleshooting**:
```bash
kubectl-ai "why is my service showing connection refused"
kagent "analyze connection issues"
```

### Empty Response Error
**Cause**: Service not responding properly
**Solution**: Check pod logs with `kubectl logs <pod-name>`

**AI-Assisted Troubleshooting**:
```bash
kubectl-ai "show logs for pod <pod-name>"
kubectl-ai "what's wrong with my service not responding"
kagent "debug service connectivity"
```

### Pod CrashLoopBackOff
**Cause**: Application failing to start (often database connection)
**Solution**: Verify secrets are correctly configured

**AI-Assisted Troubleshooting**:
```bash
kubectl-ai "analyze why pod is in CrashLoopBackOff"
kubectl-ai "show detailed pod status for <pod-name>"
kagent "troubleshoot pod startup issues"
```

### General AI-Assisted Diagnostics
```bash
kubectl-ai "perform cluster health check"
kubectl-ai "show resource usage"
kagent "analyze cluster performance"
kagent "generate deployment report"
```

## Security Best Practices Implemented
- Secrets stored separately from public configuration
- Real API keys never committed to Git
- Proper environment variable mapping
- Database credentials properly secured

## AI-Assisted Kubernetes Operations

### Using kubectl-ai (Natural Language Kubernetes)
```bash
kubectl-ai "show me all deployments"
kubectl-ai "scale backend deployment to 2 replicas"
kubectl-ai "restart the frontend deployment"
kubectl-ai "show me resource usage by pods"
kubectl-ai "check if ingress controller is running"
```

### Using kagent (AI-Powered Kubernetes Agent)
```bash
kagent "analyze cluster health"
kagent "monitor deployment status"
kagent "generate cluster report"
kagent "troubleshoot network issues"
kagent "optimize resource allocation"
```

### Using Gordon (AI-Powered Docker Assistant)
```bash
# Gordon can help with Docker optimizations
gordon optimize image --name todo-backend:latest
gordon analyze security --image todo-frontend:latest
gordon suggest improvements --dockerfile Dockerfile
```

## Docker Desktop Container Management

### To Stop Individual Docker Containers:
```bash
# Stop a specific container
docker stop <container-id>

# Stop all running containers
docker stop $(docker ps -q)

# Stop containers by name pattern
docker stop $(docker ps -q --filter "name=todo")

# Remove containers
docker rm <container-id>
docker rm $(docker ps -aq)  # Remove all containers
```

### To Stop the Minikube Cluster (Kubernetes containers):
```bash
# Stop the Minikube cluster (stops the Docker container running Kubernetes)
minikube stop

# Delete the entire Minikube cluster (more thorough)
minikube delete
```

### To Stop Docker Desktop Application:
```bash
# On Windows - End the process
taskkill /IM Docker Desktop.exe /F

# Or gracefully close it from the system tray:
# Click Docker Desktop icon in system tray → Quit Docker Desktop
```

### To Clean Up Docker Resources:
```bash
# Remove all unused images, containers, and networks
docker system prune -a

# Remove specific image
docker rmi todo-backend:latest
docker rmi todo-frontend:latest

# Check disk usage
docker system df
```

## Complete Shutdown Before PC Shutdown:
```bash
# 1. Stop port forwarding (Ctrl+C in terminal where it's running)
# 2. Stop your application deployments
kubectl delete deployment todo-app-todo-chatbot-backend
kubectl delete deployment todo-app-todo-chatbot-frontend

# 3. Or use Helm to uninstall
helm uninstall todo-app

# 4. Stop Minikube
minikube stop

# 5. Optionally quit Docker Desktop
# Windows: Right-click Docker Desktop icon in system tray → Quit Docker Desktop
```

## Cleanup Commands
```bash
# Stop port forwarding (Ctrl+C in terminal)
# Uninstall Helm release
helm uninstall todo-app

# Alternative using kubectl-ai
kubectl-ai "delete deployment todo-app"
kubectl-ai "clean up all resources"

# Alternative using kagent
kagent "cleanup all deployment resources"

# Stop Minikube
minikube stop
# Delete Minikube cluster
minikube delete
```

This complete guide provides a robust, secure, and development-friendly approach to running your Todo AI Chatbot application on a local Kubernetes cluster using Minikube. The port-forwarding approach ensures consistent access to services regardless of changing NodePort assignments. AI-assisted tools like kubectl-ai, kagent, Gordon, and Docker Desktop with AI features enhance the development and operations experience.