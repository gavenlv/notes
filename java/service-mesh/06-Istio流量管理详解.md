# 06. Istio 流量管理详解

## 1. 流量路由基础

### 1.1 VirtualService 深度解析

#### 1.1.1 路由匹配规则

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: product-service
spec:
  hosts:
  - product-service
  - api.example.com
  gateways:
  - mesh
  - public-gateway
  http:
  - name: "user-routes"
    match:
    - headers:
        x-user-type:
          exact: "premium"
      uri:
        prefix: "/api/v2"
    - queryParams:
        version:
          exact: "beta"
      method:
        exact: "GET"
    route:
    - destination:
        host: product-service
        subset: premium
      weight: 100
    timeout: 10s
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: gateway-error,connect-failure,refused-stream
  - name: "default-routes"
    route:
    - destination:
        host: product-service
        subset: standard
      weight: 100
```

#### 1.1.2 高级匹配条件

**URI 匹配模式：**
- `exact`: 精确匹配
- `prefix`: 前缀匹配
- `regex`: 正则表达式匹配

**Header 匹配：**
- 精确匹配、前缀匹配、存在性检查
- 支持多值匹配
- 支持正则表达式

### 1.2 DestinationRule 配置详解

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: product-service-dr
spec:
  host: product-service
  trafficPolicy:
    loadBalancer:
      simple: LEAST_CONN
    connectionPool:
      tcp:
        maxConnections: 100
        connectTimeout: 30s
        tcpKeepalive:
          time: 7200s
          interval: 75s
      http:
        http1MaxPendingRequests: 1024
        http2MaxRequests: 1024
        maxRequestsPerConnection: 1024
        maxRetries: 3
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
  - name: v1
    labels:
      version: v1
    trafficPolicy:
      loadBalancer:
        simple: ROUND_ROBIN
  - name: v2
    labels:
      version: v2
    trafficPolicy:
      loadBalancer:
        simple: LEAST_CONN
  - name: premium
    labels:
      version: v2
      tier: premium
```

## 2. 流量分割与权重路由

### 2.1 金丝雀发布策略

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: canary-release
spec:
  hosts:
  - product-service
  http:
  - route:
    - destination:
        host: product-service
        subset: v1
      weight: 90
    - destination:
        host: product-service
        subset: v2
      weight: 10
    mirror:
      host: product-service
      subset: v2
    mirror_percent: 5
```

### 2.2 渐进式流量切换

```yaml
# 阶段一：5% 流量
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: progressive-release-stage1
spec:
  hosts:
  - product-service
  http:
  - route:
    - destination:
        host: product-service
        subset: v1
      weight: 95
    - destination:
        host: product-service
        subset: v2
      weight: 5

# 阶段二：50% 流量
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: progressive-release-stage2
spec:
  hosts:
  - product-service
  http:
  - route:
    - destination:
        host: product-service
        subset: v1
      weight: 50
    - destination:
        host: product-service
        subset: v2
      weight: 50

# 阶段三：100% 流量
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: progressive-release-stage3
spec:
  hosts:
  - product-service
  http:
  - route:
    - destination:
        host: product-service
        subset: v2
      weight: 100
```

## 3. 故障恢复与熔断机制

### 3.1 超时与重试配置

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: resilient-service
spec:
  hosts:
  - backend-service
  http:
  - route:
    - destination:
        host: backend-service
    timeout: 5s
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: gateway-error,connect-failure,refused-stream,5xx
    fault:
      delay:
        percentage:
          value: 0.1
        fixedDelay: 1s
```

### 3.2 熔断器配置

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: circuit-breaker
spec:
  host: critical-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1000
        maxRequestsPerConnection: 10
        maxRetries: 3
    outlierDetection:
      consecutiveErrors: 5
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 20
```

## 4. 流量镜像与测试

### 4.1 流量镜像配置

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: traffic-mirroring
spec:
  hosts:
  - production-service
  http:
  - route:
    - destination:
        host: production-service
        subset: v1
      weight: 100
    mirror:
      host: staging-service
    mirror_percent: 10
    timeout: 5s
```

### 4.2 故障注入测试

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: fault-injection
spec:
  hosts:
  - test-service
  http:
  - fault:
      delay:
        percentage:
          value: 50
        fixedDelay: 5s
      abort:
        percentage:
          value: 10
        httpStatus: 503
    route:
    - destination:
        host: test-service
