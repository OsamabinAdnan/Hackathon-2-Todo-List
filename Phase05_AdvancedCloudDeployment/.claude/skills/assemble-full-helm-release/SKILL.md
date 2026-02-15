---
name: assemble-full-helm-release
description: Combines charts from helm-chart-packager into a parent Helm chart deploying Kafka → Dapr operator → Todo services → Ingress, with shared values overrides. Use when creating unified Helm charts for complete application deployment with proper service dependencies and configuration management.
---

# Assemble Full Helm Release

This skill helps create unified parent Helm charts that combine multiple subcharts (Kafka, Dapr operator, Todo services, Ingress) into a single deployable unit with proper service dependencies and shared configuration management.

## When to Use This Skill

Use this skill when:
- Creating parent Helm charts for complete application deployments
- Combining multiple service charts into a unified deployment
- Managing dependencies between Kafka, Dapr, and application services
- Coordinating configuration across multiple services
- Creating deployment blueprints for production environments
- Managing shared values across service components

## Parent Chart Structure

### Chart.yaml for Parent Chart
```yaml
apiVersion: v2
name: todo-chatbot-platform
description: A complete Todo application platform with AI chatbot, Kafka messaging, and Dapr integration
type: application
version: 1.0.0
appVersion: "1.0.0"

dependencies:
  - name: kafka
    version: ^2.0.0
    repository: https://charts.bitnami.com/bitnami
    alias: kafka
    condition: kafka.enabled

  - name: dapr
    version: ^1.11.0
    repository: https://dapr.github.io/helm-charts
    alias: dapr
    condition: dapr.enabled

  - name: todo-backend
    version: ~1.0.0
    repository: file://../todo-backend
    alias: backend
    condition: backend.enabled

  - name: todo-frontend
    version: ~1.0.0
    repository: file://../todo-frontend
    alias: frontend
    condition: frontend.enabled

  - name: todo-mcp-server
    version: ~1.0.0
    repository: file://../todo-mcp-server
    alias: mcp-server
    condition: mcpServer.enabled

  - name: ingress-nginx
    version: ^4.0.0
    repository: https://kubernetes.github.io/ingress-nginx
    alias: ingress
    condition: ingress.enabled
```

## Values Schema

### Root values.yaml
```yaml
# Global configuration
global:
  imageRegistry: ""
  storageClass: "do-block-storage"
  domain: "todo-app.digitalocean.space"
  tls:
    enabled: true
    issuer: "letsencrypt-prod"

# Kafka configuration
kafka:
  enabled: true
  architecture: "replication"
  auth:
    clientProtocol: "sasl"
    interBrokerProtocol: "sasl"
    sasl:
      mechanisms: "scram-sha-512"
      jaas:
        clientUsers:
          - "kafka-user"
        clientPasswords:
          - "changeme"
        interBrokerUser: "kafka-broker"
        interBrokerPassword: "changeme"
  replicaCount: 3
  heapOpts: "-Xmx4g -Xms4g"
  resources:
    limits:
      cpu: 2000m
      memory: 8Gi
    requests:
      cpu: 1000m
      memory: 4Gi
  storage:
    size: 100Gi
  metrics:
    kafka:
      enabled: true
      serviceMonitor:
        enabled: true
    zookeeper:
      enabled: true
      serviceMonitor:
        enabled: true

# Dapr configuration
dapr:
  enabled: true
  global:
    registry: "docker.io/daprio"
    tag: "1.11.0"
  controlPlane:
    resources:
      limits:
        cpu: 1000m
        memory: 1Gi
      requests:
        cpu: 250m
        memory: 256Mi
  placement:
    resources:
      limits:
        cpu: 500m
        memory: 256Mi
      requests:
        cpu: 100m
        memory: 128Mi
  redis:
    enabled: false  # We'll use Kafka for pubsub
  injector:
    resources:
      limits:
        cpu: 500m
        memory: 256Mi
      requests:
        cpu: 50m
        memory: 128Mi

# Backend service configuration
backend:
  enabled: true
  image:
    repository: "todo-backend"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  service:
    type: ClusterIP
    port: 8000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi
  env:
    DATABASE_URL: "postgresql://neon-db:5432/todo_db"
    KAFKA_BROKERS: "todo-chatbot-platform-kafka:9092"
    DAPR_HTTP_ENDPOINT: "http://127.0.0.1:3500"
  dapr:
    enabled: true
    appId: "todo-backend"
    appPort: 8000
    appProtocol: "http"

# Frontend service configuration
frontend:
  enabled: true
  image:
    repository: "todo-frontend"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  service:
    type: ClusterIP
    port: 3000
  resources:
    limits:
      cpu: 300m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  env:
    NEXT_PUBLIC_API_URL: "https://{{ .Values.global.domain }}/api"
    NEXT_PUBLIC_CHAT_URL: "https://{{ .Values.global.domain }}/chat"

# MCP Server configuration
mcpServer:
  enabled: true
  image:
    repository: "todo-mcp-server"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  service:
    type: ClusterIP
    port: 8080
  resources:
    limits:
      cpu: 400m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi
  env:
    DATABASE_URL: "postgresql://neon-db:5432/todo_db"
    KAFKA_BROKERS: "todo-chatbot-platform-kafka:9092"
  dapr:
    enabled: true
    appId: "todo-mcp-server"
    appPort: 8080
    appProtocol: "http"

# Ingress configuration
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "{{ .Values.global.tls.issuer }}"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60s"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60s"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60s"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
  hosts:
    - host: "{{ .Values.global.domain }}"
      paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: todo-chatbot-platform-frontend
              port:
                number: 3000
        - path: /api
          pathType: Prefix
          backend:
            service:
              name: todo-chatbot-platform-backend
              port:
                number: 8000
        - path: /chat
          pathType: Prefix
          backend:
            service:
              name: todo-chatbot-platform-mcp-server
              port:
                number: 8080
  tls:
    - secretName: todo-app-tls
      hosts:
        - "{{ .Values.global.domain }}"
```

