---
name: enforce-security-policies
description: Scans for misconfigurations (open ports, missing scopes, weak RBAC) and produces OPA Gatekeeper/Kyverno policy specs to block violations. Use when identifying and enforcing security policies through automated policy validation and violation prevention.
---

# Enforce Security Policies

This skill helps scan for security misconfigurations and produce OPA Gatekeeper or Kyverno policy specifications to enforce security policies and block violations in Kubernetes clusters.

## When to Use This Skill

Use this skill when:
- Scanning for security misconfigurations in Kubernetes resources
- Creating OPA Gatekeeper policies to enforce security standards
- Generating Kyverno policies for admission control
- Blocking security violations through automated policy enforcement
- Implementing security best practices as code
- Ensuring compliance with security standards
- Preventing misconfigured resources from being deployed

## Security Misconfiguration Scanning

### Open Ports Scanner
```bash
#!/bin/bash
# scan-open-ports.sh

NAMESPACE="${1:-todo-app}"
OUTPUT_FILE="${2:-./security-scan-results/open-ports-scan.txt}"

echo "Scanning for open ports in namespace: $NAMESPACE" > "$OUTPUT_FILE"

# Check for services with NodePort exposed
kubectl get services -n "$NAMESPACE" -o json | jq -r '.items[] | select(.spec.type == "NodePort") | "SERVICE: \(.metadata.name) - PORT: \(.spec.ports[0].nodePort) - PROTOCOL: \(.spec.ports[0].protocol)"' >> "$OUTPUT_FILE"

# Check for services with LoadBalancer exposing all IPs
kubectl get services -n "$NAMESPACE" -o json | jq -r '.items[] | select(.spec.type == "LoadBalancer") | select(.spec.loadBalancerSourceRanges == null or (.spec.loadBalancerSourceRanges | length == 0)) | "WARNING: \(.metadata.name) LoadBalancer allows all IPs"' >> "$OUTPUT_FILE"

# Check for pods with privileged ports
kubectl get pods -n "$NAMESPACE" -o json | jq -r '.items[] | .spec.containers[] | select(.ports[]) | .ports[] | select(.containerPort < 1024) | "PRIVILEGED PORT: Pod \(.metadata.name) container \(.name) port \(.containerPort)"' >> "$OUTPUT_FILE"

echo "Open ports scan completed. Results saved to: $OUTPUT_FILE"
```

### RBAC Scanner
```bash
#!/bin/bash
# scan-rbac.sh

NAMESPACE="${1:-todo-app}"
OUTPUT_FILE="${2:-./security-scan-results/rbac-scan.txt}"

echo "Scanning for RBAC misconfigurations in namespace: $NAMESPACE" > "$OUTPUT_FILE"

# Check for pods running as root
kubectl get pods -n "$NAMESPACE" -o json | jq -r '.items[] | select(.spec.securityContext.runAsNonRoot == false or .spec.securityContext.runAsUser == 0) | "WARNING: Pod \(.metadata.name) running as root"' >> "$OUTPUT_FILE"

# Check for privileged containers
kubectl get pods -n "$NAMESPACE" -o json | jq -r '.items[] | .spec.containers[] | select(.securityContext.privileged == true) | "PRIVILEGED CONTAINER: \(.name) in pod \(.metadata.name)"' >> "$OUTPUT_FILE"

# Check for capabilities that shouldn't be granted
kubectl get pods -n "$NAMESPACE" -o json | jq -r '.items[] | .spec.containers[] | select(.securityContext.capabilities.add[]? | contains(["NET_ADMIN", "SYS_ADMIN", "DAC_READ_SEARCH"])) | "CAPABILITIES VIOLATION: \(.name) in pod \(.metadata.name) has dangerous capabilities"' >> "$OUTPUT_FILE"

# Check for volumes that shouldn't be mounted
kubectl get pods -n "$NAMESPACE" -o json | jq -r '.items[] | .spec.volumes[] | select(.hostPath or .emptyDir) | "VOLUME VIOLATION: \(.name) in pod \(.metadata.name) has potentially dangerous volume type: \(.hostPath // .emptyDir | keys[] // "unknown")"' >> "$OUTPUT_FILE"

echo "RBAC scan completed. Results saved to: $OUTPUT_FILE"
```

## OPA Gatekeeper Policy Definitions

### Disallow Privileged Containers
```yaml
# disallow-privileged-containers.yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sdisallowprivilegedcontainers
spec:
  crd:
    spec:
      names:
        kind: K8sDisallowPrivilegedContainers
      validation:
        # Schema for the `parameters` field
        openAPIV3Schema:
          type: object
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8sdisallowprivilegedcontainers

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          container.securityContext.privileged == true
          msg := sprintf("Privileged container is not allowed: %v", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.initContainers[_]
          container.securityContext.privileged == true
          msg := sprintf("Privileged init container is not allowed: %v", [container.name])
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sDisallowPrivilegedContainers
metadata:
  name: disallow-privileged-containers
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces:
      - "todo-app"
```

