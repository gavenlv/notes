# BigQuery 入门指南 / Getting Started with BigQuery

## 中文版

### 什么是BigQuery？

BigQuery是Google Cloud Platform提供的一种全托管式、无服务器的数据仓库服务，它允许用户使用SQL查询大规模数据集。BigQuery的设计目标是处理PB级别的数据，并且能够在几秒钟内完成复杂的分析查询。

### 主要特点

- **无服务器架构**：无需管理基础设施，按需付费
- **高性能**：使用列式存储和分布式查询执行
- **可扩展性**：能够处理从GB到PB级别的数据
- **SQL支持**：使用标准SQL语法进行查询
- **集成性**：与Google Cloud生态系统和其他数据工具无缝集成

### 基本概念

- **项目（Project）**：资源和权限的顶级容器
- **数据集（Dataset）**：表和视图的容器，类似于传统数据库中的schema
- **表（Table）**：存储数据的结构，有模式定义
- **视图（View）**：基于SQL查询的虚拟表
- **分区表（Partitioned Table）**：按特定列（如日期）分区的表，可提高查询效率并降低成本
- **聚簇表（Clustered Table）**：在分区内按指定列排序的表，进一步优化查询性能

### 开始使用BigQuery

#### 1. 创建Google Cloud项目

1. 访问[Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用BigQuery API

#### 2. 创建数据集

```sql
CREATE SCHEMA `project_id.dataset_name`
OPTIONS(
  location = "US"
);
```

#### 3. 创建表并加载数据

```sql
-- 创建表
CREATE TABLE `project_id.dataset_name.table_name`
(
  id INT64,
  name STRING,
  created_at TIMESTAMP
);

-- 加载数据
LOAD DATA INTO `project_id.dataset_name.table_name`
FROM FILES(
  format = 'CSV',
  uris = ['gs://bucket_name/path/to/file.csv']
);
```

#### 4. 执行查询

```sql
SELECT *
FROM `project_id.dataset_name.table_name`
WHERE created_at > TIMESTAMP('2023-01-01')
LIMIT 100;
```

### 常用工具和接口

- **Google Cloud Console**：Web界面，用于管理和查询
- **bq命令行工具**：用于脚本和自动化
- **客户端库**：支持多种编程语言（Python, Java, Node.js等）
- **BigQuery API**：用于程序化访问
- **BI工具集成**：与Looker, Tableau, Power BI等工具集成

### 下一步学习

- 了解BigQuery的工作原理和架构
- 学习高级SQL功能和优化技巧
- 探索数据加载和导出选项
- 掌握权限和安全设置

---

## English Version

### What is BigQuery?

BigQuery is a fully managed, serverless data warehouse service provided by Google Cloud Platform that allows users to query large datasets using SQL. BigQuery is designed to handle petabyte-scale data and can complete complex analytical queries in seconds.

### Key Features

- **Serverless Architecture**: No infrastructure to manage, pay-as-you-go pricing
- **High Performance**: Uses columnar storage and distributed query execution
- **Scalability**: Handles data from gigabytes to petabytes
- **SQL Support**: Uses standard SQL syntax for queries
- **Integration**: Seamlessly integrates with Google Cloud ecosystem and other data tools

### Basic Concepts

- **Project**: Top-level container for resources and permissions
- **Dataset**: Container for tables and views, similar to a schema in traditional databases
- **Table**: Structure that stores data with a defined schema
- **View**: Virtual table based on SQL query
- **Partitioned Table**: Table divided by a specific column (like date) to improve query efficiency and reduce costs
- **Clustered Table**: Table sorted within partitions by specified columns, further optimizing query performance

### Getting Started with BigQuery

#### 1. Create a Google Cloud Project

1. Visit the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the BigQuery API

#### 2. Create a Dataset

```sql
CREATE SCHEMA `project_id.dataset_name`
OPTIONS(
  location = "US"
);
```

#### 3. Create a Table and Load Data

```sql
-- Create a table
CREATE TABLE `project_id.dataset_name.table_name`
(
  id INT64,
  name STRING,
  created_at TIMESTAMP
);

-- Load data
LOAD DATA INTO `project_id.dataset_name.table_name`
FROM FILES(
  format = 'CSV',
  uris = ['gs://bucket_name/path/to/file.csv']
);
```

#### 4. Run Queries

```sql
SELECT *
FROM `project_id.dataset_name.table_name`
WHERE created_at > TIMESTAMP('2023-01-01')
LIMIT 100;
```

### Common Tools and Interfaces

- **Google Cloud Console**: Web interface for management and querying
- **bq Command-line Tool**: For scripting and automation
- **Client Libraries**: Support for multiple programming languages (Python, Java, Node.js, etc.)
- **BigQuery API**: For programmatic access
- **BI Tool Integration**: Integration with Looker, Tableau, Power BI, and more

### Next Steps

- Understand BigQuery's working principles and architecture
- Learn advanced SQL features and optimization techniques
- Explore data loading and export options
- Master permissions and security settings