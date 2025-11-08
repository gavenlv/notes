# 第2章：REST Assured基础语法与核心概念

## 2.1 REST Assured核心语法结构

### 2.1.1 Given-When-Then详解

REST Assured采用BDD风格的Given-When-Then语法，这种结构使测试代码更加清晰和可读：

```java
// Given - 设置请求前置条件（可选）
given()
    .spec(requestSpec)  // 使用请求规范
    .auth().basic("username", "password")  // 基本认证
    .header("Content-Type", "application/json")  // 设置请求头
    .queryParam("param1", "value1")  // 设置查询参数
    .pathParam("userId", 123)  // 设置路径参数
    .cookies("sessionId", "abc123")  // 设置Cookie
    .body(requestBody)  // 设置请求体
    .proxy("proxy.example.com", 8080)  // 设置代理
    
// When - 执行HTTP操作
.when()
    .get("/api/users/{userId}")  // GET请求
    .post("/api/users")  // POST请求
    .put("/api/users/{userId}")  // PUT请求
    .patch("/api/users/{userId}")  // PATCH请求
    .delete("/api/users/{userId}")  // DELETE请求
    .head("/api/users/{userId}")  // HEAD请求
    .options("/api/users")  // OPTIONS请求
    .request("METHOD", "/api/resource")  // 自定义方法
    
// Then - 验证响应结果
.then()
    .statusCode(200)  // 验证状态码
    .statusLine("HTTP/1.1 200 OK")  // 验证状态行
    .contentType(ContentType.JSON)  // 验证内容类型
    .header("Cache-Control", containsString("max-age"))  // 验证响应头
    .cookie("JSESSIONID", notNullValue())  // 验证Cookie
    .body("field", equalTo("value"))  // 验证响应体字段
    .extract()  // 提取响应数据
    .log()  // 日志记录
    .time(lessThan(2000L))  // 验证响应时间
```

### 2.1.2 静态导入的使用

为了简化代码，REST Assured大量使用静态导入：

```java
import static io.restassured.RestAssured.*;
import static io.restassured.matcher.RestAssuredMatchers.*;
import static org.hamcrest.Matchers.*;

// 使用静态导入后，代码更简洁
@Test
public void staticImportExample() {
    given()
        .auth().basic("user", "pass")
        .header("Accept", "application/json")
    .when()
        .get("/api/users")
    .then()
        .statusCode(200)
        .body("users.size()", greaterThan(0))
        .body("users[0].name", notNullValue());
}
```

### 2.1.3 链式调用与流畅API

REST Assured采用流畅API设计，所有方法都返回可以继续链式调用的对象：

```java
// 完整的链式调用示例
Response response = given()
        .contentType("application/json")
        .accept("application/json")
        .queryParam("page", 1)
        .queryParam("size", 10)
        .header("Authorization", "Bearer token123")
    .when()
        .get("/api/products")
    .then()
        .statusCode(200)
        .contentType(ContentType.JSON)
        .header("X-Rate-Limit-Limit", notNullValue())
        .body("page", equalTo(1))
        .body("size", equalTo(10))
        .body("data", hasSize(10))
        .extract()
        .response();
```

## 2.2 请求构建详解

### 2.2.1 请求规范(RequestSpecification)

请求规范允许您重用请求配置，提高代码的可维护性：

```java
// 创建请求规范
RequestSpecification requestSpec = new RequestSpecBuilder()
    .setBaseUri("https://api.example.com")
    .setBasePath("/v1")
    .setContentType(ContentType.JSON)
    .addHeader("Authorization", "Bearer token123")
    .addQueryParam("api_key", "secret")
    .build();

// 使用请求规范
given()
    .spec(requestSpec)
    .pathParam("id", 123)
.when()
    .get("/users/{id}")
.then()
    .statusCode(200);
```

### 2.2.2 请求头设置

```java
// 方法1：直接设置单个头
given().header("Content-Type", "application/json");

// 方法2：设置多个头
Headers headers = new Headers(
    new Header("Content-Type", "application/json"),
    new Header("Accept", "application/json"),
    new Header("Authorization", "Bearer token")
);
given().headers(headers);

// 方法3：使用Map设置头
Map<String, String> headersMap = new HashMap<>();
headersMap.put("Content-Type", "application/json");
headersMap.put("Authorization", "Bearer token");
given().headers(headersMap);

// 方法4：添加多个相同名称的头
given()
    .header("Accept", "application/json")
    .header("Accept", "text/plain")
    .header("Accept", "application/xml");
```

### 2.2.3 参数处理

