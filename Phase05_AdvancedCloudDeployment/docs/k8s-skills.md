# Kubernetes Operation Skills for AI-Assisted Deployments

## Common Operations

### Deployment Management
- `kubectl-ai "deploy the todo frontend with 2 replicas"`
- `kubectl-ai "scale the backend to handle more load"`
- `kubectl-ai "check why the pods are failing"`

### Cluster Analysis
- `kagent "analyze the cluster health"`
- `kagent "optimize resource allocation"`
- `kubectl-ai "show resource usage by namespace"`

### Service Management
- `kubectl-ai "expose frontend service on port 3000"`
- `kubectl-ai "create ingress for the application"`

### Troubleshooting
- `kubectl-ai "get logs for failing backend pods"`
- `kubectl-ai "describe why frontend is not ready"`
- `kagent "show cluster events"`

## AI Command Patterns
- Use natural language for complex operations
- Specify desired state rather than individual commands
- Include context about the application when possible

## Best Practices
- Always verify AI-generated commands before execution
- Use dry-run options when available
- Monitor resources after AI-assisted scaling
- Validate security configurations post-deployment

## Safety Guidelines
- Never expose secrets in AI prompts
- Review AI-generated configurations for security
- Validate network policies after AI-assisted changes
- Confirm backup procedures before AI-assisted operations