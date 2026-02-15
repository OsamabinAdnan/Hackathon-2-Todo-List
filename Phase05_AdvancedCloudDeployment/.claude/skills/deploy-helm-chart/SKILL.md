---
name: Deploy Helm Chart
description: Installs/upgrades Helm chart on Minikube. Use post-generate-helm for Phase 3/4 (@specs/deployment). Triggers: 'deploy Helm Todo'. Integrates helm-chart-packager + k8s-ops-orchestrator. Inputs: chart_path, release_name, namespace. Outputs: status, pod logs.
---

## Usage

1. Confirm chart (@specs/blueprints).
2. Task: subagent_type='k8s-ops-orchestrator' or 'helm-chart-packager', prompt='Deploy {chart_path} as {release} in {namespace} on Minikube. Validate pods'.
3. Check: `helm status {release}`, `kubectl logs`.
4. TDD: E2E deploy failure test.

kubectl-ai wrapper; post-deploy validation.