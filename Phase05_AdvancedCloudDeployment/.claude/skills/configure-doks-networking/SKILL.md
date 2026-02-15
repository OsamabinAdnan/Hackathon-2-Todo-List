---
name: configure-doks-networking
description: Outputs specs for LoadBalancer services, Ingress with TLS (cert-manager), external DNS, and DO firewall rules for secure external access. Use when configuring networking for DOKS applications with proper TLS termination, external DNS, and security rules.
---

# Configure DOKS Networking

This skill helps configure networking for DigitalOcean Kubernetes Service applications with proper LoadBalancer services, Ingress with TLS termination, external DNS integration, and DigitalOcean firewall rules for secure external access.

## When to Use This Skill

Use this skill when:
- Configuring external access to DOKS applications
- Setting up TLS/SSL termination with cert-manager
- Configuring external DNS for application domains
- Setting up DigitalOcean firewall rules for security
- Implementing secure ingress patterns for DOKS
- Configuring load balancing and traffic routing

## LoadBalancer Service Configuration

### Basic LoadBalancer Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend-loadbalancer
  namespace: todo-app
  annotations:
    # DigitalOcean specific annotations
    service.beta.kubernetes.io/do-loadbalancer-enable-proxy-protocol: "true"
    service.beta.kubernetes.io/do-loadbalancer-certificate-id: "your-cert-id"
    service.beta.kubernetes.io/do-loadbalancer-redirect-http-to-https: "true"
    service.beta.kubernetes.io/do-loadbalancer-tls-passthrough: "false"
    service.beta.kubernetes.io/do-loadbalancer-size-slug: "lb-small"
    service.beta.kubernetes.io/do-loadbalancer-algorithm: "round_robin"
spec:
  type: LoadBalancer
  externalTrafficPolicy: Local
  ports:
  - name: http
    port: 80
    targetPort: 3000
    protocol: TCP
  - name: https
    port: 443
    targetPort: 3000
    protocol: TCP
  selector:
    app: todo-frontend
```

### Backend LoadBalancer Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend-loadbalancer
  namespace: todo-app
  annotations:
    service.beta.kubernetes.io/do-loadbalancer-enable-proxy-protocol: "true"
    service.beta.kubernetes.io/do-loadbalancer-certificate-id: "your-backend-cert-id"
    service.beta.kubernetes.io/do-loadbalancer-redirect-http-to-https: "true"
    service.beta.kubernetes.io/do-loadbalancer-size-slug: "lb-medium"
    service.beta.kubernetes.io/do-loadbalancer-firewall-allow: "0.0.0.0/0"  # Allow all IPs
    service.beta.kubernetes.io/do-loadbalancer-firewall-deny: "192.168.1.0/24"  # Deny specific subnet
spec:
  type: LoadBalancer
  externalTrafficPolicy: Local
  ports:
  - name: http
    port: 80
    targetPort: 8000
    protocol: TCP
  - name: https
    port: 443
    targetPort: 8000
    protocol: TCP
  selector:
    app: todo-backend
```

## Ingress Configuration

### Nginx Ingress Controller Setup
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
spec:
  interval: 5m
  chart:
    spec:
      chart: ingress-nginx
      version: "4.8.3"
      sourceRef:
        kind: HelmRepository
        name: ingress-nginx
        namespace: flux-system
  values:
    controller:
      replicaCount: 2
      service:
        type: LoadBalancer
        annotations:
          service.beta.kubernetes.io/do-loadbalancer-enable-proxy-protocol: "true"
          service.beta.kubernetes.io/do-loadbalancer-redirect-http-to-https: "true"
          service.beta.kubernetes.io/do-loadbalancer-size-slug: "lb-small"
      config:
        use-forwarded-headers: "true"
        ssl-redirect: "true"
        force-ssl-redirect: "true"
        proxy-body-size: "10m"
        proxy-buffer-size: "16k"
        proxy-connect-timeout: "60s"
        proxy-send-timeout: "60s"
        proxy-read-timeout: "60s"
        proxy-buffering: "on"
        hsts: "true"
        hsts-include-subdomains: "true"
        hsts-max-age: "15724800"
        hsts-preload: "true"
      resources:
        limits:
          cpu: 1000m
          memory: 1Gi
        requests:
          cpu: 100m
          memory: 256Mi
