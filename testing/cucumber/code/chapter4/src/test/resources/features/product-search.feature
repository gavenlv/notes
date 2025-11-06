@product-search @data-driven
Feature: 产品搜索功能

  背景:
    Given 系统中有以下产品
      | 名称         | 描述             | 价格   | 类别 | 品牌  | 库存数量 | 可用 | SKU         |
      | iPhone 14 Pro | Apple最新旗舰手机 | 999.00 | 手机 | Apple | 50       | true | IP14P-128-BLK |
      | Samsung S23   | 三星旗舰安卓手机  | 899.00 | 手机 | Samsung | 30    | true | SGS23-256-BLU |
      | MacBook Pro   | Apple高性能笔记本 | 2499.00 | 笔记本 | Apple | 15  | true | MBP16-M2-512 |
      | Sony耳机      | 索尼降噪耳机     | 399.00 | 耳机 | Sony | 0        | false | SNY-XM5-BLK |
      | iPad Air      | Apple中端平板电脑 | 599.00 | 平板 | Apple | 25       | true | IPAD-AIR-64 |

  @scenario-outline
  Scenario Outline: 使用场景大纲搜索产品
    When 用户使用场景大纲参数搜索产品: 名称包含 "<名称>", 类别 "<类别>", 品牌 "<品牌>", 价格范围 "<最低价格>" 到 "<最高价格>"
    Then 搜索结果应包含 "<结果数量>" 个产品

    Examples:
      | 名称   | 类别 | 品牌   | 最低价格 | 最高价格 | 结果数量 |
      | iPhone | 手机 | Apple  |          |          | 1       |
      |        | 手机 |        | 500      | 1000     | 2       |
      |        |      | Apple  |          |          | 3       |
      |        |      |        | 300      | 700      | 2       |
      | Pro    |      |        |          |          | 2       |
      |        | 笔记本 |      |          |          | 1       |
      |        |      | Sony   |          |          | 1       |

  @parameter-transformer
  Scenario: 使用参数转换器搜索产品
    When 用户使用转换器搜索产品: 名称包含 "iPhone", 类别 "手机", 品牌 "Apple", 价格 ">500"
    Then 搜索结果应包含 1 个产品
    And 搜索结果应包含产品 "iPhone 14 Pro"

  @parameter-transformer
  Scenario: 使用参数转换器搜索多个类别和品牌
    When 用户使用转换器搜索产品: 类别列表 "手机,平板", 品牌列表 "Apple,Samsung"
    Then 搜索结果应包含至少 1 个产品

  @parameter-transformer
  Scenario: 使用价格范围转换器搜索产品
    When 用户使用价格范围 "500-1000" 搜索产品
    Then 搜索结果应包含 2 个产品
    And 搜索结果应包含产品 "iPhone 14 Pro"
    And 搜索结果应包含产品 "Samsung S23"

  @data-table
  Scenario: 使用数据表搜索产品
    When 用户使用以下条件搜索产品
      | 名称   | 类别 | 品牌   | 最低价格 | 最高价格 |
      | iPhone | 手机 | Apple  | 500      | 1500    |
    Then 搜索结果应包含 1 个产品
    And 搜索结果应包含产品 "iPhone 14 Pro"

  @data-table
  Scenario: 使用数据表验证搜索结果
    When 用户搜索类别为 "手机" 的产品
    Then 搜索结果应包含以下产品
      | iPhone 14 Pro |
      | Samsung S23   |

  @complex-search
  Scenario: 复杂搜索条件组合
    When 用户使用以下条件搜索产品
      | 名称   | 类别 | 品牌   | 最低价格 | 最高价格 |
      |        |      | Apple  | 500      | 2000    |
    Then 搜索结果应包含 3 个产品
    And 搜索结果中的所有产品都是 "Apple" 品牌
    And 搜索结果中的所有产品价格都在 "500" 到 "2000" 之间

  @custom-object
  Scenario: 使用自定义对象参数
    Given 系统中已存在产品 "Galaxy Watch:三星智能手表:299.00:手表:Samsung:20:true:GWATCH-42-BLK"
    When 用户搜索名称包含 "Watch" 的产品
    Then 搜索结果应包含产品 "Galaxy Watch"

  @custom-object
  Scenario: 使用自定义对象验证搜索结果
    Given 系统中已存在产品 "Surface Pro:微软平板电脑:999.00:平板:Microsoft:15:true:SPRO-128"
    When 用户搜索类别为 "平板" 的产品
    Then 搜索结果应包含产品 "Surface Pro"

  @negative-testing
  Scenario: 无效搜索条件
    When 用户使用场景大纲参数搜索产品: 名称包含 "不存在的产品", 类别 "", 品牌 "", 价格范围 "" 到 ""
    Then 搜索结果应包含 0 个产品

  @negative-testing
  Scenario: 搜索无库存产品
    When 用户搜索有库存的产品
    Then 搜索结果应包含 4 个产品
    And 搜索结果不应包含产品 "Sony耳机"