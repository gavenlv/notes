# 05. Java 应用集成与最佳实践

## 1. Java 应用与 Service Mesh 集成模式

### 1.1 无侵入式集成

#### 1.1.1 Sidecar 代理模式

**优势：**
- 无需修改应用代码
- 语言无关性
- 快速部署

**部署配置示例：**
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
```

#### 1.1.2 自动 Sidecar 注入

**命名空间标签配置：**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: product
  labels:
    istio-injection: enabled
```

### 1.2 有侵入式集成

#### 1.2.1 Istio Java Client

```java
// 添加依赖
<dependency>
    <groupId>io.istio</groupId>
    <artifactId>istio-client</artifactId>
    <version>1.0.0</version>
</dependency>

// 使用 Istio Java Client
@Service
public class ProductService {
    
    @Autowired
    private IstioClient istioClient;
    
    public void updateProduct(Product product) {
        // 获取服务网格信息
        ServiceEntry serviceEntry = istioClient.getServiceEntry("inventory-service");
        
        // 执行服务调用
        String result = restTemplate.postForObject(
            "http://inventory-service/api/inventory", 
            product, String.class
        );
        
        // 记录网格指标
        istioClient.recordMetric("product_update", "success");
    }
}
```

## 2. Spring Cloud 与 Service Mesh 集成

### 2.1 Spring Cloud Kubernetes 集成

#### 2.1.1 配置管理

```java
// Spring Cloud Kubernetes 配置
@Configuration
@EnableConfigurationProperties(ProductProperties.class)
public class ProductConfig {
    
    @Bean
    @ConfigurationProperties(prefix = "product")
    public ProductProperties productProperties() {
        return new ProductProperties();
    }
    
    @Bean
    public ConfigMapPropertySourceLocator configMapPropertySourceLocator() {
        return new ConfigMapPropertySourceLocator(new KubernetesClientAutoConfig().kubernetesClient());
    }
}

// 配置类
@Data
@ConfigurationProperties(prefix = "product")
public class ProductProperties {
    private int maxRetries = 3;
    private Duration timeout = Duration.ofSeconds(5);
    private List<String> allowedCategories = Arrays.asList("electronics", "clothing");
}
```

#### 2.1.2 服务发现集成

```java
// 使用 Kubernetes 服务发现
@Service
public class InventoryClient {
    
    private final RestTemplate restTemplate;
    private final KubernetesClient kubernetesClient;
    
    public InventoryClient(RestTemplateBuilder restTemplateBuilder, 
                          KubernetesClient kubernetesClient) {
        this.restTemplate = restTemplateBuilder.build();
        this.kubernetesClient = kubernetesClient;
    }
    
    public Inventory getInventory(String productId) {
        // 通过服务名调用
        String url = "http://inventory-service/api/inventory/" + productId;
        return restTemplate.getForObject(url, Inventory.class);
    }
}
```

### 2.2 Spring Boot 健康检查集成

```java
// 健康检查端点
@Component
public class ProductHealthIndicator implements HealthIndicator {
    
    private final InventoryClient inventoryClient;
    
    public ProductHealthIndicator(InventoryClient inventoryClient) {
        this.inventoryClient = inventoryClient;
    }
    
    @Override
    public Health health() {
        try {
            // 检查依赖服务健康状态
            inventoryClient.getInventory("test");
            return Health.up()
                .withDetail("inventory-service", "available")
                .build();
        } catch (Exception e) {
            return Health.down()
                .withDetail("inventory-service", "unavailable")
                .withException(e)
                .build();
        }
    }
}

// 应用配置
@SpringBootApplication
public class ProductServiceApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(ProductServiceApplication.class, args);
    }
    
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
    
    @Bean
    public KubernetesClient kubernetesClient() {
        return new DefaultKubernetesClient();
    }
}
```

## 3. Micronaut 与 Service Mesh 集成

### 3.1 Micronaut Kubernetes 支持

#### 3.1.1 配置管理

```java
// Micronaut 配置
@ConfigurationProperties("product")
public class ProductConfiguration {
    
    private int maxRetries = 3;
    private Duration timeout = Duration.ofSeconds(5);
    private List<String> allowedCategories = Arrays.asList("electronics", "clothing");
    
    // getters and setters
}

// 应用配置
@Factory
public class ProductFactory {
    
    @Singleton
    @ConfigurationProperties("product")
    public ProductConfiguration productConfiguration() {
        return new ProductConfiguration();
    }
    
    @Singleton
    public HttpClient inventoryHttpClient(@Named("inventory") HttpClient httpClient) {
        return httpClient;
    }
}
```

