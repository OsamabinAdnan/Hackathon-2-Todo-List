---
name: create-kagent-automation
description: Outputs kagent task definitions for automated ops (e.g., restart failed consumers, scale deployments on high latency, clean old Kafka offsets). Use when defining automated operational tasks for kagent to execute based on cluster conditions and metrics.
---

# Create kagent Automation

This skill helps create kagent task definitions for automated operational tasks that respond to cluster conditions and metrics, such as restarting failed consumers, scaling deployments on high latency, and cleaning old Kafka offsets.

## When to Use This Skill

Use this skill when:
- Defining automated operational tasks for kagent execution
- Creating self-healing mechanisms for cluster components
- Implementing auto-scaling based on performance metrics
- Setting up automated cleanup tasks
- Configuring automated remediation for common issues
- Building operational runbooks as automated tasks

## kagent Task Definition Structure

### Basic Task Template
```yaml
# kagent-task-template.yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: automated-task-name
  namespace: kagent-system
spec:
  description: "Description of the automated task"
  schedule: "cron expression for scheduled tasks (optional)"
  triggers:
    - type: "metric"
      condition: "metric_name > threshold"
      resource: "resource_selector"
  actions:
    - type: "kubectl"
      command: "kubectl command to execute"
      parameters:
        namespace: "target_namespace"
        resource: "resource_name"
  retryPolicy:
    maxRetries: 3
    backoff: "exponential"
    initialDelay: "30s"
  timeout: "5m"
  enabled: true
```

## Consumer Restart Automation

### Restart Failed Kafka Consumers
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: restart-failed-kafka-consumers
  namespace: kagent-system
spec:
  description: "Automatically restart Kafka consumers that have failed"
  triggers:
    - type: "metric"
      condition: "kafka_consumer_dead_letter_queue_messages > 10"
      resource: "app.kubernetes.io/name=kafka"
  actions:
    - type: "kubectl"
      command: "scale"
      parameters:
        resource: "deployment"
        name: "${resource_name}"
        replicas: 0
        namespace: "${resource_namespace}"
    - type: "delay"
      duration: "10s"
    - type: "kubectl"
      command: "scale"
      parameters:
        resource: "deployment"
        name: "${resource_name}"
        replicas: "${original_replicas}"
        namespace: "${resource_namespace}"
  retryPolicy:
    maxRetries: 3
    backoff: "exponential"
    initialDelay: "30s"
  timeout: "10m"
  enabled: true
```

### Restart Dapr Sidecars
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: restart-unhealthy-dapr-sidecars
  namespace: kagent-system
spec:
  description: "Restart Dapr sidecars that are not responding"
  triggers:
    - type: "health"
      condition: "dapr_sidecar_not_healthy"
      resource: "dapr.io/app-id=*"
  actions:
    - type: "kubectl"
      command: "rollout"
      subcommand: "restart"
      parameters:
        resource: "deployment"
        name: "${app_name}"
        namespace: "${app_namespace}"
  retryPolicy:
    maxRetries: 2
    backoff: "linear"
    initialDelay: "60s"
  timeout: "15m"
  enabled: true
```

## Auto-Scaling Automation

### Scale Deployment Based on CPU
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: scale-deployment-high-cpu
  namespace: kagent-system
spec:
  description: "Scale deployment when CPU usage is high"
  triggers:
    - type: "metric"
      condition: "cpu_usage_percent > 80"
      resource: "app=todo-backend"
      window: "5m"
  actions:
    - type: "kubectl"
      command: "patch"
      parameters:
        resource: "deployment"
        name: "todo-backend"
        namespace: "todo-app"
        patch: '{"spec":{"replicas":${current_replicas * 1.5}}}'
        patchType: "strategic-merge"
  postActions:
    - type: "kubectl"
      command: "get"
      parameters:
        resource: "hpa"
        name: "todo-backend-hpa"
        namespace: "todo-app"
        output: "status"
  retryPolicy:
    maxRetries: 1
    backoff: "none"
  timeout: "5m"
  enabled: true
```

### Scale Kafka Based on Message Lag
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: scale-kafka-on-lag
  namespace: kagent-system
spec:
  description: "Scale Kafka brokers when consumer lag is high"
  triggers:
    - type: "metric"
      condition: "kafka_consumer_lag > 10000"
      resource: "app.kubernetes.io/name=kafka"
      window: "10m"
  actions:
    - type: "kubectl"
      command: "patch"
      parameters:
        resource: "statefulset"
        name: "todokafka-cluster-kafka"
        namespace: "kafka"
        patch: '{"spec":{"replicas":${current_replicas + 1}}}'
        patchType: "strategic-merge"
  postActions:
    - type: "kubectl"
      command: "get"
      parameters:
        resource: "pod"
        labelSelector: "strimzi.io/name=todokafka-cluster-kafka"
        namespace: "kafka"
  retryPolicy:
    maxRetries: 2
    backoff: "exponential"
    initialDelay: "60s"
  timeout: "10m"
  enabled: true
```

