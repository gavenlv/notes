# 第2章：JUnit基础概念与核心注解 - 代码示例

本章包含JUnit核心注解和基础概念的完整代码示例，包括注解使用、测试生命周期、执行控制和断言方法。

## 项目结构

```
chapter2/
├── pom.xml                              # Maven配置文件
└── src/
    ├── main/
    │   └── java/
    │       └── com/example/
    │           ├── calculator/           # 计算器相关类
    │           │   └── Calculator.java
    │           └── utils/                # 工具类
    │               └── StringHelper.java
    └── test/
        └── java/
            └── com/example/
                ├── calculator/          # 计算器测试类
                │   ├── BasicAnnotationTest.java
                │   ├── CalculatorDisplayNameTest.java
                │   ├── EnhancedCalculatorTest.java
                │   ├── LifecycleTest.java
                │   └── AllLifecycleTest.java
                ├── annotation/           # 注解示例测试
                │   ├── DisabledTest.java
                │   ├── TaggedTest.java
                │   ├── RepeatedTestDemo.java
                │   └── TestMethodVariations.java
                ├── execution/            # 执行顺序测试
                │   ├── ExecutionOrderDemo.java
                │   ├── OrderedExecutionTest.java
                │   ├── MethodNameOrderTest.java
                │   └── DisplayNameOrderTest.java
                ├── assertion/            # 断言示例
                │   ├── AssertionBasicsTest.java
                │   ├── AssertionMessagesTest.java
                │   └── AdvancedAssertionsTest.java
                └── utils/                # 工具类测试
                    └── StringHelperTest.java
```

## 运行说明

### 使用Maven
```bash
# 编译项目
mvn compile

# 运行所有测试
mvn test

# 运行特定标签的测试
mvn test -Dgroups="unit"

# 运行特定测试类
mvn test -Dtest=EnhancedCalculatorTest
```

### 在IDE中运行
1. 导入项目到IDE
2. 右键点击测试类或测试方法
3. 选择"Run"运行测试
4. 查看测试结果和控制台输出

## 核心示例说明

### 1. Calculator.java
增强版的计算器类，包含基本运算和高级运算方法，用于演示各种测试场景。

### 2. 注解示例
- BasicAnnotationTest.java: 展示基本的@Test注解使用
- DisabledTest.java: 展示@Disabled的使用
- TaggedTest.java: 展示@Tag注解的使用
- RepeatedTestDemo.java: 展示@RepeatedTest的使用

### 3. 生命周期示例
- LifecycleTest.java: 展示@BeforeEach和@AfterEach的使用
- AllLifecycleTest.java: 展示@BeforeAll和@AfterAll的使用

### 4. 执行顺序示例
- OrderedExecutionTest.java: 展示使用@Order控制执行顺序
- MethodNameOrderTest.java: 展示按方法名排序
- DisplayNameOrderTest.java: 展示按显示名称排序

### 5. 断言示例
- AssertionBasicsTest.java: 展示各种基本断言方法
- AssertionMessagesTest.java: 展示断言消息的使用
- AdvancedAssertionsTest.java: 展示高级断言技巧

## 学习要点

1. 掌握JUnit 5的核心注解及其使用场景
2. 理解测试生命周期和执行流程
3. 学会控制测试的执行和跳过
4. 熟练使用各种断言方法
5. 了解测试结果的可视化和解读

## 扩展练习

1. 创建自己的测试类，实践不同的注解
2. 尝试组合使用多个注解
3. 使用不同的断言方法验证测试结果
4. 探索IDE中的测试运行和调试功能

## 注意事项

- 测试方法不能是private
- @BeforeAll和@AfterAll方法必须是static的（除非使用@TestInstance）
- 断言消息应该清晰明了
- 避免测试方法之间的依赖