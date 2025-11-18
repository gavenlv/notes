# 第2章：JUnit基础概念与核心注解

## 2.1 JUnit框架架构

### 2.1.1 JUnit 5 架构组成

JUnit 5采用了模块化架构，主要由三个子项目组成：

1. **JUnit Platform**：基础平台，负责启动测试框架
2. **JUnit Jupiter**：新的编程模型和扩展模型，支持JUnit 5测试
3. **JUnit Vintage**：提供向后兼容性，支持运行JUnit 3和4编写的测试

```
JUnit 5 架构图
+-------------------+     +-------------------+
|  JUnit Platform   | <-- |  JUnit Jupiter    |
|                   |     |                   |
|  - TestEngine API |     |  - @Test          |
|  - Launcher API   |     |  - Assertions     |
|  - Console Launcher|    |  - Extensions     |
+-------------------+     +-------------------+
         ^                        ^
         |                        |
         |                        |
+-------------------+     +-------------------+
|  JUnit Vintage    |     |  其他测试引擎      |
|                   |     |                   |
|  - 向后兼容       |     |  - TestNG         |
|  - JUnit 3/4支持 |     |  - Spock          |
+-------------------+     +-------------------+
```

### 2.1.2 JUnit 5 vs JUnit 4

| 特性 | JUnit 4 | JUnit 5 |
|------|---------|---------|
| 包名 | org.junit.* | org.junit.jupiter.* |
| 测试注解 | @Test | @Test |
| 断言类 | org.junit.Assert | org.junit.jupiter.api.Assertions |
| 前置/后置 | @Before/@After | @BeforeEach/@AfterEach |
| 类前置/后置 | @BeforeClass/@AfterClass | @BeforeAll/@AfterAll |
| 异常测试 | @Test(expected=...) | assertThrows() |
| 超时测试 | @Test(timeout=...) | assertTimeout() |
| 参数化测试 | 需要额外库 | 内置支持 |

## 2.2 核心注解详解

### 2.2.1 基础测试注解

#### @Test

最核心的注解，标记方法为测试方法。

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class BasicAnnotationTest {
    
    @Test
    public void basicTest() {
        // 这是一个基本测试方法
        assertEquals(2 + 2, 4);
    }
    
    @Test
    void testWithoutPublicModifier() {
        // 测试方法不需要是public（JUnit 5新特性）
        assertTrue(true);
    }
    
    @Test
    @DisplayName("计算两数之和")
    public void testWithDisplayName() {
        // 使用@DisplayName提供友好的测试名称
        Calculator calculator = new Calculator();
        assertEquals(5, calculator.add(2, 3));
    }
}
```

#### @DisplayName

为测试类或测试方法提供自定义的显示名称，支持特殊字符和表情符号。

```java
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("计算器测试类")
public class CalculatorDisplayNameTest {
    
    @Test
    @DisplayName("加法运算测试 ✅")
    public void additionTest() {
        Calculator calculator = new Calculator();
        assertEquals(5, calculator.add(2, 3));
    }
    
    @Test
    @DisplayName("除法运算：5 ÷ 2 = 2.5")
    public void divisionTest() {
        Calculator calculator = new Calculator();
        assertEquals(2.5, calculator.divide(5, 2), 0.001);
    }
    
    @Test
    @DisplayName("😱 除零异常测试")
    public void divisionByZeroTest() {
        Calculator calculator = new Calculator();
        assertThrows(IllegalArgumentException.class, 
            () -> calculator.divide(5, 0));
    }
}
```

### 2.2.2 生命周期注解

#### @BeforeEach 和 @AfterEach

在每个测试方法执行前后分别执行的方法。

```java
import org.junit.jupiter.api.*;

public class LifecycleTest {
    
    private Calculator calculator;
    private int testCount;
    
    @BeforeEach
    void setUp() {
        // 每个测试方法执行前都会执行
        calculator = new Calculator();
        testCount = 0;
        System.out.println("BeforeEach: 初始化测试环境");
    }
    
    @AfterEach
    void tearDown() {
        // 每个测试方法执行后都会执行
        calculator = null;
        System.out.println("AfterEach: 清理测试环境");
    }
    
    @Test
    void testAddition() {
        testCount++;
        assertEquals(5, calculator.add(2, 3));
        System.out.println("测试加法，testCount: " + testCount);
    }
    
