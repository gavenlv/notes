# 第7章：dbt高级特性与自定义操作

## 概述
本章深入探讨dbt的高级特性和自定义操作，包括复杂宏开发、自定义物料化策略、钩子函数、包管理、性能优化技巧等高级功能。

## 7.1 高级宏开发

### 7.1.1 复杂业务逻辑宏

#### 动态SQL生成
```sql
-- 动态字段选择宏
{% macro dynamic_column_selection(table_name, columns, where_clause='') %}
    SELECT
    {% for column in columns %}
        {{ column }}{% if not loop.last %},{% endif %}
    {% endfor %}
    FROM {{ table_name }}
    {% if where_clause %}
    WHERE {{ where_clause }}
    {% endif %}
{% endmacro %}
```

#### 递归宏处理
```sql
-- 递归处理层级数据
{% macro process_hierarchical_data(root_id, depth=10) %}
    WITH RECURSIVE hierarchy AS (
        SELECT 
            id,
            parent_id,
            name,
            1 as level
        FROM categories
        WHERE id = {{ root_id }}
        
        UNION ALL
        
        SELECT 
            c.id,
            c.parent_id,
            c.name,
            h.level + 1
        FROM categories c
        INNER JOIN hierarchy h ON c.parent_id = h.id
        WHERE h.level < {{ depth }}
    )
    SELECT * FROM hierarchy
{% endmacro %}
```

### 7.1.2 宏包开发

#### 创建可复用宏包
```sql
-- 日期处理宏包
{% macro date_package__get_fiscal_quarter(date_column, fiscal_start_month=4) %}
    -- 财年季度计算
    CASE 
        WHEN EXTRACT(MONTH FROM {{ date_column }}) - {{ fiscal_start_month - 1 }} <= 0
        THEN EXTRACT(YEAR FROM {{ date_column }}) - 1 || 'Q4'
        ELSE EXTRACT(YEAR FROM {{ date_column }}) || 
             'Q' || CEILING((EXTRACT(MONTH FROM {{ date_column }}) - {{ fiscal_start_month - 1 }}) / 3.0)
    END
{% endmacro %}

{% macro date_package__get_business_days(start_date, end_date) %}
    -- 计算工作日数量
    SELECT COUNT(*) 
    FROM generate_series(
        '{{ start_date }}'::date,
        '{{ end_date }}'::date,
        '1 day'::interval
    ) as day
    WHERE EXTRACT(DOW FROM day) NOT IN (0, 6)
{% endmacro %}
```

## 7.2 自定义物料化策略

### 7.2.1 增量模型高级配置

#### 基于条件的增量更新
```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='fail',
    incremental_strategy='merge',
    
    -- 自定义增量条件
    post_hook=[
        "DELETE FROM {{ this }} WHERE updated_at < CURRENT_DATE - INTERVAL '90 days'",
        "ANALYZE {{ this }}"
    ]
) }}

SELECT *
FROM {{ source('raw_data', 'orders') }}

{% if is_incremental() %}
    WHERE updated_at > (
        SELECT COALESCE(MAX(updated_at), '1900-01-01')
        FROM {{ this }}
    )
    AND status != 'cancelled'  -- 增量条件：排除已取消订单
{% endif %}
```

#### 分区增量策略
```sql
{{ config(
    materialized='incremental',
    unique_key='event_id',
    partition_by={'field': 'event_date', 'data_type': 'date'},
    cluster_by=['user_id', 'event_type'],
    
    -- 分区管理策略
    post_hook=[
        "CALL system.partition_maintenance('{{ this }}', 'event_date', 30)"
    ]
) }}
```

### 7.2.2 物化视图策略

#### 刷新策略配置
```sql
{{ config(
    materialized='materialized_view',
    refresh_policy='auto',
    refresh_interval_minutes=60,
    
    -- 高级配置
    indexes=[
        {'columns': ['customer_id'], 'type': 'hash'},
        {'columns': ['order_date'], 'type': 'btree'}
    ]
) }}

SELECT 
    customer_id,
    COUNT(*) as order_count,
    SUM(total_amount) as total_spent
FROM {{ ref('stg_orders') }}
GROUP BY customer_id
```

