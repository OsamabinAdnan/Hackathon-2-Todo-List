---
name: generate-doks-cluster-blueprint
description: Extends blueprint-generator to produce DO-specific manifests or doctl/Terraform snippets for cluster creation (node pools, region, VPC, autoscaling). Use when creating DigitalOcean Kubernetes Service cluster blueprints with appropriate node pools, networking, and autoscaling configurations.
---

# Generate DOKS Cluster Blueprint

This skill helps generate DigitalOcean Kubernetes Service (DOKS) cluster blueprints with appropriate configurations for node pools, networking, VPC settings, and autoscaling based on application requirements.

## When to Use This Skill

Use this skill when:
- Creating new DOKS clusters for Todo application deployment
- Configuring node pools with appropriate instance types and sizing
- Setting up networking and VPC configurations for DOKS
- Defining autoscaling policies for different node pools
- Generating Terraform or doctl manifests for cluster creation
- Planning cluster infrastructure with cost optimization

## Cluster Configuration Parameters

### Basic Cluster Configuration
```yaml
# doks-cluster.yaml
cluster:
  name: "todo-app-cluster"
  region: "nyc1"  # Choose based on user requirements
  version: "1.28.3-do.0"  # Latest stable version
  tags:
    - "todo-app"
    - "production"
    - "doks"

  # Auto-upgrade settings
  auto_upgrade: true
  surge_upgrade: true

  # Maintenance window (UTC)
  maintenance_policy:
    start_time: "02:00"
    day: "sunday"
```

### Node Pool Configuration
```yaml
node_pools:
  - name: "core-pool"
    size: "s-2vcpu-4gb"  # General purpose for core services
    count: 3
    auto_scale: true
    min_nodes: 2
    max_nodes: 10
    tags:
      - "core-services"

  - name: "kafka-pool"
    size: "s-4vcpu-8gb"  # Larger for Kafka workloads
    count: 3
    auto_scale: true
    min_nodes: 2
    max_nodes: 6
    tags:
      - "kafka-workload"

  - name: "ingress-pool"
    size: "s-2vcpu-4gb"  # For ingress controllers
    count: 2
    auto_scale: false
    min_nodes: 2
    max_nodes: 2
    tags:
      - "ingress-controller"
```

## doctl Command Generation

### Cluster Creation Commands
```bash
#!/bin/bash
# create-doks-cluster.sh

# Variables
CLUSTER_NAME="todo-app-cluster"
REGION="nyc1"
VERSION="1.28.3-do.0"
TAGS="todo-app,production,doks"

# Create the cluster
doctl kubernetes cluster create $CLUSTER_NAME \
  --region $REGION \
  --version $VERSION \
  --auto-upgrade \
  --surge-upgrade \
  --maintenance-day sunday \
  --maintenance-start-time "02:00" \
  --tag $TAGS

# Add core node pool
doctl kubernetes cluster node-pool create $CLUSTER_NAME \
  --name core-pool \
  --size s-2vcpu-4gb \
  --count 3 \
  --auto-scale \
  --min-nodes 2 \
  --max-nodes 10 \
  --tag core-services

# Add Kafka node pool
doctl kubernetes cluster node-pool create $CLUSTER_NAME \
  --name kafka-pool \
  --size s-4vcpu-8gb \
  --count 3 \
  --auto-scale \
  --min-nodes 2 \
  --max-nodes 6 \
  --tag kafka-workload

# Add ingress node pool
doctl kubernetes cluster node-pool create $CLUSTER_NAME \
  --name ingress-pool \
  --size s-2vcpu-4gb \
  --count 2 \
  --auto-scale false \
  --tag ingress-controller

# Get kubeconfig
doctl kubernetes cluster kubeconfig show $CLUSTER_NAME > ~/.kube/todo-app-config
export KUBECONFIG=~/.kube/todo-app-config
```

## Terraform Configuration

