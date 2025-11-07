import io.gatling.core.Predef._
import io.gatling.http.Predef._
import io.gatling.core.structure._
import io.gatling.http.protocol.HttpProtocolBuilder
import io.gatling.core.config.GatlingConfiguration
import scala.concurrent.duration._
import scala.util.Random
import java.io.{File, PrintWriter}
import java.text.SimpleDateFormat
import java.util.Date

class Chapter6ReportsAndAnalysis {

  val httpProtocol: HttpProtocolBuilder = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .contentTypeHeader("application/json")

  // ==================== 实验1：基本报告分析 ====================
  
  /**
   * 实验1.1：简单测试报告生成
   * 目标：演示如何运行基本测试并生成报告
   */
  val basicReportExperiment = {
    val scn = scenario("Basic Report Generation")
      .exec(
        http("Get User")
          .get("/users/1")
          .check(status.is(200))
          .check(responseTimeInMillis.lt(1000))
      )
      .exec(
        http("Get Posts")
          .get("/posts?userId=1")
          .check(status.is(200))
          .check(responseTimeInMillis.lt(1000))
      )
      .pause(1, 2)
    
    setUp(
      scn.inject(
        rampUsers(5) during (10 seconds),
        constantUsersPerSec(2) during (20 seconds)
      )
    ).protocols(httpProtocol)
    // 添加基本断言，将在报告中显示
    .assertions(
      global.responseTime.mean.lt(500),
      global.successfulRequests.percent.gt(95)
    )
  }
  
  /**
   * 实验1.2：多请求类型报告
   * 目标：演示不同请求类型的报告展示
   */
  val multiRequestTypeReportExperiment = {
    val scn = scenario("Multi Request Type Report")
      .exec(
        http("GET Request")
          .get("/users/1")
          .check(status.is(200))
      )
      .pause(1)
      .exec(
        http("POST Request")
          .post("/posts")
          .body(StringBody("""{"title": "Test Post", "body": "Test Body", "userId": 1}"""))
          .check(status.is(201))
      )
      .pause(1)
      .exec(
        http("PUT Request")
          .put("/posts/1")
          .body(StringBody("""{"id": 1, "title": "Updated Post", "body": "Updated Body", "userId": 1}"""))
          .check(status.is(200))
      )
      .pause(1)
      .exec(
        http("DELETE Request")
          .delete("/posts/1")
          .check(status.is(200))
      )
      .pause(1)
    
    setUp(
      scn.inject(atOnceUsers(3))
    ).protocols(httpProtocol)
    .assertions(
      global.responseTime.max.lt(2000),
      global.successfulRequests.percent.is(100)
    )
  }
  
  /**
   * 实验1.3：错误场景报告
   * 目标：演示如何生成包含错误的测试报告
   */
  val errorScenarioReportExperiment = {
    val scn = scenario("Error Scenario Report")
      .exec(
        http("Valid Request")
          .get("/users/1")
          .check(status.is(200))
      )
      .exec(
        http("Invalid Request - 404")
          .get("/nonexistent")
          .check(status.is(404))
      )
      .exec(
        http("Server Error Request")
          .get("/users/999")
          .check(status.in(200, 404)) // 可能返回404
      )
      .pause(1)
    
    setUp(
      scn.inject(rampUsers(10) during (5 seconds))
    ).protocols(httpProtocol)
    .assertions(
      global.responseTime.mean.lt(1000),
      details("Valid Request").successfulRequests.percent.is(100),
      details("Invalid Request - 404").status.in(404)
    )
  }

  // ==================== 实验2：自定义断言与报告 ====================
  
