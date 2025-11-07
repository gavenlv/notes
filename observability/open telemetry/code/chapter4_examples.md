# 第4章示例代码：OpenTelemetry Collector

## 1. Collector配置示例

### 1.1 基本配置

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

exporters:
  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [logging]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [logging]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [logging]
```

### 1.2 高级配置

```yaml
# advanced-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
  prometheus:
    config:
      scrape_configs:
        - job_name: 'otel-collector'
          static_configs:
            - targets: ['localhost:8888']
  jaeger:
    protocols:
      grpc:
        endpoint: 0.0.0.0:14250
      thrift_http:
        endpoint: 0.0.0.0:14268

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  memory_limiter:
    limit_mib: 512
  resource:
    attributes:
      - key: environment
        value: production
        action: upsert
  attributes:
    actions:
      - key: db.user
        action: delete
      - key: sensitive.data
        action: hash

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
    namespace: "otel"
  jaeger:
    endpoint: jaeger-all-in-one:14250
    tls:
      insecure: true
  elasticsearch:
    endpoints: ["http://elasticsearch:9200"]
    index: "otel-logs"
  logging:
    loglevel: info

extensions:
  health_check:
    endpoint: 0.0.0.0:13133
  pprof:
    endpoint: 0.0.0.0:1777
  zpages:
    endpoint: 0.0.0.0:55679

service:
  extensions: [health_check, pprof, zpages]
  pipelines:
    traces:
      receivers: [otlp, jaeger]
      processors: [memory_limiter, batch, resource, attributes]
      exporters: [jaeger, logging]
    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch, resource]
      exporters: [prometheus, logging]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch, resource, attributes]
      exporters: [elasticsearch, logging]
```

## 2. Docker部署示例

### 2.1 基本Docker部署

```yaml
# docker-compose-basic.yaml
version: '3.7'

services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC receiver
      - "4318:4318"   # OTLP HTTP receiver
      - "8888:8888"   # Prometheus metrics
      - "8889:8889"   # Prometheus exporter
      - "13133:13133" # health_check extension
      - "55679:55679" # zpages extension
```

### 2.2 完整Docker部署

```yaml
# docker-compose-full.yaml
version: '3.7'

services:
  # OpenTelemetry Collector
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC receiver
      - "4318:4318"   # OTLP HTTP receiver
      - "8888:8888"   # Prometheus metrics exposed by the collector
      - "8889:8889"   # Prometheus exporter metrics
      - "13133:13133" # health_check extension
      - "55679:55679" # zpages extension
    depends_on:
      - jaeger-all-in-one
      - prometheus
      - elasticsearch

  # Jaeger
  jaeger-all-in-one:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
    environment:
      - COLLECTOR_OTLP_ENABLED=true

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --web.enable-lifecycle
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data

  # Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_URL: http://elasticsearch:9200
      ELASTICSEARCH_HOSTS: '["http://elasticsearch:9200"]'
    depends_on:
      - elasticsearch

volumes:
  es_data:
```

### 2.3 Prometheus配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8889']
```

## 3. Collector组件示例

### 3.1 接收器示例

```yaml
# receivers-example.yaml
receivers:
  # OTLP接收器
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
        cors:
          allowed_origins:
            - "http://*"
            - "https://*"
  
  # Prometheus接收器
  prometheus:
    config:
      scrape_configs:
        - job_name: 'kubernetes-pods'
          kubernetes_sd_configs:
            - role: pod
          relabel_configs:
            - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
              action: keep
              regex: true
            - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
              action: replace
              target_label: __metrics_path__
              regex: (.+)
  
  # Jaeger接收器
  jaeger:
    protocols:
      grpc:
        endpoint: 0.0.0.0:14250
      thrift_http:
        endpoint: 0.0.0.0:14268
      thrift_compact:
        endpoint: 0.0.0.0:6831
  
  # Zipkin接收器
  zipkin:
    endpoint: 0.0.0.0:9411
  
  # Kafka接收器
  kafka:
    brokers: ["kafka:9092"]
    topics: ["otel-traces", "otel-metrics", "otel-logs"]
    authentication:
      tls:
        ca_file: "/path/to/ca.pem"
        cert_file: "/path/to/cert.pem"
        key_file: "/path/to/key.pem"
  
  # 文件日志接收器
  filelog:
    include: ["/var/log/*.log"]
    start_at: beginning
    include_file_name: false
    include_file_path: true
    operators:
      - type: regex_parser
        regex: '^(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<severity>\w+) (?P<message>.*)$'
        timestamp:
          parse_from: attributes.time
          layout: '%Y-%m-%d %H:%M:%S'
        severity:
          parse_from: attributes.severity
```

