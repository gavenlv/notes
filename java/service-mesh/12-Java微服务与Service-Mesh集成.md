# 12. Java 微服务与 Service Mesh 集成

## 1. 集成架构概述

### 1.1 无侵入式集成模式

**Sidecar 代理架构：**
```
+----------------+     +----------------+
| Java Application | → | Envoy Sidecar  | → 服务网格
+----------------+     +----------------+
        |                      |
   业务逻辑处理             网络通信处理
```

### 1.2 有侵入式集成模式

**应用层集成架构：**
```
+-----------------------------+
|      Java Application       |
| +-------------------------+ |
| |  Service Mesh Client    | | ← 直接调用网格 API
| +-------------------------+ |
+-----------------------------+
```

## 2. Spring Boot 集成

### 2.1 基础配置

#### 2.1.1 应用配置

```java
@SpringBootApplication
public class ProductServiceApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(ProductServiceApplication.class, args);
    }
    
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplateBuilder()
            .setConnectTimeout(Duration.ofSeconds(5))
            .setReadTimeout(Duration.ofSeconds(10))
            .build();
    }
}
```

#### 2.1.2 Kubernetes 部署配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: product-service
  labels:
    app: product-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: product-service
  template:
    metadata:
      labels:
        app: product-service
      annotations:
        sidecar.istio.io/inject: "true"
    spec:
      containers:
      - name: product-service
        image: product-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "kubernetes"
        - name: MANAGEMENT_ENDPOINTS_WEB_EXPOSURE_INCLUDE
          value: "health,info,metrics"
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

### 2.2 健康检查配置

```java
@Component
public class ServiceHealthIndicator implements HealthIndicator {
    
    private final RestTemplate restTemplate;
    
    public ServiceHealthIndicator(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    
    @Override
    public Health health() {
        try {
            // 检查依赖服务状态
            ResponseEntity<String> response = restTemplate.getForEntity(
                "http://inventory-service/actuator/health", String.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                return Health.up()
                    .withDetail("inventory-service", "available")
                    .build();
            } else {
                return Health.down()
                    .withDetail("inventory-service", "unavailable")
                    .build();
            }
        } catch (Exception e) {
            return Health.down()
                .withDetail("inventory-service", "connection failed")
                .withException(e)
                .build();
        }
    }
}
```

### 2.3 配置管理

```java
@Configuration
@ConfigurationProperties(prefix = "service")
@Data
public class ServiceConfig {
    
    private int maxRetries = 3;
    private Duration timeout = Duration.ofSeconds(5);
    private List<String> allowedOrigins = Arrays.asList("*");
    
    @NestedConfigurationProperty
    private DatabaseConfig database = new DatabaseConfig();
    
    @NestedConfigurationProperty
    private CacheConfig cache = new CacheConfig();
}

@Data
public class DatabaseConfig {
    private String url;
    private String username;
    private String password;
    private int poolSize = 10;
}

@Data
public class CacheConfig {
    private Duration ttl = Duration.ofMinutes(10);
    private int maxSize = 1000;
}
```

## 3. Spring Cloud 集成

### 3.1 Spring Cloud Kubernetes

#### 3.1.1 依赖配置

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-kubernetes-client</artifactId>
    <version>2.1.0</version>
</dependency>

<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-kubernetes-client-config</artifactId>
    <version>2.1.0</version>
</dependency>
```

#### 3.1.2 服务发现配置

```java
@Configuration
@EnableConfigurationProperties(ServiceDiscoveryConfig.class)
public class DiscoveryConfig {
    
    @Bean
    public ServiceInstanceListSupplier serviceInstanceListSupplier(
            ReactiveDiscoveryClient discoveryClient) {
        return new ServiceInstanceListSupplier() {
            @Override
            public Flux<List<ServiceInstance>> get() {
                return discoveryClient.getInstances("product-service");
            }
            
            @Override
            public String getServiceId() {
                return "product-service";
            }
        };
    }
}
```

### 3.2 Spring Cloud Gateway 集成

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
                )
                .uri("lb://product-service"))
            .route("user-service", r -> r
                .path("/api/users/**")
                .uri("lb://user-service"))
            .build();
    }
}
```

