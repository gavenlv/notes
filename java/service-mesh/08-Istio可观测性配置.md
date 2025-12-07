# 08. Istio 可观测性配置

## 1. 可观测性架构概述

### 1.1 三大支柱

**Istio 可观测性核心组件：**
- **指标（Metrics）**：Prometheus + Grafana
- **追踪（Tracing）**：Jaeger, Zipkin
- **日志（Logging）**：Fluentd, ELK Stack

### 1.2 数据流架构

```yaml
# 可观测性数据流
Data Flow:
  Envoy Proxy → Mixer → Backend Systems
  - Metrics: Envoy → Prometheus → Grafana
  - Tracing: Envoy → Jaeger/Zipkin
  - Logs: Envoy → Fluentd → Elasticsearch → Kibana
```

## 2. 指标收集与监控

### 2.1 默认指标配置

#### 2.1.1 Istio 标准指标

**HTTP 指标：**
- `istio_requests_total`：请求总数
- `istio_request_duration_milliseconds`：请求延迟
- `istio_request_bytes`：请求大小
- `istio_response_bytes`：响应大小

**TCP 指标：**
- `istio_tcp_connections_opened_total`：TCP 连接数
- `istio_tcp_connections_closed_total`：TCP 关闭数
- `istio_tcp_received_bytes_total`：接收字节数
- `istio_tcp_sent_bytes_total`：发送字节数

#### 2.1.2 Prometheus 配置

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: istio-system
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    scrape_configs:
    - job_name: 'istio'
      kubernetes_sd_configs:
      - role: endpoints
        namespaces:
          names: ["istio-system"]
      relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        action: keep
        regex: 'istio-telemetry|istio-policy'
    
    - job_name: 'envoy-stats'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_container_name]
        action: keep
        regex: 'istio-proxy'
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\\d+)?;(\\d+)
        replacement: ${1}:15090
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: pod_name
```

### 2.2 自定义指标配置

#### 2.2.1 Telemetry API 配置

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: custom-metrics
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
      disabled: false
      tagOverrides:
        custom_tag:
          value: "api_gateway"
        response_code:
          value: "%RESPONSE_CODE%"
        request_operation:
          value: "%REQUEST_METHOD% %REQUEST_URL_PATH%"
    - match:
        metric: REQUEST_DURATION
      disabled: false
      tagOverrides:
        percentile:
          value: "50,90,95,99"
```

#### 2.2.2 业务指标集成

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: business-metrics
  namespace: product
spec:
  selector:
    matchLabels:
      app: product-service
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_COUNT
      tagOverrides:
        business_domain:
          value: "product_catalog"
        api_version:
          value: "v2"
        tenant_id:
          value: "%DYNAMIC_METADATA(com.mycompany.tenant)%"
```

## 3. 分布式追踪配置

### 3.1 Jaeger 集成配置

#### 3.1.1 追踪采样配置

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: tracing-config
  namespace: default
spec:
  selector:
    matchLabels:
      app: api-gateway
  tracing:
  - providers:
    - name: zipkin
    randomSamplingPercentage: 10.0
    customTags:
      environment:
        literal:
          value: "production"
      service_version:
        header:
          name: "x-service-version"
          defaultValue: "unknown"
      user_id:
        header:
          name: "x-user-id"
          defaultValue: "anonymous"
```

#### 3.1.2 追踪上下文传播

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: tracing-headers
  namespace: istio-system
spec:
  workloadSelector:
    labels:
      app: api-gateway
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
    patch:
      operation: MERGE
      value:
        name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          tracing:
            client_sampling:
              value: 100
            random_sampling:
              value: 10
            overall_sampling:
              value: 100
            custom_tags:
            - tag: liveness
              literal:
                value: live
            - tag: zone
              environment:
                name: ZONE
                default_value: unknown
```

### 3.2 自定义追踪配置

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: detailed-tracing
  namespace: critical
spec:
  selector:
    matchLabels:
      app: payment-service
  tracing:
  - providers:
    - name: zipkin
    randomSamplingPercentage: 100.0
    customTags:
      transaction_id:
        header:
          name: x-transaction-id
          defaultValue: "not_set"
      payment_amount:
        header:
          name: x-payment-amount
          defaultValue: "0"
      merchant_id:
        header:
          name: x-merchant-id
          defaultValue: "unknown"
```

## 4. 日志配置与管理

### 4.1 访问日志配置

#### 4.1.1 结构化日志格式

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: access-logging
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
        duration > 1000 or
        response.flags != ""
