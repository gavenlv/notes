# 第3章：OpenTelemetry Instrumentation与SDK

## 3.1 Instrumentation概述

### 3.1.1 什么是Instrumentation

Instrumentation（仪器化）是指在应用程序代码中添加可观测性功能的过程，以便收集、生成和导出遥测数据（追踪、指标和日志）。在OpenTelemetry中，Instrumentation是连接应用程序与可观测性系统的桥梁。

### 3.1.2 Instrumentation的类型

OpenTelemetry支持两种主要的Instrumentation类型：

1. **自动Instrumentation（Auto-Instrumentation）**
   - 无需修改应用程序代码
   - 通过库或代理自动拦截和检测函数调用
   - 适用于常见框架和库（如HTTP服务器、数据库客户端等）
   - 启动快速，配置简单

2. **手动Instrumentation（Manual Instrumentation）**
   - 需要修改应用程序代码
   - 使用OpenTelemetry API直接添加追踪、指标和日志
   - 提供更精细的控制和自定义
   - 适用于业务逻辑和自定义组件

### 3.1.3 Instrumentation的选择指南

| 场景 | 推荐的Instrumentation类型 |
|------|---------------------------|
| 标准Web框架（如Flask、Django、Express） | 自动Instrumentation |
| 数据库客户端（如SQLAlchemy、MongoDB） | 自动Instrumentation |
| 业务逻辑和自定义功能 | 手动Instrumentation |
| 性能关键路径 | 手动Instrumentation（优化性能） |
| 快速原型和开发 | 自动Instrumentation |

## 3.2 OpenTelemetry SDK详解

### 3.2.1 SDK架构

OpenTelemetry SDK（软件开发工具包）是OpenTelemetry的核心实现，负责：

1. **数据生成**：创建和管理追踪、指标和日志
2. **数据处理**：采样、过滤、聚合和转换数据
3. **数据导出**：将遥测数据发送到后端系统
4. **配置管理**：管理资源、采样策略和导出器

### 3.2.2 核心组件

#### 1. TracerProvider（追踪提供者）

TracerProvider是追踪的入口点，负责创建Tracer实例。

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# 创建资源
resource = Resource(attributes={
    SERVICE_NAME: "my-service"
})

# 创建TracerProvider
trace.set_tracer_provider(TracerProvider(resource=resource))

# 获取Tracer
tracer = trace.get_tracer(__name__)
```

#### 2. MeterProvider（指标提供者）

MeterProvider是指标的入口点，负责创建Meter实例。

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.prometheus import PrometheusMetricReader

# 创建资源
resource = Resource(attributes={
    SERVICE_NAME: "my-service"
})

# 创建指标读取器
reader = PrometheusMetricReader(port=9090)

# 创建MeterProvider
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))

# 获取Meter
meter = metrics.get_meter(__name__)
```

#### 3. LoggerProvider（日志提供者）

LoggerProvider是日志的入口点，负责创建Logger实例。

```python
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# 创建LoggerProvider
logger_provider = LoggerProvider()
_logs.set_logger_provider(logger_provider)

# 添加导出器
exporter = OTLPLogExporter(endpoint="http://localhost:4317", insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

# 获取Logger
logger = logger_provider.get_logger(__name__)
```

### 3.2.3 资源（Resource）

资源是描述生成遥测数据的实体的一组属性，通常包括服务名称、版本、环境等信息。

```python
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT, Resource

# 创建资源
resource = Resource(attributes={
    SERVICE_NAME: "my-service",
    SERVICE_VERSION: "1.0.0",
    DEPLOYMENT_ENVIRONMENT: "production",
    "service.instance.id": "instance-1",
    "host.name": "host-1"
})
```

### 3.2.4 上下文（Context）

上下文是OpenTelemetry中用于在分布式系统中传递信息的机制，包括追踪上下文、 baggage等。

```python
from opentelemetry import context
from opentelemetry.trace import set_span_in_context

# 获取当前上下文
current_context = context.get_current()

# 创建新上下文
new_context = set_span_in_context(span)

# 使用上下文
token = context.attach(new_context)
try:
    # 在新上下文中执行代码
    pass
finally:
    context.detach(token)
```