## Dependency Management

### Chart Dependencies with Ordering
```yaml
# Chart.yaml with proper dependency ordering
dependencies:
  # Infrastructure components first
  - name: kafka
    version: ^2.0.0
    repository: https://charts.bitnami.com/bitnami
    condition: kafka.enabled
    # Kafka needs to be ready before services that depend on it

  - name: dapr
    version: ^1.11.0
    repository: https://dapr.github.io/helm-charts
    condition: dapr.enabled
    # Dapr operator needs to be ready before services with Dapr sidecars

  # Application services
  - name: todo-backend
    version: ~1.0.0
    repository: file://../todo-backend
    condition: backend.enabled
    # Backend depends on Kafka and Dapr being available

  - name: todo-mcp-server
    version: ~1.0.0
    repository: file://../todo-mcp-server
    condition: mcpServer.enabled
    # MCP server depends on Kafka and Dapr being available

  - name: todo-frontend
    version: ~1.0.0
    repository: file://../todo-frontend
    condition: frontend.enabled
    # Frontend can start after backend and MCP server

  # Ingress last
  - name: ingress-nginx
    version: ^4.0.0
    repository: https://kubernetes.github.io/ingress-nginx
    condition: ingress.enabled
    # Ingress needs all services to be available
```

## Kubernetes Manifests

### Init Job for Pre-deployment Checks
```yaml
# templates/pre-deployment-checks.yaml
{{- if .Values.preChecks.enabled }}
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "todo-chatbot-platform.fullname" . }}-pre-checks
  labels:
    {{- include "todo-chatbot-platform.labels" . | nindent 4 }}
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: kafka-check
        image: busybox:1.35
        command: ['sh', '-c', 'until nc -z {{ include "todo-chatbot-platform.kafka.fullname" . }} 9092; do sleep 2; done; echo "Kafka is ready"']
      - name: postgres-check
        image: busybox:1.35
        command: ['sh', '-c', 'until nc -z {{ .Values.database.host }} {{ .Values.database.port }}; do sleep 2; done; echo "PostgreSQL is ready"']
  backoffLimit: 10
{{- end }}
```

