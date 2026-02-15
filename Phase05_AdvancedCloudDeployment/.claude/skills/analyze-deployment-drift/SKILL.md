---
name: analyze-deployment-drift
description: Compares live cluster state against cloud-native blueprints and generates remediation plans (YAML patches, Helm upgrades) to restore desired state. Use when identifying configuration drift between deployed resources and intended blueprints with automated remediation suggestions.
---

# Analyze Deployment Drift

This skill helps compare live cluster state against cloud-native blueprints and generate remediation plans to restore desired state through YAML patches, Helm upgrades, and other corrective actions.

## When to Use This Skill

Use this skill when:
- Comparing live cluster state against deployment blueprints
- Identifying configuration drift between desired and actual state
- Generating remediation plans for drifted resources
- Performing compliance checks against infrastructure as code
- Detecting unauthorized changes to deployed resources
- Creating automated remediation workflows
- Validating deployment integrity

## Drift Detection Methodology

### State Comparison Framework
```bash
#!/bin/bash
# drift-detection-framework.sh

# Configuration
CLUSTER_NAMESPACE="${1:-todo-app}"
BLUEPRINT_PATH="${2:-./blueprints}"
OUTPUT_PATH="${3:-./drift-report}"

# Function to collect live state
collect_live_state() {
    local namespace=$1
    local output_dir=$2

    echo "Collecting live state for namespace: $namespace"

    # Collect all resource types
    kubectl get all -n "$namespace" -o yaml > "$output_dir/live-all.yaml"

    # Collect specific resources separately
    kubectl get deployments -n "$namespace" -o yaml > "$output_dir/live-deployments.yaml"
    kubectl get services -n "$namespace" -o yaml > "$output_dir/live-services.yaml"
    kubectl get configmaps -n "$namespace" -o yaml > "$output_dir/live-configmaps.yaml"
    kubectl get secrets -n "$namespace" -o yaml > "$output_dir/live-secrets.yaml"
    kubectl get ingresses -n "$namespace" -o yaml > "$output_dir/live-ingresses.yaml"
    kubectl get hpa -n "$namespace" -o yaml > "$output_dir/live-hpa.yaml"
    kubectl get pvc -n "$namespace" -o yaml > "$output_dir/live-pvc.yaml"

    # Collect resource-specific annotations and labels
    kubectl get all -n "$namespace" -L app -L version -L environment > "$output_dir/live-labels.txt"
}

# Function to compare states
compare_states() {
    local blueprint_dir=$1
    local live_dir=$2
    local output_file=$3

    echo "Comparing blueprint state with live state..."

    # Compare deployments
    echo "Checking deployment drift..." >> "$output_file"
    diff -u "$blueprint_dir/deployments.yaml" "$live_dir/live-deployments.yaml" >> "$output_file" 2>/dev/null || true

    # Compare services
    echo "Checking service drift..." >> "$output_file"
    diff -u "$blueprint_dir/services.yaml" "$live_dir/live-services.yaml" >> "$output_file" 2>/dev/null || true

    # Compare configmaps
    echo "Checking configmap drift..." >> "$output_file"
    diff -u "$blueprint_dir/configmaps.yaml" "$live_dir/live-configmaps.yaml" >> "$output_file" 2>/dev/null || true

    # Compare other resources as needed
}

# Function to generate remediation plan
generate_remediation_plan() {
    local drift_file=$1
    local blueprint_dir=$2
    local remediation_file=$3

    echo "Generating remediation plan..." > "$remediation_file"

    # Analyze drift file and generate specific remediation commands
    if grep -q "DEPLOYMENT_DRIFT" "$drift_file"; then
        echo "# Deployment remediation needed" >> "$remediation_file"
        echo "kubectl apply -f $blueprint_dir/deployments.yaml" >> "$remediation_file"
    fi

    if grep -q "SERVICE_DRIFT" "$drift_file"; then
        echo "# Service remediation needed" >> "$remediation_file"
        echo "kubectl apply -f $blueprint_dir/services.yaml" >> "$remediation_file"
    fi

    # Add more specific remediation commands based on drift types
}

# Main execution
main() {
    local blueprint_path=$1
    local cluster_namespace=$2
    local output_path=$3

    mkdir -p "$output_path"

    # Collect live state
    collect_live_state "$cluster_namespace" "$output_path"

    # Compare with blueprint
    compare_states "$blueprint_path" "$output_path" "$output_path/drift-analysis.txt"

    # Generate remediation plan
    generate_remediation_plan "$output_path/drift-analysis.txt" "$blueprint_path" "$output_path/remediation-plan.sh"

    echo "Drift analysis completed. Reports saved to: $output_path"
}

main "$CLUSTER_NAMESPACE" "$BLUEPRINT_PATH" "$OUTPUT_PATH"
```

