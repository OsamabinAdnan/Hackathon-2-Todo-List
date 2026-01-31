---
name: Generate Dockerfile
description: Generates optimized multi-stage Dockerfiles for Todo app components (Next.js frontend, FastAPI backend) from deployment specs. Use for containerization tasks referencing @specs/api/rest-endpoints.md or Phase 3/4 deployment blueprints. Triggers: 'containerize frontend/backend', 'Dockerfile for Next.js/FastAPI'. Integrates containerization-specialist agent. Inputs: app_type (e.g. 'Next.js frontend'), dependencies, ports, env vars. Outputs: Dockerfile path in /backend or /frontend.
---

## Usage

1. Identify app_type and spec (@specs/deployment or user req).
2. Invoke Task tool: subagent_type='containerization-specialist', prompt='Generate Dockerfile for {app_type} per spec: multi-stage build, {deps}, port {port}, env from .env'.
3. Follow agent output: Write Dockerfile, validate with `docker build --no-cache`.
4. TDD: Generate failing Docker build test first if spec has tests (@specs/testing/backend-testing.md).

Prioritize Gordon/docker ai if available; fallback CLI. Ensure spec compliance (Neon DB secrets via env).