# 第三章代码示例

本目录包含《Apache Iceberg 从0入门到专家》第三章的相关代码示例。

## 目录结构

```
chapter3/
├── README.md              # 本文件
├── spark-table-ops/       # Spark表操作示例
│   ├── pom.xml            # Maven依赖配置
│   ├── table-operations.scala # 表操作示例代码
│   └── time-travel.scala  # 时间旅行示例代码
├── flink-table-ops/       # Flink表操作示例
│   ├── pom.xml            # Maven依赖配置
│   └── flink-table-ops.sql # Flink SQL表操作示例
└── advanced-features/     # 高级特性示例
    ├── schema-evolution.scala # Schema演变示例
    └── partition-management.scala # 分区管理示例
```

## 代码示例说明

### Spark表操作示例

包含使用Spark进行Iceberg表操作的完整示例，演示创建表、插入数据、查询、更新、删除等操作。

### Flink表操作示例

展示如何在Flink中使用SQL进行Iceberg表操作。

### 高级特性示例

提供Schema演变和分区管理的示例代码。

## 使用说明

1. 根据你的环境修改配置文件中的路径和参数
2. 确保已安装相应的计算引擎
3. 按照文档中的步骤执行示例代码

## 相关资源

- [第三章文档](../../3-表操作详解.md)