@bank-account @data-driven
Feature: 银行账户管理

  背景:
    Given 系统中有以下银行账户
      | 账号    | 持有人 | 账户类型 | 余额    | 透支限额 | 活跃 | 已验证 |
      | ACC1001 | 张三   | 支票账户 | 5000.00 | 1000.00  | true | true   |
      | ACC1002 | 李四   | 储蓄账户 | 12000.00| 0.00     | true | true   |
      | ACC1003 | 王五   | 信用账户 | -2000.00| 5000.00  | true | true   |
      | ACC1004 | 赵六   | 支票账户 | 3500.00 | 500.00   | true | false  |
      | ACC1005 | 钱七   | 储蓄账户 | 8000.00 | 0.00     | false| true   |

  @scenario-outline
  Scenario Outline: 使用场景大纲搜索账户
    When 用户使用场景大纲参数搜索账户: 持有人 "<持有人>", 账户类型 "<账户类型>", 余额范围 "<最低余额>" 到 "<最高余额>"
    Then 搜索结果应包含 "<结果数量>" 个账户

    Examples:
      | 持有人 | 账户类型 | 最低余额 | 最高余额 | 结果数量 |
      | 张三   |         |          |          | 1       |
      |        | 支票账户 | 0        | 6000     | 2       |
      |        | 储蓄账户 |          |          | 2       |
      |        |         | 4000     | 10000    | 2       |
      | 王     |         |          |          | 1       |
      |        | 信用账户 |          |          | 1       |
      |        |         | -3000    | 0        | 1       |

  @parameter-transformer
  Scenario: 使用参数转换器搜索账户
    When 用户使用转换器搜索账户: 持有人 "张", 账户类型 "支票账户", 余额 ">4000"
    Then 搜索结果应包含 1 个账户
    And 搜索结果应包含账户 "ACC1001"

  @parameter-transformer
  Scenario: 使用余额范围转换器搜索账户
    When 用户使用余额范围 "4000-10000" 搜索账户
    Then 搜索结果应包含 2 个账户
    And 搜索结果应包含账户 "ACC1001"
    And 搜索结果应包含账户 "ACC1004"

  @parameter-transformer
  Scenario: 使用账户状态转换器验证账户
    When 用户搜索活跃账户
    Then 搜索结果应包含 4 个账户
    And 账户 "ACC1001" 应该是 "活跃且已验证"
    And 账户 "ACC1004" 应该是 "活跃但未验证"

  @data-table
  Scenario: 使用数据表搜索账户
    When 用户使用以下条件搜索账户
      | 持有人姓名 | 账户类型 | 最低余额 | 最高余额 |
      | 张三       | 支票账户 | 4000     | 6000    |
    Then 搜索结果应包含 1 个账户
    And 搜索结果应包含账户 "ACC1001"

  @data-table
  Scenario: 使用数据表验证搜索结果
    When 用户搜索类型为 "储蓄账户" 的账户
    Then 搜索结果应包含以下账户
      | ACC1002 |
      | ACC1005 |

  @account-operations
  Scenario: 账户操作 - 存款
    When 用户向账户 "ACC1001" 存款 "1000.00"
    Then 操作应该成功
    And 账户 "ACC1001" 的余额应该是 "6000.00"

  @account-operations
  Scenario: 账户操作 - 取款
    When 用户从账户 "ACC1001" 取款 "2000.00"
    Then 操作应该成功
    And 账户 "ACC1001" 的余额应该是 "3000.00"

  @account-operations
  Scenario: 账户操作 - 超额取款
    When 用户从账户 "ACC1001" 取款 "7000.00"
    Then 操作应该失败
    And 账户 "ACC1001" 的余额应该是 "5000.00"

  @account-operations
  Scenario: 账户操作 - 激活账户
    When 用户激活账户 "ACC1005"
    Then 操作应该成功
    And 账户 "ACC1005" 应该是 "活跃且已验证"

  @account-operations
  Scenario: 账户操作 - 验证账户
    When 用户验证账户 "ACC1004"
    Then 操作应该成功
    And 账户 "ACC1004" 应该是 "活跃且已验证"

  @transfer-operations
  Scenario: 转账操作
    When 用户执行转账操作 "从ACC1001转账1000到ACC1002"
    Then 操作应该成功
    And 账户 "ACC1001" 的余额应该是 "4000.00"
    And 账户 "ACC1002" 的余额应该是 "13000.00"

  @transfer-operations
  Scenario: 转账操作 - 余额不足
    When 用户执行转账操作 "从ACC1001转账10000到ACC1002"
    Then 操作应该失败
    And 账户 "ACC1001" 的余额应该是 "5000.00"
    And 账户 "ACC1002" 的余额应该是 "12000.00"

  @transfer-operations
  Scenario: 转账操作 - 未验证账户
    When 用户执行转账操作 "从ACC1004转账1000到ACC1002"
    Then 操作应该失败
    And 账户 "ACC1004" 的余额应该是 "3500.00"
    And 账户 "ACC1002" 的余额应该是 "12000.00"

  @custom-object
  Scenario: 使用自定义对象参数
    Given 系统中已存在银行账户 "ACC1006:孙八:支票账户:2500.00:500.00:true:true"
    When 用户搜索持有人姓名包含 "孙" 的账户
    Then 搜索结果应包含账户 "ACC1006"

  @account-details
  Scenario: 查看账户详细信息
    When 用户查看账户 "ACC1001" 的详细信息
    Then 当前账户的持有人应该是 "张三"
    And 当前账户的余额应该是 "5000.00"
    And 当前账户应该是 "支票账户" 类型

  @complex-search
  Scenario: 复杂搜索条件组合
    When 用户使用以下条件搜索账户
      | 持有人姓名 | 账户类型 | 最低余额 | 最高余额 |
      |            | 支票账户 | 3000     | 6000    |
    Then 搜索结果应包含 2 个账户
    And 搜索结果中的所有账户都是 "支票账户" 类型
    And 搜索结果中的所有账户余额都在 "3000" 到 "6000" 之间

  @negative-testing
  Scenario: 无效搜索条件
    When 用户使用场景大纲参数搜索账户: 持有人 "不存在的用户", 账户类型 "", 余额范围 "" 到 ""
    Then 搜索结果应包含 0 个账户

  @negative-testing
  Scenario: 搜索非活跃账户
    When 用户搜索活跃账户
    Then 搜索结果应包含 4 个账户
    And 搜索结果不应包含账户 "ACC1005"