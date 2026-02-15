# Tasks: Phase IV: Local Kubernetes Deployment

## Feature
Deploy the complete Todo AI Chatbot (Next.js frontend + FastAPI backend with Neon DB and MCP server) to Minikube using Helm charts and AI-assisted DevOps tools, ensuring all basic task features remain functional.

## Phase 1: Setup and Environment Preparation

- [X] T001 Create helm directory structure in root project directory
- [X] T002 Verify Docker Desktop with Gordon AI is enabled and accessible
- [X] T003 Verify Minikube installation and start local cluster
- [X] T004 Verify Helm 3.x installation and initialize
- [X] T005 Install kubectl-ai plugin for AI-assisted Kubernetes operations
- [X] T006 Install kagent for cluster analysis and optimization
- [X] T007 [P] Create scripts directory for deployment automation
- [X] T008 [P] Initialize Helm chart structure in helm/todo-chatbot/

## Phase 2: Foundational Tasks

- [X] T009 [P] Create build-and-push.sh script for AI-assisted Docker operations
- [X] T010 [P] Create deploy.sh script for AI-assisted Kubernetes operations
- [X] T011 Set up environment variables for Neon DB connection in values.yaml
- [X] T012 Configure security contexts for containerized applications
- [X] T013 Set up resource requests and limits for deployments
- [X] T014 Create initial Chart.yaml for the todo-chatbot Helm chart
- [X] T015 [P] Create initial values.yaml with default configurations

## Phase 3: [US1] Frontend Containerization

- [X] T016 [US1] Create optimized Dockerfile for Next.js frontend using Gordon
- [X] T017 [US1] Build frontend Docker image using Gordon's AI assistance
- [X] T018 [US1] Test frontend container locally before deployment
- [X] T019 [US1] Create frontend deployment manifest (frontend-deployment.yaml)
- [X] T020 [US1] Create frontend service manifest with NodePort (frontend-service.yaml)
- [X] T021 [US1] Configure frontend environment variables for API connection
- [X] T022 [US1] Set up health checks for frontend container
- [X] T023 [US1] Validate frontend container with security scanning

## Phase 4: [US2] Backend Containerization

- [X] T024 [US2] Optimize existing backend Dockerfile using Gordon's AI assistance
- [ ] T025 [US2] Build backend Docker image using Gordon's AI assistance
- [ ] T026 [US2] Test backend container locally with mock DB connection
- [X] T027 [US2] Create backend deployment manifest (backend-deployment.yaml)
- [X] T028 [US2] Create backend service manifest with ClusterIP (backend-service.yaml)
- [X] T029 [US2] Configure backend environment variables for Neon DB and JWT
- [X] T030 [US2] Set up health checks for backend container
- [ ] T031 [US2] Validate backend container with security scanning

## Phase 5: [US3] MCP Server Deployment

- [ ] T032 [US3] Create MCP server deployment manifest (mcp-deployment.yaml)
- [ ] T033 [US3] Create MCP server service manifest (mcp-service.yaml)
- [ ] T034 [US3] Configure MCP server to connect with backend authentication
- [ ] T035 [US3] Set up health checks for MCP server container
- [ ] T036 [US3] Validate MCP server configuration with JWT verification

## Phase 6: [US4] Configuration and Secrets Management

- [ ] T037 [US4] Create ConfigMap for non-sensitive configuration (configmap.yaml)
- [ ] T038 [US4] Create Secret for sensitive data (NEON_DB_URL, JWT_SECRET) (secret.yaml)
- [ ] T39 [US4] Configure proper mounting of ConfigMap in deployments
- [ ] T040 [US4] Configure proper mounting of Secrets in deployments
- [ ] T041 [US4] Set up proper permissions for accessing secrets in containers

## Phase 7: [US5] Helm Chart Completion

- [X] T042 [US5] Complete Helm chart templates with proper value substitutions
- [X] T043 [US5] Create ingress configuration template (ingress.yaml)
- [X] T044 [US5] Implement proper dependency management in Chart.yaml
- [X] T045 [US5] Create NOTES.txt with post-installation instructions
- [X] T046 [US5] Add helper templates for common labeling patterns (_helpers.tpl)
- [X] T047 [US5] Validate Helm chart syntax and structure

## Phase 8: [US6] Deployment and AI-Assisted Operations