## 7.3 钩子函数与事件处理

### 7.3.1 模型级钩子

#### 前置和后置处理
```sql
{{ config(
    materialized='table',
    
    -- 前置钩子：数据准备
    pre_hook=[
        "CREATE TEMPORARY TABLE temp_customers AS SELECT * FROM {{ source('raw', 'customers') }} WHERE status = 'active'",
        "CREATE INDEX ON temp_customers (customer_id)"
    ],
    
    -- 后置钩子：清理和优化
    post_hook=[
        "GRANT SELECT ON {{ this }} TO reporting_role",
        "CREATE STATISTICS customer_stats ON {{ this }}",
        "{{ log('Model ' ~ this.name ~ ' completed successfully', info=true) }}"
    ]
) }}
```

### 7.3.2 项目级钩子

#### 全局事件处理
```yaml
# dbt_project.yml
on-run-start:
  - "{{ log('Starting dbt run at ' ~ run_started_at, info=true) }}"
  - "CREATE SCHEMA IF NOT EXISTS {{ target.schema }}"
  - "{{ create_audit_table() }}"

on-run-end:
  - "{{ log('dbt run completed at ' ~ run_started_at, info=true) }}"
  - "{{ update_run_status('completed') }}"
  - "CALL system.cleanup_temp_tables()"
```

## 7.4 包管理与依赖

### 7.4.1 第三方包集成

#### packages.yml配置
```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 0.9.2
    
  - package: calogica/dbt_expectations
    version: 0.8.5
    
  - package: dbt-labs/codegen
    version: 0.9.0
    
  - git: "https://github.com/your-company/dbt-common-macros.git"
    revision: main
    
  - local: ../shared_dbt_macros
```

### 7.4.2 自定义包开发

#### 包结构设计
```
company_dbt_package/
├── dbt_project.yml
├── macros/
│   ├── date_utils.sql
│   ├── string_utils.sql
│   └── analytics/
│       ├── cohort_analysis.sql
│       └── funnel_analysis.sql
├── models/
│   └── staging/
│       └── stg_company_specific.sql
└── README.md
```

## 7.5 性能优化高级技巧

### 7.5.1 查询优化

#### 分区和集群策略
```sql
{{ config(
    materialized='incremental',
    partition_by={'field': 'event_timestamp', 'data_type': 'timestamp', 'granularity': 'day'},
    cluster_by=['user_id', 'event_type'],
    
    -- 高级优化配置
    bigquery_labels={
        'department': 'analytics',
        'team': 'data_engineering'
    },
    
    snowflake_warehouse='ANALYTICS_WH'
) }}
```

#### 物化策略选择
```sql
-- 根据数据量选择物化策略
{% macro smart_materialization_strategy(model_name, row_count_threshold=1000000) %}
    {% set row_count = get_row_count(model_name) %}
    
    {% if row_count > row_count_threshold %}
        {{ return('incremental') }}
    {% else %}
        {{ return('table') }}
    {% endif %}
{% endmacro %}
```

### 7.5.2 内存和并发优化

#### 资源限制配置
```yaml
# dbt_project.yml
models:
  company_dbt_project:
    # 大数据量模型配置
    large_models:
      +max_query_size: 1000000
      +threads: 2
      +snowflake_warehouse: LARGE_WH
    
    # 小数据量模型配置  
    small_models:
      +max_query_size: 100000
      +threads: 8
      +snowflake_warehouse: SMALL_WH
```

## 7.6 自定义操作和插件

### 7.6.1 自定义物料化类型

#### 实现流式物化
```python
# custom_materialization.py
from dbt.adapters.base import BaseAdapter
from dbt.contracts.graph.manifest import Manifest

class StreamingMaterialization:
    def __init__(self, adapter: BaseAdapter, manifest: Manifest):
        self.adapter = adapter
        self.manifest = manifest
    
    def run(self, model):
        # 实现流式处理逻辑
        pass
```

### 7.6.2 自定义测试框架

