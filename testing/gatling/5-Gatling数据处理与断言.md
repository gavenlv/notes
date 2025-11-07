# 第5章：Gatling数据处理与断言

## 5.1 数据处理概述

在性能测试中，数据处理是一个关键环节。Gatling提供了强大的数据处理功能，使测试人员能够：

- 从各种数据源读取测试数据
- 动态生成测试数据
- 对响应数据进行提取和转换
- 将数据存储在Session中供后续使用

### 5.1.1 数据处理的重要性

1. **真实性**：使用真实数据模拟用户行为
2. **多样性**：避免缓存效应，提高测试准确性
3. **关联性**：处理请求之间的数据依赖关系
4. **验证性**：确保系统正确处理各种数据

## 5.2 数据源与Feed

### 5.2.1 CSV数据源

CSV是最常用的测试数据源之一，适用于结构化数据。

#### 基本CSV Feed

```scala
// 从CSV文件读取数据
val csvFeeder = csv("data/users.csv") // 默认分隔符为逗号

// 指定分隔符
val csvFeeder = csv("data/users.csv").separator(';')

// 随机读取
val csvFeeder = csv("data/users.csv").random

// 循环读取（默认）
val csvFeeder = csv("data/users.csv").circular

// 队列读取（不循环）
val csvFeeder = csv("data/users.csv").queue
```

#### 高级CSV Feed配置

```scala
// 转换数据
val csvFeeder = csv("data/users.csv").transform {
  case ("name", name) => ("name", name.toUpperCase)
}

// 批量读取
val csvFeeder = csv("data/users.csv").batch(5)

// 分片读取
val csvFeeder = csv("data/users.csv").shard
```

### 5.2.2 JSON数据源

JSON数据源适用于复杂结构的数据。

```scala
// 从JSON文件读取
val jsonFeeder = jsonFile("data/users.json")

// 数组JSON
val jsonArrayFeeder = jsonFile("data/users.json").array
```

### 5.2.3 JDBC数据源

从数据库直接读取测试数据。

```scala
// 配置数据库连接
val jdbcFeeder = jdbcFeeder("jdbc:mysql://localhost:3306/testdb", 
                           "user", "password", 
                           "SELECT id, name FROM users")
```

### 5.2.4 自定义Feed

```scala
// 生成随机数据
val randomFeeder = Iterator.continually(Map(
  "userId" -> scala.util.Random.nextInt(1000),
  "sessionId" -> UUID.randomUUID().toString
))

// 生成序列数据
val sequenceFeeder = Iterator.from(0).map(i => Map(
  "iteration" -> i,
  "timestamp" -> System.currentTimeMillis()
))
```

## 5.3 数据提取与转换

### 5.3.1 响应数据提取

从HTTP响应中提取数据是性能测试中的常见需求。

#### JSONPath提取

```scala
// 提取单个值
jsonPath("$.user.id").saveAs("userId")

// 提取数组
jsonPath("$.users[*].name").saveAs("userNames")

// 提取并转换
jsonPath("$.price").ofType[Double].saveAs("itemPrice")

// 条件提取
jsonPath("$..[?(@.type=='premium')].id").saveAs("premiumIds")
```

#### XPath提取（用于XML响应）

```scala
// 提取元素
xpath("//user/@id").saveAs("userId")

// 提取文本
xpath("//user/name/text()").saveAs("userName")

// 提取多个值
xpath("//users/user/id").saveAs("userIds")
```

#### 正则表达式提取

```scala
// 提取单个匹配
regex("id=(\\d+)").saveAs("userId")

// 提取所有匹配
regex("id=(\\d+)").findAll.saveAs("allIds")

// 提取第N个匹配
regex("id=(\\d+)").ofType[Int].saveAs("numericId")
```

#### CSS选择器提取（用于HTML响应）

```scala
// 提取属性
css("a#link", "href").saveAs("linkUrl")

// 提取文本
css("h1.title").ofType[String].saveAs("title")

// 提取多个值
css("li.item").findAll.saveAs("items")
```

### 5.3.2 数据转换

#### 基本转换

```scala
// 字符串操作
exec(session => {
  val originalName = session("userName").as[String]
  val transformedName = originalName.toUpperCase
  session.set("userName", transformedName)
})

// 数值操作
exec(session => {
  val price = session("price").as[Double]
  val discountedPrice = price * 0.9
  session.set("discountedPrice", discountedPrice)
})
```

#### 高级转换