```

### Application Ingress with TLS
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-app-ingress
  namespace: todo-app
  annotations:
    # Cert-Manager annotations
    cert-manager.io/cluster-issuer: "letsencrypt-prod"

    # Nginx annotations
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-buffer-size: "16k"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60s"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60s"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60s"
    nginx.ingress.kubernetes.io/proxy-buffering: "on"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_set_header X-Forwarded-Proto $http_x_forwarded_proto;
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"

    # Security headers
    nginx.ingress.kubernetes.io/configuration-snippet: |
      add_header X-Frame-Options "SAMEORIGIN" always;
      add_header X-Content-Type-Options "nosniff" always;
      add_header X-XSS-Protection "1; mode=block" always;
      add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
      add_header Referrer-Policy "strict-origin-when-cross-origin" always;
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - todo.yourdomain.com
    secretName: todo-app-tls
  rules:
  - host: todo.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-frontend
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: todo-backend
            port:
              number: 8000
      - path: /chat
        pathType: Prefix
        backend:
          service:
            name: todo-mcp-server
            port:
              number: 8080
      - path: /health
        pathType: Exact
        backend:
          service:
            name: todo-backend
            port:
              number: 8000
```

## Cert-Manager Configuration

### ClusterIssuer for Let's Encrypt
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-private-key
    solvers:
    - http01:
        ingress:
          class: nginx
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-staging-private-key
    solvers:
    - http01:
        ingress:
          class: nginx
```

## External DNS Configuration

### ExternalDNS Deployment
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: external-dns
  namespace: external-dns
spec:
  interval: 5m
  chart:
    spec:
      chart: external-dns
      version: "1.13.1"
      sourceRef:
        kind: HelmRepository
        name: external-dns
        namespace: flux-system
  values:
    provider: digitalocean
    digitalocean:
      apiToken:
        valueFrom:
          secretKeyRef:
            name: do-token
            key: token
    sources:
    - ingress
    - service
    domainFilters:
    - "yourdomain.com"
    txtOwnerId: "todo-app"
    txtPrefix: "k8s."
    policy: sync
    registry: txt
    interval: "1m"
    logLevel: info
    resources:
      limits:
        cpu: 100m
        memory: 128Mi
      requests:
        cpu: 50m
        memory: 64Mi
```

### DO Token Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: do-token
  namespace: external-dns
type: Opaque
data:
  token: <base64-encoded-do-token>
```

## DigitalOcean Firewall Configuration

### DO Firewall via Terraform
```hcl
# firewall.tf
resource "digitalocean_firewall" "todo_app_firewall" {
  name = "todo-app-firewall"

  droplet_ids = [
    # Add your droplet IDs if needed
  ]

  # Inbound rules
  inbound_rule {
    protocol         = "tcp"
    port_range       = "6443"
    source_addresses = ["0.0.0.0/0"]
    description     = "Kubernetes API server"
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["YOUR_IP/32"]  # Replace with your IP
    description     = "SSH access"
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0"]
    description     = "HTTP traffic"
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0"]
    description     = "HTTPS traffic"
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "30000-32767"  # NodePort range
    source_addresses = ["0.0.0.0/0"]
    description     = "NodePort services"
  }

  # Outbound rules
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0"]
    description          = "All outbound TCP"
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0"]
    description          = "All outbound UDP"
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0"]
    description          = "All outbound ICMP"
  }
}

