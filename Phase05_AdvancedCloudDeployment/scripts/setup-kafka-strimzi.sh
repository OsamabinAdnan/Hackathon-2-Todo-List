#!/bin/bash
# Setup Kafka using Strimzi Operator
# Phase 5: Event-driven architecture foundation
# Compatible with Minikube and production Kubernetes clusters

set -e

# Configuration
STRIMZI_VERSION="${STRIMZI_VERSION:-0.49.0}"
NAMESPACE="${KAFKA_NAMESPACE:-kafka}"
CLUSTER_TYPE="${CLUSTER_TYPE:-minikube}"  # minikube or production
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "  Strimzi Kafka Setup - Phase 5"
echo "========================================"
echo "Strimzi Version: $STRIMZI_VERSION"
echo "Namespace: $NAMESPACE"
echo "Cluster Type: $CLUSTER_TYPE"
echo "========================================"

# Create kafka namespace
echo "[1/5] Creating Kafka namespace..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Install Strimzi CRDs (v1 API)
echo "[2/5] Installing Strimzi CRDs..."
kubectl apply -f "https://github.com/strimzi/strimzi-kafka-operator/releases/download/$STRIMZI_VERSION/strimzi-crds-$STRIMZI_VERSION.yaml"

# Install Strimzi operator
echo "[3/5] Installing Strimzi Cluster Operator..."
kubectl apply -f "https://strimzi.io/install/latest?namespace=$NAMESPACE" -n "$NAMESPACE"

# Wait for operator to be ready
echo "[4/5] Waiting for Strimzi operator to be ready..."
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n "$NAMESPACE" --timeout=300s

# Deploy Kafka cluster based on environment
echo "[5/5] Deploying Kafka cluster..."
if [ "$CLUSTER_TYPE" = "production" ]; then
    echo "Deploying production Kafka cluster (3 replicas)..."
    kubectl apply -f "$PROJECT_ROOT/kubernetes/kafka-cluster-production.yaml" -n "$NAMESPACE"
else
    echo "Deploying Minikube Kafka cluster (1 replica, ephemeral)..."
    kubectl apply -f "$PROJECT_ROOT/kubernetes/kafka-cluster-minikube.yaml" -n "$NAMESPACE"
fi

# Wait for Kafka cluster to be ready
echo "Waiting for Kafka cluster to be ready (this may take 3-5 minutes)..."
kubectl wait kafka/taskflow-kafka --for=condition=Ready -n "$NAMESPACE" --timeout=600s

# Create topics
echo "Creating Kafka topics..."
kubectl apply -f "$PROJECT_ROOT/kubernetes/kafka-topics.yaml" -n "$NAMESPACE"

# Wait for topics to be ready
sleep 10
kubectl get kafkatopics -n "$NAMESPACE"

echo ""
echo "========================================"
echo "  Kafka Setup Complete!"
echo "========================================"
echo ""
echo "Kafka Bootstrap Server: taskflow-kafka-kafka-bootstrap.$NAMESPACE:9092"
echo ""
echo "Verify with:"
echo "  kubectl get kafka -n $NAMESPACE"
echo "  kubectl get kafkatopics -n $NAMESPACE"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