- [ ] T048 [US6] Load Docker images into Minikube using minikube image load
- [ ] T049 [US6] Install Helm chart to Minikube using Helm install
- [ ] T050 [US6] Verify all pods are running and ready using kubectl
- [ ] T051 [US6] Test basic connectivity between frontend and backend
- [ ] T052 [US6] Use kubectl-ai to scale frontend deployment to 2 replicas
- [ ] T053 [US6] Use kubectl-ai to check why pods are failing (if any issues)
- [ ] T054 [US6] Use kagent to analyze cluster health
- [ ] T055 [US6] Verify application accessibility via Minikube service URL

## Phase 9: [US7] Post-Deployment Validation

- [ ] T056 [US7] Test Phase 3 functionality: Add task via chat interface
- [ ] T057 [US7] Test Phase 3 functionality: List tasks via chat interface
- [ ] T058 [US7] Test Phase 3 functionality: Update task via chat interface
- [ ] T059 [US7] Test Phase 3 functionality: Complete task via chat interface
- [ ] T060 [US7] Test Phase 3 functionality: Delete task via chat interface
- [ ] T061 [US7] Verify multi-user isolation (JWT + user_id filtering) in Kubernetes
- [ ] T062 [US7] Test JWT authentication flow in containerized environment
- [ ] T063 [US7] Validate Neon DB connectivity from within Kubernetes pods

## Phase 10: [US8] AI Operations and Scaling

- [ ] T064 [US8] Use kubectl-ai to scale backend to handle more load
- [ ] T065 [US8] Use kagent to optimize resource allocation
- [ ] T066 [US8] Demonstrate horizontal pod autoscaling configuration
- [ ] T067 [US8] Verify that scaling operations maintain application functionality
- [ ] T068 [US8] Test health monitoring with readiness/liveness probes
- [ ] T069 [US8] Document AI operations used for deployment and scaling

## Phase 11: [US9] Blueprint Generation and Reusability

- [X] T070 [US9] Create reusable blueprint for containerization process
- [X] T071 [US9] Create reusable blueprint for Helm chart generation
- [X] T072 [US9] Document the deployment process as a reusable template
- [X] T073 [US9] Create subagent configuration for future deployments
- [X] T074 [US9] Generate skills for common Kubernetes operations
- [X] T075 [US9] Document lessons learned and best practices for AI-assisted deployment

## Phase 12: Polish & Cross-Cutting Concerns

- [X] T076 Update CLAUDE.md with Phase 4 deployment instructions
- [X] T077 Create comprehensive README for the Kubernetes deployment
- [X] T078 Document troubleshooting procedures for common deployment issues
- [X] T079 Add health check endpoints to backend for Kubernetes readiness
- [ ] T080 Perform final validation of all Phase 3 features in Kubernetes environment
- [ ] T081 Verify 99% pod availability and deployment time under 5 minutes
- [X] T082 Clean up any temporary files or test configurations
- [X] T083 Document the +400 bonus points earned through reusable intelligence and blueprints

## Dependencies

- **US1 (Frontend Containerization)**: Must complete before US6 (Deployment)
- **US2 (Backend Containerization)**: Must complete before US6 (Deployment)
- **US3 (MCP Server Deployment)**: Must complete before US6 (Deployment)
- **US4 (Configuration and Secrets)**: Must complete before US6 (Deployment)
- **US5 (Helm Chart Completion)**: Must complete before US6 (Deployment)
- **US6 (Deployment)**: Must complete before US7 (Post-Deployment Validation)
- **US6 (Deployment)**: Must complete before US8 (AI Operations and Scaling)
- **US6 (Deployment)**: Must complete before US9 (Blueprint Generation)

## Parallel Execution Opportunities

- **T016-T024**: Frontend and backend containerization can be done in parallel
- **T019-T027-T032**: Creating deployment manifests can be done in parallel
- **T020-T028-T033**: Creating service manifests can be done in parallel
- **T037-T038**: Creating ConfigMap and Secret can be done in parallel
- **T056-T057-T058-T059-T060**: Testing functionality can be done in parallel sequences

## Implementation Strategy

1. **MVP First**: Focus on completing US1-US6 to get a basic working deployment
2. **Incremental Delivery**: Each user story phase delivers a testable increment
3. **AI-First Approach**: Use Gordon, kubectl-ai, and kagent for all operations
4. **Validation-Driven**: Test each component before moving to the next phase
5. **Documentation-Driven**: Document all AI operations and blueprints as we go