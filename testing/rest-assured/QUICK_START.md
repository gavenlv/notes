# REST Assured 快速开始指南

本指南将帮助您快速上手REST Assured，运行第一个API测试，并了解基本概念。

## 目录

1. [环境准备](#环境准备)
2. [运行第一个测试](#运行第一个测试)
3. [基本概念](#基本概念)
4. [进阶学习路径](#进阶学习路径)
5. [常见问题](#常见问题)

## 环境准备

### 1. 系统要求

- Java 8 或更高版本
- Maven 3.0 或更高版本
- IDE（推荐 IntelliJ IDEA 或 Eclipse）

### 2. 克隆或下载示例

```bash
# 如果您使用Git
git clone [repository-url]

# 或者直接下载整个目录
```

### 3. 导入项目

将 `testing/rest-assured/code` 目录作为Maven项目导入到您的IDE中。

## 运行第一个测试

### 1. 打开 SimpleApiTest.java

在IDE中打开 `basic-examples/SimpleApiTest.java` 文件。这是最基础的API测试示例。

### 2. 运行测试

您可以通过以下方式之一运行测试：

#### 方式1：IDE中运行
- 在 `SimpleApiTest` 类中右键
- 选择 "Run 'SimpleApiTest'"
- 或者在特定测试方法上右键，选择"Run"

#### 方式2：命令行运行
```bash
# 运行所有测试
mvn test

# 运行特定测试类
mvn test -Dtest=SimpleApiTest

# 运行特定测试方法
mvn test -Dtest=SimpleApiTest#testGetSingleUser
```

### 3. 查看结果

测试运行后，您应该看到：
- 所有测试通过（绿色标记）
- 在控制台中显示测试执行结果
- 在 `target/surefire-reports` 目录下生成测试报告

## 基本概念

### 1. Given-When-Then 模式

REST Assured使用BDD风格的Given-When-Then模式：

```java
// Given - 设置请求前置条件
given()
    .header("Content-Type", "application/json")
    .queryParam("userId", 1)

// When - 执行操作
.when()
    .get("/users/1")

// Then - 验证结果
.then()
    .statusCode(200)
    .body("name", notNullValue());
```

### 2. 静态导入

为了让代码更简洁，REST Assured使用静态导入：

```java
import static io.restassured.RestAssured.*;
import static io.restassured.matcher.RestAssuredMatchers.*;
import static org.hamcrest.Matchers.*;

// 使用静态导入后
given()
    .auth().basic("user", "pass")
    .when()
    .get("/api/data")
    .then()
    .statusCode(200);
```

### 3. 响应验证

REST Assured提供了多种验证响应的方式：

```java
// 状态码验证
.then().statusCode(200)

// 响应头验证
.then().header("Content-Type", "application/json")

// 响应体验证
.then().body("name", equalTo("John Doe"))
.then().body("users", hasSize(10))
.then().body("users[0].email", containsString("@"))
```

### 4. JSONPath

JSONPath用于从JSON响应中提取数据：

```java
// 提取单个值
String name = get("/users/1").path("name");

// 提取列表
List<String> emails = get("/users").path("users.email");

// 在验证中使用JSONPath
.then().body("users[?(@.age > 30)]", hasSize(greaterThan(0)));
```

## 进阶学习路径

### 1. 学习顺序

建议按照以下顺序学习：

1. **基础语法**：完成 `basic-examples` 中的所有示例
2. **请求与响应**：学习 `request-response` 中的示例
3. **数据处理**：学习 `data-handling` 中的示例
4. **认证**：学习 `authentication` 中的示例
5. **性能测试**：学习 `performance` 中的示例
6. **框架设计**：学习 `framework` 中的示例
7. **安全测试**：学习 `security` 中的示例

### 2. 实践建议

- **运行并修改示例**：不要只看代码，运行并修改它们
- **应用到实际项目**：尝试在实际项目中应用学到的知识
- **阅读文档**：结合教程中的文档章节深入学习
- **练习编写测试**：针对您自己的API编写测试

### 3. 深入学习

当您掌握了基础知识后，可以：

1. 阅读[完整教程](README.md)
2. 学习高级特性，如自定义过滤器和序列化器
3. 构建自己的测试框架
4. 探索与CI/CD的集成

## 常见问题

### 1. 连接超时错误

**问题**：`java.net.SocketTimeoutException: Read timed out`

**解决方案**：
```java
// 设置连接和读取超时
RestAssured.config = RestAssured.config()
    .connectionTimeout(new ConnectionConfig(30000, 60000));
```

### 2. SSL证书问题

**问题**：`javax.net.ssl.SSLHandshakeException`

**解决方案**：
```java
// 对于测试环境，可以放宽SSL验证
RestAssured.useRelaxedHTTPSValidation();
```

### 3. JSON解析错误

**问题**：响应不是有效JSON格式

**解决方案**：
```java
// 检查响应内容类型
given()
    .when()
    .get("/api/data")
.then()
    .statusCode(200)
    .contentType(ContentType.JSON);  // 确保是JSON
```

### 4. 静态导入无法识别

**问题**：IDE无法识别REST Assured的静态导入

**解决方案**：
- 确保已正确添加依赖
- 在IDE中刷新Maven项目
- 手动添加导入语句：
  ```java
  import static io.restassured.RestAssured.*;
  import static org.hamcrest.Matchers.*;
  ```

## 获取帮助

如果您遇到问题：

1. 查看[完整文档](README.md)中的对应章节
2. 检查 `code` 目录中的示例
3. 搜索REST Assured官方文档
4. 提交问题到项目仓库

## 下一步

恭喜您完成了快速开始！现在您可以：

1. 运行更多示例代码
2. 阅读详细教程章节
3. 尝试修改示例以适应您的API
4. 开始为您的实际项目编写测试

祝您测试愉快！