```

#### 4.1.2 自定义日志格式

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: custom-access-logs
  namespace: istio-system
spec:
  workloadSelector:
    labels:
      app: api-gateway
  configPatches:
  - applyTo: NETWORK_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
    patch:
      operation: MERGE
      value:
        name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
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
                  "upstream_host": "%UPSTREAM_HOST%",
                  "service_name": "api-gateway",
                  "namespace": "default"
                }
```

### 4.2 应用日志集成

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: istio-system
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      read_from_head true
      <parse>
        @type multi_format
        <pattern>
          format json
          time_key time
          time_format %Y-%m-%dT%H:%M:%S.%NZ
        </pattern>
        <pattern>
          format /^(?<time>.+) (?<stream>stdout|stderr) (?<logtag>P|F) (?<log>.+)$/
          time_format %Y-%m-%dT%H:%M:%S.%N%:z
        </pattern>
      </parse>
    </source>
    
    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      logstash_format true
      logstash_prefix kubernetes
    </match>
```

## 5. Grafana 仪表板配置

### 5.1 Istio 标准仪表板

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: istio-grafana-dashboards
  namespace: istio-system
data:
  istio-mesh-dashboard.json: |
    {
      "__inputs": [],
      "__requires": [
        {
          "type": "grafana",
          "id": "grafana",
          "name": "Grafana",
          "version": "5.4.3"
        },
        {
          "type": "panel",
          "id": "graph",
          "name": "Graph",
          "version": "5.0.0"
        }
      ],
      "annotations": {
        "list": [
          {
            "builtIn": 1,
            "datasource": "-- Grafana --",
            "enable": true,
            "hide": true,
            "iconColor": "rgba(0, 211, 255, 1)",
            "name": "Annotations & Alerts",
            "type": "dashboard"
          }
        ]
      },
      "editable": true,
      "gnetId": null,
      "graphTooltip": 0,
      "id": null,
      "links": [],
      "panels": [
        {
          "aliasColors": {},
          "bars": false,
          "dashLength": 10,
          "dashes": false,
          "datasource": "Prometheus",
          "fill": 1,
          "gridPos": {
            "h": 8,
            "w": 12,
            "x": 0,
            "y": 0
          },
          "id": 1,
          "legend": {
            "avg": false,
            "current": false,
            "max": false,
            "min": false,
            "show": true,
            "total": false,
            "values": false
          },
          "lines": true,
          "linewidth": 1,
          "nullPointMode": "null",
          "percentage": false,
          "pointradius": 2,
          "points": false,
          "renderer": "flot",
          "seriesOverrides": [],
          "spaceLength": 10,
          "stack": false,
          "steppedLine": false,
          "targets": [
            {
              "expr": "sum(rate(istio_requests_total{reporter=\"destination\"}[5m])) by (response_code)",
              "format": "time_series",
              "intervalFactor": 1,
              "legendFormat": "{{response_code}}",
              "refId": "A"
            }
          ],
          "thresholds": [],
          "timeFrom": null,
          "timeShift": null,
          "title": "Request Rate by Response Code",
          "tooltip": {
            "shared": true,
            "sort": 0,
            "value_type": "individual"
          },
          "type": "graph",
          "xaxis": {
            "buckets": null,
            "mode": "time",
            "name": null,
            "show": true,
            "values": []
          },
          "yaxes": [
            {
              "format": "reqps",
              "label": null,
              "logBase": 1,
              "max": null,
              "min": null,
              "show": true
            },
            {
              "format": "short",
              "label": null,
              "logBase": 1,
              "max": null,
              "min": null,
              "show": true
            }
          ]
        }
      ],
      "refresh": "5s",
      "schemaVersion": 16,
      "style": "dark",
      "tags": [],
      "templating": {
        "list": [
          {
            "allValue": null,
            "current": {},
            "datasource": "Prometheus",
            "hide": 0,
            "includeAll": false,
            "label": "Namespace",
            "multi": false,
            "name": "namespace",
            "options": [],
            "query": "label_values(istio_requests_total, destination_workload_namespace)",
            "refresh": 1,
            "regex": "",
            "sort": 1,
            "tagValuesQuery": "",
            "tags": [],
            "tagsQuery": "",
            "type": "query",
            "useTags": false
          }
        ]
      },
      "time": {
        "from": "now-5m",
        "to": "now"
      },
      "timepicker": {
        "refresh_intervals": [
          "5s",
          "10s",
          "30s",
          "1m",
          "5m",
          "15m",
          "30m",
          "1h",
          "2h",
          "1d"
        ],
        "time_options": [
          "5m",
          "15m",
          "1h",
          "6h",
          "12h",
          "24h",
          "2d",
          "7d",
          "30d"
        ]
      },
      "timezone": "",
      "title": "Istio Mesh Dashboard",
      "uid": "istio-mesh-dashboard",
      "version": 1
    }
```

