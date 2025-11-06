# 第4章：数据驱动测试 - 代码示例

## 目录结构

```
chapter4/
├── README.md                           # 本文件
├── src/
│   ├── main/
│   │   └── java/
│   │       └── com/
│   │           └── example/
│   │               └── cucumber/
│   │                   ├── model/      # 领域模型
│   │                   │   ├── User.java
│   │                   │   ├── Product.java
│   │                   │   └── Order.java
│   │                   ├── service/    # 服务层
│   │                   │   ├── UserService.java
│   │                   │   ├── ProductService.java
│   │                   │   └── OrderService.java
│   │                   └── transformer/ # 参数转换器
│   │                       ├── UserParameterTransformer.java
│   │                       ├── ProductParameterTransformer.java
│   │                       └── OrderParameterTransformer.java
│   └── test/
│       ├── java/
│       │   └── com/
│       │       └── example/
│       │           └── cucumber/
│       │               ├── stepdefinitions/  # 步骤定义
│       │               │   ├── UserSteps.java
│       │               │   ├── ProductSteps.java
│       │               │   └── OrderSteps.java
│       │               ├── config/            # 测试配置
│       │               │   └── TestConfig.java
│       │               └── runners/           # 测试运行器
│       │                   └── CucumberTestRunner.java
│       └── resources/
│           └── features/
│               ├── user-management/          # 用户管理特性
│               │   ├── user-registration.feature
│               │   ├── user-login.feature
│               │   └── user-batch-operations.feature
│               ├── product-search/           # 产品搜索特性
│               │   ├── basic-search.feature
│               │   ├── advanced-search.feature
│               │   └── filter-combinations.feature
│               └── order-management/         # 订单管理特性
│                   ├── order-creation.feature
│                   ├── order-update.feature
│                   └── order-filter.feature
└── pom.xml                              # Maven配置文件
```

## 代码示例说明

### 1. 领域模型 (model)

- **User.java**: 用户实体模型，包含用户基本信息和状态
- **Product.java**: 产品实体模型，包含产品信息和库存
- **Order.java**: 订单实体模型，包含订单详情和状态

### 2. 服务层 (service)

- **UserService.java**: 用户服务，实现用户注册、登录、查询等功能
- **ProductService.java**: 产品服务，实现产品搜索、筛选等功能
- **OrderService.java**: 订单服务，实现订单创建、更新、查询等功能

### 3. 参数转换器 (transformer)

- **UserParameterTransformer.java**: 用户相关参数转换器，处理用户名、邮箱、密码等
- **ProductParameterTransformer.java**: 产品相关参数转换器，处理价格、分类、库存等
- **OrderParameterTransformer.java**: 订单相关参数转换器，处理订单ID、状态、金额等

### 4. 步骤定义 (stepdefinitions)

- **UserSteps.java**: 用户功能步骤定义，实现用户注册、登录、批量操作等场景
- **ProductSteps.java**: 产品功能步骤定义，实现产品搜索、筛选、排序等场景
- **OrderSteps.java**: 订单功能步骤定义，实现订单创建、更新、查询等场景

### 5. 特性文件 (features)

- **user-management/**: 用户管理相关特性文件
  - user-registration.feature: 用户注册功能测试
  - user-login.feature: 用户登录功能测试
  - user-batch-operations.feature: 用户批量操作测试
- **product-search/**: 产品搜索相关特性文件
  - basic-search.feature: 基本搜索功能测试
  - advanced-search.feature: 高级搜索功能测试
  - filter-combinations.feature: 筛选组合测试
- **order-management/**: 订单管理相关特性文件
  - order-creation.feature: 订单创建功能测试
  - order-update.feature: 订单更新功能测试
  - order-filter.feature: 订单筛选功能测试

## 如何运行测试

### 前提条件

- JDK 8或更高版本
- Maven 3.6或更高版本

### 运行所有测试

```bash
mvn clean test
```

### 运行特定特性文件

```bash
mvn test -Dcucumber.options="--features src/test/resources/features/user-management/user-registration.feature"
```

### 运行特定标签的测试

```bash
mvn test -Dcucumber.options="--tags @smoke"
```

## 测试报告

测试执行后，可以在以下位置找到测试报告：

- HTML报告: `target/cucumber-reports/cucumber.html`
- JSON报告: `target/cucumber-reports/cucumber.json`
- JUnit报告: `target/surefire-reports`

## 扩展练习

1. 添加新的参数转换器，处理更复杂的数据类型
2. 创建新的特性文件，测试更多的业务场景
3. 实现自定义DataTable转换器，处理复杂的数据结构
4. 集成数据库，实现持久化测试
5. 添加性能测试，验证系统在不同数据量下的表现

## 注意事项

- 确保所有依赖项已正确配置
- 测试数据应该独立，避免测试之间的相互影响
- 使用有意义的测试数据，提高测试的可读性
- 遵循最佳实践，保持代码的简洁和可维护性