    @Test
    void testMultiplication() {
        testCount++;
        assertEquals(6, calculator.multiply(2, 3));
        System.out.println("测试乘法，testCount: " + testCount);
    }
}
```

#### @BeforeAll 和 @AfterAll

在当前测试类中的所有测试方法执行前后分别执行一次的方法。

```java
import org.junit.jupiter.api.*;

public class AllLifecycleTest {
    
    private static Calculator calculator;
    
    @BeforeAll
    static void setUpClass() {
        // 在所有测试方法执行前执行一次
        calculator = new Calculator();
        System.out.println("BeforeAll: 初始化测试类");
    }
    
    @AfterAll
    static void tearDownClass() {
        // 在所有测试方法执行后执行一次
        calculator = null;
        System.out.println("AfterAll: 清理测试类");
    }
    
    @Test
    void testAddition() {
        assertEquals(5, calculator.add(2, 3));
        System.out.println("测试加法");
    }
    
    @Test
    void testSubtraction() {
        assertEquals(-1, calculator.add(-2, 1));
        System.out.println("测试减法");
    }
    
    // 注意：@BeforeAll和@AfterAll方法必须是static的
    // 但在@TestInstance(TestInstance.Lifecycle.PER_CLASS)模式下可以是非static的
}
```

### 2.2.3 禁用和条件测试

#### @Disabled

禁用测试类或测试方法，不会被执行。

```java
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

@Disabled("开发中，稍后完成")
public class DisabledTest {
    
    @Test
    public void notReadyYet() {
        // 这个测试不会运行
        // 因为类被@Disabled标记
    }
    
    @Test
    @Disabled("功能待实现")
    public void featureNotImplemented() {
        // 这个测试也不会运行
        // 因为方法被@Disabled标记
    }
    
    @Test
    public void workingTest() {
        // 但这个测试也不会运行
        // 因为整个类被禁用了
        assertEquals(2 + 2, 4);
    }
}
```

#### @Tag

为测试类或测试方法添加标签，用于组织和过滤测试。

```java
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

@Tag("unit")
@Tag("calculator")
public class TaggedTest {
    
    @Test
    @Tag("addition")
    public void testAddition() {
        Calculator calculator = new Calculator();
        assertEquals(5, calculator.add(2, 3));
    }
    
    @Test
    @Tag("division")
    public void testDivision() {
        Calculator calculator = new Calculator();
        assertEquals(2.5, calculator.divide(5, 2), 0.001);
    }
    
    @Test
    @Tag("slow")  // 标记为慢测试
    public void timeConsumingTest() {
        // 耗时的测试操作
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        assertTrue(true);
    }
}
```

### 2.2.4 重复测试

#### @RepeatedTest

指定测试方法重复执行的次数。

```java
import org.junit.jupiter.api.RepeatedTest;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.api.RepetitionInfo;

public class RepeatedTestDemo {
    
    @RepeatedTest(5)
    public void repeatedTest() {
        // 这个测试会执行5次
        Calculator calculator = new Calculator();
        assertEquals(4, calculator.add(2, 2));
    }
    
    @RepeatedTest(value = 3, name = "{displayName} - 第{currentRepetition}/{totalRepetitions}次")
    public void repeatedTestWithCustomName(RepetitionInfo repetitionInfo) {
        // 自定义重复测试的显示名称
        Calculator calculator = new Calculator();
        assertEquals(6, calculator.multiply(2, 3));
        System.out.println("当前重复次数: " + repetitionInfo.getCurrentRepetition());
    }
    
    @RepeatedTest(4)
    public void repeatedTestWithInfo(TestInfo testInfo, RepetitionInfo repetitionInfo) {
        // 可以获取测试信息和重复信息
        System.out.println("测试方法名: " + testInfo.getTestMethod().get().getName());
        System.out.println("当前重复: " + repetitionInfo.getCurrentRepetition());
        System.out.println("总重复次数: " + repetitionInfo.getTotalRepetitions());
        
        Calculator calculator = new Calculator();
        assertEquals(1, calculator.divide(2, 2));
    }
}
```

## 2.3 测试类与测试方法

### 2.3.1 测试类要求

JUnit 5对测试类的要求非常灵活：

- 测试类可以是public、default（包私有）或不加修饰符
- 测试类不能是抽象类
- 必须有一个无参构造函数
- 通常是一个独立的类，不继承其他类

```java
// 以下是各种有效的测试类声明方式

public class PublicTestClass {
    @Test
    void test() {}
}

class DefaultTestClass {  // 包私有的测试类
    @Test
    void test() {}
}

