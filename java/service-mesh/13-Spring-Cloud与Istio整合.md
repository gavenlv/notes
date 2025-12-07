# 13. Spring Cloud 与 Istio 整合

## 1. 整合架构概述

### 1.1 互补性分析

**Spring Cloud 优势：**
- 应用层服务治理
- 配置中心管理
- 声明式 REST 客户端
- 断路器模式实现

**Istio 优势：**
- 基础设施层服务治理
- 细粒度流量控制
- 强大的安全策略
- 丰富的可观测性

### 1.2 整合策略

```
+----------------------+     +----------------------+
|   Spring Cloud Stack  |     |     Istio Stack      |
| +------------------+ |     | +------------------+ |
| | Spring Boot App  | |     | |   Envoy Proxy    | |
| +------------------+ |     | +------------------+ |
| | Spring Cloud     | |     | |      Istio       | |
| |   Components     | |     | |   Components     | |
| +------------------+ |     | +------------------+ |
+----------------------+     +----------------------+
            |                            |
            +-------- 协同工作 -----------+
```

## 2. 服务发现整合

### 2.1 Kubernetes 服务发现

#### 2.1.1 Spring Cloud Kubernetes 配置

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-kubernetes-client</artifactId>
    <version>2.1.0</version>
</dependency>

<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-kubernetes-client-all</artifactId>
    <version>2.1.0</version>
</dependency>
```

#### 2.1.2 应用配置

```java
@SpringBootApplication
@EnableDiscoveryClient
public class ProductServiceApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(ProductServiceApplication.class, args);
    }
}

// application.yml
spring:
  cloud:
    kubernetes:
      discovery:
        all-namespaces: true
        enabled: true
        service-labels:
          environment: production
        primary-port-name: http
      config:
        enabled: true
        sources:
          - namespace: default
            name: product-config
```

### 2.2 服务发现与 Istio 集成

```java
@Configuration
public class ServiceDiscoveryConfig {
    
    @Bean
    @LoadBalanced
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
    
    @Bean
    public ServiceInstanceListSupplier serviceInstanceListSupplier(
            ReactiveDiscoveryClient discoveryClient) {
        return new DiscoveryClientServiceInstanceListSupplier(
            "product-service", discoveryClient);
    }
}

@Service
public class ProductService {
    
    private final RestTemplate restTemplate;
    
    public ProductService(@LoadBalanced RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    
    public Inventory getInventory(String productId) {
        // 通过服务名调用，由 Istio 进行负载均衡
        return restTemplate.getForObject(
            "http://inventory-service/api/inventory/{productId}", 
            Inventory.class, productId);
    }
}
```

## 3. 配置管理整合

### 3.1 ConfigMap 配置管理

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: product-service-config
  namespace: default
data:
  application.yml: |
    server:
      port: 8080
    
    spring:
      datasource:
        url: jdbc:postgresql://postgresql:5432/products
        username: ${DATABASE_USERNAME}
        password: ${DATABASE_PASSWORD}
    
    service:
      max-retries: 3
      timeout: 5000
      cache:
        ttl: 600
        max-size: 1000
    
    management:
      endpoints:
        web:
          exposure:
            include: health,info,metrics,prometheus
      metrics:
        export:
          prometheus:
            enabled: true
```

### 3.2 动态配置更新

```java
@Configuration
@RefreshScope
public class DynamicConfig {
    
    @Value("${service.max-retries:3}")
    private int maxRetries;
    
    @Value("${service.timeout:5000}")
    private int timeout;
    
    @Autowired
    private ConfigurableApplicationContext context;
    
    @EventListener
    public void handleRefreshEvent(EnvironmentChangeEvent event) {
        // 处理配置变更事件
        refreshConfiguration();
    }
    
    private void refreshConfiguration() {
        // 重新加载配置
        context.refresh();
    }
}
```

## 4. 熔断器整合

### 4.1 Resilience4j 集成

#### 4.1.1 依赖配置

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-circuitbreaker-resilience4j</artifactId>
</dependency>
```

#### 4.1.2 熔断器配置

```java
@Configuration
public class CircuitBreakerConfig {
    