## 3.3 自动Instrumentation

### 3.3.1 自动Instrumentation原理

自动Instrumentation通过以下方式工作：

1. **字节码增强**：在运行时修改应用程序字节码
2. **包装器/代理**：替换原始库函数为包装版本
3. **钩子函数**：在关键函数执行前后插入代码

### 3.3.2 常见自动Instrumentation库

#### Python自动Instrumentation

```bash
# 安装自动Instrumentation库
pip install opentelemetry-instrumentation-requests
pip install opentelemetry-instrumentation-flask
pip install opentelemetry-instrumentation-sqlalchemy
pip install opentelemetry-instrumentation-redis
pip install opentelemetry-instrumentation-mysql
pip install opentelemetry-instrumentation-psycopg2
pip install opentelemetry-instrumentation-urllib3
pip install opentelemetry-instrumentation-httpx
pip install opentelemetry-instrumentation-aiohttp-client
pip install opentelemetry-instrumentation-aiohttp-server
pip install opentelemetry-instrumentation-asgi
pip install opentelemetry-instrumentation-wsgi
pip install opentelemetry-instrumentation-grpc
pip install opentelemetry-instrumentation-jinja2
pip install opentelemetry-instrumentation-logging
pip install opentelemetry-instrumentation-redis
pip install opentelemetry-instrumentation-mysql
pip install opentelemetry-instrumentation-psycopg2
pip install opentelemetry-instrumentation-sqlalchemy
pip install opentelemetry-instrumentation-urllib3
pip install opentelemetry-instrumentation-aws-lambda
pip install opentelemetry-instrumentation-botocore
pip install opentelemetry-instrumentation-boto3sqs
pip install opentelemetry-instrumentation-django
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-instrumentation-starlette
pip install opentelemetry-instrumentation-celery
pip install opentelemetry-instrumentation-kafka-python
pip install opentelemetry-instrumentation-pymemcache
pip install opentelemetry-instrumentation-pymongo
pip install opentelemetry-instrumentation-pymysql
pip install opentelemetry-instrumentation-pyramid
pip install opentelemetry-instrumentation-sqlite3
pip install opentelemetry-instrumentation-tornado
pip install opentelemetry-instrumentation-urllib
```

#### 使用自动Instrumentation

```python
# 方法1：使用opentelemetry-instrument命令
# opentelemetry-instrument -f -l http://localhost:4318 python your_app.py

# 方法2：在代码中初始化
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.auto_instrumentation import sitecustomize
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "my-service"
})

# 设置追踪
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置导出器
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4318")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 自动instrumentation
RequestsInstrumentor().instrument()
FlaskInstrumentor().instrument()

# 你的应用代码
import requests
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    response = requests.get("https://example.com")
    return f"Hello, World! Response status: {response.status_code}"

if __name__ == "__main__":
    app.run()
```

### 3.3.3 Java自动Instrumentation

Java自动Instrumentation通过Java Agent实现：

```bash
# 下载Java Agent
wget https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar

# 使用Java Agent运行应用
java -javaagent:opentelemetry-javaagent.jar \
     -Dotel.service.name=my-service \
     -Dotel.exporter.otlp.endpoint=http://localhost:4317 \
     -jar your-application.jar
```

### 3.3.4 JavaScript自动Instrumentation

```bash
# 安装自动Instrumentation库
npm install @opentelemetry/auto-instrumentations-node
```

```javascript
// 使用自动Instrumentation
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

// 初始化SDK
const sdk = new NodeSDK({
  instrumentations: [getNodeAutoInstrumentations()],
  serviceName: 'my-service',
});

// 启动SDK
sdk.start();

// 你的应用代码
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello, World!');
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
```

## 3.4 手动Instrumentation

### 3.4.1 手动追踪Instrumentation

#### 基本追踪

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "manual-tracing-demo"
})

