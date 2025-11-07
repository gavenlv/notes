# 第2章示例代码

## 2.2 追踪（Tracing）示例

### 基本追踪示例

#### basic_tracing.py

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time
import random

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "tracing-demo"
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

def parent_operation():
    with tracer.start_as_current_span("parent-operation") as parent_span:
        parent_span.set_attribute("operation.type", "parent")
        
        # 添加事件
        parent_span.add_event("Starting parent operation")
        
        # 调用子操作
        child_operation_1()
        child_operation_2()
        
        # 添加事件
        parent_span.add_event("Parent operation completed")

def child_operation_1():
    with tracer.start_as_current_span("child-operation-1") as child_span:
        child_span.set_attribute("operation.type", "child")
        child_span.set_attribute("operation.id", "1")
        
        # 模拟工作
        time.sleep(random.uniform(0.1, 0.3))
        
        # 添加事件
        child_span.add_event("Child operation 1 completed")

def child_operation_2():
    with tracer.start_as_current_span("child-operation-2") as child_span:
        child_span.set_attribute("operation.type", "child")
        child_span.set_attribute("operation.id", "2")
        
        # 模拟工作
        time.sleep(random.uniform(0.2, 0.5))
        
        # 添加事件
        child_span.add_event("Child operation 2 completed")

if __name__ == "__main__":
    parent_operation()
    print("Tracing example completed. Check Jaeger UI at http://localhost:16686")
    
    # 等待span被导出
    time.sleep(2)
```

### HTTP追踪示例

#### http_tracing.py

```python
from flask import Flask, request, jsonify
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import requests
import time

# 创建Flask应用
app = Flask(__name__)

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "http-tracing-demo"
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

# 自动追踪HTTP请求
RequestsInstrumentor().instrument()

@app.route('/api/data')
def get_data():
    with tracer.start_as_current_span("get-data") as span:
        span.set_attribute("operation.type", "database")
        
        # 模拟数据库查询
        time.sleep(0.1)
        
        # 添加事件
        span.add_event("Database query completed")
        
        return jsonify({"data": "example data"})

@app.route('/api/external')
def call_external():
    with tracer.start_as_current_span("call-external-service") as span:
        span.set_attribute("operation.type", "external-api")
        span.set_attribute("external.service", "jsonplaceholder")
        
        # 调用外部API
        response = requests.get('https://jsonplaceholder.typicode.com/todos/1')
        
        # 添加属性
        span.set_attribute("http.status_code", response.status_code)
        
        return jsonify(response.json())

if __name__ == "__main__":
    app.run(port=5000)
```

## 2.3 指标（Metrics）示例

### 基本指标示例

#### basic_metrics.py

```python
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import time
import random
import psutil

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "metrics-demo"
})

# 设置指标
reader = PrometheusMetricReader(port=9090)
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

# 获取meter
meter = metrics.get_meter(__name__)

# 创建指标
request_counter = meter.create_counter(
    "requests_total",
    description="Total number of requests"
)

response_time_histogram = meter.create_histogram(
    "response_time_seconds",
    description="Response time in seconds"
)

memory_usage_gauge = meter.create_observable_gauge(
    "memory_usage_bytes",
    description="Current memory usage in bytes",
    callbacks=[lambda options: (psutil.virtual_memory().used, {})]
)

def process_request(request_type):
    # 记录开始时间
    start_time = time.time()
    
    # 模拟处理
    processing_time = random.uniform(0.1, 0.5)
    time.sleep(processing_time)
    
    # 记录指标
    request_counter.add(1, {"request_type": request_type})
    response_time_histogram.record(processing_time, {"request_type": request_type})
    
    return {"status": "success", "processing_time": processing_time}

if __name__ == "__main__":
    print("Starting metrics example...")
    print("Check Prometheus metrics at http://localhost:9090")
    
    # 模拟处理多个请求
    for i in range(100):
        request_type = random.choice(["read", "write", "delete"])
        result = process_request(request_type)
        print(f"Request {i+1}: {result}")
        
        time.sleep(0.5)
    
    print("Metrics example completed. Keep the process running to view metrics.")
    # 保持进程运行以便查看指标
    while True:
        time.sleep(1)
```

### 高级指标示例

#### advanced_metrics.py

```python
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import time
import random
import threading

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "advanced-metrics-demo"
})

