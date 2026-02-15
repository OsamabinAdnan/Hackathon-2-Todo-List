---
name: create-kafka-topics
description: Generates KafkaTopic CRDs (Strimzi) or topic creation scripts defining partitions, replication factor, retention, and compaction per Todo event type. Use when creating Kafka topics for Todo application events with appropriate partitioning and retention policies.
---

# Create Kafka Topics

This skill helps generate Kafka topic configurations for Todo application events using either Strimzi KafkaTopic CRDs or traditional topic creation scripts with appropriate settings for partitioning, replication, retention, and compaction.

## When to Use This Skill

Use this skill when:
- Creating Kafka topics for Todo application events
- Configuring topic partitioning based on expected throughput
- Setting up retention policies for different event types
- Implementing log compaction for entity state topics
- Managing topic lifecycle in event-driven architectures

## Topic Classification

### High-Throughput Topics
- **task.events**: Task lifecycle events (created, updated, completed, deleted)
- **user.activity**: User interaction events
- **system.metrics**: System performance and monitoring events

### State-Change Topics
- **task.state**: Current state of tasks with log compaction
- **user.profile**: User profile changes with log compaction
- **settings.changes**: Configuration changes with log compaction

### Audit/Log Topics
- **audit.log**: System audit trail
- **error.events**: Error and exception events
- **security.events**: Security-related events

## Strimzi KafkaTopic CRD Examples

### Task Events Topic
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-task-events
  labels:
    strimzi.io/cluster: todo-kafka-cluster
spec:
  partitions: 6
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824  # 1GB
    cleanup.policy: delete
    min.insync.replicas: 2
    max.message.bytes: 1048588  # 1MB
```

### User Activity Topic
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-user-activity
  labels:
    strimzi.io/cluster: todo-kafka-cluster
spec:
  partitions: 4
  replicas: 3
  config:
    retention.ms: 2592000000  # 30 days
    segment.bytes: 1073741824  # 1GB
    cleanup.policy: delete
    min.insync.replicas: 2
    max.message.bytes: 1048588  # 1MB
```

### Task State Topic (with compaction)
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-task-state
  labels:
    strimzi.io/cluster: todo-kafka-cluster
spec:
  partitions: 6
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824  # 1GB
    cleanup.policy: compact,delete
    min.cleanable.dirty.ratio: 0.1
    delete.retention.ms: 86400000  # 1 day
    min.insync.replicas: 2
    max.message.bytes: 1048588  # 1MB
```

## Topic Configuration Guidelines

### Partitioning Strategy
- **High-throughput topics**: 6-12 partitions
- **Medium-throughput topics**: 3-6 partitions
- **Low-throughput topics**: 1-3 partitions
- **Consider**: Consumer group size and parallel processing needs

### Replication Factor
- **Production**: Always use 3 replicas for durability
- **Development**: 1-2 replicas may be sufficient
- **Critical topics**: Consider 5 replicas for maximum durability

### Retention Policies
- **Real-time events**: 1-7 days
- **Analytics events**: 30-90 days
- **Audit events**: 1-7 years (regulatory compliance)
- **Temporary events**: 1 hour - 1 day

### Cleanup Policies
- **Delete**: For time-series data that expires
- **Compact**: For entity state updates
- **Compact + Delete**: For state with TTL

## Topic Creation Script (Alternative Approach)

### Using kafka-topics.sh
```bash
#!/bin/bash

# Task events topic
kafka-topics.sh --create \
  --topic todo-task-events \
  --bootstrap-server $BOOTSTRAP_SERVER \
  --partitions 6 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config cleanup.policy=delete \
  --config min.insync.replicas=2

# User activity topic
kafka-topics.sh --create \
  --topic todo-user-activity \
  --bootstrap-server $BOOTSTRAP_SERVER \
  --partitions 4 \
  --replication-factor 3 \
  --config retention.ms=2592000000 \
  --config cleanup.policy=delete \
  --config min.insync.replicas=2

# Task state topic (with compaction)
kafka-topics.sh --create \
  --topic todo-task-state \
  --bootstrap-server $BOOTSTRAP_SERVER \
  --partitions 6 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config cleanup.policy=compact,delete \
  --config min.cleanable.dirty.ratio=0.1 \
  --config delete.retention.ms=86400000 \
  --config min.insync.replicas=2
```

### Using Kafka Admin Client (Python)
```python
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

def create_todo_topics():
    admin_client = KafkaAdminClient(
        bootstrap_servers=['broker1:9092', 'broker2:9092', 'broker3:9092']
    )

    topics = [
        NewTopic(
            name='todo-task-events',
            num_partitions=6,
            replication_factor=3,
            topic_configs={
                'retention.ms': '604800000',  # 7 days
                'cleanup.policy': 'delete',
                'min.insync.replicas': '2'
            }
        ),
        NewTopic(
            name='todo-user-activity',
            num_partitions=4,
            replication_factor=3,
            topic_configs={
                'retention.ms': '2592000000',  # 30 days
                'cleanup.policy': 'delete',
                'min.insync.replicas': '2'
            }
        ),
        NewTopic(
            name='todo-task-state',
            num_partitions=6,
            replication_factor=3,
            topic_configs={
                'retention.ms': '604800000',  # 7 days
                'cleanup.policy': 'compact,delete',
                'min.cleanable.dirty.ratio': '0.1',
                'delete.retention.ms': '86400000'  # 1 day
            }
        )
    ]

    try:
        admin_client.create_topics(topics, validate_only=False)
        print("Topics created successfully")
    except TopicAlreadyExistsError:
        print("Topics already exist")
    finally:
        admin_client.close()
```

## Topic Naming Convention

### Format
`<domain>-<subdomain>-<entity>-<action>`

### Examples
- `todo-task-events` - Task lifecycle events
- `todo-user-profile` - User profile updates
- `todo-analytics-raw` - Raw analytics data
- `todo-notifications-outbound` - Outbound notifications

## Performance Considerations

### Throughput Planning
- Calculate expected messages per second
- Plan partitions based on consumer parallelism
- Consider message size for bandwidth calculations

### Storage Planning
- Estimate daily data volume
- Account for replication factor
- Plan for retention periods

## Output Format

Generate either:
1. **Strimzi KafkaTopic CRDs** - Kubernetes manifests for declarative topic management
2. **Topic creation scripts** - Command-line or programmatic topic creation
3. **Configuration documentation** - Detailed topic specifications with rationale

Include:
- Appropriate partition counts based on throughput
- Correct replication factors for durability
- Proper retention and cleanup policies
- Justification for configuration choices