# 设置追踪
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# 添加span处理器
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def process_data(data_id):
    with tracer.start_as_current_span("process-data") as span:
        # 设置属性
        span.set_attribute("data.id", data_id)
        span.set_attribute("operation.type", "processing")
        
        # 添加事件
        span.add_event("Starting data processing")
        
        # 模拟处理
        time.sleep(0.5)
        
        # 添加事件
        span.add_event("Data processing completed")
        
        return {"status": "success", "data_id": data_id}

if __name__ == "__main__":
    result = process_data("data-123")
    print(f"Result: {result}")
    
    # 等待span被导出
    time.sleep(2)
```

#### 嵌套追踪

```python
def parent_operation():
    with tracer.start_as_current_span("parent-operation") as parent_span:
        parent_span.set_attribute("operation.type", "parent")
        
        # 调用子操作
        child_operation_1()
        child_operation_2()
        
        # 设置状态
        parent_span.set_status(trace.Status(trace.StatusCode.OK))

def child_operation_1():
    with tracer.start_as_current_span("child-operation-1") as child_span:
        child_span.set_attribute("operation.type", "child")
        child_span.set_attribute("operation.id", "1")
        
        # 模拟工作
        time.sleep(0.3)
        
        # 设置状态
        child_span.set_status(trace.Status(trace.StatusCode.OK))

def child_operation_2():
    with tracer.start_as_current_span("child-operation-2") as child_span:
        child_span.set_attribute("operation.type", "child")
        child_span.set_attribute("operation.id", "2")
        
        # 模拟错误
        try:
            # 模拟错误
            raise ValueError("Simulated error")
        except Exception as e:
            # 记录异常
            child_span.record_exception(e)
            
            # 设置错误状态
            child_span.set_status(
                trace.Status(
                    trace.StatusCode.ERROR,
                    description=str(e)
                )
            )

if __name__ == "__main__":
    parent_operation()
    
    # 等待span被导出
    time.sleep(2)
```

### 3.4.2 手动指标Instrumentation

#### 计数器（Counter）

```python
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import time

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "manual-metrics-demo"
})

# 设置指标
reader = PrometheusMetricReader(port=9090)
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

# 获取meter
meter = metrics.get_meter(__name__)

# 创建计数器
request_counter = meter.create_counter(
    "requests_total",
    description="Total number of requests"
)

def process_request(endpoint, status_code):
    # 记录指标
    request_counter.add(1, {"endpoint": endpoint, "status_code": str(status_code)})
    
    return {"endpoint": endpoint, "status_code": status_code}

if __name__ == "__main__":
    # 模拟处理请求
    for i in range(10):
        endpoint = "/api/users" if i % 2 == 0 else "/api/products"
        status_code = 200 if i % 3 != 0 else 500
        
        result = process_request(endpoint, status_code)
        print(f"Processed request: {result}")
        
        time.sleep(0.5)
    
    print("Keep the process running to view metrics at http://localhost:9090")
    while True:
        time.sleep(1)
```

#### 仪表（Gauge）

```python
import psutil

# 创建仪表
memory_usage_gauge = meter.create_observable_gauge(
    "memory_usage_bytes",
    description="Current memory usage in bytes",
    callbacks=[lambda options: (psutil.virtual_memory().used, {})]
)

# 创建UpDownCounter
active_connections_gauge = meter.create_up_down_counter(
    "active_connections",
    description="Current number of active connections"
)

def simulate_connections():
    # 增加活跃连接
    active_connections_gauge.add(1)
    
    # 模拟连接活动
    time.sleep(1)
    
    # 减少活跃连接
    active_connections_gauge.add(-1)

if __name__ == "__main__":
    print("Keep the process running to view metrics at http://localhost:9090")
    
    while True:
        simulate_connections()
        time.sleep(0.5)
```

#### 直方图（Histogram）

```python
# 创建直方图
response_time_histogram = meter.create_histogram(
    "response_time_seconds",
    description="Response time in seconds"
)

def process_request():
    # 记录开始时间
    start_time = time.time()
    
    # 模拟处理
    processing_time = random.uniform(0.1, 1.0)
    time.sleep(processing_time)
    
    # 记录响应时间
    response_time_histogram.record(processing_time)
    
    return processing_time