### 3.2 处理器示例

```yaml
# processors-example.yaml
processors:
  # 批处理
  batch:
    timeout: 1s
    send_batch_size: 1024
    send_batch_max_size: 2048
  
  # 内存限制器
  memory_limiter:
    limit_mib: 512
    spike_limit_mib: 128
    check_interval: 5s
  
  # 资源处理器
  resource:
    attributes:
      - key: environment
        value: production
        action: upsert
      - key: service.version
        value: "1.0.0"
        action: upsert
      - key: temporary.attribute
        action: delete
  
  # 属性处理器
  attributes:
    actions:
      - key: db.user
        action: delete
      - key: sensitive.data
        action: hash
      - key: http.request.header.authorization
        action: delete
      - key: custom.attribute
        value: "default-value"
        action: upsert
      - key: regex.attribute
        action: extract_regex
        regex: "user_id=(?P<user_id>\\w+)"
  
  # 资源检测处理器
  resourcedetection:
    detectors: [env, gcp, aws]
    timeout: 10s
  
  # 指标转换处理器
  metricstransform:
    transforms:
      - include: "counter_.*"
        action: update
        new_name: "${1}_total"
        operations:
          - type: aggregate
            aggregation_type: sum
      - include: "timer_.*"
        action: update
        new_name: "${1}_seconds"
        operations:
          - type: scale
            scale: 0.001  # 毫秒转秒
  
  # 采样处理器
  probabilistic_sampler:
    sampling_percentage: 10
  
  # 过滤处理器
  filter:
    metrics:
      include:
        match_type: regexp
        metric_names: ["http_requests.*"]
        attributes:
          - key: service.name
            value: "payment-service"
  
  # 日志处理器
  logstransform:
    transforms:
      - include: ".*"
        match_type: regexp
        log_body: ".*"
        operations:
          - type: add
            field: attributes.environment
            value: "production"
          - type: move
            from: attributes.timestamp
            to: timestamp
```

### 3.3 导出器示例

```yaml
# exporters-example.yaml
exporters:
  # Prometheus导出器
  prometheus:
    endpoint: "0.0.0.0:8889"
    namespace: "otel"
    const_labels:
      environment: "production"
    send_timestamps: true
    metric_expiration: 180m
    enable_open_metrics: true
  
  # Jaeger导出器
  jaeger:
    endpoint: jaeger-all-in-one:14250
    tls:
      insecure: true
    sending_queue:
      enabled: true
      num_consumers: 10
      queue_size: 5000
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_interval: 30s
      max_elapsed_time: 300s
  
  # Zipkin导出器
  zipkin:
    endpoint: "http://zipkin:9411/api/v2/spans"
    format: json
    tls:
      insecure: true
  
  # Elasticsearch导出器
  elasticsearch:
    endpoints: ["http://elasticsearch:9200"]
    index: "otel-logs"
    mapping:
      body_key: "message"
      severity_key: "level"
    tls:
      insecure: true
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_interval: 30s
      max_elapsed_time: 300s
  
  # Kafka导出器
  kafka:
    brokers: ["kafka:9092"]
    topic: "otel-data"
    encoding: "json"
    authentication:
      tls:
        ca_file: "/path/to/ca.pem"
        cert_file: "/path/to/cert.pem"
        key_file: "/path/to/key.pem"
    timeout: 30s
    sending_queue:
      enabled: true
      num_consumers: 10
      queue_size: 5000
  
  # OTLP导出器
  otlp:
    endpoint: "http://otel-collector-backend:4317"
    tls:
      insecure: true
    sending_queue:
      enabled: true
      num_consumers: 10
      queue_size: 5000
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_interval: 30s
      max_elapsed_time: 300s
  
  # 日志导出器
  logging:
    loglevel: info
    sampling_initial: 10
    sampling_thereafter: 100
```