### Terraform Cluster Blueprint
```hcl
# terraform/doks-cluster.tf

terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

variable "cluster_name" {
  description = "Name of the DOKS cluster"
  type        = string
  default     = "todo-app-cluster"
}

variable "region" {
  description = "Region for the cluster"
  type        = string
  default     = "nyc1"
}

variable "version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28.3-do.0"
}

resource "digitalocean_kubernetes_cluster" "todo_cluster" {
  name    = var.cluster_name
  region  = var.region
  version = var.version

  # Auto-upgrade settings
  auto_upgrade = true
  surge_upgrade = true

  # Maintenance window
  maintenance_policy {
    start_time = "02:00"
    day        = "sunday"
  }

  # Tags
  tags = ["todo-app", "production", "doks"]

  # Node pool configurations
  node_pool {
    name       = "core-pool"
    size       = "s-2vcpu-4gb"
    node_count = 3

    auto_scale = true
    min_nodes  = 2
    max_nodes  = 10

    tags = ["core-services"]
  }

  node_pool {
    name       = "kafka-pool"
    size       = "s-4vcpu-8gb"
    node_count = 3

    auto_scale = true
    min_nodes  = 2
    max_nodes  = 6

    tags = ["kafka-workload"]
  }

  node_pool {
    name       = "ingress-pool"
    size       = "s-2vcpu-4gb"
    node_count = 2

    auto_scale = false

    tags = ["ingress-controller"]
  }
}

# Output cluster information
output "cluster_id" {
  value = digitalocean_kubernetes_cluster.todo_cluster.id
}

output "cluster_endpoint" {
  value = digitalocean_kubernetes_cluster.todo_cluster.endpoint
}

output "cluster_ca_cert" {
  value     = digitalocean_kubernetes_cluster.todo_cluster.kube_config[0].cluster_ca_certificate
  sensitive = true
}

output "node_pools" {
  value = digitalocean_kubernetes_cluster.todo_cluster.node_pool
}
```

## Advanced Networking Configuration

### VPC and Network Settings
```yaml
# networking.yaml
networking:
  vpc:
    name: "todo-app-vpc"
    region: "nyc1"
    ip_range: "10.100.0.0/16"

  subnets:
    - name: "doks-private"
      ip_range: "10.100.1.0/24"
      region: "nyc1"

    - name: "doks-public"
      ip_range: "10.100.2.0/24"
      region: "nyc1"

firewall:
  name: "doks-firewall"
  inbound_rules:
    - protocol: "tcp"
      port: "6443"
      source_addresses: ["0.0.0.0/0"]
      description: "Kubernetes API server"

    - protocol: "tcp"
      port: "22"
      source_addresses: ["YOUR_IP/32"]  # Replace with actual IP
      description: "SSH access"

    - protocol: "tcp"
      port: "80,443"
      source_addresses: ["0.0.0.0/0"]
      description: "HTTP/HTTPS traffic"

  outbound_rules:
    - protocol: "tcp"
      ports: ["1-65535"]
      destination_addresses: ["0.0.0.0/0"]
      description: "All outbound TCP"

    - protocol: "udp"
      ports: ["1-65535"]
      destination_addresses: ["0.0.0.0/0"]
      description: "All outbound UDP"
```

## Autoscaling Configuration

### Horizontal Pod Autoscaler Templates
```yaml
# autoscaling-templates.yaml
autoscaling_profiles:
  core_services:
    min_replicas: 2
    max_replicas: 10
    target_cpu_utilization: 70
    target_memory_utilization: 80

  kafka_brokers:
    min_replicas: 3
    max_replicas: 6
    target_cpu_utilization: 80
    target_memory_utilization: 85

  ingress_controllers:
    min_replicas: 2
    max_replicas: 4
    target_cpu_utilization: 60
    target_memory_utilization: 70

# Node Pool Autoscaling Configuration
node_autoscaling:
  core_pool:
    min_nodes: 2
    max_nodes: 10
    scale_down_enabled: true
    scale_down_unneeded_time: "10m"
    scale_down_utilization_threshold: 0.5

  kafka_pool:
    min_nodes: 2
    max_nodes: 6
    scale_down_enabled: true
    scale_down_unneeded_time: "15m"
    scale_down_utilization_threshold: 0.6

  ingress_pool:
    min_nodes: 2
    max_nodes: 2
    scale_down_enabled: false  # Fixed size for ingress
```

