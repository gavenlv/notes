# OpenTelemetry学习资源

本目录包含OpenTelemetry的学习资源、教程和最佳实践。OpenTelemetry是一个开源的可观测性框架，用于生成、收集、分析和导出遥测数据（指标、日志和分布式追踪），帮助开发人员更好地理解和监控分布式系统。

## OpenTelemetry概述

OpenTelemetry是由云原生计算基金会(CNCF)托管的开源项目，旨在标准化遥测数据的生成、收集和导出。它提供了一组工具、API和SDK，支持多种编程语言，使开发人员能够轻松地在应用程序中实现可观测性功能。OpenTelemetry正在成为可观测性领域的行业标准，替代了之前的OpenTracing和OpenCensus项目。

## 目录结构

### 基础入门
- OpenTelemetry简介与特点
- 可观测性三大支柱（指标、日志、追踪）
- OpenTelemetry架构与组件
- 安装与配置指南

### 核心概念
- 信号类型（Traces, Metrics, Logs）
- 上下文传播
- 资源与属性
- 采样策略

### 追踪(Tracing)
- Span与Trace概念
- 追踪上下文传播
- 追踪库使用
- 追踪数据导出

### 指标(Metrics)
- 指标类型（Counter, Gauge, Histogram等）
- 指标聚合
- 指标导出
- 指标可视化

### 日志(Logging)
- 日志与追踪关联
- 结构化日志
- 日志收集与导出
- 日志分析

### 仪表盘与可视化
- 集成Prometheus与Grafana
- Jaeger追踪可视化
- 日志聚合与分析
- 自定义仪表盘

### 集成与扩展
- 框架集成（Spring Boot, Django等）
- 数据库监控
- 消息队列监控
- 云服务集成

## 学习路径

### 初学者
1. 了解可观测性基本概念
2. 学习OpenTelemetry核心组件
3. 实现简单的应用程序追踪
4. 配置基本的指标收集

### 进阶学习
1. 掌握上下文传播机制
2. 实现自定义指标和追踪
3. 集成各种后端系统
4. 设计可观测性策略

### 高级应用
1. 实现大规模分布式追踪
2. 优化性能与资源使用
3. 构建自定义可观测性解决方案
4. 参与OpenTelemetry社区贡献

## 常见问题与解决方案

### 配置问题
- SDK配置错误
- 导出器连接问题
- 采样策略配置
- 资源属性设置

### 性能问题
- 高开销追踪
- 内存使用过高
- 网络带宽占用
- 批处理优化

### 数据问题
- 追踪数据丢失
- 指标精度问题
- 日志关联失败
- 数据格式不兼容

## 资源链接

