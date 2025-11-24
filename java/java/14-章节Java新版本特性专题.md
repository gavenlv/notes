# 第14章 Java新版本特性专题

## 本章概述

Java作为一门持续发展的编程语言，每隔一段时间就会发布新版本，引入许多新特性和改进。这些新特性不仅提升了开发效率，还增强了语言的表达能力和性能。本章将详细介绍Java 8到Java 17中的一些重要新特性，帮助开发者更好地利用现代Java进行开发。

## 目录

1. [Java 8新特性](#java-8新特性)
2. [Java 9新特性](#java-9新特性)
3. [Java 10新特性](#java-10新特性)
4. [Java 11新特性](#java-11新特性)
5. [Java 12-14新特性](#java-12-14新特性)
6. [Java 15-17新特性](#java-15-17新特性)
7. [实践案例](#实践案例)

## Java 8新特性

Java 8是Java历史上最重要的版本之一，引入了许多革命性的特性。

### Lambda表达式

Lambda表达式是Java 8最重要的新特性之一，它允许我们将函数作为方法的参数传递。

```java
// 传统的匿名内部类写法
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
Collections.sort(names, new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return a.compareTo(b);
    }
});

// Lambda表达式写法
Collections.sort(names, (a, b) -> a.compareTo(b));

// 更简洁的写法
names.sort(String::compareTo);
```

### Stream API

Stream API提供了一种高效且易于使用的处理数据的方式。

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David", "Eve");

// 过滤长度大于3的名字并转换为大写
List<String> result = names.stream()
    .filter(name -> name.length() > 3)
    .map(String::toUpperCase)
    .collect(Collectors.toList());

// 计算名字长度的总和
int totalLength = names.stream()
    .mapToInt(String::length)
    .sum();

// 查找第一个以"A"开头的名字
Optional<String> firstName = names.stream()
    .filter(name -> name.startsWith("A"))
    .findFirst();
```

### 函数式接口

Java 8引入了函数式接口的概念，即只有一个抽象方法的接口。

```java
@FunctionalInterface
public interface Calculator {
    int calculate(int a, int b);
}

// 使用Lambda表达式实现函数式接口
Calculator add = (a, b) -> a + b;
Calculator multiply = (a, b) -> a * b;

int result1 = add.calculate(5, 3); // 8
int result2 = multiply.calculate(5, 3); // 15
```

### Optional类

Optional类是一个可以为null的容器对象，用来避免空指针异常。

```java
public class UserService {
    public Optional<User> findUserById(Long id) {
        // 模拟数据库查询
        if (id <= 0) {
            return Optional.empty();
        }
        return Optional.of(new User(id, "User" + id));
    }
    
    public String getUserName(Long id) {
        return findUserById(id)
            .map(User::getName)
            .orElse("Unknown User");
    }
}
```

### 新的日期时间API

Java 8引入了新的日期时间API，解决了旧API的线程安全问题和设计缺陷。

```java
// 创建LocalDate
LocalDate today = LocalDate.now();
LocalDate specificDate = LocalDate.of(2023, 12, 25);

// 创建LocalTime
LocalTime now = LocalTime.now();
LocalTime specificTime = LocalTime.of(14, 30, 0);

// 创建LocalDateTime
LocalDateTime dateTime = LocalDateTime.now();
LocalDateTime specificDateTime = LocalDateTime.of(2023, 12, 25, 14, 30);

// 日期运算
LocalDate tomorrow = today.plusDays(1);
LocalDate nextWeek = today.plusWeeks(1);

// 格式化
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
String formatted = dateTime.format(formatter);
```

## Java 9新特性

### 模块系统（JPMS）

Java 9引入了模块系统，用于组织和管理代码。

```java
// module-info.java
module com.example.myapp {
    requires java.base;
    requires java.logging;
    exports com.example.myapp.api;
    opens com.example.myapp.impl to java.xml.bind;
}
```

### JShell

JShell是Java 9引入的交互式Java REPL工具，方便学习和测试Java代码。

```bash
# 启动JShell
jshell

# 定义变量
jshell> int x = 10;
x ==> 10

# 定义方法
jshell> int square(int x) { return x * x; }
|  created method square(int)

# 调用方法
jshell> square(5)
$3 ==> 25
```

### 接口私有方法

Java 9允许在接口中定义私有方法，提高代码复用性。

```java
public interface Calculator {
    default int add(int a, int b) {
        validateInputs(a, b);
        return a + b;
    }
    
    default int subtract(int a, int b) {
        validateInputs(a, b);
        return a - b;
    }
    
    private void validateInputs(int a, int b) {
        if (a < 0 || b < 0) {
            throw new IllegalArgumentException("Inputs must be non-negative");
        }
    }
}
```

## Java 10新特性

### 局部变量类型推断（var关键字）

Java 10引入了var关键字，允许编译器自动推断局部变量的类型。

```java
// 传统写法
List<String> names = new ArrayList<String>();
Map<String, Integer> map = new HashMap<String, Integer>();

// 使用var关键字
var names = new ArrayList<String>();
var map = new HashMap<String, Integer>();
var stream = names.stream();
var result = map.entrySet().iterator();
```

## Java 11新特性

### HTTP Client API

Java 11标准化了HTTP Client API，提供了现代化的HTTP客户端功能。

```java
// 同步GET请求
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.github.com/users/octocat"))
    .build();

HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
System.out.println(response.body());

// 异步GET请求
CompletableFuture<HttpResponse<String>> futureResponse = client.sendAsync(request, HttpResponse.BodyHandlers.ofString());
futureResponse.thenAccept(res -> System.out.println(res.body()));

// POST请求
HttpRequest postRequest = HttpRequest.newBuilder()
    .uri(URI.create("https://httpbin.org/post"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString("{\"name\":\"test\"}"))
    .build();

HttpResponse<String> postResponse = client.send(postRequest, HttpResponse.BodyHandlers.ofString());
```

### 字符串新方法

Java 11为String类增加了几个实用的方法。

```java
// 判断字符串是否为空白
String blank = "   ";
boolean isBlank = blank.isBlank(); // true

// 去除首尾空白字符
String stripped = "  Hello World  ".strip(); // "Hello World"

// 重复字符串
String repeated = "Java".repeat(3); // "JavaJavaJava"

// 行数统计
String multiline = "Line 1\nLine 2\nLine 3";
long lineCount = multiline.lines().count(); // 3
```

## Java 12-14新特性

### Switch表达式（预览特性）

Java 12开始引入Switch表达式作为预览特性，在Java 14中成为正式特性。

```java
// 传统switch语句
String dayType;
switch (day) {
    case MONDAY:
    case TUESDAY:
    case WEDNESDAY:
    case THURSDAY:
    case FRIDAY:
        dayType = "Weekday";
        break;
    case SATURDAY:
    case SUNDAY:
        dayType = "Weekend";
        break;
    default:
        dayType = "Invalid";
}

// Switch表达式
String dayType = switch (day) {
    case MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY -> "Weekday";
    case SATURDAY, SUNDAY -> "Weekend";
    default -> "Invalid";
};

// 使用yield返回值
int result = switch (operation) {
    case "+" -> a + b;
    case "-" -> a - b;
    case "*" -> a * b;
    case "/" -> {
        if (b == 0) {
            yield -1; // 不能除以0
        } else {
            yield a / b;
        }
    }
    default -> throw new IllegalArgumentException("Invalid operation");
};
```

### 文本块（预览特性）

Java 13引入文本块作为预览特性，在Java 15中成为正式特性。

```java
// 传统字符串拼接
String json = "{\n" +
              "  \"name\": \"John Doe\",\n" +
              "  \"age\": 30,\n" +
              "  \"city\": \"New York\"\n" +
              "}";

// 使用文本块
String json = """
              {
                "name": "John Doe",
                "age": 30,
                "city": "New York"
              }
              """;

// HTML模板
String html = """
              <html>
                <body>
                  <h1>Hello, World!</h1>
                </body>
              </html>
              """;
```

## Java 15-17新特性

### Sealed Classes（密封类）

Java 15开始引入密封类作为预览特性，在Java 17中成为正式特性。

```java
// 密封类只能被指定的类继承
public sealed class Shape
    permits Circle, Rectangle, Square {
    // ...
}

public final class Circle extends Shape {
    // ...
}

public non-sealed class Rectangle extends Shape {
    // 可以被其他类继承
}

public final class Square extends Rectangle {
    // ...
}
```

### Pattern Matching for instanceof

Java 14开始引入instanceof的模式匹配作为预览特性，在Java 16中成为正式特性。

```java
// 传统写法
if (obj instanceof String) {
    String str = (String) obj;
    System.out.println(str.toUpperCase());
}

// 使用模式匹配
if (obj instanceof String str) {
    System.out.println(str.toUpperCase());
}

// 在条件判断中使用
if (obj instanceof String str && str.length() > 5) {
    System.out.println(str.substring(0, 5));
}
```

### Records（记录类）

Java 14开始引入Records作为预览特性，在Java 16中成为正式特性。

```java
// 传统POJO类
public class Person {
    private final String name;
    private final int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String name() { return name; }
    public int age() { return age; }
    
    @Override
    public boolean equals(Object obj) {
        // 实现equals方法
    }
    
    @Override
    public int hashCode() {
        // 实现hashCode方法
    }
    
    @Override
    public String toString() {
        // 实现toString方法
    }
}

// 使用Record简化
public record Person(String name, int age) {}

// Record还可以有额外的方法
public record Point(int x, int y) {
    public double distanceFromOrigin() {
        return Math.sqrt(x * x + y * y);
    }
}
```

## 实践案例

### 案例1：使用Stream API处理数据

```java
public class DataProcessor {
    public static class Employee {
        private String name;
        private String department;
        private double salary;
        private int age;
        
        // 构造函数和getter方法
        public Employee(String name, String department, double salary, int age) {
            this.name = name;
            this.department = department;
            this.salary = salary;
            this.age = age;
        }
        
        // getter方法
        public String getName() { return name; }
        public String getDepartment() { return department; }
        public double getSalary() { return salary; }
        public int getAge() { return age; }
    }
    
    public static void processEmployeeData(List<Employee> employees) {
        // 按部门分组并计算平均工资
        Map<String, Double> avgSalariesByDept = employees.stream()
            .collect(Collectors.groupingBy(
                Employee::getDepartment,
                Collectors.averagingDouble(Employee::getSalary)
            ));
        
        // 找出每个部门工资最高的员工
        Map<String, Optional<Employee>> topEarnersByDept = employees.stream()
            .collect(Collectors.groupingBy(
                Employee::getDepartment,
                Collectors.maxBy(Comparator.comparingDouble(Employee::getSalary))
            ));
        
        // 年龄在25-35岁之间的员工，按工资降序排列
        List<Employee> midCareerEmployees = employees.stream()
            .filter(emp -> emp.getAge() >= 25 && emp.getAge() <= 35)
            .sorted(Comparator.comparingDouble(Employee::getSalary).reversed())
            .collect(Collectors.toList());
        
        // 输出结果
        System.out.println("Average salaries by department:");
        avgSalariesByDept.forEach((dept, avgSalary) -> 
            System.out.printf("%s: %.2f%n", dept, avgSalary));
    }
}
```

### 案例2：使用HTTP Client发送请求

```java
public class GitHubApiClient {
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    
    public GitHubApiClient() {
        this.httpClient = HttpClient.newHttpClient();
        this.objectMapper = new ObjectMapper();
    }
    
    public Optional<User> getUser(String username) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.github.com/users/" + username))
                .header("Accept", "application/vnd.github.v3+json")
                .build();
            
            HttpResponse<String> response = httpClient.send(request, 
                HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                User user = objectMapper.readValue(response.body(), User.class);
                return Optional.of(user);
            }
        } catch (Exception e) {
            System.err.println("Error fetching user: " + e.getMessage());
        }
        return Optional.empty();
    }
    
    public CompletableFuture<List<Repository>> getUserRepositoriesAsync(String username) {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://api.github.com/users/" + username + "/repos"))
            .header("Accept", "application/vnd.github.v3+json")
            .build();
        
        return httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
            .thenApply(HttpResponse::body)
            .thenApply(this::parseRepositories)
            .exceptionally(throwable -> {
                System.err.println("Error fetching repositories: " + throwable.getMessage());
                return Collections.emptyList();
            });
    }
    
    private List<Repository> parseRepositories(String json) {
        try {
            return objectMapper.readValue(json, 
                new TypeReference<List<Repository>>() {});
        } catch (Exception e) {
            System.err.println("Error parsing repositories: " + e.getMessage());
            return Collections.emptyList();
        }
    }
    
    // User和Repository类定义
    public static class User {
        public String login;
        public String name;
        public String company;
        public int public_repos;
        // getter和setter方法...
    }
    
    public static class Repository {
        public String name;
        public String description;
        public String language;
        public int stargazers_count;
        // getter和setter方法...
    }
}
```

### 案例3：使用Records简化数据类

```java
// 使用Record定义配置类
public record DatabaseConfig(
    String host,
    int port,
    String database,
    String username,
    String password
) {
    public DatabaseConfig {
        // 验证参数
        Objects.requireNonNull(host, "Host cannot be null");
        if (port <= 0 || port > 65535) {
            throw new IllegalArgumentException("Invalid port: " + port);
        }
        Objects.requireNonNull(database, "Database cannot be null");
    }
    
    // 自定义方法
    public String connectionString() {
        return String.format("jdbc:mysql://%s:%d/%s", host, port, database);
    }
}

// 使用Record定义API响应
public record ApiResponse<T>(
    boolean success,
    String message,
    T data,
    long timestamp
) {
    // 静态工厂方法
    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(true, "Success", data, System.currentTimeMillis());
    }
    
    public static <T> ApiResponse<T> error(String message) {
        return new ApiResponse<>(false, message, null, System.currentTimeMillis());
    }
}

// 使用示例
public class RecordUsageExample {
    public static void main(String[] args) {
        // 创建配置
        DatabaseConfig config = new DatabaseConfig("localhost", 3306, "mydb", "user", "pass");
        System.out.println("Connection string: " + config.connectionString());
        
        // 创建API响应
        ApiResponse<String> successResponse = ApiResponse.success("Operation completed");
        ApiResponse<String> errorResponse = ApiResponse.error("Something went wrong");
        
        System.out.println("Success: " + successResponse);
        System.out.println("Error: " + errorResponse);
    }
}
```

## 总结

Java新版本不断引入创新特性，极大地提升了开发体验和代码质量：

1. **Java 8**：Lambda表达式、Stream API、Optional类等函数式编程特性，彻底改变了Java的编程范式。

2. **Java 9**：模块系统为大型应用提供了更好的封装和依赖管理。

3. **Java 10-11**：局部变量类型推断、HTTP Client API等特性进一步简化了开发。

4. **Java 12-14**：Switch表达式、文本块等特性提高了代码的可读性和表达能力。

5. **Java 15-17**：密封类、模式匹配、记录类等现代语言特性使Java更加现代化。

在实际开发中，我们应该：
- 积极采用这些新特性来提高开发效率
- 注意兼容性问题，在升级Java版本时进行充分测试
- 持续关注Java的发展，及时学习新特性
- 在团队中推广最佳实践，确保代码质量和一致性

通过合理运用这些新特性，我们可以编写出更加简洁、高效和易维护的Java代码。