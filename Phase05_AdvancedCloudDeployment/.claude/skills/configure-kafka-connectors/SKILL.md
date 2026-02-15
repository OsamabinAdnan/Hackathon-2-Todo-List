---
name: configure-kafka-connectors
description: Produces connector configurations (e.g., JDBC sink to Neon DB for auditing, source connectors for external integrations) with authentication and error handling. Use when setting up Kafka Connect connectors for data integration between Kafka and external systems like databases, APIs, and file systems.
---

# Configure Kafka Connectors

This skill helps create and configure Kafka Connect connector configurations for data integration between Kafka and external systems such as databases, APIs, and file systems.

## When to Use This Skill

Use this skill when:
- Setting up JDBC connectors to integrate with databases (Neon DB, PostgreSQL, MySQL)
- Configuring source connectors to ingest data from external systems
- Creating sink connectors to export data from Kafka topics
- Implementing data pipelines between Kafka and other systems
- Setting up audit logging to external storage systems
- Connecting to external APIs and services

## Connector Types

### Sink Connectors
- **JDBC Sink**: Export Kafka records to relational databases
- **Elasticsearch Sink**: Index Kafka records to Elasticsearch
- **S3 Sink**: Archive Kafka records to object storage
- **HTTP Sink**: Send records to REST APIs
- **Neo4j Sink**: Store graph data from Kafka records

### Source Connectors
- **JDBC Source**: Import data from relational databases
- **MongoDB Source**: Import documents from MongoDB collections
- **Twitter Source**: Stream tweets from Twitter API
- **JMS Source**: Integrate with JMS message queues
- **File Pulse Source**: Monitor and process file changes

## JDBC Sink Connector Configuration (Neon DB)

### Basic JDBC Sink Configuration
```json
{
  "name": "todo-neon-audit-sink-connector",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "tasks.max": "3",
    "topics": "todo-task-events,todo-user-activity",
    "connection.url": "jdbc:postgresql://ep-aged-math-xxxxxx-pooler.us-east-1.aws.neon.tech/todo_db?user=username&password=password&sslmode=require",
    "connection.ds.pool.size": "5",
    "table.name.format": "kafka_${topic}",
    "insert.mode": "upsert",
    "pk.mode": "record_key",
    "pk.fields": "taskId,userId",
    "auto.create": "true",
    "auto.evolve": "true",
    "batch.size": "3000",
    "max.retries": "5",
    "retry.backoff.ms": "1000",
    "errors.tolerance": "all",
    "errors.log.enable": "true",
    "errors.log.include.messages": "true",
    "errors.deadletterqueue.topic.name": "todo-connect-errors",
    "errors.deadletterqueue.topic.replication.factor": "3"
  }
}
```

### Advanced JDBC Sink with Custom SQL
```json
{
  "name": "todo-neon-advanced-sink-connector",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "tasks.max": "2",
    "topics": "todo-task-state",
    "connection.url": "jdbc:postgresql://ep-aged-math-xxxxxx-pooler.us-east-1.aws.neon.tech/todo_db?user=username&password=password&sslmode=require",
    "connection.ds.pool.size": "3",
    "table.name.format": "tasks",
    "insert.mode": "upsert",
    "pk.mode": "record_value",
    "pk.fields": "taskId",
    "db.timezone": "UTC",
    "dialect.name": "PostgreSqlDatabaseDialect",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",
    "transforms": "unwrap,addTimestamp",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.addTimestamp.type": "org.apache.kafka.connect.transforms.InsertField$Value",
    "transforms.addTimestamp.timestamp.field": "processed_at",
    "auto.create": "false",
    "auto.evolve": "false",
    "sql.quote.identifiers": "true",
    "batch.size": "2000",
    "linger.ms": "100",
    "max.retries": "10",
    "retry.backoff.ms": "3000",
    "errors.tolerance": "all",
    "errors.log.enable": "true",
    "errors.log.include.messages": "true",
    "errors.deadletterqueue.topic.name": "todo-connect-errors",
    "errors.deadletterqueue.topic.replication.factor": "3",
    "errors.deadletterqueue.topic.max.message.bytes": "1048576"
  }
}
```

## JDBC Source Connector Configuration

### Basic JDBC Source Configuration
```json
{
  "name": "todo-neon-source-connector",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "tasks.max": "2",
    "topic.prefix": "neon-",
    "connection.url": "jdbc:postgresql://ep-aged-math-xxxxxx-pooler.us-east-1.aws.neon.tech/todo_db?user=username&password=password&sslmode=require",
    "mode": "timestamp+incrementing",
    "timestamp.column.name": "updated_at",
    "incrementing.column.name": "id",
    "numeric.mapping": "best_fit",
    "poll.interval.ms": "3000",
    "batch.max.rows": "500",
    "query": "SELECT * FROM tasks WHERE updated_at > ? ORDER BY updated_at ASC LIMIT 1000",
    "table.whitelist": "tasks,users",
    "validate.non.null": "false",
    "timestamp.delay.interval.ms": "5000",
    "transforms": "addTopicSuffix,unwrap",
    "transforms.addTopicSuffix.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.addTopicSuffix.regex": "(.*)",
    "transforms.addTopicSuffix.replacement": "$1-source",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter.schemas.enable": "false",
    "errors.tolerance": "all",
    "errors.log.enable": "true",
    "errors.log.include.messages": "true"
  }
}
```

