# 第1章：REST Assured简介与环境搭建

## 1.1 REST Assured简介

### 1.1.1 什么是REST Assured

REST Assured是一个用于简化RESTful API测试的Java库，它提供了一种简洁、直观的DSL（领域特定语言）来编写和验证HTTP请求和响应。通过REST Assured，测试人员可以使用类似自然语言的语法来编写测试代码，大大提高了API测试的可读性和可维护性。

### 1.1.2 为什么选择REST Assured

与其他API测试工具相比，REST Assured具有以下优势：

1. **简洁的DSL语法**：使用链式调用和自然语言风格，代码更加易读
2. **强大的验证能力**：支持多种响应验证方式，包括状态码、头信息、响应体等
3. **灵活的序列化/反序列化**：内置JSON、XML等格式的处理支持
4. **丰富的集成能力**：与JUnit、TestNG等测试框架无缝集成
5. **完整的认证支持**：支持OAuth、Basic Auth、Digest Auth等多种认证方式
6. **可扩展性**：支持自定义过滤器和匹配器

### 1.1.3 应用场景

REST Assured主要应用于以下场景：

- **功能测试**：验证API的功能是否符合预期
- **集成测试**：测试API与其他系统的集成情况
- **回归测试**：确保代码变更不会影响现有API功能
- **持续集成**：作为CI/CD流水线中的自动化测试环节
- **性能测试**：结合其他工具进行API性能测试
- **安全测试**：验证API的安全机制和漏洞

## 1.2 REST Assured核心概念

### 1.2.1 Given-When-Then模式

REST Assured采用BDD（行为驱动开发）中的Given-When-Then模式来组织测试代码：

```java
// Given - 设置请求前置条件
given()
    .header("Content-Type", "application/json")
    .queryParam("apiKey", "123456")
    
// When - 执行操作
.when()
    .get("/api/users/123")

// Then - 验证结果
.then()
    .statusCode(200)
    .body("name", equalTo("John Doe"));
```

- **Given**：设置请求的前置条件，如请求头、查询参数、请求体等
- **When**：执行HTTP操作，如GET、POST、PUT、DELETE等
- **Then**：验证响应结果，如状态码、响应头、响应体等

### 1.2.2 静态导入与DSL

REST Assured大量使用静态导入来提供简洁的DSL语法：

```java
import static io.restassured.RestAssured.*;
import static io.restassured.matcher.RestAssuredMatchers.*;
import static org.hamcrest.Matchers.*;

// 使用静态导入后的代码
given().
    auth().basic("user", "password").
when().
    get("/api/data").
then().
    statusCode(200).
    body("items", hasSize(greaterThan(0)));
```

### 1.2.3 JSONPath与Hamcrest匹配器

REST Assured使用JSONPath来解析和提取JSON数据，并结合Hamcrest匹配器进行灵活的断言：

```java
// 使用JSONPath提取数据
String name = get("/api/users/1").path("name");

// 使用Hamcrest匹配器进行断言
then().
    body("users.size()", equalTo(10)).
    body("users[0].email", containsString("@example.com")).
    body("users[*].age", everyItem(greaterThan(18)));
```

## 1.3 环境搭建

### 1.3.1 Maven项目配置

创建一个Maven项目，添加以下依赖到pom.xml：

```xml
<dependencies>
    <!-- REST Assured核心库 -->
    <dependency>
        <groupId>io.rest-assured</groupId>
        <artifactId>rest-assured</artifactId>
        <version>5.3.0</version>
        <scope>test</scope>
    </dependency>
    
    <!-- JSON处理支持 -->
    <dependency>
        <groupId>io.rest-assured</groupId>
        <artifactId>json-path</artifactId>
        <version>5.3.0</version>
        <scope>test</scope>
    </dependency>
    
    <!-- XML处理支持 -->
    <dependency>
        <groupId>io.rest-assured</groupId>
        <artifactId>xml-path</artifactId>
        <version>5.3.0</version>
        <scope>test</scope>
    </dependency>
    
    <!-- 测试框架 -->
    <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <version>4.13.2</version>
        <scope>test</scope>
    </dependency>
    
    <!-- 日志支持 -->
    <dependency>
        <groupId>org.slf4j</groupId>
        <artifactId>slf4j-simple</artifactId>
        <version>1.7.36</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### 1.3.2 Gradle项目配置

如果使用Gradle构建工具，添加以下依赖到build.gradle：

```gradle
dependencies {
    testImplementation 'io.rest-assured:rest-assured:5.3.0'
    testImplementation 'io.rest-assured:json-path:5.3.0'
    testImplementation 'io.rest-assured:xml-path:5.3.0'
    testImplementation 'junit:junit:4.13.2'
    testImplementation 'org.slf4j:slf4j-simple:1.7.36'
}
```

### 1.3.3 IDE配置

1. **IntelliJ IDEA**：
   - 确保安装了Maven或Gradle插件
   - 启用注解处理（如果需要）
   - 设置正确的Java版本（8+）

2. **Eclipse**：
   - 安装M2Eclipse插件（对于Maven项目）
   - 或Buildship插件（对于Gradle项目）
   - 配置Java编译器版本

### 1.3.4 基础测试类设置

创建一个基础测试类，设置全局配置：

```java
import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import org.junit.BeforeClass;
import org.junit.Test;