```java
// 查询参数
given()
    .queryParam("param1", "value1")
    .queryParam("param2", 123)
    .queryParam("flag", true)
    .queryParam("list", "a,b,c");

// 路径参数
given()
    .pathParam("userId", 123)
    .pathParam("resourceType", "profile")
.when()
    .get("/api/users/{userId}/{resourceType}");

// 表单参数
given()
    .contentType(ContentType.URLENC)
    .formParam("username", "user1")
    .formParam("password", "pass123")
    .formParam("remember", true)
.when()
    .post("/login");

// 多值参数
given()
    .queryParam("ids", "1,2,3,4,5")
    .queryParam("tags", Arrays.asList("java", "rest", "assured"));
```

### 2.2.4 请求体设置

```java
// JSON字符串
String jsonBody = "{\"name\":\"John\", \"age\":30}";
given()
    .contentType(ContentType.JSON)
    .body(jsonBody);

// 对象自动序列化
User user = new User("John", 30);
given()
    .contentType(ContentType.JSON)
    .body(user);

// 文件内容
File jsonFile = new File("user.json");
given()
    .contentType(ContentType.JSON)
    .body(jsonFile);

// 输入流
InputStream inputStream = getClass().getResourceAsStream("/user.json");
given()
    .contentType(ContentType.JSON)
    .body(inputStream);

// 表单数据
given()
    .contentType(ContentType.URLENC)
    .formParam("username", "user1")
    .formParam("password", "pass123");

// 文件上传
given()
    .multiPart("file", new File("upload.txt"))
    .multiPart("description", "File upload test")
.when()
    .post("/upload");

// 字节数组
byte[] fileBytes = Files.readAllBytes(Paths.get("data.json"));
given()
    .contentType(ContentType.JSON)
    .body(fileBytes);
```

## 2.3 响应验证详解

### 2.3.1 响应规范(ResponseSpecification)

与请求规范类似，响应规范允许您重用响应验证逻辑：

```java
// 创建响应规范
ResponseSpecification responseSpec = new ResponseSpecBuilder()
    .expectStatusCode(200)
    .expectContentType(ContentType.JSON)
    .expectHeader("Server", notNullValue())
    .expectHeader("X-Response-Time", lessThan("1000"))
    .expectBody("status", equalTo("success"))
    .expectBody("data", notNullValue())
    .build();

// 使用响应规范
given()
    .spec(requestSpec)
    .pathParam("id", 123)
.when()
    .get("/users/{id}")
.then()
    .spec(responseSpec);
```

### 2.3.2 状态码和状态行验证

```java
// 精确匹配状态码
.then().statusCode(200);

// 状态码范围
.then().statusCode(lessThan(400));

// 成功状态码（2xx）
.then().statusCode(Matchers.allOf(
    greaterThanOrEqualTo(200),
    lessThan(300)
));

// 精确匹配状态行
.then().statusLine("HTTP/1.1 200 OK");

// 状态行包含特定文本
.then().statusLine(containsString("OK"));

// 自定义状态码验证
.then().statusCode(Matchers.anyOf(
    equalTo(200),
    equalTo(201),
    equalTo(202)
));
```

### 2.3.3 响应头验证

```java
// 验证单个响应头
.then().header("Content-Type", "application/json");
.then().header("Content-Length", "1024");
.then().header("Server", containsString("nginx"));

// 验证响应头是否存在
.then().header("X-Custom-Header", notNullValue());

// 验证多个响应头
.then()
    .header("Content-Type", "application/json")
    .header("Cache-Control", containsString("max-age"))
    .header("X-Rate-Limit-Remaining", notNullValue());

// 使用Map验证多个响应头
Map<String, Object> expectedHeaders = new HashMap<>();
expectedHeaders.put("Content-Type", "application/json");
expectedHeaders.put("X-API-Version", "1.0");
.then().headers(expectedHeaders);

// 验证响应头数值
.then().header("X-Rate-Limit-Limit", Integer::parseInt, greaterThan(100));

// 验证响应头日期
.then().header("Date", greaterThan(startDate));
```

### 2.3.4 Cookie验证

```java
// 验证Cookie值
.then().cookie("sessionId", "abc123");
.then().cookie("theme", "dark");

// 验证Cookie存在
.then().cookie("userToken", notNullValue());

// 验证Cookie属性
.then()
    .cookie("sessionId", hasValue("abc123"))
    .cookie("sessionId", hasKey("Path"))
    .cookie("sessionId", hasKey("Domain"))
    .cookie("sessionId", hasKey("Secure"));

// 获取Cookie详细信息
DetailedCookie cookie = get("/login").then().extract().detailedCookie("sessionId");
String cookieValue = cookie.getValue();
String domain = cookie.getDomain();
String path = cookie.getPath();
Date expiryDate = cookie.getExpiryDate();
boolean isSecure = cookie.isSecure();
boolean isHttpOnly = cookie.isHttpOnly();
```

