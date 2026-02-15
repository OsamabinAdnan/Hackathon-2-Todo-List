#!/bin/bash
# Setup Dapr on Kubernetes
# Phase 5: Distributed Application Runtime
# Compatible with Minikube and production Kubernetes clusters

set -e

# Configuration
DAPR_VERSION="${DAPR_VERSION:-1.14.4}"
NAMESPACE="${DAPR_NAMESPACE:-dapr-system}"
CLUSTER_TYPE="${CLUSTER_TYPE:-minikube}"  # minikube or production
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "  Dapr Setup - Phase 5"
echo "========================================"
echo "Dapr Version: $DAPR_VERSION"
echo "Namespace: $NAMESPACE"
echo "Cluster Type: $CLUSTER_TYPE"
echo "========================================"

# Check if Dapr CLI is installed
if ! command -v dapr &> /dev/null; then
    echo "ERROR: Dapr CLI is not installed. Please install it first:"
    echo "  Windows: winget install Dapr.CLI"
    echo "  macOS: brew install dapr/tap/dapr-cli"
    echo "  Linux: wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash"
    exit 1
fi

# Initialize Dapr on Kubernetes
echo "[1/4] Initializing Dapr on Kubernetes..."
dapr init -k --runtime-version "$DAPR_VERSION" --wait

# Verify Dapr installation
echo "[2/4] Verifying Dapr installation..."
dapr status -k

# Apply Dapr components based on environment
echo "[3/4] Applying Dapr components..."
if [ "$CLUSTER_TYPE" = "production" ]; then
    echo "Applying production Dapr components..."
    kubectl apply -f "$PROJECT_ROOT/dapr-components/production/"
else
    echo "Applying Minikube Dapr components..."
    kubectl apply -f "$PROJECT_ROOT/dapr-components/minikube/"
fi

# Verify components
echo "[4/4] Verifying Dapr components..."
sleep 5
kubectl get components.dapr.io

echo ""
echo "========================================"
echo "  Dapr Setup Complete!"
echo "========================================"
echo ""
echo "Dapr Dashboard (if enabled):"
echo "  dapr dashboard -k"
echo ""
echo "Verify with:"
echo "  dapr status -k"
echo "  kubectl get components.dapr.io"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "Components installed:"
echo "  - kafka-pubsub (Pub/Sub)"
echo "  - statestore (State Management)"
echo "  - kubernetes-secrets (Secrets)"
echo "  - cron-binding (Bindings)"
echo ""
