# 第2章：Gatling基础概念与核心组件

## 2.1 Gatling架构概述

Gatling采用基于Actor模型的架构设计，主要由以下几个核心组件构成：

1. **Simulation（模拟）**：整个测试的入口点，定义测试场景和负载配置
2. **Scenario（场景）**：定义用户的行为流程
3. **Protocol（协议）**：定义测试使用的协议和相关配置
4. **Injection Profile（负载注入配置）**：定义虚拟用户的生成策略
5. **Feed（数据源）**：为测试提供动态数据

## 2.2 Simulation（模拟）

### 2.2.1 Simulation的概念

Simulation是Gatling测试的顶层容器，它定义了整个测试的配置和结构。每个测试脚本都必须继承`Simulation`类。

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class MySimulation extends Simulation {
  // 测试内容
}
```

### 2.2.2 Simulation的组成

一个完整的Simulation包含以下部分：

1. **协议定义**：定义测试使用的协议配置
2. **场景定义**：定义用户的行为流程
3. **负载配置**：定义虚拟用户的生成策略

### 2.2.3 Simulation的生命周期

1. **初始化阶段**：创建Simulation实例，初始化配置
2. **执行阶段**：按照负载配置执行测试场景
3. **结束阶段**：生成测试报告，清理资源

## 2.3 Scenario（场景）

### 2.3.1 Scenario的概念

Scenario定义了虚拟用户的行为流程，它由一系列的Action组成，模拟真实用户的操作。

```scala
val scn = scenario("Scenario Name")
  .exec(action1)
  .exec(action2)
  .pause(5)
```

### 2.3.2 Scenario的组成元素

1. **Action（动作）**：单个用户操作，如HTTP请求
2. **Pause（暂停）**：模拟用户思考时间
3. **Conditional（条件）**：根据条件执行不同操作
4. **Loop（循环）**：重复执行某些操作
5. **Feed（数据注入）**：为请求提供动态数据

### 2.3.3 Scenario的执行流程

1. **初始化**：创建Scenario实例
2. **执行Action**：按照定义的顺序执行各个Action
3. **处理响应**：处理服务器响应，执行检查
4. **记录数据**：记录测试数据用于生成报告

## 2.4 Protocol（协议）

### 2.4.1 Protocol的概念

Protocol定义了测试使用的协议和相关配置，Gatling支持多种协议：

1. **HTTP Protocol**：用于HTTP/HTTPS测试
2. **JMS Protocol**：用于JMS消息测试
3. **WebSocket Protocol**：用于WebSocket测试

### 2.4.2 HTTP Protocol配置

```scala
val httpProtocol = http
  .baseUrl("https://example.com") // 基础URL
  .acceptHeader("application/json") // 默认请求头
  .userAgentHeader("Gatling/3.7.0") // 用户代理
  .check(status.is(200)) // 全局状态检查
  .disableFollowRedirect // 禁用自动重定向
  .maxRedirects(5) // 最大重定向次数
  .connectionHeader("keep-alive") // 连接头
  .silentResources // 静默资源
  .disableWarmUp // 禁用预热
  .http2Enabled // 启用HTTP/2
```

### 2.4.3 Protocol的作用域

Protocol可以在不同级别定义：

1. **全局级别**：在Simulation级别定义，应用于所有场景
2. **场景级别**：在Scenario级别定义，仅应用于当前场景
3. **请求级别**：在单个请求中定义，仅应用于当前请求

## 2.5 Injection Profile（负载注入配置）

### 2.5.1 Injection Profile的概念

Injection Profile定义了虚拟用户的生成策略，包括用户数量、生成速度和持续时间等。

### 2.5.2 常见的注入模式

1. **atOnceUsers(n)**：立即注入n个用户
2. **rampUsers(n) during(d)**：在d时间内逐渐注入n个用户
3. **constantUsersPerSec(rate) during(d)**：每秒注入rate个用户，持续d时间
4. **rampUsersPerSec(rate1) to(rate2) during(d)**：在d时间内从每秒rate1个用户增加到rate2个用户
5. **heavisideUsers(n) during(d)**：在d时间内以正弦曲线逐渐注入n个用户
6. **nothingFor(d)**：等待d时间后开始注入用户

### 2.5.3 组合注入模式

可以组合多种注入模式创建复杂的负载配置：

```scala
setUp(
  scn.inject(
    nothingFor(4 seconds), // 等待4秒
    atOnceUsers(10), // 立即注入10个用户
    rampUsers(20) during (30 seconds), // 30秒内逐渐增加20个用户
    constantUsersPerSec(5) during (20 seconds) // 每秒5个用户，持续20秒
  )
).protocols(httpProtocol)
```

## 2.6 Action（动作）

### 2.6.1 Action的概念

Action是Scenario的基本组成单元，表示单个用户操作。在HTTP测试中，最常见的Action是HTTP请求。

### 2.6.2 HTTP Action的组成

一个HTTP Action包含以下部分：

1. **请求方法**：GET、POST、PUT、DELETE等
2. **请求路径**：相对于baseUrl的路径
3. **请求参数**：查询参数、路径参数等
4. **请求头**：自定义请求头
5. **请求体**：POST/PUT请求的数据
6. **检查**：验证响应内容

### 2.6.3 HTTP Action示例

```scala
http("Request Name")
  .get("/posts/1") // 请求方法和路径
  .queryParam("param1", "value1") // 查询参数
  .header("Custom-Header", "Custom-Value") // 自定义请求头
  .body(StringBody("""{"key": "value"}""")).asJson // 请求体
  .check(status.is(200)) // 状态检查
  .check(jsonPath("$.userId").is("1")) // 响应内容检查
