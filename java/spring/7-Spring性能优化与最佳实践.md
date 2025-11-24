# 第7章 Spring性能优化与最佳实践

## 目录
- [Spring性能优化策略](#spring性能优化策略)
- [JVM调优与Spring](#jvm调优与spring)
- [数据库连接池优化](#数据库连接池优化)
- [缓存策略与实现](#缓存策略与实现)
- [异步处理与响应式编程](#异步处理与响应式编程)
- [Spring Boot Actuator监控](#spring-boot-actuator监控)
- [微服务性能优化](#微服务性能优化)
- [安全性与性能平衡](#安全性与性能平衡)
- [日志优化](#日志优化)
- [测试策略与性能验证](#测试策略与性能验证)
- [生产环境部署优化](#生产环境部署优化)
- [故障排查与性能分析工具](#故障排查与性能分析工具)

## Spring性能优化策略

### 性能优化的重要性

在现代企业级应用开发中，性能优化是一个至关重要的环节。随着业务规模的增长和用户量的增加，应用的性能直接影响用户体验和业务收益。

### 常见性能瓶颈

1. **数据库访问瓶颈**
   - SQL查询效率低下
   - 缺少合适的索引
   - 连接池配置不当

2. **内存使用问题**
   - 内存泄漏
   - 对象创建过多
   - 垃圾回收频繁

3. **网络通信延迟**
   - 微服务间调用延迟
   - 外部API响应慢
   - 数据传输量过大

4. **线程阻塞**
   - 同步锁竞争
   - 阻塞IO操作
   - 线程池配置不合理

### 性能优化原则

1. **测量先行**
   ```java
   // 使用Micrometer进行指标收集
   @Component
   public class ProductService {
       
       private final MeterRegistry meterRegistry;
       private final Timer productRetrieveTimer;
       
       public ProductService(MeterRegistry meterRegistry) {
           this.meterRegistry = meterRegistry;
           this.productRetrieveTimer = Timer.builder("product.retrieve")
               .description("产品检索时间")
               .register(meterRegistry);
       }
       
       public Product getProduct(Long id) {
           return Timer.Sample.start(meterRegistry)
               .stop(productRetrieveTimer);
       }
   }
   ```

2. **避免过早优化**
   - 先保证功能正确性
   - 通过性能测试识别瓶颈
   - 有针对性地进行优化

3. **关注热点代码**
   - 识别高频调用的方法
   - 优化关键路径上的代码
   - 减少不必要的计算

## JVM调优与Spring

### JVM内存模型回顾

JVM内存主要分为以下几个区域：
- **堆内存(Heap)**：存放对象实例
- **方法区(Metaspace)**：存放类信息、常量、静态变量
- **虚拟机栈(VM Stack)**：存放局部变量、操作数栈
- **本地方法栈(Native Method Stack)**：为Native方法服务
- **程序计数器(Program Counter Register)**：当前线程执行的字节码行号

### JVM参数调优

#### 堆内存调优
```bash
# 设置初始堆大小和最大堆大小
-Xms2g -Xmx4g

# 新生代大小设置
-XX:NewSize=1g -XX:MaxNewSize=1g

# 老年代大小
-XX:OldSize=1g
```

#### 垃圾收集器选择
```bash
# G1垃圾收集器（推荐用于大堆内存）
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:G1HeapRegionSize=16m

# Parallel GC（适用于吞吐量优先场景）
-XX:+UseParallelGC
-XX:ParallelGCThreads=8
```

#### GC日志配置
```bash
# 开启GC日志
-Xloggc:gc.log
-XX:+PrintGCDetails
-XX:+PrintGCTimeStamps
-XX:+PrintGCApplicationStoppedTime
```

### Spring应用中的内存优化

#### 对象池化
```java
@Configuration
public class ObjectPoolConfig {
    
    @Bean
    public GenericObjectPool<StringBuilder> stringBuilderPool() {
        GenericObjectPoolConfig<StringBuilder> config = new GenericObjectPoolConfig<>();
        config.setMaxTotal(100);
        config.setMaxIdle(50);
        config.setMinIdle(10);
        
        return new GenericObjectPool<>(new BasePooledObjectFactory<StringBuilder>() {
            @Override
            public StringBuilder create() throws Exception {
                return new StringBuilder();
            }
            
            @Override
            public PooledObject<StringBuilder> wrap(StringBuilder obj) {
                return new DefaultPooledObject<>(obj);
            }
            
            @Override
            public void passivateObject(PooledObject<StringBuilder> p) throws Exception {
                p.getObject().setLength(0); // 清空内容而不是重新创建
            }
        }, config);
    }
}
```

#### 避免内存泄漏
```java
@Component
public class ResourceManagementService implements DisposableBean {
    
    private final List<Closeable> resources = new ArrayList<>();
    
    public void registerResource(Closeable resource) {
        resources.add(resource);
    }
    
    @Override
    public void destroy() throws Exception {
        for (Closeable resource : resources) {
            try {
                resource.close();
            } catch (IOException e) {
                // 记录日志但不中断关闭过程
                log.warn("Failed to close resource", e);
            }
        }
    }
}
```

## 数据库连接池优化

### 连接池选型

目前主流的数据库连接池有：
1. **HikariCP**：性能最优，轻量级
2. **Druid**：功能丰富，监控完善
3. **Tomcat JDBC Pool**：稳定可靠

### HikariCP配置优化
```yaml
spring:
  datasource:
    hikari:
      # 连接池基本配置
      minimum-idle: 10
      maximum-pool-size: 50
      idle-timeout: 300000
      max-lifetime: 1800000
      connection-timeout: 30000
      leak-detection-threshold: 60000
      
      # 连接测试
      connection-test-query: SELECT 1
      validation-timeout: 5000
      
      # 性能优化
      pool-name: HikariPool-Production
      initialization-fail-timeout: 1
      isolate-internal-queries: false
      allow-pool-suspension: false
      readOnly: false
      register-mbeans: false
```

### 连接池监控
```java
@Component
public class ConnectionPoolMonitor {
    
    private final HikariDataSource dataSource;
    
    public ConnectionPoolMonitor(DataSource dataSource) {
        this.dataSource = (HikariDataSource) dataSource;
    }
    
    @Scheduled(fixedRate = 30000)
    public void logPoolStatus() {
        HikariPoolMXBean poolBean = dataSource.getHikariPoolMXBean();
        
        log.info("连接池状态 - 活跃连接: {}, 空闲连接: {}, 等待连接的线程数: {}",
                poolBean.getActiveConnections(),
                poolBean.getIdleConnections(),
                poolBean.getThreadsAwaitingConnection());
    }
}
```

### SQL优化策略

#### 查询优化
```java
@Repository
public class UserRepository {
    
    @PersistenceContext
    private EntityManager entityManager;
    
    // 使用投影查询减少数据传输
    public List<UserProfileDto> findUserProfiles() {
        String jpql = "SELECT new com.example.dto.UserProfileDto(u.id, u.name, u.email) " +
                     "FROM User u WHERE u.active = true";
        return entityManager.createQuery(jpql, UserProfileDto.class)
                          .getResultList();
    }
    
    // 批量操作优化
    @Modifying
    @Query("UPDATE User u SET u.lastLoginTime = :loginTime WHERE u.id IN :ids")
    public int updateLastLoginTime(@Param("loginTime") LocalDateTime loginTime, 
                                  @Param("ids") List<Long> ids);
}
```

#### 索引优化
```sql
-- 为常用查询字段创建复合索引
CREATE INDEX idx_user_active_email ON user(active, email);

-- 为范围查询字段创建索引
CREATE INDEX idx_order_create_time ON order(create_time);

-- 避免过多索引影响写入性能
```

## 缓存策略与实现

### 缓存选型

1. **本地缓存**：Caffeine、Ehcache
2. **分布式缓存**：Redis、Memcached
3. **多级缓存**：组合使用本地+分布式缓存

### Caffeine本地缓存
```java
@Configuration
@EnableCaching
public class CacheConfig {
    
    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        cacheManager.setCaffeine(caffeineCacheBuilder());
        return cacheManager;
    }
    
    Caffeine<Object, Object> caffeineCacheBuilder() {
        return Caffeine.newBuilder()
                .maximumSize(1000)
                .expireAfterWrite(10, TimeUnit.MINUTES)
                .expireAfterAccess(1, TimeUnit.HOURS)
                .recordStats()
                .removalListener((key, value, cause) -> {
                    log.info("缓存移除 - Key: {}, Cause: {}", key, cause);
                });
    }
}
```

### Redis分布式缓存
```java
@Configuration
@EnableCaching
public class RedisConfig {
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        return template;
    }
    
    @Bean
    public CacheManager redisCacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofHours(1))
                .serializeKeysWith(RedisSerializationContext.SerializationPair.fromSerializer(new StringRedisSerializer()))
                .serializeValuesWith(RedisSerializationContext.SerializationPair.fromSerializer(new GenericJackson2JsonRedisSerializer()));
        
        return RedisCacheManager.builder(connectionFactory)
                .cacheDefaults(config)
                .build();
    }
}
```

### 缓存使用最佳实践
```java
@Service
public class ProductService {
    
    // 缓存条件表达式
    @Cacheable(value = "products", key = "#id", unless = "#result.price > 1000")
    public Product findById(Long id) {
        return productRepository.findById(id);
    }
    
    // 缓存更新
    @CachePut(value = "products", key = "#product.id")
    public Product save(Product product) {
        return productRepository.save(product);
    }
    
    // 缓存删除
    @CacheEvict(value = "products", key = "#id")
    public void delete(Long id) {
        productRepository.deleteById(id);
    }
    
    // 批量缓存清除
    @CacheEvict(value = "products", allEntries = true)
    @Transactional
    public void batchUpdate(List<Product> products) {
        productRepository.saveAll(products);
    }
}
```

## 异步处理与响应式编程

### Spring异步处理

#### @Async注解使用
```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {
    
    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("Async-Executor-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
    
    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return new SimpleAsyncUncaughtExceptionHandler();
    }
}

@Service
public class NotificationService {
    
    @Async
    public CompletableFuture<Void> sendEmailAsync(String email, String content) {
        try {
            // 模拟耗时操作
            Thread.sleep(2000);
            emailService.send(email, content);
            return CompletableFuture.completedFuture(null);
        } catch (Exception e) {
            return CompletableFuture.failedFuture(e);
        }
    }
    
    @Async("taskExecutor")
    public void processOrderAsync(Order order) {
        // 异步处理订单逻辑
        orderProcessingService.process(order);
    }
}
```

#### 异步Web请求处理
```java
@RestController
public class OrderController {
    
    @Autowired
    private OrderService orderService;
    
    @PostMapping("/orders")
    public CompletableFuture<ResponseEntity<Order>> createOrder(@RequestBody OrderRequest request) {
        return orderService.createOrderAsync(request)
                .thenApply(order -> ResponseEntity.ok(order))
                .exceptionally(throwable -> {
                    log.error("创建订单失败", throwable);
                    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
                });
    }
}
```

### 响应式编程(Spring WebFlux)

#### WebFlux控制器
```java
@RestController
@RequestMapping("/api/products")
public class ProductController {
    
    @Autowired
    private ProductService productService;
    
    @GetMapping("/{id}")
    public Mono<Product> getProduct(@PathVariable Long id) {
        return productService.findById(id);
    }
    
    @GetMapping
    public Flux<Product> getAllProducts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return productService.findAll(PageRequest.of(page, size));
    }
    
    @PostMapping
    public Mono<ResponseEntity<Product>> createProduct(@RequestBody Mono<Product> productMono) {
        return productMono
                .flatMap(productService::save)
                .map(product -> ResponseEntity.ok(product))
                .onErrorReturn(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build());
    }
}
```

#### 响应式服务层
```java
@Service
public class ProductService {
    
    @Autowired
    private ProductRepository productRepository;
    
    public Mono<Product> findById(Long id) {
        return productRepository.findById(id)
                .switchIfEmpty(Mono.error(new ProductNotFoundException("Product not found: " + id)));
    }
    
    public Flux<Product> findAll(Pageable pageable) {
        return productRepository.findAllBy(pageable);
    }
    
    public Mono<Product> save(Product product) {
        return productRepository.save(product);
    }
    
    public Mono<Product> update(Long id, Product product) {
        return productRepository.findById(id)
                .switchIfEmpty(Mono.error(new ProductNotFoundException("Product not found: " + id)))
                .flatMap(existingProduct -> {
                    existingProduct.setName(product.getName());
                    existingProduct.setPrice(product.getPrice());
                    return productRepository.save(existingProduct);
                });
    }
}
```

## Spring Boot Actuator监控

### Actuator端点配置
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "*"
  endpoint:
    health:
      show-details: always
    metrics:
      enabled: true
    prometheus:
      enabled: true
  metrics:
    export:
      prometheus:
        enabled: true
    distribution:
      percentiles-histogram:
        http:
          server:
            requests: true
```

### 自定义健康检查
```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    
    @Autowired
    private DataSource dataSource;
    
    @Override
    public Health health() {
        try (Connection connection = dataSource.getConnection()) {
            if (connection.isValid(1)) {
                return Health.up()
                        .withDetail("database", "Available")
                        .withDetail("validationQuery", "SELECT 1")
                        .build();
            } else {
                return Health.down()
                        .withDetail("database", "Unavailable")
                        .build();
            }
        } catch (SQLException e) {
            return Health.down()
                    .withDetail("database", "Connection failed")
                    .withException(e)
                    .build();
        }
    }
}
```

### 自定义指标收集
```java
@Component
public class BusinessMetricsCollector {
    
    private final MeterRegistry meterRegistry;
    private final Counter orderCounter;
    private final Timer orderProcessTimer;
    private final Gauge activeUsersGauge;
    
    public BusinessMetricsCollector(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.orderCounter = Counter.builder("business.orders")
                .description("订单数量统计")
                .register(meterRegistry);
                
        this.orderProcessTimer = Timer.builder("business.order.process")
                .description("订单处理时间")
                .register(meterRegistry);
                
        this.activeUsersGauge = Gauge.builder("business.users.active")
                .description("活跃用户数")
                .register(meterRegistry, userService, UserService::getActiveUserCount);
    }
    
    public void recordOrder() {
        orderCounter.increment();
    }
    
    public void recordOrderProcess(Duration duration) {
        orderProcessTimer.record(duration);
    }
}
```

## 微服务性能优化

### 服务间通信优化

#### Feign客户端优化
```java
@FeignClient(name = "user-service", 
             configuration = UserServiceClientConfig.class,
             fallback = UserServiceFallback.class)
public interface UserServiceClient {
    
    @GetMapping("/users/{id}")
    ResponseEntity<UserDto> getUserById(@PathVariable("id") Long id);
}

@Configuration
public class UserServiceClientConfig {
    
    @Bean
    public Request.Options options() {
        return new Request.Options(5000, 10000); // 连接超时5秒，读取超时10秒
    }
    
    @Bean
    public Retryer retryer() {
        return new Retryer.Default(100, 2000, 3); // 初始间隔100ms，最大间隔2s，最多重试3次
    }
}
```

#### 负载均衡优化
```java
@Configuration
public class LoadBalancerConfig {
    
    @Bean
    public ReactorLoadBalancer<ServiceInstance> reactorServiceInstanceLoadBalancer(
            Environment environment,
            LoadBalancerClientFactory loadBalancerClientFactory) {
        String name = environment.getProperty(LoadBalancerClientFactory.PROPERTY_NAME);
        return new RoundRobinLoadBalancer(
                loadBalancerClientFactory.getLazyProvider(name, ServiceInstanceListSupplier.class),
                name);
    }
}
```

### 服务熔断与降级
```java
@Service
public class OrderService {
    
    @Autowired
    private UserServiceClient userServiceClient;
    
    @CircuitBreaker(name = "user-service", fallbackMethod = "getUserFallback")
    public UserDto getUser(Long userId) {
        return userServiceClient.getUserById(userId).getBody();
    }
    
    public UserDto getUserFallback(Long userId, Exception ex) {
        log.warn("获取用户信息失败，使用降级方案: userId={}, exception={}", userId, ex.getMessage());
        return UserDto.builder()
                .id(userId)
                .name("未知用户")
                .email("unknown@example.com")
                .build();
    }
}
```

### 分布式追踪
```java
@RestController
@RequestMapping("/orders")
public class OrderController {
    
    @Autowired
    private OrderService orderService;
    
    @PostMapping
    public ResponseEntity<Order> createOrder(@RequestBody OrderRequest request) {
        Span span = tracer.nextSpan().name("create-order").start();
        try (Tracer.SpanInScope ws = tracer.withSpan(span)) {
            Order order = orderService.createOrder(request);
            return ResponseEntity.ok(order);
        } finally {
            span.end();
        }
    }
}
```

## 安全性与性能平衡

### 认证优化
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/actuator/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .addFilterBefore(jwtAuthenticationFilter(), UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }
    
    @Bean
    public JwtAuthenticationFilter jwtAuthenticationFilter() {
        return new JwtAuthenticationFilter();
    }
}
```

### JWT优化
```java
@Component
public class JwtTokenUtil {
    
    private final String secret = "mySecretKey";
    private final long expiration = 86400; // 24小时
    
    public String generateToken(UserDetails userDetails) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("role", userDetails.getAuthorities());
        return createToken(claims, userDetails.getUsername());
    }
    
    private String createToken(Map<String, Object> claims, String subject) {
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(subject)
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + expiration * 1000))
                .signWith(SignatureAlgorithm.HS512, secret)
                .compact();
    }
    
    public Boolean validateToken(String token, UserDetails userDetails) {
        final String username = getUsernameFromToken(token);
        return (username.equals(userDetails.getUsername()) && !isTokenExpired(token));
    }
}
```

## 日志优化

### 结构化日志
```java
@Component
public class StructuredLogger {
    
    private static final Logger logger = LoggerFactory.getLogger(StructuredLogger.class);
    
    public void logUserAction(String userId, String action, Map<String, Object> details) {
        Map<String, Object> logData = new HashMap<>();
        logData.put("timestamp", Instant.now().toString());
        logData.put("userId", userId);
        logData.put("action", action);
        logData.put("details", details);
        
        logger.info("User Action: {}", JsonUtils.toJson(logData));
    }
}
```

### 日志级别动态调整
```java
@RestController
@RequestMapping("/admin/logging")
public class LoggingController {
    
    @PostMapping("/level")
    public ResponseEntity<String> changeLogLevel(
            @RequestParam String loggerName,
            @RequestParam String level) {
        LoggerContext loggerContext = (LoggerContext) LoggerFactory.getILoggerFactory();
        Logger logger = loggerContext.getLogger(loggerName);
        logger.setLevel(Level.valueOf(level.toUpperCase()));
        return ResponseEntity.ok("日志级别已更新");
    }
}
```

## 测试策略与性能验证

### 性能测试配置
```java
@SpringBootTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestPropertySource(locations = "classpath:application-test.properties")
public class PerformanceTest {
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Test
    @RepeatedTest(100)
    public void testHighConcurrency() {
        long startTime = System.currentTimeMillis();
        
        ResponseEntity<String> response = restTemplate.getForEntity("/api/products/1", String.class);
        
        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;
        
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(duration).isLessThan(1000L); // 响应时间小于1秒
    }
}
```

### 压力测试脚本
```java
@PerformanceTest
public class LoadTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    public void loadTest() throws Exception {
        // 模拟100个并发用户，每个用户发送10个请求
        ExecutorService executor = Executors.newFixedThreadPool(100);
        CountDownLatch latch = new CountDownLatch(1000);
        
        for (int i = 0; i < 1000; i++) {
            executor.submit(() -> {
                try {
                    mockMvc.perform(get("/api/products"))
                            .andExpect(status().isOk());
                } catch (Exception e) {
                    e.printStackTrace();
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await();
        executor.shutdown();
    }
}
```

## 生产环境部署优化

### JVM参数优化
```bash
#!/bin/bash
# 生产环境JVM启动参数
JAVA_OPTS="-server \
-Xms4g -Xmx8g \
-XX:+UseG1GC \
-XX:MaxGCPauseMillis=200 \
-XX:+UnlockExperimentalVMOptions \
-XX:+UseStringDeduplication \
-XX:G1HeapRegionSize=16m \
-XX:+G1UseAdaptiveIHOP \
-XX:G1MixedGCCountTarget=8 \
-XX:+PrintGC \
-XX:+PrintGCDetails \
-XX:+PrintGCTimeStamps \
-Xloggc:/var/log/app/gc.log \
-XX:+UseGCLogFileRotation \
-XX:NumberOfGCLogFiles=5 \
-XX:GCLogFileSize=100M \
-Dcom.sun.management.jmxremote \
-Dcom.sun.management.jmxremote.port=9999 \
-Dcom.sun.management.jmxremote.authenticate=false \
-Dcom.sun.management.jmxremote.ssl=false"

java $JAVA_OPTS -jar app.jar
```

### Docker容器优化
```dockerfile
FROM openjdk:11-jre-slim

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 添加应用
COPY target/app.jar app.jar

# JVM优化参数
ENV JAVA_OPTS="-XX:+UseG1GC \
               -XX:MaxGCPauseMillis=200 \
               -XX:+UnlockExperimentalVMOptions \
               -XX:+UseStringDeduplication"

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

EXPOSE 8080

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app.jar"]
```

### Kubernetes部署优化
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spring-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: spring-app
  template:
    metadata:
      labels:
        app: spring-app
    spec:
      containers:
      - name: app
        image: spring-app:latest
        ports:
        - containerPort: 8080
        env:
        - name: JAVA_OPTS
          value: "-Xmx2g -Xms2g -XX:+UseG1GC"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

## 故障排查与性能分析工具

### 常用诊断命令
```bash
# 查看JVM进程
jps -l

# 查看JVM详细信息
jinfo -flags <pid>

# 查看GC情况
jstat -gc <pid> 1s

# 查看堆内存使用情况
jmap -heap <pid>

# 生成堆转储文件
jmap -dump:live,format=b,file=heap.hprof <pid>

# 查看线程信息
jstack <pid>
```

### Arthas在线诊断工具
```java
// 启动Arthas
java -jar arthas-boot.jar

// 查看方法调用统计
trace com.example.service.UserService getUser

// 监控方法执行
watch com.example.service.OrderService createOrder '{params, returnObj}' -x 2

// 热更新代码
redefine /tmp/UserService.class
```

### 应用监控集成
```java
@Configuration
public class MonitoringConfig {
    
    @Bean
    public TimedAspect timedAspect(MeterRegistry registry) {
        return new TimedAspect(registry);
    }
    
    @Bean
    public CountedAspect countedAspect(MeterRegistry registry) {
        return new CountedAspect(registry);
    }
}

@Service
public class BusinessService {
    
    @Timed(value = "business.operation.time", description = "业务操作耗时")
    @Counted(value = "business.operation.count", description = "业务操作次数")
    public Result performOperation(Request request) {
        // 业务逻辑
        return result;
    }
}
```

## 总结

Spring性能优化是一个系统工程，需要从多个维度综合考虑：

1. **代码层面**：优化算法、减少对象创建、合理使用缓存
2. **框架层面**：合理配置Spring、使用异步处理、优化数据库访问
3. **JVM层面**：调整堆内存、选择合适的垃圾收集器
4. **架构层面**：微服务拆分、负载均衡、熔断降级
5. **运维层面**：监控告警、日志分析、自动化部署

通过以上各个方面的优化措施，可以显著提升Spring应用的性能和稳定性。在实际应用中，应该根据具体业务场景和性能要求，有针对性地选择和实施相应的优化策略。