    @Bean
    public Customizer<Resilience4JCircuitBreakerFactory> defaultCustomizer() {
        return factory -> factory.configureDefault(id -> {
            return Resilience4JConfigBuilder.of(id)
                .circuitBreakerConfig(CircuitBreakerConfig.custom()
                    .failureRateThreshold(50)
                    .waitDurationInOpenState(Duration.ofMillis(1000))
                    .slidingWindowSize(10)
                    .build())
                .timeLimiterConfig(TimeLimiterConfig.custom()
                    .timeoutDuration(Duration.ofSeconds(5))
                    .build())
                .build();
        });
    }
}

@Service
public class ProductService {
    
    private final CircuitBreakerFactory circuitBreakerFactory;
    private final RestTemplate restTemplate;
    
    public ProductService(CircuitBreakerFactory circuitBreakerFactory,
                         RestTemplate restTemplate) {
        this.circuitBreakerFactory = circuitBreakerFactory;
        this.restTemplate = restTemplate;
    }
    
    public Product getProductWithInventory(String productId) {
        CircuitBreaker circuitBreaker = circuitBreakerFactory.create("inventory-service");
        
        return circuitBreaker.run(() -> {
            Inventory inventory = restTemplate.getForObject(
                "http://inventory-service/api/inventory/{productId}",
                Inventory.class, productId);
            
            Product product = new Product(productId);
            product.setInventory(inventory);
            return product;
            
        }, throwable -> {
            // 降级处理
            return createFallbackProduct(productId);
        });
    }
    
    private Product createFallbackProduct(String productId) {
        Product product = new Product(productId);
        product.setInventory(Inventory.EMPTY);
        return product;
    }
}
```

### 4.2 与 Istio 熔断器协同

```yaml
# Istio DestinationRule 熔断配置
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: inventory-service-dr
spec:
  host: inventory-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1000
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

## 5. 网关整合

### 5.1 Spring Cloud Gateway 配置

```java
@Configuration
public class GatewayConfig {
    
    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("product-service", r -> r
                .path("/api/products/**")
                .filters(f -> f
                    .addRequestHeader("X-Request-Id", "#{T(java.util.UUID).randomUUID().toString()}")
                    .circuitBreaker(config -> config
                        .setName("productCircuitBreaker")
                        .setFallbackUri("forward:/fallback/product"))
                    .retry(config -> config
                        .setRetries(3)
                        .setMethods(HttpMethod.GET, HttpMethod.POST))
                )
                .uri("lb://product-service"))
            .route("user-service", r -> r
                .path("/api/users/**")
                .uri("lb://user-service"))
            .build();
    }
    
    @Bean
    public GlobalFilter customGlobalFilter() {
        return (exchange, chain) -> {
            // 添加全局过滤器逻辑
            ServerHttpRequest request = exchange.getRequest().mutate()
                .header("X-Global-Filter", "enabled")
                .build();
            
            return chain.filter(exchange.mutate().request(request).build());
        };
    }
}
```

### 5.2 与 Istio Gateway 协同

```yaml
# Istio Gateway 配置
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: public-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "api.example.com"
    tls:
      httpsRedirect: true
  - port:
      number: 443
      name: https
      protocol: HTTPS
    hosts:
    - "api.example.com"
    tls:
      mode: SIMPLE
      credentialName: example-cert

# VirtualService 路由配置
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-gateway-vs
spec:
  hosts:
  - "api.example.com"
  gateways:
  - public-gateway
  http:
  - match:
    - uri:
        prefix: "/api"
    route:
    - destination:
        host: spring-cloud-gateway
        port:
          number: 8080
```

## 6. 安全整合

### 6.1 Spring Security 与 Istio 安全策略

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .authorizeRequests()
                .antMatchers("/actuator/health").permitAll()
                .antMatchers("/api/public/**").permitAll()
                .antMatchers("/api/secure/**").authenticated()
                .anyRequest().denyAll()
            .and()
            .oauth2ResourceServer()
                .jwt();
    }
    
    @Bean
    public JwtDecoder jwtDecoder() {
        return NimbusJwtDecoder.withJwkSetUri("https://auth.example.com/.well-known/jwks.json").build();
    }
}
```

### 6.2 Istio 安全策略配置

```yaml
# RequestAuthentication JWT 配置
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: default
spec:
  selector:
    matchLabels:
      app: product-service
  jwtRules:
  - issuer: "https://auth.example.com"
    jwksUri: "https://auth.example.com/.well-known/jwks.json"
    audiences:
    - "api.example.com"

