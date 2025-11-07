package chapter8

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import io.gatling.jdbc.Predef._
import io.gatling.core.structure.ScenarioBuilder
import io.gatling.http.protocol.HttpProtocolBuilder
import scala.concurrent.duration._
import io.gatling.core.feeder.FeederBuilder
import io.gatling.http.request.builder.HttpRequestBuilder.toActionBuilder

/**
 * 第8章：Gatling CI/CD集成与企业级应用示例代码
 * 包含10个实验，涵盖Jenkins集成、GitLab CI/CD集成、GitHub Actions集成、
 * Docker容器化部署、Kubernetes部署和企业级最佳实践等
 */
class Chapter8Examples {

  // ==================== 实验1：Jenkins集成示例 ====================
  
  /**
   * 实验1.1：Jenkins Pipeline集成测试
   * 适用于Jenkins CI/CD流水线中的性能测试
   */
  class JenkinsIntegrationSimulation extends Simulation {
    // 从环境变量读取配置
    val baseUrl = sys.env.getOrElse("BASE_URL", "http://test-app:8080")
    val users = sys.env.getOrElse("USERS", "100").toInt
    val duration = sys.env.getOrElse("DURATION", "60").toInt
    
    val httpProtocol = http
      .baseUrl(baseUrl)
      .acceptHeader("application/json")
      .userAgentHeader("Gatling-Jenkins-Integration")
    
    val scn = scenario("Jenkins集成测试")
      .exec(
        http("获取首页")
          .get("/")
          .check(status.is(200))
      )
      .pause(1, 3)
      .exec(
        http("获取用户列表")
          .get("/api/users")
          .check(status.is(200))
          .check(jsonPath("$.users[*].id").findAll.saveAs("userIds"))
      )
      .pause(1, 2)
      .foreach("${userIds}", "userId") {
        exec(
          http("获取用户详情")
            .get("/api/users/${userId}")
            .check(status.is(200))
        )
      }
    
    setUp(
      scn.inject(
        rampUsers(users) during (duration seconds)
      )
    ).protocols(httpProtocol)
      .assertions(
        global.responseTime.max.lt(5000),
        global.successfulRequests.percent.gt(95)
      )
  }
  
  // ==================== 实验2：GitLab CI/CD集成示例 ====================
  
  /**
   * 实验2.1：GitLab CI/CD性能测试
   * 适用于GitLab CI/CD流水线中的性能测试
   */
  class GitLabIntegrationSimulation extends Simulation {
    // 从配置文件读取参数
    val feeder = csv("gitlab_test_config.csv").random
    
    val httpProtocol = http
      .baseUrl("${base_url}")
      .acceptHeader("application/json")
      .header("Authorization", "Bearer ${api_token}")
    
    val scn = scenario("GitLab CI/CD测试")
      .feed(feeder)
      .exec(
        http("获取项目列表")
          .get("/api/v4/projects")
          .check(status.is(200))
          .check(jsonPath("$[*].id").findAll.saveAs("projectIds"))
      )
      .pause(1, 3)
      .randomSwitch(
        70 -> exec(
          http("获取项目详情")
            .get("/api/v4/projects/${projectIds.random()}")
            .check(status.is(200))
        ),
        30 -> exec(
          http("获取项目提交历史")
            .get("/api/v4/projects/${projectIds.random()}/repository/commits")
            .check(status.is(200))
        )
      )
    
    setUp(
      scn.inject(
        rampUsers(50) during (30 seconds),
        constantUsers(50) during (2 minutes)
      )
    ).protocols(httpProtocol)
  }
  
  // ==================== 实验3：GitHub Actions集成示例 ====================
  
  /**
   * 实验3.1：GitHub Actions性能测试
   * 适用于GitHub Actions工作流中的性能测试
   */
  class GitHubActionsSimulation extends Simulation {
    // 从环境变量读取配置
    val baseUrl = sys.env.getOrElse("API_URL", "https://api.github.com")
    val token = sys.env.getOrElse("GITHUB_TOKEN", "")
    
    val httpProtocol = http
      .baseUrl(baseUrl)
      .acceptHeader("application/vnd.github.v3+json")
      .header("Authorization", s"token $token")
      .header("User-Agent", "Gatling-GitHub-Actions")
    