# 设置指标
reader = PrometheusMetricReader(port=9091)
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

# 获取meter
meter = metrics.get_meter(__name__)

# 创建指标
request_counter = meter.create_counter(
    "http_requests_total",
    description="Total number of HTTP requests"
)

active_requests_gauge = meter.create_up_down_counter(
    "http_active_requests",
    description="Current number of active HTTP requests"
)

request_duration = meter.create_histogram(
    "http_request_duration_seconds",
    description="HTTP request duration in seconds"
)

error_rate = meter.create_counter(
    "http_errors_total",
    description="Total number of HTTP errors"
)

def simulate_http_request(endpoint):
    # 增加活跃请求计数
    active_requests_gauge.add(1, {"endpoint": endpoint})
    
    try:
        # 记录开始时间
        start_time = time.time()
        
        # 模拟处理
        processing_time = random.uniform(0.05, 0.5)
        time.sleep(processing_time)
        
        # 模拟可能的错误
        if random.random() < 0.1:
            raise Exception("Random error")
        
        # 记录指标
        request_counter.add(1, {"endpoint": endpoint, "method": "GET", "status": "200"})
        request_duration.record(processing_time, {"endpoint": endpoint})
        
        return {"status": "success", "processing_time": processing_time}
    
    except Exception as e:
        # 记录错误指标
        request_counter.add(1, {"endpoint": endpoint, "method": "GET", "status": "500"})
        error_rate.add(1, {"endpoint": endpoint, "error_type": type(e).__name__})
        
        return {"status": "error", "error": str(e)}
    
    finally:
        # 减少活跃请求计数
        active_requests_gauge.add(-1, {"endpoint": endpoint})

def worker():
    endpoints = ["/api/users", "/api/products", "/api/orders"]
    
    while True:
        endpoint = random.choice(endpoints)
        result = simulate_http_request(endpoint)
        print(f"Request to {endpoint}: {result}")
        
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    print("Starting advanced metrics example...")
    print("Check Prometheus metrics at http://localhost:9091")
    
    # 创建多个工作线程
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # 主线程等待
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
```

## 2.4 日志（Logging）示例

### 基本日志示例

#### basic_logging.py

```python
import logging
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "logging-demo"
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

def process_data(data_id):
    # 获取当前上下文
    current_span = trace.get_current_span()
    if current_span:
        trace_id = format(current_span.get_span_context().trace_id, "032x")
        span_id = format(current_span.get_span_context().span_id, "016x")
    else:
        trace_id = "unknown"
        span_id = "unknown"
    
    # 记录日志，包含追踪信息
    logger.info(
        f"Processing data {data_id}",
        extra={
            "trace_id": trace_id,
            "span_id": span_id,
            "data_id": data_id
        }
    )
    
    # 模拟处理
    time.sleep(0.5)
    
    # 记录日志，包含追踪信息
    logger.info(
        f"Completed processing data {data_id}",
        extra={
            "trace_id": trace_id,
            "span_id": span_id,
            "data_id": data_id
        }
    )
    
    return {"status": "success", "data_id": data_id}

def main():
    with tracer.start_as_current_span("main-operation") as span:
        logger.info("Starting main operation")
        
        # 处理多个数据项
        for i in range(3):
            with tracer.start_as_current_span(f"process-data-{i}") as child_span:
                result = process_data(f"data-{i}")
                logger.info(f"Result: {result}")
        
        logger.info("Main operation completed")

if __name__ == "__main__":
    main()
    print("Logging example completed. Check logs for trace information.")
```

### 结构化日志示例

#### structured_logging.py

```python
import json
import logging
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time
import sys

# 自定义JSON格式化器
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_object = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # 添加追踪信息
        if hasattr(record, 'trace_id'):
            log_object["trace_id"] = record.trace_id
        if hasattr(record, 'span_id'):
            log_object["span_id"] = record.span_id
        
        # 添加额外属性
        if hasattr(record, 'extra_fields'):
            log_object.update(record.extra_fields)
        
        return json.dumps(log_object)

# 配置日志
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "structured-logging-demo"
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

