import io.gatling.core.Predef._
import io.gatling.http.Predef._
import io.gatling.jdbc.Predef._
import scala.concurrent.duration._
import java.util.UUID
import java.lang.management.ManagementFactory
import scala.collection.mutable.ArrayBuffer
import java.util.concurrent.ConcurrentLinkedQueue
import scala.util.Random

/**
 * 第7章：Gatling性能优化与调试示例代码
 * 包含10个实验，涵盖JVM参数调优、测试脚本优化、资源管理、分布式测试优化和调试技巧
 */
class Chapter7Examples extends Simulation {

  // ==================== 实验1：JVM参数调优 ====================
  
  /**
   * 实验1.1：内存使用监控
   * 监控测试过程中的内存使用情况，帮助优化JVM参数
   */
  val memoryMonitor = exec(session => {
    val runtime = Runtime.getRuntime
    val totalMemory = runtime.totalMemory() / 1024 / 1024
    val freeMemory = runtime.freeMemory() / 1024 / 1024
    val usedMemory = totalMemory - freeMemory
    val maxMemory = runtime.maxMemory() / 1024 / 1024
    
    val usagePercent = (usedMemory.toDouble / maxMemory) * 100
    
    println(s"[${System.currentTimeMillis()}] 内存使用: ${usedMemory}MB / ${maxMemory}MB (${usagePercent}%)")
    
    if (usagePercent > 80) {
      println(s"警告: 内存使用率过高: ${usagePercent}%")
    }
    
    session.set("memoryUsage", usagePercent)
  })
  
  /**
   * 实验1.2：CPU使用率监控
   * 监控测试过程中的CPU使用情况
   */
  val cpuMonitor = exec(session => {
    val osBean = ManagementFactory.getOperatingSystemMXBean.asInstanceOf[com.sun.management.OperatingSystemMXBean]
    val cpuUsage = osBean.getProcessCpuLoad * 100
    
    println(s"[${System.currentTimeMillis()}] CPU使用率: ${cpuUsage}%")
    
    if (cpuUsage > 90) {
      println(s"警告: CPU使用率过高: ${cpuUsage}%")
    }
    
    session.set("cpuUsage", cpuUsage)
  })
  
  /**
   * 实验1.3：GC监控
   * 监控垃圾回收情况，帮助优化GC参数
   */
  val gcMonitor = exec(session => {
    val gcBeans = ManagementFactory.getGarbageCollectorMXBeans()
    
    gcBeans.forEach { gcBean =>
      val name = gcBean.getName
      val collectionCount = gcBean.getCollectionCount
      val collectionTime = gcBean.getCollectionTime
      
      println(s"[${System.currentTimeMillis()}] GC [$name]: 收集次数=$collectionCount, 总时间=${collectionTime}ms")
    }
    
    session
  })
  
  // ==================== 实验2：测试脚本优化 ====================
  
  /**
   * 实验2.1：请求优化 - 合并请求
   * 演示如何将多个小请求合并为一个请求，减少网络开销
   */
  val requestOptimizationScenario = scenario("请求优化")
    .exec(
      // 优化前：发送多个小请求
      exec(http("获取用户信息").get("/api/users/1"))
      exec(http("获取用户权限").get("/api/users/1/permissions"))
      exec(http("获取用户偏好").get("/api/users/1/preferences"))
      .pause(1)
      
      // 优化后：合并为一个请求
      exec(http("获取完整用户信息").get("/api/users/1?include=permissions,preferences"))
    )
  
  /**
   * 实验2.2：缓存优化
   * 演示如何通过缓存减少重复请求
   */
  val cacheOptimizationScenario = scenario("缓存优化")
    .exec(
      // 优化前：每次都获取配置
      exec(http("获取配置").get("/api/config"))
      exec(http("获取数据").get("/api/data"))
      exec(http("获取配置").get("/api/config"))
      exec(http("获取更多数据").get("/api/more-data"))
      .pause(1)
      
      // 优化后：缓存配置数据
      exec(
        http("获取配置").get("/api/config").check(jsonPath("$.config").saveAs("config"))
      ).exec(
        http("获取数据").get("/api/data")
      ).exec(
        http("获取更多数据").get("/api/more-data")
      )
    )
  
