# 第2章：Gherkin语法详解 - 代码示例

本章包含Gherkin语法详解相关的代码示例，展示如何使用Gherkin编写清晰、可维护的验收测试。

## 项目结构

```
chapter2/
├── pom.xml                                    # Maven项目配置
├── README.md                                  # 本章说明文档
└── src/
    ├── main/
    │   └── java/
    │       └── com/
    │           └── example/
    │               └── gherkin/
    │                   ├── controller/
    │                   │   └── UserController.java     # 用户控制器
    │                   ├── model/
    │                   │   └── User.java               # 用户实体类
    │                   └── service/
    │                       └── UserService.java        # 用户服务类
    └── test/
        ├── java/
        │   └── com/
        │       └── example/
        │           └── gherkin/
        │               ├── CucumberSpringIntegrationTest.java  # Cucumber与Spring集成基类
        │               ├── config/
        │               │   └── TestConfig.java               # 测试配置类
        │               ├── runners/
        │               │   └── CucumberTestRunner.java       # Cucumber测试运行器
        │               └── stepdefinitions/
        │                   ├── UserLoginSteps.java           # 用户登录步骤定义
        │                   └── UserRegistrationSteps.java    # 用户注册步骤定义
        └── resources/
            └── features/
                ├── user-login.feature             # 用户登录特性文件
                └── user-registration.feature      # 用户注册特性文件
```

## 功能特性

### 1. 用户认证系统

实现了一个完整的用户认证系统，包括：

- 用户注册
- 用户登录
- 邮箱验证
- 密码重置
- 账户启用/禁用

### 2. Gherkin特性文件

包含两个主要的特性文件：

- **user-registration.feature**: 用户注册功能的测试场景
- **user-login.feature**: 用户登录功能的测试场景

这些特性文件展示了Gherkin的各种语法特性：

- Feature（功能）
- Scenario（场景）
- Scenario Outline（场景大纲）
- Background（背景）
- Data Tables（数据表）
- Tags（标签）
- Doc Strings（文档字符串）

### 3. 步骤定义实现

提供了完整的步骤定义实现：

- **UserRegistrationSteps**: 用户注册功能的步骤定义
- **UserLoginSteps**: 用户登录功能的步骤定义

这些步骤定义展示了如何将Gherkin场景转换为可执行的测试代码。

## 运行测试

### 前提条件

- JDK 8或更高版本
- Maven 3.6或更高版本

### 运行所有测试

```bash
mvn clean test
```

### 运行特定特性文件

```bash
mvn test -Dcucumber.options="src/test/resources/features/user-registration.feature"
```

### 运行特定标签的测试

```bash
mvn test -Dcucumber.options="--tags @user-registration"
```

## 测试报告

测试执行后，可以在以下位置查看测试报告：

- HTML报告: `target/cucumber-reports/report.html`
- JSON报告: `target/cucumber-reports/report.json`
- JUnit报告: `target/cucumber-reports/report.xml`

## Gherkin语法特性展示

### 1. 基本语法

```gherkin
Feature: 用户注册管理
  作为系统用户
  我希望能够注册新账户
  以便使用系统的各项功能

  Scenario: 成功注册新用户
    When 我尝试使用以下信息注册用户:
      | username | email              | password     | firstName | lastName |
      | john_doe | john@example.com   | P@ssw0rd123  | John      | Doe     |
    Then 注册应该成功
    And 我应该收到验证令牌
```

### 2. 场景大纲

```gherkin
Scenario Outline: 使用无效邮箱格式注册
    When 我尝试使用邮箱"<email>"注册用户
    Then 注册应该失败
    And 我应该收到错误消息"Invalid email format"

    例子:
      | email              |
      | invalid-email      |
      | @example.com       |
      | user@              |
```

### 3. 背景

```gherkin
Background:
  Given 系统已经初始化用户服务

  Scenario: 成功登录
    Given 用户"john_doe"已经存在
    And 用户"john_doe"已经验证邮箱
    When 我使用用户名"john_doe"和密码"P@ssw0rd123"登录
    Then 登录应该成功
```

### 4. 标签

```gherkin
@user-registration @success
Scenario: 成功注册新用户
  ...

@user-login @wrong-password
Scenario: 使用错误密码登录
  ...
```

## 扩展练习

1. 添加更多用户管理功能的测试场景，如：
   - 密码重置
   - 用户信息更新
   - 账户启用/禁用

2. 实现更复杂的业务场景，如：
   - 用户角色管理
   - 权限验证
   - 用户会话管理

3. 尝试使用不同的Gherkin语法特性，如：
   - 嵌套数据表
   - 文档字符串
   - 更复杂的标签组合

## 相关文档

- [Gherkin语言基础](../../chapter2/2.1-gherkin-language-basics.md)
- [Gherkin高级特性](../../chapter2/2.2-gherkin-advanced-features.md)
- [Gherkin最佳实践](../../chapter2/2.3-gherkin-best-practices-design-patterns.md)
- [Gherkin实战案例](../../chapter2/2.5-gherkin-practical-examples-code.md)