## Cleanup Automation

### Clean Old Kafka Offsets
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: clean-old-kafka-offsets
  namespace: kagent-system
spec:
  description: "Clean up old Kafka consumer group offsets"
  schedule: "0 2 * * *"  # Daily at 2 AM
  actions:
    - type: "kubectl"
      command: "exec"
      parameters:
        resource: "pod"
        name: "todokafka-cluster-kafka-0"
        namespace: "kafka"
        container: "kafka"
        command: "bin/kafka-consumer-groups.sh"
        args: "--bootstrap-server localhost:9092 --list | xargs -I {} bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --delete --group {}"
  retryPolicy:
    maxRetries: 1
    backoff: "none"
  timeout: "30m"
  enabled: true
```

### Clean Expired Events
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: clean-expired-events
  namespace: kagent-system
spec:
  description: "Clean up expired events from event storage"
  schedule: "0 3 * * *"  # Daily at 3 AM
  actions:
    - type: "kubectl"
      command: "exec"
      parameters:
        resource: "pod"
        labelSelector: "app=todo-backend"
        namespace: "todo-app"
        container: "backend"
        command: "python"
        args: "scripts/cleanup_expired_events.py --older-than 7d"
  retryPolicy:
    maxRetries: 3
    backoff: "exponential"
    initialDelay: "60s"
  timeout: "15m"
  enabled: true
```

## Health Monitoring Automation

### Restart Unhealthy Pods
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: restart-unhealthy-pods
  namespace: kagent-system
spec:
  description: "Restart pods that are in CrashLoopBackOff or other unhealthy states"
  triggers:
    - type: "status"
      condition: "phase in (Failed, Unknown)"
      resource: "app=todo-*"
  actions:
    - type: "kubectl"
      command: "delete"
      parameters:
        resource: "pod"
        name: "${pod_name}"
        namespace: "${pod_namespace}"
        gracePeriodSeconds: 0
  postActions:
    - type: "delay"
      duration: "30s"
    - type: "kubectl"
      command: "get"
      parameters:
        resource: "pod"
        labelSelector: "app=${app_name}"
        namespace: "${pod_namespace}"
  retryPolicy:
    maxRetries: 2
    backoff: "linear"
    initialDelay: "120s"
  timeout: "5m"
  enabled: true
```

### Resource Cleanup
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: cleanup-unused-resources
  namespace: kagent-system
spec:
  description: "Clean up unused Kubernetes resources"
  schedule: "0 4 * * 0"  # Weekly on Sundays at 4 AM
  actions:
    - type: "kubectl"
      command: "get"
      parameters:
        resource: "pvc"
        allNamespaces: true
        output: "json"
        outputFormat: "custom-columns=NAME:.metadata.name,NAMESPACE:.metadata.namespace,STATUS:.status.phase"
    - type: "kubectl"
      command: "delete"
      parameters:
        resource: "pvc"
        labelSelector: "status=unused,ttl<24h"
        allNamespaces: true
        dryRun: false
  retryPolicy:
    maxRetries: 1
    backoff: "none"
  timeout: "20m"
  enabled: true
```

## Advanced Automation Patterns

### Conditional Scaling Based on Multiple Metrics
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: multi-metric-scaling
  namespace: kagent-system
spec:
  description: "Scale deployment based on multiple metrics (CPU, Memory, and Response Time)"
  triggers:
    - type: "composite"
      conditions:
        - metric: "cpu_usage_percent"
          condition: "> 75"
          resource: "app=todo-frontend"
        - metric: "memory_usage_percent"
          condition: "> 80"
          resource: "app=todo-frontend"
        - metric: "avg_response_time_ms"
          condition: "> 500"
          resource: "app=todo-frontend"
      operator: "and"
      window: "5m"
  actions:
    - type: "kubectl"
      command: "scale"
      parameters:
        resource: "deployment"
        name: "todo-frontend"
        namespace: "todo-app"
        replicas: "${current_replicas * 1.5 > max_replicas ? max_replicas : current_replicas * 1.5}"
  postActions:
    - type: "kubectl"
      command: "get"
      parameters:
        resource: "horizontalpodautoscaler"
        name: "todo-frontend-hpa"
        namespace: "todo-app"
  retryPolicy:
    maxRetries: 1
    backoff: "none"
  timeout: "5m"
  enabled: true
```

### Remediation Based on Log Patterns
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: log-pattern-remediation
  namespace: kagent-system
spec:
  description: "Take action based on specific log patterns"
  triggers:
    - type: "log"
      pattern: "Connection refused.*database"
      resource: "app=todo-backend"
      count: 5
      window: "1m"
  actions:
    - type: "kubectl"
      command: "get"
      parameters:
        resource: "service"
        name: "neon-db"
        namespace: "default"
        output: "yaml"
    - type: "kubectl"
      command: "exec"
      parameters:
        resource: "pod"
        name: "neon-db-pod"
        namespace: "default"
        command: "pg_isready"
    - type: "delay"
      duration: "30s"
    - type: "kubectl"
      command: "rollout"
      subcommand: "restart"
      parameters:
        resource: "deployment"
        name: "todo-backend"
        namespace: "todo-app"
  retryPolicy:
    maxRetries: 3
    backoff: "exponential"
    initialDelay: "60s"
  timeout: "10m"
  enabled: true
```

