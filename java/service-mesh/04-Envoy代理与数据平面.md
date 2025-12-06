# 04. Envoy 代理与数据平面深度解析

## 1. Envoy 架构核心概念

### 1.1 Envoy 核心组件

#### 1.1.1 监听器（Listener）

**监听器配置结构：**
```yaml
# 监听器配置示例
listeners:
- name: main_listener
  address:
    socket_address:
      address: 0.0.0.0
      port_value: 8080
  filter_chains:
  - filters:
    - name: envoy.filters.network.http_connection_manager
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
        stat_prefix: ingress_http
        route_config:
          name: local_route
          virtual_hosts:
          - name: local_service
            domains: ["*"]
            routes:
            - match:
                prefix: "/"
              route:
                cluster: service_cluster
        http_filters:
        - name: envoy.filters.http.router
```

#### 1.1.2 集群（Cluster）

**集群配置详解：**
```yaml
clusters:
- name: service_cluster
  connect_timeout: 0.25s
  type: STRICT_DNS
  lb_policy: ROUND_ROBIN
  load_assignment:
    cluster_name: service_cluster
    endpoints:
    - lb_endpoints:
      - endpoint:
          address:
            socket_address:
              address: service.default.svc.cluster.local
              port_value: 80
  circuit_breakers:
    thresholds:
    - priority: DEFAULT
      max_connections: 1000
      max_pending_requests: 1000
      max_requests: 1000
```

### 1.2 过滤器架构

#### 1.2.1 网络过滤器（Network Filters）

**过滤器链处理流程：**
```java
// 过滤器链处理伪代码
public class FilterChainProcessor {
    private List<NetworkFilter> filters;
    
    public void onData(Connection connection, Buffer data) {
        for (NetworkFilter filter : filters) {
            FilterStatus status = filter.onData(connection, data);
            if (status == FilterStatus.StopIteration) {
                break;
            }
        }
    }
}
```

#### 1.2.2 HTTP 过滤器（HTTP Filters）

```yaml
# HTTP 过滤器配置示例
http_filters:
- name: envoy.filters.http.cors
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.cors.v3.Cors
- name: envoy.filters.http.router
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
```

## 2. 动态配置系统

### 2.1 xDS API 协议

#### 2.1.1 发现服务类型

**xDS 协议家族：**
- **CDS**：集群发现服务（Cluster Discovery Service）
- **EDS**：端点发现服务（Endpoint Discovery Service）
- **LDS**：监听器发现服务（Listener Discovery Service）
- **RDS**：路由发现服务（Route Discovery Service）

```java
// xDS 客户端实现示例
public class XdsClient {
    private DiscoveryRequest createClusterRequest() {
        return DiscoveryRequest.newBuilder()
            .setTypeUrl("type.googleapis.com/envoy.config.cluster.v3.Cluster")
            .setVersionInfo(getCurrentVersion())
            .setNode(getNodeInfo())
            .build();
    }
    
    public void onClusterResponse(DiscoveryResponse response) {
        for (Any resource : response.getResourcesList()) {
            Cluster cluster = resource.unpack(Cluster.class);
            updateClusterConfig(cluster);
        }
    }
}
```

#### 2.1.2 增量 xDS（Delta xDS）

```protobuf
// 增量 xDS 协议
message DeltaDiscoveryRequest {
    string type_url = 1;
    Node node = 2;
    repeated string resource_names_subscribe = 3;
    repeated string resource_names_unsubscribe = 4;
    map<string, string> initial_resource_versions = 5;
    string response_nonce = 6;
    google.rpc.Status error_detail = 7;
}
```

### 2.2 配置热更新机制

#### 2.2.1 配置版本管理

```yaml
# 配置版本控制
version_info: "2024-01-15T10:30:00Z"
resources:
- "@type": type.googleapis.com/envoy.config.cluster.v3.Cluster
  name: service_cluster
  version: "v2"
  last_updated: "2024-01-15T10:30:00Z"
```

#### 2.2.2 优雅配置切换

