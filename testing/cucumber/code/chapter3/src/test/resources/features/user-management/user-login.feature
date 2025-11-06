@user-management @login
Feature: 用户登录功能
  作为系统用户
  我希望能够登录系统
  以便访问我的个人账户和系统功能

  Background:
    Given 用户 "testuser" 不存在

  @successful-login
  Scenario: 用户使用有效凭证登录
    Given 用户 "testuser" 存在，邮箱为 "test@example.com"，密码为 "Password123"
    When 用户使用用户名 "testuser" 和密码 "Password123" 登录
    Then 用户应该成功登录

  @wrong-password
  Scenario: 用户使用错误密码登录
    Given 用户 "testuser" 存在，邮箱为 "test@example.com"，密码为 "Password123"
    When 用户使用用户名 "testuser" 和密码 "WrongPassword" 登录
    Then 用户登录应该失败
    And 用户应该看到错误消息 "用户名或密码错误"

  @nonexistent-user
  Scenario: 用户使用不存在的用户名登录
    When 用户使用用户名 "nonexistent" 和密码 "AnyPassword123" 登录
    Then 用户登录应该失败
    And 用户应该看到错误消息 "用户名或密码错误"

  @unverified-account
  Scenario: 用户使用未验证的邮箱登录
    Given 用户 "unverified" 存在，邮箱为 "unverified@example.com"，密码为 "Password123"
    When 用户使用用户名 "unverified" 和密码 "Password123" 登录
    Then 用户应该成功登录

  @disabled-account
  Scenario: 用户使用已禁用的账户登录
    Given 用户 "disabled" 存在，邮箱为 "disabled@example.com"，密码为 "Password123"
    And 管理员禁用用户 "disabled"
    When 用户使用用户名 "disabled" 和密码 "Password123" 登录
    Then 用户登录应该失败
    And 用户应该看到错误消息 "账户已被禁用"

  @case-sensitive-username
  Scenario: 用户名大小写敏感性测试
    Given 用户 "TestUser" 存在，邮箱为 "testuser@example.com"，密码为 "Password123"
    When 用户使用用户名 "testuser" 和密码 "Password123" 登录
    Then 用户登录应该失败
    And 用户应该看到错误消息 "用户名或密码错误"

  @update-profile
  Scenario: 用户更新个人信息
    Given 用户 "profileuser" 存在，邮箱为 "profile@example.com"，密码为 "Password123"
    And 用户使用用户名 "profileuser" 和密码 "Password123" 登录
    When 用户更新个人信息为名字 "John"，姓氏 "Doe"，电话 "1234567890"
    Then 用户个人信息应该更新为名字 "John"，姓氏 "Doe"，电话 "1234567890"

  @change-password
  Scenario: 用户更改密码
    Given 用户 "passworduser" 存在，邮箱为 "password@example.com"，密码为 "OldPassword123"
    And 用户使用用户名 "passworduser" 和密码 "OldPassword123" 登录
    When 用户将密码从 "OldPassword123" 更新为 "NewPassword456"
    Then 用户密码应该更新成功
    And 用户使用用户名 "passworduser" 和密码 "NewPassword456" 登录
    Then 用户应该成功登录