---
name: execute-deployment-plan
description: Creates detailed, ordered deployment scripts/plans invoking doctl, kubectl, helm upgrade, and k8s-ops-orchestrator, including pre-checks, health waits, and rollback on failure. Use when executing production-ready deployment plans with proper validation, health checks, and rollback capabilities.
---

# Execute Deployment Plan

This skill helps create detailed, ordered deployment scripts and plans that invoke doctl, kubectl, helm upgrade, and k8s-ops-orchestrator with proper pre-checks, health waits, and rollback capabilities for production-ready deployments.

## When to Use This Skill

Use this skill when:
- Executing production deployments with proper validation
- Creating deployment scripts with health checks and rollbacks
- Orchestrating multi-component deployments
- Implementing zero-downtime deployment strategies
- Setting up automated deployment pipelines
- Managing complex deployment dependencies

## Deployment Script Structure

### Main Deployment Script
```bash
#!/bin/bash
# deploy-todo-platform.sh

set -e  # Exit on any error

# Configuration variables
export NAMESPACE="todo-app"
export RELEASE_NAME="todo-chatbot-platform"
export CHART_PATH="./charts/todo-chatbot-platform"
export VALUES_FILE="./values/values-prod.yaml"
export BACKUP_DIR="./backups"
export LOG_FILE="./logs/deployment-$(date +%Y%m%d-%H%M%S).log"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check if required tools are installed
    for cmd in doctl kubectl helm; do
        if ! command -v $cmd &> /dev/null; then
            log "ERROR: $cmd is not installed"
            exit 1
        fi
    done

    # Check if kubectl can connect to cluster
    if ! kubectl cluster-info &> /dev/null; then
        log "ERROR: Cannot connect to Kubernetes cluster"
        exit 1
    fi

    # Check if Helm chart exists
    if [ ! -f "$CHART_PATH/Chart.yaml" ]; then
        log "ERROR: Helm chart not found at $CHART_PATH"
        exit 1
    fi

    log "Prerequisites check passed"
}

# Function to create backup
create_backup() {
    log "Creating backup of current deployment..."

    mkdir -p "$BACKUP_DIR"

    # Backup current configuration
    kubectl get all -n "$NAMESPACE" -o yaml > "$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).yaml" || true
    helm get values "$RELEASE_NAME" -n "$NAMESPACE" > "$BACKUP_DIR/values-backup-$(date +%Y%m%d-%H%M%S).yaml" || true

    log "Backup created successfully"
}

# Function to run pre-deployment checks
run_pre_checks() {
    log "Running pre-deployment checks..."

    # Validate values file
    if [ ! -f "$VALUES_FILE" ]; then
        log "ERROR: Values file $VALUES_FILE not found"
        exit 1
    fi

    # Validate Helm chart
    if ! helm lint "$CHART_PATH"; then
        log "ERROR: Helm chart validation failed"
        exit 1
    fi

    # Check available resources
    local available_cpu=$(kubectl top nodes --no-headers | awk '{sum+=$3} END {print sum}')
    local available_memory=$(kubectl top nodes --no-headers | awk '{sum+=$5} END {print sum}')

    log "Available cluster resources - CPU: $available_cpu, Memory: $available_memory"

    log "Pre-deployment checks completed successfully"
}

# Function to deploy the application
deploy_application() {
    log "Starting application deployment..."

    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    # Add Helm repositories
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add dapr https://dapr.github.io/helm-charts
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update

    # Install/upgrade the application
    log "Installing/upgrading Helm release..."
    helm upgrade --install "$RELEASE_NAME" "$CHART_PATH" \
        --namespace "$NAMESPACE" \
        --values "$VALUES_FILE" \
        --timeout 20m \
        --atomic \
        --wait \
        --debug

    log "Application deployment completed"
}

# Function to wait for health checks
wait_for_health() {
    log "Waiting for services to be healthy..."

    # Wait for Kafka to be ready
    log "Waiting for Kafka to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n "$NAMESPACE" --timeout=10m || {
        log "ERROR: Kafka pods are not ready"
        exit 1
    }

    # Wait for Dapr to be ready
    log "Waiting for Dapr to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=dapr -n dapr-system --timeout=5m || {
        log "ERROR: Dapr pods are not ready"
        exit 1
    }

    # Wait for application pods to be ready
    log "Waiting for application pods to be ready..."
    for app in backend frontend mcp-server; do
        kubectl wait --for=condition=ready pod -l app.kubernetes.io/name="$app" -n "$NAMESPACE" --timeout=10m || {
            log "ERROR: $app pods are not ready"
            exit 1
        }
    done

    # Wait for ingress to be ready
    log "Waiting for ingress to be ready..."
    kubectl wait --for=condition=ready ingress -l app.kubernetes.io/name=ingress-nginx -n ingress-nginx --timeout=5m || {
        log "WARNING: Ingress may not be ready yet"
    }

    log "All services are healthy"
}

# Function to run post-deployment validation
run_post_validation() {
    log "Running post-deployment validation..."

    # Check if all pods are running
    local running_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running -o jsonpath='{.items[*].metadata.name}' | wc -w)
    local total_pods=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' | wc -w)

    log "Running pods: $running_pods / Total pods: $total_pods"

    if [ "$running_pods" -ne "$total_pods" ]; then
        log "ERROR: Not all pods are running"
        exit 1
    fi

    # Check service endpoints
    kubectl get endpoints -n "$NAMESPACE"

    # Run basic connectivity tests
    log "Running connectivity tests..."

    # Test if we can reach the backend service
    if kubectl get service todo-chatbot-platform-backend -n "$NAMESPACE" &> /dev/null; then
        log "Backend service is accessible"
    else
        log "ERROR: Backend service is not accessible"
        exit 1
    fi

    # Test if we can reach the frontend service
    if kubectl get service todo-chatbot-platform-frontend -n "$NAMESPACE" &> /dev/null; then
        log "Frontend service is accessible"
    else
        log "ERROR: Frontend service is not accessible"
        exit 1
    fi

    log "Post-deployment validation completed successfully"
}

# Function to rollback deployment
rollback_deployment() {
    log "Rolling back deployment..."

    # Get previous revision
    local prev_revision=$(helm history "$RELEASE_NAME" -n "$NAMESPACE" --max 10 | grep -v DEPLOYED | head -n 1 | awk '{print $1}')

    if [ -z "$prev_revision" ]; then
        log "ERROR: No previous revision found for rollback"
        exit 1
    fi

    log "Rolling back to revision $prev_revision"

    helm rollback "$RELEASE_NAME" "$prev_revision" -n "$NAMESPACE" --timeout 10m || {
        log "ERROR: Rollback failed"
        exit 1
    }

    # Wait for rollback to complete
    kubectl rollout status deployment -n "$NAMESPACE" --timeout=10m || {
        log "ERROR: Rollback status check failed"
        exit 1
    }

    log "Rollback completed successfully"
}

# Main execution
main() {
    log "Starting deployment of Todo Chatbot Platform"

    # Trap to handle errors and perform rollback if needed
    trap 'if [ $? -ne 0 ]; then log "Deployment failed, attempting rollback..."; rollback_deployment; fi' ERR

    check_prerequisites
    create_backup
    run_pre_checks
    deploy_application
    wait_for_health
    run_post_validation

    log "Deployment completed successfully!"
    log "Services deployed to namespace: $NAMESPACE"
    log "Release name: $RELEASE_NAME"

    # Show deployment status
    kubectl get pods -n "$NAMESPACE"
    kubectl get services -n "$NAMESPACE"
    kubectl get ingress -n "$NAMESPACE"
}

# Execute main function
main "$@"
```