```java
// 配置热更新实现
public class ConfigManager {
    private AtomicReference<Config> currentConfig = new AtomicReference<>();
    
    public void updateConfig(Config newConfig) {
        Config oldConfig = currentConfig.get();
        
        // 预热新配置
        warmUpConfig(newConfig);
        
        // 原子切换
        currentConfig.set(newConfig);
        
        // 清理旧配置
        cleanupConfig(oldConfig);
    }
}
```

## 3. 负载均衡算法深度解析

### 3.1 负载均衡策略

#### 3.1.1 轮询（Round Robin）

```java
// 轮询负载均衡实现
public class RoundRobinLoadBalancer implements LoadBalancer {
    private final List<Endpoint> endpoints;
    private final AtomicInteger currentIndex = new AtomicInteger(0);
    
    @Override
    public Endpoint chooseEndpoint(Request request) {
        int index = currentIndex.getAndIncrement() % endpoints.size();
        return endpoints.get(index);
    }
}
```

#### 3.1.2 最少连接（Least Request）

```java
// 最少连接负载均衡
public class LeastRequestLoadBalancer implements LoadBalancer {
    private final List<WeightedEndpoint> endpoints;
    
    @Override
    public Endpoint chooseEndpoint(Request request) {
        return endpoints.stream()
            .min(Comparator.comparingInt(WeightedEndpoint::getActiveRequests))
            .orElseThrow(() -> new NoAvailableEndpointException());
    }
}
```

#### 3.1.3 一致性哈希（Ring Hash）

```java
// 一致性哈希实现
public class RingHashLoadBalancer implements LoadBalancer {
    private final TreeMap<Integer, Endpoint> hashRing = new TreeMap<>();
    private final int virtualNodes;
    
    public RingHashLoadBalancer(List<Endpoint> endpoints, int virtualNodes) {
        this.virtualNodes = virtualNodes;
        for (Endpoint endpoint : endpoints) {
            for (int i = 0; i < virtualNodes; i++) {
                String nodeKey = endpoint.getAddress() + "#" + i;
                int hash = hash(nodeKey);
                hashRing.put(hash, endpoint);
            }
        }
    }
    
    @Override
    public Endpoint chooseEndpoint(Request request) {
        String key = request.getHashKey();
        int hash = hash(key);
        
        Map.Entry<Integer, Endpoint> entry = hashRing.ceilingEntry(hash);
        if (entry == null) {
            entry = hashRing.firstEntry();
        }
        
        return entry.getValue();
    }
}
```

### 3.2 健康检查机制

#### 3.2.1 主动健康检查

```yaml
# 健康检查配置
health_checks:
- timeout: 1s
  interval: 5s
  unhealthy_threshold: 3
  healthy_threshold: 2
  http_health_check:
    path: /health
    expected_statuses:
      start: 200
      end: 399
  no_traffic_interval: 30s
```

#### 3.2.2 被动健康检查

```yaml
# 异常检测配置
outlier_detection:
  consecutive_5xx: 5
  interval: 10s
  base_ejection_time: 30s
  max_ejection_percent: 50
  enforcing_consecutive_5xx: 100
```

## 4. 高级流量管理功能

### 4.1 流量分割与金丝雀发布

```yaml
# 流量分割配置
routes:
- match:
    prefix: "/api"
  route:
    weighted_clusters:
      clusters:
      - name: service_v1
        weight: 90
      - name: service_v2
        weight: 10
    timeout: 5s
    retry_policy:
      retry_on: connect-failure,refused-stream,unavailable
      num_retries: 3
      per_try_timeout: 2s
```

### 4.2 故障注入测试

```yaml
# 故障注入配置
fault:
  delay:
    percentage:
      numerator: 10
      denominator: HUNDRED
    fixed_delay: 5s
  abort:
    percentage:
      numerator: 5
      denominator: HUNDRED
    http_status: 503
```

## 5. 性能优化与调优

### 5.1 连接池优化

```yaml
# 连接池配置优化
circuit_breakers:
  thresholds:
  - priority: DEFAULT
    max_connections: 10000
    max_pending_requests: 10000
    max_requests: 10000
    max_retries: 3
  - priority: HIGH
    max_connections: 1000
    max_pending_requests: 1000
    max_requests: 1000
```