# AuthorizationPolicy 配置
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: product-service-access
  namespace: default
spec:
  selector:
    matchLabels:
      app: product-service
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/api-gateway"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/products/*"]
```

## 7. 可观测性整合

### 7.1 Micrometer 与 Prometheus 集成

```java
@Configuration
public class MetricsConfig {
    
    @Bean
    public MeterRegistry meterRegistry() {
        return new PrometheusMeterRegistry(PrometheusConfig.DEFAULT);
    }
    
    @Bean
    public TimedAspect timedAspect(MeterRegistry registry) {
        return new TimedAspect(registry);
    }
}

@Service
public class ProductService {
    
    private final Counter productRequests;
    private final Timer productQueryTimer;
    private final DistributionSummary productResponseSize;
    
    public ProductService(MeterRegistry registry) {
        this.productRequests = Counter.builder("product.requests")
            .description("Number of product requests")
            .tag("service", "product-service")
            .register(registry);
            
        this.productQueryTimer = Timer.builder("product.query.duration")
            .description("Time taken to query products")
            .register(registry);
            
        this.productResponseSize = DistributionSummary.builder("product.response.size")
            .description("Size of product responses")
            .baseUnit("bytes")
            .register(registry);
    }
    
    @Timed(value = "product.get", description = "Time taken to get product")
    public Product getProduct(String id) {
        productRequests.increment();
        
        return productQueryTimer.record(() -> {
            Product product = productRepository.findById(id);
            
            // 记录响应大小
            productResponseSize.record(calculateResponseSize(product));
            
            return product;
        });
    }
    
    private double calculateResponseSize(Product product) {
        // 计算响应大小逻辑
        return 100.0; // 示例值
    }
}
```

### 7.2 分布式追踪集成

```java
@Configuration
public class TracingConfig {
    
    @Bean
    public Tracer tracer() {
        return new BraveTracer(
            Tracing.newBuilder()
                .localServiceName("product-service")
                .sampler(Sampler.ALWAYS_SAMPLE)
                .build()
                .tracer()
        );
    }
    
    @Bean
    public RestTemplateCustomizer tracingRestTemplateCustomizer(Tracer tracer) {
        return restTemplate -> {
            List<ClientHttpRequestInterceptor> interceptors = 
                new ArrayList<>(restTemplate.getInterceptors());
            interceptors.add(0, new BraveClientHttpRequestInterceptor(
                tracer,
                new DefaultHttpClientParser(),
                brave.http.HttpTracing.create(tracing)
            ));
            restTemplate.setInterceptors(interceptors);
        };
    }
    
    @Bean
    public Filter tracingFilter(Tracer tracer) {
        return new TracingFilter(tracer);
    }
}

@Component
class TracingFilter implements Filter {
    
    private final Tracer tracer;
    
    public TracingFilter(Tracer tracer) {
        this.tracer = tracer;
    }
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, 
                        FilterChain chain) throws IOException, ServletException {
        
        Span span = tracer.nextSpan().name("http-request").start();
        
        try (Tracer.SpanInScope ws = tracer.withSpan(span)) {
            chain.doFilter(request, response);
        } finally {
            span.finish();
        }
    }
}
```

## 8. 配置管理最佳实践

### 8.1 多环境配置

```yaml
# application.yml (基础配置)
spring:
  profiles:
    active: ${PROFILE:default}
  cloud:
    kubernetes:
      config:
        enabled: true
        sources:
          - namespace: ${NAMESPACE:default}
            name: ${APP_NAME}-config