if __name__ == "__main__":
    import random
    
    print("Keep the process running to view metrics at http://localhost:9090")
    
    while True:
        processing_time = process_request()
        print(f"Request processed in {processing_time:.3f}s")
```

### 3.4.3 手动日志Instrumentation

```python
import logging
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "manual-logging-demo"
})

# 创建LoggerProvider
logger_provider = LoggerProvider(resource=resource)
_logs.set_logger_provider(logger_provider)

# 添加导出器
exporter = OTLPLogExporter(endpoint="http://localhost:4317", insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

# 获取Logger
logger = logger_provider.get_logger(__name__)

def process_data(data_id):
    # 记录日志
    logger.emit(
        log_record=_logs.LogRecord(
            timestamp=int(time.time() * 1e9),
            severity_number=_logs.SeverityNumber.INFO,
            severity_text="INFO",
            body=f"Processing data {data_id}",
            attributes={"data.id": data_id, "operation.type": "processing"}
        )
    )
    
    # 模拟处理
    time.sleep(0.5)
    
    # 记录日志
    logger.emit(
        log_record=_logs.LogRecord(
            timestamp=int(time.time() * 1e9),
            severity_number=_logs.SeverityNumber.INFO,
            severity_text="INFO",
            body=f"Completed processing data {data_id}",
            attributes={"data.id": data_id, "operation.type": "processing"}
        )
    )

if __name__ == "__main__":
    process_data("data-123")
    
    # 等待日志被导出
    time.sleep(2)
```

## 3.5 上下文传播

### 3.5.1 上下文传播概述

上下文传播是指在分布式系统中，将追踪上下文从一个服务传递到另一个服务的过程。这使得可以将不同服务中的span关联到同一个trace中。

### 3.5.2 上下文传播机制

OpenTelemetry使用以下机制进行上下文传播：

1. **HTTP头传播**：通过HTTP头传递追踪上下文
2. **RPC元数据传播**：通过RPC元数据传递追踪上下文
3. **消息队列传播**：通过消息属性传递追踪上下文

### 3.5.3 上下文传播示例

#### HTTP客户端传播

```python
import requests
from opentelemetry import trace
from opentelemetry.propagate import inject

def make_http_request(url):
    # 创建span
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("http-request") as span:
        span.set_attribute("http.url", url)
        
        # 注入上下文到HTTP头
        headers = {}
        inject(headers)
        
        # 发送请求
        response = requests.get(url, headers=headers)
        
        # 设置属性
        span.set_attribute("http.status_code", response.status_code)
        
        return response

if __name__ == "__main__":
    response = make_http_request("https://example.com")
    print(f"Response status: {response.status_code}")
```

#### HTTP服务器传播

```python
from flask import Flask, request
from opentelemetry import trace
from opentelemetry.propagate import extract

app = Flask(__name__)

@app.route("/")
def hello():
    # 提取上下文
    tracer = trace.get_tracer(__name__)
    
    headers = dict(request.headers)
    ctx = extract(headers)
    
    with tracer.start_as_current_span("http-server", context=ctx) as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", request.url)
        
        # 处理请求
        return "Hello, World!"

if __name__ == "__main__":
    app.run()
```

#### 手动上下文传播

```python
from opentelemetry import trace, context
from opentelemetry.trace import set_span_in_context

def process_with_context(data):
    # 获取当前上下文
    current_context = context.get_current()
    
    # 在新线程中使用上下文
    def worker():
        # 附加上下文
        token = context.attach(current_context)
        
        try:
            # 在上下文中创建span
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span("worker-operation"):
                # 处理数据
                print(f"Processing data: {data}")
        finally:
            # 分离上下文
            context.detach(token)
    
    # 启动线程
    import threading
    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

if __name__ == "__main__":
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("parent-operation"):
        process_with_context("test-data")
```

## 3.6 采样策略

### 3.6.1 采样概述

采样是决定是否记录和导出span的过程。采样可以减少数据量，降低性能开销，同时保持有意义的追踪数据。

### 3.6.2 采样器类型

OpenTelemetry提供多种采样器：

1. **AlwaysOnSampler**：总是采样
2. **AlwaysOffSampler**：从不采样
3. **TraceIdRatioBasedSampler**：基于比例采样
4. **ParentBasedSampler**：基于父span的采样决策

### 3.6.3 采样器配置示例

#### 基于比例的采样

```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# 创建资源
resource = Resource(attributes={
    SERVICE_NAME: "sampling-demo"
})

# 创建采样器（采样率为25%）
sampler = TraceIdRatioBased(0.25)

# 创建TracerProvider并设置采样器
tracer_provider = TracerProvider(resource=resource, sampler=sampler)
trace.set_tracer_provider(tracer_provider)

# 获取Tracer
tracer = trace.get_tracer(__name__)

# 创建span
with tracer.start_as_current_span("sampled-operation"):
    print("This span may or may not be sampled, depending on the sampling decision")
```

#### 基于父span的采样

```python
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased, ALWAYS_ON

# 创建父采样器
parent_sampler = ParentBased(
    root=TraceIdRatioBased(0.1),  # 根span使用10%采样率
    remote_parent_sampled=ALWAYS_ON,  # 远程采样的父span总是采样
    remote_parent_not_sampled=ALWAYS_ON,  # 远程未采样的父span总是采样
    local_parent_sampled=ALWAYS_ON,  # 本地采样的父span总是采样
    local_parent_not_sampled=ALWAYS_ON,  # 本地未采样的父span总是采样
)

# 创建TracerProvider并设置采样器
tracer_provider = TracerProvider(resource=resource, sampler=parent_sampler)
trace.set_tracer_provider(tracer_provider)

# 获取Tracer
tracer = trace.get_tracer(__name__)

# 创建span
with tracer.start_as_current_span("parent-operation"):
    with tracer.start_as_current_span("child-operation"):
        print("These spans follow the parent-based sampling policy")
```

#### 自定义采样器

```python
from opentelemetry.sdk.trace.sampling import Sampler, SamplingResult, Decision
from opentelemetry.context import Context
from opentelemetry.trace import SpanKind

class CustomSampler(Sampler):
    def __init__(self):
        pass
    
    def should_sample(
        self,
        parent_context: Context,
        trace_id: int,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: dict = None,
        links: list = None,
    ) -> SamplingResult:
        # 自定义采样逻辑
        # 例如，只采样包含特定属性的span
        if attributes and "important" in attributes and attributes["important"]:
            return SamplingResult(decision=Decision.RECORD_AND_SAMPLE)
        
        # 或者，只采样特定名称的span
        if "critical" in name:
            return SamplingResult(decision=Decision.RECORD_AND_SAMPLE)
        
        # 默认不采样
        return SamplingResult(decision=Decision.DROP)
    
    def get_description(self) -> str:
        return "CustomSampler"

# 创建自定义采样器
custom_sampler = CustomSampler()

# 创建TracerProvider并设置采样器
tracer_provider = TracerProvider(resource=resource, sampler=custom_sampler)
trace.set_tracer_provider(tracer_provider)

# 获取Tracer
tracer = trace.get_tracer(__name__)

# 创建span
with tracer.start_as_current_span("normal-operation"):
    print("This span will not be sampled")

with tracer.start_as_current_span("critical-operation"):
    print("This span will be sampled because it contains 'critical' in the name")

with tracer.start_as_current_span("important-operation", attributes={"important": True}):
    print("This span will be sampled because it has the 'important' attribute")
```

## 3.7 性能优化

### 3.7.1 批处理

批处理是将多个span或指标记录组合在一起，然后一次性导出，以减少网络开销。

```python
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# 创建导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# 创建批处理器
batch_span_processor = BatchSpanProcessor(
    jaeger_exporter,
    max_queue_size=2048,  # 最大队列大小
    max_export_batch_size=512,  # 最大批处理大小
    export_timeout_millis=30000,  # 导出超时时间（毫秒）
)

# 添加批处理器
trace.get_tracer_provider().add_span_processor(batch_span_processor)

# 对于日志
log_exporter = OTLPLogExporter(endpoint="http://localhost:4317", insecure=True)
batch_log_processor = BatchLogRecordProcessor(
    log_exporter,
    max_queue_size=2048,
    max_export_batch_size=512,
    export_timeout_millis=30000,
)

logger_provider.add_log_record_processor(batch_log_processor)
```

### 3.7.2 异步导出

异步导出可以在不阻塞应用程序线程的情况下导出遥测数据。

```python
from concurrent.futures import ThreadPoolExecutor

# 创建线程池
executor = ThreadPoolExecutor(max_workers=2)

# 创建异步导出器
async_span_processor = BatchSpanProcessor(
    jaeger_exporter,
    max_export_batch_size=512,
    export_timeout_millis=30000,
    executor=executor,  # 使用线程池执行导出
)

# 添加异步处理器
trace.get_tracer_provider().add_span_processor(async_span_processor)
```

### 3.7.3 采样优化

通过调整采样率来减少数据量和性能开销。

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# 在生产环境中使用较低的采样率
production_sampler = TraceIdRatioBased(0.01)  # 1%采样率

# 在开发环境中使用较高的采样率
development_sampler = TraceIdRatioBased(1.0)  # 100%采样率

# 根据环境选择采样器
import os
environment = os.getenv("ENVIRONMENT", "development")

if environment == "production":
    sampler = production_sampler
else:
    sampler = development_sampler

tracer_provider = TracerProvider(resource=resource, sampler=sampler)
trace.set_tracer_provider(tracer_provider)
```

### 3.7.4 属性过滤

过滤不必要的属性，减少数据量和存储成本。

```python
class AttributeFilter:
    def __init__(self, allowed_attributes):
        self.allowed_attributes = allowed_attributes
    
    def filter_attributes(self, attributes):
        """过滤属性，只保留允许的属性"""
        if not attributes:
            return {}
        
        return {
            key: value
            for key, value in attributes.items()
            if key in self.allowed_attributes
        }

# 创建属性过滤器
allowed_attributes = [
    "http.method",
    "http.url",
    "http.status_code",
    "user.id",
    "operation.type"
]

attribute_filter = AttributeFilter(allowed_attributes)

# 在创建span时过滤属性
def create_span_with_filtered_attributes(name, attributes):
    tracer = trace.get_tracer(__name__)
    
    # 过滤属性
    filtered_attributes = attribute_filter.filter_attributes(attributes)
    
    # 创建span
    return tracer.start_as_current_span(name, attributes=filtered_attributes)

# 使用示例
with create_span_with_filtered_attributes(
    "http-request",
    {
        "http.method": "GET",
        "http.url": "https://example.com",
        "http.status_code": 200,
        "user.id": "user-123",
        "operation.type": "http",
        "internal.attribute": "this will be filtered out"
    }
):
    print("Span created with filtered attributes")
```

## 3.8 实验验证

### 实验1：实现自定义Instrumentation

#### 实验目标
创建一个自定义的Python库，并为该库实现手动Instrumentation。

#### 实验步骤
1. 创建一个简单的数据处理库
2. 为该库添加手动Instrumentation
3. 使用该库并验证遥测数据

#### 实验代码
```python
# data_processor.py
import time
import random
from opentelemetry import trace

class DataProcessor:
    def __init__(self, name):
        self.name = name
        self.tracer = trace.get_tracer(__name__)
    
    def process_data(self, data):
        with self.tracer.start_as_current_span("process-data") as span:
            span.set_attribute("processor.name", self.name)
            span.set_attribute("data.size", len(data))
            
            # 模拟数据验证
            with self.tracer.start_as_current_span("validate-data"):
                self._validate_data(data)
            
            # 模拟数据转换
            with self.tracer.start_as_current_span("transform-data"):
                transformed_data = self._transform_data(data)
            
            # 模拟数据存储
            with self.tracer.start_as_current_span("store-data"):
                self._store_data(transformed_data)
            
            return transformed_data
    
    def _validate_data(self, data):
        # 模拟验证过程
        time.sleep(0.1)
        
        # 随机验证失败
        if random.random() < 0.1:
            raise ValueError("Data validation failed")
    
    def _transform_data(self, data):
        # 模拟转换过程
        time.sleep(0.2)
        return [item.upper() for item in data]
    
    def _store_data(self, data):
        # 模拟存储过程
        time.sleep(0.15)
        print(f"Stored {len(data)} items")

# main.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from data_processor import DataProcessor

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "custom-instrumentation-demo"
})

# 设置追踪
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置Jaeger导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# 添加span处理器
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def main():
    # 创建数据处理器
    processor = DataProcessor("main-processor")
    
    # 处理数据
    data = ["item1", "item2", "item3", "item4", "item5"]
    
    try:
        result = processor.process_data(data)
        print(f"Processing completed: {result}")
    except Exception as e:
        print(f"Processing failed: {e}")

if __name__ == "__main__":
    main()
    
    # 等待span被导出
    time.sleep(2)
```

### 实验2：实现自定义采样器

#### 实验目标
创建一个自定义采样器，根据请求属性决定是否采样。

#### 实验步骤
1. 创建一个自定义采样器类
2. 实现采样逻辑，基于请求属性
3. 配置TracerProvider使用自定义采样器
4. 验证采样行为

#### 实验代码
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import Sampler, SamplingResult, Decision
from opentelemetry.context import Context
from opentelemetry.trace import SpanKind
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time

class AttributeBasedSampler(Sampler):
    def __init__(self, sample_rate=0.1, important_attribute="important"):
        self.sample_rate = sample_rate
        self.important_attribute = important_attribute
        self.always_on_sampler = trace.sampling.ALWAYS_ON
        self.trace_id_ratio_sampler = trace.sampling.TraceIdRatioBased(sample_rate)
    
    def should_sample(
        self,
        parent_context: Context,
        trace_id: int,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: dict = None,
        links: list = None,
    ) -> SamplingResult:
        # 如果有重要属性，总是采样
        if attributes and self.important_attribute in attributes and attributes[self.important_attribute]:
            return self.always_on_sampler.should_sample(
                parent_context, trace_id, name, kind, attributes, links
            )
        
        # 否则使用基于比例的采样
        return self.trace_id_ratio_sampler.should_sample(
            parent_context, trace_id, name, kind, attributes, links
        )
    
    def get_description(self) -> str:
        return f"AttributeBasedSampler({self.sample_rate}, {self.important_attribute})"

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "custom-sampler-demo"
})