  /**
   * 实验2.3：思考时间优化
   * 演示不同思考时间策略的效果
   */
  val thinkTimeOptimizationScenario = scenario("思考时间优化")
    .exec(
      // 优化前：固定思考时间
      pause(5)
      
      // 优化后：随机思考时间
      pause(3, 7) // 3到7秒随机
      
      // 优化后：基于正态分布的思考时间
      pause(normal(5, 2)) // 均值5秒，标准差2秒
      
      // 优化后：基于百分比的思考时间
      pause(5, 10) // 5到10秒随机，更符合实际用户行为
    )
  
  // ==================== 实验3：资源管理与内存优化 ====================
  
  /**
   * 实验3.1：Session大小监控
   * 监控Session大小，防止Session过大导致内存问题
   */
  val sessionSizeMonitor = exec(session => {
    val sessionSize = session.attributes.size
    
    println(s"[${System.currentTimeMillis()}] Session大小: ${sessionSize}个属性")
    
    if (sessionSize > 100) {
      println(s"警告: Session过大，包含${sessionSize}个属性")
    }
    
    session.set("sessionSize", sessionSize)
  })
  
  /**
   * 实验3.2：及时清理Session
   * 演示如何及时清理不需要的Session数据
   */
  val sessionCleanupScenario = scenario("Session清理")
    .exec(
      // 优化前：Session中保留大量数据
      exec(
        http("获取大数据").get("/api/large-data")
          .check(jsonPath("$.data").saveAs("largeData"))
      ).exec(
        http("处理数据").post("/api/process")
          .body(StringBody("${largeData}"))
      ).pause(1)
      
      // 优化后：及时清理不需要的数据
      exec(
        http("获取大数据").get("/api/large-data")
          .check(jsonPath("$.data").saveAs("largeData"))
      ).exec(
        http("处理数据").post("/api/process")
          .body(StringBody("${largeData}"))
      ).exec(session => {
        session.remove("largeData") // 清理不需要的数据
      })
    )
  
  /**
   * 实验3.3：对象池使用
   * 演示如何使用对象池减少对象创建开销
   */
  object ObjectPoolExample {
    // 简单的对象池实现
    class ObjectPool[T <: { def reset(): Unit }](createFn: () => T) {
      private val pool = new ConcurrentLinkedQueue[T]()
      
      def borrow(): T = {
        Option(pool.poll()) match {
          case Some(obj) => obj
          case None => createFn()
        }
      }
      
      def returnObj(obj: T): Unit = {
        obj.reset()
        pool.offer(obj)
      }
    }
    
    // 示例数据对象
    class DataObject {
      var id: String = ""
      var data: String = ""
      
      def reset(): Unit = {
        id = ""
        data = ""
      }
    }
    
    // 创建对象池
    val dataObjectPool = new ObjectPool(() => new DataObject())
  }
  
  val objectPoolScenario = scenario("对象池使用")
    .exec(session => {
      import ObjectPoolExample._
      
      val dataObj = dataObjectPool.borrow()
      try {
        dataObj.id = UUID.randomUUID().toString
        dataObj.data = "测试数据"
        
        // 使用对象...
        session.set("objectId", dataObj.id)
      } finally {
        dataObjectPool.returnObj(dataObj)
      }
    })
  
  // ==================== 实验4：分布式测试优化 ====================
  
  /**
   * 实验4.1：负载均衡策略
   * 演示自定义负载均衡策略
   */
  class CustomLoadBalancer extends LoadBalancer {
    override def selectNode(nodes: Seq[Node]): Node = {
      // 基于节点负载选择节点
      nodes.minBy(_.currentLoad)
    }
  }
  
  val loadBalancingScenario = scenario("负载均衡测试")
    .exec(http("测试请求").get("/api/test"))
  
  /**
   * 实验4.2：网络连接优化
   * 演示如何优化网络连接参数
   */
  val optimizedHttpProtocol = http
    .baseUrl("http://example.com")
    .maxConnectionsPerHost(1000) // 增加最大连接数
    .acceptHeader("application/json")
    .userAgentHeader("Gatling/3.9.5")
    .disableCaching // 禁用缓存以减少内存使用
    .disableFollowRedirect // 禁用自动重定向
  