### 3.4 扩展器示例

```yaml
# extensions-example.yaml
extensions:
  # 健康检查扩展
  health_check:
    endpoint: 0.0.0.0:13133
    path: /health
    response_body:
      status: "server is healthy"
  
  # 性能分析扩展
  pprof:
    endpoint: 0.0.0.0:1777
  
  # 调试页面扩展
  zpages:
    endpoint: 0.0.0.0:55679
  
  # Ballast扩展
  ballast:
    size_mib: 512
  
  # 观察者扩展
  observer:
    ports:
      - 8888
      - 8889
      - 13133
  
  # 自定义扩展示例
  custom_extension:
    # 自定义扩展的配置参数
```

## 4. 实验代码

### 4.1 实验1：基本Collector部署与配置

```python
# experiment1.py
"""
实验1：基本Collector部署与配置
目标：学习如何部署和配置基本的OpenTelemetry Collector
"""

import requests
import time
import json
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

def setup_tracer():
    """设置追踪器"""
    resource = Resource.create({
        "service.name": "collector-experiment-1",
        "service.version": "1.0.0",
        "environment": "experiment"
    })
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)
    
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",
        insecure=True
    )
    
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    return tracer

def generate_traces(tracer, count=10):
    """生成追踪数据"""
    for i in range(count):
        with tracer.start_as_current_span(f"operation-{i}") as span:
            span.set_attribute("operation.id", i)
            span.set_attribute("operation.type", "experiment")
            
            # 模拟一些工作
            time.sleep(0.1)
            
            # 创建子span
            with tracer.start_as_current_span(f"sub-operation-{i}") as child_span:
                child_span.set_attribute("sub.operation.id", i)
                child_span.set_attribute("sub.operation.type", "child")
                time.sleep(0.05)

def check_collector_health():
    """检查Collector健康状态"""
    try:
        response = requests.get("http://localhost:13133/health", timeout=5)
        if response.status_code == 200:
            print("Collector健康检查通过")
            return True
        else:
            print(f"Collector健康检查失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"无法连接到Collector健康检查端点: {e}")
        return False

def check_collector_metrics():
    """检查Collector指标"""
    try:
        response = requests.get("http://localhost:8888/metrics", timeout=5)
        if response.status_code == 200:
            print("Collector指标端点可访问")
            metrics = response.text
            # 简单检查指标中是否包含Collector相关信息
            if "otelcol" in metrics:
                print("Collector指标数据正常")
                return True
            else:
                print("Collector指标数据异常")
                return False
        else:
            print(f"无法获取Collector指标，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"无法连接到Collector指标端点: {e}")
        return False

def main():
    print("=== 实验1：基本Collector部署与配置 ===")
    
    # 检查Collector健康状态
    print("\n1. 检查Collector健康状态...")
    if not check_collector_health():
        print("Collector未运行或不健康，请先启动Collector")
        return
    
    # 检查Collector指标
    print("\n2. 检查Collector指标...")
    check_collector_metrics()
    
    # 设置追踪器
    print("\n3. 设置追踪器...")
    tracer = setup_tracer()
    
    # 生成追踪数据
    print("\n4. 生成追踪数据...")
    generate_traces(tracer, count=20)
    
    # 等待数据发送
    print("\n5. 等待数据发送...")
    time.sleep(5)
    
    print("\n实验1完成！请检查Collector日志以确认数据已接收并处理。")
    print("Collector日志位置取决于您的配置，通常在Docker容器中或标准输出。")

if __name__ == "__main__":
    main()
```

### 4.2 实验2：高级Collector配置与组件

