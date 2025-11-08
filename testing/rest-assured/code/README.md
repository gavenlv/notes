# REST Assured 代码示例

本目录包含REST Assured教程中的所有代码示例，按章节和功能组织。

## 目录结构

```
code/
├── README.md                    # 本文件
├── basic-examples/              # 基础示例
│   ├── SimpleApiTest.java        # 简单API测试
│   ├── AuthenticationTest.java   # 认证测试
│   └── ResponseValidationTest.java # 响应验证测试
├── request-response/             # 请求与响应处理
│   ├── RequestBuilderExample.java # 请求构建示例
│   ├── ResponseExtractorExample.java # 响应提取示例
│   └── CustomFiltersExample.java # 自定义过滤器示例
├── data-handling/               # 数据处理
│   ├── JsonPathExample.java      # JSONPath示例
│   ├── XmlPathExample.java       # XMLPath示例
│   ├── DataConversionExample.java # 数据转换示例
│   └── SchemaValidationExample.java # 模式验证示例
├── authentication/               # 认证示例
│   ├── BasicAuthTest.java        # 基本认证
│   ├── OAuth2Test.java           # OAuth2认证
│   ├── ApiKeyAuthTest.java       # API密钥认证
│   └── JwtAuthTest.java          # JWT认证
├── performance/                  # 性能测试
│   ├── LoadTestExample.java      # 负载测试
│   ├── ResponseTimeTest.java     # 响应时间测试
│   └── ConcurrencyTest.java      # 并发测试
├── framework/                    # 测试框架
│   ├── BaseApiTest.java          # 基础测试类
│   ├── TestDataFactory.java      # 测试数据工厂
│   ├── ApiPageObjects.java       # API页面对象
│   └── TestReportGenerator.java  # 测试报告生成器
├── security/                     # 安全测试
│   ├── SqlInjectionTest.java     # SQL注入测试
│   ├── XssTest.java              # XSS测试
│   ├── AuthenticationBypassTest.java # 认证绕过测试
│   └── SecurityHeadersTest.java  # 安全头测试
├── resources/                    # 测试资源
│   ├── json-schemas/             # JSON模式文件
│   ├── test-data/                # 测试数据文件
│   └── config/                   # 配置文件
└── pom.xml                       # Maven配置文件
```

## 使用说明

1. 所有示例都经过验证，可以直接运行
2. 大部分示例需要根据实际API进行修改
3. 有关每个示例的详细说明，请参考对应的章节文档
4. 运行前请确保环境配置正确

## 环境要求

- Java 8或更高版本
- Maven 3.0或更高版本
- 可访问的REST API端点（示例中使用的是占位符URL）

## 快速开始

1. 克隆或下载本目录
2. 根据您的API修改示例中的URL和参数
3. 运行Maven命令：`mvn clean test`

## 贡献

欢迎提交问题报告和改进建议！