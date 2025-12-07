# 07. Istio 安全机制与实践

## 1. 安全架构概述

### 1.1 零信任安全模型

**Istio 安全核心组件：**
- **Citadel**：证书颁发机构（CA）
- **Pilot**：安全策略分发
- **Envoy**：数据平面安全执行

### 1.2 安全层次架构

```yaml
# 安全配置层次结构
Security Layers:
  - Transport Security (mTLS)
  - Authentication (JWT, OIDC)
  - Authorization (RBAC)
  - Network Policies
  - Audit & Monitoring
```

## 2. 双向 TLS（mTLS）配置

### 2.1 PeerAuthentication 配置

#### 2.1.1 命名空间级别 mTLS

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT

# 特定命名空间配置
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: product-namespace
  namespace: product
spec:
  mtls:
    mode: STRICT
```

#### 2.1.2 工作负载级别 mTLS

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: product-service-mtls
  namespace: product
spec:
  selector:
    matchLabels:
      app: product-service
  mtls:
    mode: STRICT
  portLevelMtls:
    8080:
      mode: STRICT
    9090:
      mode: DISABLE
```

### 2.2 证书管理

#### 2.2.1 自动证书轮换

```bash
# 查看证书状态
kubectl exec -it deployment/product-service -c istio-proxy -- \\\n  curl http://localhost:15000/certs

# 检查证书过期时间
kubectl exec -it deployment/product-service -c istio-proxy -- \\\n  openssl x509 -in /etc/certs/cert-chain.pem -text -noout | grep -A 2 Validity
```

#### 2.2.2 自定义根证书

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: istio-ca-root-cert
  namespace: istio-system
data:
  root-cert.pem: |
    -----BEGIN CERTIFICATE-----
    MII...
    -----END CERTIFICATE-----
```

## 3. 请求认证（RequestAuthentication）

### 3.1 JWT 认证配置

```yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: default
spec:
  selector:
    matchLabels:
      app: api-gateway
  jwtRules:
  - issuer: "https://auth.example.com"
    jwksUri: "https://auth.example.com/.well-known/jwks.json"
    audiences:
    - "api.example.com"
    - "mobile.example.com"
    jwtHeaders:
    - "x-jwt-token"
    jwtParams:
    - "token"
    forwardOriginalToken: true
    outputPayloadToHeader: x-jwt-payload
```

### 3.2 OIDC 集成

```yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: oidc-auth
  namespace: default
spec:
  selector:
    matchLabels:
      app: web-app
  jwtRules:
  - issuer: "https://accounts.google.com"
    jwksUri: "https://www.googleapis.com/oauth2/v3/certs"
    audiences:
    - "your-google-client-id"
  - issuer: "https://dev-123456.okta.com/oauth2/default"
    jwksUri: "https://dev-123456.okta.com/oauth2/default/v1/keys"
    audiences:
    - "api://default"
```

## 4. 授权策略（AuthorizationPolicy）

### 4.1 基于角色的访问控制

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: role-based-access
  namespace: default
spec:
  selector:
    matchLabels:
      app: user-service
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/admin-service"]
    to:
    - operation:
        methods: ["GET", "POST", "PUT", "DELETE"]
        paths: ["/api/users/*"]
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/user-service"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/users/*"]
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/guest-service"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/api/users/public/*"]
```

### 4.2 条件授权策略

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: conditional-access
  namespace: default
