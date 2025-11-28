# 第五章：Iceberg 生态系统集成代码示例

本目录包含了第五章中讨论的各种生态系统集成的实际代码示例。

## 目录结构

```
ecosystem-integration/
├── spark-integration/          # Spark 集成示例
│   ├── basic-setup.scala       # 基本配置和表操作
│   ├── s3-integration.scala    # S3 存储集成
│   └── atlas-integration.scala # Atlas 数据治理集成
├── flink-integration/          # Flink 集成示例
│   ├── basic-setup.java        # 基本配置和表操作
│   ├── streaming-write.java    # 流式写入示例
│   └── kafka-integration.java  # Kafka 集成示例
├── trino-integration/          # Trino 集成示例
│   ├── query-examples.sql      # 查询示例
│   └── performance-tuning.sql  # 性能优化示例
├── storage-systems/            # 存储系统集成
│   ├── hdfs-config.xml         # HDFS 配置示例
│   ├── s3-config.scala         # S3 配置示例
│   └── local-fs-config.scala   # 本地文件系统配置示例
└── visualization/              # 可视化工具集成
    ├── superset-dashboard.json # Superset 仪表板配置
    └── grafana-dashboard.json  # Grafana 仪表板配置
```

## 环境要求

- Java 8 或更高版本
- Scala 2.12 或 2.13
- Apache Spark 3.3+
- Apache Flink 1.16+
- Trino 400+
- Apache Atlas (可选)
- Superset/Grafana (可选)

## 运行说明

每个示例都包含了详细的注释说明如何运行代码。在运行之前，请确保：

1. 相关的大数据服务已经启动并正确配置
2. 必要的依赖库已经添加到类路径中
3. 配置文件中的连接信息已经更新为实际环境信息

## 示例文件说明

### Spark 集成示例
- `basic-setup.scala`: 演示如何配置 Spark Session 并进行基本的 Iceberg 表操作
- `s3-integration.scala`: 展示如何在 Spark 中配置和使用 S3 存储
- `atlas-integration.scala`: 演示如何与 Apache Atlas 集成进行数据治理

### Flink 集成示例
- `basic-setup.java`: 演示 Flink 环境的基本配置和 Iceberg Catalog 使用
- `streaming-write.java`: 展示如何将流式数据写入 Iceberg 表
- `kafka-integration.java`: 演示如何使用 Flink 消费 Kafka 数据并写入 Iceberg 表

### Trino 集成示例
- `query-examples.sql`: 包含各种 Iceberg 表查询示例
- `performance-tuning.sql`: 展示性能优化相关的查询技巧

### 存储系统集成
- `hdfs-config.xml`: HDFS 配置文件示例
- `s3-config.scala`: S3 存储配置示例
- `local-fs-config.scala`: 本地文件系统配置示例

### 可视化工具集成
- `superset-dashboard.json`: Superset 仪表板配置文件
- `grafana-dashboard.json`: Grafana 仪表板配置文件