```python
# experiment2.py
"""
实验2：高级Collector配置与组件
目标：学习如何配置Collector的高级组件和功能
"""

import requests
import time
import random
import json
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.metrics import Counter, Histogram, UpDownCounter

def setup_telemetry():
    """设置遥测（追踪和指标）"""
    resource = Resource.create({
        "service.name": "collector-experiment-2",
        "service.version": "1.0.0",
        "environment": "experiment"
    })
    
    # 设置追踪
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)
    
    otlp_trace_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",
        insecure=True
    )
    
    span_processor = BatchSpanProcessor(otlp_trace_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # 设置指标
    metric_reader = PeriodicExportingMetricReader(
        exporter=OTLPMetricExporter(
            endpoint="http://localhost:4317",
            insecure=True
        ),
        export_interval_millis=30000  # 30秒导出一次
    )
    
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
    meter = metrics.get_meter(__name__)
    
    # 创建指标
    request_counter = meter.create_counter(
        "http_requests_total",
        description="Total number of HTTP requests"
    )
    
    response_histogram = meter.create_histogram(
        "http_request_duration_seconds",
        description="HTTP request duration in seconds"
    )
    
    active_connections = meter.create_up_down_counter(
        "active_connections",
        description="Number of active connections"
    )
    
    return tracer, request_counter, response_histogram, active_connections

def generate_complex_traces(tracer, request_counter, response_histogram, active_connections):
    """生成复杂的追踪和指标数据"""
    operations = ["database_query", "cache_lookup", "api_call", "file_operation"]
    statuses = ["success", "error", "timeout"]
    
    for i in range(50):
        # 模拟连接建立
        active_connections.add(1)
        
        with tracer.start_as_current_span(f"request-{i}") as span:
            span.set_attribute("http.method", random.choice(["GET", "POST", "PUT", "DELETE"]))
            span.set_attribute("http.url", f"/api/v1/resource/{i}")
            span.set_attribute("http.status_code", random.choice([200, 201, 400, 404, 500]))
            span.set_attribute("user.id", f"user-{random.randint(1, 100)}")
            
            # 记录请求指标
            request_counter.add(
                1,
                attributes={
                    "method": span.attributes["http.method"],
                    "status": str(span.attributes["http.status_code"])[0] + "xx"  # 2xx, 4xx, 5xx
                }
            )
            
            # 模拟请求处理时间
            processing_time = random.uniform(0.1, 2.0)
            time.sleep(processing_time / 10)  # 加速模拟
            
            # 记录处理时间指标
            response_histogram.record(
                processing_time,
                attributes={
                    "method": span.attributes["http.method"],
                    "status": str(span.attributes["http.status_code"])[0] + "xx"
                }
            )
            
            # 创建子操作
            for j in range(random.randint(1, 3)):
                operation = random.choice(operations)
                with tracer.start_as_current_span(f"operation-{j}") as child_span:
                    child_span.set_attribute("operation.type", operation)
                    child_span.set_attribute("operation.status", random.choice(statuses))
                    
                    # 模拟操作时间
                    operation_time = random.uniform(0.05, 0.5)
                    time.sleep(operation_time / 10)  # 加速模拟
                    
                    # 添加事件
                    child_span.add_event(
                        f"Operation {operation} completed",
                        attributes={"duration": operation_time}
                    )
            
            # 模拟连接关闭
            active_connections.add(-1)

def check_collector_components():
    """检查Collector组件状态"""
    components = {
        "健康检查": "http://localhost:13133/health",
        "指标": "http://localhost:8888/metrics",
        "调试页面": "http://localhost:55679/debug/tracez",
        "性能分析": "http://localhost:1777/debug/pprof/"
    }
    
    for name, url in components.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ {name}组件正常工作")
            else:
                print(f"✗ {name}组件异常，状态码: {response.status_code}")
        except Exception as e:
            print(f"✗ 无法访问{name}组件: {e}")

def analyze_collector_metrics():
    """分析Collector指标"""
    try:
        response = requests.get("http://localhost:8888/metrics", timeout=5)
        if response.status_code == 200:
            metrics_data = response.text
            
            # 提取一些关键指标
            lines = metrics_data.split('\n')
            for line in lines:
                if 'otelcol_processor_accepted_spans' in line:
                    print(f"接受的Span数量: {line.split()[1]}")
                elif 'otelcol_processor_dropped_spans' in line:
                    print(f"丢弃的Span数量: {line.split()[1]}")
                elif 'otelcol_exporter_sent_spans' in line:
                    print(f"发送的Span数量: {line.split()[1]}")
                elif 'otelcol_exporter_failed_spans' in line:
                    print(f"发送失败的Span数量: {line.split()[1]}")
                
    except Exception as e:
        print(f"无法分析Collector指标: {e}")

def main():
    print("=== 实验2：高级Collector配置与组件 ===")
    
    # 检查Collector组件
    print("\n1. 检查Collector组件状态...")
    check_collector_components()
    
    # 设置遥测
    print("\n2. 设置遥测（追踪和指标）...")
    tracer, request_counter, response_histogram, active_connections = setup_telemetry()
    
    # 生成复杂的追踪和指标数据
    print("\n3. 生成复杂的追踪和指标数据...")
    generate_complex_traces(tracer, request_counter, response_histogram, active_connections)
    
    # 等待数据发送
    print("\n4. 等待数据发送...")
    time.sleep(10)
    
    # 分析Collector指标
    print("\n5. 分析Collector指标...")
    analyze_collector_metrics()
    
    print("\n实验2完成！请检查以下位置以验证结果：")
    print("- Jaeger UI: http://localhost:16686")
    print("- Prometheus UI: http://localhost:9090")
    print("- Collector调试页面: http://localhost:55679/debug/tracez")

if __name__ == "__main__":
    main()
```

