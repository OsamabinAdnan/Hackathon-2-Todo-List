# Subagent Configuration for Kubernetes Deployments

## Overview
This document outlines the configuration for various subagents used in the AI-assisted Kubernetes deployment process.

## Containerization Specialist Agent
Purpose: Handle Docker containerization tasks
Triggers: When containerizing applications
Configuration:
- Uses Gordon (Docker AI Agent) for intelligent Docker operations
- Optimizes Dockerfiles for security and performance
- Generates .dockerignore files for efficiency

## Helm Chart Packager Agent
Purpose: Generate and manage Helm charts
Triggers: When creating Kubernetes deployment packages
Configuration:
- Creates standardized Helm chart structures
- Generates templates for common Kubernetes resources
- Validates chart syntax and structure

## Kubernetes Operations Orchestrator Agent
Purpose: Manage Kubernetes deployment operations
Triggers: When deploying to Kubernetes clusters
Configuration:
- Integrates with kubectl-ai for natural language commands
- Coordinates deployment workflows
- Manages resource dependencies

## Blueprint Generator Agent
Purpose: Create reusable deployment blueprints
Triggers: When documenting deployment processes
Configuration:
- Generates documentation templates
- Captures best practices
- Creates reusable configuration patterns

## Integration Points
- All agents follow spec-driven development principles
- Coordinate through shared configuration files
- Maintain consistent naming and labeling conventions