### Require RunAsNonRoot
```yaml
# require-run-as-non-root.yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequirenonroot
spec:
  crd:
    spec:
      names:
        kind: K8sRequireNonRoot
      validation:
        openAPIV3Schema:
          type: object
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequirenonroot

        violation[{"msg": msg}] {
          input.review.kind.kind == "Pod"
          not input.review.object.spec.securityContext.runAsNonRoot
          container := input.review.object.spec.containers[_]
          not container.securityContext.runAsNonRoot
          msg := sprintf("Container %v must not run as root", [container.name])
        }

        violation[{"msg": msg}] {
          input.review.kind.kind == "Pod"
          not input.review.object.spec.securityContext.runAsNonRoot
          container := input.review.object.spec.initContainers[_]
          not container.securityContext.runAsNonRoot
          msg := sprintf("Init container %v must not run as root", [container.name])
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequireNonRoot
metadata:
  name: require-run-as-non-root
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces:
      - "todo-app"
```

### Disallow Host Namespace Sharing
```yaml
# disallow-host-namespace-sharing.yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sdisallowhostnamespace
spec:
  crd:
    spec:
      names:
        kind: K8sDisallowHostNamespace
      validation:
        openAPIV3Schema:
          type: object
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8sdisallowhostnamespace

        violation[{"msg": msg}] {
          input.review.kind.kind == "Pod"
          input.review.object.spec.hostPID == true
          msg := "Sharing the host PID namespace is not allowed"
        }

        violation[{"msg": msg}] {
          input.review.kind.kind == "Pod"
          input.review.object.spec.hostIPC == true
          msg := "Sharing the host IPC namespace is not allowed"
        }

        violation[{"msg": msg}] {
          input.review.kind.kind == "Pod"
          input.review.object.spec.hostNetwork == true
          msg := "Sharing the host network namespace is not allowed"
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sDisallowHostNamespace
metadata:
  name: disallow-host-namespace-sharing
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces:
      - "todo-app"
```

## Kyverno Policy Definitions

### Block Privileged Containers
```yaml
# block-privileged-containers.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: block-privileged-containers
  annotations:
    policies.kyverno.io/title: Block Privileged Containers
    policies.kyverno.io/category: Security
    policies.kyverno.io/severity: high
    policies.kyverno.io/subject: Pod
    policies.kyverno.io/description: >-
      This policy blocks the creation of privileged containers.
spec:
  validationFailureAction: enforce
  background: true
  rules:
  - name: block-privileged-containers
    match:
      any:
      - resources:
          kinds:
          - Pod
          namespaces:
          - "todo-app"
    validate:
      message: "Privileged containers are not allowed"
      foreach:
      - list: "request.object.spec.containers"
        deny:
          conditions:
            all:
            - key: "{{ element.securityContext.privileged || false }}"
              operator: Equals
              value: true
      - list: "request.object.spec.initContainers"
        deny:
          conditions:
            all:
            - key: "{{ element.securityContext.privileged || false }}"
              operator: Equals
              value: true
```

### Require Non-Root User
```yaml
# require-non-root-user.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-non-root-user
  annotations:
    policies.kyverno.io/title: Require Non-Root User
    policies.kyverno.io/category: Security
    policies.kyverno.io/severity: high
    policies.kyverno.io/subject: Pod
    policies.kyverno.io/description: >-
      This policy ensures containers run as non-root users.
spec:
  validationFailureAction: enforce
  background: true
  rules:
  - name: require-non-root-user
    match:
      any:
      - resources:
          kinds:
          - Pod
          namespaces:
          - "todo-app"
    validate:
      message: "Containers must run as non-root user (runAsNonRoot or runAsUser > 0)"
      pattern:
        spec:
          =(securityContext):
            runAsNonRoot: true
          containers:
          - name: "*"
            =(securityContext):
              =(runAsNonRoot): true
              =(runAsUser): ">0"
```