# application-dev.yml
service:
  max-retries: 5
  timeout: 10000
  cache:
    enabled: false

# application-prod.yml
service:
  max-retries: 3
  timeout: 5000
  cache:
    enabled: true
    ttl: 300
    max-size: 5000
```

### 8.2 配置热更新

```java
@Component
public class ConfigRefreshListener {
    
    private static final Logger logger = LoggerFactory.getLogger(ConfigRefreshListener.class);
    
    @EventListener
    public void handleRefreshEvent(RefreshScopeRefreshedEvent event) {
        logger.info("Configuration refreshed for bean: {}", event.getName());
    }
    
    @EventListener
    public void handleEnvironmentChange(EnvironmentChangeEvent event) {
        logger.info("Environment changed: {}", event.getKeys());
        
        // 重新加载相关配置
        reloadAffectedComponents(event.getKeys());
    }
    
    private void reloadAffectedComponents(Set<String> changedKeys) {
        // 根据变更的配置键重新加载相关组件
        if (changedKeys.contains("service.max-retries")) {
            // 重新配置重试逻辑
        }
        
        if (changedKeys.contains("service.timeout")) {
            // 重新配置超时设置
        }
    }
}
```

## 9. 故障排查与调试

### 9.1 健康检查端点

```java
@Component
public class CustomHealthIndicator implements HealthIndicator {
    
    private final RestTemplate restTemplate;
    private final ServiceConfig serviceConfig;
    
    public CustomHealthIndicator(RestTemplate restTemplate, 
                                ServiceConfig serviceConfig) {
        this.restTemplate = restTemplate;
        this.serviceConfig = serviceConfig;
    }
    
    @Override
    public Health health() {
        Map<String, Object> details = new HashMap<>();
        
        // 检查依赖服务
        details.put("inventory-service", checkInventoryService());
        details.put("database", checkDatabase());
        details.put("cache", checkCache());
        
        boolean allHealthy = details.values().stream()
            .allMatch(status -> status.equals("healthy"));
        
        if (allHealthy) {
            return Health.up().withDetails(details).build();
        } else {
            return Health.down().withDetails(details).build();
        }
    }
    
    private String checkInventoryService() {
        try {
            ResponseEntity<String> response = restTemplate.getForEntity(
                "http://inventory-service/actuator/health", String.class);
            
            return response.getStatusCode().is2xxSuccessful() ? "healthy" : "unhealthy";
        } catch (Exception e) {
            return "connection failed: " + e.getMessage();
        }
    }
    
    private String checkDatabase() {
        // 数据库健康检查逻辑
        return "healthy";
    }
    
    private String checkCache() {
        // 缓存健康检查逻辑
        return "healthy";
    }
}
```

### 9.2 调试工具集成

```java
@RestController
@RequestMapping("/debug")
public class DebugController {
    
    private final Environment environment;
    private final DiscoveryClient discoveryClient;
    
    public DebugController(Environment environment, 
                          DiscoveryClient discoveryClient) {
        this.environment = environment;
        this.discoveryClient = discoveryClient;
    }
    
    @GetMapping("/config")
    public Map<String, Object> getConfig() {
        Map<String, Object> config = new HashMap<>();
        
        // 获取所有配置属性
        config.put("activeProfiles", environment.getActiveProfiles());
        config.put("service.max-retries", environment.getProperty("service.max-retries"));
        config.put("service.timeout", environment.getProperty("service.timeout"));
        
        return config;
    }
    
    @GetMapping("/services")
    public List<String> getServices() {
        return discoveryClient.getServices();
    }
    
    @GetMapping("/service-instances/{serviceName}")
    public List<ServiceInstance> getServiceInstances(@PathVariable String serviceName) {
        return discoveryClient.getInstances(serviceName);
    }
}
```

---

**下一章预告：** 第14章将探讨企业级 Service Mesh 部署方案，包括多集群部署、高可用架构、灾难恢复等高级主题。