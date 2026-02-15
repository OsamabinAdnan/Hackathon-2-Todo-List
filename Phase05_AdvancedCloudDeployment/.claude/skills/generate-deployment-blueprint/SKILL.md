---
name: Generate Deployment Blueprint
description: Creates reusable YAML blueprints for Minikube/DOKS Todo deployments from specs. +200 bonus. Triggers: 'deployment blueprint'. Integrates blueprint-generator. Inputs: infrastructure_reqs (e.g. 'Minikube + Helm + Neon'). Outputs: /specs/blueprints/{name}.yaml.
---

## Usage

1. High-level spec (@specs/features/deployment.md).
2. Task: subagent_type='blueprint-generator', prompt='Generate blueprint for {reqs}, spec-driven YAML for Todo app'.
3. Validate: kubeval, spec compliance.
4. TDD: Blueprint validation tests.

Extensible to Phase V; cloud-native automation.