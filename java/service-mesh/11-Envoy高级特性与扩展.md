# 11. Envoy 高级特性与扩展

## 1. Wasm 扩展机制

### 1.1 Wasm 运行时配置

#### 1.1.1 V8 运行时配置

```yaml
http_filters:
- name: envoy.filters.http.wasm
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.wasm.v3.Wasm
    config:
      name: "custom_wasm_filter"
      vm_id: "custom_vm"
      runtime: "envoy.wasm.runtime.v8"
      configuration:
        "@type": type.googleapis.com/google.protobuf.StringValue
        value: |
          {
            "key": "value",
            "config_key": "config_value"
          }
      code:
        local:
          filename: "/etc/envoy/filters/custom.wasm"
```

#### 1.1.2 WasmTime 运行时配置

```yaml
http_filters:
- name: envoy.filters.http.wasm
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.wasm.v3.Wasm
    config:
      name: "wasmtime_filter"
      vm_id: "wasmtime_vm"
      runtime: "envoy.wasm.runtime.wasmtime"
      configuration:
        "@type": type.googleapis.com/google.protobuf.Struct
        value:
          config_key: "config_value"
          nested_config:
            key: "nested_value"
      code:
        remote:
          http_uri:
            uri: "https://storage.example.com/filters/custom.wasm"
            cluster: wasm_storage_cluster
            timeout: 30s
          sha256: "a1b2c3d4e5f6..."
```

### 1.2 Wasm 过滤器开发

#### 1.2.1 Rust Wasm 过滤器示例

```rust
use proxy_wasm::traits::*;
use proxy_wasm::types::*;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct FilterConfig {
    api_key: String,
    rate_limit: u32,
}

proxy_wasm::main! {}

struct CustomFilter;

impl Context for CustomFilter {}

impl HttpContext for CustomFilter {
    fn on_http_request_headers(&mut self, _num_headers: usize, _end_of_stream: bool) -> Action {
        // 读取配置
        let config = self.get_configuration()
            .and_then(|bytes| serde_json::from_slice::<FilterConfig>(&bytes).ok());
        
        if let Some(cfg) = config {
            // 验证 API 密钥
            let api_key = self.get_http_request_header("x-api-key");
            if api_key != Some(cfg.api_key.as_str()) {
                self.send_http_response(401, vec![], Some(b"Unauthorized"));
                return Action::Pause;
            }
            
            // 速率限制检查
            if self.check_rate_limit(cfg.rate_limit) {
                self.send_http_response(429, vec![], Some(b"Rate limit exceeded"));
                return Action::Pause;
            }
        }
        
        Action::Continue
    }
    
    fn on_http_response_headers(&mut self, _num_headers: usize, _end_of_stream: bool) -> Action {
        // 添加响应头
        self.set_http_response_header("x-processed-by", Some("custom-wasm-filter"));
        Action::Continue
    }
}

impl CustomFilter {
    fn check_rate_limit(&self, limit: u32) -> bool {
        // 实现速率限制逻辑
        false
    }
}
```

#### 1.2.2 AssemblyScript Wasm 过滤器

```typescript
// custom-filter.ts
export * from "@solo-io/proxy-runtime/proxy";
import { RootContext, Context, FilterHeadersStatusValues } from "@solo-io/proxy-runtime/proxy";

class CustomFilterRoot extends RootContext {
    configuration: string;
    
    onConfigure(configurationSize: number): bool {
        this.configuration = this.getConfiguration();
        return true;
    }
    
    createContext(context_id: u32): Context {
        return new CustomFilter(context_id, this.configuration);
    }
}

class CustomFilter extends Context {
    configuration: string;
    
    constructor(context_id: u32, configuration: string) {
        super(context_id);
        this.configuration = configuration;
    }
    
    onRequestHeaders(headerCount: i32): FilterHeadersStatusValues {
        // 处理请求头
        const path = this.getRequestHeader(":path");
        this.logInfo(`Processing request: ${path}`);
        
        // 添加自定义头
        this.setRequestHeader("x-custom-filter", "enabled");
        
        return FilterHeadersStatusValues.Continue;
    }
    
    onResponseHeaders(headerCount: i32): FilterHeadersStatusValues {
        // 处理响应头
        this.setResponseHeader("x-processed-by", "assemblyscript-filter");
        return FilterHeadersStatusValues.Continue;
    }
}

// 注册根上下文
registerRootContext((context_id: u32) => new CustomFilterRoot(context_id), "custom_filter");
```

## 2. 外部授权集成

### 2.1 外部授权服务配置

```yaml
http_filters:
- name: envoy.filters.http.ext_authz
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.ext_authz.v3.ExtAuthz
    transport_api_version: V3
    failure_mode_allow: false
    with_request_body:
      max_request_bytes: 1024
      allow_partial_message: true
    status_on_error:
      code: ServiceUnavailable
    grpc_service:
      envoy_grpc:
        cluster_name: ext_authz_service
      timeout: 0.25s
      initial_metadata:
      - key: "x-client-version"
        value: "v1.0.0"
```