### 5.2 自定义业务仪表板

```json
{
  "panels": [
    {
      "title": "Business Transaction Rate",
      "targets": [
        {
          "expr": "sum(rate(business_transactions_total[5m])) by (transaction_type)",
          "legendFormat": "{{transaction_type}}"
        }
      ]
    },
    {
      "title": "Error Rate by Service",
      "targets": [
        {
          "expr": "sum(rate(istio_requests_total{response_code=~\"5..\"}[5m])) by (destination_service)",
          "legendFormat": "{{destination_service}}"
        }
      ]
    }
  ]
}
```

## 6. 告警配置

### 6.1 Prometheus 告警规则

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-alerts
  namespace: istio-system
data:
  alerts.yml: |
    groups:
    - name: istio.alerts
      rules:
      - alert: HighRequestLatency
        expr: histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket[1m])) by (le)) > 1000
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High request latency detected"
          description: "Request latency is above 1000ms for more than 2 minutes"
      
      - alert: ServiceErrorRateHigh
        expr: sum(rate(istio_requests_total{response_code=~"5.."}[5m])) / sum(rate(istio_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for more than 5 minutes"
      
      - alert: ServiceUnavailable
        expr: up{job="kubernetes-pods"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "Service has been unavailable for more than 1 minute"
```

### 6.2 Alertmanager 配置

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: istio-system
data:
  alertmanager.yml: |
    global:
      smtp_smarthost: 'smtp.example.com:587'
      smtp_from: 'alertmanager@example.com'
      smtp_auth_username: 'alertmanager'
      smtp_auth_password: 'password'
    
    route:
      group_by: ['alertname']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 1h
      receiver: 'web.hook'
      routes:
      - match:
          severity: critical
        receiver: 'critical-alerts'
        group_wait: 5s
    
    receivers:
    - name: 'web.hook'
      webhook_configs:
      - url: 'http://webhook.example.com/alerts'
    
    - name: 'critical-alerts'
      email_configs:
      - to: 'sre-team@example.com'
        headers:
          subject: 'Critical Alert: {{ .GroupLabels.alertname }}'
      pagerduty_configs:
      - service_key: 'your-pagerduty-key'
```

## 7. 性能优化配置

### 7.1 采样率优化

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: optimized-sampling
  namespace: high-traffic
spec:
  selector:
    matchLabels:
      app: high-traffic-service
  tracing:
  - providers:
    - name: zipkin
    randomSamplingPercentage: 1.0
    
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_COUNT
      reportingInterval: 30s
```

### 7.2 资源限制配置

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: observability-resources
  namespace: istio-system
data:
  resources.yaml: |
    # Prometheus 资源限制
    resources:
      requests:
        memory: 4Gi
        cpu: 2
      limits:
        memory: 8Gi
        cpu: 4
    
    # Grafana 资源限制
    resources:
      requests:
        memory: 512Mi
        cpu: 500m
      limits:
        memory: 1Gi
        cpu: 1
    
    # Jaeger 资源限制
    resources:
      requests:
        memory: 2Gi
        cpu: 1
      limits:
        memory: 4Gi
        cpu: 2
```

## 8. 故障排查与调试

### 8.1 监控数据检查

```bash
# 检查指标数据
kubectl exec -it deployment/product-service -c istio-proxy -- \\\n  curl http://localhost:15000/stats/prometheus

# 检查追踪数据
kubectl port-forward -n istio-system deployment/jaeger 16686:16686

# 检查日志配置
kubectl exec -it deployment/product-service -c istio-proxy -- \\\n  curl http://localhost:15000/logging
```

### 8.2 配置验证

```bash
# 验证 Telemetry 配置
istioctl analyze -n default

# 检查指标收集状态
kubectl get telemetry -n default

# 查看追踪采样配置
kubectl get telemetry -o yaml -n default
```

## 9. 最佳实践

### 9.1 分层监控策略

```yaml
# 基础层监控
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: base-monitoring
  namespace: default
spec:
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_COUNT
      disabled: false
    
# 业务层监控
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: business-monitoring
  namespace: product
spec:
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_COUNT
      tagOverrides:
        business_domain:
          value: "product"
```

### 9.2 成本优化

```yaml
# 采样率优化
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: cost-optimized
  namespace: default
spec:
  tracing:
  - providers:
    - name: zipkin
    randomSamplingPercentage: 1.0
    
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_DURATION
      reportingInterval: 60s
```

---

**下一章预告：** 第9章将深入探讨 Envoy 架构与核心功能，包括过滤器机制、负载均衡、健康检查等高级特性。