### Service Account and RBAC
```yaml
# templates/rbac.yaml
{{- if .Values.rbac.create }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "todo-chatbot-platform.serviceAccountName" . }}
  labels:
    {{- include "todo-chatbot-platform.labels" . | nindent 4 }}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: {{ include "todo-chatbot-platform.fullname" . }}-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints", "persistentvolumeclaims", "events", "configmaps", "secrets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "daemonsets", "replicasets", "statefulsets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: {{ include "todo-chatbot-platform.fullname" . }}-rolebinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: {{ include "todo-chatbot-platform.fullname" . }}-role
subjects:
- kind: ServiceAccount
  name: {{ include "todo-chatbot-platform.serviceAccountName" . }}
  namespace: {{ .Release.Namespace }}
{{- end }}
```

## Advanced Configuration Patterns

### Shared Secrets Management
```yaml
# templates/shared-secrets.yaml
{{- if .Values.secrets.create }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-chatbot-platform.fullname" . }}-shared-secrets
  labels:
    {{- include "todo-chatbot-platform.labels" . | nindent 4 }}
type: Opaque
data:
  {{- if .Values.database.password }}
  database-password: {{ .Values.database.password | b64enc }}
  {{- end }}
  {{- if .Values.kafka.auth.sasl.jaas.clientPasswords }}
  kafka-password: {{ .Values.kafka.auth.sasl.jaas.clientPasswords | first | b64enc }}
  {{- end }}
  {{- if .Values.openai.apiKey }}
  openai-api-key: {{ .Values.openai.apiKey | b64enc }}
  {{- end }}
---
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-chatbot-platform.fullname" . }}-jwt-secret
  labels:
    {{- include "todo-chatbot-platform.labels" . | nindent 4 }}
type: Opaque
data:
  jwt-secret: {{ .Values.auth.jwtSecret | default (randAlphaNum 32 | b64enc) }}
{{- end }}
```

### Custom Resource Definitions
```yaml
# templates/custom-resources.yaml
{{- if .Values.customResources.create }}
---
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: {{ include "todo-chatbot-platform.fullname" . }}-cluster
  labels:
    {{- include "todo-chatbot-platform.labels" . | nindent 4 }}
spec:
  kafka:
    version: 3.6.0
    replicas: {{ .Values.kafka.replicaCount }}
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      inter.broker.protocol.version: "3.6"
    storage:
      type: jbod
      volumes:
      - id: 0
        type: persistent-claim
        size: {{ .Values.kafka.storage.size }}
        class: {{ .Values.global.storageClass }}
        deleteClaim: false
    resources:
      {{- toYaml .Values.kafka.resources | nindent 6 }}
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 10Gi
      class: {{ .Values.global.storageClass }}
      deleteClaim: false
    resources:
      {{- toYaml .Values.zookeeper.resources | nindent 6 }}
  entityOperator:
    topicOperator: {}
    userOperator: {}
{{- end }}
```

## Deployment Scripts

### Helm Upgrade Script
```bash
#!/bin/bash
# deploy-platform.sh

set -e

CHART_DIR="${1:-.}"
NAMESPACE="${2:-todo-app}"
RELEASE_NAME="${3:-todo-chatbot-platform}"
VALUES_FILE="${4:-values.yaml}"

echo "Deploying Todo Chatbot Platform..."

# Add Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add dapr https://dapr.github.io/helm-charts
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Install/upgrade the platform
helm upgrade --install $RELEASE_NAME $CHART_DIR \
  --namespace $NAMESPACE \
  --values $VALUES_FILE \
  --timeout 20m \
  --atomic \
  --wait

echo "Platform deployed successfully!"

# Verify deployment
echo "Verifying deployment..."
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

echo "Deployment verification complete!"
```