#### 3.1.2 服务调用

```java
// Micronaut HTTP 客户端
@Client(id = "inventory-service")
public interface InventoryClient {
    
    @Get("/api/inventory/{productId}")
    Mono<Inventory> getInventory(@PathVariable String productId);
    
    @Post("/api/inventory")
    Mono<Void> updateInventory(@Body InventoryUpdate update);
}

// 服务实现
@Singleton
public class ProductService {
    
    private final InventoryClient inventoryClient;
    private final ProductConfiguration configuration;
    
    public ProductService(InventoryClient inventoryClient, 
                         ProductConfiguration configuration) {
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

## 4. Quarkus 与 Service Mesh 集成

### 4.1 Quarkus Kubernetes 扩展

#### 4.1.1 配置管理

```java
// Quarkus 配置
@ConfigProperties(prefix = "product")
public class ProductConfiguration {
    
    public int maxRetries = 3;
    public Duration timeout = Duration.ofSeconds(5);
    public List<String> allowedCategories = Arrays.asList("electronics", "clothing");
}

// 应用配置
@ApplicationScoped
public class ProductService {
    
    @Inject
    @ConfigProperty(name = "product.max-retries", defaultValue = "3")
    int maxRetries;
    
    @Inject
    ProductConfiguration configuration;
    
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

#### 4.1.2 REST 客户端集成

```java
// REST 客户端接口
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

// 应用配置
@ApplicationScoped
@RegisterRestClient
public class InventoryClientConfig {
    
    @Inject
    @RestClient
    InventoryClient inventoryClient;
    
    @ConfigProperty(name = "inventory.service.url")
    String inventoryServiceUrl;
}
```

## 5. 应用配置最佳实践

### 5.1 环境变量配置

```yaml
# Deployment 环境变量配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: product-service
spec:
  template:
    spec:
      containers:
      - name: product-service
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: JAEGER_SERVICE_NAME
          value: "product-service"
        - name: JAEGER_AGENT_HOST
          value: "jaeger-agent.istio-system"
```

### 5.2 ConfigMap 配置

```yaml
# ConfigMap 配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: product-config
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
    
    product:
      max-retries: 3
      timeout: 5000
      allowed-categories: electronics,clothing
    
    management:
      endpoints:
        web:
          exposure:
            include: health,info,metrics
      endpoint:
        health:
          show-details: always
```

## 6. 安全性最佳实践

### 6.1 mTLS 配置

```yaml
# PeerAuthentication 配置
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: product-mtls
  namespace: default
spec:
  selector:
    matchLabels:
      app: product-service
  mtls:
    mode: STRICT
```

### 6.2 安全策略配置

```yaml
# AuthorizationPolicy 配置
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: product-access
  namespace: default
spec:
  selector:
    matchLabels:
      app: product-service
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/frontend-service"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/products/*"]
```

## 7. 可观测性集成

### 7.1 分布式追踪

```java
// Spring Boot 追踪配置
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

### 7.2 指标收集

```java
// Micrometer 指标配置
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

// 业务指标
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

## 8. 性能优化

### 8.1 连接池优化

```java
// HTTP 连接池配置
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

### 8.2 缓存策略

```java
// Spring Cache 配置
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

// 缓存使用
@Service
public class ProductService {
    
    @Cacheable(value = "products", key = "#id")
    public Product getProduct(String id) {
        // 数据库查询逻辑
        return productRepository.findById(id);
    }
    
    @CacheEvict(value = "products", key = "#product.id")
    public void updateProduct(Product product) {
        productRepository.save(product);
    }
}
```

## 9. 部署与运维

### 9.1 Docker 镜像构建

```dockerfile
# Dockerfile
FROM openjdk:11-jre-slim

# 设置时区
ENV TZ=Asia/Shanghai

# 创建应用目录
WORKDIR /app

# 复制 JAR 文件
COPY target/product-service.jar app.jar

# 创建非 root 用户
RUN addgroup --system app && adduser --system --group app
USER app

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

# 启动应用
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 9.2 Kubernetes 部署配置

```yaml
# Deployment 配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: product-service
  labels:
    app: product-service
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: product-service
  template:
    metadata:
      labels:
        app: product-service
        version: v1.0.0
      annotations:
        sidecar.istio.io/inject: "true"
    spec:
      containers:
      - name: product-service
        image: registry.example.com/product-service:1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "production"
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

**下一章预告：** 第6章将深入探讨 Service Mesh 性能优化、故障排查和高级运维技巧。