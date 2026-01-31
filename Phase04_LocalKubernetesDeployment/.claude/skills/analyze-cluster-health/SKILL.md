---
name: Analyze Cluster Health
description: Diagnoses Minikube issues for Todo deployments. Triggers: 'pods failing', 'cluster health'. Integrates k8s-ops-orchestrator. Inputs: query (e.g. 'why backend pods crashing'). Outputs: health report + fixes.
---

## Usage

1. User query + spec context.
2. Task: subagent_type='k8s-ops-orchestrator', prompt='Analyze {query} on Minikube Todo cluster. Report issues/recommendations'.
3. Follow: `kubectl describe pods`, logs.
4. TDD: Simulated failure tests.

kagent/kubectl-ai; AIOps monitoring.