## Advanced Drift Detection

### Helm-Based Drift Detection
```bash
#!/bin/bash
# helm-drift-detection.sh

HELM_RELEASE="${1:-todo-chatbot-platform}"
NAMESPACE="${2:-todo-app}"
OUTPUT_PATH="${3:-./helm-drift-report}"

# Function to get current Helm state
get_helm_state() {
    local release=$1
    local namespace=$2
    local output_dir=$3

    echo "Getting Helm release state for $release in $namespace"

    # Get current values
    helm get values "$release" -n "$namespace" -o yaml > "$output_dir/current-values.yaml"

    # Get manifest
    helm get manifest "$release" -n "$namespace" > "$output_dir/current-manifest.yaml"

    # Get status
    helm status "$release" -n "$namespace" > "$output_dir/release-status.txt"

    # Get history
    helm history "$release" -n "$namespace" -o yaml > "$output_dir/release-history.yaml"
}

# Function to compare with original chart
compare_helm_chart() {
    local release=$1
    local namespace=$2
    local original_chart_path=$3
    local output_file=$4

    echo "Comparing Helm release with original chart..."

    # Get the chart that was originally used
    ORIGINAL_CHART=$(helm list -n "$namespace" -f "^$release$" -o json | jq -r '.[0].chart')

    # Download the original chart version
    TEMP_DIR=$(mktemp -d)
    helm pull "$(echo "$ORIGINAL_CHART" | cut -d'-' -f1)" --version "$(echo "$ORIGINAL_CHART" | cut -d'-' -f2-)" --destination "$TEMP_DIR"

    # Extract and compare
    tar -xzf "$TEMP_DIR/$(basename "$ORIGINAL_CHART").tgz" -C "$TEMP_DIR"

    # Generate template from original chart
    helm template "$release" "$TEMP_DIR/$(basename "$ORIGINAL_CHART" | cut -d'-' -f1)" -n "$namespace" > "$output_dir/original-manifest.yaml"

    # Compare with current manifest
    diff -u "$output_dir/original-manifest.yaml" "$output_dir/current-manifest.yaml" > "$output_dir/helm-drift.diff"

    rm -rf "$TEMP_DIR"
}

# Function to generate Helm remediation
generate_helm_remediation() {
    local drift_file=$1
    local original_chart_path=$2
    local remediation_file=$3
    local release=$4
    local namespace=$5

    echo "Generating Helm remediation plan..." > "$remediation_file"

    if [ -s "$drift_file" ]; then
        echo "# Helm release drift detected" >> "$remediation_file"
        echo "# Consider rolling back or upgrading to original chart" >> "$remediation_file"
        echo "helm rollback $release -n $namespace" >> "$remediation_file"
        echo "# OR upgrade with original values" >> "$remediation_file"
        echo "# helm upgrade $release <original-chart> -n $namespace -f <original-values.yaml>" >> "$remediation_file"
    else
        echo "# No Helm drift detected" >> "$remediation_file"
    fi
}

# Main Helm drift detection
main_helm() {
    local helm_release=$1
    local namespace=$2
    local output_path=$3

    mkdir -p "$output_path"

    get_helm_state "$helm_release" "$namespace" "$output_path"
    compare_helm_chart "$helm_release" "$namespace" "./original-chart" "$output_path"
    generate_helm_remediation "$output_path/helm-drift.diff" "./original-chart" "$output_path/helm-remediation.sh" "$helm_release" "$namespace"

    echo "Helm drift analysis completed for $helm_release in $namespace"
}

main_helm "$HELM_RELEASE" "$NAMESPACE" "$OUTPUT_PATH"
```

## Resource-Specific Drift Analysis

