---
name: Validate Spec Compliance
description: Checks artifacts (Dockerfiles/charts/blueprints) against Phase specs. Triggers: post-generation validation. Inputs: artifact_path, spec_path (e.g. @specs/database/schema.md). Outputs: pass/fail report + fixes. Cross-subagent.
---

## Usage

1. Read artifact/spec.
2. Analyze diffs, compliance (TDD patterns, MCP statelessness).
3. Report: Use Edit for fixes if approved.
4. TDD: Always run before commit/PR.

Invoke phase3-compliance-reviewer if needed; no manual code.