    val scn = scenario("GitHub API测试")
      .exec(
        http("获取用户信息")
          .get("/user")
          .check(status.is(200))
          .check(jsonPath("$.id").saveAs("userId"))
          .check(jsonPath("$.login").saveAs("username"))
      )
      .pause(1, 2)
      .exec(
        http("获取用户仓库")
          .get("/user/repos")
          .queryParam("type", "owner")
          .check(status.is(200))
          .check(jsonPath("$[*].name").findAll.saveAs("repoNames"))
      )
      .pause(1, 3)
      .foreach("${repoNames}", "repoName") {
        exec(
          http("获取仓库详情")
            .get("/repos/${username}/${repoName}")
            .check(status.is(200))
            .check(jsonPath("$.stargazers_count").saveAs("stars"))
            .check(jsonPath("$.forks_count").saveAs("forks"))
        )
      }
    
    setUp(
      scn.inject(
        rampUsers(30) during (20 seconds)
      )
    ).protocols(httpProtocol)
  }
  
  // ==================== 实验4：Docker容器化部署示例 ====================
  
  /**
   * 实验4.1：Docker环境下的性能测试
   * 适用于Docker容器化部署的性能测试
   */
  class DockerIntegrationSimulation extends Simulation {
    // 从环境变量读取Docker网络配置
    val appHost = sys.env.getOrElse("APP_HOST", "app")
    val appPort = sys.env.getOrElse("APP_PORT", "8080")
    val dbHost = sys.env.getOrElse("DB_HOST", "postgres")
    val dbPort = sys.env.getOrElse("DB_PORT", "5432")
    
    val httpProtocol = http
      .baseUrl(s"http://$appHost:$appPort")
      .acceptHeader("application/json")
    
    // 数据库连接配置
    val jdbcProtocol = jdbc
      .url(s"jdbc:postgresql://$dbHost:$dbPort/testdb")
      .username("testuser")
      .password("testpass")
      .driver("org.postgresql.Driver")
    
    val scn = scenario("Docker环境测试")
      .exec(
        jdbc("检查数据库连接")
          .execute("SELECT 1")
      )
      .exec(
        http("健康检查")
          .get("/health")
          .check(status.is(200))
      )
      .pause(1, 2)
      .exec(
        http("创建测试数据")
          .post("/api/test-data")
          .body(StringBody("""{"name": "test_${randomString()}", "value": ${randomNumber()}}"""))
          .check(status.is(201))
          .check(jsonPath("$.id").saveAs("testId"))
      )
      .pause(1)
      .exec(
        http("获取测试数据")
          .get("/api/test-data/${testId}")
          .check(status.is(200))
      )
      .pause(1)
      .exec(
        http("删除测试数据")
          .delete("/api/test-data/${testId}")
          .check(status.is(204))
      )
    
    setUp(
      scn.inject(
        rampUsers(100) during (60 seconds)
      )
    ).protocols(httpProtocol, jdbcProtocol)
  }
  
  // ==================== 实验5：Kubernetes部署示例 ====================
  
  /**
   * 实验5.1：Kubernetes环境下的性能测试
   * 适用于Kubernetes部署的性能测试
   */
  class KubernetesIntegrationSimulation extends Simulation {
    // 从Kubernetes服务发现读取配置
    val namespace = sys.env.getOrElse("NAMESPACE", "default")
    val serviceName = sys.env.getOrElse("SERVICE_NAME", "my-app")
    val servicePort = sys.env.getOrElse("SERVICE_PORT", "8080")
    
    val httpProtocol = http
      .baseUrl(s"http://$serviceName.$namespace.svc.cluster.local:$servicePort")
      .acceptHeader("application/json")
      .header("X-Test-Source", "Gatling-K8s-Test")
    
    // 模拟Kubernetes环境下的用户行为
    val scn = scenario("Kubernetes环境测试")
      .exec(
        http("获取服务信息")
          .get("/info")
          .check(status.is(200))
          .check(jsonPath("$.version").saveAs("appVersion"))
          .check(jsonPath("$.pod").saveAs("podName"))
      )
      .pause(1, 3)
      .exec(
        http("获取资源使用情况")
          .get("/metrics")
          .check(status.is(200))
          .check(jsonPath("$.cpu").saveAs("cpuUsage"))
          .check(jsonPath("$.memory").saveAs("memoryUsage"))
      )
      .pause(2, 4)
      .randomSwitch(
        60 -> exec(
          http("读取操作")
            .get("/api/data")
            .queryParam("limit", "100")
            .check(status.is(200))
        ),
        40 -> exec(
          http("写入操作")
            .post("/api/data")
            .body(StringBody("""{"key": "test_${randomString()}", "value": "${randomString()}"}"""))
            .check(status.is(201))
        )
      )
    