### 4.3 实验3：Collector性能优化

```python
# experiment3.py
"""
实验3：Collector性能优化
目标：学习如何优化OpenTelemetry Collector的性能
"""

import requests
import time
import threading
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

def setup_telemetry():
    """设置遥测（追踪和指标）"""
    resource = Resource.create({
        "service.name": "collector-experiment-3",
        "service.version": "1.0.0",
        "environment": "experiment"
    })
    
    # 设置追踪
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)
    
    otlp_trace_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",
        insecure=True
    )
    
    # 使用较大的批处理大小和较短的超时来优化性能
    span_processor = BatchSpanProcessor(
        otlp_trace_exporter,
        max_export_batch_size=2048,
        max_queue_size=2048,
        export_timeout_millis=30000,
        schedule_delay_millis=5000
    )
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # 设置指标
    metric_reader = PeriodicExportingMetricReader(
        exporter=OTLPMetricExporter(
            endpoint="http://localhost:4317",
            insecure=True
        ),
        export_interval_millis=15000  # 15秒导出一次，更频繁
    )
    
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
    meter = metrics.get_meter(__name__)
    
    # 创建指标
    request_counter = meter.create_counter(
        "http_requests_total",
        description="Total number of HTTP requests"
    )
    
    response_histogram = meter.create_histogram(
        "http_request_duration_seconds",
        description="HTTP request duration in seconds"
    )
    
    return tracer, request_counter, response_histogram

def generate_high_volume_traces(tracer, request_counter, response_histogram, thread_id, span_count):
    """生成高容量的追踪数据"""
    for i in range(span_count):
        with tracer.start_as_current_span(f"request-{thread_id}-{i}") as span:
            span.set_attribute("http.method", random.choice(["GET", "POST", "PUT", "DELETE"]))
            span.set_attribute("http.url", f"/api/v1/resource/{i}")
            span.set_attribute("http.status_code", random.choice([200, 201, 400, 404, 500]))
            span.set_attribute("thread.id", thread_id)
            
            # 记录请求指标
            request_counter.add(
                1,
                attributes={
                    "method": span.attributes["http.method"],
                    "status": str(span.attributes["http.status_code"])[0] + "xx",
                    "thread_id": str(thread_id)
                }
            )
            
            # 模拟请求处理时间
            processing_time = random.uniform(0.01, 0.1)
            time.sleep(processing_time / 100)  # 加速模拟
            
            # 记录处理时间指标
            response_histogram.record(
                processing_time,
                attributes={
                    "method": span.attributes["http.method"],
                    "status": str(span.attributes["http.status_code"])[0] + "xx",
                    "thread_id": str(thread_id)
                }
            )
            
            # 创建多个子span以增加复杂度
            for j in range(random.randint(1, 5)):
                with tracer.start_as_current_span(f"sub-operation-{j}") as child_span:
                    child_span.set_attribute("operation.type", random.choice(["db_query", "cache_lookup", "api_call"]))
                    child_span.set_attribute("operation.duration", random.uniform(0.001, 0.01))

def benchmark_collector_performance():
    """基准测试Collector性能"""
    tracer, request_counter, response_histogram = setup_telemetry()
    
    # 记录开始时间
    start_time = time.time()
    
    # 使用多线程生成高容量数据
    thread_count = 10
    spans_per_thread = 100
    
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = []
        for thread_id in range(thread_count):
            futures.append(
                executor.submit(
                    generate_high_volume_traces,
                    tracer,
                    request_counter,
                    response_histogram,
                    thread_id,
                    spans_per_thread
                )
            )
        
        # 等待所有线程完成
        for future in as_completed(futures):
            future.result()
    
    # 记录结束时间
    end_time = time.time()
    total_spans = thread_count * spans_per_thread
    duration = end_time - start_time
    
    print(f"生成 {total_spans} 个span耗时: {duration:.2f} 秒")
    print(f"平均每秒生成 {total_spans / duration:.2f} 个span")
    
    return total_spans, duration

def analyze_collector_performance_metrics():
    """分析Collector性能指标"""
    try:
        response = requests.get("http://localhost:8888/metrics", timeout=5)
        if response.status_code == 200:
            metrics_data = response.text
            
            # 提取性能相关指标
            lines = metrics_data.split('\n')
            performance_metrics = {}
            
            for line in lines:
                if 'otelcol_processor_accepted_spans' in line and not line.startswith('#'):
                    performance_metrics['accepted_spans'] = int(line.split()[1])
                elif 'otelcol_processor_dropped_spans' in line and not line.startswith('#'):
                    performance_metrics['dropped_spans'] = int(line.split()[1])
                elif 'otelcol_exporter_queue_size' in line and not line.startswith('#'):
                    performance_metrics['exporter_queue_size'] = int(line.split()[1])
                elif 'otelcol_processor_queue_size' in line and not line.startswith('#'):
                    performance_metrics['processor_queue_size'] = int(line.split()[1])
                elif 'process_cpu_seconds_total' in line and not line.startswith('#'):
                    performance_metrics['cpu_seconds'] = float(line.split()[1])
                elif 'process_resident_memory_bytes' in line and not line.startswith('#'):
                    performance_metrics['memory_bytes'] = int(line.split()[1])
            
            # 计算性能指标
            if 'accepted_spans' in performance_metrics and 'dropped_spans' in performance_metrics:
                total_spans = performance_metrics['accepted_spans'] + performance_metrics['dropped_spans']
                if total_spans > 0:
                    drop_rate = (performance_metrics['dropped_spans'] / total_spans) * 100
                    print(f"Span丢弃率: {drop_rate:.2f}%")
            
            if 'memory_bytes' in performance_metrics:
                memory_mb = performance_metrics['memory_bytes'] / (1024 * 1024)
                print(f"内存使用: {memory_mb:.2f} MB")
            
            if 'exporter_queue_size' in performance_metrics:
                print(f"导出器队列大小: {performance_metrics['exporter_queue_size']}")
            
            if 'processor_queue_size' in performance_metrics:
                print(f"处理器队列大小: {performance_metrics['processor_queue_size']}")
                
            return performance_metrics
        
    except Exception as e:
        print(f"无法分析Collector性能指标: {e}")
        return None

def test_collector_load():
    """测试Collector负载"""
    print("开始负载测试...")
    
    # 基准测试
    print("\n1. 基准测试...")
    total_spans, duration = benchmark_collector_performance()
    
    # 等待数据发送
    print("\n2. 等待数据发送...")
    time.sleep(10)
    
    # 分析性能指标
    print("\n3. 分析性能指标...")
    metrics = analyze_collector_performance_metrics()
    
    # 建议优化
    print("\n4. 优化建议...")
    if metrics:
        if 'memory_bytes' in metrics and metrics['memory_bytes'] > 500 * 1024 * 1024:  # 500MB
            print("- 内存使用较高，考虑增加批处理大小或减少并发连接")
        
        if 'exporter_queue_size' in metrics and metrics['exporter_queue_size'] > 1000:
            print("- 导出器队列积压较多，考虑增加导出器并发数或优化导出器配置")
        
        if 'processor_queue_size' in metrics and metrics['processor_queue_size'] > 1000:
            print("- 处理器队列积压较多，考虑增加处理器并发数或优化处理器配置")
    
    print("\n负载测试完成！")

def main():
    print("=== 实验3：Collector性能优化 ===")
    
    # 检查Collector状态
    print("\n1. 检查Collector状态...")
    try:
        response = requests.get("http://localhost:13133/health", timeout=5)
        if response.status_code == 200:
            print("Collector健康检查通过")
        else:
            print(f"Collector健康检查失败，状态码: {response.status_code}")
            return
    except Exception as e:
        print(f"无法连接到Collector: {e}")
        return
    
    # 负载测试
    print("\n2. 负载测试...")
    test_collector_load()
    
    print("\n实验3完成！请检查以下位置以验证结果：")
    print("- Jaeger UI: http://localhost:16686")
    print("- Prometheus UI: http://localhost:9090")
    print("- Collector指标: http://localhost:8888/metrics")

if __name__ == "__main__":
    main()
```