### 2.2 自定义授权检查

```yaml
- name: envoy.filters.http.ext_authz
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.ext_authz.v3.ExtAuthz
    http_service:
      server_uri:
        uri: http://auth-service:8080/check
        cluster: auth_service_cluster
        timeout: 5s
      path_prefix: /v1/auth
      authorization_request:
        allowed_headers:
          patterns:
          - exact: "authorization"
          - exact: "x-api-key"
          - prefix: "x-custom-"
        headers_to_add:
        - key: "x-envoy-client-ip"
          value: "%DOWNSTREAM_REMOTE_ADDRESS_WITHOUT_PORT%"
      authorization_response:
        allowed_upstream_headers:
          patterns:
          - exact: "x-user-id"
          - exact: "x-user-role"
        allowed_client_headers:
          patterns:
          - exact: "x-set-cookie"
```

## 3. 高级负载均衡

### 3.1 自定义负载均衡器

```yaml
clusters:
- name: custom_lb_cluster
  lb_policy: CLUSTER_PROVIDED
  cluster_type:
    name: envoy.clusters.custom_dns
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.clusters.dynamic_forward_proxy.v3.ClusterConfig
      dns_cache_config:
        name: dynamic_forward_proxy_cache_config
        dns_lookup_family: V4_ONLY
        max_hosts: 1024
```

### 3.2 位置感知负载均衡

```yaml
clusters:
- name: locality_aware_cluster
  lb_policy: ROUND_ROBIN
  common_lb_config:
    healthy_panic_threshold:
      value: 50
    zone_aware_lb_config:
      routing_enabled:
        value: 100
      min_cluster_size: 6
  load_assignment:
    cluster_name: locality_aware_cluster
    endpoints:
    - locality:
        region: "us-east-1"
        zone: "us-east-1a"
      lb_endpoints:
      - endpoint:
          address:
            socket_address:
              address: 10.0.1.1
              port_value: 8080
        load_balancing_weight: 70
      - endpoint:
          address:
            socket_address:
              address: 10.0.1.2
              port_value: 8080
        load_balancing_weight: 30
    - locality:
        region: "us-west-1"
        zone: "us-west-1a"
      lb_endpoints:
      - endpoint:
          address:
            socket_address:
              address: 10.0.2.1
              port_value: 8080
        load_balancing_weight: 50
```

## 4. 协议转换与桥接

### 4.1 HTTP/gRPC 桥接

```yaml
http_filters:
- name: envoy.filters.http.grpc_http1_bridge
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_http1_bridge.v3.Config
- name: envoy.filters.http.grpc_json_transcoder
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_json_transcoder.v3.GrpcJsonTranscoder
    proto_descriptor: "/etc/envoy/protos/descriptor.pb"
    services: ["helloworld.Greeter"]
    print_options:
      add_whitespace: true
      always_print_primitive_fields: true
      always_print_enums_as_ints: false
      preserve_proto_field_names: false
```

### 4.2 WebSocket 支持

```yaml
http_filters:
- name: envoy.filters.http.websocket
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.websocket.v3.WebSocketConfig
    enabled: true
    idle_timeout: 3600s
    max_connect_attempts: 3
```

## 5. 高级流量控制

### 5.1 自适应并发控制

```yaml
clusters:
- name: adaptive_cluster
  circuit_breakers:
    thresholds:
    - priority: DEFAULT
      max_connections: 1000
      max_pending_requests: 1000
      max_requests: 1000
      max_retries: 3
  outlier_detection:
    consecutive_5xx: 5
    interval: 30s
    base_ejection_time: 30s
    max_ejection_percent: 50
    enforcing_consecutive_5xx: 100
    enforcing_success_rate: 100
    success_rate_minimum_hosts: 5
    success_rate_request_volume: 100
    success_rate_stdev_factor: 1900
```

### 5.2 请求镜像

```yaml
routes:
- match:
    prefix: "/api"
  route:
    cluster: primary_cluster
    request_mirror_policies:
    - cluster: mirror_cluster
      runtime_fraction:
        default_value:
          numerator: 10
          denominator: HUNDRED
      trace_sampled: true
```

## 6. 自定义访问日志

### 6.1 结构化日志格式

```yaml
access_log:
- name: envoy.access_loggers.file
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: /dev/stdout
    format: |
      {
        "timestamp": "%START_TIME%",
        "method": "%REQ(:METHOD)%",
        "path": "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%",
        "protocol": "%PROTOCOL%",
        "response_code": "%RESPONSE_CODE%",
        "response_flags": "%RESPONSE_FLAGS%",
        "bytes_received": "%BYTES_RECEIVED%",
        "bytes_sent": "%BYTES_SENT%",
        "duration": "%DURATION%",
        "upstream_service_time": "%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%",
        "x_forwarded_for": "%REQ(X-FORWARDED-FOR)%",
        "user_agent": "%REQ(USER-AGENT)%",
        "request_id": "%REQ(X-REQUEST-ID)%",
        "authority": "%REQ(:AUTHORITY)%",
        "upstream_host": "%UPSTREAM_HOST%"
      }
```

