#!/bin/bash
# =============================================================================
# Phase 5: Cleanup Script
# =============================================================================
# This script removes all Phase 5 resources from Minikube.
#
# Usage:
#   ./scripts/cleanup-phase5.sh [--all] [--keep-kafka] [--keep-dapr]
#
# Options:
#   --all         Remove everything including Kafka and Dapr
#   --keep-kafka  Keep Kafka cluster installed
#   --keep-dapr   Keep Dapr installed
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

# Parse arguments
REMOVE_ALL=false
KEEP_KAFKA=false
KEEP_DAPR=false

for arg in "$@"; do
    case $arg in
        --all) REMOVE_ALL=true ;;
        --keep-kafka) KEEP_KAFKA=true ;;
        --keep-dapr) KEEP_DAPR=true ;;
        --help|-h)
            echo "Usage: $0 [--all] [--keep-kafka] [--keep-dapr]"
            echo "  --all         Remove everything including Kafka and Dapr"
            echo "  --keep-kafka  Keep Kafka cluster installed"
            echo "  --keep-dapr   Keep Dapr installed"
            exit 0
            ;;
    esac
done

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

confirm() {
    read -p "Are you sure you want to proceed? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleanup cancelled."
        exit 0
    fi
}

cleanup_helm() {
    log_info "Uninstalling Helm release..."

    if helm list -n $NAMESPACE | grep -q $RELEASE_NAME; then
        helm uninstall $RELEASE_NAME -n $NAMESPACE
        log_success "Helm release uninstalled."
    else
        log_warn "Helm release '$RELEASE_NAME' not found."
    fi
}

cleanup_secrets() {
    log_info "Removing secrets..."

    kubectl delete secret ${RELEASE_NAME}-db-secret --ignore-not-found=true
    kubectl delete secret ${RELEASE_NAME}-jwt-secret --ignore-not-found=true
    kubectl delete secret ${RELEASE_NAME}-ai-secret --ignore-not-found=true

    log_success "Secrets removed."
}

cleanup_dapr_components() {
    log_info "Removing Dapr components..."

    kubectl delete -f dapr-components/minikube/ --ignore-not-found=true 2>/dev/null || true

    log_success "Dapr components removed."
}

cleanup_dapr() {
    if [ "$KEEP_DAPR" = true ]; then
        log_info "Keeping Dapr installed (--keep-dapr flag)"
        return
    fi

    log_info "Uninstalling Dapr..."

    if dapr status -k &> /dev/null; then
        dapr uninstall -k
        log_success "Dapr uninstalled."
    else
        log_warn "Dapr not installed on cluster."
    fi
}

cleanup_kafka() {
    if [ "$KEEP_KAFKA" = true ]; then
        log_info "Keeping Kafka installed (--keep-kafka flag)"
        return
    fi

    log_info "Removing Kafka resources..."

    # Delete Kafka topics
    kubectl delete -f kubernetes/kafka-topics.yaml -n $KAFKA_NAMESPACE --ignore-not-found=true 2>/dev/null || true

    # Delete Kafka cluster
    kubectl delete -f kubernetes/kafka-cluster-minikube.yaml -n $KAFKA_NAMESPACE --ignore-not-found=true 2>/dev/null || true

    # Wait for Kafka resources to be deleted
    log_info "Waiting for Kafka resources to be deleted..."
    sleep 10

    if [ "$REMOVE_ALL" = true ]; then
        # Delete Strimzi operator
        log_info "Removing Strimzi operator..."
        kubectl delete -f 'https://strimzi.io/install/latest?namespace=kafka' -n $KAFKA_NAMESPACE --ignore-not-found=true 2>/dev/null || true

        # Delete Kafka namespace
        kubectl delete namespace $KAFKA_NAMESPACE --ignore-not-found=true 2>/dev/null || true
    fi

    log_success "Kafka resources removed."
}

cleanup_images() {
    log_info "Removing Docker images from Minikube..."

    # Point to Minikube's Docker
    eval $(minikube docker-env)

    # Remove images
    docker rmi todo-frontend:latest 2>/dev/null || true
    docker rmi todo-backend:latest 2>/dev/null || true
    docker rmi notification-service:latest 2>/dev/null || true
    docker rmi recurring-service:latest 2>/dev/null || true

    log_success "Docker images removed."
}

# Main
main() {
    echo ""
    echo "============================================================"
    echo "  Phase 5: Cleanup"
    echo "============================================================"
    echo ""

    log_warn "This will remove the following resources:"
    echo "  - Helm release: $RELEASE_NAME"
    echo "  - Kubernetes secrets"
    echo "  - Dapr components"

    if [ "$KEEP_DAPR" = false ]; then
        echo "  - Dapr installation"
    fi

    if [ "$KEEP_KAFKA" = false ]; then
        echo "  - Kafka cluster and topics"
        if [ "$REMOVE_ALL" = true ]; then
            echo "  - Strimzi operator"
            echo "  - Kafka namespace"
        fi
    fi

    if [ "$REMOVE_ALL" = true ]; then
        echo "  - Docker images"
    fi

    echo ""
    confirm

    cleanup_helm
    cleanup_secrets
    cleanup_dapr_components

    if [ "$REMOVE_ALL" = true ] || [ "$KEEP_DAPR" = false ]; then
        cleanup_dapr
    fi

    if [ "$REMOVE_ALL" = true ] || [ "$KEEP_KAFKA" = false ]; then
        cleanup_kafka
    fi

    if [ "$REMOVE_ALL" = true ]; then
        cleanup_images
    fi

    echo ""
    log_success "Cleanup complete!"
    echo ""
    echo "To redeploy, run:"
    echo "  ./scripts/deploy-minikube-phase5.sh"
    echo ""
}

main