// 测试类不继承任何特定类（与JUnit 4不同）
class PlainTestClass {
    @Test
    void test() {}
}

// 包含构造函数的测试类
class TestWithConstructor {
    private Calculator calculator;
    
    TestWithConstructor() {
        // 构造函数会在每个测试前执行
        calculator = new Calculator();
    }
    
    @Test
    void test() {
        assertEquals(4, calculator.add(2, 2));
    }
}
```

### 2.3.2 测试方法要求

JUnit 5对测试方法的要求：

- 不能是abstract
- 必须是无参方法
- 返回类型应该是void（虽然JUnit 5允许其他返回类型，但不推荐）
- 不能是private，但可以是protected、package-private或public

```java
import org.junit.jupiter.api.Test;

public class TestMethodVariations {
    
    // 以下是各种有效的测试方法声明
    
    @Test
    public void publicTest() {}
    
    @Test
    protected void protectedTest() {}
    
    @Test
    void packagePrivateTest() {}  // 包私有（不加修饰符）
    
    // 不推荐的测试方法（有返回值）
    @Test
    int notRecommendedTest() {  // 虽然技术上可行，但不推荐
        return 42;
    }
    
    // 以下测试方法声明是无效的
    
    @Test
    private void privateTest() {}  // 编译错误：private方法不能是测试方法
    
    @Test
    abstract void abstractTest();  // 编译错误：abstract方法不能是测试方法
    
    @Test
    void testWithParameters(int param) {}  // 编译错误：测试方法不能有参数
}
```

## 2.4 测试执行顺序

### 2.4.1 默认执行顺序

JUnit 5默认按照确定但不可预测的顺序执行测试方法，这有助于避免测试间的依赖。

```java
import org.junit.jupiter.api.*;

public class ExecutionOrderDemo {
    
    @Test
    void firstTest() {
        System.out.println("执行第一个测试");
        assertTrue(true);
    }
    
    @Test
    void secondTest() {
        System.out.println("执行第二个测试");
        assertTrue(true);
    }
    
    @Test
    void thirdTest() {
        System.out.println("执行第三个测试");
        assertTrue(true);
    }
    
    // 注意：JUnit 5不保证测试方法按照代码中的顺序执行
}
```

### 2.4.2 控制执行顺序

可以通过`@TestMethodOrder`注解和`MethodOrderer`接口控制测试方法执行顺序。

```java
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation;
import org.junit.jupiter.api.Order;

@TestMethodOrder(OrderAnnotation.class)  // 使用@Order注解控制顺序
public class OrderedExecutionTest {
    
    @Test
    @Order(3)  // 第三个执行
    public void thirdTest() {
        System.out.println("第三个测试");
        assertEquals(5, 2 + 3);
    }
    
    @Test
    @Order(1)  // 第一个执行
    public void firstTest() {
        System.out.println("第一个测试");
        assertEquals(4, 2 + 2);
    }
    
    @Test
    @Order(2)  // 第二个执行
    public void secondTest() {
        System.out.println("第二个测试");
        assertEquals(6, 3 + 3);
    }
}

// 另一种控制顺序的方式：按照方法名排序
@TestMethodOrder(MethodOrderer.MethodName.class)
public class MethodNameOrderTest {
    
    @Test
    public void testA() {
        System.out.println("方法A");
    }
    
    @Test
    public void testB() {
        System.out.println("方法B");
    }
    
    @Test
    public void testC() {
        System.out.println("方法C");
    }
    
    // 按照字母顺序执行：testA, testB, testC
}

// 按照显示名称排序
@TestMethodOrder(MethodOrderer.DisplayName.class)
@DisplayName("按显示名称排序的测试")
public class DisplayNameOrderTest {
    
    @Test
    @DisplayName("C - 最后一个")
    public void testC() {}
    
    @Test
    @DisplayName("A - 第一个")
    public void testA() {}
    
    @Test
    @DisplayName("B - 中间")
    public void testB() {}
    
    // 按照DisplayName字母顺序执行：A, B, C
}
```

## 2.5 断言入门

### 2.5.1 基本断言方法

JUnit 5提供了丰富的断言方法，位于`org.junit.jupiter.api.Assertions`类中。

```java
import static org.junit.jupiter.api.Assertions.*;

public class AssertionBasicsTest {
    
