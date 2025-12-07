# 09. Envoy 架构与核心功能

## 1. Envoy 核心架构

### 1.1 组件架构概述

**Envoy 核心组件：**
- **监听器（Listener）**：网络连接入口
- **过滤器（Filter）**：请求处理链
- **集群（Cluster）**：后端服务集合
- **路由（Route）**：请求路由规则

### 1.2 数据流处理流程

```yaml
# Envoy 数据流处理
Data Flow:
  客户端请求 → 监听器 → 网络过滤器 → HTTP 过滤器 → 路由 → 集群 → 后端服务
  
  响应流程：
  后端服务 → 上游过滤器 → 下游过滤器 → 监听器 → 客户端
```

## 2. 监听器配置

### 2.1 基础监听器配置

```yaml
listeners:
- name: main_http_listener
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

### 2.2 高级监听器配置

```yaml
listeners:
- name: tcp_proxy_listener
  address:
    socket_address:
      address: 0.0.0.0
      port_value: 9000
  filter_chains:
  - filters:
    - name: envoy.filters.network.tcp_proxy
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.filters.network.tcp_proxy.v3.TcpProxy
        stat_prefix: tcp_stats
        cluster: tcp_service_cluster
        idle_timeout: 1h
        max_connect_attempts: 3
```

## 3. 过滤器机制

### 3.1 网络过滤器

#### 3.1.1 HTTP 连接管理器

```yaml
filters:
- name: envoy.filters.network.http_connection_manager
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
    stat_prefix: ingress_http
    http2_protocol_options:
      max_concurrent_streams: 100
      initial_stream_window_size: 65536
      initial_connection_window_size: 1048576
    common_http_protocol_options:
      idle_timeout: 3600s
      max_connection_duration: 0s
      max_headers_count: 100
      max_stream_duration: 0s
    route_config:
      name: local_route
      virtual_hosts:
      - name: backend
        domains: ["*"]
        routes:
        - match:
            prefix: "/"
          route:
            cluster: backend_cluster
    http_filters:
    - name: envoy.filters.http.router
```

#### 3.1.2 TCP 代理过滤器

```yaml
filters:
- name: envoy.filters.network.tcp_proxy
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.network.tcp_proxy.v3.TcpProxy
    stat_prefix: tcp_stats
    cluster: backend_cluster
    access_log:
    - name: envoy.access_loggers.file
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
        path: /dev/stdout
```

### 3.2 HTTP 过滤器

#### 3.2.1 路由器过滤器

```yaml
http_filters:
- name: envoy.filters.http.router
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
    dynamic_stats: true
    start_child_span: true
```

#### 3.2.2 CORS 过滤器

```yaml
http_filters:
- name: envoy.filters.http.cors
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.cors.v3.Cors
- name: envoy.filters.http.router
```

#### 3.2.3 速率限制过滤器

```yaml
http_filters:
- name: envoy.filters.http.ratelimit
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.ratelimit.v3.RateLimit
    domain: apis
    timeout: 0.25s
    failure_mode_deny: true
    rate_limit_service:
      grpc_service:
        envoy_grpc:
          cluster_name: rate_limit_service
- name: envoy.filters.http.router
```

## 4. 集群配置

### 4.1 基础集群配置

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
```

### 4.2 高级集群配置

```yaml
clusters:
- name: high_performance_cluster
  connect_timeout: 1s
  type: EDS
  lb_policy: LEAST_REQUEST
  circuit_breakers:
    thresholds:
    - priority: DEFAULT
      max_connections: 10000
      max_pending_requests: 10000
      max_requests: 10000
      max_retries: 3
  outlier_detection:
    consecutive_5xx: 5
    interval: 30s
    base_ejection_time: 30s
    max_ejection_percent: 50
  http2_protocol_options:
    max_concurrent_streams: 100
  health_checks:
  - timeout: 5s
    interval: 30s
    unhealthy_threshold: 3
    healthy_threshold: 2
    http_health_check:
      path: /health
      expected_statuses:
        - start: 200
          end: 399
```

## 5. 负载均衡策略

### 5.1 负载均衡算法

#### 5.1.1 轮询（Round Robin）

```yaml
clusters:
- name: round_robin_cluster
  lb_policy: ROUND_ROBIN
```

#### 5.1.2 最少请求（Least Request）

```yaml
clusters:
- name: least_request_cluster
  lb_policy: LEAST_REQUEST
```

#### 5.1.3 环哈希（Ring Hash）

```yaml
clusters:
- name: ring_hash_cluster
  lb_policy: RING_HASH
  lb_config:
    ring_hash_lb_config:
      minimum_ring_size: 1024
      maximum_ring_size: 16384
```

#### 5.1.4 随机（Random）

```yaml
clusters:
- name: random_cluster
  lb_policy: RANDOM
```

### 5.2 一致性哈希

```yaml
routes:
- match:
    prefix: "/api"
  route:
    cluster: api_cluster
    hash_policy:
    - header:
        header_name: x-user-id
    - cookie:
        name: session_id
        ttl: 0s
        path: /
```

## 6. 健康检查机制

### 6.1 HTTP 健康检查

```yaml
health_checks:
- timeout: 5s
  interval: 30s
  unhealthy_threshold: 3
  healthy_threshold: 2
  http_health_check:
    path: /health
    expected_statuses:
      - start: 200
        end: 399
    method: GET
    host: health-check.example.com
```