    setUp(
      scn.inject(
        rampUsers(200) during (90 seconds),
        constantUsers(200) during (3 minutes)
      )
    ).protocols(httpProtocol)
  }
  
  // ==================== 实验6：分布式测试示例 ====================
  
  /**
   * 实验6.1：分布式性能测试
   * 适用于大规模分布式性能测试
   */
  class DistributedTestSimulation extends Simulation {
    // 从环境变量读取分布式配置
    val nodeIndex = sys.env.getOrElse("NODE_INDEX", "0").toInt
    val totalNodes = sys.env.getOrElse("TOTAL_NODES", "3").toInt
    val baseUrl = sys.env.getOrElse("BASE_URL", "http://load-balancer:8080")
    
    val httpProtocol = http
      .baseUrl(baseUrl)
      .acceptHeader("application/json")
      .header("X-Node-Index", nodeIndex.toString)
    
    // 根据节点索引分配不同的用户范围
    val userRangeStart = nodeIndex * 1000
    val userRangeEnd = (nodeIndex + 1) * 1000
    
    val userFeeder = Iterator.continually(Map(
      "userId" -> (userRangeStart + scala.util.Random.nextInt(userRangeEnd - userRangeStart)),
      "sessionId" -> java.util.UUID.randomUUID().toString
    ))
    
    val scn = scenario("分布式测试")
      .feed(userFeeder)
      .exec(
        http("用户登录")
          .post("/api/auth/login")
          .body(StringBody("""{"userId": ${userId}, "sessionId": "${sessionId}"}"""))
          .check(status.is(200))
          .check(jsonPath("$.token").saveAs("authToken"))
      )
      .pause(1, 3)
      .exec(
        http("获取用户数据")
          .get("/api/users/${userId}")
          .header("Authorization", "Bearer ${authToken}")
          .check(status.is(200))
      )
      .pause(2, 4)
      .exec(
        http("执行业务操作")
          .post("/api/operations")
          .header("Authorization", "Bearer ${authToken}")
          .body(StringBody("""{"userId": ${userId}, "operation": "test", "timestamp": ${System.currentTimeMillis()}}"""))
          .check(status.is(201))
      )
      .pause(1, 2)
      .exec(
        http("用户登出")
          .post("/api/auth/logout")
          .header("Authorization", "Bearer ${authToken}")
          .check(status.is(200))
      )
    
    setUp(
      scn.inject(
        rampUsers(500) during (2 minutes)
      )
    ).protocols(httpProtocol)
  }
  
  // ==================== 实验7：微服务性能测试示例 ====================
  
  /**
   * 实验7.1：微服务架构性能测试
   * 适用于微服务架构下的性能测试
   */
  class MicroservicesTestSimulation extends Simulation {
    // 定义各个微服务的协议
    val userServiceProtocol = http
      .baseUrl("http://user-service:8080")
      .acceptHeader("application/json")
      .header("X-Trace-ID", "${traceId}")
    
    val productServiceProtocol = http
      .baseUrl("http://product-service:8080")
      .acceptHeader("application/json")
      .header("X-Trace-ID", "${traceId}")
    
    val orderServiceProtocol = http
      .baseUrl("http://order-service:8080")
      .acceptHeader("application/json")
      .header("X-Trace-ID", "${traceId}")
    
    val paymentServiceProtocol = http
      .baseUrl("http://payment-service:8080")
      .acceptHeader("application/json")
      .header("X-Trace-ID", "${traceId}")
    
    // 生成唯一的追踪ID
    val traceIdFeeder = Iterator.continually(Map(
      "traceId" -> java.util.UUID.randomUUID().toString
    ))
    
    // 用户注册流程
    val userRegistration = exec(
      userServiceProtocol.post("/users")
        .body(StringBody("""{"username": "user_${randomString()}", "email": "user_${randomString()}@example.com"}"""))
        .check(status.is(201))
        .check(jsonPath("$.id").saveAs("userId"))
    )
    
