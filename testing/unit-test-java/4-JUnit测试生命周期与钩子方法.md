# 第4章：JUnit测试生命周期与钩子方法

## 4.1 测试生命周期概述

### 4.1.1 生命周期阶段

JUnit测试生命周期包含以下几个关键阶段：

1. **测试类实例化**：每个测试类都会创建一个实例
2. **@BeforeAll执行**：在所有测试方法之前执行一次
3. **@BeforeEach执行**：在每个测试方法之前执行
4. **测试方法执行**：实际的测试方法
5. **@AfterEach执行**：在每个测试方法之后执行
6. **@AfterAll执行**：在所有测试方法之后执行

```java
import org.junit.jupiter.api.*;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class LifecycleDemoTest {
    
    @BeforeAll
    static void setUpAll() {
        System.out.println("1. @BeforeAll - 所有测试前执行一次");
    }
    
    @BeforeEach
    void setUp() {
        System.out.println("2. @BeforeEach - 每个测试前执行");
    }
    
    @Test
    @Order(1)
    void firstTest() {
        System.out.println("3. 执行第一个测试方法");
    }
    
    @Test
    @Order(2)
    void secondTest() {
        System.out.println("3. 执行第二个测试方法");
    }
    
    @AfterEach
    void tearDown() {
        System.out.println("4. @AfterEach - 每个测试后执行");
    }
    
    @AfterAll
    static void tearDownAll() {
        System.out.println("5. @AfterAll - 所有测试后执行一次");
    }
}
```

执行顺序示例输出：
```
1. @BeforeAll - 所有测试前执行一次
2. @BeforeEach - 每个测试前执行
3. 执行第一个测试方法
4. @AfterEach - 每个测试后执行
2. @BeforeEach - 每个测试前执行
3. 执行第二个测试方法
4. @AfterEach - 每个测试后执行
5. @AfterAll - 所有测试后执行一次
```

### 4.1.2 生命周期注解对比

| 注解 | 执行时机 | 执行次数 | 是否静态 | 用途 |
|------|----------|----------|----------|------|
| @BeforeAll | 所有测试方法前 | 1次 | 必须是静态 | 初始化共享资源 |
| @BeforeEach | 每个测试方法前 | N次（N为测试方法数） | 非静态 | 初始化单个测试环境 |
| @AfterEach | 每个测试方法后 | N次 | 非静态 | 清理单个测试环境 |
| @AfterAll | 所有测试方法后 | 1次 | 必须是静态 | 清理共享资源 |

## 4.2 生命周期钩子方法详解

### 4.2.1 @BeforeAll 和 @AfterAll

这两个注解用于执行全局的初始化和清理操作，通常用于：

- 初始化昂贵的共享资源
- 设置和拆除数据库连接
- 启动和停止服务器
- 初始化缓存或单例对象

```java
import org.junit.jupiter.api.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)  // 允许非静态的@BeforeAll/@AfterAll
public class GlobalResourceTest {
    
    private static DatabaseConnection dbConnection;
    private static TestServer testServer;
    
    @BeforeAll
    static void initializeGlobalResources() throws Exception {
        System.out.println("初始化全局资源...");
        
        // 初始化数据库连接
        dbConnection = new DatabaseConnection();
        dbConnection.connect();
        
        // 启动测试服务器
        testServer = new TestServer();
        testServer.start();
        
        // 准备测试数据
        dbConnection.execute("CREATE TABLE IF NOT EXISTS users (id INT, name VARCHAR(50))");
        dbConnection.execute("INSERT INTO users VALUES (1, 'test-user')");
        
        System.out.println("全局资源初始化完成");
    }
    
    @AfterAll
    static void cleanupGlobalResources() {
        System.out.println("清理全局资源...");
        
        if (dbConnection != null) {
            // 清理测试数据
            dbConnection.execute("DROP TABLE IF EXISTS users");
            // 关闭数据库连接
            dbConnection.close();
        }
        
        if (testServer != null) {
            // 停止测试服务器
            testServer.stop();
        }
        
        System.out.println("全局资源清理完成");
    }
    
    @Test
    void testDatabaseOperations() {
        // 使用共享的数据库连接进行测试
        List<User> users = dbConnection.query("SELECT * FROM users", User.class);
        assertEquals(1, users.size(), "应该有一条测试用户记录");
        assertEquals("test-user", users.get(0).getName(), "用户名应该是'test-user'");
    }
    
    @Test
    void testServerOperations() {
        // 使用共享的测试服务器进行测试
        Response response = testServer.request("/api/users/1");
        assertEquals(200, response.getStatusCode(), "应该返回200状态码");
        
        User user = response.getBody(User.class);
        assertEquals("test-user", user.getName(), "用户名应该是'test-user'");
    }
}
```

