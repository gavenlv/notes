# 第3章：Gatling脚本编写与基础测试

## 3.1 Gatling脚本结构

### 3.1.1 基本结构

一个完整的Gatling脚本包含以下几个部分：

```scala
package computerdatabase  // 包名（可选）

import io.gatling.core.Predef._  // 核心导入
import io.gatling.http.Predef._  // HTTP协议导入
import scala.concurrent.duration._  // 时间单位导入

class SimulationName extends Simulation {  // 继承Simulation类
  
  // 1. 协议定义
  val httpProtocol = http
    .baseUrl("https://example.com")
    .acceptHeader("application/json")
  
  // 2. 场景定义
  val scn = scenario("Scenario Name")
    .exec(http("Request Name").get("/path"))
  
  // 3. 负载配置
  setUp(
    scn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)
}
```

### 3.1.2 导入语句

Gatling脚本中常用的导入语句：

```scala
// 核心导入
import io.gatling.core.Predef._

// HTTP协议导入
import io.gatling.http.Predef._

// WebSocket协议导入
import io.gatling.websocket.Predef._

// JMS协议导入
import io.gatling.jms.Predef._

// 时间单位导入
import scala.concurrent.duration._

// JSON处理导入
import io.gatling.http.check.JsonPathChecks

// 正则表达式导入
import io.gatling.http.check.RegexCheck
```

## 3.2 HTTP请求详解

### 3.2.1 HTTP方法

Gatling支持所有常见的HTTP方法：

```scala
// GET请求
http("Get Request").get("/resource")

// POST请求
http("Post Request").post("/resource")

// PUT请求
http("Put Request").put("/resource")

// DELETE请求
http("Delete Request").delete("/resource")

// PATCH请求
http("Patch Request").patch("/resource")

// HEAD请求
http("Head Request").head("/resource")

// OPTIONS请求
http("Options Request").options("/resource")
```

### 3.2.2 请求参数

#### 查询参数

```scala
// 单个查询参数
http("Request with Query Param")
  .get("/resource")
  .queryParam("key1", "value1")

// 多个查询参数
http("Request with Multiple Query Params")
  .get("/resource")
  .queryParam("key1", "value1")
  .queryParam("key2", "value2")

// 多值查询参数
http("Request with Multi-Value Query Param")
  .get("/resource")
  .queryParam("key", "value1")
  .queryParam("key", "value2")

// 使用Map添加查询参数
http("Request with Query Param Map")
  .get("/resource")
  .queryParamMap(Map("key1" -> "value1", "key2" -> "value2"))
```

#### 路径参数

```scala
// 直接在路径中使用变量
http("Request with Path Param")
  .get("/resource/${param}")

// 使用pathParam方法
http("Request with Path Param Method")
  .get("/resource")
  .pathParam("param", "value")
```

#### 请求体

```scala
// 字符串请求体
http("Request with String Body")
  .post("/resource")
  .body(StringBody("""{"key": "value"}"""))

// 文件请求体
http("Request with File Body")
  .post("/resource")
  .body(RawFileBody("data.json"))

// EL文件请求体（支持变量替换）
http("Request with EL File Body")
  .post("/resource")
  .body(ElFileBody("data.json"))

// 表单请求体
http("Request with Form Body")
  .post("/resource")
  .formParam("key1", "value1")
  .formParam("key2", "value2")

// 多部分表单请求体
http("Request with Multipart Form Body")
  .post("/resource")
  .formParam("key1", "value1")
  .formUpload("file", "test.txt")

// 流式请求体
http("Request with Stream Body")
  .post("/resource")
  .body(ByteArrayBody("data".getBytes))
```

### 3.2.3 请求头

```scala
// 单个请求头
http("Request with Header")
  .get("/resource")
  .header("Custom-Header", "Custom-Value")

// 多个请求头
http("Request with Multiple Headers")
  .get("/resource")
  .header("Header1", "Value1")
  .header("Header2", "Value2")

// 使用Map添加请求头
http("Request with Header Map")
  .get("/resource")
  .headers(Map("Header1" -> "Value1", "Header2" -> "Value2"))

// 常用请求头
http("Request with Common Headers")
  .get("/resource")
  .header("Accept", "application/json")
  .header("Content-Type", "application/json")
  .header("User-Agent", "Gatling/3.7.0")
  .header("Authorization", "Bearer token")
```

### 3.2.4 认证

