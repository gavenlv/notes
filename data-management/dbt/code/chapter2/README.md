# 第2章代码示例：dbt核心概念与模型定义

## 代码结构说明

本章代码演示dbt模型的核心概念，包括模型配置、依赖管理、分层架构和高级特性。

## 文件说明

### 模型文件
- `models/staging/` - 原始数据层模型
- `models/intermediate/` - 中间层模型
- `models/marts/` - 业务数据层模型

### 配置文件
- `dbt_project.yml` - 项目配置，包含分层配置
- `models/sources.yml` - 数据源定义
- `models/schema.yml` - 模型文档和测试

### 高级特性
- `models/incremental/` - 增量模型示例
- `snapshots/` - 快照示例
- `seeds/` - 种子数据示例

## 运行步骤

### 1. 环境准备

确保已安装dbt并配置数据库连接。

### 2. 运行示例

```bash
# 查看模型依赖关系
dbt ls --resource-type model

# 编译所有模型
dbt compile

# 运行staging层模型
dbt run --models staging.*

# 运行中间层模型
dbt run --models intermediate.*

# 运行marts层模型
dbt run --models marts.*

# 运行增量模型
dbt run --models incremental.*

# 创建快照
dbt snapshot

# 加载种子数据
dbt seed
```

### 3. 查看依赖关系

```bash
# 生成文档
dbt docs generate

# 查看DAG图
dbt docs serve
```

## 学习目标

通过本章代码，您将学会：
- 设计合理的模型分层架构
- 配置不同的物化策略
- 管理模型间的依赖关系
- 使用增量模型处理大数据
- 创建数据快照跟踪历史变化
- 使用种子数据管理静态数据

## 关键概念演示

### 1. 分层架构
- **Staging层**：数据清洗和基础转换
- **Intermediate层**：复杂业务逻辑
- **Marts层**：分析就绪的数据模型

### 2. 物化策略
- `view`：轻量级转换
- `table`：频繁查询的结果
- `incremental`：大数据量增量处理

### 3. 依赖管理
- 使用`ref()`函数引用其他模型
- dbt自动解析依赖关系
- 可视化DAG图

## 注意事项

- 增量模型需要配置合适的唯一键
- 快照需要定义更新策略
- 种子数据适合静态参考数据
- 根据数据量选择合适的物化策略