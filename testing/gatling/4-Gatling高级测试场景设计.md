# 第4章：Gatling高级测试场景设计

## 4.1 多场景组合

### 4.1.1 场景权重分配

在性能测试中，我们经常需要模拟不同用户行为模式的组合。Gatling允许我们定义多个场景，并为每个场景分配不同的权重。

```scala
// 定义多个场景
val browseScenario = scenario("Browse Products")
  .exec(http("Home Page").get("/"))
  .pause(2, 5)
  .exec(http("Products Page").get("/products"))
  .pause(2, 5)
  .exec(http("Product Details").get("/products/1"))

val searchScenario = scenario("Search Products")
  .exec(http("Home Page").get("/"))
  .pause(1, 3)
  .exec(http("Search").get("/search?q=laptop"))
  .pause(1, 3)
  .exec(http("Search Results").get("/search/results"))

val checkoutScenario = scenario("Checkout Process")
  .exec(http("Home Page").get("/"))
  .pause(1, 2)
  .exec(http("Products Page").get("/products"))
  .pause(2, 4)
  .exec(http("Add to Cart").post("/cart/add").formParam("productId", "1"))
  .pause(1, 3)
  .exec(http("Checkout").get("/checkout"))
  .pause(3, 5)
  .exec(http("Place Order").post("/checkout/place"))

// 设置负载配置，分配不同权重
setUp(
  browseScenario.inject(rampUsers(70) during (60 seconds)), // 70%用户浏览
  searchScenario.inject(rampUsers(20) during (60 seconds)), // 20%用户搜索
  checkoutScenario.inject(rampUsers(10) during (60 seconds)) // 10%用户结账
).protocols(httpProtocol)
```

### 4.1.2 场景链式组合

有时我们需要将多个场景链接在一起，形成一个更复杂的用户行为流程。

```scala
// 定义基础场景
val loginScenario = scenario("Login")
  .exec(http("Login Page").get("/login"))
  .pause(2)
  .exec(
    http("Login Action")
      .post("/login")
      .formParam("username", "user1")
      .formParam("password", "pass1")
      .check(status.is(302)) // 重定向到主页
      .check(header("Location").saveAs("redirectUrl"))
  )
  .exec(http("Redirect").get("${redirectUrl}"))
  .check(status.is(200))

val browseProductsScenario = scenario("Browse Products")
  .exec(http("Products Page").get("/products"))
  .pause(2, 5)
  .exec(http("Product Details").get("/products/1"))
  .pause(2, 5)
  .exec(http("Product Details").get("/products/2"))

val checkoutScenario = scenario("Checkout Process")
  .exec(http("Cart Page").get("/cart"))
  .pause(2, 4)
  .exec(http("Checkout").get("/checkout"))
  .pause(3, 5)
  .exec(http("Place Order").post("/checkout/place"))

// 组合场景
val fullUserJourneyScenario = scenario("Full User Journey")
  .exec(loginScenario)
  .pause(5, 10)
  .exec(browseProductsScenario)
  .pause(10, 15)
  .exec(checkoutScenario)

// 设置负载配置
setUp(
  fullUserJourneyScenario.inject(rampUsers(20) during (60 seconds))
).protocols(httpProtocol)
```

### 4.1.3 场景条件组合

我们可以根据条件动态选择执行不同的场景。

```scala
// 定义条件场景
val premiumUserScenario = scenario("Premium User Flow")
  .exec(http("Premium Features").get("/premium"))
  .pause(2, 4)
  .exec(http("Exclusive Content").get("/premium/exclusive"))

val regularUserScenario = scenario("Regular User Flow")
  .exec(http("Regular Features").get("/features"))
  .pause(2, 4)
  .exec(http("Standard Content").get("/content"))

// 主场景，根据用户类型选择子场景
val mainScenario = scenario("Conditional User Flow")
  .feed(csv("users.csv").random) // 加载用户数据，包含userType字段
  .doSwitch("${userType}")(
    "premium" -> exec(premiumUserScenario),
    "regular" -> exec(regularUserScenario),
    "default" -> exec(regularUserScenario)
  )

// 设置负载配置
setUp(
  mainScenario.inject(rampUsers(50) during (60 seconds))
).protocols(httpProtocol)
```

## 4.2 负载注入策略

### 4.2.1 基本负载注入模式

Gatling提供了多种负载注入模式，以模拟不同的用户行为和负载情况。