### 6.2 gRPC 访问日志

```yaml
access_log:
- name: envoy.access_loggers.grpc
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.grpc.v3.HttpGrpcAccessLogConfig
    common_config:
      log_name: envoy_access_log
      grpc_service:
        envoy_grpc:
          cluster_name: access_log_service
      transport_api_version: V3
    additional_request_headers_to_log:
    - "x-custom-header"
    - "x-user-id"
    additional_response_headers_to_log:
    - "x-response-time"
    - "x-trace-id"
    additional_response_trailers_to_log:
    - "grpc-status"
    - "grpc-message"
```

## 7. 高级监控指标

### 7.1 自定义指标

```yaml
stats_config:
  stats_tags:
  - tag_name: api_version
    fixed_value: "v2"
  - tag_name: endpoint
    regex: "^/api/v[0-9]+/([^/?#]+)"
  - tag_name: status_category
    regex: "^([0-9])[0-9][0-9]$"
    
stats_matcher:
  inclusion_list:
    patterns:
    - prefix: "cluster."
    - prefix: "listener."
    - exact: "http.ingress_http.downstream_rq_total"
    - suffix: "_bucket"
```

### 7.2 指标聚合

```yaml
clusters:
- name: monitored_cluster
  stats:
    timeout_budgets: true
    request_response_sizes: true
    upstream_rq_retry: true
    upstream_rq_timeout: true
    
  upstream_config:
    alt_stat_name: "custom_cluster_stats"
```

## 8. 安全扩展

### 8.1 自定义 TLS 验证

```yaml
transport_socket:
  name: envoy.transport_sockets.tls
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.UpstreamTlsContext
    common_tls_context:
      validation_context:
        custom_validator_config:
          name: envoy.tls.cert_validator.custom
          typed_config:
            "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.CertValidatorConfig
            ca_cert: "/etc/ssl/certs/ca.pem"
            crl: "/etc/ssl/certs/crl.pem"
```

### 8.2 外部证书管理

```yaml
transport_socket:
  name: envoy.transport_sockets.tls
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
    common_tls_context:
      tls_certificate_sds_secret_configs:
      - name: server-cert
        sds_config:
          resource_api_version: V3
          api_config_source:
            api_type: GRPC
            transport_api_version: V3
            grpc_services:
            - envoy_grpc:
                cluster_name: sds_cluster
      validation_context_sds_secret_config:
        name: validation-context
        sds_config:
          resource_api_version: V3
          api_config_source:
            api_type: GRPC
            transport_api_version: V3
            grpc_services:
            - envoy_grpc:
                cluster_name: sds_cluster
```

## 9. 性能优化扩展

### 9.1 连接复用优化

```yaml
clusters:
- name: optimized_cluster
  upstream_connection_options:
    tcp_keepalive:
      keepalive_probes: 3
      keepalive_time: 300
      keepalive_interval: 60
    
  upstream_http_protocol_options:
    auto_sni: true
    auto_san_validation: true
    
  http2_protocol_options:
    max_concurrent_streams: 100
    initial_stream_window_size: 65536
    initial_connection_window_size: 1048576
    max_outbound_frames: 10000
    max_outbound_control_frames: 1000
    max_consecutive_inbound_frames_with_empty_payload: 1
    max_inbound_priority_frames_per_stream: 100
    max_inbound_window_update_frames_per_data_frame_sent: 10
```

### 9.2 内存管理优化

```yaml
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
  
  - name: envoy.overload_actions.disable_http_keep_alive
    triggers:
    - name: envoy.resource_monitors.fixed_heap
      threshold:
        value: 0.90
```

## 10. 调试与故障排查

### 10.1 高级调试配置

```yaml
admin:
  access_log_path: /tmp/admin_access.log
  address:
    socket_address:
      address: 127.0.0.1
      port_value: 9901
  
layered_runtime:
  layers:
  - name: static_layer
    static_layer:
      health_check:
        min_interval: 5
      overload:
        global_downstream_max_connections: 50000
  - name: admin_layer
    admin_layer: {}
```

### 10.2 性能分析配置

```yaml
# 启用性能分析
tracing:
  http:
    name: envoy.tracers.dynamic_ot
    typed_config:
      "@type": type.googleapis.com/envoy.config.trace.v3.DynamicOtConfig
      library: /usr/local/lib/libjaegertracing_plugin.so
      config:
        service_name: envoy-proxy
        sampler:
          type: const
          param: 1
        reporter:
          logSpans: true
          localAgentHostPort: jaeger:6831
```

---

**下一章预告：** 第12章将重点讲解 Java 微服务与 Service Mesh 的集成实践，包括 Spring Cloud、Micronaut、Quarkus 等框架的具体集成方案。