  /**
   * 实验2.1：性能断言报告
   * 目标：演示如何使用性能断言并在报告中查看结果
   */
  val performanceAssertionExperiment = {
    val scn = scenario("Performance Assertions")
      .exec(
        http("Fast Request")
          .get("/users/1")
          .check(status.is(200))
          .check(responseTimeInMillis.lt(500)) // 期望快速响应
      )
      .exec(
        http("Slow Request")
          .get("/posts")
          .check(status.is(200))
          .check(responseTimeInMillis.lt(2000)) // 期望较慢但可接受的响应
      )
      .pause(1, 3)
    
    setUp(
      scn.inject(
        rampUsers(5) during (10 seconds),
        constantUsersPerSec(3) during (30 seconds)
      )
    ).protocols(httpProtocol)
    // 详细的性能断言
    .assertions(
      // 全局断言
      global.responseTime.mean.lt(1000),
      global.responseTime.max.lt(5000),
      global.responseTime.percentile1.lt(500), // 50th percentile
      global.responseTime.percentile2.lt(1000), // 75th percentile
      global.responseTime.percentile3.lt(2000), // 95th percentile
      global.responseTime.percentile4.lt(3000), // 99th percentile
      global.successfulRequests.percent.gt(95),
      
      // 特定请求断言
      details("Fast Request").responseTime.mean.lt(300),
      details("Slow Request").responseTime.mean.lt(1500),
      details("Fast Request").successfulRequests.percent.is(100)
    )
  }
  
  /**
   * 实验2.2：业务断言报告
   * 目标：演示如何使用业务相关的断言
   */
  val businessAssertionExperiment = {
    val scn = scenario("Business Assertions")
      .exec(
        http("Get User")
          .get("/users/1")
          .check(status.is(200))
          .check(jsonPath("$.id").is("1"))
          .check(jsonPath("$.name").exists)
          .check(jsonPath("$.email").exists)
      )
      .exec(
        http("Get User Posts")
          .get("/posts?userId=1")
          .check(status.is(200))
          .check(jsonPath("$[*]").count.gt(0)) // 确保用户有帖子
          .check(jsonPath("$[0].userId").is("1")) // 确保帖子属于该用户
      )
      .pause(1)
    
    setUp(
      scn.inject(rampUsers(10) during (15 seconds))
    ).protocols(httpProtocol)
    // 业务断言
    .assertions(
      global.successfulRequests.percent.is(100),
      details("Get User").responseTime.mean.lt(500),
      details("Get User Posts").responseTime.mean.lt(800),
      global.requestsPerSec.gt(1.0) // 确保每秒至少处理1个请求
    )
  }
  
  /**
   * 实验2.3：动态断言报告
   * 目标：演示如何根据测试结果动态调整断言
   */
  val dynamicAssertionExperiment = {
    val scn = scenario("Dynamic Assertions")
      .exec(
        http("Get All Users")
          .get("/users")
          .check(status.is(200))
          .check(jsonPath("$[*]").count.saveAs("userCount"))
      )
      .exec(session => {
        val userCount = session("userCount").as[Int]
        println(s"Found $userCount users")
        session
      })
      .exec(
        http("Get All Posts")
          .get("/posts")
          .check(status.is(200))
          .check(jsonPath("$[*]").count.saveAs("postCount"))
      )
      .exec(session => {
        val postCount = session("postCount").as[Int]
        println(s"Found $postCount posts")
        session
      })
      .pause(1)
    
    setUp(
      scn.inject(atOnceUsers(5))
    ).protocols(httpProtocol)
    // 动态断言将基于实际返回的数据
    .assertions(
      global.successfulRequests.percent.is(100),
      global.responseTime.mean.lt(1000)
    )
  }

  // ==================== 实验3：性能趋势分析 ====================
  
  /**
   * 实验3.1：基准测试报告
   * 目标：演示如何创建性能基准测试报告
   */
  val benchmarkTestExperiment = {
    val scn = scenario("Benchmark Test")
      .exec(
        http("API Endpoint")
          .get("/users/1")
          .check(status.is(200))
          .check(responseTimeInMillis.saveAs("responseTime"))
      )
      .exec(session => {
        val responseTime = session("responseTime").as[Long]
        println(s"Response time: ${responseTime}ms")
        session
      })
      .pause(1)
    
    // 设置严格的性能基准
    setUp(
      scn.inject(
        rampUsers(20) during (30 seconds),
        constantUsersPerSec(5) during (60 seconds)
      )
    ).protocols(httpProtocol)
    .assertions(
      // 严格的性能基准
      global.responseTime.mean.lt(200),
      global.responseTime.percentile3.lt(500), // 95%的请求在500ms内完成
      global.responseTime.max.lt(1000),
      global.successfulRequests.percent.is(100),
      global.requestsPerSec.gt(5.0)
    )
  }
  