### 5.2 内存与 CPU 优化

```yaml
# 资源限制配置
admin:
  access_log_path: /tmp/admin_access.log
  address:
    socket_address:
      address: 127.0.0.1
      port_value: 9901

# 性能调优参数
overload_manager:
  refresh_interval: 0.25s
  resource_monitors:
  - name: envoy.resource_monitors.fixed_heap
    typed_config:
      "@type": type.googleapis.com/envoy.config.resource_monitor.fixed_heap.v2alpha.FixedHeapConfig
      max_heap_size_bytes: 2147483648
```

## 6. 可观测性配置

### 6.1 指标收集

```yaml
# 统计配置
stats_config:
  stats_tags:
  - tag_name: cluster_name
    regex: "^cluster\\.((.+?)\\.)"
  - tag_name: route_name
    regex: "^http\\.ingress_http\\.((.+?)\\.)"
  use_all_default_tags: true

# 指标刷新间隔
stats_flush_interval: 60s
```

### 6.2 分布式追踪

```yaml
# 追踪配置
tracing:
  http:
    name: envoy.tracers.zipkin
    typed_config:
      "@type": type.googleapis.com/envoy.config.trace.v3.ZipkinConfig
      collector_cluster: zipkin
      collector_endpoint: "/api/v2/spans"
      collector_endpoint_version: HTTP_JSON
      shared_span_context: false
```

### 6.3 访问日志

```yaml
# 访问日志配置
access_log:
- name: envoy.access_loggers.file
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: /dev/stdout
    format: |
      [%START_TIME%] "%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)% %PROTOCOL%"
      %RESPONSE_CODE% %RESPONSE_FLAGS% %BYTES_RECEIVED% %BYTES_SENT% %DURATION%
      %RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)% "%REQ(X-FORWARDED-FOR)%" "%REQ(USER-AGENT)%"
      "%REQ(X-REQUEST-ID)%" "%REQ(:AUTHORITY)%" "%UPSTREAM_HOST%"
```

## 7. 安全配置

### 7.1 TLS 配置

```yaml
# TLS 终止配置
transport_socket:
  name: envoy.transport_sockets.tls
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
    common_tls_context:
      tls_certificates:
      - certificate_chain:
          filename: "/etc/certs/tls.crt"
        private_key:
          filename: "/etc/certs/tls.key"
      validation_context:
        trusted_ca:
          filename: "/etc/certs/ca.crt"
    require_client_certificate: true
```

### 7.2 网络策略

```yaml
# 网络过滤器链
filter_chains:
- filters:
  - name: envoy.filters.network.rbac
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.network.rbac.v3.RBAC
      stat_prefix: rbac
      rules:
        policies:
          "service-policy":
            permissions:
            - any: true
            principals:
            - authenticated:
                principal_name:
                  exact: spiffe://cluster.local/ns/default/sa/frontend
```

## 8. 扩展开发

### 8.1 自定义过滤器开发

```cpp
// C++ 自定义过滤器示例
class CustomHttpFilter : public Http::StreamFilter {
public:
    Http::FilterHeadersStatus decodeHeaders(Http::RequestHeaderMap& headers, bool) override {
        // 自定义头部处理逻辑
        headers.addCopy(Http::LowerCaseString("x-custom-header"), "custom-value");
        return Http::FilterHeadersStatus::Continue;
    }
    
    Http::FilterDataStatus decodeData(Buffer::Instance& data, bool) override {
        // 自定义数据处理逻辑
        return Http::FilterDataStatus::Continue;
    }
};
```

### 8.2 Wasm 扩展

```yaml
# Wasm 过滤器配置
http_filters:
- name: envoy.filters.http.wasm
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.wasm.v3.Wasm
    config:
      name: "custom_filter"
      root_id: "custom_root"
      vm_config:
        vm_id: "custom_vm"
        runtime: "envoy.wasm.runtime.v8"
        code:
          local:
            filename: "/etc/envoy/filters/custom.wasm"
```

---

**下一章预告：** 第5章将重点讲解 Java 应用如何与 Service Mesh 集成，包括 Spring Cloud、Micronaut 等框架的最佳实践。