# 创建自定义采样器
sampler = AttributeBasedSampler(sample_rate=0.1, important_attribute="important")

# 创建TracerProvider并设置采样器
tracer_provider = TracerProvider(resource=resource, sampler=sampler)
trace.set_tracer_provider(tracer_provider)

# 配置Jaeger导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# 添加span处理器
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 获取Tracer
tracer = trace.get_tracer(__name__)

def process_request(request_id, important=False):
    attributes = {"request.id": request_id}
    if important:
        attributes["important"] = True
    
    with tracer.start_as_current_span("process-request", attributes=attributes):
        # 模拟处理
        time.sleep(0.1)
        print(f"Processed request {request_id} (important: {important})")

def main():
    # 处理多个请求，其中一些是重要的
    for i in range(20):
        important = i % 5 == 0  # 每5个请求中有1个是重要的
        process_request(f"req-{i+1}", important)
    
    print("Check Jaeger UI to see which requests were sampled: http://localhost:16686")

if __name__ == "__main__":
    main()
    
    # 等待span被导出
    time.sleep(2)
```

### 实验3：实现上下文传播

#### 实验目标
实现一个简单的分布式系统，展示上下文如何在服务之间传播。

#### 实验步骤
1. 创建两个服务（客户端和服务器）
2. 实现HTTP客户端和服务器，支持上下文传播
3. 验证追踪上下文在服务之间的传播

#### 实验代码
```python
# server.py
from flask import Flask, request, jsonify
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.propagate import extract
import time

