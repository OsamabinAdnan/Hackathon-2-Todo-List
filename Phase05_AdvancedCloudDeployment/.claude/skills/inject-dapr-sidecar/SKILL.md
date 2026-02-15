---
name: inject-dapr-sidecar
description: Produces Kubernetes Deployment annotations and patches (dapr.io/enabled, dapr.io/app-id, dapr.io/app-port, dapr.io/sidecar-image) for all Todo services (backend, chatbot, reminder). Use when configuring Dapr sidecar injection for Todo application services in Kubernetes.
---

# Inject Dapr Sidecar

This skill helps generate Kubernetes Deployment configurations with proper Dapr sidecar annotations and patches for Todo application services including backend, chatbot, and reminder services.

## When to Use This Skill

Use this skill when:
- Adding Dapr sidecar injection to existing Kubernetes deployments
- Configuring Dapr for microservices in Todo application
- Setting up service-to-service communication via Dapr
- Enabling pub/sub patterns with Dapr sidecar
- Securing service communication with Dapr

## Basic Dapr Sidecar Annotations

### Minimal Dapr Annotations
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app: todo-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        - name: DAPR_GRPC_PORT
          value: "50001"
```

## Dapr Configuration for Different Services

### Backend Service with Dapr
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  namespace: todo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/app-protocol: "http"
        dapr.io/app-max-concurrency: "10"
        dapr.io/config: "dapr-config"
        dapr.io/log-level: "info"
        dapr.io/sidecar-cpu-limit: "0.5"
        dapr.io/sidecar-cpu-request: "0.1"
        dapr.io/sidecar-memory-limit: "512Mi"
        dapr.io/sidecar-memory-request: "256Mi"
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: auth-secret
              key: jwt_secret
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      imagePullSecrets:
      - name: regcred
```

### Chatbot Service with Dapr
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-chatbot
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-chatbot
  template:
    metadata:
      labels:
        app: todo-chatbot
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-chatbot"
        dapr.io/app-port: "3000"
        dapr.io/app-protocol: "http"
        dapr.io/app-max-concurrency: "5"
        dapr.io/config: "dapr-config"
        dapr.io/log-level: "debug"
        dapr.io/sidecar-cpu-limit: "0.75"
        dapr.io/sidecar-cpu-request: "0.25"
        dapr.io/sidecar-memory-limit: "768Mi"
        dapr.io/sidecar-memory-request: "384Mi"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
      - name: chatbot
        image: todo-chatbot:latest
        ports:
        - containerPort: 3000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api_key
        - name: MCP_SERVER_URL
          value: "http://mcp-server:8080"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Reminder Service with Dapr
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-reminder
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-reminder
  template:
    metadata:
      labels:
        app: todo-reminder
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-reminder"
        dapr.io/app-port: "8080"
        dapr.io/app-protocol: "http"
        dapr.io/app-max-concurrency: "1"
        dapr.io/config: "dapr-config"
        dapr.io/log-level: "info"
        dapr.io/sidecar-cpu-limit: "0.25"
        dapr.io/sidecar-cpu-request: "0.1"
        dapr.io/sidecar-memory-limit: "256Mi"
        dapr.io/sidecar-memory-request: "128Mi"
        dapr.io/enable-metrics: "true"
        dapr.io/metrics-port: "9090"
    spec:
      containers:
      - name: reminder
        image: todo-reminder:latest
        ports:
        - containerPort: 8080
        - containerPort: 9090
        env:
        - name: SCHEDULER_INTERVAL
          value: "60"
        - name: NOTIFICATION_SERVICE_URL
          value: "http://notification-service:8080"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

## Advanced Dapr Configuration