```

## 2.7 Check（检查）

### 2.7.1 Check的概念

Check用于验证服务器响应是否符合预期，是测试成功与否的关键。

### 2.7.2 常见的检查类型

1. **状态检查**：验证HTTP状态码
2. **响应时间检查**：验证响应时间
3. **响应内容检查**：验证响应内容
4. **响应头检查**：验证响应头
5. **JSON/XML检查**：验证JSON/XML内容

### 2.7.3 Check示例

```scala
http("Request Name")
  .get("/api/resource")
  .check(status.is(200)) // 状态码检查
  .check(responseTimeInMillis.lte(1000)) // 响应时间检查
  .check(bodyString.is("Expected Response")) // 响应内容检查
  .check(header("Content-Type").is("application/json")) // 响应头检查
  .check(jsonPath("$.field").is("value")) // JSON检查
  .check(xpath("//field").is("value")) // XML检查
```

## 2.8 Feed（数据源）

### 2.8.1 Feed的概念

Feed用于为测试提供动态数据，可以从文件、数据库或其他数据源中读取数据。

### 2.8.2 常见的Feed类型

1. **CSV Feed**：从CSV文件中读取数据
2. **JSON Feed**：从JSON文件中读取数据
3. **JDBC Feed**：从数据库中读取数据
4. **Redis Feed**：从Redis中读取数据
5. **自定义Feed**：自定义数据源

### 2.8.3 Feed示例

```scala
// CSV Feed
val csvFeeder = csv("data.csv").random // 随机读取
val csvFeederCircular = csv("data.csv").circular // 循环读取

// JSON Feed
val jsonFeeder = jsonFile("data.json").random

// 使用Feed
val scn = scenario("Feed Example")
  .feed(csvFeeder) // 注入数据
  .exec(http("Request with Data")
    .get("/resource/${param}") // 使用变量
  )
```

## 2.9 Session（会话）

### 2.9.1 Session的概念

Session是Gatling中用于存储和传递数据的机制，每个虚拟用户都有自己的Session。

### 2.9.2 Session的组成

1. **用户ID**：唯一标识虚拟用户
2. **开始时间**：用户开始时间
3. **属性**：存储用户相关的数据
4. **计数器**：用于计数和循环

### 2.9.3 Session操作

```scala
// 设置Session属性
exec(session => session.set("key", "value"))

// 获取Session属性
exec(session => {
  val value = session("key").as[String]
  session
})

// 移除Session属性
.exec(session => session.remove("key"))

// 重置Session
exec(session => session.reset)
```

## 2.10 Assertion（断言）

### 2.10.1 Assertion的概念

Assertion用于在测试结束后验证整体测试结果是否符合预期。

### 2.10.2 常见的断言类型

1. **全局断言**：验证整个测试的结果
2. **响应时间断言**：验证响应时间
3. **成功率断言**：验证请求成功率
4. **请求数断言**：验证请求总数

### 2.10.3 Assertion示例

```scala
setUp(
  scn.inject(atOnceUsers(10))
).protocols(httpProtocol)
.assertions(
  global.responseTime.max.lt(1000), // 最大响应时间小于1000毫秒
  global.successfulRequests.percent.gt(95), // 成功率大于95%
  global.requestsPerSec.gt(100) // 每秒请求数大于100
)
```

## 2.11 实验一：理解Simulation和Scenario

### 实验目标

1. 理解Simulation的基本结构
2. 掌握Scenario的组成和执行流程
3. 学会创建简单的测试场景

### 实验步骤

1. 创建一个新的Simulation类
2. 定义HTTP协议配置
3. 创建一个简单的Scenario
4. 配置负载注入
5. 运行测试并分析结果

### 实验代码

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

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
```

## 2.12 实验二：探索不同的负载注入模式

### 实验目标

1. 理解不同的负载注入模式
2. 掌握如何组合多种注入模式
3. 学会根据测试需求选择合适的注入模式

### 实验步骤

1. 创建多个Scenario，每个使用不同的注入模式
2. 比较不同注入模式的测试结果
3. 组合多种注入模式创建复杂负载

### 实验代码

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

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
```

## 2.13 实验三：使用Feed实现数据驱动测试

### 实验目标

1. 理解Feed的概念和作用
2. 掌握如何从CSV文件中读取数据
3. 学会在测试中使用动态数据

### 实验步骤

1. 创建测试数据CSV文件
2. 定义Feed并配置读取策略
3. 在Scenario中使用Feed数据
4. 运行测试并验证结果

### 实验代码

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

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
```

## 2.14 本章小结

本章详细介绍了Gatling的基础概念和核心组件，包括Simulation、Scenario、Protocol、Injection Profile、Action、Check、Feed、Session和Assertion。通过三个实验，我们深入理解了这些概念的实际应用。

掌握这些基础概念是编写高效、可靠的Gatling测试脚本的关键。在下一章中，我们将学习如何编写更复杂的Gatling脚本和基础测试，进一步探索Gatling的强大功能。