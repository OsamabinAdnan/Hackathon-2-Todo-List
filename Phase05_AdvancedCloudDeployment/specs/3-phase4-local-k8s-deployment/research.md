# Research: Phase IV: Local Kubernetes Deployment

## Phase 0: Research and Unknown Resolution

### Decision: Docker AI Agent (Gordon) Availability and Usage
**Rationale**: Gordon is prioritized for AI-assisted Docker operations as specified in requirements. If unavailable due to regional restrictions, standard Docker CLI commands will be used.
**Alternatives considered**:
- Standard Docker CLI commands (fallback option)
- Claude Code-generated Docker commands (when Gordon unavailable)

### Decision: Subagent Orchestration Strategy
**Rationale**: Containerization Subagent first, then Helm Chart Subagent, coordinated by Kubernetes Operations Subagent with Blueprint Generator for reusability. This earns +200 Reusable Intelligence and +200 Blueprints bonuses.
**Alternatives considered**:
- Manual implementation (violates constitution)
- Single combined agent (reduces modularity and reusability)

### Decision: Helm Chart Configuration
**Rationale**: Single chart with separate frontend/backend deployments chosen for simplicity, with parameterized values.yaml for Neon DB secrets/JWT. This maintains security and scalability.
**Alternatives considered**:
- Multi-chart approach (adds complexity without clear benefits for this scope)
- Single deployment (violates separation of concerns)

### Decision: Minikube Service Exposure
**Rationale**: Port-forward prioritized for local testing, though NodePort services will be used for Minikube compatibility. This provides reliable local access.
**Alternatives considered**:
- LoadBalancer service (emulates cloud provider LB in Minikube but unnecessary overhead)
- Ingress controller (more complex than needed for local deployment)

### AI DevOps Tools Research

#### Gordon (Docker AI Agent)
- Available in Docker Desktop 4.53+ Beta features
- Commands: `docker ai "what can you do?"`, `docker ai "generate Dockerfile for Next.js app"`
- Enables AI-assisted Docker operations as required

#### kubectl-ai (Kubernetes AI Agent)
- Provides natural language Kubernetes commands
- Commands: `kubectl-ai "deploy frontend with 2 replicas"`, `kubectl-ai "scale backend to handle more load"`
- Enables AI-assisted Kubernetes operations as required

#### Kagent (Kubernetes Agent)
- Advanced cluster analysis and troubleshooting
- Commands: `kagent "analyze cluster health"`, `kagent "optimize resource allocation"`
- Provides deeper Kubernetes insights as required

### Architecture Considerations
- **Containerization**: Both Next.js frontend and FastAPI backend must be containerized with optimized Dockerfiles
- **Kubernetes Native**: Deploy to Minikube using industry-standard practices
- **Helm Packaging**: Package applications using Helm for configuration management
- **Declarative Infrastructure**: All infrastructure defined in code with version control
- **AI-Assisted Operations**: Leverage Gordon, kubectl-ai and kagent for Kubernetes operations
- **Reusable Intelligence**: Implement subagents and skills for modular, reusable DevOps tasks
- **Cloud-Native Blueprints**: Develop blueprints powered by Claude Code Agent Skills

### Security Considerations
- Maintain Neon DB and JWT authentication compatibility in containerized environment
- Ensure user isolation (JWT + user_id filtering) preserved in Kubernetes deployment
- Proper secrets management for sensitive data (NEON_DB_URL, JWT_SECRET, etc.)
- Network policies for service-to-service communication