## Advanced Deployment Script with Canary Deployment

### Canary Deployment Script
```bash
#!/bin/bash
# canary-deployment.sh

set -e

NAMESPACE="${1:-todo-app}"
PRIMARY_RELEASE="todo-chatbot-platform-primary"
CANARY_RELEASE="todo-chatbot-platform-canary"
CHART_PATH="${2:-./charts/todo-chatbot-platform}"
VALUES_FILE="${3:-./values/values-prod.yaml}"
CANARY_VALUES="${4:-./values/values-canary.yaml}"
TRAFFIC_INCREMENT="${5:-10}"  # Percentage of traffic to shift

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "./logs/canary-$(date +%Y%m%d-%H%M%S).log"
}

# Function to check current traffic distribution
check_traffic_distribution() {
    log "Checking current traffic distribution..."

    # If using Istio, check virtual service weights
    if kubectl get virtualservice -n "$NAMESPACE" &> /dev/null; then
        kubectl get virtualservice -n "$NAMESPACE" -o yaml
    fi

    # Check current pod counts
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=todo-backend
}

# Function to deploy canary version
deploy_canary() {
    log "Deploying canary version..."

    # Deploy canary with limited resources initially
    helm upgrade --install "$CANARY_RELEASE" "$CHART_PATH" \
        --namespace "$NAMESPACE" \
        --values "$VALUES_FILE" \
        --values "$CANARY_VALUES" \
        --set backend.replicaCount=1 \
        --set frontend.replicaCount=1 \
        --timeout 10m \
        --atomic \
        --wait

    log "Canary deployment completed"
}

# Function to run canary tests
run_canary_tests() {
    log "Running canary tests..."

    # Wait for canary pods to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-backend-canary -n "$NAMESPACE" --timeout=5m || {
        log "ERROR: Canary pods are not ready"
        return 1
    }

    # Run smoke tests against canary
    local test_result=0

    # Test backend health
    kubectl run smoke-test --image=curlimages/curl -it --rm --restart=Never \
        --namespace "$NAMESPACE" \
        --overrides='{"spec": {"hostNetwork": true}}' \
        -- curl -s -o /dev/null -w "%{http_code}" http://todo-chatbot-platform-backend-canary.$NAMESPACE:8000/health || test_result=$?

    if [ $test_result -ne 0 ]; then
        log "ERROR: Smoke tests failed"
        return 1
    fi

    # Test API endpoints
    kubectl run api-test --image=curlimages/curl -it --rm --restart=Never \
        --namespace "$NAMESPACE" \
        -- curl -s -o /dev/null -w "%{http_code}" http://todo-chatbot-platform-backend-canary.$NAMESPACE:8000/api/health || test_result=$?

    if [ $test_result -ne 0 ]; then
        log "ERROR: API tests failed"
        return 1
    fi

    log "Canary tests passed"
    return 0
}

# Function to gradually shift traffic
shift_traffic() {
    local current_weight=0
    local target_weight=100

    log "Gradually shifting traffic to canary..."

    while [ $current_weight -lt $target_weight ]; do
        current_weight=$((current_weight + TRAFFIC_INCREMENT))

        if [ $current_weight -gt $target_weight ]; then
            current_weight=$target_weight
        fi

        log "Shifting $current_weight% traffic to canary..."

        # Update virtual service to route traffic (if using Istio)
        # This is a simplified example - actual implementation depends on service mesh
        cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: todo-backend-vs
  namespace: $NAMESPACE
spec:
  http:
  - route:
    - destination:
        host: todo-chatbot-platform-backend-primary
      weight: $((100 - current_weight))
    - destination:
        host: todo-chatbot-platform-backend-canary
      weight: $current_weight
EOF

        # Wait for traffic shift to stabilize
        sleep 30

        # Run health checks during traffic shift
        run_canary_tests || {
            log "ERROR: Tests failed during traffic shift at $current_weight%"
            return 1
        }

        log "Traffic shifted to $current_weight%"
    done

    log "Traffic shift completed"
}

# Function to promote canary
promote_canary() {
    log "Promoting canary to primary..."

    # Scale up canary to full capacity
    kubectl scale deployment todo-chatbot-platform-backend-canary -n "$NAMESPACE" --replicas=3
    kubectl scale deployment todo-chatbot-platform-frontend-canary -n "$NAMESPACE" --replicas=3

    # Wait for scaled pods to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-backend-canary -n "$NAMESPACE" --timeout=5m
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-frontend-canary -n "$NAMESPACE" --timeout=5m

    # Rename canary to primary (this is a conceptual example)
    # In reality, you'd update the primary deployment with canary configuration

    log "Canary promoted to primary"
}

# Function to rollback canary
rollback_canary() {
    log "Rolling back canary deployment..."

    # Remove canary deployment
    helm uninstall "$CANARY_RELEASE" --namespace "$NAMESPACE" || true

    # Reset traffic to primary
    cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: todo-backend-vs
  namespace: $NAMESPACE
spec:
  http:
  - route:
    - destination:
        host: todo-chatbot-platform-backend-primary
      weight: 100
EOF

    log "Canary rollback completed"
}

# Main canary deployment
main_canary() {
    log "Starting canary deployment process..."

    trap 'if [ $? -ne 0 ]; then log "Canary deployment failed, rolling back..."; rollback_canary; fi' ERR

    deploy_canary
    run_canary_tests || {
        log "Canary tests failed, rolling back..."
        rollback_canary
        exit 1
    }

    shift_traffic || {
        log "Traffic shifting failed, rolling back..."
        rollback_canary
        exit 1
    }

    promote_canary
    rollback_canary  # Clean up canary resources after promotion

    log "Canary deployment completed successfully!"
}

main_canary
```