```scala
// JSON转换
exec(session => {
  val jsonString = session("response").as[String]
  val json = parse(jsonString)
  val transformedJson = json.transformField {
    case JField("name", JString(s)) => JField("name", JString(s.toUpperCase))
  }
  session.set("transformedResponse", compact(render(transformedJson)))
})

// 列表操作
exec(session => {
  val items = session("items").as[Seq[String]]
  val filteredItems = items.filter(_.startsWith("A"))
  session.set("filteredItems", filteredItems)
})
```

## 5.4 Session管理

### 5.4.1 Session基础

Session是Gatling中存储和传递数据的核心机制。

```scala
// 设置值
exec(session => session.set("key", "value"))

// 获取值
exec(session => {
  val value = session("key").as[String]
  println(s"Value: $value")
  session
})

// 删除值
exec(session => session.remove("key"))

// 检查是否存在
exec(session => {
  if (session.contains("key")) {
    // 处理存在的键
  }
  session
})
```

### 5.4.2 Session操作函数

Gatling提供了便捷的Session操作函数。

```scala
// 设置多个值
exec(setAll(Map(
  "userId" -> 123,
  "userName" -> "testuser",
  "timestamp" -> System.currentTimeMillis()
)))

// 条件设置
exec(setIf(session => session("status").as[String] == "active")("isActive", true))

// 默认值
exec(setIfAbsent("defaultValue", "default"))

// 增加计数器
exec(incrementCounter("requestCount"))
exec(decrementCounter("remainingRequests"))
```

### 5.4.3 Session生命周期

```scala
// 初始化Session
exec(session => session.set("startTime", System.currentTimeMillis()))

// 传递Session
exec(
  get("/api/users/${userId}")
    .check(jsonPath("$.id").saveAs("retrievedUserId"))
)

// 清理Session
exec(session => session.removeAll("tempData"))
```

## 5.5 断言与验证

### 5.5.1 基本断言

断言用于验证响应是否符合预期。

#### 状态码检查

```scala
// 检查特定状态码
check(status.is(200))

// 检查状态码范围
check(status.in(200, 201, 202))

// 检查状态码不在特定值
check(status.not(404))
```

#### 响应时间检查

```scala
// 检查响应时间小于指定值
check(responseTimeInMillis.lt(1000))

// 检查响应时间在范围内
check(responseTimeInMillis.between(100, 500))

// 检查响应时间大于指定值
check(responseTimeInMillis.gt(100))
```

#### 响应体检查

```scala
// 检查响应体包含特定字符串
check(bodyString.saveAs("responseBody"))
check(bodyString.contains("success"))

// 检查响应体长度
check(bodyLength.is(100))

// 检查响应体正则匹配
check(bodyString.regex("error:\\s*\\d+"))
```

### 5.5.2 高级断言

#### JSON断言

```scala
// 检查JSON路径存在
check(jsonPath("$.user").exists)

// 检查JSON路径不存在
check(jsonPath("$.error").notExists)

// 检查JSON值
check(jsonPath("$.status").is("active"))

// 检查JSON数组大小
check(jsonPath("$.items[*]").count.is(10))

// 检查JSON数组每个元素
check(jsonPath("$.items[*].price").findAll.saveAs("prices"))
```

#### XPath断言

```scala
// 检查XPath存在
check(xpath("//user").exists)

// 检查XPath值
check(xpath("//user/@id").is("123"))

// 检查XPath数量
check(xpath("//users/user").count.is(5))
```

#### 自定义断言

```scala
// 使用自定义验证函数
check(bodyString.transform(_.length > 100).is(true))

// 复杂断言
check(responseTimeInMillis.saveAs("rt"))
exec(session => {
  val rt = session("rt").as[Int]
  if (rt > 1000) {
    println(s"Warning: Slow response time $rt ms")
  }
  session
})
```

### 5.5.3 全局断言

```scala
// 设置全局断言
setUp(
  scn.inject(atOnceUsers(10))
).assertions(
  global.responseTime.max.lt(1000),
  global.successfulRequests.percent.gt(95)
)
```

## 5.6 数据验证技术

### 5.6.1 数据完整性验证

```scala
// 验证返回数据与请求数据的一致性
exec(
  http("Create User")
    .post("/api/users")
    .body(StringBody("""{"name":"${userName}","email":"${userEmail}"}"""))
    .check(jsonPath("$.name").is("${userName}"))
    .check(jsonPath("$.email").is("${userEmail}"))
)
```

### 5.6.2 业务逻辑验证