## 4. Micronaut 集成

### 4.1 基础配置

```java
@Factory
public class MicronautConfig {
    
    @Singleton
    @ConfigurationProperties("service")
    public ServiceConfiguration serviceConfiguration() {
        return new ServiceConfiguration();
    }
    
    @Singleton
    public HttpClient httpClient(@Named("service") HttpClient httpClient) {
        return httpClient;
    }
}

@ConfigurationProperties("service")
public class ServiceConfiguration {
    
    private int maxRetries = 3;
    private Duration timeout = Duration.ofSeconds(5);
    private List<String> allowedOrigins = Arrays.asList("*");
    
    // getters and setters
}
```

### 4.2 HTTP 客户端集成

```java
@Client(id = "inventory-service")
public interface InventoryClient {
    
    @Get("/api/inventory/{productId}")
    Mono<Inventory> getInventory(@PathVariable String productId);
    
    @Post("/api/inventory")
    Mono<Void> updateInventory(@Body InventoryUpdate update);
}

@Singleton
public class ProductService {
    
    private final InventoryClient inventoryClient;
    private final ServiceConfiguration configuration;
    
    public ProductService(InventoryClient inventoryClient, 
                         ServiceConfiguration configuration) {
        this.inventoryClient = inventoryClient;
        this.configuration = configuration;
    }
    
    public Mono<Product> getProductWithInventory(String productId) {
        return inventoryClient.getInventory(productId)
            .timeout(configuration.getTimeout())
            .retry(configuration.getMaxRetries())
            .map(inventory -> {
                Product product = new Product(productId);
                product.setInventory(inventory);
                return product;
            });
    }
}
```

## 5. Quarkus 集成

### 5.1 基础配置

```java
@ApplicationScoped
public class ProductService {
    
    @ConfigProperty(name = "service.max-retries", defaultValue = "3")
    int maxRetries;
    
    @ConfigProperty(name = "service.timeout", defaultValue = "5")
    Duration timeout;
    
    @RestClient
    InventoryClient inventoryClient;
    
    public Product getProduct(String productId) {
        Inventory inventory = inventoryClient.getInventory(productId);
        Product product = new Product(productId);
        product.setInventory(inventory);
        return product;
    }
}
```

### 5.2 REST 客户端配置

```java
@Path("/api/inventory")
@RegisterRestClient
public interface InventoryClient {
    
    @GET
    @Path("/{productId}")
    Inventory getInventory(@PathParam("productId") String productId);
    
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    void updateInventory(InventoryUpdate update);
}

// application.properties 配置
quarkus.rest-client.inventory-client.url=http://inventory-service:8080
quarkus.rest-client.inventory-client.connect-timeout=5000
quarkus.rest-client.inventory-client.read-timeout=10000
```

## 6. 服务网格客户端集成

### 6.1 Istio Java Client

```java
@Service
public class MeshAwareService {
    
    @Autowired
    private IstioClient istioClient;
    
    public void processRequest(Request request) {
        // 获取服务网格信息
        ServiceEntry serviceEntry = istioClient.getServiceEntry("target-service");
        
        // 执行服务调用
        String result = executeServiceCall(request);
        
        // 记录网格指标
        istioClient.recordMetric("request_processed", "success");
    }
    
    private String executeServiceCall(Request request) {
        // 使用服务网格进行服务调用
        return "result";
    }
}
```

### 6.2 自定义网格感知客户端

```java
@Component
public class MeshAwareHttpClient {
    
    private final RestTemplate restTemplate;
    private final MeshConfig meshConfig;
    
    public MeshAwareHttpClient(RestTemplateBuilder restTemplateBuilder, 
                              MeshConfig meshConfig) {
        this.restTemplate = restTemplateBuilder.build();
        this.meshConfig = meshConfig;
    }
    
    public <T> T executeWithRetry(String serviceName, String path, 
                                 Class<T> responseType, Object... uriVariables) {
        
        String url = buildServiceUrl(serviceName, path);
        
        return RetryTemplate.builder()
            .maxAttempts(meshConfig.getMaxRetries())
            .fixedBackoff(meshConfig.getRetryInterval())
            .retryOn(IOException.class)
            .retryOn(HttpServerErrorException.class)
            .build()
            .execute(context -> {
                return restTemplate.getForObject(url, responseType, uriVariables);
            });
    }
    
    private String buildServiceUrl(String serviceName, String path) {
        return String.format("http://%s%s", serviceName, path);
    }
}
```