```scala
// 基本认证
http("Request with Basic Auth")
  .get("/resource")
  .basicAuth("username", "password")

// 摘要认证
http("Request with Digest Auth")
  .get("/resource")
  .digestAuth("username", "password")

// OAuth认证
http("Request with OAuth")
  .get("/resource")
  .header("Authorization", "Bearer oauth_token")

// API Key认证
http("Request with API Key")
  .get("/resource")
  .header("X-API-Key", "api_key_value")
```

## 3.3 响应处理

### 3.3.1 状态码检查

```scala
// 检查特定状态码
http("Request with Status Check")
  .get("/resource")
  .check(status.is(200))

// 检查状态码范围
http("Request with Status Range Check")
  .get("/resource")
  .check(status.in(200, 201, 202))

// 检查状态码不在特定值
http("Request with Status Not Check")
  .get("/resource")
  .check(status.not(404))

// 检查状态码在特定范围
http("Request with Status Between Check")
  .get("/resource")
  .check(status.between(200, 299))
```

### 3.3.2 响应时间检查

```scala
// 检查响应时间小于特定值
http("Request with Response Time Check")
  .get("/resource")
  .check(responseTimeInMillis.lte(1000))

// 检查响应时间大于特定值
http("Request with Response Time Greater Check")
  .get("/resource")
  .check(responseTimeInMillis.gte(100))

// 检查响应时间在特定范围
http("Request with Response Time Between Check")
  .get("/resource")
  .check(responseTimeInMillis.between(100, 1000))

// 检查响应时间在特定范围（包含边界）
http("Request with Response Time Inclusive Check")
  .get("/resource")
  .check(responseTimeInMillis.in(100, 1000))
```

### 3.3.3 响应内容检查

```scala
// 检查响应体包含特定字符串
http("Request with Body String Check")
  .get("/resource")
  .check(bodyString.is("Expected Response"))

// 检查响应体包含特定字符串（不区分大小写）
http("Request with Body String Contains Check")
  .get("/resource")
  .check(bodyString.contains("Expected"))

// 检查响应体匹配正则表达式
http("Request with Body Regex Check")
  .get("/resource")
  .check(bodyString.regex("Expected.*Pattern"))

// 检查响应体长度
http("Request with Body Length Check")
  .get("/resource")
  .check(bodyBytes.length.lte(1000))
```

### 3.3.4 JSON响应检查

```scala
// 检查JSON路径存在
http("Request with JSON Path Exists Check")
  .get("/resource")
  .check(jsonPath("$.field").exists)

// 检查JSON路径值
http("Request with JSON Path Value Check")
  .get("/resource")
  .check(jsonPath("$.field").is("value"))

// 检查JSON路径值在特定范围
http("Request with JSON Path Range Check")
  .get("/resource")
  .check(jsonPath("$.numberField").in(1, 2, 3))

// 检查JSON路径值匹配正则表达式
http("Request with JSON Path Regex Check")
  .get("/resource")
  .check(jsonPath("$.stringField").regex("pattern.*"))

// 检查JSON数组长度
http("Request with JSON Array Length Check")
  .get("/resource")
  .check(jsonPath("$.arrayField").ofLength(5))

// 检查JSON数组包含特定值
http("Request with JSON Array Contains Check")
  .get("/resource")
  .check(jsonPath("$.arrayField").find.is("value"))

// 保存JSON路径值到Session
http("Request with JSON Path Save")
  .get("/resource")
  .check(jsonPath("$.field").saveAs("savedValue"))
```

### 3.3.5 XML响应检查

```scala
// 检查XPath存在
http("Request with XPath Exists Check")
  .get("/resource")
  .check(xpath("//field").exists)

// 检查XPath值
http("Request with XPath Value Check")
  .get("/resource")
  .check(xpath("//field").is("value"))

// 检查XPath值在特定范围
http("Request with XPath Range Check")
  .get("/resource")
  .check(xpath("//numberField").in(1, 2, 3))

// 检查XPath值匹配正则表达式
http("Request with XPath Regex Check")
  .get("/resource")
  .check(xpath("//stringField").regex("pattern.*"))

// 保存XPath值到Session
http("Request with XPath Save")
  .get("/resource")
  .check(xpath("//field").saveAs("savedValue"))
```

### 3.3.6 响应头检查

