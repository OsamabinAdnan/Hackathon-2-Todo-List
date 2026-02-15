---
name: generate-kubectl-ai-prompts
description: Translates natural language queries (e.g., "investigate delayed task reminders") into precise kubectl-ai commands for logs, pod status, Dapr metrics, Kafka lag, and event traces. Use when converting user queries into specific kubectl-ai commands for cluster diagnostics and troubleshooting.
---

# Generate kubectl-ai Prompts

This skill helps translate natural language queries into precise kubectl-ai commands for cluster diagnostics, troubleshooting, and monitoring of various components including logs, pod status, Dapr metrics, Kafka lag, and event traces.

## When to Use This Skill

Use this skill when:
- Translating user queries into specific kubectl-ai commands
- Performing cluster diagnostics and troubleshooting
- Investigating application performance issues
- Monitoring Dapr, Kafka, and other service metrics
- Retrieving logs and status information from Kubernetes resources
- Conducting root cause analysis for system issues

## Natural Language to kubectl-ai Command Translation

### Basic Query Patterns

#### Pod Status Investigation
**Natural Language**: "Check the status of all backend pods"
**kubectl-ai Command**:
```bash
kubectl-ai get pods -l app=todo-backend -o wide
```

**Natural Language**: "Show me the status of pods with errors"
**kubectl-ai Command**:
```bash
kubectl-ai get pods --field-selector=status.phase!=Running
```

#### Log Retrieval
**Natural Language**: "Get logs from the kafka broker pods"
**kubectl-ai Command**:
```bash
kubectl-ai logs -l app.kubernetes.io/name=kafka --tail=100
```

**Natural Language**: "Show me error logs from the backend service"
**kubectl-ai Command**:
```bash
kubectl-ai logs -l app=todo-backend --since=1h | grep -i error
```

#### Resource Utilization
**Natural Language**: "Check resource usage of all pods"
**kubectl-ai Command**:
```bash
kubectl-ai top pods
```

**Natural Language**: "Show memory usage of kafka pods"
**kubectl-ai Command**:
```bash
kubectl-ai top pods -l app.kubernetes.io/name=kafka --containers
```

## Dapr-Specific Commands

### Dapr Component Status
**Natural Language**: "Check the status of Dapr components"
**kubectl-ai Command**:
```bash
kubectl-ai get components.dapr.io -A
```

**Natural Language**: "Get Dapr sidecar logs for backend service"
**kubectl-ai Command**:
```bash
kubectl-ai logs -l app=todo-backend -c daprd
```

### Dapr Metrics and Tracing
**Natural Language**: "Show Dapr metrics for the backend service"
**kubectl-ai Command**:
```bash
kubectl-ai exec -it $(kubectl-ai get pods -l app=todo-backend -o jsonpath='{.items[0].metadata.name}') -- curl -s http://localhost:9090/metrics | grep dapr
```

**Natural Language**: "Check Dapr pubsub status"
**kubectl-ai Command**:
```bash
kubectl-ai get subscriptions.dapr.io -A
```

## Kafka-Specific Commands

### Kafka Brokers and Topics
**Natural Language**: "Check Kafka broker status"
**kubectl-ai Command**:
```bash
kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka
```

**Natural Language**: "Get Kafka topic details"
**kubectl-ai Command**:
```bash
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

### Kafka Consumer Lag
**Natural Language**: "Check consumer lag for task events topic"
**kubectl-ai Command**:
```bash
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group todo-backend-group
```

### Kafka Logs
**Natural Language**: "Get Kafka broker logs"
**kubectl-ai Command**:
```bash
kubectl-ai logs -l strimzi.io/name=todokafka-cluster-kafka --tail=100
```

## Event and Trace Investigation

### Event Trace Analysis
**Natural Language**: "Investigate delayed task reminders"
**kubectl-ai Commands**:
```bash
# Check reminder service logs
kubectl-ai logs -l app=todo-reminder --since=10m

# Check Kafka topic for reminder events
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic reminder.events --from-beginning --max-messages 10

# Check consumer group lag
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group reminder-consumer-group
```

## Advanced Diagnostic Commands

### Multi-Component Investigation
**Natural Language**: "Check why the chatbot service is not responding"
**kubectl-ai Commands**:
```bash
# Check pod status
kubectl-ai get pods -l app=todo-chatbot

# Check service endpoints
kubectl-ai get endpoints todo-chatbot-service

# Get application logs
kubectl-ai logs -l app=todo-chatbot --tail=50

# Check Dapr sidecar
kubectl-ai logs -l app=todo-chatbot -c daprd

