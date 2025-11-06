# language: zh-CN
功能: 用户注册管理
  作为系统用户
  我希望能够注册新账户
  以便使用系统的各项功能

  背景:
    给定 系统已经初始化用户服务

  @user-registration @success
  场景: 成功注册新用户
    当 我尝试使用以下信息注册用户:
      | username | email              | password     | firstName | lastName |
      | john_doe | john@example.com   | P@ssw0rd123  | John      | Doe     |
    那么 注册应该成功
    并且 我应该收到验证令牌
    并且 用户状态应该是"未验证"

  @user-registration @duplicate-username
  场景: 使用已存在的用户名注册
    并且 用户"jane_doe"已经存在
    当 我尝试使用用户名"jane_doe"注册新用户
    那么 注册应该失败
    并且 我应该收到错误消息"Username already exists"

  @user-registration @duplicate-email
  场景: 使用已存在的邮箱注册
    并且 用户"jane_smith"已经存在，邮箱为"jane@example.com"
    当 我尝试使用邮箱"jane@example.com"注册新用户
    那么 注册应该失败
    并且 我应该收到错误消息"Email already exists"

  @user-registration @invalid-email
  场景大纲: 使用无效邮箱格式注册
    当 我尝试使用邮箱"<email>"注册用户
    那么 注册应该失败
    并且 我应该收到错误消息"Invalid email format"

    例子:
      | email              |
      | invalid-email      |
      | @example.com       |
      | user@              |
      | user@.com          |
      | user@domain        |

  @user-registration @weak-password
  场景大纲: 使用弱密码注册
    当 我尝试使用密码"<password>"注册用户
    那么 注册应该失败
    并且 我应该收到错误消息"Password does not meet security requirements"

    例子:
      | password     |
      | 123          |
      | password     |
      | PASSWORD     |
      | Pass123      |
      | P@ss         |

  @user-registration @verification
  场景: 验证用户邮箱
    给定 我已经成功注册用户"bob_wilson"
    并且 我收到了验证令牌
    当 我使用验证令牌验证邮箱
    那么 验证应该成功
    并且 用户状态应该是"已验证"

  @user-registration @invalid-token
  场景: 使用无效令牌验证邮箱
    当 我使用无效令牌验证邮箱
    那么 验证应该失败
    并且 我应该收到错误消息"Invalid verification token"

  @user-registration @bulk-registration
  场景: 批量注册用户
    当 我尝试注册以下多个用户:
      | username   | email                | password     | firstName | lastName |
      | alice      | alice@example.com    | P@ssw0rd123  | Alice     | Smith   |
      | bob        | bob@example.com      | P@ssw0rd456  | Bob       | Johnson |
      | charlie    | charlie@example.com  | P@ssw0rd789  | Charlie   | Brown   |
    那么 所有用户都应该注册成功
    并且 每个用户都应该收到验证令牌
    并且 所有用户状态都应该是"未验证"