  /**
   * 实验3.2：负载测试报告
   * 目标：演示不同负载下的性能测试报告
   */
  val loadTestExperiment = {
    val scn = scenario("Load Test")
      .exec(
        http("User API")
          .get("/users/1")
          .check(status.is(200))
      )
      .exec(
        http("Post API")
          .get("/posts/1")
          .check(status.is(200))
      )
      .pause(500.milliseconds, 2.seconds)
    
    // 渐进式负载测试
    setUp(
      scn.inject(
        rampUsersPerSec(1) to 10 during (60 seconds), // 每秒用户数从1增加到10
        constantUsersPerSec(10) during (120 seconds) // 保持每秒10个用户2分钟
      )
    ).protocols(httpProtocol)
    .assertions(
      // 随着负载增加，适当放宽性能要求
      global.responseTime.mean.lt(1000),
      global.responseTime.percentile3.lt(2000),
      global.successfulRequests.percent.gt(95)
    )
  }
  
  /**
   * 实验3.3：压力测试报告
   * 目标：演示系统极限压力测试报告
   */
  val stressTestExperiment = {
    val scn = scenario("Stress Test")
      .exec(
        http("Critical API")
          .get("/users/1")
          .check(status.in(200, 429, 503)) // 允许限流或服务不可用
      )
      .pause(200.milliseconds, 1.second)
    
    // 高强度压力测试
    setUp(
      scn.inject(
        rampUsersPerSec(10) to 50 during (120 seconds), // 每秒用户数从10增加到50
        constantUsersPerSec(50) during (180 seconds) // 保持每秒50个用户3分钟
      )
    ).protocols(httpProtocol)
    .assertions(
      // 在压力测试中，放宽性能要求，关注系统稳定性
      global.responseTime.mean.lt(5000),
      global.responseTime.percentile3.lt(10000),
      global.successfulRequests.percent.gt(80) // 允许部分请求失败
    )
  }

  // ==================== 高级报告分析示例 ====================
  
  /**
   * 高级示例1：自定义数据收集
   * 目标：演示如何收集自定义数据用于分析
   */
  val customDataCollectionExperiment = {
    // 创建自定义数据收集器
    val customDataCollector = new StringBuilder()
    val dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
    
    val scn = scenario("Custom Data Collection")
      .exec(
        http("API Request")
          .get("/users/1")
          .check(status.is(200))
          .check(responseTimeInMillis.saveAs("responseTime"))
          .check(jsonPath("$.name").saveAs("userName"))
      )
      .exec(session => {
        // 收集自定义数据
        val timestamp = dateFormat.format(new Date())
        val responseTime = session("responseTime").as[Long]
        val userName = session("userName").as[String]
        
        // 格式化数据
        val dataLine = s"$timestamp, $responseTime, $userName\n"
        customDataCollector.append(dataLine)
        
        session
      })
      .pause(1)
    
    // 测试结束后保存自定义数据
    after {
      // 将收集的数据写入文件
      val file = new File("custom_data.csv")
      val writer = new PrintWriter(file)
      try {
        writer.write("Timestamp, ResponseTime, UserName\n")
        writer.write(customDataCollector.toString())
        println(s"Custom data saved to ${file.getAbsolutePath}")
      } finally {
        writer.close()
      }
    }
    
    setUp(
      scn.inject(rampUsers(10) during (30 seconds))
    ).protocols(httpProtocol)
    .assertions(
      global.responseTime.mean.lt(1000),
      global.successfulRequests.percent.gt(95)
    )
  }
  
