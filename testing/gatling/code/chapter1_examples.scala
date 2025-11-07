// 第1章示例代码：Gatling简介与环境搭建

package computerdatabase

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

/**
 * 实验1：第一个Gatling测试
 * 目的：验证Gatling环境安装正确，创建一个简单的HTTP GET请求测试
 */
class BasicSimulation extends Simulation {

  // HTTP配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com") // 基础URL
    .acceptHeader("application/json") // 默认请求头
    .userAgentHeader("Gatling/3.7.0") // 用户代理

  // 场景定义
  val scn = scenario("Basic Test")
    .exec(http("Get All Posts")
      .get("/posts")
      .check(status.is(200))) // 检查响应状态码为200

  // 设置负载
  setUp(
    scn.inject(atOnceUsers(1)) // 注入1个用户
  ).protocols(httpProtocol)
}

/**
 * 实验2：多用户并发测试
 * 目的：测试多个并发用户对同一接口的请求
 */
class ConcurrentUsersSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  val scn = scenario("Concurrent Users Test")
    .exec(http("Get All Posts")
      .get("/posts")
      .check(status.is(200)))
    .pause(2, 5) // 随机暂停2-5秒

  setUp(
    scn.inject(
      rampUsers(10) during (30 seconds) // 30秒内逐渐增加10个用户
    )
  ).protocols(httpProtocol)
}

/**
 * 实验3：不同请求类型测试
 * 目的：演示GET、POST、PUT、DELETE等不同HTTP请求方法
 */
class MultipleMethodsSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .contentTypeHeader("application/json")

  val scn = scenario("Multiple Methods Test")
    .exec(
      http("GET Request")
        .get("/posts/1")
        .check(status.is(200))
    )
    .pause(1)
    .exec(
      http("POST Request")
        .post("/posts")
        .body(StringBody("""{"title": "foo", "body": "bar", "userId": 1}""")).asJson
        .check(status.is(201))
    )
    .pause(1)
    .exec(
      http("PUT Request")
        .put("/posts/1")
        .body(StringBody("""{"id": 1, "title": "foo", "body": "bar", "userId": 1}""")).asJson
        .check(status.is(200))
    )
    .pause(1)
    .exec(
      http("DELETE Request")
        .delete("/posts/1")
        .check(status.is(200))
    )

  setUp(
    scn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}

/**
 * 实验4：响应数据验证
 * 目的：演示如何验证响应内容
 */
class ResponseValidationSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  val scn = scenario("Response Validation Test")
    .exec(
      http("Get Post and Validate")
        .get("/posts/1")
        .check(status.is(200))
        .check(jsonPath("$.userId").is("1")) // 验证JSON路径
        .check(jsonPath("$.title").exists) // 验证字段存在
        .check(responseTimeInMillis.lte(1000)) // 验证响应时间小于1000毫秒
    )

  setUp(
    scn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}

/**
 * 实验5：参数化测试
 * 目的：演示如何使用CSV文件中的测试数据
 */
class ParameterizedSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  // 从CSV文件中读取数据
  val feeder = csv("test_data.csv").random // 随机读取数据

  val scn = scenario("Parameterized Test")
    .feed(feeder) // 注入数据
    .exec(
      http("Get Post by ID")
        .get("/posts/${postId}") // 使用变量
        .check(status.is(200))
        .check(jsonPath("$.id").is("${postId}")) // 验证ID匹配
    )

  setUp(
    scn.inject(atOnceUsers(5))
  ).protocols(httpProtocol)
}

/**
 * 实验6：循环测试
 * 目的：演示如何使用循环执行相同的请求
 */
class LoopSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  val scn = scenario("Loop Test")
    .repeat(5) { // 重复5次
      exec(
        http("Get Random Post")
          .get("/posts/${__randomInt(1, 100)}") // 随机ID
          .check(status.is(200))
      )
      .pause(1)
    }

  setUp(
    scn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}

/**
 * 实验7：条件测试
 * 目的：演示如何根据条件执行不同的操作
 */
class ConditionalSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  val scn = scenario("Conditional Test")
    .exec(
      http("Get Post")
        .get("/posts/1")
        .check(status.is(200))
        .check(jsonPath("$.userId").saveAs("userId")) // 保存userId到变量
    )
    .doIf("${userId}", "1") { // 如果userId等于1
      exec(
        http("Get User")
          .get("/users/${userId}")
          .check(status.is(200))
      )
    }
    .doIfOrElse("${userId}", "1") { // 如果userId等于1
      exec(
        http("Get User 1")
          .get("/users/1")
          .check(status.is(200))
      )
    } { // 否则
      exec(
        http("Get All Users")
          .get("/users")
          .check(status.is(200))
      )
    }

  setUp(
    scn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}

/**
 * 实验8：负载注入模式比较
 * 目的：演示不同的负载注入模式
 */
class LoadInjectionSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")

  val scn = scenario("Load Injection Test")
    .exec(
      http("Get All Posts")
        .get("/posts")
        .check(status.is(200))
    )
    .pause(1, 3)

  setUp(
    scn.inject(
      nothingFor(4 seconds), // 等待4秒
      atOnceUsers(10), // 立即注入10个用户
      rampUsers(20) during (30 seconds), // 30秒内逐渐增加20个用户
      constantUsersPerSec(5) during (20 seconds), // 每秒5个用户，持续20秒
      constantUsersPerSec(5) during (20 seconds) randomized, // 随机分布的每秒5个用户，持续20秒
      rampUsersPerSec(1) to 5 during (20 seconds), // 20秒内从每秒1个用户增加到每秒5个用户
      rampUsersPerSec(5) to 1 during (20 seconds), // 20秒内从每秒5个用户减少到每秒1个用户
      heavisideUsers(100) during (20 seconds) // 20秒内逐渐增加100个用户（正弦曲线）
    )
  ).protocols(httpProtocol)
}

/**
 * 实验9：自定义请求头
 * 目的：演示如何设置自定义请求头
 */
class CustomHeadersSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .header("Custom-Header", "Custom-Value") // 全局自定义头

  val scn = scenario("Custom Headers Test")
    .exec(
      http("Get with Custom Headers")
        .get("/posts/1")
        .header("Request-Specific-Header", "Request-Specific-Value") // 请求特定头
        .check(status.is(200))
    )

  setUp(
    scn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}

/**
 * 实验10：基本认证测试
 * 目的：演示如何使用基本认证
 */
class BasicAuthSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .basicAuth("username", "password") // 基本认证

  val scn = scenario("Basic Auth Test")
    .exec(
      http("Get with Basic Auth")
        .get("/posts/1")
        .check(status.is(200))
    )

  setUp(
    scn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}