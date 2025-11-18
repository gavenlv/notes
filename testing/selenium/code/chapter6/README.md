# 第6章代码示例 - Selenium等待机制与异常处理

本目录包含第6章"Selenium等待机制与异常处理"的代码示例，涵盖以下内容：

## 代码示例说明

### 1. 等待机制示例
- **ImplicitWaitTest.java** - 演示隐式等待的使用
- **ExplicitWaitTest.java** - 演示显式等待的使用
- **FluentWaitTest.java** - 演示流畅等待的使用
- **CustomWaitConditions.java** - 自定义等待条件

### 2. 异常处理示例
- **ExceptionHandlingTest.java** - 演示各种异常的处理
- **RetryMechanismTest.java** - 演示重试机制
- **TimeoutHandlingTest.java** - 演示超时处理

### 3. 等待策略示例
- **WaitStrategiesTest.java** - 演示不同等待策略
- **PageLoadWaitTest.java** - 演示页面加载等待
- **ElementWaitTest.java** - 演示元素等待
- **AsyncOperationTest.java** - 演示异步操作等待

### 4. 实用工具类
- **WaitUtils.java** - 等待工具类
- **ExceptionUtils.java** - 异常处理工具类
- **RetryUtils.java** - 重试机制工具类

## 运行说明

1. 使用Maven运行测试：`mvn test`
2. 使用TestNG运行：`mvn test -DsuiteXmlFile=testng.xml`
3. 在IDE中直接运行测试类

## 环境要求

- Java 11+
- Maven 3.6+
- Chrome浏览器
- ChromeDriver（由WebDriverManager自动管理）

## 项目结构

```
src/test/java/com/example/selenium/tests/
├── ImplicitWaitTest.java          # 隐式等待示例
├── ExplicitWaitTest.java           # 显式等待示例
├── FluentWaitTest.java             # 流畅等待示例
├── CustomWaitConditions.java       # 自定义等待条件
├── ExceptionHandlingTest.java     # 异常处理示例
├── RetryMechanismTest.java         # 重试机制示例
├── TimeoutHandlingTest.java        # 超时处理示例
├── WaitStrategiesTest.java         # 等待策略示例
├── PageLoadWaitTest.java           # 页面加载等待
├── ElementWaitTest.java            # 元素等待
└── AsyncOperationTest.java         # 异步操作等待

src/main/java/com/example/selenium/utils/
├── WaitUtils.java                  # 等待工具类
├── ExceptionUtils.java             # 异常处理工具类
└── RetryUtils.java                 # 重试机制工具类

src/test/resources/
├── wait-test.html                   # 等待测试页面
└── async-test.html                  # 异步操作测试页面
```

## 设计原则

1. **避免混合使用** - 不要在同一测试中同时使用隐式等待和显式等待
2. **适当设置超时** - 根据实际需要设置合理的等待时间
3. **异常粒度** - 捕获特定异常而非通用异常
4. **重试策略** - 实现合理的重试策略，避免无限重试
5. **性能考虑** - 避免过长的等待时间影响测试性能

## 最佳实践

1. 优先使用显式等待而非隐式等待
2. 为特定场景创建自定义等待条件
3. 为不稳定测试实现合理的重试机制
4. 捕获并记录异常信息，便于调试
5. 在异常处理中提供有意义的错误信息
6. 使用流畅等待实现更复杂的等待逻辑