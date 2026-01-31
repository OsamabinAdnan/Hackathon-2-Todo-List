---
name: Build and Push Docker Image
description: Builds Docker image from Dockerfile and pushes to registry (local Minikube/Docker Hub). Use after generate-dockerfile for Phase 3/4 deployments (@specs/features/deployment.md). Triggers: 'build image', 'docker push Todo backend'. Integrates containerization-specialist. Inputs: dockerfile_path, image_tag, registry_url. Outputs: image ID, push confirmation.
---

## Usage

1. Confirm Dockerfile exists (Read tool).
2. Invoke Task: subagent_type='containerization-specialist', prompt='Build/push image from {dockerfile_path}, tag {image_tag}, registry {registry_url}. Handle errors, spec compliance'.
3. Validate: `docker images | grep {tag}`, push logs.
4. TDD: Test build failure scenarios first.

Gordon/docker ai preferred; CLI fallback (`docker build -t {tag} . && docker push`). Error handling for failures.