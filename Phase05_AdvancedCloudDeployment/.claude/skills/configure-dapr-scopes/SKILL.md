---
name: configure-dapr-scopes
description: Defines Dapr scoped components and policies to restrict publish/subscribe access to authorized services/topics, preventing unauthorized event flows. Use when configuring Dapr scoping policies for secure service-to-service communication and topic access control.
---

# Configure Dapr Scopes

This skill helps define Dapr scoped components and policies to restrict publish/subscribe access to authorized services/topics, preventing unauthorized event flows and securing service-to-service communication.

## When to Use This Skill

Use this skill when:
- Securing Dapr pub/sub communications between services
- Implementing access control for specific topics
- Restricting service-to-service communication
- Preventing unauthorized event publishing/subscribing
- Implementing security policies for Dapr components
- Ensuring proper isolation between services

## Dapr Scoping Fundamentals

### Component Scoping Overview
Dapr scoping allows you to restrict which applications can use specific components. This is achieved through the `scopes` field in component definitions.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secure-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "dapr-user"
  - name: saslPassword
    value: "dapr-password"
  - name: saslMechanism
    value: "PLAIN"
  scopes:
  - todo-backend
  - todo-chatbot
  - todo-reminder
```

## Service-Specific Scoping

### Backend Service Scoping
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: backend-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "backend-user"
  - name: saslPassword
    value: "backend-password"
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "backend-consumer-group"
  scopes:
  - todo-backend
```

### Chatbot Service Scoping
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: chatbot-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "chatbot-user"
  - name: saslPassword
    value: "chatbot-password"
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "chatbot-consumer-group"
  scopes:
  - todo-chatbot
```

### Reminder Service Scoping
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: salsUsername
    value: "reminder-user"
  - name: saslPassword
    value: "reminder-password"
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "reminder-consumer-group"
  scopes:
  - todo-reminder
```

## Topic-Specific Scoping

### Task Events Topic Scoping
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-events-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "task-events-user"
  - name: saslPassword
    value: "task-events-password"
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "task-events-consumer-group"
  scopes:
  - todo-backend      # Can publish task events
  - todo-chatbot      # Can subscribe to task events
  - todo-reminder     # Can subscribe to task events for reminders
```

### User Events Topic Scoping
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: user-events-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "user-events-user"
  - name: saslPassword
    value: "user-events-password"
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "user-events-consumer-group"
  scopes:
  - todo-backend      # Can publish user events
  - todo-chatbot      # Can subscribe to user events
```

## Advanced Scoping Policies

### Multi-Tenant Scoping
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: tenant-isolated-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "tenant-isolated-user"
  - name: saslPassword
    value: "tenant-isolated-password"
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "tenant-isolated-consumer-group"
  scopes:
  - todo-backend-prod
  - todo-chatbot-prod
  - todo-reminder-prod
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: tenant-isolated-pubsub-staging
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "staging-user"
  - name: saslPassword
    value: "staging-password"
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "staging-consumer-group"
  scopes:
  - todo-backend-staging
  - todo-chatbot-staging
  - todo-reminder-staging
```

### Read-Write Scoping with Different Components
```yaml
# Write-only component for publishers
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-events-write
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "write-user"
  - name: saslPassword
    value: "write-password"
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "write-only-group"
  scopes:
  - todo-backend

---
# Read-only component for subscribers
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-events-read
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "read-user"
  - name: saslPassword
    value: "read-password"
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "read-only-group"
  scopes:
  - todo-chatbot
  - todo-reminder
```

## Security Scoping with Secrets

### Scoped Components with Secret Stores
```yaml
# Secret Store Component
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secure-secret-store
  namespace: todo-app
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
  scopes:
  - todo-backend
  - todo-chatbot
  - todo-reminder

---
# Pub/Sub Component using scoped secrets
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secret-scoped-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "scoped-user"
  - name: saslPassword
    secretKeyRef:
      name: kafka-secrets
      key: password
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  scopes:
  - todo-backend
```

## Namespace-Based Scoping

### Cross-Namespace Scoping
```yaml
# Backend in backend namespace
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: backend-pubsub
  namespace: backend
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  scopes:
  - todo-backend

---
# Chatbot in frontend namespace
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: chatbot-pubsub
  namespace: frontend
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  scopes:
  - todo-chatbot
```

## Service Identity Scoping

### Service Account Based Scoping
```yaml
# Dapr Configuration for service identity
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: service-identity-config
  namespace: todo-app
