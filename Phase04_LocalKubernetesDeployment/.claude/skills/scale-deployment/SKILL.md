---
name: Scale Deployment
description: Scales K8s deployments for Todo app load handling. Use for ops (@specs/features/scaling). Triggers: 'scale backend'. Integrates k8s-ops-orchestrator. Inputs: deployment_name, replicas, limits. Outputs: scale status.
---

## Usage

1. Spec ref (@specs/api/rest-endpoints.md).
2. Task: subagent_type='k8s-ops-orchestrator', prompt='Scale {deployment} to {replicas}, limits {cpu/mem}. Monitor stability'.
3. Verify: `kubectl get deployments`, metrics.
4. TDD: Scale test under load.

kubectl-ai; dynamic scaling blueprints.