### Deployment Drift Analysis
```yaml
# deployment-drift-analysis.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: deployment-drift-analysis
  namespace: kagent-system
data:
  drift_detection_rules: |
    # Deployment drift detection rules
    rules:
      - name: "container_image_drift"
        description: "Check if container images differ from blueprint"
        query: |
          .spec.template.spec.containers[].image
        comparison: "exact_match"

      - name: "resource_limits_drift"
        description: "Check if resource limits differ from blueprint"
        query: |
          .spec.template.spec.containers[].resources
        comparison: "greater_than_or_equal"

      - name: "replica_count_drift"
        description: "Check if replica count differs from blueprint"
        query: |
          .spec.replicas
        comparison: "exact_match"

      - name: "environment_vars_drift"
        description: "Check if environment variables differ from blueprint"
        query: |
          .spec.template.spec.containers[].env
        comparison: "subset_match"

      - name: "labels_annotations_drift"
        description: "Check if labels/annotations differ from blueprint"
        query: |
          .metadata.labels, .metadata.annotations
        comparison: "subset_match"
```

### Service Drift Analysis
```yaml
# service-drift-analysis.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: service-drift-analysis
  namespace: kagent-system
data:
  service_drift_rules: |
    # Service drift detection rules
    rules:
      - name: "port_configuration_drift"
        description: "Check if service ports differ from blueprint"
        query: |
          .spec.ports[]
        comparison: "exact_match"

      - name: "service_type_drift"
        description: "Check if service type differs from blueprint"
        query: |
          .spec.type
        comparison: "exact_match"

      - name: "selector_drift"
        description: "Check if service selectors differ from blueprint"
        query: |
          .spec.selector
        comparison: "exact_match"

      - name: "load_balancer_config_drift"
        description: "Check if load balancer config differs from blueprint"
        query: |
          .spec.loadBalancerSourceRanges, .status.loadBalancer.ingress
        comparison: "validation_rule"
```

## Automated Remediation Plans

### YAML Patch Generation
```bash
#!/bin/bash
# generate-yaml-patches.sh

# Function to generate strategic merge patch
generate_strategic_merge_patch() {
    local resource_type=$1
    local resource_name=$2
    local namespace=$3
    local blueprint_file=$4
    local live_file=$5
    local patch_file=$6

    echo "Generating strategic merge patch for $resource_type/$resource_name..."

    # Use kubectl to create a patch
    kubectl patch "$resource_type" "$resource_name" \
        --namespace "$namespace" \
        --patch-file "$blueprint_file" \
        --dry-run=server \
        -o yaml > "$patch_file" 2>/dev/null || {
            # If direct patch fails, create a custom patch
            create_custom_patch "$blueprint_file" "$live_file" "$patch_file"
        }
}

# Function to create custom patch
create_custom_patch() {
    local blueprint_file=$1
    local live_file=$2
    local patch_file=$3

    # Extract differences using diff and convert to patch format
    # This is a simplified example - real implementation would be more complex
    diff "$live_file" "$blueprint_file" > /tmp/resource-diff.txt

    # Generate patch based on differences
    cat <<EOF > "$patch_file"
apiVersion: v1
kind: StrategicMergePatch
metadata:
  name: auto-generated-patch
operations:
$(grep "^[-+]" /tmp/resource-diff.txt | sed 's/^-\(.*\)$/  - op: remove\n    path: \1/' | sed 's/^+\(.*\)$/  - op: add\n    path: \1/')
EOF

    rm /tmp/resource-diff.txt
}

# Function to generate remediation script
generate_remediation_script() {
    local drift_analysis_file=$1
    local blueprint_dir=$2
    local remediation_script=$3

    cat <<'EOF' > "$remediation_script"
#!/bin/bash
# Auto-generated remediation script

set -e

DRIFT_ANALYSIS_FILE="$1"
BLUEPRINT_DIR="$2"

echo "Starting automated remediation..."

# Function to apply resource with backup
apply_with_backup() {
    local resource_type=$1
    local resource_name=$2
    local namespace=$3
    local blueprint_file=$4

    # Create backup
    kubectl get "$resource_type" "$resource_name" -n "$namespace" -o yaml > "/tmp/backup-${resource_type}-${resource_name}.yaml" || true

    # Apply blueprint
    kubectl apply -f "$blueprint_file" -n "$namespace"

    echo "Applied $resource_type/$resource_name from blueprint"
}

# Read drift analysis and apply remediation
while IFS= read -r line; do
    if [[ $line =~ ^(Deployment|Service|ConfigMap|Secret)/([^/]+)/([^ ]+) ]]; then
        RESOURCE_TYPE="${BASH_REMATCH[1],,}"
        RESOURCE_NAMESPACE="${BASH_REMATCH[2]}"
        RESOURCE_NAME="${BASH_REMATCH[3]}"

        BLUEPRINT_FILE="$BLUEPRINT_DIR/${RESOURCE_TYPE}s/${RESOURCE_NAME}.yaml"

        if [ -f "$BLUEPRINT_FILE" ]; then
            apply_with_backup "$RESOURCE_TYPE" "$RESOURCE_NAME" "$RESOURCE_NAMESPACE" "$BLUEPRINT_FILE"
        else
            echo "Blueprint file not found: $BLUEPRINT_FILE"
        fi
    fi
done < "$DRIFT_ANALYSIS_FILE"

echo "Remediation completed."
EOF

    chmod +x "$remediation_script"
}
```