spec:
  accessControl:
    defaultAction: deny
    targets:
    - name: todo-backend
      rules:
      - name: allow-backend-to-task-events
        verb: publish
        operation: /v1.0/publish/task-events-pubsub/task.created
        type: allow
      - name: allow-backend-to-user-events
        verb: publish
        operation: /v1.0/publish/user-events-pubsub/user.login
        type: allow
    - name: todo-chatbot
      rules:
      - name: allow-chatbot-to-task-events
        verb: subscribe
        operation: /v1.0/topic/task-events-pubsub/task.created
        type: allow
      - name: allow-chatbot-to-user-events
        verb: subscribe
        operation: /v1.0/topic/user-events-pubsub/user.login
        type: allow
```

## Topic Filtering Scoping

### Topic-Specific Access Control
```yaml
# Component with restricted topics
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: filtered-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "filtered-user"
  - name: saslPassword
    value: "filtered-password"
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  # Topic-level filtering in metadata
  - name: allowedTopics
    value: "task.created,task.completed,user.login"
  scopes:
  - todo-backend
  - todo-chatbot
```

## Advanced Security Policies

### Complete Security Configuration
```yaml
# Secure pubsub with multiple security layers
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: enterprise-secure-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  # Connection settings
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9093"
  # Authentication
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "enterprise-user"
  - name: saslPassword
    secretKeyRef:
      name: enterprise-secrets
      key: kafka-password
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  # Encryption
  - name: enableTLS
    value: "true"
  # Consumer settings
  - name: consumerGroup
    value: "enterprise-consumer-group"
  # Performance settings
  - name: maxMessageBytes
    value: 2097152
  # Security settings
  - name: disableTls
    value: "false"
  - name: version
    value: "2.8.0"
  scopes:
  # Only specific services can access this component
  - todo-backend-enterprise
  - todo-chatbot-enterprise
  - todo-reminder-enterprise

---
# Dapr configuration for access control
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: enterprise-access-control
  namespace: todo-app
spec:
  accessControl:
    defaultAction: deny
    trustDomain: "todo-app-enterprise"
    targets:
    - name: todo-backend-enterprise
      defaultAction: allow
      policies:
      - appId: todo-backend-enterprise
        namespace: todo-app
        rules:
        - name: publish-task-events
          action: allow
          operations:
          - name: /v1.0/publish/enterprise-secure-pubsub/task.*
          httpVerb:
          - POST
    - name: todo-chatbot-enterprise
      defaultAction: allow
      policies:
      - appId: todo-chatbot-enterprise
        namespace: todo-app
        rules:
        - name: subscribe-task-events
          action: allow
          operations:
          - name: /v1.0/topic/enterprise-secure-pubsub/task.*
          httpVerb:
          - POST
```

## Scoping Best Practices

### Security-First Scoping Template
```yaml
# Template for secure component scoping
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secure-component-template
  namespace: todo-app
spec:
  type: pubsub.kafka  # Or other component type
  version: v1
  metadata:
  # Essential security settings
  - name: brokers
    value: "your-kafka-brokers:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "your-username"
  - name: saslPassword
    secretKeyRef:
      name: your-secret-name
      key: your-secret-key
  - name: saslMechanism
    value: "SCRAM-SHA-512"  # Or appropriate mechanism

  # Optional but recommended settings
  - name: enableTLS
    value: "true"
  - name: consumerGroup
    value: "your-consumer-group"
  - name: maxMessageBytes
    value: 1048576

  # CRITICAL: Define scopes to limit access
  scopes:
  # List ONLY the applications that should access this component
  - app-that-needs-access-1
  - app-that-needs-access-2
  # Do NOT include '*' or generic names
```

## Validation and Monitoring

### Scoping Validation Script
```bash
#!/bin/bash
# validate_dapr_scoping.sh

NAMESPACE="todo-app"

echo "Validating Dapr component scoping..."

# Get all Dapr components
COMPONENTS=$(kubectl get components.dapr.io -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')

for component in $COMPONENTS; do
  echo "Checking component: $component"

  # Get scopes for the component
  SCOPES=$(kubectl get component.dapr.io $component -n $NAMESPACE -o jsonpath='{.spec.scopes[*]}' 2>/dev/null)

  if [ -z "$SCOPES" ]; then
    echo "  ⚠️  WARNING: Component $component has no scopes defined (accessible by all apps)"
  else
    echo "  ✅ Component $component is scoped to: $SCOPES"
  fi

  # Check if '*' is in scopes (which is bad)
  if echo "$SCOPES" | grep -q '\*'; then
    echo "  🚨 CRITICAL: Component $component has wildcard scope"
  fi
done

echo "Scoping validation complete."
```

## Output Format

Generate Dapr component configurations with:
- Proper scoping to limit access to authorized services
- Security configurations for authentication and encryption
- Namespace-aware scoping when needed
- Service identity verification
- Access control policies
- Validation guidelines for security
- Documentation of scope limitations