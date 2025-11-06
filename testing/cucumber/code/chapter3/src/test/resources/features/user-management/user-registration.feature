@user-management @registration
Feature: 用户注册功能
  作为系统用户
  我希望能够注册账户
  以便使用系统的各项功能

  Background:
    Given 用户 "existinguser" 不存在

  @successful-registration
  Scenario: 用户使用有效信息成功注册
    When 用户使用用户名 "newuser"，邮箱 "newuser@example.com" 和密码 "StrongPass123" 注册
    Then 用户应该成功注册
    And 用户 "newuser" 应该存在
    And 系统应该有 1 个用户

  @duplicate-username
  Scenario: 用户使用已存在的用户名注册
    Given 用户 "existinguser" 存在，邮箱为 "existing@example.com"，密码为 "Password123"
    When 用户使用用户名 "existinguser"，邮箱 "another@example.com" 和密码 "StrongPass123" 注册
    Then 用户注册应该失败
    And 用户应该看到错误消息 "用户名已存在"

  @duplicate-email
  Scenario: 用户使用已存在的邮箱注册
    Given 用户 "existinguser" 存在，邮箱为 "existing@example.com"，密码为 "Password123"
    When 用户使用用户名 "newuser"，邮箱 "existing@example.com" 和密码 "StrongPass123" 注册
    Then 用户注册应该失败
    And 用户应该看到错误消息 "邮箱已存在"

  @invalid-email
  Scenario: 用户使用无效邮箱格式注册
    When 用户使用用户名 "newuser"，邮箱 "invalid-email" 和密码 "StrongPass123" 注册
    Then 用户注册应该失败
    And 用户应该看到错误消息 "邮箱格式无效"

  @weak-password
  Scenario: 用户使用弱密码注册
    When 用户使用用户名 "newuser"，邮箱 "newuser@example.com" 和密码 "weak" 注册
    Then 用户注册应该失败
    And 用户应该看到错误消息 "密码强度不足"

  @batch-registration
  Scenario: 批量创建用户
    When 已创建以下用户:
      | username | email              | password     | firstName | lastName |
      | user1    | user1@example.com  | Password123  | John      | Doe     |
      | user2    | user2@example.com  | StrongPass123 | Jane      | Smith   |
      | user3    | user3@example.com  | MyPass123    | Bob       | Johnson |
    Then 系统应该有 3 个用户
    And 用户 "user1" 应该存在
    And 用户 "user2" 应该存在
    And 用户 "user3" 应该存在

  @email-verification
  Scenario: 验证用户邮箱
    Given 用户 "unverified" 存在，邮箱为 "unverified@example.com"，密码为 "Password123"
    When 管理员验证用户 "unverified" 的邮箱
    Then 用户 "unverified" 的邮箱应该已验证

  @account-disabled
  Scenario: 禁用用户账户
    Given 用户 "activeuser" 存在，邮箱为 "active@example.com"，密码为 "Password123"
    When 管理员禁用用户 "activeuser"
    Then 用户 "activeuser" 应该被禁用