    // 产品浏览流程
    val productBrowsing = exec(
      productServiceProtocol.get("/products")
        .queryParam("limit", "20")
        .check(status.is(200))
        .check(jsonPath("$[*].id").findAll.saveAs("productIds"))
    )
    
    // 下单流程
    val orderPlacement = exec(
      orderServiceProtocol.post("/orders")
        .body(StringBody("""{"userId": ${userId}, "items": [{"productId": ${productIds.random()}, "quantity": 1}]}"""))
        .check(status.is(201))
        .check(jsonPath("$.id").saveAs("orderId"))
        .check(jsonPath("$.totalAmount").saveAs("orderAmount"))
    )
    
    // 支付流程
    val paymentProcessing = exec(
      paymentServiceProtocol.post("/payments")
        .body(StringBody("""{"orderId": ${orderId}, "amount": ${orderAmount}, "method": "credit_card"}"""))
        .check(status.is(201))
        .check(jsonPath("$.id").saveAs("paymentId"))
        .check(jsonPath("$.status").is("completed"))
    )
    
    // 完整的微服务业务流程
    val scn = scenario("微服务业务流程")
      .feed(traceIdFeeder)
      .exec(userRegistration)
      .pause(2, 5)
      .exec(productBrowsing)
      .pause(1, 3)
      .exec(orderPlacement)
      .pause(1, 2)
      .exec(paymentProcessing)
      .pause(1, 2)
      .exec(
        orderServiceProtocol.get("/orders/${orderId}")
          .check(status.is(200))
          .check(jsonPath("$.status").is("completed"))
      )
    
    setUp(
      scn.inject(
        rampUsers(100) during (60 seconds),
        constantUsers(100) during (5 minutes)
      )
    ).protocols(userServiceProtocol, productServiceProtocol, orderServiceProtocol, paymentServiceProtocol)
  }
  
  // ==================== 实验8：混沌工程集成示例 ====================
  
  /**
   * 实验8.1：混沌工程集成测试
   * 将性能测试与混沌工程结合，测试系统在故障情况下的表现
   */
  class ChaosEngineeringSimulation extends Simulation {
    val httpProtocol = http
      .baseUrl("http://api.example.com")
      .acceptHeader("application/json")
    
    // 正常请求
    val normalRequest = exec(
      http("正常请求")
        .get("/api/data")
        .check(status.in(200, 500)) // 允许服务器错误
        .check(responseTimeInMillis.lte(2000)) // 正常情况下响应时间不超过2秒
    )
    
    // 注入延迟
    val latencyInjection = exec(
      http("延迟注入")
        .get("/api/data")
        .header("X-Chaos-Latency", "1000") // 注入1000ms延迟
        .check(status.in(200, 500))
        .check(responseTimeInMillis.lte(3000)) // 允许更长的响应时间
    )
    
    // 注入错误
    val errorInjection = exec(
      http("错误注入")
        .get("/api/data")
        .header("X-Chaos-Error", "500") // 注入500错误
        .check(status.in(200, 500))
    )
    
    // 注入超时
    val timeoutInjection = exec(
      http("超时注入")
        .get("/api/data")
        .header("X-Chaos-Timeout", "5000") // 注入5秒超时
        .check(status.in(200, 500, 408)) // 允许超时状态码
    )
    
    // 混沌测试场景
    val chaosScenario = scenario("混沌工程测试")
      .exec(normalRequest)
      .pause(1)
      .exec(latencyInjection)
      .pause(1)
      .exec(errorInjection)
      .pause(1)
      .exec(timeoutInjection)
      .pause(1)
      .exec(normalRequest) // 恢复后的请求
    
    setUp(
      chaosScenario.inject(
        rampUsers(50) during (30 seconds)
      )
    ).protocols(httpProtocol)
      .assertions(
        // 在混沌注入期间，允许更高的错误率
        global.failedRequests.percent.lt(50),
        // 即使有混沌注入，大部分请求仍应在合理时间内完成
        global.responseTime.percentile3.lt(5000)
      )
  }
  
  // ==================== 实验9：性能基线比较示例 ====================
  