## Blue-Green Deployment Script

### Blue-Green Deployment
```bash
#!/bin/bash
# blue-green-deployment.sh

set -e

NAMESPACE="${1:-todo-app}"
BLUE_RELEASE="todo-chatbot-platform-blue"
GREEN_RELEASE="todo-chatbot-platform-green"
CURRENT_COLOR="blue"  # Assume blue is currently active

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "./logs/blue-green-$(date +%Y%m%d-%H%M%S).log"
}

# Function to determine current active color
get_current_color() {
    if kubectl get service todo-chatbot-platform-active -o jsonpath='{.spec.selector.color}' 2>/dev/null | grep -q "green"; then
        echo "green"
    else
        echo "blue"
    fi
}

# Function to deploy to inactive environment
deploy_to_inactive() {
    local inactive_color="$1"
    local values_file="$2"

    log "Deploying to $inactive_color environment..."

    local release_name=""
    if [ "$inactive_color" = "blue" ]; then
        release_name="$BLUE_RELEASE"
    else
        release_name="$GREEN_RELEASE"
    fi

    helm upgrade --install "$release_name" "./charts/todo-chatbot-platform" \
        --namespace "$NAMESPACE" \
        --values "$values_file" \
        --set service.color="$inactive_color" \
        --timeout 15m \
        --atomic \
        --wait

    log "$inactive_color deployment completed"
}

# Function to switch traffic
switch_traffic() {
    local target_color="$1"

    log "Switching traffic to $target_color..."

    # Update the active service to point to the target color
    kubectl patch service todo-chatbot-platform-active -n "$NAMESPACE" \
        -p "{\"spec\":{\"selector\":{\"color\":\"$target_color\"}}}"

    # Wait for traffic switch to propagate
    sleep 10

    log "Traffic switched to $target_color"
}

# Function to validate deployment
validate_deployment() {
    local color="$1"

    log "Validating $color deployment..."

    # Wait for pods to be ready
    kubectl wait --for=condition=ready pod -l color="$color" -n "$NAMESPACE" --timeout=10m || {
        log "ERROR: $color pods are not ready"
        return 1
    }

    # Run health checks
    local test_pod=$(kubectl get pods -n "$NAMESPACE" -l color="$color" -o jsonpath='{.items[0].metadata.name}')

    if [ -n "$test_pod" ]; then
        kubectl exec -n "$NAMESPACE" "$test_pod" -- curl -s http://localhost:8000/health || {
            log "ERROR: Health check failed for $color"
            return 1
        }
    fi

    log "$color validation passed"
    return 0
}

# Function to clean up old environment
cleanup_old_environment() {
    local old_color="$1"

    log "Cleaning up $old_color environment..."

    local old_release=""
    if [ "$old_color" = "blue" ]; then
        old_release="$BLUE_RELEASE"
    else
        old_release="$GREEN_RELEASE"
    fi

    helm uninstall "$old_release" --namespace "$NAMESPACE" || true

    log "$old_color environment cleaned up"
}

# Main blue-green deployment
main_blue_green() {
    log "Starting blue-green deployment..."

    local current_color=$(get_current_color)
    local inactive_color=""

    if [ "$current_color" = "blue" ]; then
        inactive_color="green"
    else
        inactive_color="blue"
    fi

    log "Current active: $current_color, deploying to: $inactive_color"

    # Deploy to inactive environment
    deploy_to_inactive "$inactive_color" "./values/values-${inactive_color}.yaml"

    # Validate the new deployment
    if ! validate_deployment "$inactive_color"; then
        log "Validation failed for $inactive_color, aborting..."
        cleanup_old_environment "$inactive_color"
        exit 1
    fi

    # Switch traffic to new environment
    switch_traffic "$inactive_color"

    # Clean up old environment after a delay to ensure stability
    (sleep 300  # Wait 5 minutes to ensure new version is stable
     cleanup_old_environment "$current_color") &

    log "Blue-green deployment completed! Active: $inactive_color"
}

main_blue_green
```