### 官方资源
- [OpenTelemetry官网](https://opentelemetry.io/)
- [官方文档](https://opentelemetry.io/docs/)
- [规范文档](https://github.com/open-telemetry/opentelemetry-specification)
- [GitHub仓库](https://github.com/open-telemetry)

### 学习资源
- [OpenTelemetry入门指南](https://opentelemetry.io/docs/instrumentation/)
- [语言特定文档](https://opentelemetry.io/docs/instrumentation/)
- [示例代码](https://github.com/open-telemetry/opentelemetry-java/tree/main/examples)
- [社区资源](https://github.com/open-telemetry/community)

### 工具与平台
- [Jaeger](https://www.jaegertracing.io/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Zipkin](https://zipkin.io/)

## 代码示例

### Java示例
```java
// 添加依赖
// implementation 'io.opentelemetry:opentelemetry-api:1.25.0'
// implementation 'io.opentelemetry:opentelemetry-sdk:1.25.0'
// implementation 'io.opentelemetry:opentelemetry-exporter-jaeger:1.25.0'
// implementation 'io.opentelemetry:opentelemetry-exporter-prometheus:1.25.0'

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.propagation.W3CTraceContextPropagator;
import io.opentelemetry.context.Scope;
import io.opentelemetry.context.propagation.TextMapPropagator;
import io.opentelemetry.exporter.jaeger.JaegerGrpcSpanExporter;
import io.opentelemetry.exporter.prometheus.PrometheusHttpServer;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.metrics.SdkMeterProvider;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.semconv.resource.attributes.ResourceAttributes;

public class OpenTelemetryExample {
    private static final String INSTRUMENTATION_NAME = OpenTelemetryExample.class.getName();
    private static final Tracer tracer = OpenTelemetryExample.initializeOpenTelemetry().getTracer(INSTRUMENTATION_NAME);
    
    public static void main(String[] args) {
        // 创建一个span
        Span span = tracer.spanBuilder("main-operation").startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // 在span范围内执行业务逻辑
            doWork();
        } finally {
            span.end();
        }
        
        // 等待一段时间确保span被导出
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            // 忽略异常
        }
    }
    
    private static void doWork() {
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
            .put(ResourceAttributes.SERVICE_NAME, "example-service")
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
        
        // 创建指标提供者
        PrometheusHttpServer prometheusExporter = PrometheusHttpServer.builder()
            .setPort(9090)
            .build();
        
        SdkMeterProvider meterProvider = SdkMeterProvider.builder()
            .registerMetricReader(prometheusExporter)
            .setResource(resource)
            .build();
        
        // 创建OpenTelemetry实例
        return OpenTelemetrySdk.builder()
            .setTracerProvider(tracerProvider)
            .setMeterProvider(meterProvider)
            .setPropagators(TextMapPropagator.composite(W3CTraceContextPropagator.getInstance()))
            .buildAndRegisterGlobal();
    }
}
```

### Python示例
```python
# 安装依赖
# pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger opentelemetry-exporter-prometheus opentelemetry-instrumentation-requests

from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import time
import random

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

histogram = meter.create_histogram(
    "request_duration",
    description="Request duration in seconds",
    unit="s"
)

# 自动检测requests库
RequestsInstrumentor().instrument()

def process_request():
    # 创建一个span
    with tracer.start_as_current_span("process-request") as span:
        # 添加属性
        span.set_attribute("operation.name", "process")
        span.set_attribute("operation.type", "business-logic")
        
        # 添加事件
        span.add_event("Starting request processing")
        
        # 模拟处理时间
        processing_time = random.uniform(0.1, 0.5)
        time.sleep(processing_time)
        
        # 记录指标
        counter.add(1, {"endpoint": "/api/process"})
        histogram.record(processing_time, {"endpoint": "/api/process"})
        
        # 添加事件
        span.add_event("Request processing completed")
        
        # 模拟可能的错误
        if random.random() < 0.1:
            span.record_exception(Exception("Random processing error"))
            raise Exception("Random processing error")

def main():
    print("Starting OpenTelemetry example...")
    
    # 模拟多个请求
    for i in range(10):
        try:
            process_request()
            print(f"Request {i+1} processed successfully")
        except Exception as e:
            print(f"Request {i+1} failed: {str(e)}")
        
        time.sleep(1)
    
    print("Example completed. Check Jaeger UI at http://localhost:16686")
    print("Check Prometheus metrics at http://localhost:9090")

if __name__ == "__main__":
    main()
```

### JavaScript/Node.js示例
```javascript
// 安装依赖
// npm install @opentelemetry/api @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node @opentelemetry/exporter-jaeger @opentelemetry/exporter-prometheus

const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { JaegerExporter } = require('@opentelemetry/exporter-jaeger');
const { PrometheusExporter } = require('@opentelemetry/exporter-prometheus');
const { trace, metrics } = require('@opentelemetry/api');
const express = require('express');
const axios = require('axios');

// 初始化OpenTelemetry
const sdk = new NodeSDK({
  traceExporter: new JaegerExporter({
    endpoint: 'http://localhost:14268/api/traces',
  }),
  metricReader: new PrometheusExporter({
    port: 9090,
  }),
  instrumentations: [getNodeAutoInstrumentations()],
  serviceName: 'example-service',
});

// 启动SDK
sdk.start();

// 获取tracer和meter
const tracer = trace.getTracer('example-service');
const meter = metrics.getMeter('example-service');

// 创建指标
const requestCounter = meter.createCounter('requests', {
  description: 'Number of requests',
});

const responseTimeHistogram = meter.createHistogram('response_time', {
  description: 'Response time in milliseconds',
  unit: 'ms',
});

// 创建Express应用
const app = express();
const port = 3000;

// 中间件：添加追踪和指标
app.use((req, res, next) => {
  const span = tracer.startSpan(`${req.method} ${req.path}`);
  
  // 记录请求开始时间
  const startTime = Date.now();
  
  // 添加span属性
  span.setAttributes({
    'http.method': req.method,
    'http.url': req.url,
    'http.target': req.path,
  });
  
  // 在响应结束时记录指标和结束span
  res.on('finish', () => {
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    // 记录指标
    requestCounter.add(1, {
      method: req.method,
      path: req.path,
      status_code: res.statusCode.toString(),
    });
    
    responseTimeHistogram.record(duration, {
      method: req.method,
      path: req.path,
    });
    
    // 添加响应属性
    span.setAttributes({
      'http.status_code': res.statusCode,
    });
    
    // 结束span
    span.end();
  });
  
  next();
});

// 路由：主页
app.get('/', (req, res) => {
  const span = trace.getActiveSpan();
  span.addEvent('Handling home page request');
  
  res.send('Hello, OpenTelemetry!');
});

// 路由：模拟API调用
app.get('/api/data', async (req, res) => {
  const span = trace.getActiveSpan();
  span.addEvent('Fetching external data');
  
  try {
    // 创建子span用于外部API调用
    const apiSpan = tracer.startSpan('external-api-call');
    
    try {
      // 模拟外部API调用
      const response = await axios.get('https://jsonplaceholder.typicode.com/posts/1');
      
      apiSpan.setAttributes({
        'http.status_code': response.status,
        'api.url': 'https://jsonplaceholder.typicode.com/posts/1',
      });
      
      res.json(response.data);
    } finally {
      apiSpan.end();
    }
  } catch (error) {
    span.recordException(error);
    res.status(500).json({ error: 'Failed to fetch data' });
  }
});

// 路由：模拟错误
app.get('/api/error', (req, res) => {
  const span = trace.getActiveSpan();
  
  try {
    // 模拟错误
    throw new Error('Something went wrong');
  } catch (error) {
    span.recordException(error);
    span.setStatus({ code: trace.SpanStatusCode.ERROR, message: error.message });
    res.status(500).json({ error: error.message });
  }
});

// 启动服务器
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
  console.log(`Check traces at http://localhost:16686`);
  console.log(`Check metrics at http://localhost:9090`);
});

// 优雅关闭
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('OpenTelemetry terminated'))
    .catch((error) => console.error('Error terminating OpenTelemetry', error))
    .finally(() => process.exit(0));
});
```

### Go示例
```go
// 添加依赖
// go get go.opentelemetry.io/otel
// go get go.opentelemetry.io/otel/exporters/jaeger
// go get go.opentelemetry.io/otel/exporters/prometheus
// go get go.opentelemetry.io/otel/sdk
// go get go.opentelemetry.io/otel/trace
// go get go.opentelemetry.io/otel/metric
// go get go.opentelemetry.io/otel/attribute

package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/jaeger"
	"go.opentelemetry.io/otel/exporters/prometheus"
	"go.opentelemetry.io/otel/metric"
	"go.opentelemetry.io/otel/metric/global"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/metric"
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

	// 创建Prometheus导出器
	promExporter, err := prometheus.New()
	if err != nil {
		log.Fatalf("failed to create Prometheus exporter: %v", err)
	}

	// 创建资源
	res, err := resource.New(context.Background(),
		resource.WithAttributes(
			semconv.ServiceNameKey.String("example-service"),
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

	// 创建指标提供者
	mp := metric.NewMeterProvider(
		metric.WithResource(res),
		metric.WithReader(promExporter),
	)

	// 注册提供者
	otel.SetTracerProvider(tp)
	global.SetMeterProvider(mp)
	otel.SetTextMapPropagator(propagation.TraceContext{})

	// 返回关闭函数
	return func() {
		ctx, cancel := context.WithTimeout(context.Background(), time.Second*5)
		defer cancel()
		if err := tp.Shutdown(ctx); err != nil {
			log.Printf("failed to shutdown TracerProvider: %v", err)
		}
		if err := mp.Shutdown(ctx); err != nil {
			log.Printf("failed to shutdown MeterProvider: %v", err)
		}
	}
}

func main() {
	// 初始化提供者
	shutdown := initProvider()
	defer shutdown()

	// 获取tracer和meter
	tracer := otel.Tracer("example-service")
	meter := global.Meter("example-service")

	// 创建指标
	requestCounter, err := meter.Int64Counter("requests", metric.WithDescription("Number of requests"))
	if err != nil {
		log.Fatalf("failed to create counter: %v", err)
	}

	responseTimeHistogram, err := meter.Float64Histogram("response_time", metric.WithDescription("Response time in seconds"))
	if err != nil {
		log.Fatalf("failed to create histogram: %v", err)
	}

	// 创建HTTP处理器
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// 从请求中提取上下文
		ctx := otel.GetTextMapPropagator().Extract(r.Context(), propagation.HeaderCarrier(r.Header))

		// 创建span
		ctx, span := tracer.Start(ctx, "http-request")
		defer span.End()

		// 添加属性
		span.SetAttributes(
			attribute.String("http.method", r.Method),
			attribute.String("http.url", r.URL.String()),
		)

		// 记录开始时间
		startTime := time.Now()

		// 添加事件
		span.AddEvent("Processing request")

		// 模拟处理
		time.Sleep(time.Millisecond * time.Duration(100+time.Now().UnixNano()%500))

		// 记录指标
		requestCounter.Add(ctx, 1, metric.WithAttributes(attribute.String("path", r.URL.Path)))
		responseTimeHistogram.Record(ctx, time.Since(startTime).Seconds(), metric.WithAttributes(attribute.String("path", r.URL.Path)))

		// 返回响应
		fmt.Fprintf(w, "Hello, OpenTelemetry! Request processed in %v", time.Since(startTime))
	})

	http.HandleFunc("/api/data", func(w http.ResponseWriter, r *http.Request) {
		// 从请求中提取上下文
		ctx := otel.GetTextMapPropagator().Extract(r.Context(), propagation.HeaderCarrier(r.Header))

		// 创建span
		ctx, span := tracer.Start(ctx, "api-data-request")
		defer span.End()

		// 添加属性
		span.SetAttributes(
			attribute.String("http.method", r.Method),
			attribute.String("http.url", r.URL.String()),
		)

		// 添加事件
		span.AddEvent("Fetching data")

		// 创建子span用于外部API调用
		ctx, apiSpan := tracer.Start(ctx, "external-api-call")
		defer apiSpan.End()

		// 模拟外部API调用
		time.Sleep(time.Millisecond * 200)

		// 添加属性
		apiSpan.SetAttributes(
			attribute.String("api.url", "https://api.example.com/data"),
		)

		// 返回响应
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"id": 1, "name": "Example Data", "timestamp": "%s"}`, time.Now().Format(time.RFC3339))
	})

	// 启动HTTP服务器
	fmt.Println("Starting server on :8080")
	fmt.Println("Check traces at http://localhost:16686")
	fmt.Println("Check metrics at http://localhost:9090/metrics")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
```

### Spring Boot集成示例
```java
// 添加依赖
// implementation 'io.opentelemetry:opentelemetry-api:1.25.0'
// implementation 'io.opentelemetry:opentelemetry-sdk:1.25.0'
// implementation 'io.opentelemetry:opentelemetry-exporter-jaeger:1.25.0'
// implementation 'io.opentelemetry.instrumentation:opentelemetry-spring-boot-starter:1.25.0-alpha'
// implementation 'io.opentelemetry:opentelemetry-exporter-prometheus:1.25.0'

package com.example.opentelemetrydemo;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.metrics.LongCounter;
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import javax.annotation.PostConstruct;
import java.util.Random;

@SpringBootApplication
@RestController
public class OpenTelemetryDemoApplication {
    
    private final Tracer tracer;
    private final LongCounter requestCounter;
    private final RestTemplate restTemplate;
    
    @Autowired
    public OpenTelemetryDemoApplication(OpenTelemetry openTelemetry) {
        this.tracer = openTelemetry.getTracer(OpenTelemetryDemoApplication.class.getName());
        this.restTemplate = new RestTemplate();
        
        // 创建指标
        Meter meter = openTelemetry.getMeter(OpenTelemetryDemoApplication.class.getName());
        this.requestCounter = meter.counterBuilder("requests")
                .setDescription("Number of requests")
                .build();
    }
    
    public static void main(String[] args) {
        SpringApplication.run(OpenTelemetryDemoApplication.class, args);
    }
    
    @GetMapping("/")
    public String home() {
        Span span = tracer.spanBuilder("home").startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // 记录请求计数
            requestCounter.add(1, Attributes.builder()
                    .put("endpoint", "/")
                    .put("method", "GET")
                    .build());
            
            // 添加事件
            span.addEvent("Processing home request");
            
            // 模拟处理时间
            Thread.sleep(new Random().nextInt(100));
            
            return "Hello, OpenTelemetry!";
        } catch (InterruptedException e) {
            span.recordException(e);
            return "Error: " + e.getMessage();
        } finally {
            span.end();
        }
    }
    
    @GetMapping("/api/data/{id}")
    public String getData(@PathVariable String id) {
        Span span = tracer.spanBuilder("get-data").startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // 记录请求计数
            requestCounter.add(1, Attributes.builder()
                    .put("endpoint", "/api/data/{id}")
                    .put("method", "GET")
                    .put("data_id", id)
                    .build());
            
            // 添加属性
            span.setAttribute("data.id", id);
            
            // 添加事件
            span.addEvent("Fetching data");
            
            // 创建子span用于外部API调用
            Span apiSpan = tracer.spanBuilder("external-api-call").startSpan();
            try (Scope apiScope = apiSpan.makeCurrent()) {
                // 模拟外部API调用
                Thread.sleep(new Random().nextInt(200) + 100);
                
                // 添加属性
                apiSpan.setAttribute("api.url", "https://api.example.com/data/" + id);
                
                // 返回模拟数据
                return "{\"id\":\"" + id + "\",\"name\":\"Example Data\",\"value\":" + new Random().nextInt(100) + "}";
            } finally {
                apiSpan.end();
            }
        } catch (InterruptedException e) {
            span.recordException(e);
            return "Error: " + e.getMessage();
        } finally {
            span.end();
        }
    }
    
    @GetMapping("/api/chain")
    public String chainRequest() {
        Span span = tracer.spanBuilder("chain-request").startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // 记录请求计数
            requestCounter.add(1, Attributes.builder()
                    .put("endpoint", "/api/chain")
                    .put("method", "GET")
                    .build());
            
            // 添加事件
            span.addEvent("Starting chain request");
            
            // 调用本地API
            String result1 = restTemplate.getForObject("http://localhost:8080/api/data/1", String.class);
            
            // 添加事件
            span.addEvent("First API call completed");
            
            // 再次调用本地API
            String result2 = restTemplate.getForObject("http://localhost:8080/api/data/2", String.class);
            
            // 添加事件
            span.addEvent("Second API call completed");
            
            return "{\"result1\":" + result1 + ",\"result2\":" + result2 + "}";
        } finally {
            span.end();
        }
    }
    
    @GetMapping("/api/error")
    public String error() {
        Span span = tracer.spanBuilder("error-endpoint").startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // 记录请求计数
            requestCounter.add(1, Attributes.builder()
                    .put("endpoint", "/api/error")
                    .put("method", "GET")
                    .build());
            
            // 添加事件
            span.addEvent("Simulating error");
            
            // 模拟错误
            throw new RuntimeException("Simulated error for demonstration");
        } finally {
            span.end();
        }
    }
}
```

## 最佳实践

### 追踪设计
- 设计有意义的span名称和属性
- 使用适当的span类型（客户端、服务器、内部等）
- 避免过度追踪和性能影响
- 实现适当的采样策略

### 指标设计
- 选择合适的指标类型
- 使用有意义的标签和属性
- 避免高基数指标
- 定期评估指标有效性

### 日志关联
- 在日志中包含追踪ID和span ID
- 使用结构化日志格式
- 确保日志级别适当
- 避免敏感信息泄露

### 性能优化
- 使用批处理导出器
- 配置适当的采样率
- 优化资源使用
- 监控OpenTelemetry自身性能

### 部署与运维
- 使用配置管理工具
- 实施适当的资源限制
- 设置监控和报警
- 定期备份配置

## 贡献指南

1. 添加新的学习资源时，请确保：
   - 内容准确且实用
   - 包含实际示例和代码
   - 注明来源和参考链接

2. 在本README.md中更新目录结构

## 注意事项

- OpenTelemetry仍在快速发展中，API可能会发生变化
- 不同语言的实现可能存在差异
- 生产环境部署需要考虑性能和资源消耗
- 注意数据隐私和合规性要求
- 定期更新OpenTelemetry库和组件