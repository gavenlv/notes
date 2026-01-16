# 第1章：dbt基础概念与入门

## 1.1 什么是dbt？

dbt（Data Build Tool）是一个开源的数据转换工具，专门用于数据仓库环境。它允许数据分析师和工程师使用SQL来转换数据，同时提供了版本控制、测试、文档化和依赖管理等功能。

### 1.1.1 dbt的核心价值

- **SQL为中心**：使用熟悉的SQL语言进行数据转换
- **版本控制友好**：所有转换逻辑都是纯文本文件
- **测试驱动**：内置数据质量测试框架
- **文档化**：自动生成数据文档
- **模块化**：可重用的数据模型和宏

### 1.1.2 dbt的工作流程

```
原始数据源 → dbt转换 → 分析就绪的数据
    ↓              ↓              ↓
数据库表       SQL模型       数据模型
数据文件       测试用例       文档
API数据        依赖管理       版本控制
```

## 1.2 dbt的架构组成

### 1.2.1 核心组件

1. **dbt Core**：命令行工具，核心转换引擎
2. **dbt Cloud**：云端托管服务，提供Web界面
3. **适配器**：连接不同数据库的驱动程序

### 1.2.2 项目结构

一个典型的dbt项目包含以下目录：

```
my_dbt_project/
├── dbt_project.yml    # 项目配置文件
├── models/            # 数据模型目录
│   ├── staging/       # 原始数据层
│   ├── marts/         # 业务数据层
│   └── intermediate/  # 中间层
├── tests/             # 测试文件
├── macros/            # 宏定义
├── snapshots/         # 快照定义
├── analyses/          # 分析查询
└── seeds/             # 种子数据
```

## 1.3 安装和配置dbt

### 1.3.1 环境准备

#### 方法一：使用pip安装

```bash
# 创建虚拟环境
python -m venv dbt_env
source dbt_env/bin/activate  # Windows: dbt_env\Scripts\activate

# 安装dbt（以PostgreSQL为例）
pip install dbt-postgres
```

#### 方法二：使用conda安装

```bash
conda create -n dbt_env python=3.8
conda activate dbt_env
conda install -c conda-forge dbt-postgres
```

### 1.3.2 验证安装

```bash
# 检查dbt版本
dbt --version

# 查看帮助
dbt --help
```

## 1.4 创建第一个dbt项目

### 1.4.1 初始化项目

```bash
# 创建项目目录
mkdir my_first_dbt_project
cd my_first_dbt_project

# 初始化dbt项目
dbt init my_first_dbt_project
```

### 1.4.2 项目配置文件

创建`dbt_project.yml`文件：

```yaml
# dbt_project.yml
name: 'my_first_dbt_project'
version: '1.0.0'

profile: 'my_first_dbt_project'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"  # 编译输出目录
clean-targets:         # 清理目录
  - "target"
  - "dbt_packages"

models:
  my_first_dbt_project:
    # 配置模型
    materialized: table
```

### 1.4.3 数据库连接配置

创建`~/.dbt/profiles.yml`文件：

```yaml
my_first_dbt_project:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5432
      user: my_user
      pass: my_password
      dbname: my_database
      schema: dbt_my_user
      threads: 4
      keepalives_idle: 0
```

## 1.5 创建第一个数据模型

### 1.5.1 基础模型定义

创建`models/staging/stg_customers.sql`：

```sql
-- models/staging/stg_customers.sql
{{ config(materialized='view') }}

with source_data as (
    select
        id as customer_id,
        first_name,
        last_name,
        email,
        created_at,
        updated_at
    from {{ source('raw', 'customers') }}
)

select * from source_data
```

### 1.5.2 数据源定义

创建`models/sources.yml`：

```yaml
# models/sources.yml
version: 2

sources:
  - name: raw
    description: "原始数据源"
    tables:
      - name: customers
        description: "客户基本信息表"
        columns:
          - name: id
            description: "客户ID"
          - name: first_name
            description: "名字"
          - name: last_name
            description: "姓氏"
          - name: email
            description: "邮箱地址"
```

## 1.6 运行和测试模型

### 1.6.1 编译模型

```bash
# 编译SQL模型，检查语法
dbt compile
```

### 1.6.2 运行模型

```bash
# 运行所有模型
dbt run

# 运行特定模型
dbt run --models stg_customers

# 运行特定目录下的模型
dbt run --models staging.*
```

### 1.6.3 测试数据质量

```bash
# 运行所有测试
dbt test

# 测试特定模型
dbt test --models stg_customers
```

## 1.7 查看文档

### 1.7.1 生成文档

```bash
# 生成文档
dbt docs generate

# 启动文档服务器
dbt docs serve
```

### 1.7.2 访问文档

打开浏览器访问：`http://localhost:8080`

## 1.8 最佳实践

### 1.8.1 项目结构最佳实践

1. **分层设计**：staging → intermediate → marts
2. **命名规范**：使用有意义的名称
3. **版本控制**：所有文件纳入Git管理
4. **环境分离**：开发、测试、生产环境分离

### 1.8.2 开发流程

1. **本地开发**：在本地环境开发和测试
2. **代码审查**：通过Pull Request进行代码审查
3. **CI/CD**：自动化测试和部署
4. **监控告警**：监控数据质量和性能

## 1.9 常见问题与解决方案

### 1.9.1 连接问题

**问题**：无法连接到数据库
**解决方案**：检查`profiles.yml`配置和网络连接

### 1.9.2 依赖问题

**问题**：模型依赖关系错误
**解决方案**：使用`ref()`函数正确引用其他模型

### 1.9.3 性能问题

**问题**：模型运行缓慢
**解决方案**：优化SQL查询，添加索引

## 1.10 本章总结

本章介绍了dbt的基本概念、安装配置和第一个项目的创建。您学会了：

- dbt的核心概念和工作原理
- 如何安装和配置dbt环境
- 创建和运行第一个数据模型
- 基本的测试和文档生成

在下一章中，我们将深入探讨dbt的核心概念和模型定义。

---

**下一步**：[第2章：dbt核心概念与模型定义](./2-dbt核心概念与模型定义.md)