### 4.2.2 @BeforeEach 和 @AfterEach

这两个注解用于执行每个测试方法前后的准备和清理工作，通常用于：

- 重置对象状态
- 准备测试数据
- 清理临时文件
- 重置计数器或标志

```java
public class PerTestResourceTest {
    
    private List<String> testList;
    private File tempFile;
    private long startTime;
    
    @BeforeEach
    void setUpBeforeEachTest() throws IOException {
        System.out.println("准备测试环境...");
        
        // 初始化测试列表
        testList = new ArrayList<>();
        
        // 创建临时文件
        tempFile = File.createTempFile("test", ".txt");
        
        // 记录开始时间
        startTime = System.currentTimeMillis();
        
        System.out.println("测试环境准备完成");
    }
    
    @AfterEach
    void tearDownAfterEachTest() {
        System.out.println("清理测试环境...");
        
        // 清理测试列表
        testList.clear();
        testList = null;
        
        // 删除临时文件
        if (tempFile != null && tempFile.exists()) {
            tempFile.delete();
        }
        
        // 记录测试执行时间
        long duration = System.currentTimeMillis() - startTime;
        System.out.println("测试执行时间: " + duration + "ms");
        
        System.out.println("测试环境清理完成");
    }
    
    @Test
    void testListOperations() {
        // 测试列表操作
        testList.add("item1");
        testList.add("item2");
        
        assertEquals(2, testList.size(), "列表应该包含2个元素");
        assertTrue(testList.contains("item1"), "列表应该包含'item1'");
        assertTrue(testList.contains("item2"), "列表应该包含'item2'");
    }
    
    @Test
    void testFileOperations() throws IOException {
        // 测试文件操作
        Files.write(tempFile.toPath(), "test content".getBytes());
        
        String content = new String(Files.readAllBytes(tempFile.toPath()));
        assertEquals("test content", content, "文件内容应该正确");
    }
}
```

## 4.3 测试实例生命周期

### 4.3.1 两种实例生命周期模式

JUnit 5支持两种测试实例生命周期模式：

1. **PER_METHOD（默认）**：每个测试方法创建新的测试类实例
2. **PER_CLASS**：整个测试类只创建一个实例

```java
// 默认的PER_METHOD模式（每个测试方法一个实例）
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class PerMethodLifecycleTest {
    
    private static int instanceCounter = 0;
    private int instanceField;
    
    public PerMethodLifecycleTest() {
        instanceCounter++;
        instanceField = instanceCounter;
        System.out.println("创建实例 #" + instanceCounter);
    }
    
    @Test
    @Order(1)
    void test1() {
        System.out.println("test1, instanceField = " + instanceField);
        assertEquals(1, instanceField);
    }
    
    @Test
    @Order(2)
    void test2() {
        System.out.println("test2, instanceField = " + instanceField);
        assertEquals(2, instanceField);
    }
}

// PER_CLASS模式（整个测试类一个实例）
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class PerClassLifecycleTest {
    
    private static int instanceCounter = 0;
    private int instanceField;
    
    public PerClassLifecycleTest() {
        instanceCounter++;
        instanceField = instanceCounter;
        System.out.println("创建实例 #" + instanceCounter);
    }
    
    @Test
    @Order(1)
    void test1() {
        System.out.println("test1, instanceField = " + instanceField);
        assertEquals(1, instanceField);
    }
    
    @Test
    @Order(2)
    void test2() {
        System.out.println("test2, instanceField = " + instanceField);
        assertEquals(1, instanceField);
    }
}
```

### 4.3.2 生命周期模式的选择