# 创建Flask应用
app = Flask(__name__)

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "server-service"
})

# 设置追踪
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置Jaeger导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# 添加span处理器
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 自动追踪Flask请求
FlaskInstrumentor().instrument_app(app)

@app.route("/api/process")
def process_data():
    # 提取上下文
    headers = dict(request.headers)
    ctx = extract(headers)
    
    # 在提取的上下文中创建span
    with tracer.start_as_current_span("server-process", context=ctx) as span:
        span.set_attribute("server.operation", "process")
        
        # 获取请求参数
        data_id = request.args.get("data_id", "unknown")
        span.set_attribute("data.id", data_id)
        
        # 模拟处理
        time.sleep(0.2)
        
        # 添加事件
        span.add_event("Data processed successfully")
        
        return jsonify({"status": "success", "data_id": data_id})

if __name__ == "__main__":
    app.run(port=5001)
```

```python
# client.py
import requests
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.propagate import inject
import time

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "client-service"
})

# 设置追踪
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置Jaeger导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# 添加span处理器
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def call_server(data_id):
    with tracer.start_as_current_span("client-request") as span:
        span.set_attribute("client.operation", "request")
        span.set_attribute("data.id", data_id)
        
        # 注入上下文到HTTP头
        headers = {}
        inject(headers)
        
        # 发送请求
        url = f"http://localhost:5001/api/process?data_id={data_id}"
        response = requests.get(url, headers=headers)
        
        # 设置属性
        span.set_attribute("http.status_code", response.status_code)
        
        return response.json()

