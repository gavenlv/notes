# 第二章代码示例

本目录包含《Apache Iceberg 从0入门到专家》第二章的相关代码示例。

## 目录结构

```
chapter2/
├── README.md          # 本文件
├── spark-setup/       # Spark集成示例
│   ├── pom.xml        # Maven依赖配置
│   ├── spark-shell.sh # Spark Shell启动脚本
│   └── spark-example.scala # Spark示例代码
├── flink-setup/       # Flink集成示例
│   ├── pom.xml        # Maven依赖配置
│   └── flink-example.sql # Flink SQL示例
├── presto-setup/      # Presto集成示例
│   └── catalog.properties # Catalog配置文件
└── config/            # 通用配置文件
    ├── spark-defaults.conf # Spark配置
    └── log4j.properties   # 日志配置
```

## 代码示例说明

### Spark集成示例

包含Spark与Iceberg集成的完整示例，演示如何配置Spark Session并创建Iceberg表。

### Flink集成示例

展示如何在Flink中配置Iceberg Catalog并创建流式表。

### Presto集成示例

提供Presto查询Iceberg表的配置示例。

## 使用说明

1. 根据你的环境修改配置文件中的路径和参数
2. 确保已安装相应的计算引擎
3. 按照文档中的步骤执行示例代码

## 相关资源

- [第二章文档](../../2-环境搭建与配置.md)