| 场景 | 推荐模式 | 原因 |
|------|----------|------|
| 大多数测试用例 | PER_METHOD | 避免测试间状态污染 |
| 需要共享非静态字段 | PER_CLASS | 简化资源共享 |
| 测试实例创建成本高 | PER_CLASS | 提高测试执行效率 |
| 需要在@BeforeAll中使用实例字段 | PER_CLASS | 非静态访问实例字段 |

```java
// 适合使用PER_CLASS模式的例子
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class ExpensiveResourceTest {
    
    private DatabaseService databaseService;  // 昂贵的资源
    private Map<String, User> userCache;      // 需要在测试间共享
    
    // PER_CLASS模式下，@BeforeAll可以是非静态的
    @BeforeAll
    void initializeSharedResources() {
        // 初始化昂贵的资源
        databaseService = new DatabaseService();
        databaseService.initialize();
        
        // 初始化共享缓存
        userCache = new HashMap<>();
    }
    
    @AfterAll
    void cleanupSharedResources() {
        if (databaseService != null) {
            databaseService.shutdown();
        }
    }
    
    @BeforeEach
    void setupForTest() {
        // 每个测试前准备，但可以访问共享资源
        databaseService.clearTestData();
        userCache.clear();
    }
    
    @Test
    void testUserCreation() {
        // 测试用户创建
        User user = new User("test-user");
        boolean created = databaseService.saveUser(user);
        
        assertTrue(created, "用户创建应该成功");
        
        // 缓存用户信息
        userCache.put(user.getId(), user);
        assertEquals(1, userCache.size(), "缓存中应该有一个用户");
    }
    
    @Test
    void testUserRetrieval() {
        // 测试用户检索
        User user = new User("retrieval-user");
        databaseService.saveUser(user);
        
        User retrievedUser = databaseService.getUser(user.getId());
        assertNotNull(retrievedUser, "应该能检索到用户");
        assertEquals("retrieval-user", retrievedUser.getName(), "用户名应该匹配");
        
        // 缓存用户信息
        userCache.put(user.getId(), user);
        assertTrue(userCache.containsKey(user.getId()), "缓存中应该包含该用户");
    }
}
```

## 4.4 测试构造函数

### 4.4.1 使用构造函数初始化

在JUnit 5中，测试类的构造函数可以用于初始化测试依赖。

```java
public class ConstructorInjectionTest {
    
    private final UserService userService;
    private final EmailService emailService;
    private final TestConfig config;
    
    // 通过构造函数注入依赖
    public ConstructorInjectionTest(UserService userService, EmailService emailService, TestConfig config) {
        this.userService = userService;
        this.emailService = emailService;
        this.config = config;
        System.out.println("构造函数初始化完成，注入了测试依赖");
    }
    
    @Test
    void testUserServiceWithDependency() {
        User user = new User("test-user");
        
        // 使用注入的服务进行测试
        boolean result = userService.createUser(user);
        assertTrue(result, "用户创建应该成功");
        
        // 验证邮件服务被调用
        boolean emailSent = emailService.welcomeEmailSent(user.getEmail());
        assertTrue(emailSent, "欢迎邮件应该已发送");
    }
    
    @Test
    void testConfigurationAccess() {
        // 使用注入的配置
        int maxUsers = config.getMaxUsersPerAccount();
        assertTrue(maxUsers > 0, "最大用户数应该大于0");
        
        String apiUrl = config.getApiUrl();
        assertNotNull(apiUrl, "API URL不应该为null");
        assertTrue(apiUrl.startsWith("http"), "API URL应该以http开头");
    }
}
```

### 4.4.2 参数化构造函数

JUnit 5支持在测试类中使用参数化构造函数。