  /**
   * 高级示例2：多环境比较测试
   * 目标：演示如何设计用于多环境性能比较的测试
   */
  val environmentComparisonExperiment = {
    // 可以通过参数指定不同环境的URL
    val baseUrl = System.getProperty("baseUrl", "https://jsonplaceholder.typicode.com")
    
    val envProtocol = http
      .baseUrl(baseUrl)
      .acceptHeader("application/json")
      .contentTypeHeader("application/json")
    
    val scn = scenario("Environment Comparison")
      .exec(
        http("Get User")
          .get("/users/1")
          .check(status.is(200))
          .check(responseTimeInMillis.saveAs("userResponseTime"))
      )
      .exec(
        http("Get Posts")
          .get("/posts")
          .check(status.is(200))
          .check(responseTimeInMillis.saveAs("postsResponseTime"))
      )
      .exec(session => {
        val userTime = session("userResponseTime").as[Long]
        val postsTime = session("postsResponseTime").as[Long]
        
        println(s"Environment: $baseUrl")
        println(s"User API Response Time: ${userTime}ms")
        println(s"Posts API Response Time: ${postsTime}ms")
        
        session
      })
      .pause(1)
    
    setUp(
      scn.inject(rampUsers(20) during (60 seconds))
    ).protocols(envProtocol)
    .assertions(
      global.responseTime.mean.lt(1500),
      global.successfulRequests.percent.gt(95)
    )
  }
  
  /**
   * 高级示例3：性能回归测试
   * 目标：演示如何设计用于检测性能回归的测试
   */
  val performanceRegressionTestExperiment = {
    val scn = scenario("Performance Regression Test")
      .exec(
        http("Critical API 1")
          .get("/users/1")
          .check(status.is(200))
      )
      .exec(
        http("Critical API 2")
          .get("/posts/1")
          .check(status.is(200))
      )
      .exec(
        http("Data Intensive API")
          .get("/posts")
          .check(status.is(200))
      )
      .pause(500.milliseconds, 1.5.seconds)
    
    // 设置严格的性能阈值，用于检测回归
    setUp(
      scn.inject(
        rampUsers(30) during (45 seconds),
        constantUsersPerSec(10) during (90 seconds)
      )
    ).protocols(httpProtocol)
    .assertions(
      // 严格的性能阈值，任何超出都表示可能的回归
      global.responseTime.mean.lt(800),
      global.responseTime.percentile3.lt(1500), // 95%的请求
      global.responseTime.max.lt(5000),
      global.successfulRequests.percent.gt(99),
      
      // 特定API的性能阈值
      details("Critical API 1").responseTime.mean.lt(500),
      details("Critical API 2").responseTime.mean.lt(500),
      details("Data Intensive API").responseTime.mean.lt(1200),
      
      // 吞吐量要求
      global.requestsPerSec.gt(8.0)
    )
  }
  
  /**
   * 高级示例4：自定义报告生成
   * 目标：演示如何生成自定义格式的报告
   */
  val customReportGenerationExperiment = {
    val scn = scenario("Custom Report Generation")
      .exec(
        http("API Request")
          .get("/users/1")
          .check(status.is(200))
          .check(responseTimeInMillis.saveAs("responseTime"))
      )
      .exec(session => {
        // 在Session中存储自定义指标
        val responseTime = session("responseTime").as[Long]
        session.set("customMetric", responseTime * 1.2) // 自定义计算
      })
      .pause(1)
    
    // 测试结束后生成自定义报告
    after {
      // 这里可以添加自定义报告生成逻辑
      // 例如：生成JSON、XML或CSV格式的报告
      val reportData = Map(
        "testName" -> "Custom Report Test",
        "timestamp" -> System.currentTimeMillis(),
        "status" -> "Completed"
      )
      
      // 简单示例：将报告数据写入JSON文件
      import scala.util.parsing.json._
      val jsonReport = JSONObject(reportData)
      
      val file = new File("custom_report.json")
      val writer = new PrintWriter(file)
      try {
        writer.write(jsonReport.toString())
        println(s"Custom report saved to ${file.getAbsolutePath}")
      } finally {
        writer.close()
      }
    }
    
    setUp(
      scn.inject(rampUsers(15) during (30 seconds))
    ).protocols(httpProtocol)
    .assertions(
      global.responseTime.mean.lt(1000),
      global.successfulRequests.percent.gt(95)
    )
  }
}