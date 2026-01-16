# 第2章：dbt核心概念与模型定义

## 2.1 dbt模型的核心概念

### 2.1.1 什么是dbt模型？

dbt模型是使用SQL定义的数据转换逻辑，它们是dbt项目的核心构建块。每个模型对应一个SQL文件，定义了如何从原始数据转换为分析就绪的数据。

### 2.1.2 模型的关键特性

- **声明式**：描述想要的结果，而不是如何实现
- **可组合**：模型可以引用其他模型
- **可测试**：内置数据质量测试
- **可文档化**：自动生成文档
- **版本控制**：所有模型都是文本文件

## 2.2 模型配置与物化策略

### 2.2.1 模型配置语法

```sql
-- 在模型文件中配置
{{ config(
    materialized='table',
    schema='analytics',
    alias='customer_summary',
    tags=['daily', 'reporting']
) }}

select * from {{ ref('stg_customers') }}
```

### 2.2.2 物化策略类型

| 物化类型 | 描述 | 适用场景 |
|---------|------|----------|
| `table` | 创建物理表 | 频繁查询的最终结果 |
| `view` | 创建视图 | 轻量级转换，实时性要求高 |
| `incremental` | 增量更新表 | 大数据量，只处理新数据 |
| `ephemeral` | 临时CTE | 中间计算，不物化到数据库 |

### 2.2.3 物化策略选择指南

```sql
-- 示例：根据数据量选择物化策略
{{ config(
    materialized=(
        "incremental" if is_incremental() 
        else "table"
    )
) }}

{% if is_incremental() %}
    -- 增量模式：只处理新数据
    select * from {{ this }}
    where updated_at > (select max(updated_at) from {{ this }})
{% else %}
    -- 全量模式：处理所有数据
    select * from {{ source('raw', 'customers') }}
{% endif %}
```

## 2.3 模型依赖与引用

### 2.3.1 引用其他模型

使用`ref()`函数引用其他模型：

```sql
-- 正确：使用ref()函数
select * from {{ ref('stg_customers') }}

-- 错误：直接使用表名
select * from stg_customers  -- 不推荐！
```

### 2.3.2 依赖关系管理

dbt自动解析模型间的依赖关系：

```sql
-- models/marts/dim_customers.sql
{{ config(materialized='table') }}

with customer_data as (
    select * from {{ ref('stg_customers') }}  -- 依赖staging层
),
order_data as (
    select * from {{ ref('stg_orders') }}     -- 依赖staging层
)

select 
    c.customer_id,
    c.full_name,
    count(o.order_id) as order_count,
    sum(o.total_amount) as total_spent
from customer_data c
left join order_data o on c.customer_id = o.customer_id
group by 1, 2
```

### 2.3.3 可视化依赖关系

```bash
# 生成DAG图
dbt docs generate

# 查看依赖关系
dbt ls --resource-type model --output name | dbt-deps
```

## 2.4 模型分层架构

### 2.4.1 经典三层架构

```
models/
├── staging/           # 原始数据层
│   ├── stg_customers.sql
│   └── stg_orders.sql
├── intermediate/      # 中间层
│   ├── int_customer_orders.sql
│   └── int_product_sales.sql
└── marts/            # 业务数据层
    ├── dim_customers.sql
    ├── fact_orders.sql
    └── fct_daily_sales.sql
```

### 2.4.2 各层职责说明

#### Staging层（原始数据层）
- **目的**：数据清洗和基础转换
- **特点**：接近原始数据结构
- **物化**：通常使用view

```sql
-- models/staging/stg_customers.sql
{{ config(materialized='view') }}

select
    id as customer_id,
    trim(first_name) as first_name,
    trim(last_name) as last_name,
    lower(email) as email,
    created_at::timestamp as created_at
from {{ source('raw', 'customers') }}
where deleted_at is null
```

#### Intermediate层（中间层）
- **目的**：复杂业务逻辑和关联
- **特点**：可重用的业务逻辑
- **物化**：table或view

