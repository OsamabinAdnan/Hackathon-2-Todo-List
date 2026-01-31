# Troubleshooting Guide for Todo Chatbot Kubernetes Deployment

## Common Issues and Solutions

### Pods Stuck in Pending State
**Symptoms**: Pods show status "Pending"
**Causes**:
- Insufficient resources (CPU/Memory)
- Node selector constraints
- Persistent volume issues

**Solutions**:
```bash
# Check resource usage
kubectl top nodes
kubectl describe nodes

# Check pod events
kubectl describe pod <pod-name>

# Adjust resource requests/limits
helm upgrade <release-name> ./helm/todo-chatbot/ --set backend.resources.requests.cpu=200m
```

### Pods in CrashLoopBackOff
**Symptoms**: Pods continuously restarting
**Causes**:
- Application startup errors
- Missing configuration
- Database connection issues

**Solutions**:
```bash
# Check pod logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # Previous instance logs

# Check environment variables
kubectl exec <pod-name> -- env

# Test database connection
kubectl run test-db --image=busybox --rm -it -- wget <database-url>
```

### Services Not Accessible
**Symptoms**: Cannot reach application via service
**Causes**:
- Incorrect service configuration
- Pod network issues
- Firewall rules

**Solutions**:
```bash
# Check service configuration
kubectl get svc <service-name> -o yaml

# Check endpoints
kubectl get ep <service-name>

# Test connectivity from inside cluster
kubectl run test-connectivity --image=curlimages/curl -it --rm -- curl -v http://<service-name>:<port>
```

### Ingress Not Working
**Symptoms**: Cannot access application via Ingress URL
**Causes**:
- Ingress controller not installed
- Incorrect host/path configuration
- TLS certificate issues

**Solutions**:
```bash
# Check ingress configuration
kubectl get ingress <ingress-name> -o yaml

# Check ingress controller logs
kubectl logs -l app.kubernetes.io/name=nginx-ingress-controller

# Verify host resolution
kubectl exec -it <any-pod> -- nslookup <your-host>
```

### Database Connection Failures
**Symptoms**: Application logs show database connection errors
**Causes**:
- Incorrect database URL
- Network policies blocking connection
- Database credentials issues

**Solutions**:
```bash
# Verify secrets are mounted correctly
kubectl exec <backend-pod> -- env | grep DATABASE

# Test database connectivity
kubectl run test-db --image=nicolaka/netshoot -it --rm -- bash
# Inside netshoot container:
# nc -zv <database-host> <database-port>
```

### Health Checks Failing
**Symptoms**: Pods show as unhealthy, restart loops
**Causes**:
- Health check endpoints not responding
- Application taking too long to start
- Network issues

**Solutions**:
```bash
# Check health check configuration
kubectl get deployment <deployment-name> -o yaml | grep -A 10 -B 10 health

# Test health endpoint from within cluster
kubectl exec <pod-name> -- curl -v http://localhost:<port>/health
```

## AI-Assisted Troubleshooting

### Using kubectl-ai
```bash
# Get detailed pod information
kubectl-ai "show me detailed information about failing backend pods"

# Check resource usage
kubectl-ai "show me resource usage by namespace"

# Find issues with pods
kubectl-ai "check why pods are failing"
```

### Using kagent
```bash
# Analyze cluster health
kagent "analyze cluster health"

# Find resource issues
kagent "find resource bottlenecks in todo namespace"

# Optimize cluster
kagent "optimize resource allocation"
```

## Security Issues

### Image Pull Issues
**Symptoms**: ImagePullBackOff errors
**Solutions**:
```bash
# Check image pull secrets
kubectl get secrets | grep registry

# Verify image exists
docker pull <image-name>
```

### RBAC Issues
**Symptoms**: Permission denied errors
**Solutions**:
```bash
# Check pod service account
kubectl get pod <pod-name> -o yaml | grep serviceAccount

# Verify RBAC bindings
kubectl auth can-i --list --as=system:serviceaccount:<namespace>:<service-account>
```

## Performance Issues

### High Resource Usage
**Symptoms**: CPU/Memory spikes
**Solutions**:
```bash
# Check resource usage
kubectl top pods
kubectl top nodes

# Adjust resource limits
helm upgrade <release-name> ./helm/todo-chatbot/ \
  --set backend.resources.limits.cpu=1 \
  --set backend.resources.limits.memory=1Gi
```

### Slow Response Times
**Symptoms**: Application responds slowly
**Solutions**:
```bash
# Check for bottlenecks
kubectl top pods
kubectl logs <slow-pod> --since=5m

# Scale problematic deployments
kubectl scale deployment <deployment-name> --replicas=3
```

## Networking Issues

### Service Mesh Problems
**Symptoms**: Inter-service communication fails
**Solutions**:
```bash
# Test connectivity between services
kubectl run test --image=curlimages/curl -it --rm -- curl -v http://backend-service:8000/health

# Check network policies
kubectl get networkpolicy
```

## Monitoring Commands

### Useful Monitoring Commands
```bash
# Watch all pods in real-time
kubectl get pods -w

# Monitor events
kubectl get events --watch

# Monitor logs across deployments
kubectl logs -l app=backend --follow

# Resource monitoring
kubectl top pods --containers
```

## Quick Fixes

### Restart All Pods
```bash
kubectl rollout restart deployment -n <namespace>
```

### Rollback to Previous Version
```bash
kubectl rollout undo deployment/<deployment-name>
```

### Scale to Zero and Back
```bash
kubectl scale deployment/<deployment-name> --replicas=0
kubectl scale deployment/<deployment-name> --replicas=<original-count>
```

## When to Seek Help

Contact your DevOps team when:
- Issues persist after trying the above solutions
- You suspect infrastructure-level problems
- Security vulnerabilities are suspected
- Performance issues impact users significantly