```

## 5. 高级路由策略

### 5.1 基于内容的流量路由

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: content-based-routing
spec:
  hosts:
  - api-gateway
  http:
  - match:
    - headers:
        x-region:
          exact: "us-east"
      uri:
        prefix: "/api"
    route:
    - destination:
        host: us-east-service
  - match:
    - headers:
        x-region:
          exact: "eu-west"
      uri:
        prefix: "/api"
    route:
    - destination:
        host: eu-west-service
  - match:
    - queryParams:
        category:
          exact: "electronics"
    route:
    - destination:
        host: electronics-service
```

### 5.2 流量优先级配置

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: priority-routing
spec:
  hosts:
  - multi-tenant-service
  http:
  - match:
    - headers:
        x-tenant-id:
          exact: "enterprise"
    route:
    - destination:
        host: multi-tenant-service
        subset: enterprise
    timeout: 10s
  - match:
    - headers:
        x-tenant-id:
          exact: "standard"
    route:
    - destination:
        host: multi-tenant-service
        subset: standard
    timeout: 5s
  - route:
    - destination:
        host: multi-tenant-service
        subset: free
    timeout: 2s
```

## 6. 跨服务流量管理

### 6.1 ServiceEntry 外部服务集成

```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-api
spec:
  hosts:
  - api.external.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  resolution: DNS
  location: MESH_EXTERNAL
```

### 6.2 多集群流量管理

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: multi-cluster
spec:
  hosts:
  - global-service
  http:
  - route:
    - destination:
        host: global-service.cluster1.svc.cluster.local
      weight: 50
    - destination:
        host: global-service.cluster2.svc.cluster.local
      weight: 50
```

## 7. 性能优化配置

### 7.1 连接池优化

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: optimized-connection-pool
spec:
  host: high-traffic-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1000
        connectTimeout: 1s
      http:
        http2MaxRequests: 1000
        maxRequestsPerConnection: 100
        maxRetries: 2
    loadBalancer:
      consistentHash:
        httpHeaderName: x-user-id
```

### 7.2 负载均衡策略

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: load-balancing
spec:
  host: balanced-service
  trafficPolicy:
    loadBalancer:
      consistentHash:
        httpHeaderName: x-session-id
    localityLbSetting:
      enabled: true
      failover:
      - from: us-east
        to: us-west
      - from: eu-west
        to: us-east
```

## 8. 监控与调试

### 8.1 流量监控指标

```bash
# 查看流量统计
kubectl exec -it deployment/product-service -c istio-proxy -- \\\n  curl -s http://localhost:15000/stats | grep -E "cluster|upstream"

# 查看路由配置
kubectl exec -it deployment/product-service -c istio-proxy -- \\\n  curl -s http://localhost:15000/config_dump

# 查看访问日志
kubectl logs deployment/product-service -c istio-proxy -f
```

### 8.2 故障排查工具

```bash
# 检查代理状态
istioctl proxy-status

# 检查配置同步
istioctl proxy-config cluster deployment/product-service

# 检查路由规则
istioctl proxy-config route deployment/product-service

# 检查端点发现
istioctl proxy-config endpoint deployment/product-service
```

## 9. 最佳实践

### 9.1 命名规范

```yaml
# VirtualService 命名规范
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: product-service-vs  # 服务名 + vs
  namespace: product

# DestinationRule 命名规范
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: product-service-dr  # 服务名 + dr
  namespace: product
```

### 9.2 配置管理

```yaml
# 使用 ConfigMap 管理配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: istio-traffic-config
  namespace: istio-system
data:
  virtualservice.yaml: |
    apiVersion: networking.istio.io/v1beta1
    kind: VirtualService
    metadata:
      name: product-service
    spec:
      hosts:
      - product-service
      http:
      - route:
        - destination:
            host: product-service
  
  destinationrule.yaml: |
    apiVersion: networking.istio.io/v1beta1
    kind: DestinationRule
    metadata:
      name: product-service
    spec:
      host: product-service
      subsets:
      - name: v1
        labels:
          version: v1
```

### 9.3 版本控制

```yaml
# 使用 Helm 管理版本
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: {{ .Chart.Name }}-vs
  labels:
    app.kubernetes.io/version: {{ .Chart.AppVersion }}
    app.kubernetes.io/managed-by: {{ .Release.Service }}
  annotations:
    config.istio.io/version: "{{ .Values.istio.version }}"
spec:
  hosts:
  - {{ .Values.service.name }}
  http:
  - route:
    - destination:
        host: {{ .Values.service.name }}
        subset: {{ .Values.service.version }}
```

---

**下一章预告：** 第7章将深入探讨 Istio 安全机制，包括 mTLS、认证授权、安全策略等高级安全功能。