## 2.4 响应体验证详解

### 2.4.1 JSON响应体验证

```java
// 基本字段验证
.then()
    .body("name", equalTo("John Doe"))
    .body("age", equalTo(30))
    .body("email", containsString("@"))
    .body("active", equalTo(true));

// 嵌套对象验证
.then()
    .body("address.street", equalTo("123 Main St"))
    .body("address.city", equalTo("New York"))
    .body("address.zipCode", equalTo("10001"));

// 数组验证
.then()
    .body("users", hasSize(5))
    .body("users[0].name", equalTo("Alice"))
    .body("users[1].age", greaterThan(18));

// 数组元素验证
.then()
    .body("users[*].name", hasItems("Alice", "Bob", "Charlie"))
    .body("users[*].age", everyItem(greaterThan(0)))
    .body("users[?(@.age > 30)]", hasSize(2));

// 数组筛选（JSONPath）
.then()
    .body("users[?(@.name == 'John')].age", equalTo(30))
    .body("users[?(@.age > 25)]", hasSize(greaterThan(0)));

// 空值验证
.then()
    .body("name", notNullValue())
    .body("description", nullValue())
    .body("middleName", either(nullValue()).or(notNullValue()));
```

### 2.4.2 XML响应体验证

```java
// XML元素验证
.then()
    .body("user.name", equalTo("John Doe"))
    .body("user.age", equalTo("30"))
    .body("user.email", containsString("@"));

// 使用XPath验证
.then()
    .body(hasXPath("/user/name", equalTo("John Doe")))
    .body(hasXPath("/user/address/city", equalTo("New York")))
    .body(hasXPath("//email[contains(text(), '@')]")));

// XML属性验证
.then()
    .body("user.@id", equalTo("123"))
    .body("user.@status", equalTo("active"));

// 命名空间处理
.then()
    .body(hasXPath("//ns:user/ns:name", 
        namespace("ns", "http://example.com/namespace"),
        equalTo("John")));
```

### 2.4.3 响应体类型验证

```java
// 使用Hamcrest匹配器
.then()
    .body("name", instanceOf(String.class))
    .body("age", instanceOf(Integer.class))
    .body("active", instanceOf(Boolean.class));

// 验证数组
.then().body("items", isA(List.class));

// 验证Map
.then().body("metadata", isA(Map.class));

// 响应体大小验证
.then()
    .body("users.size()", greaterThan(0))
    .body("users.size()", lessThan(100));
```

## 2.5 响应数据提取

### 2.5.1 完整响应提取

```java
// 提取完整响应
Response response = given()
    .when()
    .get("/api/users")
    .then()
    .extract()
    .response();

// 获取响应数据
int statusCode = response.getStatusCode();
String statusLine = response.getStatusLine();
Headers headers = response.getHeaders();
String body = response.getBody().asString();
long responseTime = response.getTime();

// 获取JSON路径
String name = response.jsonPath().getString("users[0].name");
int age = response.jsonPath().getInt("users[0].age");
List<String> names = response.jsonPath().getList("users.name");
```

### 2.5.2 部分数据提取

```java
// 提取特定路径
String name = get("/api/users/1").path("name");
List<String> emails = get("/api/users").path("users.email");
Map<String, Object> address = get("/api/users/1").path("address");

// 提取多个路径
JsonPath jsonPath = get("/api/users/1").jsonPath();
String name = jsonPath.getString("name");
int age = jsonPath.getInt("age");
String email = jsonPath.getString("contact.email");

// 提取响应头
String contentType = get("/api/users").header("Content-Type");
String server = get("/api/users").header("Server");
```

### 2.5.3 响应体反序列化

```java
// 反序列化为Java对象
User user = get("/api/users/1")
    .as(User.class);

List<User> users = get("/api/users")
    .jsonPath()
    .getList(".", User.class);

// 反序列化为Map
Map<String, Object> userMap = get("/api/users/1")
    .as(Map.class);

// 使用自定义反序列化器
Gson gson = new Gson();
User user = gson.fromJson(
    get("/api/users/1").getBody().asString(), 
    User.class
);
```

## 2.6 日志记录与调试

### 2.6.1 请求日志

```java
// 记录完整请求
given()
    .log().all()
    .when()
    .get("/api/users");

// 记录请求头
given()
    .log().headers()
    .when()
    .get("/api/users");

// 记录请求体
given()
    .log().body()
    .when()
    .get("/api/users");

// 记录请求参数
given()
    .log().params()
    .when()
    .get("/api/users");
```

### 2.6.2 响应日志

