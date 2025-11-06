Feature: 用户登录功能
  作为一个系统用户
  我希望能够登录系统
  以便访问系统功能

  Scenario: 成功登录
    Given 我有一个登录服务
    And 用户 "admin" 存在且密码为 "admin123"
    When 我使用用户名 "admin" 和密码 "admin123" 登录
    Then 我应该能够成功登录
    And 我应该看到 "登录成功" 的消息

  Scenario: 用户名不存在
    Given 我有一个登录服务
    When 我使用用户名 "nonexistent" 和密码 "password" 登录
    Then 我应该无法登录
    And 我应该看到 "用户不存在" 的消息

  Scenario: 密码错误
    Given 我有一个登录服务
    And 用户 "admin" 存在且密码为 "admin123"
    When 我使用用户名 "admin" 和密码 "wrongpassword" 登录
    Then 我应该无法登录
    And 我应该看到 "密码错误" 的消息

  Scenario: 账户被禁用
    Given 我有一个登录服务
    And 用户 "admin" 存在且密码为 "admin123"
    And 用户 "admin" 已被禁用
    When 我使用用户名 "admin" 和密码 "admin123" 登录
    Then 我应该无法登录
    And 我应该看到 "账户已被禁用" 的消息

  Scenario Outline: 多种登录情况测试
    Given 我有一个登录服务
    And 用户 "{username}" 存在且密码为 "{password}"
    When 我使用用户名 "{username}" 和密码 "{loginPassword}" 登录
    Then 我应该{success}登录
    And 我应该看到 "{message}" 的消息

    Examples:
      | username | password   | loginPassword | success | message         |
      | admin   | admin123   | admin123      | 能够    | 登录成功        |
      | user    | user123    | user123       | 能够    | 登录成功        |
      | admin   | admin123   | wrongpassword | 无法    | 密码错误        |
      | test    | test123    | test123       | 能够    | 登录成功        |
      | test    | test123    | wrong         | 无法    | 密码错误        |