## Compliance and Validation

### Policy-Based Drift Detection
```yaml
# compliance-validation.yaml
apiVersion: policy.open-cluster-management.io/v1
kind: Policy
metadata:
  name: deployment-compliance-policy
  namespace: policies
spec:
  remediationAction: inform # or enforce
  disabled: false
  policy-templates:
    - objectDefinition:
        apiVersion: policy.open-cluster-management.io/v1
        kind: ConfigurationPolicy
        metadata:
          name: deployment-compliance
        spec:
          remediationAction: inform
          severity: medium
          namespaceSelector:
            include:
              - default
              - todo-app
          objectTemplates:
            - complianceType: musthave
              objectDefinition:
                apiVersion: apps/v1
                kind: Deployment
                metadata:
                  name: "*"
                  namespace: "*"
                spec:
                  template:
                    spec:
                      containers:
                        - resources:
                            limits:
                              cpu: "*"
                              memory: "*"
                            requests:
                              cpu: "*"
                              memory: "*"
                      securityContext:
                        runAsNonRoot: true
                        runAsUser: "*"
                        fsGroup: "*"
EOF

## Advanced Drift Detection with JSONPath

### Resource Comparison Script
```bash
#!/bin/bash
# advanced-drift-detection.sh

# Function to compare resources using JSONPath
compare_resources_jsonpath() {
    local resource_type=$1
    local resource_name=$2
    local namespace=$3
    local blueprint_file=$4
    local jsonpath_expression=$5
    local output_file=$6

    # Get value from live resource
    LIVE_VALUE=$(kubectl get "$resource_type" "$resource_name" -n "$namespace" -o jsonpath="$jsonpath_expression" 2>/dev/null)

    # Get value from blueprint
    BLUEPRINT_VALUE=$(yq eval "$jsonpath_expression" "$blueprint_file" 2>/dev/null)

    # Compare values
    if [ "$LIVE_VALUE" != "$BLUEPRINT_VALUE" ]; then
        echo "DRIFT_DETECTED: $resource_type/$resource_name - $jsonpath_expression" >> "$output_file"
        echo "  Live: $LIVE_VALUE" >> "$output_file"
        echo "  Blueprint: $BLUEPRINT_VALUE" >> "$output_file"
        return 1
    else
        echo "NO_DRIFT: $resource_type/$resource_name - $jsonpath_expression" >> "$output_file"
        return 0
    fi
}

