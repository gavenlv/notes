# 第3章：JUnit断言与验证机制

## 3.1 断言基础回顾

### 3.1.1 断言的作用与原理

断言是测试框架的核心机制，用于验证实际结果与期望结果是否一致。如果断言失败，测试将立即终止并报告失败。

```java
// 断言的基本原理
public class AssertionPrinciple {
    
    // 简化的assertEquals实现原理
    public static void assertEquals(Object expected, Object actual) {
        if (!expected.equals(actual)) {
            throw new AssertionFailedError(
                String.format("期望: %s, 实际: %s", expected, actual));
        }
    }
}
```

### 3.1.2 断言失败时的行为

当断言失败时：

1. 抛出`AssertionFailedError`异常
2. 记录失败消息和位置信息
3. 终止当前测试方法
4. 报告测试失败状态

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class AssertionFailureExample {
    
    @Test
    public void demonstrationOfFailure() {
        // 这个断言会失败，并展示详细的错误信息
        assertEquals("hello", "world", "字符串比较失败");
        // 这行代码不会执行，因为前面的断言已经失败
        System.out.println("这行不会被执行");
    }
}
```

## 3.2 基本断言方法详解

### 3.2.1 相等性断言

#### assertEquals

验证两个对象是否相等（调用equals方法）。

```java
import static org.junit.jupiter.api.Assertions.*;

public class EqualityAssertionsTest {
    
    @Test
    public void assertEqualsBasics() {
        // 基本类型相等性断言
        assertEquals(4, 2 + 2);
        assertEquals(4.5, 4.5);
        assertEquals('a', 'a');
        assertEquals(true, 5 > 3);
        
        // 对象相等性断言
        String str1 = "hello";
        String str2 = "hello";
        assertEquals(str1, str2, "两个内容相同的字符串应该相等");
        
        // 数组相等性断言
        int[] expected = {1, 2, 3};
        int[] actual = {1, 2, 3};
        assertArrayEquals(expected, actual, "数组内容应该相等");
        
        // 浮点数相等性断言（允许误差）
        assertEquals(Math.PI, 3.14159, 0.001, "π的近似值");
    }
    
    @Test
    public void assertEqualsWithMessage() {
        String expected = "JUnit 5";
        String actual = "JUnit 4";
        
        // 带有错误消息的断言
        assertEquals(expected, actual, 
            String.format("版本不匹配，期望: %s, 实际: %s", expected, actual));
            
        // 使用Lambda消息（更高效，只在失败时计算）
        assertEquals(expected, actual, 
            () -> String.format("期望版本: %s, 实际版本: %s", expected, actual));
    }
}
```

#### assertNotEquals

验证两个对象不相等。

```java
@Test
public void assertNotEqualsExample() {
    // 基本类型不相等断言
    assertNotEquals(4, 5);
    
    // 对象不相等断言
    String str1 = new String("hello");
    String str2 = new String("world");
    assertNotEquals(str1, str2, "内容不同的字符串不应该相等");
    
    // 注意：这里会比较引用，而不是内容
    String str3 = new String("hello");
    String str4 = new String("hello");
    assertNotSame(str3, str4, "两个不同对象不应该指向同一引用");
}
```

### 3.2.2 同一性断言

#### assertSame 和 assertNotSame

验证两个引用是否指向同一个对象。

```java
public class IdentityAssertionsTest {
    
    @Test
    public void identityAssertions() {
        // 同一性测试
        String str1 = "test";
        String str2 = "test";  // 字符串常量池，指向同一对象
        assertSame(str1, str2, "字符串常量应该指向同一对象");
        
        String str3 = new String("test");
        String str4 = new String("test");
        assertNotSame(str3, str4, "new创建的对象不应该指向同一引用");
        
        // 相等性vs同一性
        assertEquals(str3, str4, "内容应该相等");
        assertNotSame(str3, str4, "引用不应该相同");
    }
}
```

### 3.2.3 真值断言

#### assertTrue, assertFalse

验证布尔表达式的真假。

```java
public class TruthinessAssertionsTest {
    
