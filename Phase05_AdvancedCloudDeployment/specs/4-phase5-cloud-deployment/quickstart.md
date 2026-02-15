# Quickstart: Phase 5 Advanced Cloud Deployment

**Branch**: `main` | **Date**: 2026-02-10

## Prerequisites

### Local Development (Minikube)
- Docker Desktop installed and running
- Minikube installed (`minikube version` ≥ v1.32)
- kubectl installed (`kubectl version` ≥ v1.28)
- Helm 3 installed (`helm version` ≥ v3.14)
- Dapr CLI installed (`dapr --version` ≥ v1.13)
- Python 3.13+ with UV package manager
- Node.js 22+ with npm

### Cloud Deployment (Oracle OKE)
- Oracle Cloud account (Always Free tier)
- OCI CLI installed and configured
- kubectl configured for OKE cluster access

## Local Minikube Deployment

### Step 1: Start Minikube
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

### Step 2: Install Dapr
```bash
dapr init -k --wait
dapr status -k  # Verify all Dapr services running
```

### Step 3: Deploy Kafka (Strimzi)
```bash
# Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Deploy Kafka cluster
kubectl apply -f kubernetes/kafka-cluster-minikube.yaml -n kafka
kubectl wait kafka/taskflow-kafka --for=condition=Ready -n kafka --timeout=300s

# Create topics
kubectl apply -f kubernetes/kafka-topics.yaml -n kafka
```

### Step 4: Apply Dapr Components
```bash
kubectl apply -f dapr-components/minikube/
```

### Step 5: Build and Load Docker Images
```bash
# Build images
cd frontend && docker build -t todo-frontend:latest . && cd ..
cd backend && docker build -t todo-backend:latest . && cd ..
cd services/notification-service && docker build -t notification-service:latest . && cd ../..
cd services/recurring-service && docker build -t recurring-service:latest . && cd ../..

# Load into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
minikube image load notification-service:latest
minikube image load recurring-service:latest
```

### Step 6: Create Secrets
```bash
kubectl create secret generic todo-secrets \
  --from-literal=NEON_DB_URL='your-neon-db-url' \
  --from-literal=JWT_SECRET='your-jwt-secret' \
  --from-literal=OPENROUTER_API_KEY='your-api-key'
```

### Step 7: Deploy with Helm
```bash
cd helm/todo-chatbot
helm install todo-chatbot . -f values-minikube.yaml
```

### Step 8: Verify
```bash
# Check all pods are running with Dapr sidecars
kubectl get pods

# Run verification script
bash scripts/verify-phase5.sh
```

### Step 9: Access Application
```bash
minikube service todo-chatbot-frontend --url
```

## Automated Deployment (Single Command)
```bash
bash scripts/deploy-minikube-phase5.sh
```

## Oracle OKE Cloud Deployment

### Step 1: Configure OCI CLI
```bash
oci setup config
kubectl config use-context <oke-context>
```

### Step 2: Deploy
```bash
bash scripts/deploy-oke-phase5.sh
```

## Cleanup
```bash
# Minikube
bash scripts/cleanup-phase5.sh

# Full Minikube reset
minikube delete
```

## Verification Commands

```bash
# Check pod status
kubectl get pods -o wide

# Check Dapr sidecars
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.name}{" "}{end}{"\n"}{end}'

# Check Kafka topics
kubectl get kafkatopics -n kafka

# Test event flow
bash scripts/test-event-flow.sh

# View service logs
kubectl logs -l app=backend -c backend
kubectl logs -l app=notification-service -c notification-service
kubectl logs -l app=recurring-service -c recurring-service
```
