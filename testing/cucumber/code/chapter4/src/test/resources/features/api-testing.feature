@api-testing @data-driven
Feature: API测试数据驱动

  背景:
    Given API基础URL设置为 "http://localhost"
    And 请求头包含 "Content-Type": "application/json"

  @scenario-outline
  Scenario Outline: 使用场景大纲测试API端点
    When 用户发送 "<方法>" 请求到 "<端点>"
    Then 响应状态码应该是 "<状态码>"
    And 响应应该包含字段 "<响应字段>"

    Examples:
      | 方法  | 端点           | 状态码 | 响应字段 |
      | GET   | /api/products  | 200    | products |
      | GET   | /api/accounts  | 200    | accounts |
      | POST  | /api/products  | 201    | id       |
      | GET   | /api/nonexistent | 404 | error    |

  @parameter-transformer
  Scenario: 使用参数转换器测试API
    When 用户发送 "GET" 请求到 "/api/products?category=手机&brand=Apple"
    Then 响应状态码应该是 "200"
    And 响应应该包含字段 "products"

  @data-table
  Scenario: 使用数据表设置API测试参数
    When 使用以下数据表设置API测试参数
      | header.Authorization | Bearer token123 |
      | body.name            | 测试产品        |
      | body.price           | 999.00          |
      | body.category        | 手机            |
    And 用户发送 "POST" 请求到 "/api/products"
    Then 响应状态码应该是 "201"
    And 响应应该包含字段 "id"

  @data-table
  Scenario: 使用数据表验证API响应
    When 用户发送 "GET" 请求到 "/api/products/1"
    Then 响应状态码应该是 "200"
    And 响应应该包含以下数据
      | name     | iPhone 14 Pro |
      | price    | 999.00        |
      | category | 手机          |
      | brand    | Apple         |

  @scenario-outline
  Scenario Outline: 使用场景大纲测试带参数的API请求
    When 使用场景大纲参数发送 "<方法>" 请求到 "<端点>"，参数为 "<参数>"
    Then 响应状态码应该是 "<状态码>"

    Examples:
      | 方法  | 端点          | 参数                          | 状态码 |
      | GET   | /api/products | category=手机,brand=Apple      | 200    |
      | GET   | /api/products | minPrice=500,maxPrice=1000    | 200    |
      | GET   | /api/accounts | type=支票账户,active=true     | 200    |
      | GET   | /api/accounts | minBalance=1000,verified=true | 200    |

  @performance-testing
  Scenario: API性能测试
    When 用户发送 "GET" 请求到 "/api/products"
    Then 响应状态码应该是 "200"
    And 响应时间应该小于 "1000" 毫秒

  @negative-testing
  Scenario: API错误处理测试
    When 用户发送 "GET" 请求到 "/api/nonexistent"
    Then 响应状态码应该是 "404"
    And 响应应该包含字段 "error"
    And 响应中字段 "error" 的值应该是 "Not Found"

  @negative-testing
  Scenario: API无效请求测试
    When 请求体包含 "name": ""
    And 请求体包含 "price": "invalid_price"
    And 用户发送 "POST" 请求到 "/api/products"
    Then 响应状态码应该是 "400"
    And 响应应该包含字段 "errors"