    @Test
    public void booleanAssertions() {
        // 简单布尔表达式
        assertTrue(5 > 3, "5应该大于3");
        assertFalse(3 > 5, "3不应该大于5");
        
        // 复杂布尔表达式
        String str = "JUnit测试";
        assertTrue(str != null && str.contains("JUnit"), 
            "字符串不应该为空且应该包含'JUnit'");
        
        // 使用Lambda消息
        assertTrue(() -> {
            int result = 2 + 2;
            return result == 4;
        }, "2 + 2 应该等于 4");
        
        // 测试对象状态的布尔值
        List<String> list = Arrays.asList("a", "b", "c");
        assertTrue(list.contains("b"), "列表应该包含'b'");
        assertFalse(list.isEmpty(), "列表不应该为空");
    }
}
```

### 3.2.4 空值断言

#### assertNull, assertNotNull

验证对象是否为null。

```java
public class NullnessAssertionsTest {
    
    @Test
    public void nullAssertions() {
        // 基本null测试
        String nullString = null;
        assertNull(nullString, "字符串应该为null");
        
        String notNullString = "hello";
        assertNotNull(notNullString, "字符串不应该为null");
        
        // 方法返回值测试
        String result = getOptionalString(false);
        assertNull(result, "条件为false时应该返回null");
        
        result = getOptionalString(true);
        assertNotNull(result, "条件为true时应该返回非null值");
    }
    
    // 辅助方法，根据条件返回字符串或null
    private String getOptionalString(boolean condition) {
        return condition ? "optional value" : null;
    }
}
```

## 3.3 高级断言方法

### 3.3.1 集合断言

#### assertArrayEquals, assertIterableEquals, assertLinesMatch

验证集合内容。

```java
import java.util.*;

public class CollectionAssertionsTest {
    
    @Test
    public void arrayAssertions() {
        // 基本类型数组
        int[] expected = {1, 2, 3, 4, 5};
        int[] actual = {1, 2, 3, 4, 5};
        assertArrayEquals(expected, actual, "数组内容应该相等");
        
        // 对象数组
        String[] expectedStr = {"a", "b", "c"};
        String[] actualStr = {"a", "b", "c"};
        assertArrayEquals(expectedStr, actualStr, "字符串数组内容应该相等");
        
        // 多维数组
        int[][] expected2D = {{1, 2}, {3, 4}};
        int[][] actual2D = {{1, 2}, {3, 4}};
        assertArrayEquals(expected2D, actual2D, "二维数组内容应该相等");
    }
    
    @Test
    public void iterableAssertions() {
        List<String> expected = Arrays.asList("a", "b", "c");
        List<String> actual = Arrays.asList("a", "b", "c");
        assertIterableEquals(expected, actual, "可迭代对象内容应该相等");
        
        // 不同类型的可迭代对象
        Set<String> set = new HashSet<>(Arrays.asList("c", "b", "a"));
        List<String> list = Arrays.asList("a", "b", "c");
        assertIterableEquals(list, set, "顺序无关的可迭代对象内容应该相等");
    }
    
    @Test
    public void linesMatchAssertions() {
        List<String> expected = Arrays.asList("line 1", "line 2", "line 3");
        List<String> actual = Arrays.asList("line 1", "line 2", "line 3");
        assertLinesMatch(expected, actual, "行列表应该匹配");
        
        // 使用通配符
        List<String> expectedPattern = Arrays.asList("line *", "line 2", ">> regular expression <<");
        List<String> actualLines = Arrays.asList("line 1", "line 2", "something else");
        assertLinesMatch(expectedPattern, actualLines, "使用通配符的行匹配");
    }
}
```

### 3.3.2 异常断言

#### assertThrows, assertDoesNotThrow

验证异常的抛出。

```java
public class ExceptionAssertionsTest {
    