```java
// 配置参数化测试
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class ParameterizedConstructorTest {
    
    private final String input;
    private final boolean expectedResult;
    private final PalindromeChecker checker;
    
    // 参数化构造函数
    public ParameterizedConstructorTest(String input, boolean expectedResult) {
        this.input = input;
        this.expectedResult = expectedResult;
        this.checker = new PalindromeChecker();
    }
    
    @Test
    void palindromeTest() {
        boolean actualResult = checker.isPalindrome(input);
        assertEquals(expectedResult, actualResult, 
            String.format("'%s'的回文检查结果应该是%s", input, expectedResult));
    }
    
    // 提供测试参数的静态方法
    @ParameterizedTest
    @MethodSource("palindromeTestCases")
    void testWithParameters(String input, boolean expected) {
        boolean result = checker.isPalindrome(input);
        assertEquals(expected, result);
    }
    
    static Stream<Arguments> palindromeTestCases() {
        return Stream.of(
            Arguments.of("level", true),
            Arguments.of("hello", false),
            Arguments.of("madam", true),
            Arguments.of("java", false)
        );
    }
}
```

## 4.5 条件执行

### 4.5.1 基于操作系统的条件测试

```java
import org.junit.jupiter.api.condition.*;

public class ConditionalExecutionTest {
    
    @Test
    @EnabledOnOs(OS.WINDOWS)
    void windowsOnlyTest() {
        System.out.println("这个测试只在Windows上运行");
        // Windows特定的测试逻辑
    }
    
    @Test
    @EnabledOnOs({OS.MAC, OS.LINUX})
    void macOrLinuxTest() {
        System.out.println("这个测试只在Mac或Linux上运行");
        // Unix-like系统的测试逻辑
    }
    
    @Test
    @DisabledOnOs(OS.WINDOWS)
    void notOnWindowsTest() {
        System.out.println("这个测试不在Windows上运行");
        // 非Windows系统的测试逻辑
    }
}
```

### 4.5.2 基于Java版本的条件测试

```java
public class JavaVersionConditionalTest {
    
    @Test
    @EnabledOnJre({JRE.JAVA_8, JRE.JAVA_11})
    void java8Or11Test() {
        System.out.println("这个测试只在Java 8或11上运行");
        // 适用于Java 8和11的测试逻辑
    }
    
    @Test
    @EnabledOnJre(JRE.JAVA_17)
    void java17OnlyTest() {
        System.out.println("这个测试只在Java 17上运行");
        // Java 17特性的测试逻辑
    }
    
    @Test
    @DisabledOnJre(JRE.JAVA_8)
    void notJava8Test() {
        System.out.println("这个测试不在Java 8上运行");
        // 需要Java 9+特性的测试逻辑
    }
}
```

### 4.5.3 基于系统属性的条件测试

```java
public class SystemPropertyConditionalTest {
    
    @Test
    @EnabledIfSystemProperty(named = "test.profile", matches = "integration")
    void integrationProfileTest() {
        System.out.println("这个测试只在test.profile=integration时运行");
        // 集成测试逻辑
    }
    
    @Test
    @EnabledIfSystemProperty(named = "database.url", matches = ".*h2.*")
    void h2DatabaseTest() {
        System.out.println("这个测试只在数据库是H2时运行");
        // H2数据库特定的测试逻辑
    }
    
    @Test
    @DisabledIfSystemProperty(named = "test.slow", matches = "true")
    void fastTestOnly() {
        System.out.println("这个测试在test.slow不为true时运行");
        // 快速测试逻辑
    }
    
    @Test
    @EnabledIfEnvironmentVariable(named = "CI", matches = "true")
    void ciOnlyTest() {
        System.out.println("这个测试只在CI环境运行");
        // CI环境特定的测试逻辑
    }
}
```

### 4.5.4 自定义条件注解