### Block Dangerous Capabilities
```yaml
# block-dangerous-capabilities.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: block-dangerous-capabilities
  annotations:
    policies.kyverno.io/title: Block Dangerous Capabilities
    policies.kyverno.io/category: Security
    policies.kyverno.io/severity: high
    policies.kyverno.io/subject: Pod
    policies.kyverno.io/description: >-
      This policy blocks dangerous capabilities from being added to containers.
spec:
  validationFailureAction: enforce
  background: true
  rules:
  - name: block-dangerous-capabilities
    match:
      any:
      - resources:
          kinds:
          - Pod
          namespaces:
          - "todo-app"
    validate:
      message: "Adding dangerous capabilities is not allowed"
      foreach:
      - list: "request.object.spec.containers"
        deny:
          conditions:
            all:
            - key: "{{ element.securityContext.capabilities.add || `[]` | contains(@, 'NET_ADMIN') }}"
              operator: Equals
              value: true
            - key: "{{ element.securityContext.capabilities.add || `[]` | contains(@, 'SYS_ADMIN') }}"
              operator: Equals
              value: true
            - key: "{{ element.securityContext.capabilities.add || `[]` | contains(@, 'DAC_READ_SEARCH') }}"
              operator: Equals
              value: true
            - key: "{{ element.securityContext.capabilities.add || `[]` | contains(@, 'SYS_PTRACE') }}"
              operator: Equals
              value: true
```

## Advanced Security Policies

### Restrict Volume Types
```yaml
# restrict-volume-types.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: restrict-volume-types
  annotations:
    policies.kyverno.io/title: Restrict Volume Types
    policies.kyverno.io/category: Security
    policies.kyverno.io/severity: medium
    policies.kyverno.io/subject: Pod
    policies.kyverno.io/description: >-
      This policy restricts volume types that can be used in pods.
spec:
  validationFailureAction: enforce
  background: true
  rules:
  - name: restrict-volume-types
    match:
      any:
      - resources:
          kinds:
          - Pod
          namespaces:
          - "todo-app"
    validate:
      message: "The following volume types are not allowed: hostPath, emptyDir, downwardAPI"
      pattern:
        spec:
          =(volumes):
          - =(hostPath): "null"
          - =(emptyDir): "null"
          - =(downwardAPI): "null"
```

### Enforce Resource Limits
```yaml
# enforce-resource-limits.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: enforce-resource-limits
  annotations:
    policies.kyverno.io/title: Enforce Resource Limits
    policies.kyverno.io/category: Security
    policies.kyverno.io/severity: medium
    policies.kyverno.io/subject: Pod
    policies.kyverno.io/description: >-
      This policy ensures all containers have resource limits defined.
spec:
  validationFailureAction: enforce
  background: true
  rules:
  - name: enforce-resource-limits
    match:
      any:
      - resources:
          kinds:
          - Pod
          namespaces:
          - "todo-app"
    validate:
      message: "All containers must have CPU and memory limits defined"
      foreach:
      - list: "request.object.spec.containers"
        pattern:
          resources:
            limits:
              cpu: "?*"
              memory: "?*"
```

### Secure Image Registries
```yaml
# secure-image-registries.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: secure-image-registries
  annotations:
    policies.kyverno.io/title: Secure Image Registries
    policies.kyverno.io/category: Security
    policies.kyverno.io/severity: high
    policies.kyverno.io/subject: Pod
    policies.kyverno.io/description: >-
      This policy only allows images from trusted registries.
spec:
  validationFailureAction: enforce
  background: true
  rules:
  - name: secure-image-registries
    match:
      any:
      - resources:
          kinds:
          - Pod
          namespaces:
          - "todo-app"
    validate:
      message: "Images must be from trusted registries: docker.io/library/, gcr.io/, quay.io/"
      foreach:
      - list: "request.object.spec.containers"
        deny:
          conditions:
            all:
            - key: "{{ element.image }}"
              operator: AnyNotIn
              value: ["docker.io/library/*", "gcr.io/*", "quay.io/*", "your-registry.com/*"]
```

## Policy Enforcement Dashboard

### Security Policy Status Dashboard
```yaml
# security-policy-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-policy-dashboard
  namespace: kyverno
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "Security Policy Compliance Dashboard",
        "rows": [
          {
            "title": "Policy Violations",
            "panels": [
              {
                "title": "Violations by Policy",
                "type": "graph",
                "targets": [
                  {
                    "query": "kyverno_policy_results_total{result='fail'}",
                    "legendFormat": "{{ policy }}"
                  }
                ]
              },
              {
                "title": "Violations by Resource Type",
                "type": "graph",
                "targets": [
                  {
                    "query": "kyverno_policy_results_total{result='fail'}",
                    "legendFormat": "{{ resource_kind }}"
                  }
                ]
              }
            ]
          },
          {
            "title": "Admission Control",
            "panels": [
              {
                "title": "Admission Requests",
                "type": "graph",
                "targets": [
                  {
                    "query": "kyverno_admission_requests_total",
                    "legendFormat": "Requests"
                  }
                ]
              },
              {
                "title": "Admission Blocked",
                "type": "graph",
                "targets": [
                  {
                    "query": "kyverno_admission_review_duration_seconds_count{allowed='false'}",
                    "legendFormat": "Blocked Requests"
                  }
                ]
              }
            ]
          }
        ]
      }
    }
```