    @Test
    public void exceptionAssertions() {
        // 测试特定异常的抛出
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            throw new IllegalArgumentException("无效参数");
        });
        
        assertEquals("无效参数", exception.getMessage());
        
        // 测试异常类型和消息
        Throwable thrown = assertThrows(RuntimeException.class, () -> {
            throw new NullPointerException("空指针异常");
        });
        
        assertTrue(thrown instanceof NullPointerException);
        assertEquals("空指针异常", thrown.getMessage());
    }
    
    @Test
    public void exceptionWithAssertionsInside() {
        // 在异常测试内部使用其他断言
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            validateAge(-5);
        });
        
        assertEquals("年龄不能为负数", exception.getMessage());
        assertNotNull(exception.getCause(), "异常原因不应该为null");
    }
    
    @Test
    public void noExceptionThrown() {
        // 测试方法不抛出异常
        assertDoesNotThrow(() -> {
            validateAge(25);  // 合法年龄，不抛出异常
        }, "合法年龄不应该抛出异常");
        
        // 返回值测试
        String result = assertDoesNotThrow(() -> {
            return getValueOrThrow(true);
        }, "当条件为true时不应该抛出异常");
        
        assertEquals("valid value", result, "返回值应该正确");
    }
    
    // 辅助方法
    private void validateAge(int age) {
        if (age < 0) {
            throw new IllegalArgumentException("年龄不能为负数");
        }
    }
    
    private String getValueOrThrow(boolean condition) {
        if (!condition) {
            throw new IllegalStateException("条件不满足");
        }
        return "valid value";
    }
}
```

### 3.3.3 超时断言

#### assertTimeout, assertTimeoutPreemptively

验证执行时间。

```java
import java.time.Duration;
import java.util.concurrent.*;

public class TimeoutAssertionsTest {
    
    @Test
    public void timeoutAssertions() {
        // 基本超时测试 - 等待代码执行完成
        assertTimeout(Duration.ofSeconds(2), () -> {
            // 需要在2秒内完成的操作
            Thread.sleep(1000);
            return "完成";
        });
        
        // 测试返回值
        String result = assertTimeout(Duration.ofMillis(500), () -> {
            Thread.sleep(200);
            return "操作结果";
        }, "操作应该在500ms内完成");
        
        assertEquals("操作结果", result, "返回值应该正确");
    }
    
    @Test
    public void preemptiveTimeoutAssertions() {
        // 抢占式超时 - 超时后立即中断
        assertTimeoutPreemptively(Duration.ofMillis(500), () -> {
            // 如果执行超过500ms会被中断
            Thread.sleep(1000);  // 这会被中断
            return "不应该到达这里";
        });
    }
    
    @Test
    public void timeoutWithExecutable() {
        // 使用Executable接口
        assertTimeout(Duration.ofSeconds(1), (Executable) () -> {
            // 耗时操作
            Thread.sleep(500);
        });
    }
}
```

## 3.4 第三方断言库

### 3.4.1 AssertJ介绍

AssertJ是一个流畅的断言库，提供了更丰富的断言方法和更易读的语法。

```java
import static org.assertj.core.api.Assertions.*;

public class AssertJDemo {
    
    @Test
    public void assertJBasics() {
        // 流畅的断言语法
        String name = "JUnit";
        assertThat(name).isEqualTo("JUnit")
                       .startsWith("J")
                       .endsWith("t")
                       .hasSize(5)
                       .contains("Uni");
        
        // 数组和集合断言
        List<String> languages = Arrays.asList("Java", "Python", "JavaScript");
        assertThat(languages).hasSize(3)
                            .contains("Java")
                            .doesNotContain("C++")
                            .allMatch(s -> s.length() > 2);
        
        // 对象断言
        Person person = new Person("张三", 25);
        assertThat(person).extracting(Person::getName, Person::getAge)
                         .containsExactly("张三", 25);
    }
    
    @Test
    public void assertJExceptions() {
        // 异常断言
        assertThatThrownBy(() -> {
            throw new IllegalArgumentException("无效参数");
        }).isInstanceOf(IllegalArgumentException.class)
          .hasMessage("无效参数")
          .hasNoCause();
    }
    
    // 辅助类
    static class Person {
        private String name;
        private int age;
        
        public Person(String name, int age) {
            this.name = name;
            this.age = age;
        }
        
        public String getName() { return name; }
        public int getAge() { return age; }
    }
}
```

### 3.4.2 Hamcrest匹配器

Hamcrest提供匹配器风格的断言语法。

```java
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;

public class HamcrestDemo {
    
    @Test
    public void hamcrestBasics() {
        // 基本匹配器
        assertThat(2 + 2, equalTo(4));
        assertThat("hello", startsWith("h"));
        assertThat(Arrays.asList("a", "b", "c"), hasItem("b"));
        
        // 组合匹配器
        String text = "JUnit 5测试框架";
        assertThat(text, allOf(
            startsWith("JUnit"),
            containsString("测试"),
            endsWith("框架")
        ));
        
        // 任意匹配器
        assertThat("hello world", anyOf(
            containsString("java"),
            containsString("world")
        ));
    }
}
```

## 3.5 自定义断言

### 3.5.1 创建自定义断言方法

```java
import static org.junit.jupiter.api.Assertions.*;