### Custom Dapr Sidecar Image
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend-custom-sidecar
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend-custom-sidecar
  template:
    metadata:
      labels:
        app: todo-backend-custom-sidecar
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend-custom"
        dapr.io/app-port: "8000"
        dapr.io/app-protocol: "http"
        dapr.io/sidecar-image: "daprio/daprd:edge"
        dapr.io/sidecar-registry: "docker.io"
        dapr.io/sidecar-cpu-limit: "0.5"
        dapr.io/sidecar-cpu-request: "0.1"
        dapr.io/sidecar-memory-limit: "512Mi"
        dapr.io/sidecar-memory-request: "256Mi"
        dapr.io/enable-profiling: "true"
        dapr.io/profile-port: "7777"
        dapr.io/disable-builtin-k8s-secret-store: "false"
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Dapr with Health Checks
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend-health
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend-health
  template:
    metadata:
      labels:
        app: todo-backend-health
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend-health"
        dapr.io/app-port: "8000"
        dapr.io/app-protocol: "http"
        dapr.io/enable-metrics: "true"
        dapr.io/metrics-port: "9090"
        dapr.io/enable-api-logging: "true"
        dapr.io/log-as-json: "true"
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        - containerPort: 9090
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
        startupProbe:
          httpGet:
            path: /startup
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          failureThreshold: 30
        env:
        - name: DAPR_HTTP_ENDPOINT
          value: "http://localhost:3500"
        - name: DAPR_GRPC_ENDPOINT
          value: "http://localhost:50001"
```

## Dapr Configuration with Security

### Secure Dapr Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend-secure
  namespace: todo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend-secure
  template:
    metadata:
      labels:
        app: todo-backend-secure
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend-secure"
        dapr.io/app-port: "8000"
        dapr.io/app-protocol: "http"
        dapr.io/app-ssl: "true"
        dapr.io/config: "secure-dapr-config"
        dapr.io/enable-mtls: "true"
        dapr.io/sidecar-cpu-limit: "0.5"
        dapr.io/sidecar-cpu-request: "0.1"
        dapr.io/sidecar-memory-limit: "512Mi"
        dapr.io/sidecar-memory-request: "256Mi"
        dapr.io/allowed-outbound-hosts: "api.example.com,db.example.com"
    spec:
      serviceAccountName: todo-backend-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: secure-db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: secrets
          mountPath: /etc/secrets
          readOnly: true
      volumes:
      - name: secrets
        secret:
          secretName: app-secrets
```

## Dapr Service Configuration

### Service for Dapr-enabled Application
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend-service
  labels:
    app: todo-backend
spec:
  selector:
    app: todo-backend
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 8000
  - name: dapr-http
    protocol: TCP
    port: 3500
    targetPort: 3500
  - name: dapr-grpc
    protocol: TCP
    port: 50001
    targetPort: 50001
  type: ClusterIP
```

## Patching Existing Deployments

### Strategic Merge Patch for Dapr Injection
```yaml
# patch-dapr.yaml
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend-patched"
        dapr.io/app-port: "8000"
        dapr.io/app-protocol: "http"
        dapr.io/config: "dapr-config"
```

Apply with:
```bash
kubectl patch deployment todo-backend -p "$(cat patch-dapr.yaml)"
```

### JSON Merge Patch for Dapr Injection
```json
{
  "spec": {
    "template": {
      "metadata": {
        "annotations": {
          "dapr.io/enabled": "true",
          "dapr.io/app-id": "todo-backend-json-patch",
          "dapr.io/app-port": "8000",
          "dapr.io/app-protocol": "http"
        }
      }
    }
  }
}
```

## Multi-Service Dapr Configuration

### Complete Todo App Dapr Setup
```yaml
---
# Backend Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/app-protocol: "http"
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000

---
# Chatbot Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-chatbot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-chatbot
  template:
    metadata:
      labels:
        app: todo-chatbot
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-chatbot"
        dapr.io/app-port: "3000"
        dapr.io/app-protocol: "http"
    spec:
      containers:
      - name: chatbot
        image: todo-chatbot:latest
        ports:
        - containerPort: 3000

---
# Reminder Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-reminder
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-reminder
  template:
    metadata:
      labels:
        app: todo-reminder
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-reminder"
        dapr.io/app-port: "8080"
        dapr.io/app-protocol: "http"
    spec:
      containers:
      - name: reminder
        image: todo-reminder:latest
        ports:
        - containerPort: 8080
```

## Output Format

Generate Kubernetes Deployment configurations with:
- Proper Dapr annotations for each service
- Appropriate resource limits for Dapr sidecar
- Security configurations where needed
- Health check configurations
- Environment variables for Dapr endpoints
- Complete service setup for Dapr-enabled applications