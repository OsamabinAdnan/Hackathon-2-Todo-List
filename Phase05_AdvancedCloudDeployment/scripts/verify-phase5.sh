#!/bin/bash
# =============================================================================
# Phase 5: Deployment Verification Script
# =============================================================================
# This script verifies that the Phase 5 deployment is healthy and functional.
#
# Usage:
#   ./scripts/verify-phase5.sh [--verbose]
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
RELEASE_NAME="todo-chatbot"
KAFKA_NAMESPACE="kafka"
VERBOSE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --verbose|-v) VERBOSE=true ;;
    esac
done

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; ((PASSED++)); }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; ((WARNINGS++)); }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; ((FAILED++)); }

check_pod_status() {
    local app=$1
    local name="${RELEASE_NAME}-${app}"

    if kubectl get pod -l app=$app,app.kubernetes.io/instance=$RELEASE_NAME -o name &> /dev/null; then
        local status=$(kubectl get pod -l app=$app,app.kubernetes.io/instance=$RELEASE_NAME -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
        local ready=$(kubectl get pod -l app=$app,app.kubernetes.io/instance=$RELEASE_NAME -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)

        if [ "$status" = "Running" ] && [ "$ready" = "True" ]; then
            log_success "$app pod is running and ready"
            return 0
        else
            log_error "$app pod status: $status, ready: $ready"
            return 1
        fi
    else
        log_error "$app pod not found"
        return 1
    fi
}

check_service() {
    local app=$1
    local name="${RELEASE_NAME}-${app}"

    if kubectl get svc $name &> /dev/null; then
        log_success "$app service exists"
        return 0
    else
        log_error "$app service not found"
        return 1
    fi
}

check_health_endpoint() {
    local app=$1
    local port=$2
    local path=${3:-/health}

    local pod=$(kubectl get pod -l app=$app,app.kubernetes.io/instance=$RELEASE_NAME -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$pod" ]; then
        log_error "$app health check failed - pod not found"
        return 1
    fi

    local response=$(kubectl exec $pod -- curl -s -o /dev/null -w '%{http_code}' http://localhost:$port$path 2>/dev/null || echo "000")

    if [ "$response" = "200" ]; then
        log_success "$app health check passed (HTTP $response)"
        return 0
    else
        log_error "$app health check failed (HTTP $response)"
        return 1
    fi
}

check_dapr_sidecar() {
    local app=$1

    local pod=$(kubectl get pod -l app=$app,app.kubernetes.io/instance=$RELEASE_NAME -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$pod" ]; then
        log_warn "$app Dapr sidecar check skipped - pod not found"
        return 1
    fi

    local containers=$(kubectl get pod $pod -o jsonpath='{.spec.containers[*].name}' 2>/dev/null)

    if echo "$containers" | grep -q "daprd"; then
        log_success "$app has Dapr sidecar"
        return 0
    else
        log_warn "$app does not have Dapr sidecar"
        return 1
    fi
}

check_kafka() {
    log_info "Checking Kafka cluster..."

    # Check if Kafka pod exists
    if kubectl get pod -l strimzi.io/name=taskflow-kafka-kafka -n $KAFKA_NAMESPACE &> /dev/null; then
        local status=$(kubectl get pod -l strimzi.io/name=taskflow-kafka-kafka -n $KAFKA_NAMESPACE -o jsonpath='{.items[0].status.phase}' 2>/dev/null)

        if [ "$status" = "Running" ]; then
            log_success "Kafka cluster is running"

            # Check topics
            local topics=$(kubectl exec taskflow-kafka-kafka-0 -n $KAFKA_NAMESPACE -- \
                bin/kafka-topics.sh --list --bootstrap-server localhost:9092 2>/dev/null || echo "")

            if echo "$topics" | grep -q "task-events"; then
                log_success "Kafka topic 'task-events' exists"
            else
                log_warn "Kafka topic 'task-events' not found"
            fi

            if echo "$topics" | grep -q "reminders"; then
                log_success "Kafka topic 'reminders' exists"
            else
                log_warn "Kafka topic 'reminders' not found"
            fi

            return 0
        else
            log_error "Kafka cluster status: $status"
            return 1
        fi
    else
        log_warn "Kafka cluster not found (may be disabled)"
        return 1
    fi
}

check_dapr_components() {
    log_info "Checking Dapr components..."

    # Check if Dapr is installed
    if ! dapr status -k &> /dev/null; then
        log_warn "Dapr not installed on cluster"
        return 1
    fi

    log_success "Dapr is installed on cluster"

    # Check pub/sub component
    if kubectl get component kafka-pubsub &> /dev/null; then
        log_success "Dapr kafka-pubsub component exists"
    else
        log_warn "Dapr kafka-pubsub component not found"
    fi

    # Check state store component
    if kubectl get component statestore &> /dev/null; then
        log_success "Dapr statestore component exists"
    else
        log_warn "Dapr statestore component not found"
    fi

    return 0
}

# Main verification
main() {
    echo ""
    echo "============================================================"
    echo "  Phase 5: Deployment Verification"
    echo "============================================================"
    echo ""

    # Core Services
    log_info "Checking core services..."
    echo ""

    check_pod_status "backend"
    check_service "backend"
    check_health_endpoint "backend" 8000 "/health"

    echo ""
    check_pod_status "frontend"
    check_service "frontend"

    # Phase 5 Services
    echo ""
    log_info "Checking Phase 5 services..."
    echo ""

    # Notification service (may be disabled)
    if kubectl get deployment ${RELEASE_NAME}-notification &> /dev/null; then
        check_pod_status "notification"
        check_service "notification"
        check_health_endpoint "notification" 8001 "/health"
    else
        log_warn "Notification service not deployed"
    fi

    echo ""

    # Recurring service (may be disabled)
    if kubectl get deployment ${RELEASE_NAME}-recurring &> /dev/null; then
        check_pod_status "recurring"
        check_service "recurring"
        check_health_endpoint "recurring" 8002 "/health"
    else
        log_warn "Recurring service not deployed"
    fi

    # Dapr
    echo ""
    log_info "Checking Dapr integration..."
    echo ""

    check_dapr_sidecar "backend"
    check_dapr_sidecar "notification"
    check_dapr_sidecar "recurring"
    check_dapr_components

    # Kafka
    echo ""
    check_kafka

    # Summary
    echo ""
    echo "============================================================"
    echo "  Verification Summary"
    echo "============================================================"
    echo ""
    echo -e "  ${GREEN}Passed:${NC}   $PASSED"
    echo -e "  ${RED}Failed:${NC}   $FAILED"
    echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
    echo ""

    if [ $FAILED -gt 0 ]; then
        echo -e "${RED}Some checks failed. Please investigate.${NC}"
        exit 1
    elif [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}All critical checks passed with warnings.${NC}"
        exit 0
    else
        echo -e "${GREEN}All checks passed successfully!${NC}"
        exit 0
    fi
}

main