def log_with_trace(message, level="info", **kwargs):
    # 获取当前上下文
    current_span = trace.get_current_span()
    if current_span:
        trace_id = format(current_span.get_span_context().trace_id, "032x")
        span_id = format(current_span.get_span_context().span_id, "016x")
    else:
        trace_id = "unknown"
        span_id = "unknown"
    
    # 记录结构化日志
    log_method = getattr(logger, level.lower())
    log_method(
        message,
        extra={
            "trace_id": trace_id,
            "span_id": span_id,
            "extra_fields": kwargs
        }
    )

def process_user_request(user_id, action):
    with tracer.start_as_current_span("process-user-request") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("action", action)
        
        # 记录日志
        log_with_trace(
            f"Processing user request",
            user_id=user_id,
            action=action,
            component="user-service"
        )
        
        # 模拟处理
        time.sleep(0.5)
        
        # 记录日志
        log_with_trace(
            f"User request processed",
            user_id=user_id,
            action=action,
            component="user-service",
            status="success"
        )
        
        return {"status": "success", "user_id": user_id, "action": action}

def main():
    with tracer.start_as_current_span("main-operation") as span:
        log_with_trace("Starting main operation", component="main-service")
        
        # 处理用户请求
        for user_id in ["user-1", "user-2", "user-3"]:
            result = process_user_request(user_id, "get_profile")
            log_with_trace(f"User request result", result=result)
        
        log_with_trace("Main operation completed", component="main-service")

if __name__ == "__main__":
    main()
    print("Structured logging example completed. Check JSON logs for trace information.")
```

## 2.5 三大信号关联示例

### 关联示例

#### correlated_signals.py

```python
import json
import logging
import time
import random
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 自定义JSON格式化器
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_object = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # 添加追踪信息
        if hasattr(record, 'trace_id'):
            log_object["trace_id"] = record.trace_id
        if hasattr(record, 'span_id'):
            log_object["span_id"] = record.span_id
        
        # 添加额外属性
        if hasattr(record, 'extra_fields'):
            log_object.update(record.extra_fields)
        
        return json.dumps(log_object)

# 配置日志
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "correlated-signals-demo"
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

# 设置指标
reader = PrometheusMetricReader(port=9092)
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

# 获取meter
meter = metrics.get_meter(__name__)

# 创建指标
request_counter = meter.create_counter(
    "requests_total",
    description="Total number of requests"
)

response_time_histogram = meter.create_histogram(
    "response_time_seconds",
    description="Response time in seconds"
)

def log_with_trace(message, level="info", **kwargs):
    # 获取当前上下文
    current_span = trace.get_current_span()
    if current_span:
        trace_id = format(current_span.get_span_context().trace_id, "032x")
        span_id = format(current_span.get_span_context().span_id, "016x")
    else:
        trace_id = "unknown"
        span_id = "unknown"
    
    # 记录结构化日志
    log_method = getattr(logger, level.lower())
    log_method(
        message,
        extra={
            "trace_id": trace_id,
            "span_id": span_id,
            "extra_fields": kwargs
        }
    )

def process_request(request_id, endpoint):
    with tracer.start_as_current_span("process-request") as span:
        # 设置span属性
        span.set_attribute("request.id", request_id)
        span.set_attribute("endpoint", endpoint)
        
        # 记录开始时间
        start_time = time.time()
        
        # 记录日志
        log_with_trace(
            f"Processing request",
            request_id=request_id,
            endpoint=endpoint,
            component="request-processor"
        )
        
        try:
            # 模拟处理
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)
            
            # 模拟可能的错误
            if random.random() < 0.2:
                raise Exception("Random processing error")
            
            # 记录指标
            request_counter.add(1, {"endpoint": endpoint, "status": "success"})
            response_time_histogram.record(processing_time, {"endpoint": endpoint})
            
            # 记录日志
            log_with_trace(
                f"Request processed successfully",
                request_id=request_id,
                endpoint=endpoint,
                processing_time=processing_time,
                component="request-processor",
                status="success"
            )
            
            return {"status": "success", "request_id": request_id, "processing_time": processing_time}
        
        except Exception as e:
            # 记录异常
            span.record_exception(e)
            
            # 记录指标
            request_counter.add(1, {"endpoint": endpoint, "status": "error"})
            
            # 记录日志
            log_with_trace(
                f"Request processing failed",
                request_id=request_id,
                endpoint=endpoint,
                error=str(e),
                component="request-processor",
                status="error",
                level="error"
            )
            
            # 重新抛出异常
            raise

