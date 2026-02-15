---
name: monitor-kafka-health
description: Creates kubectl-ai/kagent prompts and scripts to inspect broker status, consumer lag, throughput, partition distribution, and alert on anomalies. Use when monitoring Kafka cluster health and performance with kubectl-ai and kagent tools for DigitalOcean Kubernetes Service.
---

# Monitor Kafka Health

This skill helps create monitoring solutions for Kafka clusters using kubectl-ai and kagent tools to inspect broker status, consumer lag, throughput, partition distribution, and detect anomalies.

## When to Use This Skill

Use this skill when:
- Monitoring Kafka cluster health on DigitalOcean Kubernetes Service
- Inspecting broker status and performance metrics
- Tracking consumer lag across consumer groups
- Monitoring throughput and partition distribution
- Setting up alerting for cluster anomalies
- Troubleshooting performance issues in Kafka clusters

## Broker Health Monitoring

### Broker Status Check
```bash
# Check Kafka broker pods status
kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o wide

# Check broker logs for errors
kubectl-ai logs -l strimzi.io/name=todokafka-cluster-kafka --tail=100 | grep -i error

# Check broker resource utilization
kubectl-ai top pods -l strimzi.io/name=todokafka-cluster-kafka

# Describe broker pods for detailed status
kubectl-ai describe pods -l strimzi.io/name=todokafka-cluster-kafka
```

### Broker Configuration Verification
```bash
# Get Kafka cluster configuration
kubectl-ai get kafka todokafka-cluster -o yaml

# Check KafkaTopic resources
kubectl-ai get kafkatopic -o wide

# Verify broker connectivity
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
  bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

## Consumer Lag Monitoring

### Consumer Group Status
```bash
# List consumer groups
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Describe specific consumer group
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group <consumer-group-name>

# Check consumer lag for all groups
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --state | grep -E "(CONSUMER-ID|GROUP|TOPIC|LAG)"
```

### Consumer Lag Script
```bash
#!/bin/bash
# monitor_consumer_lag.sh

KAFKA_POD=$(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}' --field-selector=status.phase==Running)
CONSUMER_GROUPS=$(kubectl-ai exec $KAFKA_POD -- bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list)

for group in $CONSUMER_GROUPS; do
  echo "Checking consumer group: $group"
  kubectl-ai exec $KAFKA_POD -- bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group $group | \
  awk 'NR>1 {sum+=$5} END {print "Total lag for group " ENVIRON["group"] ": " sum}'
done
```

## Throughput Monitoring

### Topic Metrics
```bash
# Get topic details
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic <topic-name>

# Check all topics
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Get partition details for a topic
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic <topic-name> --under-replicated
```

### Throughput Measurement Script
```bash
#!/bin/bash
# measure_throughput.sh

KAFKA_POD=$(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}' --field-selector=status.phase==Running)

echo "Measuring Kafka throughput..."

# Get current message count for topics
for topic in $(kubectl-ai exec $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --list); do
  if [[ $topic != "__"* ]]; then
    echo "Topic: $topic"
    kubectl-ai exec $KAFKA_POD -- bin/kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic $topic
  fi
done
```

## Partition Distribution Monitoring

### Partition Balance Check
```bash
# Check partition distribution
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topics-with-overrides

# Check for under-replicated partitions
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --under-replicated

# Check for leader imbalance
kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --unavailable-partitions
```

## Comprehensive Monitoring Script

### Kafka Health Check Script
```bash
#!/bin/bash
# kafka_health_check.sh

set -euo pipefail

KAFKA_CLUSTER_NAME="todokafka-cluster"
KAFKA_LABEL="strimzi.io/name=${KAFKA_CLUSTER_NAME}-kafka"
OUTPUT_FILE="/tmp/kafka_health_report_$(date +%Y%m%d_%H%M%S).txt"

echo "Starting Kafka health check..." | tee $OUTPUT_FILE

# Function to run kubectl command and append to output
run_check() {
  local description="$1"
  local command="$2"

  echo "" | tee -a $OUTPUT_FILE
  echo "=== $description ===" | tee -a $OUTPUT_FILE
  echo "Command: $command" | tee -a $OUTPUT_FILE
  echo "----------------------------------------" | tee -a $OUTPUT_FILE

  if eval "$command"; then
    echo "✅ SUCCESS" | tee -a $OUTPUT_FILE
  else
    echo "❌ FAILED" | tee -a $OUTPUT_FILE
  fi
}

# Check if Kafka pods are running
KAFKA_POD=$(kubectl-ai get pods -l $KAFKA_LABEL -o jsonpath='{.items[0].metadata.name}' --field-selector=status.phase==Running || echo "")
if [ -z "$KAFKA_POD" ]; then
  echo "No running Kafka pods found!" | tee -a $OUTPUT_FILE
  exit 1
fi

echo "Using Kafka pod: $KAFKA_POD" | tee -a $OUTPUT_FILE

# Basic cluster info
run_check "Cluster Info" "kubectl-ai get kafka $KAFKA_CLUSTER_NAME -o yaml"
run_check "Kafka Pods Status" "kubectl-ai get pods -l $KAFKA_LABEL -o wide"
run_check "Kafka Pod Resources" "kubectl-ai top pods -l $KAFKA_LABEL"