  /**
   * 实验9.1：性能基线比较测试
   * 与历史性能基线比较，检测性能退化
   */
  class BaselineComparisonSimulation extends Simulation {
    // 从环境变量读取基线数据
    val baselineResponseTime = sys.env.getOrElse("BASELINE_RESPONSE_TIME", "500").toDouble
    val baselineThroughput = sys.env.getOrElse("BASELINE_THROUGHPUT", "1000").toDouble
    val baselineErrorRate = sys.env.getOrElse("BASELINE_ERROR_RATE", "0.1").toDouble
    
    val httpProtocol = http
      .baseUrl("http://api.example.com")
      .acceptHeader("application/json")
    
    val scn = scenario("基线比较测试")
      .exec(
        http("获取数据")
          .get("/api/data")
          .check(status.is(200))
          .check(responseTimeInMillis.lte(baselineResponseTime * 1.2)) // 允许比基线高20%
      )
      .pause(1, 2)
      .exec(
        http("提交数据")
          .post("/api/data")
          .body(StringBody("""{"key": "test", "value": "value"}"""))
          .check(status.is(201))
          .check(responseTimeInMillis.lte(baselineResponseTime * 1.2))
      )
      .pause(1, 2)
      .exec(
        http("更新数据")
          .put("/api/data/1")
          .body(StringBody("""{"key": "test", "value": "updated_value"}"""))
          .check(status.is(200))
          .check(responseTimeInMillis.lte(baselineResponseTime * 1.2))
      )
    
    setUp(
      scn.inject(
        rampUsers(100) during (60 seconds),
        constantUsers(100) during (4 minutes)
      )
    ).protocols(httpProtocol)
      .assertions(
        // 响应时间不应比基线高出20%
        global.responseTime.mean.lte(baselineResponseTime * 1.2),
        // 吞吐量不应比基线低10%
        global.requestsPerSec.gt(baselineThroughput * 0.9),
        // 错误率不应比基线高1%
        global.failedRequests.percent.lte(baselineErrorRate * 10)
      )
  }
  
  // ==================== 实验10：企业级监控集成示例 ====================
  
  /**
   * 实验10.1：企业级监控集成测试
   * 与企业监控系统（如Prometheus、Grafana）集成
   */
  class EnterpriseMonitoringSimulation extends Simulation {
    val httpProtocol = http
      .baseUrl("http://api.example.com")
      .acceptHeader("application/json")
      .header("X-Test-Run-ID", "${testRunId}")
    
    // 生成测试运行ID
    val testRunIdFeeder = Iterator.continually(Map(
      "testRunId" -> s"test-${System.currentTimeMillis()}"
    ))
    
    // 自定义指标收集
    val collectMetrics = exec(session => {
      // 这里可以添加自定义指标收集逻辑
      // 例如：将指标发送到Prometheus Pushgateway
      val responseTime = session("responseTime").asOption[Long]
      val statusCode = session("status").asOption[Int]
      
      // 在实际应用中，这里会调用Prometheus客户端发送指标
      println(s"收集指标: 响应时间=$responseTime, 状态码=$statusCode")
      
      session
    })
    
    val scn = scenario("企业级监控测试")
      .feed(testRunIdFeeder)
      .exec(
        http("获取系统状态")
          .get("/api/system/status")
          .check(status.is(200))
          .check(responseTimeInMillis.saveAs("responseTime"))
          .check(status.saveAs("status"))
      )
      .exec(collectMetrics)
      .pause(1, 2)
      .exec(
        http("获取业务指标")
          .get("/api/metrics/business")
          .check(status.is(200))
          .check(responseTimeInMillis.saveAs("responseTime"))
          .check(status.saveAs("status"))
      )
      .exec(collectMetrics)
      .pause(1, 2)
      .exec(
        http("获取性能指标")
          .get("/api/metrics/performance")
          .check(status.is(200))
          .check(responseTimeInMillis.saveAs("responseTime"))
          .check(status.saveAs("status"))
      )
      .exec(collectMetrics)
    
    setUp(
      scn.inject(
        rampUsers(50) during (30 seconds),
        constantUsers(50) during (3 minutes)
      )
    ).protocols(httpProtocol)
      .assertions(
        global.responseTime.mean.lt(1000),
        global.successfulRequests.percent.gt(99)
      )
  }
}