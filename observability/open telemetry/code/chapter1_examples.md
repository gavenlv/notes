# 第1章示例代码

## 1.6 第一个OpenTelemetry应用

### Python示例

#### basic_tracing.py

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time

# 设置资源
resource = Resource(attributes={
    SERVICE_NAME: "example-service"
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
from opentelemetry.exporter.prometheus import PrometheusMetricReader
reader = PrometheusMetricReader(port=9090)
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

# 获取meter
meter = metrics.get_meter(__name__)

# 创建指标
counter = meter.create_counter(
    "requests",
    description="Number of requests"
)

def do_work():
    # 创建一个span
    with tracer.start_as_current_span("do-work") as span:
        # 添加属性
        span.set_attribute("operation.name", "do_work")
        
        # 添加事件
        span.add_event("Starting work")
        
        # 模拟工作
        time.sleep(1)
        
        # 记录指标
        counter.add(1)
        
        # 添加事件
        span.add_event("Work completed")

if __name__ == "__main__":
    do_work()
    print("Work completed. Check Jaeger UI at http://localhost:16686")
    print("Check Prometheus metrics at http://localhost:9090")
```

#### enhanced_tracing.py

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time
import random

# 设置资源，包含更多属性
resource = Resource(attributes={
    SERVICE_NAME: "enhanced-service",
    SERVICE_VERSION: "1.0.0",
    "environment": "development",
    "instance.id": "instance-1"
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
from opentelemetry.exporter.prometheus import PrometheusMetricReader
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

def process_request(request_id):
    # 创建一个span
    with tracer.start_as_current_span("process-request") as span:
        # 添加属性
        span.set_attribute("request.id", request_id)
        span.set_attribute("operation.type", "business-logic")
        
        # 添加事件
        span.add_event("Starting request processing")
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 模拟处理时间
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)
            
            # 记录指标
            request_counter.add(1, {"endpoint": "/api/process", "status": "success"})
            response_time_histogram.record(processing_time, {"endpoint": "/api/process"})
            
            # 添加事件
            span.add_event("Request processing completed")
            
            # 模拟可能的错误
            if random.random() < 0.1:
                raise Exception("Random processing error")
                
            return {"status": "success", "request_id": request_id}
            
        except Exception as e:
            # 记录异常
            span.record_exception(e)
            
            # 记录指标
            request_counter.add(1, {"endpoint": "/api/process", "status": "error"})
            
            # 重新抛出异常
            raise

def main():
    print("Starting enhanced OpenTelemetry example...")
    
    # 模拟多个请求
    for i in range(10):
        try:
            result = process_request(f"req-{i+1}")
            print(f"Request {i+1} processed successfully: {result}")
        except Exception as e:
            print(f"Request {i+1} failed: {str(e)}")
        
        time.sleep(0.5)
    
    print("Example completed. Check Jaeger UI at http://localhost:16686")
    print("Check Prometheus metrics at http://localhost:9090")

if __name__ == "__main__":
    main()
```

### Java示例

#### BasicTracing.java

```java
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import io.opentelemetry.exporter.jaeger.JaegerGrpcSpanExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.semconv.resource.attributes.ResourceAttributes;

public class BasicTracing {
    private static final String INSTRUMENTATION_NAME = BasicTracing.class.getName();
    
    public static void main(String[] args) {
        // 初始化OpenTelemetry
        OpenTelemetry openTelemetry = initializeOpenTelemetry();
        
        // 获取tracer
        Tracer tracer = openTelemetry.getTracer(INSTRUMENTATION_NAME);
        
        // 创建一个span
        Span span = tracer.spanBuilder("main-operation").startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // 在span范围内执行业务逻辑
            doWork(tracer);
        } finally {
            span.end();
        }
        
        // 等待一段时间确保span被导出
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            // 忽略异常
        }
        
        System.out.println("Work completed. Check Jaeger UI at http://localhost:16686");
    }
    
    private static void doWork(Tracer tracer) {
        // 创建子span
        Span childSpan = tracer.spanBuilder("doWork").startSpan();
        
        try (Scope scope = childSpan.makeCurrent()) {
            // 模拟一些工作
            Thread.sleep(1000);
            
            // 添加事件
            childSpan.addEvent("Doing some work");
            
            // 添加属性
            childSpan.setAttribute("work.type", "computation");
            
            // 模拟更多工作
            Thread.sleep(500);
        } catch (InterruptedException e) {
            childSpan.recordException(e);
        } finally {
            childSpan.end();
        }
    }
    
    private static OpenTelemetry initializeOpenTelemetry() {
        // 创建资源
        Resource resource = Resource.getDefault()
            .toBuilder()
            .put(ResourceAttributes.SERVICE_NAME, "basic-java-service")
            .put(ResourceAttributes.SERVICE_VERSION, "1.0.0")
            .build();
        
        // 创建Jaeger导出器
        JaegerGrpcSpanExporter jaegerExporter = JaegerGrpcSpanExporter.builder()
            .setEndpoint("http://localhost:14250")
            .build();
        
        // 创建追踪提供者
        SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
            .addSpanProcessor(BatchSpanProcessor.builder(jaegerExporter).build())
            .setResource(resource)
            .build();
        
        // 创建OpenTelemetry实例
        return OpenTelemetrySdk.builder()
            .setTracerProvider(tracerProvider)
            .buildAndRegisterGlobal();
    }
}
```

### JavaScript/Node.js示例

#### basic-tracing.js

```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { JaegerExporter } = require('@opentelemetry/exporter-jaeger');

// 初始化OpenTelemetry
const sdk = new NodeSDK({
  traceExporter: new JaegerExporter({
    endpoint: 'http://localhost:14268/api/traces',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
  serviceName: 'basic-node-service',
});

// 启动SDK
sdk.start();

const { trace } = require('@opentelemetry/api');
const tracer = trace.getTracer('basic-node-service');

function doWork() {
  // 创建一个span
  const span = tracer.startSpan('do-work');
  
  try {
    // 添加属性
    span.setAttributes({
      'work.type': 'computation',
      'work.complexity': 'medium',
    });
    
    // 添加事件
    span.addEvent('Starting work');
    
    // 模拟工作
    setTimeout(() => {
      span.addEvent('Work completed');
      span.end();
      
      console.log('Work completed. Check Jaeger UI at http://localhost:16686');
    }, 1500);
    
  } catch (error) {
    span.recordException(error);
    span.end();
    throw error;
  }
}

// 执行工作
doWork();

// 优雅关闭
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('OpenTelemetry terminated'))
    .catch((error) => console.error('Error terminating OpenTelemetry', error))
    .finally(() => process.exit(0));
});
```

### Go示例

#### basic-tracing.go

```go
package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/jaeger"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.4.0"
	"go.opentelemetry.io/otel/trace"
)

func initProvider() func() {
	// 创建Jaeger导出器
	exp, err := jaeger.New(jaeger.WithCollectorEndpoint(jaeger.WithEndpoint("http://localhost:14268/api/traces")))
	if err != nil {
		log.Fatalf("failed to create Jaeger exporter: %v", err)
	}

	// 创建资源
	res, err := resource.New(context.Background(),
		resource.WithAttributes(
			semconv.ServiceNameKey.String("basic-go-service"),
			semconv.ServiceVersionKey.String("1.0.0"),
		),
	)
	if err != nil {
		log.Fatalf("failed to create resource: %v", err)
	}

	// 创建追踪提供者
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exp),
		sdktrace.WithResource(res),
	)

	// 注册提供者
	otel.SetTracerProvider(tp)
	otel.SetTextMapPropagator(propagation.TraceContext{})

	// 返回关闭函数
	return func() {
		ctx, cancel := context.WithTimeout(context.Background(), time.Second*5)
		defer cancel()
		if err := tp.Shutdown(ctx); err != nil {
			log.Printf("failed to shutdown TracerProvider: %v", err)
		}
	}
}

func doWork(tracer trace.Tracer) {
	// 创建一个span
	ctx, span := tracer.Start(context.Background(), "do-work")
	defer span.End()

	// 添加属性
	span.SetAttributes(
		attribute.String("work.type", "computation"),
		attribute.Int("work.complexity", 5),
	)

	// 添加事件
	span.AddEvent("Starting work", trace.WithAttributes(attribute.String("phase", "initialization")))

	// 模拟工作
	time.Sleep(1 * time.Second)

	// 添加事件
	span.AddEvent("Work completed", trace.WithAttributes(attribute.String("phase", "finalization")))
}

func main() {
	// 初始化提供者
	shutdown := initProvider()
	defer shutdown()

	// 获取tracer
	tracer := otel.Tracer("basic-go-service")

	// 执行工作
	doWork(tracer)

	fmt.Println("Work completed. Check Jaeger UI at http://localhost:16686")
}
```

## 1.7 实验与验证

### 实验1：创建第一个追踪

#### experiment1.py

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time

def experiment1():
    print("实验1：创建第一个追踪")
    
    # 设置资源
    resource = Resource(attributes={
        SERVICE_NAME: "experiment1-service"
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
    
    # 创建一个span
    with tracer.start_as_current_span("experiment1-operation") as span:
        # 添加属性
        span.set_attribute("experiment.name", "第一个追踪实验")
        span.set_attribute("experiment.step", 1)
        
        # 添加事件
        span.addEvent("实验开始")
        
        # 模拟工作
        time.sleep(1)
        
        # 添加事件
        span.addEvent("实验完成")
    
    print("实验1完成。请在Jaeger UI中查看追踪数据：http://localhost:16686")
    
    # 等待span被导出
    time.sleep(2)

if __name__ == "__main__":
    experiment1()
```

### 实验2：添加指标收集

#### experiment2.py

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time

def experiment2():
    print("实验2：添加指标收集")
    
    # 设置资源
    resource = Resource(attributes={
        SERVICE_NAME: "experiment2-service"
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
    reader = PrometheusMetricReader(port=9091)  # 使用不同端口避免冲突
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)
    
    # 获取meter
    meter = metrics.get_meter(__name__)
    
    # 创建指标
    counter = meter.create_counter(
        "experiment2_requests",
        description="实验2的请求数量"
    )
    
    # 创建一个span并记录指标
    with tracer.start_as_current_span("experiment2-operation") as span:
        # 添加属性
        span.set_attribute("experiment.name", "指标收集实验")
        span.set_attribute("experiment.step", 2)
        
        # 添加事件
        span.addEvent("实验开始")
        
        # 记录指标
        counter.add(1, {"endpoint": "/experiment2", "method": "GET"})
        
        # 模拟工作
        time.sleep(1)
        
        # 再次记录指标
        counter.add(1, {"endpoint": "/experiment2", "method": "POST"})
        
        # 添加事件
        span.addEvent("实验完成")
    
    print("实验2完成。")
    print("请在Jaeger UI中查看追踪数据：http://localhost:16686")
    print("请在Prometheus中查看指标数据：http://localhost:9091")
    
    # 等待span被导出
    time.sleep(2)

if __name__ == "__main__":
    experiment2()
```

### 实验3：添加资源属性

#### experiment3.py

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import time
import os

def experiment3():
    print("实验3：添加资源属性")
    
    # 设置资源，包含更多属性
    resource = Resource(attributes={
        SERVICE_NAME: "experiment3-service",
        SERVICE_VERSION: "1.0.0",
        "environment": "development",
        "instance.id": os.getenv("INSTANCE_ID", "unknown"),
        "host.name": os.getenv("HOSTNAME", "localhost"),
        "deployment.region": "us-west-2",
        "team.name": "observability"
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
    
    # 创建一个span
    with tracer.start_as_current_span("experiment3-operation") as span:
        # 添加属性
        span.set_attribute("experiment.name", "资源属性实验")
        span.set_attribute("experiment.step", 3)
        
        # 添加事件
        span.addEvent("实验开始")
        
        # 模拟工作
        time.sleep(1)
        
        # 添加事件
        span.addEvent("实验完成")
    
    print("实验3完成。请在Jaeger UI中查看追踪数据和资源属性：http://localhost:16686")
    
    # 等待span被导出
    time.sleep(2)

if __name__ == "__main__":
    experiment3()
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
      - targets: ['host.docker.internal:9090', 'host.docker.internal:9091']
```

## 运行指南

1. 启动Docker Compose服务：
```bash
docker-compose up -d
```

2. 运行Python示例：
```bash
python basic_tracing.py
python enhanced_tracing.py
python experiment1.py
python experiment2.py
python experiment3.py
```

3. 运行Java示例：
```bash
javac -cp "opentelemetry-api-1.25.0.jar:opentelemetry-sdk-1.25.0.jar:opentelemetry-exporter-jaeger-1.25.0.jar:opentelemetry-sdk-trace-1.25.0.jar:opentelemetry-sdk-common-1.25.0.jar:opentelemetry-api-logs-1.25.0.jar" BasicTracing.java
java -cp ".:opentelemetry-api-1.25.0.jar:opentelemetry-sdk-1.25.0.jar:opentelemetry-exporter-jaeger-1.25.0.jar:opentelemetry-sdk-trace-1.25.0.jar:opentelemetry-sdk-common-1.25.0.jar:opentelemetry-api-logs-1.25.0.jar" BasicTracing
```

4. 运行JavaScript示例：
```bash
node basic-tracing.js
```

5. 运行Go示例：
```bash
go mod init basic-tracing
go get go.opentelemetry.io/otel
go get go.opentelemetry.io/otel/exporters/jaeger
go get go.opentelemetry.io/otel/sdk
go get go.opentelemetry.io/otel/trace
go get go.opentelemetry.io/otel/attribute
go get go.opentelemetry.io/otel/propagation
go get go.opentelemetry.io/otel/sdk/resource
go get go.opentelemetry.io/otel/semconv/v1.4.0
go run basic-tracing.go
```

6. 查看结果：
   - Jaeger UI：http://localhost:16686
   - Prometheus UI：http://localhost:9090