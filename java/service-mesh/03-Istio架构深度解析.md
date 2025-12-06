# 03. Istio 架构深度解析

## 1. Istio 整体架构

### 1.1 控制平面组件

#### 1.1.1 Istiod（核心控制平面）

**架构组成：**
- **Pilot**：服务发现与流量管理
- **Citadel**：安全与身份认证
- **Galley**：配置验证与分发

```java
// Istiod 核心架构示例
public class IstiodArchitecture {
    private PilotService pilot;      // 服务发现与流量管理
    private CitadelService citadel;  // 安全认证
    private GalleyService galley;    // 配置管理
    
    public void bootstrap() {
        // 初始化控制平面组件
        pilot.initialize();
        citadel.setupCertificateAuthority();
        galley.startConfigValidation();
    }
}
```

#### 1.1.2 数据平面：Envoy Proxy

**Envoy 核心特性：**
- 高性能 C++ 代理
- 支持 HTTP/1.1, HTTP/2, gRPC
- 动态配置热更新
- 丰富的可观测性指标

### 1.2 Istio 配置模型

#### 1.2.1 Kubernetes CRD（自定义资源定义）

**核心 CRD 资源：**
- **VirtualService**：路由规则定义
- **DestinationRule**：流量策略配置
- **Gateway**：入口网关配置
- **ServiceEntry**：外部服务接入

```yaml
# VirtualService 配置示例
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: product-service
spec:
  hosts:
  - product-service
  http:
  - match:
    - headers:
        version:
          exact: "v2"
    route:
    - destination:
        host: product-service
        subset: v2
  - route:
    - destination:
        host: product-service
        subset: v1
```

## 2. 流量管理深度解析

### 2.1 智能路由策略

#### 2.1.1 条件路由

**路由匹配条件类型：**
- URI 路径匹配
- Header 匹配
- 查询参数匹配
- 权重分配

```yaml
# 复杂路由配置
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-gateway
spec:
  hosts:
  - api.example.com
  gateways:
  - istio-gateway
  http:
  - match:
    - uri:
        prefix: /api/v1/users
      headers:
        x-region:
          exact: "us-east"
    route:
    - destination:
        host: user-service
        subset: us-east
  - match:
    - uri:
        prefix: /api/v1/products
      queryParams:
        category:
          exact: "electronics"
    route:
    - destination:
        host: product-service
        subset: electronics
```

#### 2.1.2 流量镜像（Shadow Traffic）

```yaml
# 流量镜像配置
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: payment-service
spec:
  hosts:
  - payment-service
  http:
  - route:
    - destination:
        host: payment-service
        subset: v1
      weight: 100
    mirror:
      host: payment-service
      subset: v2
    mirror_percent: 10
```

### 2.2 故障恢复策略

#### 2.2.1 超时与重试

```yaml
# 超时重试配置
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service
spec:
  hosts:
  - order-service
  http:
  - route:
    - destination:
        host: order-service
    timeout: 5s
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: gateway-error,connect-failure,refused-stream
```

#### 2.2.2 熔断器配置

```yaml
# DestinationRule 熔断配置
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: inventory-service
spec:
  host: inventory-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1000
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutiveErrors: 5
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

## 3. 安全架构深度解析

### 3.1 mTLS（双向 TLS）

#### 3.1.1 证书管理

**证书生命周期管理：**
- 自动证书轮换
- 根证书颁发机构（CA）
- 工作负载身份认证

```yaml
# PeerAuthentication 配置
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT

# 命名空间级别配置
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: product-namespace
  namespace: product
spec:
  mtls:
    mode: STRICT
```

#### 3.1.2 安全策略配置

```yaml
# AuthorizationPolicy 配置
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-access
  namespace: default
spec:
  selector:
    matchLabels:
      app: api-gateway
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/frontend-service"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

### 3.2 JWT 认证与授权

```yaml
# RequestAuthentication JWT 配置
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
```

## 4. 可观测性架构

### 4.1 遥测数据收集

#### 4.1.1 指标（Metrics）

**默认收集的指标：**
- 请求量（request_count）
- 请求延迟（request_duration）
- 错误率（error_count）
- TCP 连接指标

```yaml
# Telemetry 配置示例
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: custom-metrics
  namespace: default
spec:
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_COUNT
        mode: CLIENT_AND_SERVER
      disabled: false
      tagOverrides:
        custom_tag:
          value: "custom_value"
```

#### 4.1.2 分布式追踪

```yaml
# 追踪配置
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: tracing-config
  namespace: default
spec:
  tracing:
  - providers:
    - name: zipkin
    customTags:
      environment:
        literal:
          value: production
      user_id:
        header:
          name: x-user-id
          defaultValue: unknown
```

### 4.2 访问日志配置

```yaml
# 访问日志配置
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: access-logging
  namespace: default
spec:
  accessLogging:
  - providers:
    - name: envoy
    disabled: false
```

## 5. 高级配置模式

### 5.1 多集群部署

#### 5.1.1 集群网络配置

```yaml
# ServiceEntry 多集群配置
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: cross-cluster-service
  namespace: default
spec:
  hosts:
  - service.cluster2.global
  location: MESH_INTERNAL
  ports:
  - number: 80
    name: http
    protocol: HTTP
  resolution: DNS
  endpoints:
  - address: 10.0.0.1
    ports:
      http: 80
    locality: us-west1/zone1
  - address: 10.0.0.2
    ports:
      http: 80
    locality: us-east1/zone1
```

### 5.2 工作负载入口配置

```yaml
# Gateway 配置示例
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: public-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*.example.com"
    tls:
      httpsRedirect: true
  - port:
      number: 443
      name: https
      protocol: HTTPS
    hosts:
    - "*.example.com"
    tls:
      mode: SIMPLE
      credentialName: example-cert
```

## 6. 性能优化与最佳实践

### 6.1 资源优化配置

```yaml
# Sidecar 资源限制
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: default
  namespace: default
spec:
  workloadSelector:
    labels:
      app: critical-service
  egress:
  - hosts:
    - "./critical-database.default.svc.cluster.local"
    - "istio-system/*"
  resources:
    limits:
      cpu: 200m
      memory: 128Mi
    requests:
      cpu: 100m
      memory: 64Mi
```

### 6.2 网络性能优化

```yaml
# 网络策略优化
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: performance-optimized
spec:
  host: high-performance-service
  trafficPolicy:
    loadBalancer:
      simple: LEAST_CONN
    connectionPool:
      tcp:
        connectTimeout: 1s
        maxConnections: 1000
      http:
        http2MaxRequests: 1000
        maxRequestsPerConnection: 10
        maxRetries: 3
```

## 7. 故障排查与调试

### 7.1 调试工具与命令

```bash
# 获取代理状态
kubectl exec -it deployment/product-service -c istio-proxy -- pilot-agent request GET servers

# 查看代理配置
kubectl exec -it deployment/product-service -c istio-proxy -- pilot-agent request GET config_dump

# 检查证书状态
kubectl exec -it deployment/product-service -c istio-proxy -- pilot-agent request GET certs

# 查看访问日志
kubectl logs deployment/product-service -c istio-proxy
```

### 7.2 常见问题诊断

**连接问题诊断：**
1. 检查 mTLS 配置
2. 验证服务发现
3. 检查网络策略
4. 查看代理状态

**性能问题诊断：**
1. 分析指标数据
2. 检查资源限制
3. 优化路由配置
4. 调整连接池参数

---

**下一章预告：** 第4章将深入探讨 Envoy 代理的数据平面实现原理和高级配置。