# Check if Dapr is connected to Kafka
kubectl-ai exec -it $(kubectl-ai get pods -l app=todo-chatbot -o jsonpath='{.items[0].metadata.name}') -- curl -s http://localhost:3500/v1.0/healthz

# Check resource usage
kubectl-ai top pods -l app=todo-chatbot
```

### Performance Issue Investigation
**Natural Language**: "Investigate high latency in task creation"
**kubectl-ai Commands**:
```bash
# Check backend service performance
kubectl-ai top pods -l app=todo-backend

# Get detailed logs for task creation
kubectl-ai logs -l app=todo-backend --since=5m | grep -i "task.created\|POST.*tasks"

# Check Kafka topic for task events
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic task.events

# Check Dapr pubsub metrics
kubectl-ai exec -it $(kubectl-ai get pods -l app=todo-backend -o jsonpath='{.items[0].metadata.name}') -- curl -s http://localhost:9090/metrics | grep dapr_io_pubsub_sent

# Check for resource contention
kubectl-ai describe nodes
```

## System Health Monitoring

### Cluster-Wide Health Check
**Natural Language**: "Perform a cluster health check"
**kubectl-ai Commands**:
```bash
# Check all pods status
kubectl-ai get pods --all-namespaces --field-selector=status.phase!=Running

# Check node status
kubectl-ai get nodes

# Check system pods
kubectl-ai get pods -n kube-system

# Check events
kubectl-ai get events --all-namespaces --sort-by='.lastTimestamp'

# Check resource quotas
kubectl-ai get resourcequota --all-namespaces
```

### Application-Specific Health Check
**Natural Language**: "Check health of the todo application stack"
**kubectl-ai Commands**:
```bash
# Check all todo app pods
kubectl-ai get pods -n todo-app

# Check all todo app services
kubectl-ai get services -n todo-app

# Check ingress status
kubectl-ai get ingress -n todo-app

# Check all todo app deployments
kubectl-ai get deployments -n todo-app

# Check all todo app configmaps and secrets
kubectl-ai get configmaps,secrets -n todo-app
```

## Troubleshooting Scenarios

### Common Application Issues
**Natural Language**: "Application is throwing 500 errors"
**kubectl-ai Commands**:
```bash
# Check for crash loops
kubectl-ai get pods -n todo-app -o json | jq '.items[] | select(.status.containerStatuses[]?.restartCount > 5) | .metadata.name'

# Get recent logs
kubectl-ai logs -n todo-app --since=10m --all-containers=true

# Check resource limits
kubectl-ai describe pods -n todo-app

# Check service endpoints
kubectl-ai get endpoints -n todo-app
```

### Network Connectivity Issues
**Natural Language**: "Services can't connect to each other"
**kubectl-ai Commands**:
```bash
# Check network policies
kubectl-ai get networkpolicies -A

# Check service discovery
kubectl-ai get svc -n todo-app

# Check DNS resolution
kubectl-ai run debug --image=nicolaka/netshoot -it --rm --restart=Never --overrides='{"spec":{"hostNetwork": true}}' -- nslookup todo-backend-service.todo-app.svc.cluster.local

# Check endpoints
kubectl-ai get endpoints -n todo-app
```

## Advanced kubectl-ai Patterns

### Conditional and Complex Queries
**Natural Language**: "Show me pods that restarted more than 10 times in the last hour"
**kubectl-ai Command**:
```bash
kubectl-ai get pods --all-namespaces -o json | jq -r '.items[] | select(.status.containerStatuses[]?.restartCount > 10) | "\(.metadata.namespace)/\(.metadata.name) Restart Count: \(.status.containerStatuses[]?.restartCount)"'
```

**Natural Language**: "Find pods with high CPU usage"
**kubectl-ai Command**:
```bash
kubectl-ai top pods --all-namespaces | awk 'NR>1 {if($3 != "<unknown>") {cpu=$3; gsub(/mi$/, "", cpu); if(cpu > 500) print $0}}'
```

### Event Correlation
**Natural Language**: "Correlate pod restarts with error logs"
**kubectl-ai Commands**:
```bash
# Get events for pod restarts
kubectl-ai get events --all-namespaces --field-selector=reason=BackOff --sort-by='.lastTimestamp'

# Get logs around the same time
kubectl-ai logs --since=10m --all-containers=true -n todo-app
```

## Output Format

Generate kubectl-ai commands that:
- Translate natural language queries into specific kubectl-ai commands
- Include appropriate selectors (-l, -n) for targeted queries
- Provide both simple and complex command patterns
- Include diagnostic commands for different system components
- Offer troubleshooting workflows for common issues
- Incorporate advanced filtering and formatting options
- Provide context-aware command suggestions
- Include error handling and validation commands