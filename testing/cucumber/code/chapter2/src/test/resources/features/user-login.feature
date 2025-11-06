# language: zh-CN
功能: 用户登录认证
  作为已注册用户
  我希望能够登录系统
  以便访问我的个人账户和使用系统功能

  背景:
    给定 系统已经初始化用户服务

  @user-login @success
  场景: 成功登录
    给定 用户"john_doe"已经存在
    并且 用户"john_doe"已经验证邮箱
    并且 用户"john_doe"的密码是"P@ssw0rd123"
    当 我使用用户名"john_doe"和密码"P@ssw0rd123"登录
    那么 登录应该成功
    并且 我应该收到用户信息
    并且 最后登录时间应该被更新

  @user-login @wrong-password
  场景: 使用错误密码登录
    给定 用户"jane_doe"已经存在
    并且 用户"jane_doe"已经验证邮箱
    当 我使用用户名"jane_doe"和错误密码登录
    那么 登录应该失败
    并且 我应该收到错误消息"Invalid username or password"

  @user-login @nonexistent-user
  场景: 使用不存在的用户名登录
    当 我使用用户名"nonexistent_user"登录
    那么 登录应该失败
    并且 我应该收到错误消息"Invalid username or password"

  @user-login @unverified-account
  场景: 使用未验证账户登录
    给定 用户"bob_wilson"已经存在
    并且 用户"bob_wilson"尚未验证邮箱
    当 我使用用户名"bob_wilson"和正确密码登录
    那么 登录应该失败
    并且 我应该收到错误消息"Account is not verified"

  @user-login @disabled-account
  场景: 使用已禁用账户登录
    给定 用户"alice_smith"已经存在
    并且 用户"alice_smith"已经验证邮箱
    并且 用户"alice_smith"的账户已被禁用
    当 我使用用户名"alice_smith"和正确密码登录
    那么 登录应该失败
    并且 我应该收到错误消息"Account is disabled"

  @user-login @multiple-attempts
  场景: 多次登录尝试
    给定 用户"charlie_brown"已经存在
    并且 用户"charlie_brown"已经验证邮箱
    并且 用户"charlie_brown"的密码是"P@ssw0rd789"
    当 我尝试使用以下凭据登录:
      | username      | password      | expectedResult |
      | charlie_brown | wrong_pass    | 失败          |
      | charlie_brown | P@ssw0rd789   | 成功          |
      | charlie_brown | another_wrong | 失败          |
    那么 登录结果应该与预期一致

  @user-login @case-sensitivity
  场景: 用户名大小写敏感性测试
    给定 用户"john_doe"已经存在
    并且 用户"john_doe"已经验证邮箱
    当 我尝试使用以下用户名变体登录:
      | username      | expectedResult |
      | john_doe      | 成功          |
      | John_Doe      | 失败          |
      | JOHN_DOE      | 失败          |
      | john_doe      | 成功          |
    那么 登录结果应该与预期一致

  @user-login @session-management
  场景: 登录会话管理
    给定 用户"session_user"已经存在
    并且 用户"session_user"已经验证邮箱
    当 我使用用户名"session_user"和正确密码登录
    那么 登录应该成功
    并且 应该创建新的用户会话
    并且 会话应该包含用户标识信息
    当 我注销当前会话
    那么 会话应该被终止
    当 我尝试使用已注销的会话访问受保护资源
    那么 访问应该被拒绝