```scala
// 检查响应头存在
http("Request with Header Exists Check")
  .get("/resource")
  .check(header("Content-Type").exists)

// 检查响应头值
http("Request with Header Value Check")
  .get("/resource")
  .check(header("Content-Type").is("application/json"))

// 检查响应头值包含特定字符串
http("Request with Header Contains Check")
  .get("/resource")
  .check(header("Content-Type").contains("application"))

// 检查响应头值匹配正则表达式
http("Request with Header Regex Check")
  .get("/resource")
  .check(header("Content-Type").regex("application/.*"))

// 保存响应头值到Session
http("Request with Header Save")
  .get("/resource")
  .check(header("Content-Type").saveAs("savedContentType"))
```

## 3.4 场景流程控制

### 3.4.1 顺序执行

```scala
val scn = scenario("Sequential Execution")
  .exec(http("Request 1").get("/resource1"))
  .exec(http("Request 2").get("/resource2"))
  .exec(http("Request 3").get("/resource3"))
```

### 3.4.2 暂停

```scala
// 固定暂停时间
val scn = scenario("Fixed Pause")
  .exec(http("Request 1").get("/resource1"))
  .pause(5) // 暂停5秒
  .exec(http("Request 2").get("/resource2"))

// 随机暂停时间范围
val scn = scenario("Random Pause Range")
  .exec(http("Request 1").get("/resource1"))
  .pause(2, 5) // 暂停2-5秒之间的随机时间

// 使用时间单位
val scn = scenario("Pause with Time Unit")
  .exec(http("Request 1").get("/resource1"))
  .pause(500 milliseconds) // 暂停500毫秒
  .pause(2 seconds) // 暂停2秒
  .pause(1 minute) // 暂停1分钟

// 使用支持暂停的配置
val scn = scenario("Pause with Support")
  .exec(http("Request 1").get("/resource1"))
  .pause(5, constantPauses) // 固定暂停5秒
  .pause(2, 5, exponentialPauses) // 指数增长暂停
  .pause(2, 5, uniformPauses) // 均匀分布暂停
```

### 3.4.3 条件执行

```scala
// doIf - 如果条件为真则执行
val scn = scenario("Do If")
  .exec(session => session.set("condition", true))
  .doIf("${condition}") {
    exec(http("Conditional Request").get("/resource"))
  }

// doIfOrElse - 如果条件为真则执行第一个代码块，否则执行第二个代码块
val scn = scenario("Do If Or Else")
  .exec(session => session.set("condition", false))
  .doIfOrElse("${condition}") {
    exec(http("If Request").get("/resource1"))
  } {
    exec(http("Else Request").get("/resource2"))
  }

// doSwitch - 多条件分支
val scn = scenario("Do Switch")
  .exec(session => session.set("case", "case2"))
  .doSwitch("${case}")(
    "case1" -> exec(http("Case 1 Request").get("/resource1")),
    "case2" -> exec(http("Case 2 Request").get("/resource2")),
    "default" -> exec(http("Default Request").get("/default"))
  )

// doSwitchOrElse - 多条件分支，带默认分支
val scn = scenario("Do Switch Or Else")
  .exec(session => session.set("case", "unknown"))
  .doSwitchOrElse("${case}")(
    "case1" -> exec(http("Case 1 Request").get("/resource1")),
    "case2" -> exec(http("Case 2 Request").get("/resource2"))
  ) {
    exec(http("Else Request").get("/else"))
  }

// randomSwitch - 随机分支
val scn = scenario("Random Switch")
  .randomSwitch(
    50.0 -> exec(http("50% Request").get("/resource1")),
    30.0 -> exec(http("30% Request").get("/resource2")),
    20.0 -> exec(http("20% Request").get("/resource3"))
  )

// uniformRandomSwitch - 均匀随机分支
val scn = scenario("Uniform Random Switch")
  .uniformRandomSwitch(
    exec(http("Request 1").get("/resource1")),
    exec(http("Request 2").get("/resource2")),
    exec(http("Request 3").get("/resource3"))
  )
```

### 3.4.4 循环执行

```scala
// repeat - 固定次数循环
val scn = scenario("Repeat Loop")
  .repeat(5) {
    exec(http("Repeated Request").get("/resource"))
  }

// repeat - 带计数器的循环
val scn = scenario("Repeat with Counter")
  .repeat(5, "counter") {
    exec(http("Request ${counter}").get("/resource/${counter}"))
  }

// foreach - 遍历集合
val scn = scenario("ForEach Loop")
  .foreach(Seq("item1", "item2", "item3"), "item") {
    exec(http("Request with ${item}").get("/resource/${item}"))
  }

// during - 时间循环
val scn = scenario("During Loop")
  .during(30 seconds) {
    exec(http("Request during 30s").get("/resource"))
    .pause(1)
  }

// asLongAs - 条件循环
val scn = scenario("As Long As Loop")
  .asLongAs(session => session("counter").as[Int] < 5) {
    exec(session => session.set("counter", session("counter").as[Int] + 1))
    .exec(http("Request ${counter}").get("/resource/${counter}"))
  }

// forever - 无限循环（通常与其他条件结合使用）
val scn = scenario("Forever Loop")
  .forever {
    exec(http("Forever Request").get("/resource"))
    .pause(1)
  }
```