spec:
  selector:
    matchLabels:
      app: payment-service
  rules:
  - when:
    - key: request.auth.claims[groups]
      values: ["admin", "finance"]
    - key: request.headers[x-request-id]
      values: ["*"]
    to:
    - operation:
        methods: ["POST", "PUT"]
        paths: ["/api/payments/*"]
  - when:
    - key: request.auth.claims[groups]
      values: ["user"]
    - key: request.time
      values: ["Mon, Tue, Wed, Thu, Fri 09:00-18:00 +08:00"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/api/payments/user/*"]
```

### 4.3 拒绝策略配置

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-policy
  namespace: default
spec:
  selector:
    matchLabels:
      app: sensitive-service
  action: DENY
  rules:
  - from:
    - source:
        notPrincipals: ["cluster.local/ns/default/sa/trusted-service"]
    to:
    - operation:
        methods: ["DELETE"]
        paths: ["/api/sensitive/*"]
  - when:
    - key: request.headers[user-agent]
      values: ["*bot*", "*crawler*"]
```

## 5. 网络安全策略

### 5.1 网络策略集成

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: product-service-policy
  namespace: product
spec:
  podSelector:
    matchLabels:
      app: product-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

### 5.2 服务网格边界安全

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: mesh-border
  namespace: istio-system
spec:
  selector:
    matchLabels:
      istio: ingressgateway
  mtls:
    mode: STRICT

apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: ingress-access
  namespace: istio-system
spec:
  selector:
    matchLabels:
      istio: ingressgateway
  rules:
  - from:
    - source:
        ipBlocks: ["192.168.0.0/16", "10.0.0.0/8"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

## 6. 安全监控与审计

### 6.1 安全事件日志

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: security-audit
  namespace: default
spec:
  selector:
    matchLabels:
      app: api-gateway
  accessLogging:
  - providers:
    - name: envoy
    disabled: false
    filter:
      expression: >
        response.code >= 400 or 
        connection.termination_details != "" or
        response.flags != ""
```

### 6.2 安全指标收集

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: security-metrics
  namespace: default
spec:
  selector:
    matchLabels:
      app: api-gateway
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_COUNT
      tagOverrides:
        response_code:
          value: "%RESPONSE_CODE%"
        response_flags:
          value: "%RESPONSE_FLAGS%"
        request_auth:
          value: "%DYNAMIC_METADATA(envoy.filters.http.jwt_auth:payload)%"
```

## 7. 高级安全特性

### 7.1 自定义认证扩展

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: custom-auth
  namespace: istio-system
spec:
  workloadSelector:
    labels:
      app: api-gateway
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: GATEWAY
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.ext_authz
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.ext_authz.v3.ExtAuthz
          grpc_service:
            envoy_grpc:
              cluster_name: ext-authz-service
          failure_mode_allow: false
          include_peer_certificate: true
```

### 7.2 安全头配置

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: security-headers
  namespace: istio-system
spec:
  workloadSelector:
    labels:
      app: web-app
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_OUTBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.lua
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
          inline_code: |
            function envoy_on_response(response_handle)
              response_handle:headers():add("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
              response_handle:headers():add("X-Content-Type-Options", "nosniff")
              response_handle:headers():add("X-Frame-Options", "DENY")
              response_handle:headers():add("X-XSS-Protection", "1; mode=block")
              response_handle:headers():add("Content-Security-Policy", "default-src 'self'")
            end
```

## 8. 合规性与审计

### 8.1 PCI DSS 合规配置

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: pci-compliance
  namespace: payment
spec:
  selector:
    matchLabels:
      app: payment-service
  rules:
  - when:
    - key: request.auth.claims[pci_level]
      values: ["1"]
    - key: request.headers[x-pci-audit]
      values: ["enabled"]
    to:
    - operation:
        methods: ["POST", "PUT"]
        paths: ["/api/payments/*"]
```

### 8.2 GDPR 数据保护

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: gdpr-compliance
  namespace: user-data
spec:
  selector:
    matchLabels:
      app: user-service
  rules:
  - when:
    - key: request.auth.claims[data_protection_officer]
      values: ["true"]
    - key: request.headers[x-gdpr-consent]
      values: ["given"]
    to:
    - operation:
        methods: ["GET", "DELETE"]
        paths: ["/api/user-data/*"]
```

## 9. 故障排查与调试

### 9.1 安全配置检查

```bash
# 检查 mTLS 状态
istioctl authn tls-check product-service.product.svc.cluster.local

# 检查授权策略
istioctl authz check deployment/product-service

# 查看代理安全配置
kubectl exec -it deployment/product-service -c istio-proxy -- \\\n  curl http://localhost:15000/config_dump?include_eds
```

### 9.2 安全事件分析

```bash
# 查看安全相关日志
kubectl logs deployment/product-service -c istio-proxy | grep -E "RBAC|AUTHZ|TLS"

# 分析访问日志中的安全事件
kubectl logs deployment/product-service -c istio-proxy | \\\n  jq 'select(.response_flags != "" or .response_code >= 400)'
```

## 10. 最佳实践

### 10.1 安全策略命名规范

```yaml
# 命名规范示例
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: product-service-read-only  # 服务名 + 策略类型
  namespace: product

apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: product-service-mtls  # 服务名 + mtls
  namespace: product
```

### 10.2 分层安全策略

```yaml
# 网络层安全
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: baseline-security

# 传输层安全
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: strict-mtls

# 应用层安全
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: fine-grained-access
```

### 10.3 安全审计配置

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-audit-config
  namespace: istio-system
data:
  audit.yaml: |
    rules:
    - level: Metadata
      resources:
      - group: "security.istio.io"
        resources: ["authorizationpolicies", "peerauthentications"]
    
    policy:
      rules:
      - level: Metadata
        resources:
        - group: ""
          resources: ["secrets"]
```

---

**下一章预告：** 第8章将深入探讨 Istio 可观测性配置，包括指标收集、分布式追踪、日志聚合等高级监控功能。