    @Test
    public void equalityAssertions() {
        // 相等性断言
        assertEquals(4, 2 + 2, "2 + 2 应该等于 4");
        assertEquals("hello", "he" + "llo");
        
        // 对象相等性（调用equals方法）
        String str1 = new String("test");
        String str2 = new String("test");
        assertEquals(str1, str2, "两个内容相同的字符串应该相等");
    }
    
    @Test
    public void identityAssertions() {
        // 同一性断言（比较引用）
        String str1 = "test";
        String str2 = str1;
        assertSame(str1, str2, "两个引用应该指向同一个对象");
        
        String str3 = new String("test");
        assertNotSame(str1, str3, "两个引用不应该指向同一个对象");
    }
    
    @Test
    public void truthinessAssertions() {
        // 真值断言
        assertTrue(5 > 3, "5应该大于3");
        assertFalse(3 > 5, "3不应该大于5");
        
        // 空值断言
        String nullString = null;
        assertNull(nullString, "值应该为null");
        
        String notNullString = "not null";
        assertNotNull(notNullString, "值不应该为null");
    }
    
    @Test
    public void arrayAssertions() {
        // 数组断言
        int[] expected = {1, 2, 3};
        int[] actual = {1, 2, 3};
        assertArrayEquals(expected, actual, "数组内容应该相等");
        
        // 数组内容不同会导致断言失败
        // int[] different = {1, 2, 4};
        // assertArrayEquals(expected, different);  // 会失败
    }
    
    @Test
    public void iterableAssertions() {
        // 可迭代对象断言
        List<String> expected = Arrays.asList("a", "b", "c");
        List<String> actual = Arrays.asList("a", "b", "c");
        assertLinesMatch(expected, actual, "列表内容应该匹配");
    }
    
    @Test
    public void timeoutAssertions() {
        // 超时断言
        assertTimeout(Duration.ofSeconds(2), () -> {
            // 会在2秒内完成的代码
            Thread.sleep(1000);
            return "完成";
        }, "操作应该在2秒内完成");
        
        // 超时会立即返回，不会等待代码执行完成
        assertTimeoutPreemptively(Duration.ofMillis(500), () -> {
            // 如果超过500ms会立即中断
            return "完成";
        });
    }
    
    @Test
    public void exceptionAssertions() {
        // 异常断言
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            throw new IllegalArgumentException("无效参数");
        }, "应该抛出IllegalArgumentException");
        
        assertEquals("无效参数", exception.getMessage(), "异常消息应该匹配");
        
        // 也可以检查异常类型
        Throwable thrown = assertThrows(Exception.class, () -> {
            throw new RuntimeException("运行时异常");
        });
        
        assertTrue(thrown instanceof RuntimeException, "应该是RuntimeException类型");
    }
    
    @Test
    public void failAssertions() {
        // fail方法显式使测试失败
        if (false) {  // 根据实际条件判断
            fail("测试条件不满足，测试失败");
        }
    }
}
```

### 2.5.2 断言消息

断言方法通常可以接受一个消息参数，用于在断言失败时提供更详细的信息。

```java
import static org.junit.jupiter.api.Assertions.*;

public class AssertionMessagesTest {
    
    @Test
    public void testWithStaticMessages() {
        // 静态消息
        assertEquals(4, 2 + 3, "计算结果不正确");
    }
    
    @Test
    public void testWithDynamicMessages() {
        // 使用Lambda表达式的动态消息（只在失败时计算）
        int a = 2;
        int b = 3;
        int sum = a + b;
        assertEquals(6, sum, () -> String.format("%d + %d = %d，但期望是6", a, b, sum));
    }
    
    @Test
    public void testWithCustomMessage() {
        // 自定义格式化的消息
        String expected = "hello";
        String actual = "world";
        assertEquals(expected, actual, 
            String.format("期望值: '%s', 实际值: '%s'", expected, actual));
    }
}
```

## 2.6 实践示例

### 2.6.1 简单计算器测试

结合本章学到的注解和断言，为计算器类编写更完整的测试。

```java
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

@DisplayName("增强版计算器测试")
@TestMethodOrder(OrderAnnotation.class)
public class EnhancedCalculatorTest {
    
    private Calculator calculator;
    
    @BeforeAll
    static void setUpClass() {
        System.out.println("=== 计算器测试开始 ===");
    }
    
    @AfterAll
    static void tearDownClass() {
        System.out.println("=== 计算器测试结束 ===");
    }
    
    @BeforeEach
    void setUp() {
        calculator = new Calculator();
    }
    
