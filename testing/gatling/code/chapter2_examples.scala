// 第2章示例代码：Gatling基础概念与核心组件

package computerdatabase

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

/**
 * 实验1：理解Simulation和Scenario
 * 目的：演示Simulation的基本结构和Scenario的组成
 */
class SimulationScenarioExperiment extends Simulation {

  // HTTP协议配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Experiment")

  // 场景定义
  val scn = scenario("Basic Scenario")
    .exec(
      http("Get All Posts")
        .get("/posts")
        .check(status.is(200))
    )
    .pause(2)
    .exec(
      http("Get Single Post")
        .get("/posts/1")
        .check(status.is(200))
        .check(jsonPath("$.userId").exists)
    )

  // 负载配置
  setUp(
    scn.inject(
      rampUsers(5) during (10 seconds)
    )
  ).protocols(httpProtocol)
}

/**
 * 实验2：探索不同的负载注入模式
 * 目的：演示不同的负载注入模式及其组合
 */
class InjectionProfileExperiment extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  // 基础场景
  val baseScenario = scenario("Base Scenario")
    .exec(
      http("Get Post")
        .get("/posts/${__randomInt(1, 100)}")
        .check(status.is(200))
    )
    .pause(1, 3)

  // 立即注入
  setUp(
    baseScenario.inject(atOnceUsers(10))
      .protocols(httpProtocol)
  ).assertions(global.responseTime.max.lt(2000))

  // 渐进注入
  setUp(
    baseScenario.inject(rampUsers(20) during (30 seconds))
      .protocols(httpProtocol)
  ).assertions(global.responseTime.max.lt(2000))

  // 恒定速率注入
  setUp(
    baseScenario.inject(constantUsersPerSec(5) during (20 seconds))
      .protocols(httpProtocol)
  ).assertions(global.responseTime.max.lt(2000))

  // 组合注入
  setUp(
    baseScenario.inject(
      nothingFor(5 seconds),
      rampUsers(10) during (10 seconds),
      constantUsersPerSec(5) during (20 seconds),
      rampUsersPerSec(5) to (10) during (10 seconds)
    ).protocols(httpProtocol)
  ).assertions(global.responseTime.max.lt(2000))
}

/**
 * 实验3：使用Feed实现数据驱动测试
 * 目的：演示如何从CSV文件中读取数据并在测试中使用
 */
class FeedExperiment extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  // 定义Feed
  val postFeeder = csv("posts.csv").random // 随机读取
  val userFeeder = csv("users.csv").circular // 循环读取

  // 使用Feed的场景
  val feedScenario = scenario("Feed Scenario")
    .feed(postFeeder)
    .feed(userFeeder)
    .exec(
      http("Get Post by ID")
        .get("/posts/${postId}")
        .check(status.is(200))
        .check(jsonPath("$.title").is("${postTitle}"))
    )
    .pause(1)
    .exec(
      http("Get User by ID")
        .get("/users/${userId}")
        .check(status.is(200))
        .check(jsonPath("$.name").is("${userName}"))
    )

  setUp(
    feedScenario.inject(
      rampUsers(10) during (20 seconds)
    )
  ).protocols(httpProtocol)
}

/**
 * 实验4：Protocol配置示例
 * 目的：演示各种HTTP协议配置选项
 */
class ProtocolConfigurationExperiment extends Simulation {

  // 基本HTTP协议配置
  val basicHttpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Protocol Experiment")

  // 高级HTTP协议配置
  val advancedHttpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Advanced Protocol")
    .disableFollowRedirect // 禁用自动重定向
    .maxRedirects(5) // 最大重定向次数
    .connectionHeader("keep-alive") // 连接头
    .silentResources // 静默资源
    .disableWarmUp // 禁用预热
    .http2Enabled // 启用HTTP/2
    .shareConnections // 共享连接
    .perUserConnection // 每用户连接
    .virtualHost("example.com") // 虚拟主机
    .proxy(Proxy("proxy.example.com", 8080)) // 代理配置