import static io.restassured.RestAssured.*;
import static io.restassured.matcher.RestAssuredMatchers.*;
import static org.hamcrest.Matchers.*;

public class BaseApiTest {
    
    @BeforeClass
    public static void setup() {
        // 设置基础URI
        RestAssured.baseURI = "https://jsonplaceholder.typicode.com";
        
        // 设置基础路径
        RestAssured.basePath = "/todos";
        
        // 设置默认内容类型
        RestAssured.defaultParser = Parser.JSON;
        
        // 启用日志记录
        RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();
        
        // 设置连接超时（毫秒）
        RestAssured.config = RestAssuredConfig.config()
            .connectionTimeout(new ConnectionConfig(30000, 30000));
    }
    
    @Test
    public void basicGetTest() {
        // 简单的GET请求测试
        given()
            .queryParam("userId", 1)
        .when()
            .get()
        .then()
            .statusCode(200)
            .body("size()", greaterThan(0));
    }
}
```

## 1.4 第一个REST Assured测试

### 1.4.1 创建测试类

创建您的第一个REST Assured测试类：

```java
import io.restassured.http.ContentType;
import org.junit.Test;

import static io.restassured.RestAssured.*;
import static io.rest-assured.matcher.RestAssuredMatchers.*;
import static org.hamcrest.Matchers.*;

public class FirstTest {
    
    @Test
    public void testGetUser() {
        // 测试获取单个用户信息
        given()
            .pathParam("userId", 1)
        .when()
            .get("https://jsonplaceholder.typicode.com/users/{userId}")
        .then()
            .statusCode(200)
            .contentType(ContentType.JSON)
            .body("id", equalTo(1))
            .body("name", notNullValue())
            .body("email", containsString("@"))
            .body("address.city", notNullValue())
            .body("company.name", notNullValue());
    }
    
    @Test
    public void testCreatePost() {
        // 测试创建新帖子
        String requestBody = "{\n" +
            "  \"title\": \"REST Assured Test\",\n" +
            "  \"body\": \"This is a test post created with REST Assured\",\n" +
            "  \"userId\": 1\n" +
            "}";
        
        given()
            .contentType(ContentType.JSON)
            .body(requestBody)
        .when()
            .post("https://jsonplaceholder.typicode.com/posts")
        .then()
            .statusCode(201)
            .body("title", equalTo("REST Assured Test"))
            .body("id", notNullValue());
    }
}
```

### 1.4.2 运行测试

在IDE中运行测试，或使用命令行：

```bash
# Maven
mvn test

# Gradle
gradle test
```

测试运行后，您应该看到所有测试通过，并且在控制台中显示请求和响应的日志（因为我们在基础测试类中启用了日志记录）。

### 1.4.3 查看测试报告

REST Assured测试的输出会被包含在测试框架的报告中：

- **JUnit**：查看`target/surefire-reports`目录下的XML和HTML报告
- **TestNG**：查看`test-output`目录下的HTML报告

## 1.5 实践练习

### 练习1：获取用户列表

编写一个测试，获取所有用户列表，并验证：
- 响应状态码为200
- 响应内容为JSON格式
- 用户数量大于0
- 每个用户都有id、name、email字段

### 练习2：获取特定用户信息

编写一个测试，获取ID为2的用户信息，并验证：
- 响应状态码为200
- 用户ID为2
- 用户名和邮箱不为空
- 地址包含城市信息

### 练习3：更新用户信息

编写一个测试，更新ID为1的用户信息，并验证：
- 更新请求返回状态码200
- 响应中包含更新的信息

## 1.6 常见问题与解决方案

### 问题1：依赖冲突

**问题现象**：运行测试时出现NoClassDefFoundError或NoSuchMethodError

**解决方案**：
1. 检查依赖版本是否兼容
2. 使用`mvn dependency:tree`检查依赖树
3. 排除冲突的依赖：
   ```xml
   <dependency>
       <groupId>io.rest-assured</groupId>
       <artifactId>rest-assured</artifactId>
       <version>5.3.0</version>
       <exclusions>
           <exclusion>
               <groupId>org.codehaus.groovy</groupId>
               <artifactId>groovy</artifactId>
           </exclusion>
       </exclusions>
   </dependency>
   ```

### 问题2：SSL证书问题

**问题现象**：访问HTTPS API时出现SSLHandshakeException

**解决方案**：
```java
// 方法1：信任所有证书（仅用于测试环境）
RestAssured.config = RestAssured.config()
    .sslConfig(new SSLConfig().relaxedHTTPSValidation());

// 方法2：使用自定义信任库
RestAssured.config = RestAssured.config()
    .sslConfig(new SSLConfig()
        .trustStore("/path/to/truststore.jks", "password"));
```

### 问题3：请求超时

**问题现象**：请求响应缓慢，导致测试超时

**解决方案**：
```java
// 设置连接和读取超时
RestAssured.config = RestAssured.config()
    .connectionTimeout(new ConnectionConfig(10000, 30000));
```

## 1.7 总结

本章介绍了REST Assured的基本概念、核心特性和环境搭建步骤。通过本章的学习，您应该能够：

1. 理解REST Assured是什么及其优势
2. 掌握Given-When-Then模式的使用
3. 搭建REST Assured测试环境
4. 编写并运行简单的API测试
5. 解决常见的环境配置问题

在下一章中，我们将深入学习REST Assured的基础语法和核心概念，探索更复杂的请求构建和响应验证技巧。