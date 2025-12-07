# 10. Envoy 配置与过滤器机制

## 1. 配置管理架构

### 1.1 xDS API 协议家族

**xDS 协议组件：**
- **LDS**: Listener Discovery Service
- **RDS**: Route Discovery Service  
- **CDS**: Cluster Discovery Service
- **EDS**: Endpoint Discovery Service
- **SDS**: Secret Discovery Service

### 1.2 配置发现流程

```yaml
# xDS 配置示例
node:
  id: envoy-node-1
  cluster: production
  metadata:
    version: "1.0.0"
    region: "us-east-1"

dynamic_resources:
  lds_config:
    resource_api_version: V3
    api_config_source:
      api_type: GRPC
      transport_api_version: V3
      grpc_services:
      - envoy_grpc:
          cluster_name: xds_cluster
  cds_config:
    resource_api_version: V3
    api_config_source:
      api_type: GRPC
      transport_api_version: V3
      grpc_services:
      - envoy_grpc:
          cluster_name: xds_cluster
```

## 2. 过滤器链机制

### 2.1 过滤器执行顺序

#### 2.1.1 网络过滤器链

```yaml
filter_chains:
- filters:
  - name: envoy.filters.network.client_ssl_auth
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.network.client_ssl_auth.v3.ClientSSLAuth
      auth_api_cluster: auth_service
      stat_prefix: client_ssl_auth
  - name: envoy.filters.network.http_connection_manager
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
      stat_prefix: ingress_http
      http_filters:
      - name: envoy.filters.http.cors
      - name: envoy.filters.http.fault
      - name: envoy.filters.http.router
```

#### 2.1.2 HTTP 过滤器链

```yaml
http_filters:
# 1. 认证过滤器
- name: envoy.filters.http.jwt_authn
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.jwt_authn.v3.JwtAuthentication
    providers:
      example_provider:
        issuer: https://example.com
        audiences:
        - api.example.com
        remote_jwks:
          http_uri:
            uri: https://example.com/.well-known/jwks.json
            cluster: jwks_cluster
            timeout: 5s
          cache_duration: 300s
    rules:
    - match:
        prefix: /api
      requires:
        provider_name: example_provider

# 2. 速率限制过滤器
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

# 3. 路由器过滤器
- name: envoy.filters.http.router
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
```

### 2.2 过滤器配置深度解析

#### 2.2.1 JWT 认证过滤器

```yaml
- name: envoy.filters.http.jwt_authn
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.jwt_authn.v3.JwtAuthentication
    providers:
      auth0_provider:
        issuer: https://dev-123456.auth0.com/
        audiences:
        - https://api.example.com
        - https://mobile.example.com
        from_headers:
        - name: Authorization
          value_prefix: "Bearer "
        from_params:
        - access_token
        forward: true
        forward_payload_header: x-jwt-payload
        payload_in_metadata: jwt_payload
        remote_jwks:
          http_uri:
            uri: https://dev-123456.auth0.com/.well-known/jwks.json
            cluster: auth0_jwks_cluster
            timeout: 5s
          cache_duration:
            seconds: 300
          async_fetch:
            fast_listener: true
    rules:
    - match:
        prefix: /api/secure
      requires:
        requires_any:
          requirements:
          - provider_name: auth0_provider
          - allow_missing: {}
    - match:
        prefix: /api/public
      requires:
        allow_missing: {}
```

#### 2.2.2 故障注入过滤器

```yaml
- name: envoy.filters.http.fault
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.fault.v3.HTTPFault
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
    max_active_faults: 100
    response_rate_limit:
      percentage:
        numerator: 10
        denominator: HUNDRED
      limit_kbps: 100
```

## 3. 高级路由配置

### 3.1 虚拟主机配置

```yaml
virtual_hosts:
- name: api_gateway
  domains:
  - "api.example.com"
  - "*.api.example.com"
  routes:
  - match:
      prefix: "/v1/users"
      headers:
      - name: x-version
        exact_match: "beta"
    route:
      cluster: users_v2_cluster
      prefix_rewrite: "/api/v2/users"
      timeout: 10s
      retry_policy:
        retry_on: 5xx,gateway-error
        num_retries: 3
        per_try_timeout: 2s
        retry_host_predicate:
        - name: envoy.retry_host_predicates.previous_hosts
  - match:
      prefix: "/v1/products"
      query_parameters:
      - name: category
        string_match:
          exact: "electronics"
    route:
      weighted_clusters:
        clusters:
        - name: products_electronics_cluster
          weight: 80
        - name: products_general_cluster
          weight: 20
      max_grpc_timeout: 5s
  - match:
      path: "/health"
    direct_response:
      status: 200
      body:
        inline_string: "OK"
  - match:
      prefix: "/"
    redirect:
      path_redirect: "/docs"
      https_redirect: true
```

