---
name: generate-kafka-helm-values
description: Outputs customized values.yaml for Strimzi or Bitnami Kafka Helm charts, including replica count, storage class, security (SASL/SSL), resource limits, and DOKS-specific settings. Use when configuring Kafka deployments on DigitalOcean Kubernetes Service with appropriate security and resource settings.
---

# Generate Kafka Helm Values

This skill helps generate customized values.yaml files for Kafka Helm charts (Strimzi or Bitnami) with appropriate configurations for DigitalOcean Kubernetes Service.

## When to Use This Skill

Use this skill when:
- Deploying Kafka to DigitalOcean Kubernetes Service (DOKS)
- Configuring Kafka clusters with appropriate security settings
- Setting up resource limits and storage configurations
- Customizing Kafka for specific workload requirements
- Integrating Kafka with existing infrastructure

## Configuration Parameters

### Cluster Configuration
- **Replica Count**: Number of Kafka brokers for availability
- **Zookeeper**: Number of Zookeeper nodes (typically 3 for production)
- **Listeners**: Internal and external listener configurations
- **Authentication**: SASL/SSL settings for secure connections

### Storage Configuration
- **Storage Class**: DOKS-specific storage class (e.g., do-block-storage)
- **Storage Size**: Disk space per broker based on expected throughput
- **Storage Type**: Persistent volumes for durability
- **Backup Settings**: Backup and recovery configurations

### Resource Limits
- **CPU Limits**: CPU allocation per broker
- **Memory Limits**: Memory allocation per broker
- **Resource Requests**: Minimum resources guaranteed
- **Affinity Rules**: Node placement strategies

### Security Settings
- **SASL Authentication**: Username/password or certificate-based auth
- **SSL Encryption**: TLS/SSL configuration for data in transit
- **Network Policies**: Ingress/egress restrictions
- **RBAC Configuration**: Role-based access controls

## Strimzi-Specific Configuration

### Kafka Cluster CRD
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka-cluster
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
        authentication:
          type: scram-sha-512
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
        size: 100Gi
        class: do-block-storage
        deleteClaim: false
    resources:
      requests:
        memory: 4Gi
        cpu: 1000m
      limits:
        memory: 8Gi
        cpu: 2000m
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 10Gi
      class: do-block-storage
      deleteClaim: false
    resources:
      requests:
        memory: 1Gi
        cpu: 500m
      limits:
        memory: 2Gi
        cpu: 1000m
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

### Kafka Connect CRD
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnect
metadata:
  name: todo-kafka-connect
  annotations:
    strimzi.io/use-connector-resources: "true"
spec:
  version: 3.6.0
  replicas: 1
  bootstrapServers: todo-kafka-cluster-kafka-bootstrap:9093
  authentication:
    type: scram-sha-512
    username: connect
  tls:
    trustedCertificates: []
  resources:
    requests:
      memory: 2Gi
      cpu: 500m
    limits:
      memory: 4Gi
      cpu: 1000m
  config:
    group.id: kafka-connect-group
    offset.storage.topic: kafka-connect-offsets
    config.storage.topic: kafka-connect-configs
    status.storage.topic: kafka-connect-status
    config.storage.replication.factor: 3
    offset.storage.replication.factor: 3
    status.storage.replication.factor: 3
    producer.security.protocol: SASL_SSL
    producer.sasl.mechanism: SCRAM-SHA-512
    consumer.security.protocol: SASL_SSL
    consumer.sasl.mechanism: SCRAM-SHA-512
```

## Bitnami Kafka Configuration

### Values.yaml Example
```yaml
# Global settings
global:
  storageClass: do-block-storage

# Kafka settings
kafka:
  auth:
    clientProtocol: sasl
    interBrokerProtocol: sasl
    sasl:
      mechanisms: scram-sha-512
      jaas:
        clientUsers:
          - kafka-user
        clientPasswords:
          - changeme
        interBrokerUser: kafka-broker
        interBrokerPassword: changeme

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

  # Network configuration
  externalAccess:
    enabled: false

  # Logging
  logLevel: INFO

# Zookeeper settings
zookeeper:
  replicaCount: 3

  resources:
    limits:
      cpu: 1000m
      memory: 2Gi
    requests:
      cpu: 500m
      memory: 1Gi

  storage:
    size: 10Gi

# Metrics
metrics:
  kafka:
    enabled: true
    serviceMonitor:
      enabled: true
  zookeeper:
    enabled: true
    serviceMonitor:
      enabled: true
```

## DOKS-Specific Considerations

### Storage Classes
- Use `do-block-storage` for persistent volumes
- Consider SSD vs standard storage based on IOPS requirements
- Set appropriate reclaim policy for data protection

### Networking
- Configure internal cluster networking
- Set up proper firewall rules for Kafka ports
- Consider VPC peering for external connections

### Security
- Enable authentication and encryption by default
- Use DigitalOcean's managed certificates where possible
- Implement proper RBAC for cluster access

## Output Format

Generate a complete values.yaml file or Kafka CRD manifest with:
- All required configurations for the target environment
- Security settings properly configured
- Resource limits appropriate for expected load
- Storage settings optimized for performance and cost
- Monitoring and alerting configurations included