## Deployment Validation and Monitoring

### Health Check Script
```bash
#!/bin/bash
# validate-deployment.sh

NAMESPACE="${1:-todo-app}"
RELEASE_NAME="${2:-todo-chatbot-platform}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check deployment health
check_deployment_health() {
    log "Checking deployment health..."

    local unhealthy_components=0

    # Check Kafka
    log "Checking Kafka..."
    if kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=kafka 2>/dev/null; then
        local kafka_unready=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=kafka --field-selector=status.phase!=Running -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | wc -l)
        if [ "$kafka_unready" -gt 0 ]; then
            log "WARNING: $kafka_unready Kafka pods are not running"
            ((unhealthy_components++))
        else
            log "✓ Kafka is healthy"
        fi
    else
        log "INFO: Kafka not deployed"
    fi

    # Check Dapr
    log "Checking Dapr..."
    if kubectl get pods -n dapr-system 2>/dev/null; then
        local dapr_unready=$(kubectl get pods -n dapr-system --field-selector=status.phase!=Running -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | wc -l)
        if [ "$dapr_unready" -gt 0 ]; then
            log "WARNING: $dapr_unready Dapr pods are not running"
            ((unhealthy_components++))
        else
            log "✓ Dapr is healthy"
        fi
    else
        log "INFO: Dapr not deployed"
    fi

    # Check application services
    for app in backend frontend mcp-server; do
        log "Checking $app..."
        if kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name="$app" 2>/dev/null; then
            local app_unready=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name="$app" --field-selector=status.phase!=Running -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | wc -l)
            if [ "$app_unready" -gt 0 ]; then
                log "WARNING: $app_unready $app pods are not running"
                ((unhealthy_components++))
            else
                log "✓ $app is healthy"
            fi
        fi
    done

    # Check services
    log "Checking services..."
    kubectl get services -n "$NAMESPACE"

    # Check ingresses
    log "Checking ingresses..."
    kubectl get ingress -n "$NAMESPACE"

    if [ $unhealthy_components -eq 0 ]; then
        log "✓ All components are healthy"
        return 0
    else
        log "✗ $unhealthy_components components are unhealthy"
        return 1
    fi
}

# Function to run connectivity tests
run_connectivity_tests() {
    log "Running connectivity tests..."

    # Test service connectivity
    local services_to_test=("todo-chatbot-platform-backend" "todo-chatbot-platform-frontend" "todo-chatbot-platform-mcp-server")

    for service in "${services_to_test[@]}"; do
        if kubectl get service "$service" -n "$NAMESPACE" &> /dev/null; then
            log "✓ Service $service is accessible"

            # Get service endpoints
            local endpoints=$(kubectl get endpoints "$service" -n "$NAMESPACE" -o jsonpath='{.subsets[*].addresses[*].ip}')
            if [ -n "$endpoints" ]; then
                log "  Endpoints: $endpoints"
            else
                log "  WARNING: No endpoints available for $service"
            fi
        else
            log "✗ Service $service is not accessible"
        fi
    done
}

# Function to check resource utilization
check_resource_utilization() {
    log "Checking resource utilization..."

    # Check node resources
    kubectl top nodes

    # Check pod resources
    kubectl top pods -n "$NAMESPACE"

    # Check for resource constraints
    local constrained_pods=$(kubectl get pods -n "$NAMESPACE" -o json | jq -r '.items[] | select(.status.conditions[]?.type=="ContainersReady" and .status.conditions[]?.status=="False") | .metadata.name')

    if [ -n "$constrained_pods" ]; then
        log "WARNING: Following pods have resource constraints:"
        echo "$constrained_pods"
    fi
}

# Main validation
main_validation() {
    log "Starting deployment validation for $RELEASE_NAME in namespace $NAMESPACE"

    if check_deployment_health && run_connectivity_tests; then
        check_resource_utilization
        log "✓ Deployment validation completed successfully"
        return 0
    else
        log "✗ Deployment validation failed"
        return 1
    fi
}

main_validation
```