  val networkOptimizationScenario = scenario("网络连接优化")
    .exec(http("测试请求").get("/api/test"))
  
  /**
   * 实验4.3：结果收集优化
   * 演示如何优化结果收集过程
   */
  class OptimizedDataWriter extends DataWriter {
    private val buffer = new ArrayBuffer[RequestMessage]()
    private val batchSize = 1000
    
    override def write(requestMessage: RequestMessage): Unit = {
      buffer += requestMessage
      if (buffer.size >= batchSize) {
        flush()
      }
    }
    
    private def flush(): Unit = {
      // 批量写入数据
      println(s"批量写入${buffer.size}条记录")
      buffer.clear()
    }
  }
  
  val resultCollectionScenario = scenario("结果收集优化")
    .exec(http("测试请求").get("/api/test"))
  
  // ==================== 实验5：调试技巧与问题排查 ====================
  
  /**
   * 实验5.1：自定义日志记录
   * 演示如何添加自定义日志记录
   */
  val customLoggingScenario = scenario("自定义日志记录")
    .exec(session => {
      val userId = session("userId").asOption[String].getOrElse("unknown")
      println(s"[${System.currentTimeMillis()}] 处理用户请求: $userId")
      session
    })
    .exec(
      http("测试请求")
        .get("/api/test")
        .check(
          status.saveAs("status"),
          responseTimeInMillis.saveAs("responseTime")
        )
    )
    .exec(session => {
      val status = session("status").as[Int]
      val responseTime = session("responseTime").as[Long]
      
      if (status != 200) {
        println(s"[${System.currentTimeMillis()}] 请求失败，状态码: $status")
      }
      
      if (responseTime > 5000) {
        println(s"[${System.currentTimeMillis()}] 响应时间过长: ${responseTime}ms")
      }
      
      session
    })
  
  /**
   * 实验5.2：连接超时诊断
   * 演示如何诊断连接超时问题
   */
  val connectionTimeoutScenario = scenario("连接超时诊断")
    .exec(
      http("测试请求")
        .get("/api/test")
        .check(
          status.saveAs("status"),
          responseTimeInMillis.saveAs("responseTime")
        )
    )
    .exec(session => {
      val status = session("status").as[Int]
      val responseTime = session("responseTime").as[Long]
      
      if (status != 200) {
        println(s"[${System.currentTimeMillis()}] 请求失败，状态码: $status")
      }
      
      if (responseTime > 5000) {
        println(s"[${System.currentTimeMillis()}] 响应时间过长: ${responseTime}ms")
      }
      
      session
    })
  
  /**
   * 实验5.3：性能基准测试
   * 演示如何进行性能基准测试
   */
  val benchmarkScenario = scenario("性能基准测试")
    .exec(
      // 基准测试：简单GET请求
      exec(http("基准测试-简单GET").get("/api/simple"))
      .pause(1)
      
      // 基准测试：带参数GET请求
      exec(http("基准测试-带参数GET").get("/api/param?test=value"))
      .pause(1)
      
      // 基准测试：POST请求
      exec(
        http("基准测试-POST")
          .post("/api/post")
          .body(StringBody("""{"test": "value"}"""))
          .header("Content-Type", "application/json")
      )
      .pause(1)
    )
  
  // ==================== 实验6：高级优化策略 ====================
  
  /**
   * 实验6.1：自定义协议处理器
   * 演示如何实现自定义协议处理器
   */
  class CustomProtocol extends Protocol {
    override def buildUrl(request: Request): String = {
      // 自定义URL构建逻辑
      s"${request.baseUrl}${request.url.path}?${request.queryParams.mkString("&")}"
    }
    
    override def buildHeaders(request: Request): Map[String, String] = {
      // 自定义请求头构建逻辑
      Map(
        "X-Custom-Header" -> "custom-value",
        "X-Request-ID" -> UUID.randomUUID().toString
      )
    }
  }
  
  val customProtocolScenario = scenario("自定义协议处理器")
    .exec(http("测试请求").get("/api/test"))
  