def main():
    with tracer.start_as_current_span("main-operation") as span:
        log_with_trace("Starting main operation", component="main-service")
        
        # 处理多个请求
        endpoints = ["/api/users", "/api/products", "/api/orders"]
        for i in range(10):
            request_id = f"req-{i+1}"
            endpoint = random.choice(endpoints)
            
            try:
                result = process_request(request_id, endpoint)
                log_with_trace(f"Request result", result=result)
            except Exception as e:
                log_with_trace(f"Request failed", request_id=request_id, error=str(e), level="error")
        
        log_with_trace("Main operation completed", component="main-service")

if __name__ == "__main__":
    print("Starting correlated signals example...")
    print("Check Jaeger UI at http://localhost:16686")
    print("Check Prometheus metrics at http://localhost:9092")
    
    main()
    
    print("Correlated signals example completed.")
    print("Keep the process running to view metrics.")
    
    # 保持进程运行以便查看指标
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
```

## 2.7 实验代码

### 实验1：创建并分析追踪

#### experiment1_tracing.py

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time
import random

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "experiment1-tracing"
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

def simulate_service_call(service_name, operation_name):
    with tracer.start_as_current_span(f"{service_name}.{operation_name}") as span:
        span.set_attribute("service.name", service_name)
        span.set_attribute("operation.name", operation_name)
        
        # 模拟处理时间
        processing_time = random.uniform(0.1, 0.5)
        time.sleep(processing_time)
        
        # 添加事件
        span.add_event(f"Operation {operation_name} completed")
        
        return processing_time

def main():
    with tracer.start_as_current_span("user-request") as root_span:
        root_span.set_attribute("user.id", "user-123")
        root_span.set_attribute("request.type", "get-user-profile")
        
        # 调用认证服务
        with tracer.start_as_current_span("call-auth-service") as span:
            auth_time = simulate_service_call("auth-service", "authenticate")
            span.set_attribute("auth.time", auth_time)
        
        # 调用用户服务
        with tracer.start_as_current_span("call-user-service") as span:
            user_time = simulate_service_call("user-service", "get-profile")
            span.set_attribute("user.time", user_time)
        
        # 调用订单服务
        with tracer.start_as_current_span("call-order-service") as span:
            order_time = simulate_service_call("order-service", "get-orders")
            span.set_attribute("order.time", order_time)
        
        # 添加事件
        root_span.add_event("User request completed")

if __name__ == "__main__":
    print("实验1：创建并分析追踪")
    print("请在Jaeger UI中查看追踪数据：http://localhost:16686")
    
    main()
    
    # 等待span被导出
    time.sleep(2)
    
    print("实验1完成。")
```

### 实验2：收集和分析指标

#### experiment2_metrics.py

```python
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import time
import random

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "experiment2-metrics"
})

# 设置指标
reader = PrometheusMetricReader(port=9093)
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

# 获取meter
meter = metrics.get_meter(__name__)

# 创建指标
request_counter = meter.create_counter(
    "requests_total",
    description="Total number of requests"
)

response_time_histogram = meter.create_histogram(
    "response_time_seconds",
    description="Response time in seconds"
)

error_counter = meter.create_counter(
    "errors_total",
    description="Total number of errors"
)

def simulate_request(endpoint):
    # 记录开始时间
    start_time = time.time()
    
    # 模拟处理
    processing_time = random.uniform(0.05, 0.5)
    time.sleep(processing_time)
    
    # 模拟可能的错误
    if random.random() < 0.15:
        # 记录错误指标
        error_counter.add(1, {"endpoint": endpoint, "error_type": "processing_error"})
        raise Exception("Random processing error")
    
    # 记录指标
    request_counter.add(1, {"endpoint": endpoint, "status": "success"})
    response_time_histogram.record(processing_time, {"endpoint": endpoint})
    
    return processing_time

def main():
    print("实验2：收集和分析指标")
    print("请在Prometheus中查看指标数据：http://localhost:9093")
    
    endpoints = ["/api/users", "/api/products", "/api/orders"]
    
    # 模拟处理多个请求
    for i in range(100):
        endpoint = random.choice(endpoints)
        
        try:
            processing_time = simulate_request(endpoint)
            print(f"Request {i+1} to {endpoint} completed in {processing_time:.3f}s")
        except Exception as e:
            print(f"Request {i+1} to {endpoint} failed: {str(e)}")
        
        time.sleep(0.1)
    
    print("实验2完成。保持进程运行以查看指标。")
    
    # 保持进程运行以便查看指标
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
```