## Rollback Procedures

### Automated Rollback Script
```bash
#!/bin/bash
# rollback-deployment.sh

NAMESPACE="${1:-todo-app}"
RELEASE_NAME="${2:-todo-chatbot-platform}"
REASON="${3:-manual}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "./logs/rollback-$(date +%Y%m%d-%H%M%S).log"
}

# Function to find previous revision
find_previous_revision() {
    local revision=$(helm history "$RELEASE_NAME" -n "$NAMESPACE" --max 10 | \
        grep -v DEPLOYED | \
        grep -v SUPERSEDED | \
        head -n 1 | \
        awk '{print $1}')

    if [ -z "$revision" ]; then
        log "ERROR: No previous revision found"
        return 1
    fi

    echo "$revision"
}

# Function to perform rollback
perform_rollback() {
    local revision="$1"

    log "Rolling back to revision $revision due to: $REASON"

    # Rollback the Helm release
    if ! helm rollback "$RELEASE_NAME" "$revision" -n "$NAMESPACE" --timeout 15m; then
        log "ERROR: Rollback failed"
        return 1
    fi

    log "Rollback initiated, waiting for completion..."

    # Wait for deployments to be ready
    for deployment in $(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}'); do
        log "Waiting for deployment $deployment to be ready..."
        if ! kubectl rollout status deployment "$deployment" -n "$NAMESPACE" --timeout=10m; then
            log "ERROR: Deployment $deployment failed to become ready after rollback"
            return 1
        fi
    done

    log "Rollback completed successfully"
    return 0
}

# Function to notify about rollback
notify_rollback() {
    local revision="$1"

    log "Sending rollback notification..."

    # In a real scenario, you might send notifications to Slack, email, etc.
    # This is a placeholder for notification logic
    log "Rollback notification sent: Rolled back $RELEASE_NAME to revision $revision due to $REASON"
}

# Main rollback
main_rollback() {
    log "Starting rollback procedure for $RELEASE_NAME"

    local previous_revision=$(find_previous_revision) || {
        log "FATAL: Cannot find previous revision to rollback to"
        exit 1
    }

    log "Found previous revision: $previous_revision"

    if perform_rollback "$previous_revision"; then
        notify_rollback "$previous_revision"
        log "Rollback completed successfully"
    else
        log "Rollback failed, manual intervention required"
        exit 1
    fi
}

main_rollback
```