## 5. 运行指南

### 5.1 环境准备

1. 安装Docker和Docker Compose
2. 安装Python 3.7+
3. 安装必要的Python依赖：
   ```bash
   pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation-requests requests
   ```

### 5.2 启动Collector

1. 基本部署：
   ```bash
   docker-compose -f docker-compose-basic.yaml up -d
   ```

2. 完整部署：
   ```bash
   docker-compose -f docker-compose-full.yaml up -d
   ```

### 5.3 运行实验

1. 实验1：基本Collector部署与配置
   ```bash
   python experiment1.py
   ```

2. 实验2：高级Collector配置与组件
   ```bash
   python experiment2.py
   ```

3. 实验3：Collector性能优化
   ```bash
   python experiment3.py
   ```

### 5.4 验证结果

1. 检查Collector健康状态：
   ```bash
   curl http://localhost:13133/health
   ```

2. 查看Collector指标：
   ```bash
   curl http://localhost:8888/metrics
   ```

3. 访问Jaeger UI：
   ```
   http://localhost:16686
   ```

4. 访问Prometheus UI：
   ```
   http://localhost:9090
   ```

5. 访问Collector调试页面：
   ```
   http://localhost:55679/debug/tracez
   ```

### 5.5 停止Collector

```bash
docker-compose -f docker-compose-basic.yaml down
# 或
docker-compose -f docker-compose-full.yaml down
```

## 6. 故障排除

### 6.1 常见问题

1. Collector无法启动
   - 检查配置文件语法
   - 确认端口未被占用
   - 查看Docker日志

2. 数据未发送到后端
   - 检查导出器配置
   - 确认网络连接
   - 查看Collector日志

3. 性能问题
   - 调整批处理大小
   - 优化采样策略
   - 增加资源限制

### 6.2 调试命令

1. 查看Collector日志：
   ```bash
   docker-compose logs otel-collector
   ```

2. 检查Collector配置：
   ```bash
   docker exec otel-collector otelcol validate /etc/otel-collector-config.yaml
   ```

3. 查看Collector状态：
   ```bash
   curl http://localhost:13133/health
   ```