### 3.4.5 嵌套结构

```scala
// 嵌套循环
val scn = scenario("Nested Loops")
  .repeat(3, "outer") {
    repeat(2, "inner") {
      exec(http("Request ${outer}-${inner}").get("/resource/${outer}/${inner}"))
    }
  }

// 嵌套条件
val scn = scenario("Nested Conditions")
  .doIf("${condition1}") {
    exec(http("Request 1").get("/resource1"))
    .doIf("${condition2}") {
      exec(http("Request 2").get("/resource2"))
    }
  }

// 循环与条件嵌套
val scn = scenario("Loop and Condition Nesting")
  .repeat(5) {
    exec(http("Request").get("/resource"))
    .check(jsonPath("$.status").saveAs("status"))
    .doIf("${status}", "success") {
      exec(http("Success Request").get("/success"))
    }
  }
```

## 3.5 实验一：创建简单的GET请求测试

### 实验目标

1. 掌握GET请求的基本用法
2. 学会添加查询参数和请求头
3. 学会检查响应状态和内容

### 实验步骤

1. 创建一个新的Simulation类
2. 定义HTTP协议配置
3. 创建一个简单的GET请求场景
4. 添加查询参数和请求头
5. 添加响应检查
6. 配置负载并运行测试

### 实验代码

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class SimpleGetRequestExperiment extends Simulation {

  // HTTP协议配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Experiment")

  // 场景定义
  val scn = scenario("Simple GET Request")
    .exec(
      http("Get All Posts")
        .get("/posts")
        .queryParam("userId", "1") // 添加查询参数
        .header("X-Custom-Header", "Custom-Value") // 添加自定义请求头
        .check(status.is(200)) // 检查状态码
        .check(responseTimeInMillis.lte(1000)) // 检查响应时间
        .check(jsonPath("$[0].userId").is("1")) // 检查响应内容
    )

  // 负载配置
  setUp(
    scn.inject(
      rampUsers(5) during (10 seconds)
    )
  ).protocols(httpProtocol)
}
```

## 3.6 实验二：创建POST请求测试

### 实验目标

1. 掌握POST请求的基本用法
2. 学会添加请求体
3. 学会检查创建资源的响应

### 实验步骤

1. 创建一个新的Simulation类
2. 定义HTTP协议配置
3. 创建一个POST请求场景
4. 添加JSON请求体
5. 添加响应检查
6. 配置负载并运行测试

### 实验代码

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class PostRequestExperiment extends Simulation {

  // HTTP协议配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .contentTypeHeader("application/json")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Experiment")

  // 场景定义
  val scn = scenario("POST Request Test")
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

  // 负载配置
  setUp(
    scn.inject(
      rampUsers(3) during (10 seconds)
    )
  ).protocols(httpProtocol)
}
```

## 3.7 实验三：创建复杂场景测试

### 实验目标

1. 掌握复杂场景的设计方法
2. 学会使用循环和条件控制流程
3. 学会使用Session存储和传递数据

### 实验步骤

1. 创建一个新的Simulation类
2. 定义HTTP协议配置
3. 创建一个包含多个步骤的复杂场景
4. 使用循环和条件控制流程
5. 使用Session存储和传递数据
6. 配置负载并运行测试

### 实验代码

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class ComplexScenarioExperiment extends Simulation {

  // HTTP协议配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Experiment")

  // 场景定义
  val scn = scenario("Complex Scenario Test")
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

  // 负载配置
  setUp(
    scn.inject(
      rampUsers(5) during (15 seconds)
    )
  ).protocols(httpProtocol)
}
```

## 3.8 本章小结

本章详细介绍了Gatling脚本编写的各个方面，包括脚本结构、HTTP请求、响应处理和场景流程控制。通过三个实验，我们学习了如何创建简单的GET请求、POST请求以及复杂的测试场景。

掌握这些脚本编写技巧是进行有效性能测试的基础。在下一章中，我们将学习如何设计更高级的测试场景，包括多场景组合、负载策略优化和高级数据处理技巧。