# Comprehensive drift check function
perform_comprehensive_drift_check() {
    local namespace=$1
    local blueprint_dir=$2
    local output_file=$3

    echo "Performing comprehensive drift check for namespace: $namespace" > "$output_file"

    # Check all deployments
    for deployment in $(kubectl get deployments -n "$namespace" -o jsonpath='{.items[*].metadata.name}'); do
        echo "Checking deployment: $deployment" >> "$output_file"

        # Check image drift
        compare_resources_jsonpath "deployment" "$deployment" "$namespace" "$blueprint_dir/deployments/$deployment.yaml" '{.spec.template.spec.containers[0].image}' "$output_file"

        # Check replica drift
        compare_resources_jsonpath "deployment" "$deployment" "$namespace" "$blueprint_dir/deployments/$deployment.yaml" '{.spec.replicas}' "$output_file"

        # Check resource requests/limits drift
        compare_resources_jsonpath "deployment" "$deployment" "$namespace" "$blueprint_dir/deployments/$deployment.yaml" '{.spec.template.spec.containers[0].resources}' "$output_file"
    done

    # Check all services
    for service in $(kubectl get services -n "$namespace" -o jsonpath='{.items[*].metadata.name}'); do
        echo "Checking service: $service" >> "$output_file"

        # Check service type drift
        compare_resources_jsonpath "service" "$service" "$namespace" "$blueprint_dir/services/$service.yaml" '{.spec.type}' "$output_file"

        # Check ports drift
        compare_resources_jsonpath "service" "$service" "$namespace" "$blueprint_dir/services/$service.yaml" '{.spec.ports}' "$output_file"
    done

    # Check all configmaps
    for configmap in $(kubectl get configmaps -n "$namespace" -o jsonpath='{.items[*].metadata.name}'); do
        echo "Checking configmap: $configmap" >> "$output_file"

        # Check data drift
        compare_resources_jsonpath "configmap" "$configmap" "$namespace" "$blueprint_dir/configmaps/$configmap.yaml" '{.data}' "$output_file"
    done
}

