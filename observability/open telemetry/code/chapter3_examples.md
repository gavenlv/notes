# 第3章：OpenTelemetry Instrumentation与SDK 示例代码

## 目录
1. [自动Instrumentation示例](#自动instrumentation示例)
2. [手动Instrumentation示例](#手动instrumentation示例)
3. [上下文传播示例](#上下文传播示例)
4. [采样策略示例](#采样策略示例)
5. [性能优化示例](#性能优化示例)
6. [实验代码](#实验代码)

## 自动Instrumentation示例

### Python自动Instrumentation示例

#### basic_auto_instrumentation.py

```python
"""
基本自动Instrumentation示例
使用opentelemetry-instrument命令自动instrumentation
"""

import requests
from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def hello():
    # 这个HTTP请求会被自动instrumentation
    response = requests.get("https://example.com")
    
    # 模拟处理时间
    time.sleep(0.1)
    
    return f"Hello, World! Response status: {response.status_code}"

@app.route("/api/users")
def get_users():
    # 模拟数据库查询
    time.sleep(0.2)
    
    return {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
    }

if __name__ == "__main__":
    app.run(port=5000)
```

#### code_auto_instrumentation.py

```python
"""
代码中配置自动Instrumentation示例
"""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.auto_instrumentation import sitecustomize
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import requests
from flask import Flask
import time

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "auto-instrumentation-demo"
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
app = Flask(__name__)

@app.route("/")
def hello():
    response = requests.get("https://example.com")
    return f"Hello, World! Response status: {response.status_code}"

@app.route("/api/data")
def get_data():
    # 这个请求会被自动instrumentation
    response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
    
    # 模拟处理时间
    time.sleep(0.1)
    
    return {
        "status": "success",
        "data": response.json()
    }

if __name__ == "__main__":
    app.run(port=5000)
```

### Java自动Instrumentation示例

#### AutoInstrumentationDemo.java

```java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
import org.springframework.beans.factory.annotation.Autowired;

@SpringBootApplication
@RestController
public class AutoInstrumentationDemo {
    
    @Autowired
    private RestTemplate restTemplate;
    
    public static void main(String[] args) {
        SpringApplication.run(AutoInstrumentationDemo.class, args);
    }
    
    @GetMapping("/")
    public String hello() {
        // 这个HTTP请求会被Java Agent自动instrumentation
        String response = restTemplate.getForObject("https://example.com", String.class);
        return "Hello, World! Response: " + response.substring(0, Math.min(50, response.length()));
    }
    
    @GetMapping("/api/data")
    public Object getData() {
        // 这个请求也会被自动instrumentation
        Object data = restTemplate.getForObject("https://jsonplaceholder.typicode.com/posts/1", Object.class);
        return data;
    }
}
```

### JavaScript自动Instrumentation示例

#### auto_instrumentation_demo.js

```javascript
/**
 * JavaScript自动Instrumentation示例
 */

const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-otlp-http');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const express = require('express');
const axios = require('axios');

// 初始化SDK
const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'auto-instrumentation-demo',
  }),
  traceExporter: new OTLPTraceExporter({
    url: 'http://localhost:4318/v1/traces',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

// 启动SDK
sdk.start();

const app = express();
const port = 3000;

app.get('/', async (req, res) => {
  try {
    // 这个HTTP请求会被自动instrumentation
    const response = await axios.get('https://example.com');
    res.send(`Hello, World! Response status: ${response.status}`);
  } catch (error) {
    res.status(500).send(`Error: ${error.message}`);
  }
});

app.get('/api/data', async (req, res) => {
  try {
    // 这个请求也会被自动instrumentation
    const response = await axios.get('https://jsonplaceholder.typicode.com/posts/1');
    res.json({
      status: 'success',
      data: response.data
    });
  } catch (error) {
    res.status(500).send(`Error: ${error.message}`);
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});

// 优雅关闭
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('SDK shut down successfully'))
    .catch((error) => console.error('Error shutting down SDK', error))
    .finally(() => process.exit(0));
});
```

## 手动Instrumentation示例

### Python手动追踪Instrumentation示例

#### basic_manual_tracing.py

```python
"""
基本手动追踪Instrumentation示例
"""

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
    # 基本追踪
    result = process_data("data-123")
    print(f"Result: {result}")
    
    # 嵌套追踪
    parent_operation()
    
    # 等待span被导出
    time.sleep(2)
```

### Python手动指标Instrumentation示例

#### manual_metrics_instrumentation.py

```python
"""
手动指标Instrumentation示例
"""

from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import time
import random
import psutil

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

# 创建直方图
response_time_histogram = meter.create_histogram(
    "response_time_seconds",
    description="Response time in seconds"
)

def process_request(endpoint, status_code):
    # 记录开始时间
    start_time = time.time()
    
    # 模拟处理
    processing_time = random.uniform(0.1, 1.0)
    time.sleep(processing_time)
    
    # 记录指标
    request_counter.add(1, {"endpoint": endpoint, "status_code": str(status_code)})
    response_time_histogram.record(processing_time, {"endpoint": endpoint})
    
    return {"endpoint": endpoint, "status_code": status_code, "processing_time": processing_time}

def simulate_connections():
    # 增加活跃连接
    active_connections_gauge.add(1)
    
    # 模拟连接活动
    time.sleep(1)
    
    # 减少活跃连接
    active_connections_gauge.add(-1)

if __name__ == "__main__":
    print("Keep the process running to view metrics at http://localhost:9090")
    
    # 模拟处理请求
    for i in range(10):
        endpoint = "/api/users" if i % 2 == 0 else "/api/products"
        status_code = 200 if i % 3 != 0 else 500
        
        result = process_request(endpoint, status_code)
        print(f"Processed request: {result}")
        
        # 模拟连接
        if i % 2 == 0:
            simulate_connections()
        
        time.sleep(0.5)
    
    print("Keep the process running to view metrics at http://localhost:9090")
    while True:
        simulate_connections()
        time.sleep(0.5)
```

### Python手动日志Instrumentation示例

#### manual_logging_instrumentation.py

```python
"""
手动日志Instrumentation示例
"""

import logging
import time
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk._logs import LogRecord, SeverityNumber

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
        log_record=LogRecord(
            timestamp=int(time.time() * 1e9),
            severity_number=SeverityNumber.INFO,
            severity_text="INFO",
            body=f"Processing data {data_id}",
            attributes={"data.id": data_id, "operation.type": "processing"}
        )
    )
    
    # 模拟处理
    time.sleep(0.5)
    
    # 记录日志
    logger.emit(
        log_record=LogRecord(
            timestamp=int(time.time() * 1e9),
            severity_number=SeverityNumber.INFO,
            severity_text="INFO",
            body=f"Completed processing data {data_id}",
            attributes={"data.id": data_id, "operation.type": "processing"}
        )
    )
    
    # 记录警告日志
    logger.emit(
        log_record=LogRecord(
            timestamp=int(time.time() * 1e9),
            severity_number=SeverityNumber.WARN,
            severity_text="WARN",
            body=f"Data {data_id} took longer than expected",
            attributes={"data.id": data_id, "operation.type": "processing", "warning.type": "performance"}
        )
    )

def process_data_with_error(data_id):
    # 记录日志
    logger.emit(
        log_record=LogRecord(
            timestamp=int(time.time() * 1e9),
            severity_number=SeverityNumber.INFO,
            severity_text="INFO",
            body=f"Starting processing data {data_id}",
            attributes={"data.id": data_id, "operation.type": "processing"}
        )
    )
    
    try:
        # 模拟处理
        time.sleep(0.2)
        
        # 模拟错误
        raise ValueError(f"Invalid data format for {data_id}")
    except Exception as e:
        # 记录错误日志
        logger.emit(
            log_record=LogRecord(
                timestamp=int(time.time() * 1e9),
                severity_number=SeverityNumber.ERROR,
                severity_text="ERROR",
                body=f"Failed to process data {data_id}: {str(e)}",
                attributes={
                    "data.id": data_id,
                    "operation.type": "processing",
                    "error.type": type(e).__name__,
                    "error.message": str(e)
                }
            )
        )

if __name__ == "__main__":
    process_data("data-123")
    process_data_with_error("data-456")
    
    # 等待日志被导出
    time.sleep(2)
```

## 上下文传播示例

### HTTP客户端传播示例

#### http_client_propagation.py

```python
"""
HTTP客户端上下文传播示例
"""

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
    SERVICE_NAME: "http-client-propagation-demo"
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

def make_http_request(url):
    # 创建span
    with tracer.start_as_current_span("http-request") as span:
        span.set_attribute("http.url", url)
        
        # 注入上下文到HTTP头
        headers = {}
        inject(headers)
        
        print(f"Injected headers: {headers}")
        
        # 发送请求
        response = requests.get(url, headers=headers)
        
        # 设置属性
        span.set_attribute("http.status_code", response.status_code)
        
        return response

def make_multiple_requests():
    with tracer.start_as_current_span("multiple-requests") as span:
        # 请求1
        response1 = make_http_request("https://example.com")
        print(f"Response 1 status: {response1.status_code}")
        
        # 请求2
        response2 = make_http_request("https://jsonplaceholder.typicode.com/posts/1")
        print(f"Response 2 status: {response2.status_code}")

if __name__ == "__main__":
    make_multiple_requests()
    
    # 等待span被导出
    time.sleep(2)
```

### HTTP服务器传播示例

#### http_server_propagation.py

```python
"""
HTTP服务器上下文传播示例
"""

from flask import Flask, request
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.propagate import extract
import requests
import time

# 创建Flask应用
app = Flask(__name__)

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "http-server-propagation-demo"
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

@app.route("/")
def hello():
    # 提取上下文
    headers = dict(request.headers)
    ctx = extract(headers)
    
    with tracer.start_as_current_span("http-server", context=ctx) as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", request.url)
        
        # 调用下游服务
        call_downstream_service()
        
        return "Hello, World!"

@app.route("/api/process")
def process_data():
    # 提取上下文
    headers = dict(request.headers)
    ctx = extract(headers)
    
    with tracer.start_as_current_span("process-data", context=ctx) as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", request.url)
        
        # 获取请求参数
        data_id = request.args.get("data_id", "unknown")
        span.set_attribute("data.id", data_id)
        
        # 模拟处理
        time.sleep(0.2)
        
        # 调用下游服务
        downstream_result = call_downstream_service_with_context()
        
        return {
            "status": "success",
            "data_id": data_id,
            "downstream_result": downstream_result
        }

def call_downstream_service():
    with tracer.start_as_current_span("downstream-call") as span:
        span.set_attribute("service.name", "downstream")
        
        # 模拟下游调用
        time.sleep(0.1)
        
        return {"result": "success"}

def call_downstream_service_with_context():
    with tracer.start_as_current_span("downstream-call-with-context") as span:
        span.set_attribute("service.name", "downstream")
        
        # 注入上下文到HTTP头
        headers = {}
        inject(headers)
        
        # 发送请求到外部服务
        response = requests.get("https://jsonplaceholder.typicode.com/posts/1", headers=headers)
        
        span.set_attribute("http.status_code", response.status_code)
        
        return response.json()

if __name__ == "__main__":
    app.run(port=5001)
```

### 手动上下文传播示例

#### manual_context_propagation.py

```python
"""
手动上下文传播示例
"""

from opentelemetry import trace, context
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_span_in_context
import time
import threading

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "manual-context-propagation-demo"
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

def process_with_context(data):
    # 获取当前上下文
    current_context = context.get_current()
    
    # 在新线程中使用上下文
    def worker():
        # 附加上下文
        token = context.attach(current_context)
        
        try:
            # 在上下文中创建span
            with tracer.start_as_current_span("worker-operation"):
                # 处理数据
                time.sleep(0.2)
                print(f"Processing data: {data}")
        finally:
            # 分离上下文
            context.detach(token)
    
    # 启动线程
    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

def process_with_new_context(data):
    # 创建新上下文
    with tracer.start_as_current_span("parent-operation") as parent_span:
        parent_span.set_attribute("data.id", data)
        
        # 创建子上下文
        child_context = set_span_in_context(parent_span)
        
        # 在新线程中使用子上下文
        def child_worker():
            # 附加上下文
            token = context.attach(child_context)
            
            try:
                # 在上下文中创建span
                with tracer.start_as_current_span("child-operation"):
                    # 处理数据
                    time.sleep(0.2)
                    print(f"Child processing data: {data}")
            finally:
                # 分离上下文
                context.detach(token)
        
        # 启动线程
        thread = threading.Thread(target=child_worker)
        thread.start()
        thread.join()

if __name__ == "__main__":
    # 使用当前上下文
    with tracer.start_as_current_span("main-operation"):
        process_with_context("test-data-1")
    
    # 使用新上下文
    process_with_new_context("test-data-2")
    
    # 等待span被导出
    time.sleep(2)
```

## 采样策略示例

### 基于比例的采样示例

#### ratio_based_sampling.py

```python
"""
基于比例的采样示例
"""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
import time

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "ratio-based-sampling-demo"
})

# 创建采样器（采样率为25%）
sampler = TraceIdRatioBased(0.25)

# 创建TracerProvider并设置采样器
tracer_provider = TracerProvider(resource=resource, sampler=sampler)
trace.set_tracer_provider(tracer_provider)

# 获取Tracer
tracer = trace.get_tracer(__name__)

# 配置导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# 添加span处理器
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def create_spans(count):
    for i in range(count):
        with tracer.start_as_current_span(f"sampled-operation-{i+1}") as span:
            span.set_attribute("operation.id", i+1)
            
            # 模拟工作
            time.sleep(0.1)
            
            # 检查是否被采样
            if span.is_recording():
                print(f"Span {i+1} is being recorded (sampled)")
            else:
                print(f"Span {i+1} is not being recorded (not sampled)")

if __name__ == "__main__":
    print("Creating 20 spans with 25% sampling rate...")
    create_spans(20)
    
    print("Check Jaeger UI to see which spans were sampled: http://localhost:16686")
    
    # 等待span被导出
    time.sleep(2)
```

### 基于父span的采样示例

#### parent_based_sampling.py

```python
"""
基于父span的采样示例
"""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased, ALWAYS_ON, ALWAYS_OFF
import time

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "parent-based-sampling-demo"
})

# 创建父采样器
parent_sampler = ParentBased(
    root=TraceIdRatioBased(0.1),  # 根span使用10%采样率
    remote_parent_sampled=ALWAYS_ON,  # 远程采样的父span总是采样
    remote_parent_not_sampled=ALWAYS_ON,  # 远程未采样的父span总是采样
    local_parent_sampled=ALWAYS_ON,  # 本地采样的父span总是采样
    local_parent_not_sampled=ALWAYS_OFF,  # 本地未采样的父span从不采样
)

# 创建TracerProvider并设置采样器
tracer_provider = TracerProvider(resource=resource, sampler=parent_sampler)
trace.set_tracer_provider(tracer_provider)

# 获取Tracer
tracer = trace.get_tracer(__name__)

# 配置导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# 添加span处理器
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def create_root_spans(count):
    for i in range(count):
        with tracer.start_as_current_span(f"root-operation-{i+1}") as span:
            span.set_attribute("operation.type", "root")
            span.set_attribute("operation.id", i+1)
            
            # 创建子span
            create_child_spans(f"root-{i+1}", 3)
            
            # 检查是否被采样
            if span.is_recording():
                print(f"Root span {i+1} is being recorded (sampled)")
            else:
                print(f"Root span {i+1} is not being recorded (not sampled)")

def create_child_spans(parent_id, count):
    for i in range(count):
        with tracer.start_as_current_span(f"child-operation-{parent_id}-{i+1}") as span:
            span.set_attribute("operation.type", "child")
            span.set_attribute("operation.id", i+1)
            span.set_attribute("parent.id", parent_id)
            
            # 模拟工作
            time.sleep(0.05)
            
            # 检查是否被采样
            if span.is_recording():
                print(f"  Child span {parent_id}-{i+1} is being recorded (sampled)")
            else:
                print(f"  Child span {parent_id}-{i+1} is not being recorded (not sampled)")

if __name__ == "__main__":
    print("Creating root spans with 10% sampling rate...")
    create_root_spans(5)
    
    print("Check Jaeger UI to see which spans were sampled: http://localhost:16686")
    
    # 等待span被导出
    time.sleep(2)
```

### 自定义采样器示例

#### custom_sampler.py

```python
"""
自定义采样器示例
"""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import Sampler, SamplingResult, Decision
from opentelemetry.context import Context
from opentelemetry.trace import SpanKind
import time

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "custom-sampler-demo"
})

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
        
        # 或者，基于trace_id的哈希值进行采样
        if hash(str(trace_id)) % 10 < 3:  # 30%采样率
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

# 配置导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# 添加span处理器
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def create_spans():
    # 创建普通span
    with tracer.start_as_current_span("normal-operation"):
        print("This span may or may not be sampled, depending on the trace_id")
    
    # 创建重要span
    with tracer.start_as_current_span("important-operation", attributes={"important": True}):
        print("This span will be sampled because it has the 'important' attribute")
    
    # 创建关键span
    with tracer.start_as_current_span("critical-operation"):
        print("This span will be sampled because it contains 'critical' in the name")
    
    # 创建普通span
    with tracer.start_as_current_span("another-normal-operation"):
        print("This span may or may not be sampled, depending on the trace_id")

if __name__ == "__main__":
    print("Creating spans with custom sampling logic...")
    create_spans()
    
    print("Check Jaeger UI to see which spans were sampled: http://localhost:16686")
    
    # 等待span被导出
    time.sleep(2)
```

## 性能优化示例

### 批处理示例

#### batch_processing.py

```python
"""
批处理示例
"""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "batch-processing-demo"
})

# 设置追踪
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置导出器
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

def create_spans(count):
    start_time = time.time()
    
    for i in range(count):
        with tracer.start_as_current_span(f"batch-operation-{i+1}") as span:
            span.set_attribute("operation.id", i+1)
            
            # 模拟工作
            time.sleep(0.01)
    
    end_time = time.time()
    print(f"Created {count} spans in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    print("Creating 100 spans with batch processing...")
    create_spans(100)
    
    # 等待span被导出
    print("Waiting for spans to be exported...")
    time.sleep(5)
    
    print("Check Jaeger UI to see the spans: http://localhost:16686")
```

### 异步导出示例

#### async_export.py

```python
"""
异步导出示例
"""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from concurrent.futures import ThreadPoolExecutor
import time

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "async-export-demo"
})

# 设置追踪
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

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

def create_spans(count):
    start_time = time.time()
    
    for i in range(count):
        with tracer.start_as_current_span(f"async-operation-{i+1}") as span:
            span.set_attribute("operation.id", i+1)
            
            # 模拟工作
            time.sleep(0.01)
    
    end_time = time.time()
    print(f"Created {count} spans in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    print("Creating 100 spans with async export...")
    create_spans(100)
    
    # 等待span被导出
    print("Waiting for spans to be exported...")
    time.sleep(5)
    
    print("Check Jaeger UI to see the spans: http://localhost:16686")
    
    # 关闭线程池
    executor.shutdown(wait=True)
```

### 属性过滤示例

#### attribute_filtering.py

```python
"""
属性过滤示例
"""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "attribute-filtering-demo"
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

# 创建span时过滤属性
def create_span_with_filtered_attributes(name, attributes):
    # 过滤属性
    filtered_attributes = attribute_filter.filter_attributes(attributes)
    
    # 创建span
    with tracer.start_as_current_span(name, attributes=filtered_attributes) as span:
        span.set_attribute("filtered", True)
        
        # 模拟工作
        time.sleep(0.1)
        
        return span

if __name__ == "__main__":
    # 创建带有各种属性的span
    create_span_with_filtered_attributes(
        "http-request",
        {
            "http.method": "GET",
            "http.url": "https://example.com",
            "http.status_code": 200,
            "user.id": "user-123",
            "operation.type": "http",
            "internal.attribute": "this will be filtered out",
            "debug.info": "this will also be filtered out"
        }
    )
    
    print("Created span with filtered attributes")
    
    # 等待span被导出
    time.sleep(2)
    
    print("Check Jaeger UI to see the filtered attributes: http://localhost:16686")
```

## 实验代码

### 实验1：实现自定义Instrumentation

#### data_processor.py

```python
"""
自定义数据处理库
"""

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
```

#### experiment1_main.py

```python
"""
实验1主程序：使用自定义Instrumentation
"""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from data_processor import DataProcessor
import time

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
    
    print("Check Jaeger UI to see the custom instrumentation: http://localhost:16686")
```

### 实验2：实现自定义采样器

#### experiment2_main.py

```python
"""
实验2主程序：使用自定义采样器
"""

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

#### experiment3_server.py

```python
"""
实验3服务器程序：实现上下文传播
"""

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

#### experiment3_client.py

```python
"""
实验3客户端程序：实现上下文传播
"""

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

## 运行指南

### 运行自动Instrumentation示例

1. 安装依赖：
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-requests opentelemetry-instrumentation-flask
```

2. 运行基本自动Instrumentation示例：
```bash
opentelemetry-instrument -f -l http://localhost:4318 python basic_auto_instrumentation.py
```

3. 运行代码中配置自动Instrumentation示例：
```bash
python code_auto_instrumentation.py
```

### 运行手动Instrumentation示例

1. 安装依赖：
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger opentelemetry-exporter-prometheus opentelemetry-exporter-otlp
```

2. 运行手动追踪示例：
```bash
python basic_manual_tracing.py
```

3. 运行手动指标示例：
```bash
python manual_metrics_instrumentation.py
```

4. 运行手动日志示例：
```bash
python manual_logging_instrumentation.py
```

### 运行上下文传播示例

1. 安装依赖：
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger opentelemetry-instrumentation-flask requests
```

2. 运行HTTP服务器传播示例：
```bash
python http_server_propagation.py
```

3. 在另一个终端运行HTTP客户端传播示例：
```bash
python http_client_propagation.py
```

### 运行采样策略示例

1. 安装依赖：
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger
```

2. 运行基于比例的采样示例：
```bash
python ratio_based_sampling.py
```

3. 运行基于父span的采样示例：
```bash
python parent_based_sampling.py
```

4. 运行自定义采样器示例：
```bash
python custom_sampler.py
```

### 运行性能优化示例

1. 安装依赖：
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger
```

2. 运行批处理示例：
```bash
python batch_processing.py
```

3. 运行异步导出示例：
```bash
python async_export.py
```

4. 运行属性过滤示例：
```bash
python attribute_filtering.py
```

### 运行实验代码

1. 安装依赖：
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger opentelemetry-instrumentation-flask requests flask
```

2. 运行实验1：自定义Instrumentation
```bash
python experiment1_main.py
```

3. 运行实验2：自定义采样器
```bash
python experiment2_main.py
```

4. 运行实验3：上下文传播
   - 在一个终端运行服务器：
   ```bash
   python experiment3_server.py
   ```
   - 在另一个终端运行客户端：
   ```bash
   python experiment3_client.py
   ```

### 查看结果

1. 启动Jaeger：
```bash
docker run -d -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one:latest
```

2. 访问Jaeger UI：http://localhost:16686

3. 启动Prometheus（用于指标示例）：
```bash
docker run -d -p 9090:9090 prom/prometheus
```

4. 访问Prometheus UI：http://localhost:9090

5. 启动OpenTelemetry Collector（用于日志示例）：
```bash
docker run -d -p 4317:4317 -p 4318:4318 -v $(pwd)/otel-collector-config.yaml:/etc/otel-collector-config.yaml otel/opentelemetry-collector:latest --config=/etc/otel-collector-config.yaml
```

### 注意事项

1. 确保所有依赖项都已正确安装
2. 确保Jaeger、Prometheus和OpenTelemetry Collector（如果需要）正在运行
3. 根据你的环境调整导出器配置
4. 在生产环境中，使用适当的采样率和批处理设置以优化性能