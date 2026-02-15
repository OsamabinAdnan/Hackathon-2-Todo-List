---
name: generate-dapr-pubsub-component
description: Outputs Dapr Component YAML for Kafka pub/sub type, specifying bootstrap servers, topics, consumer groups, authentication, and retry policies. Use when configuring Dapr pub/sub components for Kafka integration with proper authentication and reliability settings.
---

# Generate Dapr Pub/Sub Component

This skill helps generate Dapr Component YAML configurations for Kafka pub/sub integration, specifying bootstrap servers, topics, consumer groups, authentication, and retry policies.

## When to Use This Skill

Use this skill when:
- Setting up Dapr pub/sub integration with Apache Kafka
- Configuring Kafka components for microservice communication
- Defining authentication and security settings for Kafka
- Configuring retry policies and error handling
- Setting up consumer groups for event processing

## Component Configuration Structure

### Basic Kafka Pub/Sub Component
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  # Kafka broker configuration
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  # Topic configuration
  - name: consumerGroup
    value: "dapr-consumer-group"
  # Authentication settings
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "dapr-user"
  - name: saslPassword
    value: "dapr-password"
  - name: saslMechanism
    value: "PLAIN"
  # TLS/SSL configuration
  - name: maxMessageBytes
    value: 1024
  - name: consumeRetryInterval
    value: 200ms
```

## Authentication Methods

### SASL/PLAIN Authentication
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-sasl-plain-pubsub
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
  - name: consumerGroup
    value: "todo-app-group"
  - name: maxMessageBytes
    value: 1024
  - name: consumeRetryInterval
    value: 200ms
```

### SASL/SCRAM Authentication
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-sasl-scram-pubsub
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
    value: "SCRAM-SHA-256"
  - name: consumerGroup
    value: "todo-app-group"
  - name: maxMessageBytes
    value: 1024
  - name: consumeRetryInterval
    value: 200ms
```

### SSL/TLS Authentication
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-ssl-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9093"
  - name: authRequired
    value: "true"
  - name: enableTLS
    value: "true"
  - name: saslUsername
    value: "dapr-user"
  - name: saslPassword
    value: "dapr-password"
  - name: saslMechanism
    value: "PLAIN"
  - name: caCert
    value: |
      -----BEGIN CERTIFICATE-----
      ...certificate content...
      -----END CERTIFICATE-----
  - name: clientCert
    value: |
      -----BEGIN CERTIFICATE-----
      ...certificate content...
      -----END CERTIFICATE-----
  - name: clientKey
    value: |
      -----BEGIN RSA PRIVATE KEY-----
      ...key content...
      -----END RSA PRIVATE KEY-----
  - name: consumerGroup
    value: "todo-app-group"
  - name: maxMessageBytes
    value: 1024
  - name: consumeRetryInterval
    value: 200ms
```

## Topic-Specific Configuration

### Topic Metadata Configuration
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-topic-specific-pubsub
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
    value: "${secretStore.secretName.username}"
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "todo-app-group"
  - name: disableTls
    value: "false"
  - name: maxMessageBytes
    value: 2048
  - name: consumeRetryInterval
    value: 500ms
  - name: publishRetryInterval
    value: 1000ms
  - name: version
    value: "2.1.1"
  - name: metadata
    value: |
      {
        "request.timeout.ms": "30000",
        "delivery.timeout.ms": "60000",
        "acks": "all",
        "retries": "3",
        "batch.num.messages": "10000",
        "batch.size": "16384"
      }
```

## Consumer Group Configuration

### Multiple Consumer Groups
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-multi-consumer-pubsub
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
  - name: consumerGroup
    value: "todo-app-group"
  # Additional consumer configuration
  - name: consumerConfig
    value: |
      {
        "max.poll.records": "100",
        "max.poll.interval.ms": "300000",
        "session.timeout.ms": "10000",
        "heartbeat.interval.ms": "3000",
        "enable.auto.commit": "true",
        "auto.commit.interval.ms": "5000",
        "auto.offset.reset": "latest"
      }
  - name: publishConfig
    value: |
      {
        "request.timeout.ms": "30000",
        "delivery.timeout.ms": "60000",
        "acks": "all",
        "retries": "3",
        "compression.type": "snappy",
        "batch.size": "16384",
        "linger.ms": "5"
      }
```

## Retry and Error Handling Configuration

### Advanced Retry Policies
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-advanced-retry-pubsub
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
  - name: consumerGroup
    value: "todo-app-group"
  # Retry configuration
  - name: publishRetryInterval
    value: 1000ms
  - name: publishRetryThreshold
    value: 3
  - name: consumeRetryInterval
    value: 200ms
  - name: consumeRetryThreshold
    value: 5
  # Error handling
  - name: errorHandling
    value: |
      {
        "deadLetterQueue": {
          "topic": "dapr-errors",
          "partition": 0
        },
        "retryPolicy": {
          "maxRetries": 3,
          "backoffMultiplier": 2,
          "initialDelay": "1s",
          "maxDelay": "30s"
        }
      }
  - name: maxMessageBytes
    value: 1048576
```

## Production-Ready Configuration

### Production Kafka Component
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-production-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  # Kafka cluster configuration
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  # Authentication and security
  - name: authRequired
    value: "true"
  - name: saslUsername
    value: "dapr-user"
  - name: saslPassword
    secretKeyRef:
      name: kafka-secrets
      key: saslPassword
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "todo-app-production-group"
  # Performance settings
  - name: maxMessageBytes
    value: 2097152  # 2MB
  - name: consumeRetryInterval
    value: 500ms
  - name: publishRetryInterval
    value: 1000ms
  # TLS/SSL settings
  - name: enableTLS
    value: "true"
  # Topic configuration
  - name: disableTls
    value: "false"
  # Version compatibility
  - name: version
    value: "2.8.0"
  # Advanced configuration
  - name: metadata
    value: |
      {
        "request.timeout.ms": "30000",
        "delivery.timeout.ms": "120000",
        "acks": "all",
        "retries": "2147483647",
        "max.in.flight.requests.per.connection": "1",
        "enable.idempotence": "true",
        "batch.size": "16384",
        "linger.ms": "5",
        "compression.type": "snappy"
      }
```

## Secret Management

### Using Kubernetes Secrets
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-secret-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap:9092"
  - name: authRequired
    value: "true"
  - name: saslUsername
    secretKeyRef:
      name: kafka-auth
      key: username
  - name: saslPassword
    secretKeyRef:
      name: kafka-auth
      key: password
  - name: saslMechanism
    value: "SCRAM-SHA-512"
  - name: consumerGroup
    value: "todo-app-secure-group"
  - name: maxMessageBytes
    value: 1024
  - name: consumeRetryInterval
    value: 200ms
```

## Output Format

Generate Dapr Component YAML with:
- Proper authentication settings for the target environment
- Appropriate consumer group configuration
- Retry policies and error handling
- Security configurations (TLS/SSL, SASL)
- Performance tuning parameters
- Secret management for sensitive information
- Proper metadata for production use