### 6.2 TCP 健康检查

```yaml
health_checks:
- timeout: 5s
  interval: 30s
  unhealthy_threshold: 3
  healthy_threshold: 2
  tcp_health_check:
    send:
      text: "PING\r\n"
    receive:
    - text: "PONG"
```

### 6.3 gRPC 健康检查

```yaml
health_checks:
- timeout: 5s
  interval: 30s
  unhealthy_threshold: 3
  healthy_threshold: 2
  grpc_health_check:
    service_name: grpc.health.v1.Health
    authority: health-check.example.com
```

## 7. 端点发现

### 7.1 静态端点配置

```yaml
clusters:
- name: static_cluster
  type: STATIC
  load_assignment:
    cluster_name: static_cluster
    endpoints:
    - lb_endpoints:
      - endpoint:
          address:
            socket_address:
              address: 10.0.0.1
              port_value: 8080
      - endpoint:
          address:
            socket_address:
              address: 10.0.0.2
              port_value: 8080
```

### 7.2 动态端点发现（EDS）

```yaml
clusters:
- name: eds_cluster
  type: EDS
  eds_cluster_config:
    eds_config:
      api_config_source:
        api_type: GRPC
        grpc_services:
        - envoy_grpc:
            cluster_name: xds_cluster
```

## 8. 高级特性

### 8.1 熔断器配置

```yaml
circuit_breakers:
  thresholds:
  - priority: DEFAULT
    max_connections: 1000
    max_pending_requests: 1000
    max_requests: 1000
    max_retries: 3
  - priority: HIGH
    max_connections: 2000
    max_pending_requests: 2000
    max_requests: 2000
    max_retries: 5
```

### 8.2 超时配置

```yaml
routes:
- match:
    prefix: "/api"
  route:
    cluster: api_cluster
    timeout: 5s
    retry_policy:
      retry_on: connect-failure,refused-stream,unavailable
      num_retries: 3
      per_try_timeout: 2s
      retry_host_predicate:
      - name: envoy.retry_host_predicates.previous_hosts
```

### 8.3 重试策略

```yaml
retry_policy:
  retry_on: 5xx,gateway-error,connect-failure,refused-stream
  num_retries: 3
  per_try_timeout: 2s
  retry_back_off:
    base_interval: 0.25s
    max_interval: 60s
  retry_host_predicate:
  - name: envoy.retry_host_predicates.previous_hosts
  retry_priority:
    name: envoy.retry_priorities.previous_priorities
    typed_config:
      "@type": type.googleapis.com/envoy.config.retry.previous_priorities.PreviousPrioritiesConfig
      update_frequency: 2
```

## 9. 性能优化

### 9.1 连接池优化

```yaml
clusters:
- name: optimized_cluster
  connect_timeout: 0.25s
  per_connection_buffer_limit_bytes: 32768
  upstream_connection_options:
    tcp_keepalive:
      keepalive_probes: 3
      keepalive_time: 300
      keepalive_interval: 60
```

### 9.2 缓冲区配置

```yaml
listeners:
- name: optimized_listener
  per_connection_buffer_limit_bytes: 32768
  filter_chains:
  - filters:
    - name: envoy.filters.network.http_connection_manager
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
        stream_idle_timeout: 300s
        request_timeout: 300s
        drain_timeout: 600s
        delayed_close_timeout: 1s
```

## 10. 监控与调试

### 10.1 统计配置

```yaml
stats_config:
  stats_tags:
  - tag_name: cluster_name
    regex: "^cluster\\.((.+?)\\.)"
  - tag_name: route_name
    regex: "^http\\.ingress_http\\.((.+?)\\.)"
  use_all_default_tags: true

stats_flush_interval: 60s
```

### 10.2 管理接口

```yaml
admin:
  access_log_path: /tmp/admin_access.log
  address:
    socket_address:
      address: 127.0.0.1
      port_value: 9901
```

### 10.3 调试工具

```bash
# 查看配置
curl http://localhost:9901/config_dump

# 查看统计信息
curl http://localhost:9901/stats

# 查看集群信息
curl http://localhost:9901/clusters

# 查看监听器信息
curl http://localhost:9901/listeners
```

## 11. 最佳实践

### 11.1 配置模板

```yaml
# 基础配置模板
node:
  cluster: ${CLUSTER_NAME}
  id: ${NODE_ID}

admin:
  access_log_path: /tmp/admin_access.log
  address:
    socket_address:
      address: 127.0.0.1
      port_value: 9901

static_resources:
  listeners:
  - name: listener_0
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 10000
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
  clusters:
  - name: service_cluster
    connect_timeout: 0.25s
    type: STATIC
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: service_cluster
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: 127.0.0.1
                port_value: 8080
```

### 11.2 性能优化配置

```yaml
# 高性能配置
clusters:
- name: high_perf_cluster
  connect_timeout: 0.1s
  per_connection_buffer_limit_bytes: 32768
  upstream_connection_options:
    tcp_keepalive:
      keepalive_probes: 3
      keepalive_time: 300
      keepalive_interval: 60
  http2_protocol_options:
    max_concurrent_streams: 100
    initial_stream_window_size: 65536
    initial_connection_window_size: 1048576
```

---

**下一章预告：** 第10章将深入探讨 Envoy 配置与过滤器机制，包括自定义过滤器开发、Wasm 扩展等高级功能。