  // 基本场景
  val scn = scenario("Protocol Test")
    .exec(
      http("Get All Posts")
        .get("/posts")
        .check(status.is(200))
    )

  // 使用基本协议配置
  setUp(
    scn.inject(atOnceUsers(5))
  ).protocols(basicHttpProtocol)
}

/**
 * 实验5：Check（检查）示例
 * 目的：演示各种检查类型和用法
 */
class CheckExperiment extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  val scn = scenario("Check Test")
    .exec(
      http("Get Post with Checks")
        .get("/posts/1")
        // 状态检查
        .check(status.is(200))
        // 响应时间检查
        .check(responseTimeInMillis.lte(1000))
        // 响应内容检查
        .check(bodyString.saveAs("responseBody"))
        // 响应头检查
        .check(header("Content-Type").exists)
        .check(header("Content-Type").is("application/json; charset=utf-8"))
        // JSON检查
        .check(jsonPath("$.id").is("1"))
        .check(jsonPath("$.userId").exists)
        .check(jsonPath("$.title").saveAs("postTitle"))
        // 正则表达式检查
        .check(regex("\"userId\": (\\d+)").saveAs("userId"))
        // CSS选择器检查（适用于HTML）
        // .check(css("title").is("Example Page"))
    )
    .exec(session => {
      println("Response Body: " + session("responseBody").as[String])
      println("Post Title: " + session("postTitle").as[String])
      println("User ID: " + session("userId").as[String])
      session
    })

  setUp(
    scn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}

/**
 * 实验6：Session操作示例
 * 目的：演示如何操作Session中的数据
 */
class SessionExperiment extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  val scn = scenario("Session Test")
    .exec(session => session.set("customKey", "customValue")) // 设置Session属性
    .exec(session => {
      println("Custom Value: " + session("customKey").as[String])
      session
    })
    .exec(
      http("Get Post")
        .get("/posts/1")
        .check(status.is(200))
        .check(jsonPath("$.userId").saveAs("userId"))
    )
    .exec(session => {
      val userId = session("userId").as[String]
      println("User ID from response: " + userId)
      session.set("nextPostId", (userId.toInt + 1).toString) // 计算并设置新值
    })
    .exec(
      http("Get Next Post")
        .get("/posts/${nextPostId}")
        .check(status.is(200))
    )
    .exec(session => session.remove("customKey")) // 移除Session属性

  setUp(
    scn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}

/**
 * 实验7：Assertion（断言）示例
 * 目的：演示各种断言类型和用法
 */
class AssertionExperiment extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  val scn = scenario("Assertion Test")
    .exec(
      http("Get All Posts")
        .get("/posts")
        .check(status.is(200))
    )
    .pause(1)
    .exec(
      http("Get Single Post")
        .get("/posts/1")
        .check(status.is(200))
    )

  setUp(
    scn.inject(
      rampUsers(10) during (10 seconds)
    )
  ).protocols(httpProtocol)
  .assertions(
    // 全局断言
    global.responseTime.max.lt(2000), // 最大响应时间小于2000毫秒
    global.responseTime.mean.lt(1000), // 平均响应时间小于1000毫秒
    global.successfulRequests.percent.gt(95), // 成功率大于95%
    global.requestsPerSec.gt(5), // 每秒请求数大于5
    global.allRequests.count.is(20), // 总请求数等于20
    
    // 针对特定请求的断言
    details("Get All Posts").responseTime.max.lt(1500),
    details("Get Single Post").successfulRequests.percent.is(100)
  )
}

/**
 * 实验8：循环和条件示例
 * 目的：演示循环和条件结构的使用
 */
