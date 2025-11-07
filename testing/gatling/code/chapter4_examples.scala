package computerdatabase

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class Chapter4Examples extends Simulation {

  // HTTP协议配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Chapter 4 Examples")

  // ==================== 实验1：多场景组合测试 ====================
  
  // 场景1：浏览商品
  val browseScenario = scenario("Browse Products")
    .exec(
      http("Get All Posts")
        .get("/posts")
        .check(status.is(200))
    )
    .pause(2, 5)
    .exec(
      http("Get Post Details")
        .get("/posts/1")
        .check(status.is(200))
    )
    .pause(2, 5)
    .exec(
      http("Get Comments")
        .get("/comments?postId=1")
        .check(status.is(200))
    )

  // 场景2：搜索商品
  val searchScenario = scenario("Search Products")
    .exec(
      http("Get Users")
        .get("/users")
        .check(status.is(200))
    )
    .pause(1, 3)
    .exec(
      http("Get User Posts")
        .get("/posts?userId=1")
        .check(status.is(200))
    )
    .pause(1, 3)
    .exec(
      http("Get User Details")
        .get("/users/1")
        .check(status.is(200))
    )

  // 场景3：结账流程
  val checkoutScenario = scenario("Checkout Process")
    .exec(
      http("Create Post")
        .post("/posts")
        .body(StringBody("""{
          "title": "Test Product",
          "body": "Test Description",
          "userId": 1
        }""")).asJson
        .check(status.is(201))
        .check(jsonPath("$.id").saveAs("postId"))
    )
    .pause(1, 3)
    .exec(
      http("Create Comment")
        .post("/comments")
        .body(StringBody("""{
          "postId": ${postId},
          "name": "Test User",
          "email": "test@example.com",
          "body": "Test Comment"
        }""")).asJson
        .check(status.is(201))
    )
    .pause(3, 5)
    .exec(
      http("Get Created Post")
        .get("/posts/${postId}")
        .check(status.is(200))
    )

  // ==================== 实验2：场景链式组合 ====================
  
  // 定义基础场景
  val loginScenario = scenario("Login")
    .exec(
      http("Login Page")
        .get("/users/1")
        .check(status.is(200))
        .check(jsonPath("$.id").is("1"))
        .check(jsonPath("$.name").saveAs("userName"))
    )
    .pause(2)
    .exec(session => {
      println(s"Logged in as: ${session("userName").as[String]}")
      session
    })

  val browseProductsScenario = scenario("Browse Products")
    .exec(
      http("Products Page")
        .get("/posts")
        .check(status.is(200))
    )
    .pause(2, 5)
    .exec(
      http("Product Details")
        .get("/posts/1")
        .check(status.is(200))
    )
    .pause(2, 5)
    .exec(
      http("Product Details")
        .get("/posts/2")
        .check(status.is(200))
    )

  val checkoutScenario2 = scenario("Checkout Process 2")
    .exec(
      http("Cart Page")
        .get("/posts/1")
        .check(status.is(200))
    )
    .pause(2, 4)
    .exec(
      http("Checkout")
        .post("/comments")
        .body(StringBody("""{
          "postId": 1,
          "name": "Customer",
          "email": "customer@example.com",
          "body": "Order placed"
        }""")).asJson
        .check(status.is(201))
    )
    .pause(3, 5)
    .exec(
      http("Place Order")
        .get("/comments/1")
        .check(status.is(200))
    )

  // 组合场景
  val fullUserJourneyScenario = scenario("Full User Journey")
    .exec(loginScenario)
    .pause(5, 10)
    .exec(browseProductsScenario)
    .pause(10, 15)
    .exec(checkoutScenario2)

  // ==================== 实验3：场景条件组合 ====================
  
  // 定义条件场景
  val premiumUserScenario = scenario("Premium User Flow")
    .exec(
      http("Premium Features")
        .get("/posts/1")
        .check(status.is(200))
    )
    .pause(2, 4)
    .exec(
      http("Exclusive Content")
        .get("/comments?postId=1")
        .check(status.is(200))
    )

  val regularUserScenario = scenario("Regular User Flow")
    .exec(
      http("Regular Features")
        .get("/posts")
        .check(status.is(200))
    )
    .pause(2, 4)
    .exec(
      http("Standard Content")
        .get("/users")
        .check(status.is(200))
    )

  // 主场景，根据用户类型选择子场景
  val mainScenario = scenario("Conditional User Flow")
    .feed(csv("users.csv").random) // 加载用户数据，包含userType字段
    .doSwitch("${userType}")(
      "premium" -> exec(premiumUserScenario),
      "regular" -> exec(regularUserScenario),
      "default" -> exec(regularUserScenario)
    )

  // ==================== 实验4：负载注入策略 ====================
  
  // 测试场景
  val loadTestScenario = scenario("Load Injection Test")
    .exec(
      http("Get Posts")
        .get("/posts")
        .check(status.is(200))
    )
    .pause(1, 3)
    .exec(
      http("Get Users")
        .get("/users")
        .check(status.is(200))
    )
    .pause(1, 3)
    .exec(
      http("Get Comments")
        .get("/comments")
        .check(status.is(200))
    )

  // ==================== 实验5：思考时间模拟 ====================
  
  // 固定暂停时间
  val fixedPauseScenario = scenario("Fixed Pause")
    .exec(
      http("Request 1")
        .get("/posts/1")
        .check(status.is(200))
    )
    .pause(5) // 暂停5秒
    .exec(
      http("Request 2")
        .get("/posts/2")
        .check(status.is(200))
    )

  // 随机暂停时间范围
  val randomPauseScenario = scenario("Random Pause")
    .exec(
      http("Request 1")
        .get("/posts/1")
        .check(status.is(200))
    )
    .pause(2, 5) // 暂停2-5秒之间的随机时间
    .exec(
      http("Request 2")
        .get("/posts/2")
        .check(status.is(200))
    )

  // 基于响应时间的动态暂停
  val dynamicPauseScenario = scenario("Dynamic Pause")
    .exec(
      http("Request 1")
        .get("/posts/1")
        .check(status.is(200))
        .check(responseTimeInMillis.saveAs("responseTime"))
    )
    .exec(session => {
      // 根据响应时间计算暂停时间
      val responseTime = session("responseTime").as[Long]
      val pauseTime = if (responseTime > 1000) 5 else 2
      session.set("pauseTime", pauseTime)
    })
    .pause("${pauseTime}") // 使用动态计算的暂停时间
    .exec(
      http("Request 2")
        .get("/posts/2")
        .check(status.is(200))
    )

  // ==================== 实验6：CSV数据源 ====================
  
  // CSV数据源
  val csvFeeder = csv("posts.csv").random

  // 场景：使用CSV数据
  val csvScenario = scenario("CSV Data Test")
    .feed(csvFeeder)
    .exec(
      http("Get Post with CSV Data")
        .get("/posts/${postId}")
        .check(status.is(200))
        .check(jsonPath("$.userId").is("${userId}"))
    )
    .pause(1, 2)

  // ==================== 实验7：JSON数据源 ====================
  
  // JSON数据源
  val jsonFeeder = jsonFile("users.json").random

  // 场景：使用JSON数据
  val jsonScenario = scenario("JSON Data Test")
    .feed(jsonFeeder)
    .exec(
      http("Get User with JSON Data")
        .get("/users/${userId}")
        .check(status.is(200))
        .check(jsonPath("$.name").is("${name}"))
    )
    .pause(1, 2)

  // ==================== 实验8：自定义数据源 ====================
  
  // 自定义数据源
  val customFeeder = Iterator.continually(Map(
    "postId" -> scala.util.Random.nextInt(100),
    "userId" -> (1 + scala.util.Random.nextInt(10)),
    "timestamp" -> System.currentTimeMillis()
  ))

  // 场景：使用自定义数据
  val customScenario = scenario("Custom Data Test")
    .feed(customFeeder)
    .exec(
      http("Get Post with Custom Data")
        .get("/posts/${postId}")
        .check(status.is(200))
    )
    .pause(1, 2)
    .exec(
      http("Get User with Custom Data")
        .get("/users/${userId}")
        .check(status.is(200))
    )
    .pause(1, 2)

  // ==================== 实验9：多数据源组合 ====================
  
  // 多个CSV文件
  val postsFeeder = csv("posts.csv").random
  val usersFeeder = csv("users.csv").random

  // 场景：使用多个数据源
  val multiFeederScenario = scenario("Multiple Data Sources Test")
    .feed(usersFeeder)
    .feed(postsFeeder)
    .exec(
      http("Request with Multiple Data")
        .get("/users/${userId}/posts")
        .check(status.is(200))
    )
    .pause(1, 2)
    .exec(
      http("Request with Post Data")
        .get("/posts/${postId}")
        .check(status.is(200))
    )

  // ==================== 实验10：高级负载注入策略 ====================
  
  // 阶梯式注入
  val stepLoadScenario = scenario("Step Load Test")
    .exec(
      http("Step Load Request")
        .get("/posts")
        .check(status.is(200))
    )
    .pause(1, 2)

  // ==================== 负载配置 ====================
  
  // 运行所有场景
  setUp(
    // 实验1：多场景组合测试
    browseScenario.inject(rampUsers(7) during (15 seconds)).protocols(httpProtocol),
    searchScenario.inject(rampUsers(2) during (15 seconds)).protocols(httpProtocol),
    checkoutScenario.inject(rampUsers(1) during (15 seconds)).protocols(httpProtocol),
    
    // 实验2：场景链式组合
    fullUserJourneyScenario.inject(rampUsers(3) during (15 seconds)).protocols(httpProtocol),
    
    // 实验3：场景条件组合
    mainScenario.inject(rampUsers(5) during (15 seconds)).protocols(httpProtocol),
    
    // 实验4：负载注入策略
    loadTestScenario.inject(
      nothingFor(5 seconds),              // 前5秒不注入用户
      atOnceUsers(2),                     // 立即注入2个用户
      rampUsers(4) during (10 seconds),   // 10秒内线性注入4个用户
      constantUsersPerSec(1) during (15 seconds), // 15秒内每秒注入1个用户
      rampUsers(6) during (20 seconds)     // 20秒内线性注入6个用户
    ).protocols(httpProtocol),
    
    // 实验5：思考时间模拟
    fixedPauseScenario.inject(rampUsers(2) during (10 seconds)).protocols(httpProtocol),
    randomPauseScenario.inject(rampUsers(2) during (10 seconds)).protocols(httpProtocol),
    dynamicPauseScenario.inject(rampUsers(2) during (10 seconds)).protocols(httpProtocol),
    
    // 实验6：CSV数据源
    csvScenario.inject(rampUsers(3) during (10 seconds)).protocols(httpProtocol),
    
    // 实验7：JSON数据源
    jsonScenario.inject(rampUsers(3) during (10 seconds)).protocols(httpProtocol),
    
    // 实验8：自定义数据源
    customScenario.inject(rampUsers(3) during (10 seconds)).protocols(httpProtocol),
    
    // 实验9：多数据源组合
    multiFeederScenario.inject(rampUsers(3) during (10 seconds)).protocols(httpProtocol),
    
    // 实验10：高级负载注入策略
    stepLoadScenario.inject(
      incrementUsersPerSec(2) // 每秒增加2个用户
        .times(3) // 重复3次
        .eachLevelLasting(10 seconds) // 每个阶梯持续10秒
        .separatedByRampsLasting(5 seconds) // 阶梯之间间隔5秒
        .startingFrom(1) // 从每秒1个用户开始
    ).protocols(httpProtocol)
  )
}