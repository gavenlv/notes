# 第5章代码示例：Gunicorn监控与日志管理

本章包含用于演示Gunicorn监控与日志管理的代码示例，包括监控应用和日志分析工具。

## 文件说明

- `monitoring_app.py` - 用于演示监控功能的Flask应用
- `log_analyzer.py` - Gunicorn日志分析工具
- `requirements.txt` - 项目依赖列表

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行监控应用

```bash
# 启动应用
gunicorn -w 4 -k sync monitoring_app:application

# 访问监控端点
curl http://localhost:8000/metrics
curl http://localhost:8000/health
curl http://localhost:8000/prometheus-metrics
```

### 分析日志

```bash
# 分析Gunicorn访问日志
python log_analyzer.py /var/log/gunicorn/access.log

# 分析最近1000条日志并保存到文件
python log_analyzer.py /var/log/gunicorn/access.log --max-lines 1000 --output report.json
```

## 监控端点

- `/` - 基本响应端点
- `/metrics` - 提供JSON格式的性能指标
- `/health` - 健康检查端点，返回系统状态
- `/logs` - 模拟日志端点（仅用于演示）
- `/slow-request` - 模拟慢请求，用于测试监控
- `/error` - 模拟错误，用于测试错误监控
- `/prometheus-metrics` - 提供Prometheus格式的指标

## 日志分析功能

日志分析工具提供以下分析功能：

1. **状态码分布**：分析不同HTTP状态码的分布
2. **响应时间分析**：计算平均、最小、最大、百分位数等
3. **热门路径**：找出访问最频繁的路径
4. **IP统计**：统计访问最频繁的IP地址
5. **时间段分析**：分析不同时间段的请求分布
6. **User-Agent分析**：分析客户端类型分布
7. **慢请求识别**：找出响应时间超过阈值的请求

## 监控指标

### 应用指标

- **请求计数**：总请求数
- **错误计数**：总错误数
- **错误率**：错误请求百分比
- **平均响应时间**：所有请求的平均响应时间
- **P95响应时间**：95%请求的响应时间

### 系统指标

- **CPU使用率**：当前CPU使用百分比
- **内存使用率**：当前内存使用百分比
- **可用内存**：系统可用内存量
- **磁盘使用率**：磁盘使用百分比

### 进程指标

- **进程ID**：Gunicorn主进程ID
- **内存使用**：进程内存使用量（RSS、VMS）

## 集成监控系统

### Prometheus集成

使用`/prometheus-metrics`端点可以轻松集成Prometheus：

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'gunicorn'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/prometheus-metrics'
```

### Grafana仪表板

在Grafana中创建仪表板，可视化以下指标：

- 请求率趋势图
- 错误率趋势图
- 响应时间分布图
- 系统资源使用图

## 告警设置

### 告警规则示例

```yaml
# prometheus_alerts.yml
groups:
  - name: gunicorn_alerts
    rules:
      - alert: HighErrorRate
        expr: (gunicorn_errors_total / gunicorn_requests_total) * 100 > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Gunicorn error rate is {{ $value }}%"
      
      - alert: HighResponseTime
        expr: gunicorn_request_duration_seconds > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "Average response time is {{ $value }}s"
      
      - alert: HighCpuUsage
        expr: gunicorn_cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "Gunicorn CPU usage is {{ $value }}%"
      
      - alert: HighMemoryUsage
        expr: gunicorn_memory_usage_bytes / (1024 * 1024 * 1024) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Gunicorn memory usage is {{ $value }}GB"
```

## 高级监控技巧

### 自定义指标

在应用中添加自定义指标：

```python
# 在监控应用中添加
from prometheus_client import Counter, Histogram, Gauge

# 定义指标
REQUEST_COUNT = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('app_active_connections', 'Active connections')

# 在请求处理中使用
@app.route('/custom-endpoint')
def custom_endpoint():
    REQUEST_COUNT.labels(method='GET', endpoint='/custom-endpoint').inc()
    
    start_time = time.time()
    # 处理请求
    result = process_request()
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return jsonify(result)
```

### 分布式追踪

使用OpenTelemetry实现分布式追踪：

```python
# 安装依赖
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-flask

# 在应用中添加
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# 配置追踪
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# 在请求处理中使用
@app.route('/traced-endpoint')
def traced_endpoint():
    with tracer.start_as_current_span("traced_operation"):
        # 业务逻辑
        result = expensive_operation()
        return jsonify(result)
```

## 日志管理最佳实践

1. **结构化日志**：使用JSON格式的日志，便于分析
2. **日志轮转**：配置logrotate，防止日志文件过大
3. **集中日志**：使用ELK Stack或类似工具集中管理日志
4. **敏感信息**：确保不记录敏感信息（密码、令牌等）
5. **日志级别**：合理设置日志级别，平衡详细度和性能

## 故障排除

1. **指标缺失**：检查监控应用是否正常运行
2. **日志解析错误**：确认日志格式与解析器匹配
3. **性能影响**：监控本身不应显著影响应用性能
4. **告警风暴**：设置合理的告警阈值和抑制规则