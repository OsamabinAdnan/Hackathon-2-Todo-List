#!/bin/bash
# =============================================================================
# Phase 5: Single-Command Minikube Deployment Script
# =============================================================================
# This script deploys the complete Todo AI Chatbot with event-driven architecture
# to Minikube, including Kafka, Dapr, and all microservices.
#
# Prerequisites:
#   - Minikube installed and running (minikube start)
#   - kubectl configured for Minikube
#   - Helm 3.x installed
#   - Dapr CLI installed
#   - Docker available (for building images)
#
# Usage:
#   ./scripts/deploy-minikube-phase5.sh [--skip-build] [--skip-kafka] [--skip-dapr]
#
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="default"
RELEASE_NAME="todo-chatbot"
KAFKA_NAMESPACE="kafka"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Parse arguments
SKIP_BUILD=false
SKIP_KAFKA=false
SKIP_DAPR=false

for arg in "$@"; do
    case $arg in
        --skip-build) SKIP_BUILD=true ;;
        --skip-kafka) SKIP_KAFKA=true ;;
        --skip-dapr) SKIP_DAPR=true ;;
        --help|-h)
            echo "Usage: $0 [--skip-build] [--skip-kafka] [--skip-dapr]"
            echo "  --skip-build  Skip Docker image building"
            echo "  --skip-kafka  Skip Kafka/Strimzi installation"
            echo "  --skip-dapr   Skip Dapr installation"
            exit 0
            ;;
    esac
done

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Minikube
    if ! command -v minikube &> /dev/null; then
        log_error "Minikube is not installed. Please install it first."
        exit 1
    fi

    # Check Minikube is running
    if ! minikube status &> /dev/null; then
        log_warn "Minikube is not running. Starting Minikube..."
        minikube start --memory=4096 --cpus=2
    fi

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install it first."
        exit 1
    fi

    # Check Helm
    if ! command -v helm &> /dev/null; then
        log_error "Helm is not installed. Please install it first."
        exit 1
    fi

    # Check Dapr CLI
    if ! command -v dapr &> /dev/null; then
        log_error "Dapr CLI is not installed. Please install it first."
        exit 1
    fi

    log_success "All prerequisites met."
}

build_docker_images() {
    if [ "$SKIP_BUILD" = true ]; then
        log_info "Skipping Docker image build (--skip-build flag)"
        return
    fi

    log_info "Building Docker images..."

    # Point Docker to Minikube's Docker daemon
    eval $(minikube docker-env)

    # Build backend
    log_info "Building backend image..."
    docker build -t todo-backend:latest "$PROJECT_ROOT/backend"

    # Build frontend
    log_info "Building frontend image..."
    docker build -t todo-frontend:latest "$PROJECT_ROOT/frontend"

    # Build notification service
    log_info "Building notification-service image..."
    docker build -t notification-service:latest "$PROJECT_ROOT/services/notification-service"

    # Build recurring service
    log_info "Building recurring-service image..."
    docker build -t recurring-service:latest "$PROJECT_ROOT/services/recurring-service"

    log_success "All Docker images built successfully."
}

install_strimzi_kafka() {
    if [ "$SKIP_KAFKA" = true ]; then
        log_info "Skipping Kafka installation (--skip-kafka flag)"
        return
    fi

    log_info "Installing Strimzi Kafka operator..."

    # Create Kafka namespace
    kubectl create namespace $KAFKA_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

    # Install Strimzi operator
    if ! kubectl get deployment strimzi-cluster-operator -n $KAFKA_NAMESPACE &> /dev/null; then
        log_info "Installing Strimzi operator..."
        kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n $KAFKA_NAMESPACE || true

        # Wait for operator to be ready
        log_info "Waiting for Strimzi operator to be ready..."
        kubectl wait --for=condition=available --timeout=300s deployment/strimzi-cluster-operator -n $KAFKA_NAMESPACE
    else
        log_info "Strimzi operator already installed."
    fi

    # Deploy Kafka cluster
    log_info "Deploying Kafka cluster..."
    kubectl apply -f "$PROJECT_ROOT/kubernetes/kafka-cluster-minikube.yaml" -n $KAFKA_NAMESPACE

    # Wait for Kafka to be ready
    log_info "Waiting for Kafka cluster to be ready (this may take a few minutes)..."
    kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=600s -n $KAFKA_NAMESPACE || {
        log_warn "Kafka not ready yet, continuing anyway..."
    }

    # Create topics
    log_info "Creating Kafka topics..."
    kubectl apply -f "$PROJECT_ROOT/kubernetes/kafka-topics.yaml" -n $KAFKA_NAMESPACE

    log_success "Kafka installation complete."
}

install_dapr() {
    if [ "$SKIP_DAPR" = true ]; then
        log_info "Skipping Dapr installation (--skip-dapr flag)"
        return
    fi

    log_info "Installing Dapr on Kubernetes..."

    # Check if Dapr is already installed
    if dapr status -k &> /dev/null; then
        log_info "Dapr is already installed."
    else
        log_info "Initializing Dapr on Kubernetes..."
        dapr init -k --wait
    fi

    # Apply Dapr components
    log_info "Applying Dapr components..."
    kubectl apply -f "$PROJECT_ROOT/dapr-components/minikube/"

    log_success "Dapr installation complete."
}