def main():
    # 调用服务器多次
    for i in range(5):
        data_id = f"data-{i+1}"
        result = call_server(data_id)
        print(f"Result: {result}")
        time.sleep(0.5)
    
    print("Check Jaeger UI to see trace propagation: http://localhost:16686")

if __name__ == "__main__":
    main()
    
    # 等待span被导出
    time.sleep(2)
```

## 3.9 常见问题与解决方案

### 3.9.1 性能影响

**问题**：Instrumentation对应用程序性能有多大影响？

**解决方案**：
1. 使用采样减少数据量
2. 使用批处理减少网络开销
3. 使用异步导出不阻塞主线程
4. 在生产环境中调整采样率

### 3.9.2 数据丢失

**问题**：为什么有些遥测数据没有出现在后端？

**解决方案**：
1. 检查网络连接和防火墙设置
2. 确认导出器配置正确
3. 检查批处理设置和超时配置
4. 确认采样策略不会丢弃重要数据

### 3.9.3 上下文传播失败

**问题**：为什么追踪在不同服务之间不连续？

**解决方案**：
1. 确保所有服务使用相同的传播格式
2. 检查HTTP头是否被中间件或代理过滤
3. 确认客户端和服务器都正确提取和注入上下文
4. 验证异步操作正确传递上下文

### 3.9.4 高基数属性

**问题**：为什么指标或追踪数据量过大？

**解决方案**：
1. 避免使用高基数属性（如用户ID、请求ID）
2. 使用属性过滤器限制导出的属性
3. 对于高基数数据，考虑使用日志而非指标
4. 使用合适的采样策略

### 3.9.5 资源配置

**问题**：如何正确配置资源属性？

**解决方案**：
1. 确保每个服务都有唯一的service.name
2. 添加service.version和deployment.environment
3. 包含service.instance.id标识实例
4. 使用语义约定标准化属性名称

## 3.10 最佳实践

1. **分层Instrumentation**：结合自动和手动Instrumentation，快速启动并精细化控制
2. **渐进式实施**：从关键路径开始，逐步扩展到整个系统
3. **统一配置**：使用配置中心管理Instrumentation配置
4. **性能监控**：监控Instrumentation本身的性能影响
5. **团队协作**：制定团队范围内的Instrumentation标准和约定
6. **定期审查**：定期审查和优化Instrumentation策略
7. **文档记录**：记录自定义Instrumentation和配置决策
8. **测试验证**：为Instrumentation编写测试，确保其正常工作