public class CustomAssertions {
    
    /**
     * 验证密码强度
     */
    public static void assertPasswordStrength(String password, PasswordStrength expectedStrength) {
        PasswordStrength actualStrength = PasswordValidator.checkStrength(password);
        assertEquals(expectedStrength, actualStrength,
            String.format("密码'%s'强度应该是%s，但实际是%s", 
                password, expectedStrength, actualStrength));
    }
    
    /**
     * 验证邮箱格式
     */
    public static void assertValidEmail(String email) {
        assertTrue(EmailValidator.isValid(email),
            String.format("'%s'应该是有效的邮箱地址", email));
    }
    
    /**
     * 验证日期范围
     */
    public static void assertDateInRange(LocalDate date, LocalDate start, LocalDate end) {
        assertTrue((date.isEqual(start) || date.isAfter(start)) && 
                  (date.isEqual(end) || date.isBefore(end)),
            String.format("日期%s应该在%s和%s之间", date, start, end));
    }
    
    // 辅助类
    enum PasswordStrength { WEAK, MEDIUM, STRONG }
    
    static class PasswordValidator {
        static PasswordStrength checkStrength(String password) {
            if (password == null || password.length() < 6) {
                return PasswordStrength.WEAK;
            } else if (password.length() < 10) {
                return PasswordStrength.MEDIUM;
            } else {
                return PasswordStrength.STRONG;
            }
        }
    }
    
    static class EmailValidator {
        static boolean isValid(String email) {
            return email != null && email.matches("^[A-Za-z0-9+_.-]+@(.+)$");
        }
    }
}

// 使用自定义断言
public class CustomAssertionsTest {
    
    @Test
    public void testPasswordStrength() {
        CustomAssertions.assertPasswordStrength("123", PasswordStrength.WEAK);
        CustomAssertions.assertPasswordStrength("password", PasswordStrength.MEDIUM);
        CustomAssertions.assertPasswordStrength("strongPassword123", PasswordStrength.STRONG);
    }
    
    @Test
    public void testEmailValidation() {
        CustomAssertions.assertValidEmail("user@example.com");
        CustomAssertions.assertValidEmail("test.email+tag@domain.co.uk");
    }
    
    @Test
    public void testDateRange() {
        LocalDate date = LocalDate.of(2023, 6, 15);
        LocalDate start = LocalDate.of(2023, 1, 1);
        LocalDate end = LocalDate.of(2023, 12, 31);
        
        CustomAssertions.assertDateInRange(date, start, end);
    }
}
```

### 3.5.2 使用AssertJ创建自定义断言

```java
import org.assertj.core.api.AbstractAssert;

public class PersonAssert extends AbstractAssert<PersonAssert, Person> {
    
    protected PersonAssert(Person actual) {
        super(actual, PersonAssert.class);
    }
    
    public static PersonAssert assertThat(Person actual) {
        return new PersonAssert(actual);
    }
    
    public PersonAssert hasName(String expectedName) {
        isNotNull();
        if (!actual.getName().equals(expectedName)) {
            failWithMessage("期望姓名是<%s>，但实际是<%s>", expectedName, actual.getName());
        }
        return this;
    }
    
    public PersonAssert hasAge(int expectedAge) {
        isNotNull();
        if (actual.getAge() != expectedAge) {
            failWithMessage("期望年龄是<%s>，但实际是<%s>", expectedAge, actual.getAge());
        }
        return this;
    }
    
    public PersonAssert isAdult() {
        isNotNull();
        if (actual.getAge() < 18) {
            failWithMessage("期望<%s>是成年人，但年龄只有<%s>", actual.getName(), actual.getAge());
        }
        return this;
    }
}

// 使用自定义AssertJ断言
public class PersonAssertTest {
    