### 实验3：记录和分析日志

#### experiment3_logging.py

```python
import json
import logging
import time
import random
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 自定义JSON格式化器
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_object = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # 添加追踪信息
        if hasattr(record, 'trace_id'):
            log_object["trace_id"] = record.trace_id
        if hasattr(record, 'span_id'):
            log_object["span_id"] = record.span_id
        
        # 添加额外属性
        if hasattr(record, 'extra_fields'):
            log_object.update(record.extra_fields)
        
        return json.dumps(log_object)

# 配置日志
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "experiment3-logging"
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

def log_with_trace(message, level="info", **kwargs):
    # 获取当前上下文
    current_span = trace.get_current_span()
    if current_span:
        trace_id = format(current_span.get_span_context().trace_id, "032x")
        span_id = format(current_span.get_span_context().span_id, "016x")
    else:
        trace_id = "unknown"
        span_id = "unknown"
    
    # 记录结构化日志
    log_method = getattr(logger, level.lower())
    log_method(
        message,
        extra={
            "trace_id": trace_id,
            "span_id": span_id,
            "extra_fields": kwargs
        }
    )

def process_user_request(user_id, action):
    with tracer.start_as_current_span("process-user-request") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("action", action)
        
        # 记录日志
        log_with_trace(
            f"Processing user request",
            user_id=user_id,
            action=action,
            component="user-service"
        )
        
        # 模拟处理
        time.sleep(random.uniform(0.1, 0.3))
        
        # 模拟可能的错误
        if random.random() < 0.2:
            error_msg = "User not found"
            span.set_attribute("error.message", error_msg)
            
            # 记录错误日志
            log_with_trace(
                f"User request failed",
                user_id=user_id,
                action=action,
                error=error_msg,
                component="user-service",
                level="error"
            )
            
            raise Exception(error_msg)
        
        # 记录日志
        log_with_trace(
            f"User request processed",
            user_id=user_id,
            action=action,
            component="user-service"
        )
        
        return {"status": "success", "user_id": user_id, "action": action}

def main():
    print("实验3：记录和分析日志")
    print("请查看结构化日志输出，注意其中的追踪信息。")
    
    with tracer.start_as_current_span("main-operation") as span:
        log_with_trace("Starting main operation", component="main-service")
        
        # 处理用户请求
        users = ["user-1", "user-2", "user-3", "user-4", "user-5"]
        actions = ["get_profile", "update_profile", "delete_profile"]
        
        for user_id in users:
            action = random.choice(actions)
            
            try:
                result = process_user_request(user_id, action)
                log_with_trace(f"User request result", result=result)
            except Exception as e:
                log_with_trace(f"User request failed", user_id=user_id, action=action, error=str(e), level="error")
        
        log_with_trace("Main operation completed", component="main-service")
    
    # 等待span被导出
    time.sleep(2)
    
    print("实验3完成。")
    print("请在Jaeger UI中查看追踪数据：http://localhost:16686")

if __name__ == "__main__":
    main()
```

### 实验4：关联三大信号

#### experiment4_correlation.py

