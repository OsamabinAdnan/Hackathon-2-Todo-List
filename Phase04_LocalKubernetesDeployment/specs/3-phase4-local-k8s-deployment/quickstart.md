# Quickstart: Phase IV: Local Kubernetes Deployment

## Prerequisites

### System Requirements
- Docker Desktop 4.53+ with Docker AI Agent (Gordon) enabled in Beta features
- Minikube installed and running
- Helm 3.x installed
- kubectl installed
- kubectl-ai plugin installed (optional but recommended)
- kagent installed (optional but recommended)

### Environment Setup
1. Enable Gordon in Docker Desktop:
   - Go to Settings → Experimental Features
   - Toggle on "Enable AI Toolkit"

2. Start Minikube:
   ```bash
   minikube start
   ```

3. Verify tools:
   ```bash
   docker ai --version
   kubectl version
   helm version
   minikube version
   ```

## Deployment Process

### Step 1: Containerize Applications
Use Gordon to generate optimized Dockerfiles:

For Frontend:
```bash
# Navigate to frontend directory
cd frontend/

# Use Gordon to generate Dockerfile
docker ai "generate optimized Dockerfile for Next.js app with multi-stage build"
```

For Backend:
```bash
# Navigate to backend directory
cd backend/

# Use Gordon to optimize existing Dockerfile or generate if needed
docker ai "optimize Dockerfile for FastAPI app with production configuration"
```

### Step 2: Build and Tag Images
```bash
# Build frontend image
docker build -t todo-frontend:latest .

# Build backend image
cd ../backend
docker build -t todo-backend:latest .
```

### Step 3: Load Images into Minikube
```bash
# Load images into minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
```

### Step 4: Create Helm Chart
```bash
# Create Helm chart directory
mkdir -p helm/todo-chatbot

# Use kubectl-ai to generate basic chart structure
kubectl-ai "create helm chart structure for todo-chatbot with frontend and backend deployments"
```

### Step 5: Deploy to Minikube
```bash
# Navigate to Helm chart directory
cd helm/todo-chatbot

# Install the chart
helm install todo-chatbot .
```

### Step 6: Verify Deployment
```bash
# Check pods
kubectl get pods

# Check services
kubectl get svc

# Access the application
minikube service <frontend-service-name> --url
```

## AI-Assisted Operations

### Using kubectl-ai
```bash
# Scale frontend to 2 replicas
kubectl-ai "scale frontend deployment to 2 replicas"

# Check why pods are failing
kubectl-ai "check why pods are failing"

# Scale backend to handle more load
kubectl-ai "scale backend to handle more load"
```

### Using kagent
```bash
# Analyze cluster health
kagent "analyze cluster health"

# Optimize resource allocation
kagent "optimize resource allocation"
```

## Environment Variables Configuration

The application requires the following environment variables:

### Backend (FastAPI)
- `NEON_DB_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT token signing
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `JWT_EXPIRY_DAYS`: Days for JWT expiry (default: 7)

### Frontend (Next.js)
- `NEXT_PUBLIC_API_BASE_URL`: Base URL for backend API
- `NEXT_PUBLIC_CHATKIT_API_KEY`: API key for ChatKit (if using)

These will be configured in the Helm chart's values.yaml file.

## Expected Output

Upon successful deployment:
- Frontend service accessible via NodePort
- Backend API service running internally
- MCP server operational for AI chatbot functionality
- All Phase 3 features preserved (task CRUD via chat interface)
- Multi-user isolation maintained (JWT + user_id filtering)

## Troubleshooting

### Common Issues
1. **Images not found in Minikube**:
   - Ensure images are loaded with `minikube image load`

2. **Services not accessible**:
   - Use `minikube service <service-name> --url` to get the correct URL

3. **Database connection issues**:
   - Verify NEON_DB_URL is correctly configured in secrets

4. **Authentication failures**:
   - Ensure JWT_SECRET matches between frontend and backend

### AI Troubleshooting
```bash
# Use kagent for cluster analysis
kagent "analyze the cluster health"

# Use kubectl-ai for specific issues
kubectl-ai "why is the frontend pod not starting?"
```

## Next Steps

After successful deployment:
1. Verify all Phase 3 functionality works in Kubernetes environment
2. Test AI chatbot functionality
3. Validate user authentication and task management
4. Run scaling demonstrations using kubectl-ai
5. Document the deployment process and create blueprints