    @AfterEach
    void tearDown() {
        System.out.println("测试完成，清理资源");
    }
    
    @Test
    @Order(1)
    @DisplayName("基础算术运算测试")
    public void basicArithmeticTests() {
        // 加法测试
        assertEquals(5, calculator.add(2, 3), "2 + 3 应该等于 5");
        assertEquals(-1, calculator.add(-2, 1), "-2 + 1 应该等于 -1");
        
        // 减法测试
        assertEquals(1, calculator.subtract(3, 2), "3 - 2 应该等于 1");
        assertEquals(-3, calculator.subtract(-2, 1), "-2 - 1 应该等于 -3");
        
        // 乘法测试
        assertEquals(6, calculator.multiply(2, 3), "2 * 3 应该等于 6");
        assertEquals(0, calculator.multiply(5, 0), "任何数乘以0应该等于 0");
    }
    
    @Test
    @Order(2)
    @DisplayName("除法运算测试")
    public void divisionTests() {
        // 正常除法测试
        assertEquals(2.5, calculator.divide(5, 2), 0.001, "5 / 2 约等于 2.5");
        assertEquals(-2.5, calculator.divide(-5, 2), 0.001, "-5 / 2 约等于 -2.5");
        
        // 除零异常测试
        Exception exception = assertThrows(IllegalArgumentException.class, 
            () -> calculator.divide(5, 0), "除零应该抛出异常");
        assertEquals("除数不能为0", exception.getMessage(), "异常消息应该正确");
    }
    
    @Test
    @Order(3)
    @DisplayName("高级运算测试")
    public void advancedOperationsTests() {
        // 幂运算测试
        assertEquals(8, calculator.power(2, 3), "2的3次方应该等于 8");
        assertEquals(1, calculator.power(10, 0), "任何数的0次方应该等于 1");
        
        // 平方根测试
        assertEquals(3, calculator.sqrt(9), 0.001, "9的平方根应该等于 3");
        assertEquals(0, calculator.sqrt(0), "0的平方根应该等于 0");
    }
    
    @Test
    @Order(4)
    @DisplayName("输入验证测试")
    public void inputValidationTests() {
        // 平方根负数测试
        Exception exception = assertThrows(IllegalArgumentException.class, 
            () -> calculator.sqrt(-4), "负数平方根应该抛出异常");
        assertEquals("不能计算负数的平方根", exception.getMessage(), 
            "异常消息应该正确");
    }
    
    @Test
    @RepeatedTest(3)
    @DisplayName("重复测试: 随机数运算")
    public void randomCalculationTest(RepetitionInfo repetitionInfo) {
        // 生成随机数进行测试
        int a = (int) (Math.random() * 10);
        int b = (int) (Math.random() * 10) + 1;  // 避免除零
        
        double result = calculator.divide(a, b);
        assertTrue(result >= 0 && result <= 10, 
            "结果应该在0到10之间: " + result);
        
        System.out.printf("第%d次重复: %d / %d = %.2f%n", 
            repetitionInfo.getCurrentRepetition(), a, b, result);
    }
}
```

## 2.7 小结

本章深入讲解了JUnit框架的基础概念和核心注解，主要内容包括：

1. **JUnit 5架构**：Platform、Jupiter、Vintage三个子项目的分工
2. **核心注解**：@Test、@DisplayName、@BeforeEach、@AfterEach、@BeforeAll、@AfterAll等
3. **测试控制**：@Disabled、@Tag、@RepeatedTest等控制测试执行的方法
4. **执行顺序**：如何控制测试方法的执行顺序
5. **断言基础**：基本断言方法的使用和消息定制

掌握这些基础概念和注解是编写高质量单元测试的关键。在下一章中，我们将深入学习JUnit的断言与验证机制，探索更丰富的测试验证技巧。

## 2.8 实践练习

### 练习1：注解使用
1. 创建一个测试类，使用本章学到的所有生命周期注解
2. 在每个注解对应的方法中打印日志，观察执行顺序
3. 尝试不同的测试类和方法声明方式

### 练习2：断言练习
1. 为字符串处理类编写测试
2. 使用不同的断言方法验证各种情况
3. 为断言添加有意义的消息

### 练习3：测试控制
1. 使用@Tag注解标记不同类型的测试
2. 创建重复测试并观察执行效果
3. 控制测试方法的执行顺序

通过这些练习，您将巩固对JUnit核心概念和注解的理解，为后续学习打下坚实基础。