```python
import json
import logging
import time
import random
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 自定义JSON格式化器
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_object = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # 添加追踪信息
        if hasattr(record, 'trace_id'):
            log_object["trace_id"] = record.trace_id
        if hasattr(record, 'span_id'):
            log_object["span_id"] = record.span_id
        
        # 添加额外属性
        if hasattr(record, 'extra_fields'):
            log_object.update(record.extra_fields)
        
        return json.dumps(log_object)

# 配置日志
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "experiment4-correlation"
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

# 设置指标
reader = PrometheusMetricReader(port=9094)
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

# 获取meter
meter = metrics.get_meter(__name__)

# 创建指标
request_counter = meter.create_counter(
    "requests_total",
    description="Total number of requests"
)

response_time_histogram = meter.create_histogram(
    "response_time_seconds",
    description="Response time in seconds"
)

error_counter = meter.create_counter(
    "errors_total",
    description="Total number of errors"
)

def log_with_trace(message, level="info", **kwargs):
    # 获取当前上下文
    current_span = trace.get_current_span()
    if current_span:
        trace_id = format(current_span.get_span_context().trace_id, "032x")
        span_id = format(current_span.get_span_context().span_id, "016x")
    else:
        trace_id = "unknown"
        span_id = "unknown"
    
    # 记录结构化日志
    log_method = getattr(logger, level.lower())
    log_method(
        message,
        extra={
            "trace_id": trace_id,
            "span_id": span_id,
            "extra_fields": kwargs
        }
    )

def process_request(request_id, endpoint):
    with tracer.start_as_current_span("process-request") as span:
        # 设置span属性
        span.set_attribute("request.id", request_id)
        span.set_attribute("endpoint", endpoint)
        
        # 记录开始时间
        start_time = time.time()
        
        # 记录日志
        log_with_trace(
            f"Processing request",
            request_id=request_id,
            endpoint=endpoint,
            component="request-processor"
        )
        
        try:
            # 模拟处理
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)
            
            # 模拟可能的错误
            if random.random() < 0.2:
                raise Exception("Random processing error")
            
            # 记录指标
            request_counter.add(1, {"endpoint": endpoint, "status": "success"})
            response_time_histogram.record(processing_time, {"endpoint": endpoint})
            
            # 记录日志
            log_with_trace(
                f"Request processed successfully",
                request_id=request_id,
                endpoint=endpoint,
                processing_time=processing_time,
                component="request-processor",
                status="success"
            )
            
            return {"status": "success", "request_id": request_id, "processing_time": processing_time}
        
        except Exception as e:
            # 记录异常
            span.record_exception(e)
            
            # 记录指标
            request_counter.add(1, {"endpoint": endpoint, "status": "error"})
            error_counter.add(1, {"endpoint": endpoint, "error_type": type(e).__name__})
            
            # 记录日志
            log_with_trace(
                f"Request processing failed",
                request_id=request_id,
                endpoint=endpoint,
                error=str(e),
                component="request-processor",
                status="error",
                level="error"
            )
            
            # 重新抛出异常
            raise

def main():
    print("实验4：关联三大信号")
    print("请在以下位置查看数据：")
    print("- Jaeger UI: http://localhost:16686")
    print("- Prometheus: http://localhost:9094")
    print("- 控制台日志（包含追踪信息）")
    
    with tracer.start_as_current_span("main-operation") as span:
        log_with_trace("Starting main operation", component="main-service")
        
        # 处理多个请求
        endpoints = ["/api/users", "/api/products", "/api/orders"]
        for i in range(20):
            request_id = f"req-{i+1}"
            endpoint = random.choice(endpoints)
            
            try:
                result = process_request(request_id, endpoint)
                log_with_trace(f"Request result", result=result)
            except Exception as e:
                log_with_trace(f"Request failed", request_id=request_id, error=str(e), level="error")
        
        log_with_trace("Main operation completed", component="main-service")
    
    # 等待span被导出
    time.sleep(2)
    
    print("实验4完成。")
    print("保持进程运行以查看指标。")
    
    # 保持进程运行以便查看指标
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
```

## Docker Compose配置

#### docker-compose.yml

```yaml
version: '3.7'

services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
      - "6831:6831/udp"
    environment:
      - COLLECTOR_OTLP_ENABLED=true

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
```

#### prometheus.yml

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'opentelemetry'
    static_configs:
      - targets: ['host.docker.internal:9090', 'host.docker.internal:9091', 
                  'host.docker.internal:9092', 'host.docker.internal:9093', 
                  'host.docker.internal:9094']
```

## 运行指南

1. 启动Docker Compose服务：
```bash
docker-compose up -d
```

2. 运行追踪示例：
```bash
python basic_tracing.py
python http_tracing.py
python experiment1_tracing.py
```

3. 运行指标示例：
```bash
python basic_metrics.py
python advanced_metrics.py
python experiment2_metrics.py
```

4. 运行日志示例：
```bash
python basic_logging.py
python structured_logging.py
python experiment3_logging.py
```

5. 运行关联示例：
```bash
python correlated_signals.py
python experiment4_correlation.py
```

6. 查看结果：
   - Jaeger UI：http://localhost:16686
   - Prometheus UI：http://localhost:9090
   - 控制台日志输出