## Cost Optimization Configuration

### Resource Sizing Guidelines
```yaml
# cost-optimization.yaml
cost_optimization:
  node_pool_sizing:
    core_pool:
      # For general microservices and APIs
      instance_types:
        - "s-2vcpu-4gb"  # Small workloads
        - "s-4vcpu-8gb"  # Medium workloads
        - "s-8vcpu-16gb" # Large workloads

    kafka_pool:
      # For Kafka workloads requiring more memory and CPU
      instance_types:
        - "s-4vcpu-8gb"  # Small Kafka cluster
        - "s-8vcpu-16gb" # Medium Kafka cluster
        - "m-16vcpu-32gb" # Large Kafka cluster

    ingress_pool:
      # For ingress controllers and load balancers
      instance_types:
        - "s-2vcpu-4gb"  # Small ingress
        - "s-4vcpu-8gb"  # Medium ingress

  spot_instances:
    enabled: false  # Disable for critical workloads
    max_price: null

  reserved_instances:
    enabled: false  # Consider for predictable workloads
    term: "1-year"
    payment_option: "No Upfront"
```

## Monitoring and Observability

### Cluster Monitoring Setup
```yaml
# monitoring.yaml
monitoring:
  cluster_monitoring:
    enabled: true
    retention_days: 30

  logging:
    enabled: true
    retention_days: 30

  metrics:
    enabled: true
    retention_days: 90

  alerting:
    cpu_threshold: 85
    memory_threshold: 85
    disk_threshold: 80
    network_threshold: 90
```

## Terraform Variables and Outputs

### Terraform Variables File
```hcl
# terraform/variables.tf
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "todo-app"
}

variable "environment" {
  description = "Environment type"
  type        = string
  default     = "production"
  validation {
    condition = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
  default     = "nyc1"
}

variable "node_pool_sizes" {
  description = "Map of node pool sizes"
  type = map(object({
    size       = string
    count      = number
    auto_scale = bool
    min_nodes  = number
    max_nodes  = number
  }))
  default = {
    core = {
      size       = "s-2vcpu-4gb"
      count      = 3
      auto_scale = true
      min_nodes  = 2
      max_nodes  = 10
    }
    kafka = {
      size       = "s-4vcpu-8gb"
      count      = 3
      auto_scale = true
      min_nodes  = 2
      max_nodes  = 6
    }
  }
}
```

### Terraform Outputs File
```hcl
# terraform/outputs.tf
output "cluster_name" {
  description = "Name of the created cluster"
  value       = digitalocean_kubernetes_cluster.todo_cluster.name
}

output "cluster_endpoint" {
  description = "Endpoint of the created cluster"
  value       = digitalocean_kubernetes_cluster.todo_cluster.endpoint
}

output "cluster_kubeconfig" {
  description = "Kubeconfig for the cluster"
  value       = digitalocean_kubernetes_cluster.todo_cluster.kube_config[0].raw_config
  sensitive   = true
}

output "node_pool_details" {
  description = "Details of created node pools"
  value = {
    for pool in digitalocean_kubernetes_cluster.todo_cluster.node_pool :
    pool.name => {
      id         = pool.id
      size       = pool.size
      node_count = pool.node_count
      auto_scale = pool.auto_scale
      min_nodes  = pool.min_nodes
      max_nodes  = pool.max_nodes
    }
  }
}
```

## Output Format

Generate cluster blueprints that include:
- Complete doctl command sequences for cluster creation
- Terraform configuration files with variables and outputs
- Node pool specifications with appropriate sizing
- Networking and VPC configurations
- Autoscaling policies for different workloads
- Cost optimization recommendations
- Security and firewall configurations
- Monitoring and observability setups
- Complete deployment scripts with error handling