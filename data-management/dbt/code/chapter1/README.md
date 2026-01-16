# 第1章代码示例：dbt基础概念与入门

## 代码结构说明

本章代码包含一个完整的dbt项目示例，演示如何从零开始创建和运行dbt项目。

## 文件说明

- `dbt_project.yml` - dbt项目配置文件
- `profiles.yml` - 数据库连接配置文件（示例）
- `models/staging/stg_customers.sql` - 第一个数据模型
- `models/sources.yml` - 数据源定义
- `run_example.sh` - 运行示例的脚本（Linux/Mac）
- `run_example.bat` - 运行示例的脚本（Windows）

## 运行步骤

### 1. 环境准备

确保已安装：
- Python 3.7+
- dbt-core 和相应的数据库适配器
- Git（可选）

### 2. 配置数据库连接

编辑 `profiles.yml` 文件，配置您的数据库连接信息。

### 3. 运行示例

```bash
# 编译模型
dbt compile

# 运行模型
dbt run

# 运行测试
dbt test

# 生成文档
dbt docs generate

# 查看文档
dbt docs serve
```

## 学习目标

通过本章代码，您将学会：
- 创建基本的dbt项目结构
- 定义数据源和模型
- 运行和测试dbt模型
- 生成项目文档

## 注意事项

- 请根据您的数据库类型修改适配器和连接配置
- 示例中的表名和字段名需要根据您的实际数据调整
- 在生产环境中，请使用环境变量管理敏感信息