#### 扩展测试能力
```sql
-- 复杂业务规则测试
{% test complex_business_rule(model, rule_condition, error_message) %}
    SELECT 
        COUNT(*) as violation_count
    FROM {{ model }}
    WHERE NOT ({{ rule_condition }})
    
    HAVING COUNT(*) > 0
{% endtest %}
```

## 7.7 安全与权限管理

### 7.7.1 数据脱敏

#### 敏感字段处理
```sql
{{ config(
    materialized='table',
    secure=true,
    
    -- 数据脱敏配置
    post_hook=[
        "CREATE MASKING POLICY email_mask AS (val string) 
         RETURNS string -> CASE 
             WHEN CURRENT_ROLE() = 'ANALYST' THEN val
             ELSE REGEXP_REPLACE(val, '(.).*@', '\\1***@')
         END",
        "ALTER TABLE {{ this }} ALTER COLUMN email SET MASKING POLICY email_mask"
    ]
) }}
```

### 7.7.2 行级安全

#### RLS策略实现
```sql
-- 行级安全策略
CREATE POLICY customer_data_access ON {{ this }}
    FOR ALL
    USING (
        current_user = customer_manager 
        OR department = current_department()
    );

ALTER TABLE {{ this }} ENABLE ROW LEVEL SECURITY;
```

## 7.8 监控与可观测性

### 7.8.1 自定义指标收集

#### 运行指标监控
```sql
-- 运行统计收集
{% macro collect_run_metrics() %}
    INSERT INTO dbt_run_metrics (
        model_name,
        run_id,
        rows_processed,
        execution_time,
        status
    )
    SELECT 
        '{{ this.name }}',
        '{{ invocation_id }}',
        COUNT(*),
        {{ execution_time() }},
        'completed'
    FROM {{ this }}
{% endmacro %}
```

### 7.8.2 错误处理和重试

#### 容错机制
```yaml
# dbt_project.yml
models:
  company_dbt_project:
    +retry_attempts: 3
    +retry_delay: 60
    +on_error: continue  # 或 'fail'
```

## 7.9 实战案例：电商数据分析平台

### 7.9.1 高级客户分群系统

#### 动态分群逻辑
```sql
{% macro dynamic_customer_segmentation(segmentation_rules) %}
    WITH segmentation_base AS (
        SELECT 
            customer_id,
            {% for rule in segmentation_rules %}
            CASE 
                {% for condition in rule.conditions %}
                WHEN {{ condition.expression }} THEN '{{ rule.segment_name }}'
                {% endfor %}
                ELSE 'default'
            END as segment_{{ loop.index }}
            {% if not loop.last %},{% endif %}
            {% endfor %}
        FROM {{ ref('int_customer_metrics') }}
    )
    
    SELECT 
        customer_id,
        -- 优先级分段逻辑
        COALESCE(
            segment_1, segment_2, segment_3, 'unsegmented'
        ) as final_segment
    FROM segmentation_base
{% endmacro %}
```

### 7.9.2 实时数据管道

#### 流式处理集成
```sql
{{ config(
    materialized='incremental',
    unique_key='event_id',
    incremental_strategy='merge',
    
    -- 流式处理配置
    post_hook=[
        "CALL kafka_consumer.acknowledge_messages('{{ this.name }}')",
        "{{ update_stream_watermark(this.name) }}"
    ]
) }}

SELECT *
FROM kafka_stream('customer_events')
WHERE event_timestamp > '{{ get_stream_watermark() }}'
```

## 总结

本章详细介绍了dbt的高级特性和自定义操作，包括：

1. **复杂宏开发** - 动态SQL生成、递归处理、宏包设计
2. **自定义物料化策略** - 增量模型高级配置、物化视图策略
3. **钩子函数与事件处理** - 模型级和项目级钩子
4. **包管理与依赖** - 第三方包集成、自定义包开发
5. **性能优化高级技巧** - 查询优化、资源管理
6. **自定义操作和插件** - 扩展dbt功能
7. **安全与权限管理** - 数据脱敏、行级安全
8. **监控与可观测性** - 指标收集、错误处理
9. **实战案例** - 电商数据分析平台高级功能

这些高级特性使得dbt能够适应更复杂的业务场景，提供更强的灵活性和扩展性。