```java
// 自定义条件注解
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@ExtendWith(CustomConditionExtension.class)
public @interface CustomCondition {
    String value();
}

// 自定义条件扩展
public class CustomConditionExtension implements ExecutionCondition, BeforeEachCallback {
    
    @Override
    public ConditionEvaluationResult evaluateExecutionCondition(
            ExtensionContext context) {
        
        // 检查测试类或方法是否有@CustomCondition注解
        Optional<CustomCondition> annotation = context.getElement()
            .flatMap(el -> el.getAnnotation(CustomCondition.class));
            
        if (!annotation.isPresent()) {
            return ConditionEvaluationResult.enabled("未使用@CustomCondition注解");
        }
        
        String condition = annotation.get().value();
        
        // 根据条件决定是否执行测试
        if (shouldRun(condition)) {
            return ConditionEvaluationResult.enabled(
                String.format("条件'%s'满足，执行测试", condition));
        } else {
            return ConditionEvaluationResult.disabled(
                String.format("条件'%s'不满足，跳过测试", condition));
        }
    }
    
    @Override
    public void beforeEach(ExtensionContext context) {
        // 在测试执行前的回调
        System.out.println("自定义条件扩展：测试即将开始");
    }
    
    private boolean shouldRun(String condition) {
        // 这里可以实现自定义的条件逻辑
        // 例如：检查配置文件、环境变量等
        return "run".equals(condition);
    }
}

// 使用自定义条件
public class CustomConditionTest {
    
    @Test
    @CustomCondition("run")
    void shouldRunTest() {
        System.out.println("条件满足，执行测试");
        assertTrue(true);
    }
    
    @Test
    @CustomCondition("skip")
    void shouldSkipTest() {
        System.out.println("这条消息不应该出现");
        fail("这个测试应该被跳过");
    }
}
```

## 4.6 测试执行顺序控制

### 4.6.1 控制测试类执行顺序

```java
// 定义测试执行顺序的注解
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface TestOrder {
    int value();
}

// 自定义测试顺序控制器
public class CustomClassOrderer implements ClassOrderer {
    
    @Override
    public void orderClasses(ClassOrdererContext context) {
        return context.getClassDescriptors().stream()
            .sorted((c1, c2) -> {
                // 获取@TestOrder注解的值
                int order1 = getTestOrder(c1.getTestClass());
                int order2 = getTestOrder(c2.getTestClass());
                
                return Integer.compare(order1, order2);
            })
            .collect(Collectors.toList());
    }
    
    private int getTestOrder(Class<?> testClass) {
        TestOrder annotation = testClass.getAnnotation(TestOrder.class);
        return annotation != null ? annotation.value() : Integer.MAX_VALUE;
    }
}

// 使用自定义顺序
@TestClassOrder(CustomClassOrderer.class)
public class TestOrderingExample {
    
    @TestOrder(1)
    public static class FirstTestSuite {
        @Test void test1() { System.out.println("第一组测试1"); }
        @Test void test2() { System.out.println("第一组测试2"); }
    }
    
    @TestOrder(2)
    public static class SecondTestSuite {
        @Test void test1() { System.out.println("第二组测试1"); }
        @Test void test2() { System.out.println("第二组测试2"); }
    }
    
    @TestOrder(3)
    public static class ThirdTestSuite {
        @Test void test1() { System.out.println("第三组测试1"); }
        @Test void test2() { System.out.println("第三组测试2"); }
    }
}
```

### 4.6.2 测试执行依赖

虽然不推荐测试间依赖，但有时确实需要控制执行顺序：

```java
@TestMethodOrder(OrderAnnotation.class)
public class TestDependencyExample {
    
    private static String sharedState;
    
    @Test
    @Order(1)
    void setupSharedState() {
        sharedState = "initialized";
        System.out.println("初始化共享状态: " + sharedState);
    }
    
    @Test
    @Order(2)
    @EnabledIfSystemProperty(named = "test.dependencies", matches = "true")
    void useSharedState() {
        assertNotNull(sharedState, "共享状态应该已经初始化");
        assertEquals("initialized", sharedState, "共享状态应该正确");
        System.out.println("使用共享状态: " + sharedState);
    }
    
    @Test
    @Order(3)
    @EnabledIfSystemProperty(named = "test.dependencies", matches = "true")
    void modifySharedState() {
        sharedState = "modified";
        System.out.println("修改共享状态: " + sharedState);
    }
    
    @Test
    @Order(4)
    @EnabledIfSystemProperty(named = "test.dependencies", matches = "true")
    void verifyModifiedState() {
        assertEquals("modified", sharedState, "共享状态应该已被修改");
        System.out.println("验证修改后的状态: " + sharedState);
    }
}
```

## 4.7 生命周期最佳实践

### 4.7.1 资源管理原则

1. **最小化共享资源**：尽量使用@BeforeEach而非@BeforeAll
2. **明确清理资源**：使用@AfterAll和@AfterEach确保资源释放
3. **处理异常**：在钩子方法中适当处理异常
4. **资源隔离**：避免测试间相互影响