    @Test
    public void customAssertJTest() {
        Person person = new Person("张三", 25);
        
        PersonAssert.assertThat(person)
                  .hasName("张三")
                  .hasAge(25)
                  .isAdult();
    }
}
```

## 3.6 断言最佳实践

### 3.6.1 断言选择指南

| 场景 | 推荐断言 | 示例 |
|------|----------|------|
| 基本相等性 | assertEquals | assertEquals(5, result) |
| 对象引用比较 | assertSame/assertNotSame | assertSame(obj1, obj2) |
| 布尔条件 | assertTrue/falseError | assertTrue(condition) |
| 空值检查 | assertNull/assertNotNull | assertNull(value) |
| 集合内容 | assertArrayEquals | assertArrayEquals(expected, actual) |
| 异常验证 | assertThrows | assertThrows(Exception.class, () -> {...}) |
| 超时检查 | assertTimeout | assertTimeout(Duration.ofSeconds(1), () -> {...}) |
| 复杂条件 | 自定义断言或第三方库 | assertThat(list).hasSize(3) |

### 3.6.2 断言消息最佳实践

1. **描述性消息**：清楚说明期望值和实际值
2. **简洁明了**：避免冗长的消息
3. **使用Lambda**：对于复杂消息使用Lambda表达式
4. **国际化考虑**：考虑多语言环境

```java
// 好的断言消息示例
@Test
public void goodAssertionMessages() {
    // 描述性消息
    assertEquals(expectedValue, actualValue, 
        String.format("方法%应该返回%s，但实际返回%s", 
            methodName, expectedValue, actualValue));
    
    // 使用Lambda消息（更高效）
    assertEquals(expectedValue, actualValue, 
        () -> String.format("计算结果不正确，期望：%s，实际：%s", 
            expectedValue, actualValue));
}

// 不推荐的断言消息示例
@Test
public void badAssertionMessages() {
    // 太简单
    assertEquals(expected, actual, "不匹配");
    
    // 太冗长
    assertEquals(expected, actual, 
        "我们在执行testSomeMethod方法时，期望得到的结果是" + expected + 
        "，但实际得到的结果是" + actual + "，这表明我们的实现可能有问题，" +
        "需要进一步检查代码逻辑和算法实现，特别是数据转换和边界条件处理");
}
```

### 3.6.3 断言性能考虑

1. **优先快速失败的断言**
2. **避免复杂的断言消息计算**
3. **对重复的断言逻辑提取方法**

```java
@Test
public void assertionPerformance() {
    // 好的做法：快速失败的断言在前
    assertNotNull(result, "结果不应该为null");  // 快速失败
    assertEquals(expectedLength, result.length(), "结果长度不正确");
    
    // 避免不必要的计算
    assertEquals(expectedValue, actualValue, 
        () -> computeComplexErrorMessage());  // 使用Lambda延迟计算
    
    // 提取重复的断言逻辑
    assertValidUser(user);  // 封装常用断言
    assertValidUser(anotherUser);
}

private void assertValidUser(User user) {
    assertNotNull(user, "用户不应该为null");
    assertNotNull(user.getId(), "用户ID不应该为null");
    assertTrue(user.getName().length() > 0, "用户名不能为空");
}
```

## 3.7 小结

本章详细讲解了JUnit的断言与验证机制，主要内容包括：

1. **断言基础**：断言的作用、原理和失败行为
2. **基本断言方法**：assertEquals、assertNotEquals、assertSame等
3. **高级断言方法**：集合断言、异常断言、超时断言
4. **第三方断言库**：AssertJ和Hamcrest的使用
5. **自定义断言**：创建和使用自定义断言方法
6. **断言最佳实践**：选择合适的断言和编写有意义的消息

掌握断言机制是编写有效单元测试的关键。在下一章中，我们将学习JUnit的测试生命周期与钩子方法，深入了解测试的执行流程。

## 3.8 实践练习

### 练习1：基本断言
1. 为字符串工具类编写测试，使用各种相等性断言
2. 为集合处理类编写测试，使用集合断言
3. 为可能抛出异常的方法编写测试，使用异常断言

### 练习2：高级断言
1. 使用AssertJ重写现有测试，体验流畅的断言语法
2. 创建自定义断言方法，封装常用的验证逻辑
3. 为时间敏感的操作编写超时断言测试

### 练习3：断言优化
1. 检查现有测试的断言消息，改进使其更清晰
2. 优化断言的执行顺序，提高测试效率
3. 提取重复的断言逻辑到方法或自定义断言中

通过这些练习，您将掌握各种断言方法的使用，能够编写清晰、高效、易于维护的测试代码。