```sql
-- models/intermediate/int_customer_metrics.sql
{{ config(materialized='table') }}

with customer_orders as (
    select
        customer_id,
        count(*) as order_count,
        sum(total_amount) as lifetime_value
    from {{ ref('stg_orders') }}
    where status = 'completed'
    group by 1
)

select 
    c.*,
    coalesce(co.order_count, 0) as order_count,
    coalesce(co.lifetime_value, 0) as lifetime_value
from {{ ref('stg_customers') }} c
left join customer_orders co on c.customer_id = co.customer_id
```

#### Marts层（业务数据层）
- **目的**：面向分析的数据模型
- **特点**：星型/雪花模型，维度建模
- **物化**：通常使用table

```sql
-- models/marts/dim_customers.sql
{{ config(materialized='table') }}

select
    customer_id,
    first_name,
    last_name,
    email,
    order_count,
    lifetime_value,
    case 
        when lifetime_value > 1000 then 'VIP'
        when lifetime_value > 100 then 'Regular'
        else 'New'
    end as customer_segment
from {{ ref('int_customer_metrics') }}
```

## 2.5 高级模型特性

### 2.5.1 增量模型（Incremental Models）

```sql
-- models/marts/fct_orders_incremental.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='fail'
) }}

select
    order_id,
    customer_id,
    order_date,
    total_amount,
    status,
    created_at
from {{ ref('stg_orders') }}

{% if is_incremental() %}
    where created_at >= (
        select max(created_at) from {{ this }}
    )
{% endif %}
```

### 2.5.2 快照（Snapshots）

```sql
-- snapshots/customers_snapshot.sql
{% snapshot customers_snapshot %}

{{ config(
    target_schema='snapshots',
    unique_key='customer_id',
    strategy='timestamp',
    updated_at='updated_at'
) }}

select * from {{ source('raw', 'customers') }}

{% endsnapshot %}
```

### 2.5.3 种子数据（Seeds）

```csv
# seeds/country_codes.csv
country_code,country_name,region
US,United States,North America
CN,China,Asia
JP,Japan,Asia
```

```sql
-- 在模型中使用种子数据
select 
    c.*,
    cc.country_name
from {{ ref('stg_customers') }} c
left join {{ ref('country_codes') }} cc 
    on c.country_code = cc.country_code
```

## 2.6 模型最佳实践

### 2.6.1 命名规范

```sql
-- 好的命名
models/staging/stg_customers.sql
models/marts/dim_customers.sql
models/marts/fct_orders.sql

-- 不好的命名
models/customers.sql
models/orders_fact.sql
```

### 2.6.2 代码组织

```sql
-- 好的组织：清晰的CTE结构
with
source_data as (
    select * from {{ ref('stg_customers') }}
),
enriched_data as (
    select
        *,
        case when email like '%@gmail.com' then 'Gmail' else 'Other' end as email_provider
    from source_data
),
final as (
    select * from enriched_data
)

select * from final
```

### 2.6.3 性能优化

```sql
-- 添加索引提示
{{ config(
    materialized='table',
    indexes=[
        {'columns': ['customer_id'], 'type': 'btree'},
        {'columns': ['created_at'], 'type': 'btree'}
    ]
) }}

-- 分区表
{{ config(
    materialized='incremental',
    partition_by={'field': 'order_date', 'data_type': 'date'}
) }}
```

## 2.7 调试和故障排除

### 2.7.1 常用调试命令

```bash
# 编译特定模型查看SQL
dbt compile --models stg_customers

# 查看模型依赖关系
dbt ls --resource-type model --output name | dbt-deps

# 运行前预览SQL
dbt run --models stg_customers --dry-run
```

### 2.7.2 常见错误处理

```sql
-- 错误：循环依赖
-- 模型A引用模型B，模型B又引用模型A

-- 解决方案：重新设计模型结构，避免循环引用
```

## 2.8 本章总结

本章深入探讨了dbt模型的核心概念，包括：

- 模型配置和物化策略
- 依赖管理和引用机制
- 分层架构设计
- 高级特性如增量模型和快照
- 最佳实践和调试技巧

通过本章学习，您应该能够：
- 设计合理的模型分层架构
- 选择合适的物化策略
- 管理模型间的依赖关系
- 使用高级特性优化数据管道

---

**下一步**：[第3章：dbt测试与文档](./3-dbt测试与文档.md)