```java
public class ResourceManagementBestPractices {
    
    // 好的做法：最小化共享资源
    @BeforeEach
    void setupPerTest() {
        // 每个测试创建独立的资源
        testRepository = new InMemoryRepository();
        testUserService = new UserService(testRepository);
    }
    
    // 谨慎使用：全局共享资源
    @BeforeAll
    static void setupGlobalResources() throws Exception {
        // 只在必要时使用全局资源
        connectionPool = new ConnectionPool(10);
        connectionPool.initialize();
    }
    
    // 好的做法：确保资源清理
    @AfterAll
    static void cleanupGlobalResources() {
        if (connectionPool != null) {
            try {
                connectionPool.shutdown();
            } catch (Exception e) {
                // 适当处理异常，不要影响其他清理工作
                System.err.println("关闭连接池时出错: " + e.getMessage());
            }
        }
    }
    
    // 好的做法：每个测试后清理
    @AfterEach
    void cleanupPerTest() {
        if (testRepository != null) {
            testRepository.clear();  // 清理测试数据
        }
    }
}
```

### 4.7.2 避免常见陷阱

1. **测试独立性**：确保测试不依赖于执行顺序
2. **静态字段使用**：谨慎使用静态字段存储测试状态
3. **异常传播**：钩子方法中的异常会影响测试结果
4. **线程安全**：考虑并发测试场景

```java
// 避免的陷阱示例

public class CommonPitfalls {
    
    // 陷阱1：测试间的状态依赖（不推荐）
    private static int counter = 0;
    
    @Test
    void test1() {
        counter = 5;  // 修改共享状态
        assertEquals(5, counter);
    }
    
    @Test
    void test2() {
        // 依赖于test1的执行，如果执行顺序改变就会失败
        assertEquals(5, counter);
    }
    
    // 正确的做法：避免测试间状态依赖
    @Test
    void correctTest1() {
        int localCounter = 5;  // 使用局部变量
        assertEquals(5, localCounter);
    }
    
    @Test
    void correctTest2() {
        int localCounter = 5;  // 独立的状态
        assertEquals(5, localCounter);
    }
    
    // 陷阱2：钩子方法中的异常会影响测试
    @BeforeEach
    void riskySetup() {
        // 这里的异常会导致测试失败
        // 应该添加适当的异常处理
        try {
            riskyOperation();
        } catch (Exception e) {
            // 记录错误但不影响测试
            System.err.println("设置阶段出错: " + e.getMessage());
        }
    }
    
    private void riskyOperation() throws Exception {
        // 可能抛出异常的操作
    }
}
```

## 4.8 小结

本章深入讲解了JUnit的测试生命周期与钩子方法，主要内容包括：

1. **测试生命周期概述**：各个阶段的执行顺序和时机
2. **生命周期钩子方法**：@BeforeAll、@AfterAll、@BeforeEach、@AfterEach的使用
3. **测试实例生命周期**：PER_METHOD和PER_CLASS两种模式的选择
4. **测试构造函数**：依赖注入和参数化构造函数
5. **条件执行**：基于操作系统、Java版本、系统属性的条件测试
6. **测试执行顺序**：控制类和方法执行顺序的方法
7. **生命周期最佳实践**：资源管理和常见陷阱避免

掌握测试生命周期是编写可靠、高效单元测试的基础。在下一章中，我们将学习Mockito框架与模拟对象，了解如何在隔离的环境中测试代码。

## 4.9 实践练习

### 练习1：生命周期实践
1. 创建一个测试类，使用所有生命周期注解
2. 在钩子方法中打印日志，观察执行顺序
3. 比较PER_METHOD和PER_CLASS两种实例生命周期模式的区别

### 练习2：资源管理
1. 创建一个需要昂贵资源的测试类
2. 使用@BeforeAll和@AfterAll管理全局资源
3. 使用@BeforeEach和@AfterEach管理测试特定资源

### 练习3：条件执行
1. 创建基于系统属性的条件测试
2. 编写自定义条件扩展
3. 使用不同的条件组合控制测试执行

通过这些练习，您将深入理解JUnit的生命周期机制，能够编写高效、可靠的测试代码。