# Associate firewall with load balancer
resource "digitalocean_loadbalancer" "todo_lb" {
  name   = "todo-app-lb"
  region = "nyc1"

  forwarding_rule {
    entry_port     = 80
    entry_protocol = "http"

    target_port     = 3000
    target_protocol = "http"
  }

  forwarding_rule {
    entry_port     = 443
    entry_protocol = "https"
    certificate_id = "your-cert-id"

    target_port     = 3000
    target_protocol = "https"
  }

  healthcheck {
    port     = 3000
    protocol = "http"
    path     = "/health"
  }

  droplet_ids = []  # Will be populated by DOKS
}
```

## Advanced Security Configuration

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-network-policy
  namespace: todo-app
spec:
  podSelector:
    matchLabels:
      app: todo-frontend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: todo-app
    ports:
    - protocol: TCP
      port: 8000  # Backend API
    - protocol: TCP
      port: 8080  # MCP server
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: todo-app
spec:
  podSelector:
    matchLabels:
      app: todo-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: todo-app
      podSelector:
        matchLabels:
          app: todo-frontend
    - namespaceSelector:
        matchLabels:
          name: todo-app
      podSelector:
        matchLabels:
          app: todo-mcp-server
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
  - to:
    - namespaceSelector:
        matchLabels:
          name: default
      podSelector:
        matchLabels:
          app: neon-db
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector:
        matchLabels:
          name: default
      podSelector:
        matchLabels:
          app: kafka
    ports:
    - protocol: TCP
      port: 9092
```

## Load Balancer with Health Checks

### Advanced LoadBalancer Configuration
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend-advanced-lb
  namespace: todo-app
  annotations:
    service.beta.kubernetes.io/do-loadbalancer-enable-proxy-protocol: "true"
    service.beta.kubernetes.io/do-loadbalancer-certificate-id: "your-cert-id"
    service.beta.kubernetes.io/do-loadbalancer-redirect-http-to-https: "true"
    service.beta.kubernetes.io/do-loadbalancer-tls-passthrough: "false"
    service.beta.kubernetes.io/do-loadbalancer-size-slug: "lb-medium"
    service.beta.kubernetes.io/do-loadbalancer-algorithm: "least_connections"
    service.beta.kubernetes.io/do-loadbalancer-health-check-path: "/health"
    service.beta.kubernetes.io/do-loadbalancer-health-check-protocol: "http"
    service.beta.kubernetes.io/do-loadbalancer-health-check-port: "3000"
    service.beta.kubernetes.io/do-loadbalancer-sticky-sessions-type: "cookies"
    service.beta.kubernetes.io/do-loadbalancer-sticky-sessions-cookie-name: "todo-session"
    service.beta.kubernetes.io/do-loadbalancer-sticky-sessions-cookie-ttl: "300"
spec:
  type: LoadBalancer
  externalTrafficPolicy: Local
  healthCheckNodePort: 31234
  ports:
  - name: http
    port: 80
    targetPort: 3000
    protocol: TCP
  - name: https
    port: 443
    targetPort: 3000
    protocol: TCP
  selector:
    app: todo-frontend
```

## DNS and Domain Configuration

### DNS Records Management
```yaml
# DNS records configuration for external-dns
apiVersion: externaldns.k8s.io/v1alpha1
kind: DNSEndpoint
metadata:
  name: todo-app-dns
  namespace: todo-app
spec:
  endpoints:
  - dnsName: todo.yourdomain.com
    recordType: A
    targets: ["your-load-balancer-ip"]
    ttl: 300
  - dnsName: "*.todo.yourdomain.com"
    recordType: A
    targets: ["your-load-balancer-ip"]
    ttl: 300
```

## Security Headers Configuration

### Ingress with Security Headers
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-todo-ingress
  namespace: todo-app
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Frame-Options SAMEORIGIN";
      more_set_headers "X-Content-Type-Options nosniff";
      more_set_headers "X-XSS-Protection \"1; mode=block\"";
      more_set_headers "Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\"";
      more_set_headers "Referrer-Policy strict-origin-when-cross-origin";
      more_set_headers "Content-Security-Policy \"default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.openai.com; frame-ancestors 'none';\"";
      more_set_headers "Permissions-Policy \"geolocation=(), microphone=(), camera=()\"";
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - todo.yourdomain.com
    secretName: todo-app-tls
  rules:
  - host: todo.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-frontend
            port:
              number: 3000
```

## Output Format

Generate networking configurations that include:
- LoadBalancer service definitions with DO-specific annotations
- Ingress configurations with TLS termination
- Cert-Manager ClusterIssuer configurations
- ExternalDNS setup for automatic DNS management
- DigitalOcean firewall rules for security
- Network policies for traffic control
- Health check configurations
- Security headers and SSL settings
- Domain and DNS management configurations