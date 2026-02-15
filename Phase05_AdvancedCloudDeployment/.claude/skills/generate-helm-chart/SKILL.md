---
name: Generate Helm Chart
description: Creates full Helm chart for Todo components (frontend/backend) from specs. Use for K8s packaging (@specs/blueprints). Triggers: 'Helm chart for backend'. Integrates helm-chart-packager agent. Inputs: app_components, replicas, resources, Neon secrets. Outputs: /helm/{app}/ chart path. Parameterized values.yaml.
---

## Usage

1. Review spec (@specs/api/rest-endpoints.md).
2. Task: subagent_type='helm-chart-packager', prompt='Generate Helm chart for {components}, replicas {n}, resources {limits}, Neon DB secrets. Store /helm/, Minikube compatible'.
3. Validate: `helm lint {path}`, template render.
4. TDD: Failing helm template test.

Use kubectl-ai/kagent; ensure Neon integration, multi-component support.