class LoopAndConditionalExperiment extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  val scn = scenario("Loop and Conditional Test")
    .exec(
      http("Get Post")
        .get("/posts/1")
        .check(status.is(200))
        .check(jsonPath("$.userId").saveAs("userId"))
    )
    // 条件执行
    .doIf("${userId}", "1") {
      exec(
        http("Get User 1")
          .get("/users/1")
          .check(status.is(200))
      )
    }
    .doIfOrElse("${userId}", "1") {
      exec(
        http("Get User 1 Alternative")
          .get("/users/1")
          .check(status.is(200))
      )
    } {
      exec(
        http("Get All Users")
          .get("/users")
          .check(status.is(200))
      )
    }
    // 随机选择
    .randomSwitch(
      50.0 -> exec(http("Random Get Posts").get("/posts")),
      30.0 -> exec(http("Random Get Users").get("/users")),
      20.0 -> exec(http("Random Get Comments").get("/comments"))
    )
    // 循环执行
    .repeat(3, "counter") {
      exec(
        http("Get Post ${counter}")
          .get("/posts/${counter}")
          .check(status.is(200))
      )
      .pause(1)
    }
    // foreach循环
    .foreach(Seq("1", "2", "3"), "postId") {
      exec(
        http("Get Post ${postId}")
          .get("/posts/${postId}")
          .check(status.is(200))
      )
    }
    // while循环
    .asLongAs(session => session("counter").as[Int] < 5) {
      exec(session => session.set("counter", session("counter").as[Int] + 1))
        .exec(
          http("Get Post ${counter}")
            .get("/posts/${counter}")
            .check(status.is(200))
        )
    }

  setUp(
    scn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}

/**
 * 实验9：多场景示例
 * 目的：演示如何在同一个Simulation中定义多个场景
 */
class MultipleScenariosExperiment extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  // 场景1：浏览帖子
  val browsePostsScenario = scenario("Browse Posts")
    .exec(
      http("Get All Posts")
        .get("/posts")
        .check(status.is(200))
    )
    .pause(2, 5)
    .repeat(3) {
      exec(
        http("Get Random Post")
          .get("/posts/${__randomInt(1, 100)}")
          .check(status.is(200))
      )
      .pause(1, 3)
    }

  // 场景2：浏览用户
  val browseUsersScenario = scenario("Browse Users")
    .exec(
      http("Get All Users")
        .get("/users")
        .check(status.is(200))
    )
    .pause(2, 5)
    .repeat(3) {
      exec(
        http("Get Random User")
          .get("/users/${__randomInt(1, 10)}")
          .check(status.is(200))
      )
      .pause(1, 3)
    }

  // 场景3：浏览评论
  val browseCommentsScenario = scenario("Browse Comments")
    .exec(
      http("Get All Comments")
        .get("/comments")
        .check(status.is(200))
    )
    .pause(2, 5)
    .repeat(3) {
      exec(
        http("Get Random Comment")
          .get("/comments/${__randomInt(1, 500)}")
          .check(status.is(200))
      )
      .pause(1, 3)
    }

  // 设置多个场景的负载
  setUp(
    browsePostsScenario.inject(
      rampUsers(10) during (20 seconds)
    ),
    browseUsersScenario.inject(
      rampUsers(5) during (15 seconds)
    ),
    browseCommentsScenario.inject(
      rampUsers(3) during (10 seconds)
    )
  ).protocols(httpProtocol)
}

/**
 * 实验10：自定义函数示例
 * 目的：演示如何在测试中使用自定义函数
 */
class CustomFunctionExperiment extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  // 自定义函数：生成随机字符串
  def randomString(length: Int): String = {
    val chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    Random.alphanumeric.take(length).mkString
  }

  // 自定义函数：计算斐波那契数列
  def fibonacci(n: Int): Int = {
    if (n <= 1) n
    else fibonacci(n - 1) + fibonacci(n - 2)
  }

  val scn = scenario("Custom Function Test")
    .exec(session => session.set("randomString", randomString(10)))
    .exec(session => session.set("fibonacci", fibonacci(10)))
    .exec(session => {
      println("Random String: " + session("randomString").as[String])
      println("Fibonacci: " + session("fibonacci").as[Int])
      session
    })
    .exec(
      http("Get Post with Custom Header")
        .get("/posts/1")
        .header("X-Random-String", "${randomString}")
        .header("X-Fibonacci", "${fibonacci}")
        .check(status.is(200))
    )

  setUp(
    scn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}