```scala
// 立即注入所有用户
setUp(
  scn.inject(atOnceUsers(100))
).protocols(httpProtocol)

// 线性增长注入用户
setUp(
  scn.inject(rampUsers(100) during (30 seconds))
).protocols(httpProtocol)

// 阶梯式增长
setUp(
  scn.inject(
    incrementUsersPerSec(10) // 每秒增加10个用户
      .times(5) // 重复5次
      .eachLevelLasting(10 seconds) // 每个阶梯持续10秒
      .separatedByRampsLasting(5 seconds) // 阶梯之间间隔5秒
      .startingFrom(10) // 从每秒10个用户开始
  )
).protocols(httpProtocol)

// 恒定速率
setUp(
  scn.inject(constantUsersPerSec(20) during (60 seconds))
).protocols(httpProtocol)

// 随机注入
setUp(
  scn.inject(
    splitUsers(100) into (rampUsers(10) during (5 seconds)) separatedBy (10 seconds)
  )
).protocols(httpProtocol)

// 复杂注入组合
setUp(
  scn.inject(
    nothingFor(5 seconds), // 前5秒不注入用户
    atOnceUsers(10), // 立即注入10个用户
    rampUsers(50) during (20 seconds), // 20秒内线性注入50个用户
    constantUsersPerSec(20) during (30 seconds), // 30秒内每秒注入20个用户
    rampUsers(100) during (40 seconds) // 40秒内线性注入100个用户
  )
).protocols(httpProtocol)
```

### 4.2.2 高级负载注入模式

Gatling 3.7+引入了更高级的负载注入模式，可以更精确地控制负载。

```scala
// 阶梯式注入（新版本）
setUp(
  scn.inject(
    stressPeakUsers(100) during (60 seconds) // 60秒内达到100个用户的压力峰值
  )
).protocols(httpProtocol)

// 复杂阶梯式注入
setUp(
  scn.inject(
    incrementConcurrentUsers(5) // 每次增加5个并发用户
      .times(10) // 重复10次
      .eachLevelLasting(15 seconds) // 每个级别持续15秒
      .separatedByRampsLasting(10 seconds) // 级别之间间隔10秒
      .startingFrom(5) // 从5个并发用户开始
  )
).protocols(httpProtocol)

// 自定义负载注入
val customInjection = injection.Sequence(
  injection.Step(
    injection.Pace(1.second), // 每秒注入一个用户
    30.seconds, // 持续30秒
    "Warm-up" // 阶段名称
  ),
  injection.Step(
    injection.Ramp(10.users, 30.seconds), // 30秒内从0增加到10个用户
    60.seconds, // 持续60秒
    "Ramp-up"
  ),
  injection.Step(
    injection.Hold(10.users), // 保持10个用户
    120.seconds, // 持续120秒
    "Steady State"
  ),
  injection.Step(
    injection.Ramp(0.users, 30.seconds), // 30秒内从10个用户减少到0
    30.seconds, // 持续30秒
    "Ramp-down"
  )
)

setUp(
  scn.inject(customInjection)
).protocols(httpProtocol)
```

## 4.3 思考时间模拟

### 4.3.1 固定和随机暂停

在真实用户行为中，用户在操作之间会有思考时间。Gatling提供了多种方式来模拟这种行为。

```scala
// 固定暂停时间
val scn = scenario("Fixed Pause")
  .exec(http("Request 1").get("/resource1"))
  .pause(5) // 暂停5秒
  .exec(http("Request 2").get("/resource2"))

// 随机暂停时间范围
val scn = scenario("Random Pause")
  .exec(http("Request 1").get("/resource1"))
  .pause(2, 5) // 暂停2-5秒之间的随机时间
  .exec(http("Request 2").get("/resource2"))

// 使用时间单位
val scn = scenario("Time Unit Pause")
  .exec(http("Request 1").get("/resource1"))
  .pause(500 milliseconds) // 暂停500毫秒
  .pause(2 seconds) // 暂停2秒
  .pause(1 minute) // 暂停1分钟
  .exec(http("Request 2").get("/resource2"))
```

### 4.3.2 高级暂停策略

Gatling提供了更高级的暂停策略，以更真实地模拟用户行为。

