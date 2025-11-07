package computerdatabase

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class Chapter3Examples extends Simulation {

  // HTTP协议配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Chapter 3 Examples")

  // ==================== 实验1：创建简单的GET请求测试 ====================
  
  // 场景1：基本GET请求
  val basicGetScenario = scenario("Basic GET Request")
    .exec(
      http("Get All Posts")
        .get("/posts")
        .queryParam("userId", "1") // 添加查询参数
        .header("X-Custom-Header", "Custom-Value") // 添加自定义请求头
        .check(status.is(200)) // 检查状态码
        .check(responseTimeInMillis.lte(1000)) // 检查响应时间
        .check(jsonPath("$[0].userId").is("1")) // 检查响应内容
    )

  // ==================== 实验2：创建POST请求测试 ====================
  
  // 场景2：POST请求
  val postRequestScenario = scenario("POST Request Test")
    .exec(
      http("Create New Post")
        .post("/posts")
        .body(StringBody("""{
          "title": "Gatling Test Post",
          "body": "This is a test post created by Gatling",
          "userId": 1
        }""")).asJson
        .check(status.is(201)) // 检查创建成功状态码
        .check(jsonPath("$.title").is("Gatling Test Post")) // 检查返回的标题
        .check(jsonPath("$.id").saveAs("postId")) // 保存创建的帖子ID
    )
    .pause(1)
    .exec(
      http("Get Created Post")
        .get("/posts/${postId}")
        .check(status.is(200))
        .check(jsonPath("$.title").is("Gatling Test Post"))
    )

  // ==================== 实验3：创建复杂场景测试 ====================
  
  // 场景3：复杂场景
  val complexScenario = scenario("Complex Scenario Test")
    // 初始化Session
    .exec(session => session.set("counter", 1))
    // 获取用户列表
    .exec(
      http("Get Users")
        .get("/users")
        .check(status.is(200))
        .check(jsonPath("$[0].id").saveAs("firstUserId"))
    )
    // 循环获取用户的帖子
    .repeat(3, "iteration") {
      exec(
        http("Get User Posts")
          .get("/posts?userId=${firstUserId}")
          .check(status.is(200))
          .check(jsonPath("$[0].id").saveAs("postId"))
      )
      // 获取帖子的评论
      .exec(
        http("Get Post Comments")
          .get("/comments?postId=${postId}")
          .check(status.is(200))
          .check(jsonPath("$[0].email").saveAs("commentEmail"))
      )
      // 条件执行：如果评论邮箱是特定值，则获取用户信息
      .doIf("${commentEmail}", "Eliseo@gardner.biz") {
        exec(
          http("Get Specific User")
            .get("/users/${firstUserId}")
            .check(status.is(200))
        )
      }
      // 更新计数器
      .exec(session => session.set("counter", session("counter").as[Int] + 1))
      // 随机暂停
      .pause(1, 3)
    }

  // ==================== 实验4：HTTP方法测试 ====================
  
  // 场景4：HTTP方法
  val httpMethodsScenario = scenario("HTTP Methods Test")
    .exec(
      http("GET Request")
        .get("/posts/1")
        .check(status.is(200))
    )
    .pause(1)
    .exec(
      http("POST Request")
        .post("/posts")
        .body(StringBody("""{
          "title": "Test Post",
          "body": "Test body",
          "userId": 1
        }""")).asJson
        .check(status.is(201))
        .check(jsonPath("$.id").saveAs("newPostId"))
    )
    .pause(1)
    .exec(
      http("PUT Request")
        .put("/posts/${newPostId}")
        .body(StringBody("""{
          "id": ${newPostId},
          "title": "Updated Test Post",
          "body": "Updated test body",
          "userId": 1
        }""")).asJson
        .check(status.is(200))
    )
    .pause(1)
    .exec(
      http("DELETE Request")
        .delete("/posts/${newPostId}")
        .check(status.is(200))
    )

  // ==================== 实验5：请求参数和头测试 ====================
  
  // 场景5：请求参数和头
  val paramsAndHeadersScenario = scenario("Request Parameters and Headers Test")
    // 查询参数测试
    .exec(
      http("Query Params Test")
        .get("/posts")
        .queryParam("userId", "1")
        .queryParam("_limit", "5")
        .check(status.is(200))
        .check(jsonPath("$[0].userId").is("1"))
    )
    .pause(1)
    // 路径参数测试
    .exec(
      http("Path Param Test")
        .get("/posts/${postId}")
        .pathParam("postId", "1")
        .check(status.is(200))
        .check(jsonPath("$.id").is("1"))
    )
    .pause(1)
    // 请求头测试
    .exec(
      http("Headers Test")
        .get("/posts/1")
        .header("Accept", "application/json")
        .header("Accept-Language", "en-US")
        .header("Cache-Control", "no-cache")
        .check(status.is(200))
    )
    .pause(1)
    // 基本认证测试
    .exec(
      http("Basic Auth Test")
        .get("/posts/1")
        .basicAuth("user", "pass")
        .check(status.is(200))
    )

  // ==================== 实验6：响应处理测试 ====================
  
  // 场景6：响应处理
  val responseHandlingScenario = scenario("Response Handling Test")
    // 状态码检查
    .exec(
      http("Status Code Check")
        .get("/posts/1")
        .check(status.is(200))
    )
    .pause(1)
    // 响应时间检查
    .exec(
      http("Response Time Check")
        .get("/posts")
        .check(responseTimeInMillis.lte(2000))
    )
    .pause(1)
    // JSON响应检查
    .exec(
      http("JSON Response Check")
        .get("/posts/1")
        .check(jsonPath("$.userId").exists)
        .check(jsonPath("$.id").is("1"))
        .check(jsonPath("$.title").saveAs("postTitle"))
    )
    .pause(1)
    // 响应头检查
    .exec(
      http("Response Headers Check")
        .get("/posts/1")
        .check(header("Content-Type").exists)
        .check(header("Content-Type").is("application/json; charset=utf-8"))
    )

  // ==================== 实验7：循环控制测试 ====================
  
  // 场景7：循环控制
  val loopControlScenario = scenario("Loop Control Test")
    // 固定次数循环
    .repeat(3) {
      exec(
        http("Repeat Request")
          .get("/posts")
          .queryParam("page", "${counter}")
          .check(status.is(200))
      )
    }
    .pause(1)
    // 带计数器的循环
    .repeat(5, "counter") {
      exec(
        http("Counter Request")
          .get("/posts/${counter}")
          .check(status.is(200))
      )
    }
    .pause(1)
    // 遍历集合
    .foreach(Seq("1", "2", "3"), "userId") {
      exec(
        http("ForEach Request")
          .get("/posts?userId=${userId}")
          .check(status.is(200))
      )
    }
    .pause(1)
    // 时间循环
    .during(10 seconds) {
      exec(
        http("During Request")
          .get("/posts/1")
          .check(status.is(200))
      )
      .pause(1)
    }

  // ==================== 实验8：条件控制测试 ====================
  
  // 场景8：条件控制
  val conditionalControlScenario = scenario("Conditional Control Test")
    // 设置条件变量
    .exec(session => session.set("condition", true))
    .exec(session => session.set("case", "case2"))
    // doIf条件
    .doIf("${condition}") {
      exec(
        http("Conditional Request")
          .get("/posts/1")
          .check(status.is(200))
      )
    }
    .pause(1)
    // doIfOrElse条件
    .doIfOrElse("${condition}") {
      exec(
        http("If Request")
          .get("/posts/1")
          .check(status.is(200))
      )
    } {
      exec(
        http("Else Request")
          .get("/posts/2")
          .check(status.is(200))
      )
    }
    .pause(1)
    // doSwitch条件
    .doSwitch("${case}")(
      "case1" -> exec(http("Case 1 Request").get("/posts/1")),
      "case2" -> exec(http("Case 2 Request").get("/posts/2")),
      "default" -> exec(http("Default Request").get("/posts"))
    )
    .pause(1)
    // randomSwitch条件
    .randomSwitch(
      50.0 -> exec(http("50% Request").get("/posts/1")),
      30.0 -> exec(http("30% Request").get("/posts/2")),
      20.0 -> exec(http("20% Request").get("/posts/3"))
    )

  // ==================== 实验9：Session操作测试 ====================
  
  // 场景9：Session操作
  val sessionOperationsScenario = scenario("Session Operations Test")
    // 设置Session变量
    .exec(session => session.set("userId", "1"))
    .exec(session => session.set("userName", "John Doe"))
    // 使用Session变量
    .exec(
      http("Session Variable Request")
        .get("/users/${userId}")
        .check(status.is(200))
        .check(jsonPath("$.name").is("${userName}"))
    )
    .pause(1)
    // 保存响应到Session
    .exec(
      http("Save Response to Session")
        .get("/users/1")
        .check(status.is(200))
        .check(jsonPath("$.email").saveAs("userEmail"))
    )
    .exec(session => {
      println(s"User email: ${session("userEmail").as[String]}")
      session
    })
    .pause(1)
    // 修改Session变量
    .exec(session => session.set("userId", "2"))
    .exec(
      http("Modified Session Variable Request")
        .get("/users/${userId}")
        .check(status.is(200))
    )

  // ==================== 实验10：嵌套结构测试 ====================
  
  // 场景10：嵌套结构
  val nestedStructureScenario = scenario("Nested Structure Test")
    // 嵌套循环
    .repeat(2, "outer") {
      repeat(2, "inner") {
        exec(
          http("Nested Loop Request")
            .get("/posts/${outer}")
            .check(status.is(200))
        )
        .pause(1)
      }
    }
    .pause(2)
    // 嵌套条件
    .exec(session => session.set("condition1", true))
    .exec(session => session.set("condition2", false))
    .doIf("${condition1}") {
      exec(
        http("Outer Condition Request")
          .get("/posts/1")
          .check(status.is(200))
      )
      .doIf("${condition2}") {
        exec(
          http("Inner Condition Request")
            .get("/posts/2")
            .check(status.is(200))
        )
      } {
        exec(
          http("Inner Else Request")
            .get("/posts/3")
            .check(status.is(200))
        )
      }
    }
    .pause(2)
    // 循环与条件嵌套
    .repeat(3) {
      exec(
        http("Loop Request")
          .get("/posts/1")
          .check(status.is(200))
          .check(jsonPath("$.id").saveAs("postId"))
      )
      .doIf("${postId}", "1") {
        exec(
          http("Conditional Request")
            .get("/comments?postId=1")
            .check(status.is(200))
        )
      }
      .pause(1)
    }

  // ==================== 负载配置 ====================
  
  // 运行所有场景
  setUp(
    // 实验1：基本GET请求
    basicGetScenario.inject(
      rampUsers(5) during (10 seconds)
    ).protocols(httpProtocol),
    
    // 实验2：POST请求
    postRequestScenario.inject(
      rampUsers(3) during (10 seconds)
    ).protocols(httpProtocol),
    
    // 实验3：复杂场景
    complexScenario.inject(
      rampUsers(2) during (15 seconds)
    ).protocols(httpProtocol),
    
    // 实验4：HTTP方法
    httpMethodsScenario.inject(
      rampUsers(3) during (10 seconds)
    ).protocols(httpProtocol),
    
    // 实验5：请求参数和头
    paramsAndHeadersScenario.inject(
      rampUsers(3) during (10 seconds)
    ).protocols(httpProtocol),
    
    // 实验6：响应处理
    responseHandlingScenario.inject(
      rampUsers(3) during (10 seconds)
    ).protocols(httpProtocol),
    
    // 实验7：循环控制
    loopControlScenario.inject(
      rampUsers(2) during (15 seconds)
    ).protocols(httpProtocol),
    
    // 实验8：条件控制
    conditionalControlScenario.inject(
      rampUsers(3) during (10 seconds)
    ).protocols(httpProtocol),
    
    // 实验9：Session操作
    sessionOperationsScenario.inject(
      rampUsers(3) during (10 seconds)
    ).protocols(httpProtocol),
    
    // 实验10：嵌套结构
    nestedStructureScenario.inject(
      rampUsers(2) during (15 seconds)
    ).protocols(httpProtocol)
  )
}