### 3.2 高级匹配规则

#### 3.2.1 正则表达式匹配

```yaml
routes:
- match:
    safe_regex:
      regex: "^/api/v[0-9]+/users/[0-9]+$"
  route:
    cluster: users_api_cluster
- match:
    safe_regex:
      regex: "^/api/v[0-9]+/products/[a-zA-Z0-9_-]+$"
  route:
    cluster: products_api_cluster
```

#### 3.2.2 复杂条件匹配

```yaml
routes:
- match:
    prefix: "/api"
    headers:
    - name: x-user-role
      string_match:
        exact: "admin"
    - name: x-region
      string_match:
        exact: "us-east"
    query_parameters:
    - name: debug
      string_match:
        exact: "true"
  route:
    cluster: admin_api_cluster
    metadata_match:
      filter_metadata:
        envoy.lb:
          canary: false
```

## 4. 集群高级配置

### 4.1 负载均衡配置

```yaml
clusters:
- name: weighted_cluster
  type: EDS
  lb_policy: ROUND_ROBIN
  load_assignment:
    cluster_name: weighted_cluster
    endpoints:
    - lb_endpoints:
      - endpoint:
          address:
            socket_address:
              address: 10.0.1.1
              port_value: 8080
        load_balancing_weight: 70
        metadata:
          filter_metadata:
            envoy.lb:
              version: "v1"
              zone: "us-east-1a"
      - endpoint:
          address:
            socket_address:
              address: 10.0.1.2
              port_value: 8080
        load_balancing_weight: 30
        metadata:
          filter_metadata:
            envoy.lb:
              version: "v2"
              zone: "us-east-1b"
  common_lb_config:
    healthy_panic_threshold:
      value: 50
    zone_aware_lb_config:
      routing_enabled:
        value: 100
      min_cluster_size: 6
```

### 4.2 健康检查高级配置

```yaml
health_checks:
- timeout: 5s
  interval: 30s
  interval_jitter: 15s
  unhealthy_threshold: 3
  healthy_threshold: 2
  no_traffic_interval: 60s
  unhealthy_interval: 5s
  unhealthy_edge_interval: 10s
  healthy_edge_interval: 10s
  event_log_path: /tmp/health_events.log
  always_log_health_check_failures: true
  tcp_health_check:
    send:
      text: "01020304"
    receive:
    - text: "04030201"
  event_service:
    grpc_service:
      envoy_grpc:
        cluster_name: health_event_service
```

## 5. 自定义过滤器开发

### 5.1 Lua 过滤器

```yaml
http_filters:
- name: envoy.filters.http.lua
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
    inline_code: |
      function envoy_on_request(request_handle)
        -- 添加自定义头部
        request_handle:headers():add("x-custom-header", "custom-value")
        
        -- 记录请求信息
        local path = request_handle:headers():get(":path")
        request_handle:logInfo("Processing request: " .. path)
        
        -- 请求验证
        local auth_header = request_handle:headers():get("authorization")
        if not auth_header then
          request_handle:respond(
            {[":status"] = "401"},
            "Unauthorized"
          )
          return
        end
      end
      
      function envoy_on_response(response_handle)
        -- 添加响应头部
        response_handle:headers():add("x-response-time", os.date())
        
        -- 修改响应状态码
        if response_handle:headers():get(":status") == "404" then
          response_handle:headers():replace(":status", "200")
          response_handle:body():setBytes("Custom 404 Handler")
        end
      end
```

### 5.2 Wasm 过滤器

```yaml
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
        configuration:
          "@type": type.googleapis.com/google.protobuf.StringValue
          value: |
            {
              "key": "value",
              "number": 42
            }
```

## 6. 扩展配置机制

### 6.1 TypedExtensionConfig

```yaml
typed_extension_protocol_options:
  envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
    "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
    explicit_http_config:
      http2_protocol_options:
        max_concurrent_streams: 100
        initial_stream_window_size: 65536
        initial_connection_window_size: 1048576
```