create_secrets() {
    log_info "Creating Kubernetes secrets..."

    # Check if secrets file exists
    SECRETS_FILE="$PROJECT_ROOT/.env.kubernetes"
    if [ ! -f "$SECRETS_FILE" ]; then
        log_warn "Secrets file not found at $SECRETS_FILE"
        log_warn "Creating template secrets file..."

        cat > "$SECRETS_FILE" << 'EOF'
# Kubernetes secrets for Todo Chatbot
# Fill in these values and run the deploy script again

# Database (Neon PostgreSQL)
NEON_DB_URL=postgresql://user:password@host/database

# JWT Authentication
JWT_SECRET=your-256-bit-secret-key-here

# AI API Keys (at least one required)
OPENROUTER_API_KEY=your-openrouter-key
QWEN_API_KEY=your-qwen-key
COHERE_API_KEY=your-cohere-key
EOF
        log_error "Please fill in $SECRETS_FILE and run the script again."
        exit 1
    fi

    # Source secrets
    source "$SECRETS_FILE"

    # Create database secret
    kubectl create secret generic ${RELEASE_NAME}-db-secret \
        --from-literal=NEON_DB_URL="$NEON_DB_URL" \
        --dry-run=client -o yaml | kubectl apply -f -

    # Create JWT secret
    kubectl create secret generic ${RELEASE_NAME}-jwt-secret \
        --from-literal=JWT_SECRET="$JWT_SECRET" \
        --dry-run=client -o yaml | kubectl apply -f -

    # Create AI secrets
    kubectl create secret generic ${RELEASE_NAME}-ai-secret \
        --from-literal=OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}" \
        --from-literal=OPENROUTER_URL="https://openrouter.ai/api/v1" \
        --from-literal=OPENROUTER_MODEL="arcee-ai/trinity-large-preview:free" \
        --from-literal=QWEN_API_KEY="${QWEN_API_KEY:-}" \
        --from-literal=QWEN_URL="https://portal.qwen.ai/v1" \
        --from-literal=QWEN_MODEL="qwen3-coder-plus" \
        --from-literal=COHERE_API_KEY="${COHERE_API_KEY:-}" \
        --from-literal=COHERE_URL="https://api.cohere.ai/v1" \
        --from-literal=COHERE_MODEL="command-a-03-2025" \
        --dry-run=client -o yaml | kubectl apply -f -

    log_success "Secrets created successfully."
}

deploy_helm_chart() {
    log_info "Deploying Todo Chatbot with Helm..."

    cd "$PROJECT_ROOT/helm/todo-chatbot"

    # Install or upgrade the Helm release
    helm upgrade --install $RELEASE_NAME . \
        -f values-minikube.yaml \
        --namespace $NAMESPACE \
        --wait \
        --timeout 10m

    log_success "Helm deployment complete."
}

verify_deployment() {
    log_info "Verifying deployment..."

    # Wait for all pods to be ready
    log_info "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=$RELEASE_NAME --timeout=300s || {
        log_warn "Some pods may not be ready yet."
    }

    # Show pod status
    echo ""
    log_info "Pod Status:"
    kubectl get pods -l app.kubernetes.io/instance=$RELEASE_NAME

    # Show services
    echo ""
    log_info "Services:"
    kubectl get svc -l app.kubernetes.io/instance=$RELEASE_NAME

    # Check Dapr sidecars
    if [ "$SKIP_DAPR" = false ]; then
        echo ""
        log_info "Dapr Sidecars:"
        kubectl get pods -l dapr.io/enabled=true -o wide
    fi

    log_success "Deployment verification complete."
}

print_access_info() {
    echo ""
    echo "============================================================"
    echo -e "${GREEN}  Deployment Complete!${NC}"
    echo "============================================================"
    echo ""
    echo "Access your application:"
    echo ""
    echo "  Frontend URL:"
    echo "    minikube service ${RELEASE_NAME}-frontend --url"
    echo ""
    echo "  Backend URL:"
    echo "    minikube service ${RELEASE_NAME}-backend --url"
    echo ""
    echo "  Dashboard:"
    echo "    minikube dashboard"
    echo ""
    echo "Verification:"
    echo "    ./scripts/verify-phase5.sh"
    echo ""
    echo "Test Event Flow:"
    echo "    ./scripts/test-event-flow.sh"
    echo ""
    echo "Cleanup:"
    echo "    ./scripts/cleanup-phase5.sh"
    echo ""
    echo "============================================================"
}

# Main execution
main() {
    echo ""
    echo "============================================================"
    echo "  Phase 5: Minikube Deployment"
    echo "============================================================"
    echo ""

    check_prerequisites
    build_docker_images
    install_strimzi_kafka
    install_dapr
    create_secrets
    deploy_helm_chart
    verify_deployment
    print_access_info
}

main