## 7. 配置管理最佳实践

### 7.1 ConfigMap 配置

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
      allowed-origins: 
        - "*"
    
    management:
      endpoints:
        web:
          exposure:
            include: health,info,metrics
      endpoint:
        health:
          show-details: always
```

### 7.2 Secret 配置

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: database-secret
  namespace: default
type: Opaque
data:
  username: dXNlcm5hbWU=  # base64 encoded
  password: cGFzc3dvcmQ=  # base64 encoded
```

## 8. 监控与可观测性

### 8.1 Micrometer 指标配置

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
    
    private final Counter productViewCounter;
    private final Timer productQueryTimer;
    
    public ProductService(MeterRegistry registry) {
        this.productViewCounter = Counter.builder("product.views")
            .description("Number of product views")
            .register(registry);
            
        this.productQueryTimer = Timer.builder("product.query.duration")
            .description("Time taken to query products")
            .register(registry);
    }
    
    public Product getProduct(String id) {
        return productQueryTimer.record(() -> {
            Product product = productRepository.findById(id);
            productViewCounter.increment();
            return product;
        });
    }
}
```

### 8.2 分布式追踪配置

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
    public RestTemplateCustomizer restTemplateCustomizer(Tracer tracer) {
        return restTemplate -> {
            List<ClientHttpRequestInterceptor> interceptors = 
                new ArrayList<>(restTemplate.getInterceptors());
            interceptors.add(new BraveClientHttpRequestInterceptor(
                tracer,
                new DefaultHttpClientParser(),
                brave.http.HttpTracing.create(tracing)
            ));
            restTemplate.setInterceptors(interceptors);
        };
    }
}
```

## 9. 安全性配置

### 9.1 mTLS 配置

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: product-service-mtls
  namespace: default
spec:
  selector:
    matchLabels:
      app: product-service
  mtls:
    mode: STRICT
```

### 9.2 安全策略配置

```yaml
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

## 10. 性能优化

### 10.1 连接池优化

```java
@Configuration
public class HttpClientConfig {
    
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplateBuilder()
            .setConnectTimeout(Duration.ofSeconds(5))
            .setReadTimeout(Duration.ofSeconds(10))
            .requestFactory(() -> {
                HttpComponentsClientHttpRequestFactory factory = 
                    new HttpComponentsClientHttpRequestFactory();
                factory.setHttpClient(httpClient());
                return factory;
            })
            .build();
    }
    
    @Bean
    public CloseableHttpClient httpClient() {
        return HttpClients.custom()
            .setMaxConnTotal(100)
            .setMaxConnPerRoute(20)
            .setConnectionTimeToLive(30, TimeUnit.SECONDS)
            .build();
    }
}
```

### 10.2 缓存策略

```java
@Configuration
@EnableCaching
public class CacheConfig {
    
    @Bean
    public CacheManager cacheManager() {
        return new CaffeineCacheManager() {
            @Override
            protected Cache createNativeCaffeineCache(String name) {
                return Caffeine.newBuilder()
                    .expireAfterWrite(10, TimeUnit.MINUTES)
                    .maximumSize(1000)
                    .build();
            }
        };
    }
}

@Service
public class ProductService {
    
    @Cacheable(value = "products", key = "#id")
    public Product getProduct(String id) {
        return productRepository.findById(id);
    }
    
    @CacheEvict(value = "products", key = "#product.id")
    public void updateProduct(Product product) {
        productRepository.save(product);
    }
}
```

---

**下一章预告：** 第13章将深入探讨 Spring Cloud 与 Istio 的深度整合，包括服务发现、配置管理、熔断器等高级集成特性。