```java
// 记录完整响应
given()
    .when()
    .get("/api/users")
    .then()
    .log().all();

// 记录响应头
given()
    .when()
    .get("/api/users")
    .then()
    .log().headers();

// 记录响应体
given()
    .when()
    .get("/api/users")
    .then()
    .log().body();

// 记录响应状态
given()
    .when()
    .get("/api/users")
    .then()
    .log().status();

// 如果验证失败则记录完整信息
given()
    .when()
    .get("/api/users")
    .then()
    .log().ifValidationFails();
```

### 2.6.3 全局日志配置

```java
// 全局启用请求和响应日志（仅在验证失败时）
RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();

// 全局启用请求日志
RestAssured.config = RestAssured.config()
    .logConfig(LogConfig.logConfig()
        .enableLoggingOfRequestAndResponseIfValidationFails());

// 配置日志详细级别
RestAssured.config = RestAssured.config()
    .logConfig(LogConfig.logConfig()
        .enablePrettyPrinting(true));

// 配置自定义日志实现
Logger logger = LoggerFactory.getLogger(MyTest.class);
RestAssured.config = RestAssured.config()
    .logConfig(LogConfig.logConfig()
        .defaultStream(System.out)
        .enablePrettyPrinting(true));
```

## 2.7 配置与过滤器

### 2.7.1 全局配置

```java
// 设置基础URI
RestAssured.baseURI = "https://api.example.com";

// 设置基础路径
RestAssured.basePath = "/v1";

// 设置默认端口
RestAssured.port = 8080;

// 设置认证
RestAssured.authentication = basic("username", "password");

// 设置代理
RestAssured.proxy("proxy.example.com", 8080);

// 设置内容类型
RestAssured.defaultParser = Parser.JSON;

// 设置URL编码
RestAssured.urlEncodingEnabled = true;

// 重置配置
RestAssured.reset();
```

### 2.7.2 配置对象

```java
// 使用配置对象
RestAssured.config = RestAssured.config()
    .sslConfig(SSLConfig.sslConfig().relaxedHTTPSValidation())
    .connectionTimeout(new ConnectionConfig(30000, 60000))
    .httpClient(HttpClientConfig.httpClientConfig()
        .setParam("http.protocol.content-charset", "UTF-8"))
    .encoderConfig(EncoderConfig.encoderConfig()
        .defaultContentCharset("UTF-8"))
    .decoderConfig(DecoderConfig.decoderConfig()
        .defaultContentCharset("UTF-8"))
    .sessionConfig(SessionConfig.sessionConfig()
        .sessionIdName("JSESSIONID"));
```

### 2.7.3 过滤器使用

```java
// 全局过滤器
RestAssured.filters(
    new RequestLoggingFilter(),
    new ResponseLoggingFilter()
);

// 请求级别过滤器
given()
    .filter(new RequestLoggingFilter(LogDetail.ALL))
    .filter(new ResponseLoggingFilter(LogDetail.ALL))
    .when()
    .get("/api/users");

// 自定义过滤器
Filter customFilter = new Filter() {
    @Override
    public Response filter(FilterableRequestSpecification requestSpec, 
                         FilterableResponseSpecification responseSpec, 
                         FilterContext ctx) {
        System.out.println("执行自定义过滤器逻辑");
        return ctx.next(requestSpec, responseSpec);
    }
};

given()
    .filter(customFilter)
    .when()
    .get("/api/users");
```

## 2.8 实践练习

### 练习1：构建复杂请求

创建一个测试，构建包含以下元素的请求：
- 基础URI：https://reqres.in/api
- 基础路径：/users
- 查询参数：page=2&delay=3
- 请求头：Accept=application/json, Authorization=Bearer token123
- 路径参数：userId=5

### 练习2：复杂响应验证

创建一个测试，验证响应中：
- 状态码为200
- 响应头Content-Type为application/json
- 响应体包含data数组，且数组大小大于0
- data数组中第一个用户的id、email和first_name字段不为空
- 响应时间小于2秒

### 练习3：提取并验证数据

创建一个测试，执行以下操作：
1. 获取用户列表
2. 提取第一个用户的ID
3. 使用提取的ID获取该用户的详细信息
4. 验证详细信息与列表中的信息一致

## 2.9 总结

本章深入介绍了REST Assured的基础语法和核心概念，包括：

1. **Given-When-Then语法结构** - 理解如何构建可读性强的测试代码
2. **请求构建** - 掌握请求规范、请求头、参数和请求体的设置方法
3. **响应验证** - 学习状态码、响应头、Cookie和响应体验证技巧
4. **数据提取** - 了解如何从响应中提取所需数据
5. **日志记录与调试** - 掌握调试和问题排查方法
6. **配置与过滤器** - 学习全局配置和自定义过滤器的使用

通过本章的学习，您应该能够编写结构清晰、功能完整的REST Assured测试。在下一章中，我们将深入探讨请求构建与参数处理的高级技巧。