```scala
// 验证业务规则
exec(
  http("Place Order")
    .post("/api/orders")
    .body(StringBody("""{"userId":"${userId}","items":${items}}"""))
    .check(jsonPath("$.totalPrice").saveAs("totalPrice"))
).exec(session => {
  val items = session("items").as[String]
  val totalPrice = session("totalPrice").as[Double]
  
  // 验证总价计算是否正确
  val expectedTotal = calculateExpectedTotal(items)
  if (math.abs(totalPrice - expectedTotal) > 0.01) {
    println(s"Price calculation error: expected $expectedTotal, got $totalPrice")
  }
  
  session
})
```

### 5.6.3 数据一致性验证

```scala
// 验证数据在不同API间的一致性
exec(
  http("Get User Details")
    .get("/api/users/${userId}")
    .check(jsonPath("$.name").saveAs("userName"))
).exec(
  http("Get User Orders")
    .get("/api/users/${userId}/orders")
    .check(jsonPath("$[*].customerName").findAll.saveAs("orderCustomerNames"))
).exec(session => {
  val userName = session("userName").as[String]
  val orderCustomerNames = session("orderCustomerNames").as[Seq[String]]
  
  // 验证所有订单的客户名称一致
  if (!orderCustomerNames.forall(_ == userName)) {
    println("Data inconsistency: customer names don't match across orders")
  }
  
  session
})
```

## 5.7 实验与练习

### 实验1：CSV数据读取与使用

**目标**：学习如何从CSV文件读取数据并在请求中使用

**步骤**：
1. 创建包含用户数据的CSV文件
2. 配置CSV Feeder
3. 在请求中使用CSV数据
4. 验证数据正确传递

**预期结果**：
- 成功读取CSV数据
- 在请求中正确使用数据
- 验证数据传递正确

### 实验2：JSON响应数据提取

**目标**：学习如何从JSON响应中提取数据

**步骤**：
1. 发送请求获取JSON响应
2. 使用JSONPath提取数据
3. 将提取的数据保存到Session
4. 在后续请求中使用提取的数据

**预期结果**：
- 成功提取JSON数据
- 数据正确保存到Session
- 后续请求正确使用提取的数据

### 实验3：自定义断言实现

**目标**：学习如何实现自定义断言验证业务逻辑

**步骤**：
1. 定义业务规则
2. 实现自定义验证函数
3. 在测试中应用自定义断言
4. 分析断言结果

**预期结果**：
- 自定义断言正确实现
- 业务规则得到验证
- 测试结果符合预期

## 5.8 最佳实践

### 5.8.1 数据管理最佳实践

1. **数据隔离**：不同环境使用不同数据源
2. **数据规模**：确保测试数据量足够大，避免缓存效应
3. **数据多样性**：覆盖各种边界情况和异常数据
4. **数据更新**：定期更新测试数据，保持真实性

### 5.8.2 断言设计最佳实践

1. **关键断言**：优先验证关键业务指标
2. **性能断言**：设置合理的性能阈值
3. **错误处理**：为断言失败提供清晰的错误信息
4. **断言范围**：避免过多细粒度断言影响性能

### 5.8.3 Session管理最佳实践

1. **命名规范**：使用有意义的Session变量名
2. **数据清理**：及时清理不再需要的Session数据
3. **内存管理**：避免在Session中存储大量数据
4. **数据共享**：合理设计Session数据在不同请求间的共享

## 5.9 常见问题与解决方案

### 5.9.1 数据读取问题

**问题**：CSV文件读取失败
**解决方案**：
- 检查文件路径是否正确
- 确认文件格式符合CSV标准
- 验证分隔符设置是否正确

### 5.9.2 数据提取问题

**问题**：JSONPath无法提取数据
**解决方案**：
- 验证JSONPath表达式语法
- 检查响应数据是否为有效JSON
- 使用调试工具查看实际响应内容

### 5.9.3 断言失败问题

**问题**：断言频繁失败
**解决方案**：
- 检查断言条件是否过于严格
- 验证测试数据是否符合预期
- 调整断言阈值或实现更灵活的断言逻辑

## 5.10 总结

本章详细介绍了Gatling中的数据处理与断言机制，包括：

1. **数据源管理**：CSV、JSON、JDBC等多种数据源的使用
2. **数据提取与转换**：从响应中提取数据并进行转换
3. **Session管理**：在测试过程中存储和传递数据
4. **断言与验证**：验证响应数据和业务逻辑
5. **最佳实践**：数据处理和断言设计的最佳实践

掌握这些技术将帮助你构建更加真实、可靠的性能测试场景，有效验证系统的功能和性能表现。下一章将介绍Gatling的报告与结果分析功能，帮助你更好地理解和评估测试结果。