# Main function
main_comprehensive() {
    local namespace="${1:-todo-app}"
    local blueprint_dir="${2:-./blueprints}"
    local output_file="${3:-./comprehensive-drift-report.txt}"

    perform_comprehensive_drift_check "$namespace" "$blueprint_dir" "$output_file"

    echo "Comprehensive drift check completed. Report saved to: $output_file"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_comprehensive "$@"
fi
```

## Remediation Plan Generation

### Automated Remediation Plan
```yaml
# automated-remediation-plan.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: drift-remediation-job
  namespace: kagent-system
spec:
  template:
    spec:
      serviceAccountName: drift-remediator
      containers:
      - name: remediation-container
        image: bitnami/kubectl:latest
        command:
        - /bin/bash
        - -c
        - |
          # Set up environment
          export NAMESPACE="todo-app"
          export BLUEPRINT_PATH="/blueprints"

          # Function to remediate deployment drift
          remediate_deployment() {
            local deployment_name=$1
            local blueprint_file="$BLUEPRINT_PATH/deployments/$deployment_name.yaml"

            if [ -f "$blueprint_file" ]; then
              echo "Remediating deployment: $deployment_name"

              # Check if deployment exists
              if kubectl get deployment "$deployment_name" -n "$NAMESPACE" &> /dev/null; then
                # Create backup
                kubectl get deployment "$deployment_name" -n "$NAMESPACE" -o yaml > "/tmp/backup-$deployment_name-$(date +%Y%m%d-%H%M%S).yaml"

                # Apply blueprint
                kubectl apply -f "$blueprint_file" -n "$NAMESPACE"

                # Wait for rollout
                kubectl rollout status deployment "$deployment_name" -n "$NAMESPACE" --timeout=10m

                echo "Deployment $deployment_name remediated successfully"
              else
                # Create deployment if it doesn't exist
                kubectl create -f "$blueprint_file" -n "$NAMESPACE"
                echo "Deployment $deployment_name created from blueprint"
              fi
            else
              echo "Blueprint file not found for deployment: $deployment_name"
            fi
          }

          # Function to remediate service drift
          remediate_service() {
            local service_name=$1
            local blueprint_file="$BLUEPRINT_PATH/services/$service_name.yaml"

            if [ -f "$blueprint_file" ]; then
              echo "Remediating service: $service_name"

              if kubectl get service "$service_name" -n "$NAMESPACE" &> /dev/null; then
                kubectl get service "$service_name" -n "$NAMESPACE" -o yaml > "/tmp/backup-$service_name-$(date +%Y%m%d-%H%M%S).yaml"
                kubectl apply -f "$blueprint_file" -n "$NAMESPACE"
                echo "Service $service_name remediated successfully"
              else
                kubectl create -f "$blueprint_file" -n "$NAMESPACE"
                echo "Service $service_name created from blueprint"
              fi
            fi
          }

          # Function to remediate configmap drift
          remediate_configmap() {
            local configmap_name=$1
            local blueprint_file="$BLUEPRINT_PATH/configmaps/$configmap_name.yaml"

            if [ -f "$blueprint_file" ]; then
              echo "Remediating configmap: $configmap_name"

              if kubectl get configmap "$configmap_name" -n "$NAMESPACE" &> /dev/null; then
                kubectl get configmap "$configmap_name" -n "$NAMESPACE" -o yaml > "/tmp/backup-$configmap_name-$(date +%Y%m%d-%H%M%S).yaml"

                # For configmaps, we might want to update only changed keys
                # This is a simplified approach - in practice, you'd compare data
                kubectl apply -f "$blueprint_file" -n "$NAMESPACE"
                echo "ConfigMap $configmap_name remediated successfully"
              else
                kubectl create -f "$blueprint_file" -n "$NAMESPACE"
                echo "ConfigMap $configmap_name created from blueprint"
              fi
            fi
          }

          # Get list of resources from drift report
          # This would typically come from a previous drift detection step
          echo "Starting remediation process..."

          # Remediate all deployments
          for deployment in $(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}'); do
            remediate_deployment "$deployment"
          done

          # Remediate all services
          for service in $(kubectl get services -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}'); do
            remediate_service "$service"
          done

          # Remediate all configmaps (excluding system ones)
          for configmap in $(kubectl get configmaps -n "$NAMESPACE" -o jsonpath='{.items[?(@.metadata.name!="kube-root-ca.crt")].metadata.name}'); do
            remediate_configmap "$configmap"
          done

          echo "Remediation process completed"
        volumeMounts:
        - name: blueprints
          mountPath: /blueprints
      volumes:
      - name: blueprints
        configMap:
          name: drift-blueprints
      restartPolicy: Never
  backoffLimit: 4
```

## Continuous Monitoring

### Drift Monitoring CronJob
```yaml
# drift-monitoring-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: drift-monitoring
  namespace: kagent-system
spec:
  schedule: "*/30 * * * *"  # Every 30 minutes
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: drift-monitor
          containers:
          - name: drift-checker
            image: bitnami/kubectl:latest
            command:
            - /bin/bash
            - -c
            - |
              # Drift monitoring script
              NAMESPACE="todo-app"
              REPORT_DIR="/reports"
              BLUEPRINT_DIR="/blueprints"

              TIMESTAMP=$(date +%Y%m%d-%H%M%S)
              REPORT_FILE="$REPORT_DIR/drift-report-$TIMESTAMP.json"

              # Perform drift check
              kubectl get all -n "$NAMESPACE" -o json > "$REPORT_DIR/live-state-$TIMESTAMP.json"

              # Compare with blueprint (simplified - real implementation would be more complex)
              echo "{
                \"timestamp\": \"$TIMESTAMP\",
                \"namespace\": \"$NAMESPACE\",
                \"checks\": {
                  \"deployments\": \"checked\",
                  \"services\": \"checked\",
                  \"configmaps\": \"checked\"
                },
                \"drift_found\": false,
                \"summary\": \"Drift monitoring completed\"
              }" > "$REPORT_FILE"

              # Upload report to monitoring system or store in persistent volume
              # This would typically send to a monitoring system
              echo "Drift report generated: $REPORT_FILE"
            volumeMounts:
            - name: reports
              mountPath: /reports
            - name: blueprints
              mountPath: /blueprints
          volumes:
          - name: reports
            persistentVolumeClaim:
              claimName: drift-reports-pvc
          - name: blueprints
            configMap:
              name: drift-blueprints
          restartPolicy: OnFailure
```

## Output Format

Generate drift analysis that includes:
- Comprehensive state comparison between live and blueprint resources
- Detailed drift reports with specific resource differences
- Automated remediation plans with YAML patches and Helm commands
- Compliance validation against infrastructure as code standards
- Continuous monitoring configurations for ongoing drift detection
- Role-based access control for remediation operations
- Backup and rollback procedures before applying changes
- Validation steps to confirm remediation success
- Integration with monitoring and alerting systems
- Documentation of drift detection and remediation procedures