## Self-Healing Patterns

### Database Connection Recovery
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: database-connection-recovery
  namespace: kagent-system
spec:
  description: "Restart services when database connection issues are detected"
  triggers:
    - type: "log"
      pattern: "FATAL.*database.*connection"
      resource: "app=todo-backend"
      count: 3
      window: "2m"
  actions:
    - type: "kubectl"
      command: "get"
      parameters:
        resource: "secret"
        name: "db-connection"
        namespace: "todo-app"
        output: "yaml"
    - type: "kubectl"
      command: "exec"
      parameters:
        resource: "pod"
        labelSelector: "app=neon-db"
        namespace: "default"
        command: "pg_isready"
    - type: "delay"
      duration: "60s"
    - type: "kubectl"
      command: "rollout"
      subcommand: "restart"
      parameters:
        resource: "deployment"
        name: "todo-backend"
        namespace: "todo-app"
  postActions:
    - type: "delay"
      duration: "5m"
    - type: "kubectl"
      command: "logs"
      parameters:
        resource: "pod"
        labelSelector: "app=todo-backend"
        namespace: "todo-app"
        since: "5m"
        grep: "database.*connected"
  retryPolicy:
    maxRetries: 2
    backoff: "exponential"
    initialDelay: "120s"
  timeout: "15m"
  enabled: true
```

## Monitoring and Alerting

### Resource Quota Enforcement
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: resource-quota-enforcement
  namespace: kagent-system
spec:
  description: "Enforce resource quotas and clean up over-limit resources"
  triggers:
    - type: "metric"
      condition: "namespace_resource_usage_percent > 90"
      resource: "namespace=*"
  actions:
    - type: "kubectl"
      command: "get"
      parameters:
        resource: "pod"
        namespace: "${namespace_name}"
        output: "json"
    - type: "kubectl"
      command: "top"
      parameters:
        resource: "pod"
        namespace: "${namespace_name}"
    - type: "kubectl"
      command: "delete"
      parameters:
        resource: "pod"
        namespace: "${namespace_name}"
        labelSelector: "priority=low"
        dryRun: false
  retryPolicy:
    maxRetries: 1
    backoff: "none"
  timeout: "10m"
  enabled: true
```

## Task Scheduling and Coordination

### Coordinated Multi-Resource Actions
```yaml
apiVersion: kagent.io/v1
kind: Task
metadata:
  name: coordinated-maintenance
  namespace: kagent-system
spec:
  description: "Coordinated maintenance across multiple resources"
  schedule: "0 2 * * 6"  # Saturdays at 2 AM
  actions:
    - type: "kubectl"
      command: "scale"
      parameters:
        resource: "deployment"
        name: "todo-frontend"
        namespace: "todo-app"
        replicas: 0
    - type: "delay"
      duration: "30s"
    - type: "kubectl"
      command: "scale"
      parameters:
        resource: "deployment"
        name: "todo-backend"
        namespace: "todo-app"
        replicas: 0
    - type: "delay"
      duration: "60s"
    - type: "kubectl"
      command: "exec"
      parameters:
        resource: "pod"
        labelSelector: "app.kubernetes.io/name=kafka"
        namespace: "kafka"
        container: "kafka"
        command: "bin/kafka-topics.sh"
        args: "--bootstrap-server localhost:9092 --describe"
    - type: "kubectl"
      command: "scale"
      parameters:
        resource: "deployment"
        name: "todo-backend"
        namespace: "todo-app"
        replicas: 2
    - type: "delay"
      duration: "60s"
    - type: "kubectl"
      command: "scale"
      parameters:
        resource: "deployment"
        name: "todo-frontend"
        namespace: "todo-app"
        replicas: 2
  postActions:
    - type: "delay"
      duration: "5m"
    - type: "kubectl"
      command: "get"
      parameters:
        resource: "pods"
        namespace: "todo-app"
        output: "wide"
  retryPolicy:
    maxRetries: 1
    backoff: "none"
  timeout: "30m"
  enabled: true
```

## Output Format

Generate kagent task definitions that include:
- Proper trigger conditions based on metrics, logs, or schedules
- Appropriate action sequences with parameter substitution
- Retry policies and timeout configurations
- Pre and post-action validations
- Resource selectors and namespace specifications
- Conditional logic for complex scenarios
- Error handling and recovery procedures
- Documentation and description for each task
- Scheduling information for periodic tasks
- Integration with monitoring and alerting systems