## HTTP Sink Connector Configuration

### Basic HTTP Sink
```json
{
  "name": "todo-http-notification-sink",
  "config": {
    "connector.class": "com.github.jcustenborder.kafka.connect.http.HttpSinkConnector",
    "tasks.max": "1",
    "topics": "todo-alerts,todo-notifications",
    "http.url": "https://api.notification-service.com/webhook",
    "http.method": "POST",
    "http.headers": "Content-Type:application/json,Authorization:Bearer ${file:/opt/kafka/secrets/oauth.token}",
    "http.request.template": "{\"event\": ${value}, \"timestamp\": \"${now()}\", \"source\": \"todo-app\"}",
    "http.authentication.type": "BEARER",
    "http.authentication.oauth.token.file.path": "/opt/kafka/secrets/oauth.token",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",
    "errors.tolerance": "all",
    "errors.log.enable": "true",
    "errors.deadletterqueue.topic.name": "http-sink-errors",
    "errors.deadletterqueue.topic.replication.factor": "3",
    "http.retry.backoff.ms": "1000",
    "http.retry.max.attempts": "5",
    "http.timeout.connect.ms": "5000",
    "http.timeout.read.ms": "10000"
  }
}
```

## File Pulse Source Connector Configuration

### File Monitoring Connector
```json
{
  "name": "todo-log-file-source",
  "config": {
    "connector.class": "tech.streamflow.kafka.connect.source.FilePulseSourceConnector",
    "tasks.max": "1",
    "topic": "todo-log-events",
    "file.file_reader.fs.scan.directory.path": "/var/log/todo-app/",
    "file.filter.regexp": ".*\\.log$",
    "file.monitoring.list.internal.topics": "true",
    "file.reader.buf.size": "16384",
    "file.parser.grok.patterns": "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}",
    "transforms": "addTopicPrefix,addStaticFields",
    "transforms.addTopicPrefix.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.addTopicPrefix.regex": "(.*)",
    "transforms.addTopicPrefix.replacement": "logs-$1",
    "transforms.addStaticFields.type": "org.apache.kafka.connect.transforms.ValueUpdater",
    "transforms.addStaticFields.updates": "source:todo-app-logs",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "errors.tolerance": "all",
    "errors.log.enable": "true",
    "errors.deadletterqueue.topic.name": "file-source-errors"
  }
}
```

## Security and Authentication

### SSL/TLS Configuration
```json
{
  "config": {
    "...": "...",
    "connection.ssl.mode": "require",
    "connection.ssl.key.password": "${file:/opt/kafka/secrets/db-key-password.txt}",
    "connection.ssl.keystore.location": "/opt/kafka/secrets/db-keystore.jks",
    "connection.ssl.keystore.password": "${file:/opt/kafka/secrets/keystore-password.txt}",
    "connection.ssl.truststore.location": "/opt/kafka/secrets/db-truststore.jks",
    "connection.ssl.truststore.password": "${file:/opt/kafka/secrets/truststore-password.txt}"
  }
}
```

### SASL/SCRAM Authentication
```json
{
  "config": {
    "...": "...",
    "producer.security.protocol": "SASL_SSL",
    "producer.sasl.mechanism": "SCRAM-SHA-512",
    "producer.sasl.jaas.config": "org.apache.kafka.common.security.scram.ScramLoginModule required username=\"kafka-connect\" password=\"${file:/opt/kafka/secrets/connect-password.txt}\";"
  }
}
```

## Error Handling and Monitoring

### Dead Letter Queue Configuration
```json
{
  "config": {
    "...": "...",
    "errors.tolerance": "all",
    "errors.log.enable": "true",
    "errors.log.include.messages": "true",
    "errors.deadletterqueue.topic.name": "connect-errors",
    "errors.deadletterqueue.topic.replication.factor": "3",
    "errors.deadletterqueue.topic.max.message.bytes": "1048576",
    "errors.retry.timeout": "-1",
    "errors.retry.delay.max.ms": "60000"
  }
}
```

### Monitoring and Metrics
```json
{
  "config": {
    "...": "...",
    "consumer.interceptor.classes": "io.confluent.monitoring.clients.interceptor.MonitoringConsumerInterceptor",
    "producer.interceptor.classes": "io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor",
    "reporters": "io.confluent.monitoring.clients.interceptor.KafkaMetricsReporter",
    "metric.reporters": "io.confluent.metrics.reporter.ConfluentMetricsReporter",
    "confluent.metrics.reporter.bootstrap.servers": "kafka:9092",
    "confluent.metrics.reporter.topic.replicas": "3"
  }
}
```

## Connector Management

### Health Check Configuration
```json
{
  "name": "todo-connector-health-check",
  "config": {
    "connector.class": "io.confluent.connect.monitoring.MonitoringConnector",
    "tasks.max": "1",
    "topics": "connect-status",
    "interval.ms": "30000",
    "include.tasks": "true",
    "include.connectors": "true",
    "status.topic": "connect-status",
    "status.storage.topic": "connect-status-storage",
    "status.storage.replication.factor": "3"
  }
}
```

## Output Format

Generate connector configuration in JSON format with:
- Appropriate connector class for the target system
- Proper authentication and security settings
- Error handling and dead letter queue configuration
- Performance tuning parameters
- Monitoring and logging configuration
- Clear documentation of configuration parameters