### 6.2 自定义协议选项

```yaml
clusters:
- name: custom_protocol_cluster
  typed_extension_protocol_options:
    envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
      "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
      common_http_protocol_options:
        idle_timeout: 3600s
        max_connection_duration: 7200s
      upstream_http_protocol_options:
        auto_sni: true
        auto_san_validation: true
```

## 7. 配置验证与测试

### 7.1 配置验证工具

```bash
# 验证配置语法
envoy --mode validate --config-path /path/to/config.yaml

# 检查配置转储
curl -s http://localhost:9901/config_dump | jq .

# 测试路由配置
curl -s http://localhost:9901/routes | jq .
```

### 7.2 单元测试配置

```yaml
# 测试配置示例
static_resources:
  listeners:
  - name: test_listener
    address:
      socket_address:
        address: 127.0.0.1
        port_value: 10001
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: test
          route_config:
            name: test_route
            virtual_hosts:
            - name: test_service
              domains: ["test.example.com"]
              routes:
              - match:
                  prefix: "/test"
                direct_response:
                  status: 200
                  body:
                    inline_string: "TEST_OK"
          http_filters:
          - name: envoy.filters.http.router
```

## 8. 性能优化配置

### 8.1 连接池优化

```yaml
clusters:
- name: optimized_cluster
  connect_timeout: 0.1s
  per_connection_buffer_limit_bytes: 32768
  upstream_connection_options:
    tcp_keepalive:
      keepalive_probes: 3
      keepalive_time: 300
      keepalive_interval: 60
  circuit_breakers:
    thresholds:
    - priority: DEFAULT
      max_connections: 10000
      max_pending_requests: 10000
      max_requests: 10000
      max_retries: 3
    - priority: HIGH
      max_connections: 20000
      max_pending_requests: 20000
      max_requests: 20000
      max_retries: 5
```

### 8.2 内存优化

```yaml
# 内存限制配置
overload_manager:
  refresh_interval: 0.25s
  resource_monitors:
  - name: envoy.resource_monitors.fixed_heap
    typed_config:
      "@type": type.googleapis.com/envoy.config.resource_monitor.fixed_heap.v2alpha.FixedHeapConfig
      max_heap_size_bytes: 2147483648
  actions:
  - name: envoy.overload_actions.stop_accepting_requests
    triggers:
    - name: envoy.resource_monitors.fixed_heap
      threshold:
        value: 0.95
```

## 9. 安全配置

### 9.1 TLS 配置

```yaml
transport_socket:
  name: envoy.transport_sockets.tls
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.UpstreamTlsContext
    common_tls_context:
      tls_params:
        tls_minimum_protocol_version: TLSv1_2
        tls_maximum_protocol_version: TLSv1_3
        cipher_suites:
        - ECDHE-ECDSA-AES128-GCM-SHA256
        - ECDHE-RSA-AES128-GCM-SHA256
        - ECDHE-ECDSA-AES256-GCM-SHA384
        - ECDHE-RSA-AES256-GCM-SHA384
      validation_context:
        trusted_ca:
          filename: /etc/ssl/certs/ca-certificates.crt
        verify_subject_alt_name:
        - "*.example.com"
    sni: api.example.com
```

### 9.2 网络策略

```yaml
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
  - name: envoy.filters.network.http_connection_manager
```

## 10. 监控与调试

### 10.1 统计配置

```yaml
stats_config:
  stats_tags:
  - tag_name: cluster_name
    regex: "^cluster\\.((.+?)\\.)"
  - tag_name: response_code
    regex: "^response_code\\.((.+?)\\.)"
  - tag_name: zone
    fixed_value: "us-east-1"
  use_all_default_tags: true
  stats_matcher:
    inclusion_list:
      patterns:
      - prefix: "cluster."
      - prefix: "listener."
      - exact: "http.ingress_http.downstream_rq_total"
```

### 10.2 追踪配置

```yaml
tracing:
  http:
    name: envoy.tracers.zipkin
    typed_config:
      "@type": type.googleapis.com/envoy.config.trace.v3.ZipkinConfig
      collector_cluster: zipkin
      collector_endpoint: "/api/v2/spans"
      collector_endpoint_version: HTTP_JSON
      shared_span_context: false
      trace_id_128bit: true
```

---

**下一章预告：** 第11章将探讨 Envoy 高级特性与扩展，包括自定义扩展开发、Wasm 运行时、外部授权等高级功能。