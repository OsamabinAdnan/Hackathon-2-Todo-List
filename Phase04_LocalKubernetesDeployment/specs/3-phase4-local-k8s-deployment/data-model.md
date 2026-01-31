# Data Model: Phase IV: Local Kubernetes Deployment

## Kubernetes Resource Models

### Deployment Entity
- **Name**: String (e.g., "frontend", "backend", "mcp-server")
- **Image**: String (e.g., "todo-frontend:latest", "todo-backend:latest")
- **Replicas**: Integer (default: 1, scalable)
- **Resources**: Object (requests/limits for CPU/Memory)
- **Environment**: Array of key-value pairs (configurable via values.yaml)
- **Ports**: Array of port mappings (containerPort, servicePort)
- **Health Checks**: Object (readiness/liveness probes)

### Service Entity
- **Name**: String (corresponds to deployment)
- **Type**: String ("ClusterIP", "NodePort", "LoadBalancer")
- **Selector**: Object (labels to match deployment)
- **Ports**: Array of port mappings (port, targetPort, protocol)

### ConfigMap Entity
- **Name**: String (e.g., "todo-app-config")
- **Data**: Object (key-value pairs for non-sensitive configuration)
- **Labels**: Object (metadata for organization)

### Secret Entity
- **Name**: String (e.g., "todo-app-secrets")
- **Data**: Object (base64 encoded sensitive values)
- **Type**: String ("Opaque", "kubernetes.io/dockerconfigjson")

### Ingress Entity
- **Name**: String (e.g., "todo-app-ingress")
- **Hosts**: Array of hostnames
- **Paths**: Array of path mappings (path, serviceName, servicePort)
- **TLS**: Array of TLS configurations

### Helm Chart Entity
- **Name**: String (e.g., "todo-chatbot")
- **Version**: String (semantic versioning)
- **Description**: String (purpose of the chart)
- **Maintainers**: Array of maintainer objects
- **Dependencies**: Array of chart dependencies
- **Values**: Object (default configuration values)

### Values Configuration Entity
- **Global**: Object (global configuration parameters)
- **Frontend**: Object (frontend-specific configuration)
  - replicaCount: Integer
  - image: Object (repository, tag, pullPolicy)
  - service: Object (type, port)
  - resources: Object (requests/limits)
- **Backend**: Object (backend-specific configuration)
  - replicaCount: Integer
  - image: Object (repository, tag, pullPolicy)
  - service: Object (type, port)
  - resources: Object (requests/limits)
  - config: Object (database URL, JWT settings)
- **MCP Server**: Object (MCP server-specific configuration)
  - replicaCount: Integer
  - image: Object (repository, tag, pullPolicy)
  - service: Object (type, port)
  - resources: Object (requests/limits)

## Relationships
- Deployment ←→ Service (one-to-many via selectors)
- ConfigMap → Deployment (referenced via volume mounts)
- Secret → Deployment (referenced via environment variables or volume mounts)
- Ingress → Service (routes traffic to services)
- Helm Chart ⊃ Values (chart contains default values)

## Validation Rules
- Deployment name must be unique within namespace
- Service ports must not conflict with other services
- Secret values must be base64 encoded
- Image repository and tag must be valid Docker image references
- Resource requests must not exceed limits
- Ingress paths must be unique within host

## State Transitions
- Deployment: Pending → Running → Terminated (lifecycle managed by Kubernetes)
- Pod: Pending → Running → Succeeded/Failed (based on container execution)
- Service: Created → Active → Deleted (network endpoint lifecycle)