  /**
   * 实验6.2：高效的自定义断言
   * 演示如何实现高效的自定义断言
   */
  class EfficientCheck extends Check[String] {
    override def check(response: Response, session: Session): Validation[String] = {
      // 使用更高效的验证逻辑
      if (response.body.length > 1000) {
        KO("响应体过大")
      } else {
        OK(response.body)
      }
    }
  }
  
  val efficientCheckScenario = scenario("高效断言")
    .exec(
      http("测试请求")
        .get("/api/test")
        .check(new EfficientCheck())
    )
  
  /**
   * 实验6.3：批量结果处理
   * 演示如何批量处理测试结果
   */
  class BatchResultProcessor extends DataWriter {
    private val batch = new ArrayBuffer[RequestMessage]()
    private val batchSize = 1000
    
    override def write(requestMessage: RequestMessage): Unit = {
      batch += requestMessage
      if (batch.size >= batchSize) {
        processBatch()
      }
    }
    
    private def processBatch(): Unit = {
      // 批量处理结果数据
      // 可以使用批量插入数据库、批量写入文件等方式
      println(s"批量处理${batch.size}条记录")
      batch.clear()
    }
  }
  
  val batchProcessingScenario = scenario("批量结果处理")
    .exec(http("测试请求").get("/api/test"))
  
  // ==================== 测试场景设置 ====================
  
  // HTTP协议配置
  val httpProtocol = http
    .baseUrl("http://example.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling/3.9.5")
  
  // 设置测试场景
  setUp(
    // 实验1：JVM参数调优
    memoryMonitor.inject(
      rampUsers(10) during (30 seconds)
    ).protocols(httpProtocol),
    
    cpuMonitor.inject(
      rampUsers(10) during (30 seconds)
    ).protocols(httpProtocol),
    
    gcMonitor.inject(
      rampUsers(10) during (30 seconds)
    ).protocols(httpProtocol),
    
    // 实验2：测试脚本优化
    requestOptimizationScenario.inject(
      rampUsers(5) during (10 seconds)
    ).protocols(httpProtocol),
    
    cacheOptimizationScenario.inject(
      rampUsers(5) during (10 seconds)
    ).protocols(httpProtocol),
    
    thinkTimeOptimizationScenario.inject(
      rampUsers(5) during (10 seconds)
    ).protocols(httpProtocol),
    
    // 实验3：资源管理与内存优化
    sessionSizeMonitor.inject(
      rampUsers(10) during (30 seconds)
    ).protocols(httpProtocol),
    
    sessionCleanupScenario.inject(
      rampUsers(5) during (10 seconds)
    ).protocols(httpProtocol),
    
    objectPoolScenario.inject(
      rampUsers(5) during (10 seconds)
    ).protocols(httpProtocol),
    
    // 实验4：分布式测试优化
    loadBalancingScenario.inject(
      rampUsers(100) during (60 seconds)
    ).protocols(httpProtocol)
    .loadBalancer(new CustomLoadBalancer()),
    
    networkOptimizationScenario.inject(
      rampUsers(100) during (60 seconds)
    ).protocols(optimizedHttpProtocol),
    
    resultCollectionScenario.inject(
      rampUsers(100) during (60 seconds)
    ).protocols(httpProtocol),
    
    // 实验5：调试技巧与问题排查
    customLoggingScenario.inject(
      rampUsers(10) during (30 seconds)
    ).protocols(httpProtocol),
    
    connectionTimeoutScenario.inject(
      rampUsers(10) during (30 seconds)
    ).protocols(httpProtocol),
    
    benchmarkScenario.inject(
      rampUsers(10) during (30 seconds)
    ).protocols(httpProtocol),
    
    // 实验6：高级优化策略
    customProtocolScenario.inject(
      rampUsers(10) during (30 seconds)
    ).protocols(new CustomProtocol()),
    
    efficientCheckScenario.inject(
      rampUsers(10) during (30 seconds)
    ).protocols(httpProtocol),
    
    batchProcessingScenario.inject(
      rampUsers(10) during (30 seconds)
    ).protocols(httpProtocol)
  ).assertions(
    global.responseTime.max.lt(1000),
    global.successfulRequests.percent.gt(95)
  )
}