### Canary Deployment Script
```bash
#!/bin/bash
# canary-deployment.sh

set -e

NAMESPACE="${1:-todo-app}"
CANARY_VALUES="${2:-values-canary.yaml}"
PRIMARY_RELEASE="todo-chatbot-platform-primary"
CANARY_RELEASE="todo-chatbot-platform-canary"

echo "Starting canary deployment..."

# Deploy canary version to 20% of traffic
helm upgrade --install $CANARY_RELEASE . \
  --namespace $NAMESPACE \
  --values $CANARY_VALUES \
  --set backend.replicaCount=1 \
  --set frontend.replicaCount=1 \
  --atomic \
  --wait

# Wait for canary pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-backend-canary -n $NAMESPACE --timeout=300s

# Run smoke tests against canary
echo "Running smoke tests on canary deployment..."
kubectl run smoke-test --image=curlimages/curl -it --rm --restart=Never \
  --namespace $NAMESPACE \
  -- curl -s -o /dev/null -w "%{http_code}" http://todo-chatbot-platform-backend-canary.$NAMESPACE:8000/health

SMOKE_TEST_RESULT=$?

if [ $SMOKE_TEST_RESULT -eq 0 ]; then
  echo "Smoke tests passed. Promoting canary to primary..."
  # Scale up canary to full capacity
  kubectl scale deployment todo-chatbot-platform-backend-canary -n $NAMESPACE --replicas=3
  kubectl scale deployment todo-chatbot-platform-frontend-canary -n $NAMESPACE --replicas=3

  # Switch traffic to canary (via service update or Istio if available)
  # Remove primary deployment after verification
  helm uninstall $PRIMARY_RELEASE --namespace $NAMESPACE
  # Rename canary to primary
  kubectl patch deployment todo-chatbot-platform-backend-canary -n $NAMESPACE -p '{"metadata":{"name":"todo-chatbot-platform-backend"}}'
else
  echo "Smoke tests failed. Rolling back canary deployment..."
  helm uninstall $CANARY_RELEASE --namespace $NAMESPACE
  exit 1
fi

echo "Canary deployment completed successfully!"
```

## Values Validation

### Schema Validation
```yaml
# values.schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "global": {
      "type": "object",
      "properties": {
        "domain": {
          "type": "string",
          "pattern": "^([a-z0-9]+(-[a-z0-9]+)*\\.)+[a-z]{2,}$"
        },
        "storageClass": {
          "type": "string"
        }
      },
      "required": ["domain"]
    },
    "kafka": {
      "type": "object",
      "properties": {
        "enabled": {
          "type": "boolean"
        },
        "replicaCount": {
          "type": "integer",
          "minimum": 1,
          "maximum": 10
        },
        "resources": {
          "type": "object",
          "properties": {
            "requests": {
              "type": "object",
              "properties": {
                "memory": {
                  "type": "string"
                },
                "cpu": {
                  "type": "string"
                }
              }
            },
            "limits": {
              "type": "object",
              "properties": {
                "memory": {
                  "type": "string"
                },
                "cpu": {
                  "type": "string"
                }
              }
            }
          }
        }
      }
    },
    "backend": {
      "type": "object",
      "properties": {
        "enabled": {
          "type": "boolean"
        },
        "image": {
          "type": "object",
          "properties": {
            "repository": {
              "type": "string"
            },
            "tag": {
              "type": "string"
            }
          }
        }
      }
    }
  },
  "required": ["global", "kafka", "backend"]
}
```

## Production-Ready Configuration

### Production Values
```yaml
# values-production.yaml
global:
  domain: "todo.yourdomain.com"
  tls:
    issuer: "letsencrypt-prod"

kafka:
  enabled: true
  replicaCount: 3
  resources:
    limits:
      cpu: 4000m
      memory: 16Gi
    requests:
      cpu: 2000m
      memory: 8Gi
  storage:
    size: 500Gi
  auth:
    sasl:
      jaas:
        clientPasswords:
          - "your-secure-kafka-password"

dapr:
  enabled: true
  global:
    tag: "1.11.0"
  controlPlane:
    resources:
      limits:
        cpu: 2000m
        memory: 2Gi
      requests:
        cpu: 500m
        memory: 512Mi

backend:
  enabled: true
  replicaCount: 3
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
  dapr:
    appId: "todo-backend-prod"

frontend:
  enabled: true
  replicaCount: 3
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi

mcpServer:
  enabled: true
  replicaCount: 2
  resources:
    limits:
      cpu: 800m
      memory: 1Gi
    requests:
      cpu: 400m
      memory: 512Mi

ingress:
  enabled: true
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
```

## Output Format

Generate Helm chart assemblies that include:
- Complete Chart.yaml with all dependencies and aliases
- Comprehensive values.yaml with all configurable parameters
- Kubernetes manifests for proper service ordering
- Deployment scripts with error handling and verification
- Validation schemas for configuration integrity
- Production-ready configurations with resource limits
- Security configurations for secrets and RBAC
- Documentation for installation and customization