## Policy Audit and Reporting

### Policy Audit Script
```bash
#!/bin/bash
# policy-audit.sh

NAMESPACE="${1:-todo-app}"
OUTPUT_DIR="${2:-./policy-audit-results}"

mkdir -p "$OUTPUT_DIR"

echo "Starting security policy audit for namespace: $NAMESPACE" > "$OUTPUT_DIR/audit-summary.txt"

# Check existing pods against security policies
echo "Checking existing pods for security compliance..." >> "$OUTPUT_DIR/audit-summary.txt"

kubectl get pods -n "$NAMESPACE" -o json | jq -r '
.items[] as $pod |
"Pod: \($pod.metadata.name)" +
"\n  Run as non-root: \($pod.spec.securityContext.runAsNonRoot // false)" +
"\n  Privileged containers: \([$pod.spec.containers[]?.securityContext.privileged // false] | map(select(. == true)) | length > 0)" +
"\n  Host PID: \($pod.spec.hostPID // false)" +
"\n  Host Network: \($pod.spec.hostNetwork // false)" +
"\n  Dangerous capabilities: \([$pod.spec.containers[]?.securityContext.capabilities.add[]?] | map(select(test("NET_ADMIN|SYS_ADMIN|DAC_READ_SEARCH"))) | length > 0)\n"
' >> "$OUTPUT_DIR/pod-security-analysis.txt"

# Check existing services for security issues
echo "Checking services for security issues..." >> "$OUTPUT_DIR/audit-summary.txt"

kubectl get services -n "$NAMESPACE" -o json | jq -r '
.items[] as $svc |
"Service: \($svc.metadata.name)" +
"\n  Type: \($svc.spec.type)" +
"\n  LoadBalancer Source Ranges: \($svc.spec.loadBalancerSourceRanges // "None - allows all IPs")" +
"\n  NodePorts: \([$svc.spec.ports[]? | select(.nodePort)] | map(.nodePort) | join(", "))\n"
' >> "$OUTPUT_DIR/service-security-analysis.txt"

# Generate compliance report
TOTAL_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers | wc -l)
SECURE_PODS=$(kubectl get pods -n "$NAMESPACE" -o json | jq -r '
[
  .items[] |
  select(
    (.spec.securityContext.runAsNonRoot // false) == true and
    ([.spec.containers[]?.securityContext.privileged // false] | all(. == false)) and
    (.spec.hostPID // false) == false and
    (.spec.hostNetwork // false) == false
  )
] | length
')

echo "Compliance Summary:" >> "$OUTPUT_DIR/audit-summary.txt"
echo "Total Pods: $TOTAL_PODS" >> "$OUTPUT_DIR/audit-summary.txt"
echo "Secure Pods: $SECURE_PODS" >> "$OUTPUT_DIR/audit-summary.txt"
echo "Compliance Rate: $(( SECURE_PODS * 100 / TOTAL_PODS ))%" >> "$OUTPUT_DIR/audit-summary.txt"

echo "Policy audit completed. Results saved to: $OUTPUT_DIR"
```

## Policy Remediation

### Auto-remediation Policy
```yaml
# auto-remediation-policy.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: auto-remediation-policy
  annotations:
    policies.kyverno.io/title: Auto-Remediation Policy
    policies.kyverno.io/category: Security
    policies.kyverno.io/severity: medium
    policies.kyverno.io/subject: Pod
    policies.kyverno.io/description: >-
      This policy automatically adds security context to pods that don't have it.
spec:
  validationFailureAction: audit  # Use audit mode for auto-remediation
  background: true
  rules:
  - name: add-security-context
    match:
      any:
      - resources:
          kinds:
          - Pod
          namespaces:
          - "todo-app"
    mutate:
      patchStrategicMerge:
        spec:
          =(securityContext):
            runAsNonRoot: true
            runAsUser: 1000
            fsGroup: 2000
          containers:
          - =(securityContext):
              =(allowPrivilegeEscalation): false
              =(readOnlyRootFilesystem): true
              =(runAsNonRoot): true
              =(capabilities):
                drop:
                - ALL
```

## Output Format

Generate security policies that include:
- OPA Gatekeeper constraint templates and constraints
- Kyverno policy definitions for admission control
- Security scanning scripts for vulnerability detection
- Compliance dashboards for monitoring policy adherence
- Automated remediation policies for fixing violations
- Audit and reporting mechanisms for security posture
- Integration with monitoring and alerting systems
- Comprehensive documentation for each policy
- Validation and testing procedures for policies
- Rollback and exception handling for policy enforcement