# Broker connectivity
run_check "Broker Connectivity" "kubectl-ai exec $KAFKA_POD -- bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092"

# Topic information
run_check "List of Topics" "kubectl-ai exec $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --list"
run_check "Topic Details" "kubectl-ai exec $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe"

# Consumer group information
run_check "Consumer Groups" "kubectl-ai exec $KAFKA_POD -- bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list"

# Under-replicated partitions check
run_check "Under-replicated Partitions" "kubectl-ai exec $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --under-replicated"

# Unavailable partitions check
run_check "Unavailable Partitions" "kubectl-ai exec $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --unavailable-partitions"

# Log any errors in Kafka pods
run_check "Recent Error Logs" "kubectl-ai logs -l $KAFKA_LABEL --since=10m | grep -i error || echo 'No errors found in last 10 minutes'"

echo "" | tee -a $OUTPUT_FILE
echo "Kafka health check completed. Report saved to: $OUTPUT_FILE" | tee -a $OUTPUT_FILE
```

## Alerting Configuration

### Prometheus Metrics for Kafka
```yaml
# prometheus-kafka-rules.yml
groups:
  - name: kafka.rules
    rules:
      - alert: KafkaDown
        expr: up{job="kafka"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Kafka instance is down"
          description: "Kafka instance {{ $labels.instance }} has been down for more than 1 minute."

      - alert: HighConsumerLag
        expr: kafka_consumer_group_lag > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High consumer lag detected"
          description: "Consumer group {{ $labels.consumer_group }} on topic {{ $labels.topic }} has lag of {{ $value }} messages."

      - alert: UnderReplicatedPartitions
        expr: kafka_server_replicamanager_underreplicatedpartitions > 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Under-replicated partitions detected"
          description: "{{ $value }} partitions are under-replicated in Kafka cluster."

      - alert: OfflinePartitions
        expr: kafka_controller_kafkacontroller_offlinepartitionscount > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Offline partitions detected"
          description: "{{ $value }} partitions are offline in Kafka cluster."
```

## kagent Integration Prompts

### Health Check Prompt for kagent
```
Analyze the Kafka cluster health by running these diagnostic commands:

1. Check the status of all Kafka cluster pods:
   kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o wide

2. Get resource utilization of Kafka pods:
   kubectl-ai top pods -l strimzi.io/name=todokafka-cluster-kafka

3. Check Kafka cluster CRD status:
   kubectl-ai get kafka todokafka-cluster -o yaml

4. List all Kafka topics:
   kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

5. Check for under-replicated partitions:
   kubectl-ai exec -it $(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}') -- \
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --under-replicated

Based on the results, provide a health assessment and recommend any necessary actions.
```

### Performance Analysis Prompt for kagent
```
Perform a performance analysis of the Kafka cluster:

1. Measure consumer lag for all consumer groups:
   - Get list of consumer groups
   - For each group, get lag information
   - Identify groups with high lag (>1000 messages)

2. Check partition distribution and balance:
   - List all topics and their partition counts
   - Check if partitions are evenly distributed across brokers
   - Identify any imbalanced topics

3. Assess throughput patterns:
   - Get topic sizes and message rates
   - Compare current throughput with historical baselines
   - Identify any unusual patterns

4. Resource utilization check:
   - Check CPU and memory usage of Kafka brokers
   - Compare with configured limits
   - Assess if scaling is needed

Provide a performance report with metrics, identified issues, and recommendations.
```

## Anomaly Detection

### Anomaly Detection Script
```bash
#!/bin/bash
# detect_anomalies.sh

KAFKA_POD=$(kubectl-ai get pods -l strimzi.io/name=todokafka-cluster-kafka -o jsonpath='{.items[0].metadata.name}' --field-selector=status.phase==Running)

echo "Detecting Kafka anomalies..."

# Check for high consumer lag
echo "Checking for high consumer lag..."
for group in $(kubectl-ai exec $KAFKA_POD -- bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list); do
  total_lag=$(kubectl-ai exec $KAFKA_POD -- bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group $group 2>/dev/null | \
  awk 'NR>1 {sum+=$5} END {print sum+0}')

  if [ "$total_lag" -gt 1000 ]; then
    echo "⚠️  WARNING: Consumer group '$group' has high lag: $total_lag messages"
  fi
done

# Check for under-replicated partitions
echo "Checking for under-replicated partitions..."
under_replicated=$(kubectl-ai exec $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --under-replicated 2>&1 | wc -l)
if [ "$under_replicated" -gt 0 ]; then
  echo "🚨 CRITICAL: Found under-replicated partitions"
  kubectl-ai exec $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --under-replicated
fi

# Check for unavailable partitions
echo "Checking for unavailable partitions..."
unavailable=$(kubectl-ai exec $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --unavailable-partitions 2>&1 | wc -l)
if [ "$unavailable" -gt 0 ]; then
  echo "🚨 CRITICAL: Found unavailable partitions"
  kubectl-ai exec $KAFKA_POD -- bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --unavailable-partitions
fi

echo "Anomaly detection completed."
```

## Output Format

Generate monitoring solutions that include:
- Shell scripts for automated health checks
- kubectl-ai command sequences for manual inspection
- kagent prompts for AI-assisted analysis
- Alerting rules for Prometheus/Grafana
- Anomaly detection algorithms
- Performance baseline comparisons
- Recommended actions for identified issues