```scala
// 指数分布暂停
val scn = scenario("Exponential Pause")
  .exec(http("Request 1").get("/resource1"))
  .pause(5, exponentialPauses) // 指数分布暂停
  .exec(http("Request 2").get("/resource2"))

// 均匀分布暂停
val scn = scenario("Uniform Pause")
  .exec(http("Request 1").get("/resource1"))
  .pause(5, uniformPauses) // 均匀分布暂停
  .exec(http("Request 2").get("/resource2"))

// 正态分布暂停
val scn = scenario("Normal Pause")
  .exec(http("Request 1").get("/resource1"))
  .pause(5, normalPausesWithStdDev(2)) // 正态分布暂停，标准差为2
  .exec(http("Request 2").get("/resource2"))

// 自定义暂停分布
val scn = scenario("Custom Pause")
  .exec(http("Request 1").get("/resource1"))
  .pause(5, customPauses(() => scala.util.Random.nextInt(10))) // 自定义暂停分布
  .exec(http("Request 2").get("/resource2"))
```

### 4.3.3 基于响应的动态暂停

我们可以根据响应内容或响应时间动态调整暂停时间。

```scala
// 基于响应时间的动态暂停
val scn = scenario("Response Time Based Pause")
  .exec(
    http("Request 1")
      .get("/resource1")
      .check(responseTimeInMillis.saveAs("responseTime"))
  )
  .exec(session => {
    // 根据响应时间计算暂停时间
    val responseTime = session("responseTime").as[Long]
    val pauseTime = if (responseTime > 1000) 5 else 2
    session.set("pauseTime", pauseTime)
  })
  .pause("${pauseTime}") // 使用动态计算的暂停时间
  .exec(http("Request 2").get("/resource2"))

// 基于响应内容的动态暂停
val scn = scenario("Response Content Based Pause")
  .exec(
    http("Request 1")
      .get("/resource1")
      .check(jsonPath("$.status").saveAs("status"))
  )
  .exec(session => {
    // 根据响应状态计算暂停时间
    val status = session("status").as[String]
    val pauseTime = if (status == "success") 2 else 5
    session.set("pauseTime", pauseTime)
  })
  .pause("${pauseTime}") // 使用动态计算的暂停时间
  .exec(http("Request 2").get("/resource2"))
```

## 4.4 数据驱动测试

### 4.4.1 CSV数据源

CSV是Gatling中最常用的数据源，可以轻松加载测试数据。

```scala
// 加载CSV文件
val csvFeeder = csv("data.csv") // 默认循环策略
val csvFeederRandom = csv("data.csv").random // 随机选择
val csvFeederQueue = csv("data.csv").queue // 队列策略，用完后停止
val csvFeederShuffle = csv("data.csv").shuffle // 随机打乱，然后循环

// 使用CSV数据
val scn = scenario("CSV Data Test")
  .feed(csvFeeder)
  .exec(http("Request with Data")
    .get("/resource/${id}")
    .queryParam("name", "${name}")
  )

// 多个CSV文件
val usersFeeder = csv("users.csv").random
val productsFeeder = csv("products.csv").random

val scn = scenario("Multiple CSV Test")
  .feed(usersFeeder)
  .feed(productsFeeder)
  .exec(http("Request with Multiple Data")
    .get("/users/${userId}/products/${productId}")
  )
```

### 4.4.2 JSON数据源

除了CSV，Gatling也支持JSON格式的数据源。

```scala
// 加载JSON文件
val jsonFeeder = jsonFile("data.json")
val jsonFeederRandom = jsonFile("data.json").random

// 使用JSON数据
val scn = scenario("JSON Data Test")
  .feed(jsonFeederRandom)
  .exec(http("Request with JSON Data")
    .get("/resource/${id}")
    .queryParam("name", "${name}")
    .queryParam("category", "${details.category}")
  )
```

### 4.4.3 JDBC数据源

Gatling可以从数据库直接加载测试数据。

```scala
// 配置JDBC数据源
val jdbcFeeder = jdbcFeeder("jdbc:mysql://localhost:3306/testdb", "user", "password", 
  "SELECT id, name, email FROM users")

// 使用JDBC数据
val scn = scenario("JDBC Data Test")
  .feed(jdbcFeeder)
  .exec(http("Request with DB Data")
    .get("/users/${id}")
    .check(status.is(200))
  )
```

### 4.4.4 自定义数据源

我们也可以创建自定义的数据源。

```scala
// 创建自定义Feeder
val customFeeder = Iterator.continually(Map(
  "id" -> scala.util.Random.nextInt(1000),
  "name" -> s"user-${scala.util.Random.nextInt(1000)}",
  "timestamp" -> System.currentTimeMillis()
))

// 使用自定义数据
val scn = scenario("Custom Data Test")
  .feed(customFeeder)
  .exec(http("Request with Custom Data")
    .get("/resource/${id}")
    .queryParam("name", "${name}")
    .queryParam("timestamp", "${timestamp}")
  )
```