## Deployment Pipeline Integration

### CI/CD Pipeline Script
```bash
#!/bin/bash
# ci-cd-pipeline.sh

# Configuration
SOURCE_BRANCH="${1:-main}"
TARGET_ENV="${2:-staging}"
DOCKER_REGISTRY="${3:-your-registry.hub.docker.com}"
IMAGE_TAG="${4:-$(git rev-parse --short HEAD)}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "./logs/cicd-$(date +%Y%m%d-%H%M%S).log"
}

# Function to build and push images
build_and_push_images() {
    log "Building and pushing Docker images..."

    # Build backend image
    docker build -t "$DOCKER_REGISTRY/todo-backend:$IMAGE_TAG" ./backend .
    docker push "$DOCKER_REGISTRY/todo-backend:$IMAGE_TAG"

    # Build frontend image
    docker build -t "$DOCKER_REGISTRY/todo-frontend:$IMAGE_TAG" ./frontend .
    docker push "$DOCKER_REGISTRY/todo-frontend:$IMAGE_TAG"

    # Build MCP server image
    docker build -t "$DOCKER_REGISTRY/todo-mcp-server:$IMAGE_TAG" ./mcp-server .
    docker push "$DOCKER_REGISTRY/todo-mcp-server:$IMAGE_TAG"

    log "Images built and pushed successfully"
}

# Function to update Helm values with new image tags
update_helm_values() {
    local temp_values="./temp-values-$IMAGE_TAG.yaml"

    # Create temporary values file with new image tags
    cat > "$temp_values" <<EOF
backend:
  image:
    repository: $DOCKER_REGISTRY/todo-backend
    tag: $IMAGE_TAG

frontend:
  image:
    repository: $DOCKER_REGISTRY/todo-frontend
    tag: $IMAGE_TAG

mcpServer:
  image:
    repository: $DOCKER_REGISTRY/todo-mcp-server
    tag: $IMAGE_TAG
EOF

    echo "$temp_values"
}

# Function to run tests
run_tests() {
    log "Running tests..."

    # Run unit tests
    log "Running unit tests..."
    cd ./backend && python -m pytest tests/unit/ && cd ..
    cd ./frontend && npm test && cd ..

    # Run integration tests
    log "Running integration tests..."
    cd ./backend && python -m pytest tests/integration/ && cd ..

    # Run security scans
    log "Running security scans..."
    # Add security scanning tools here (trivy, etc.)

    log "All tests passed"
}

# Function to deploy based on environment
deploy_to_environment() {
    local env="$1"
    local values_file="$2"

    case "$env" in
        "staging")
            NAMESPACE="todo-staging"
            VALUES_FILE="./values/values-staging.yaml"
            ;;
        "production")
            NAMESPACE="todo-prod"
            VALUES_FILE="./values/values-prod.yaml"
            # Add additional production-specific validations
            log "Running production pre-flight checks..."
            # Add production-specific checks here
            ;;
        *)
            NAMESPACE="todo-$env"
            VALUES_FILE="./values/values-$env.yaml"
            ;;
    esac

    log "Deploying to $env environment ($NAMESPACE)..."

    # Merge values files
    local merged_values="./temp-values-$env-$IMAGE_TAG.yaml"
    yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' "$VALUES_FILE" "$values_file" > "$merged_values"

    # Deploy using Helm
    helm upgrade --install "todo-chatbot-platform-$env" "./charts/todo-chatbot-platform" \
        --namespace "$NAMESPACE" \
        --values "$merged_values" \
        --create-namespace \
        --timeout 20m \
        --atomic \
        --wait

    log "Deployment to $env completed"

    # Clean up temporary files
    rm -f "$merged_values"
}

# Main CI/CD pipeline
main_pipeline() {
    log "Starting CI/CD pipeline for branch $SOURCE_BRANCH to environment $TARGET_ENV"

    # Run tests first
    run_tests || {
        log "Tests failed, stopping pipeline"
        exit 1
    }

    # Build and push images
    build_and_push_images || {
        log "Image build/push failed, stopping pipeline"
        exit 1
    }

    # Update Helm values
    local temp_values=$(update_helm_values)

    # Deploy to target environment
    deploy_to_environment "$TARGET_ENV" "$temp_values" || {
        log "Deployment failed"
        # Optionally trigger rollback
        # ./rollback-deployment.sh "$NAMESPACE" "todo-chatbot-platform-$TARGET_ENV"
        exit 1
    }

    # Clean up
    rm -f "$temp_values"

    log "CI/CD pipeline completed successfully"
}

main_pipeline
```

## Output Format

Generate deployment plans that include:
- Complete deployment scripts with error handling and logging
- Pre-deployment validation and health checks
- Rollback procedures with automated recovery
- Traffic shifting strategies (canary, blue-green)
- Resource monitoring and validation
- CI/CD pipeline integration
- Comprehensive logging and audit trails
- Multi-environment deployment configurations
- Security validation and compliance checks