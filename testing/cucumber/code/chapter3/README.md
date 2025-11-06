# 第3章：Step Definitions实现 - 代码示例

本章包含Step Definitions实现的完整代码示例，展示了如何编写高质量的步骤定义代码。

## 目录结构

```
chapter3/
├── src/
│   ├── main/
│   │   └── java/
│   │       └── com/example/gherkin/
│   │           ├── model/
│   │           │   ├── User.java
│   │           │   ├── Product.java
│   │           │   ├── Order.java
│   │           │   ├── Cart.java
│   │           │   └── Payment.java
│   │           ├── service/
│   │           │   ├── UserService.java
│   │           │   ├── ProductService.java
│   │           │   ├── OrderService.java
│   │           │   ├── CartService.java
│   │           │   └── PaymentService.java
│   │           └── util/
│   │               ├── DateUtils.java
│   │               ├── MoneyConverter.java
│   │               └── TestDataFactory.java
│   └── test/
│       ├── java/
│       │   └── com/example/gherkin/
│       │       ├── stepdefinitions/
│       │       │   ├── UserSteps.java
│       │       │   ├── ProductSteps.java
│       │       │   ├── OrderSteps.java
│       │       │   ├── CartSteps.java
│       │       │   ├── PaymentSteps.java
│       │       │   └── ParameterConverters.java
│       │       ├── hooks/
│       │       │   ├── DatabaseHooks.java
│       │       │   └── ScreenshotHooks.java
│       │       ├── config/
│       │       │   ├── TestConfig.java
│       │       │   └── CucumberConfig.java
│       │       ├── runners/
│       │       │   ├── CucumberTestRunner.java
│       │       │   └── PerformanceTestRunner.java
│       │       └── context/
│       │           └── TestContext.java
│       └── resources/
│           └── features/
│               ├── user-management/
│               │   ├── user-registration.feature
│               │   └── user-login.feature
│               ├── product-management/
│               │   ├── product-browsing.feature
│               │   └── product-search.feature
│               ├── shopping-cart/
│               │   ├── cart-management.feature
│               │   └── checkout.feature
│               ├── order-management/
│               │   ├── order-creation.feature
│               │   └── order-payment.feature
│               └── performance/
│                   └── bulk-operations.feature
└── README.md
```

## 代码示例说明

### 模型类 (Model Classes)

- `User.java`: 用户实体模型
- `Product.java`: 产品实体模型
- `Order.java`: 订单实体模型
- `Cart.java`: 购物车实体模型
- `Payment.java`: 支付实体模型

### 服务类 (Service Classes)

- `UserService.java`: 用户业务逻辑服务
- `ProductService.java`: 产品业务逻辑服务
- `OrderService.java`: 订单业务逻辑服务
- `CartService.java`: 购物车业务逻辑服务
- `PaymentService.java`: 支付业务逻辑服务

### 步骤定义类 (Step Definition Classes)

- `UserSteps.java`: 用户相关功能的步骤定义
- `ProductSteps.java`: 产品相关功能的步骤定义
- `OrderSteps.java`: 订单相关功能的步骤定义
- `CartSteps.java`: 购物车相关功能的步骤定义
- `PaymentSteps.java`: 支付相关功能的步骤定义
- `ParameterConverters.java`: 自定义参数转换器

### 钩子类 (Hook Classes)

- `DatabaseHooks.java`: 数据库操作钩子
- `ScreenshotHooks.java`: 截图钩子

### 配置类 (Configuration Classes)

- `TestConfig.java`: 测试配置
- `CucumberConfig.java`: Cucumber配置

### 运行器类 (Runner Classes)

- `CucumberTestRunner.java`: 标准Cucumber测试运行器
- `PerformanceTestRunner.java`: 性能测试运行器

### 上下文类 (Context Classes)

- `TestContext.java`: 测试上下文，用于共享状态

### 特性文件 (Feature Files)

- 用户管理功能特性文件
- 产品管理功能特性文件
- 购物车功能特性文件
- 订单管理功能特性文件
- 性能测试特性文件

## 运行测试

### 运行所有测试

```bash
mvn test
```

### 运行特定特性

```bash
mvn test -Dcucumber.options="--tags @user-management"
mvn test -Dcucumber.options="--tags @product-management"
mvn test -Dcucumber.options="--tags @shopping-cart"
mvn test -Dcucumber.options="--tags @order-management"
mvn test -Dcucumber.options="--tags @performance"
```

### 运行特定场景

```bash
mvn test -Dcucumber.options="--name '用户使用有效凭证登录'"
```

## 生成报告

### HTML报告

```bash
mvn test -Dcucumber.options="--plugin html:target/cucumber-html-report"
```

### JSON报告

```bash
mvn test -Dcucumber.options="--plugin json:target/cucumber.json"
```

### JUnit报告

```bash
mvn test -Dcucumber.options="--plugin junit:target/cucumber-junit-report.xml"
```

## 扩展练习

1. 添加新的功能模块（如评论、评分）
2. 实现更多的参数转换器
3. 添加更多的性能测试场景
4. 实现并行测试执行
5. 集成测试覆盖率报告

## 注意事项

1. 确保所有依赖项已正确配置
2. 数据库连接配置正确
3. 测试数据准备充分
4. 测试环境隔离
5. 清理测试数据