## 4.5 实验一：多场景组合测试

### 实验目标

1. 掌握多场景组合的方法
2. 学会为不同场景分配权重
3. 学会场景链式组合

### 实验步骤

1. 创建三个不同的场景：浏览商品、搜索商品、结账流程
2. 为每个场景分配不同的权重
3. 设置负载配置并运行测试
4. 分析测试结果

### 实验代码

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class MultiScenarioExperiment extends Simulation {

  // HTTP协议配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Multi-Scenario Experiment")

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

  // 负载配置，分配不同权重
  setUp(
    browseScenario.inject(rampUsers(14) during (30 seconds)), // 70%用户浏览
    searchScenario.inject(rampUsers(4) during (30 seconds)),  // 20%用户搜索
    checkoutScenario.inject(rampUsers(2) during (30 seconds))  // 10%用户结账
  ).protocols(httpProtocol)
}
```

## 4.6 实验二：负载注入策略测试

### 实验目标

1. 掌握不同的负载注入策略
2. 学会组合多种注入策略
3. 理解不同策略对测试结果的影响

### 实验步骤

1. 创建一个简单的测试场景
2. 使用多种负载注入策略
3. 比较不同策略的测试结果
4. 分析最适合的注入策略

### 实验代码

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class LoadInjectionExperiment extends Simulation {

  // HTTP协议配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Load Injection Experiment")

  // 测试场景
  val scn = scenario("Load Injection Test")
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

  // 负载配置 - 复杂注入组合
  setUp(
    scn.inject(
      nothingFor(5 seconds),              // 前5秒不注入用户
      atOnceUsers(5),                     // 立即注入5个用户
      rampUsers(10) during (20 seconds),  // 20秒内线性注入10个用户
      constantUsersPerSec(2) during (30 seconds), // 30秒内每秒注入2个用户
      rampUsers(15) during (40 seconds)   // 40秒内线性注入15个用户
    )
  ).protocols(httpProtocol)
}
```

## 4.7 实验三：数据驱动测试

### 实验目标

1. 掌握CSV数据源的使用
2. 学会使用JSON数据源
3. 学会创建自定义数据源

### 实验步骤

1. 创建CSV和JSON数据文件
2. 创建使用这些数据源的测试场景
3. 创建自定义数据源
4. 运行测试并验证数据使用情况

### 实验代码

```scala
import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class DataDrivenExperiment extends Simulation {

  // HTTP协议配置
  val httpProtocol = http
    .baseUrl("https://jsonplaceholder.typicode.com")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Data-Driven Experiment")

  // CSV数据源
  val csvFeeder = csv("posts.csv").random

  // JSON数据源
  val jsonFeeder = jsonFile("users.json").random

  // 自定义数据源
  val customFeeder = Iterator.continually(Map(
    "postId" -> scala.util.Random.nextInt(100),
    "userId" -> (1 + scala.util.Random.nextInt(10)),
    "timestamp" -> System.currentTimeMillis()
  ))

  // 场景1：使用CSV数据
  val csvScenario = scenario("CSV Data Test")
    .feed(csvFeeder)
    .exec(
      http("Get Post with CSV Data")
        .get("/posts/${postId}")
        .check(status.is(200))
        .check(jsonPath("$.userId").is("${userId}"))
    )
    .pause(1, 2)

  // 场景2：使用JSON数据
  val jsonScenario = scenario("JSON Data Test")
    .feed(jsonFeeder)
    .exec(
      http("Get User with JSON Data")
        .get("/users/${userId}")
        .check(status.is(200))
        .check(jsonPath("$.name").is("${name}"))
    )
    .pause(1, 2)

  // 场景3：使用自定义数据
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

  // 负载配置
  setUp(
    csvScenario.inject(rampUsers(5) during (10 seconds)),
    jsonScenario.inject(rampUsers(5) during (10 seconds)),
    customScenario.inject(rampUsers(5) during (10 seconds))
  ).protocols(httpProtocol)
}
```

## 4.8 本章小结

本章详细介绍了Gatling高级测试场景设计的方法，包括多场景组合、负载注入策略、思考时间模拟和数据驱动测试。通过三个实验，我们学习了如何创建多场景组合测试、负载注入策略测试和数据驱动测试。

掌握这些高级场景设计技巧可以帮助我们更真实地模拟用户行为，设计更有效的性能测试。在下一章中，我们将学习Gatling的数据处理与断言技巧，以更深入地分析测试结果。