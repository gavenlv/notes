# 第4章：dbt宏与Jinja模板

## 4.1 Jinja模板引擎基础

Jinja是dbt中使用的模板引擎，它允许在SQL中嵌入动态逻辑，使代码更加模块化和可重用。

### 4.1.1 Jinja基本语法

```sql
-- 变量插值
{{ variable_name }}

-- 控制结构
{% for item in list %}
    {{ item }}
{% endfor %}

-- 条件判断
{% if condition %}
    -- 代码块
{% elif other_condition %}
    -- 其他代码块
{% else %}
    -- 默认代码块
{% endif %}
```

### 4.1.2 dbt特有的Jinja函数

| 函数 | 描述 | 示例 |
|------|------|------|
| `ref()` | 引用其他模型 | `{{ ref('stg_customers') }}` |
| `source()` | 引用数据源 | `{{ source('raw', 'customers') }}` |
| `config()` | 模型配置 | `{{ config(materialized='table') }}` |
| `this` | 引用当前模型 | `{{ this }}` |

## 4.2 宏（Macros）基础

### 4.2.1 什么是宏？

宏是可重用的代码块，类似于编程语言中的函数。它们可以接受参数并返回结果。

### 4.2.2 创建第一个宏

```sql
-- macros/format_date.sql
{% macro format_date(date_column, format='YYYY-MM-DD') %}
  /*
  日期格式化宏
  
  Args:
    date_column: 日期字段
    format: 目标格式，默认为YYYY-MM-DD
    
  Returns:
    格式化后的日期表达式
  */
  
  to_char({{ date_column }}, '{{ format }}')
{% endmacro %}
```

### 4.2.3 在模型中使用宏

```sql
-- 使用日期格式化宏
select
    order_id,
    {{ format_date('order_date') }} as formatted_date,
    {{ format_date('created_at', 'YYYY-MM-DD HH24:MI:SS') }} as created_timestamp
from {{ ref('stg_orders') }}
```

## 4.3 常用宏模式

### 4.3.1 字段选择宏

```sql
-- macros/get_columns.sql
{% macro get_columns(table_name, exclude_columns=[]) %}
  /*
  动态获取表字段列表，排除指定字段
  */
  
  {%- set columns = adapter.get_columns_in_relation(ref(table_name)) -%}
  
  {%- for column in columns -%}
    {%- if column.name not in exclude_columns -%}
      {{ column.name }}{% if not loop.last %},{% endif %}
    {%- endif -%}
  {%- endfor -%}
{% endmacro %}

-- 使用示例
select
    {{ get_columns('stg_customers', ['deleted_at']) }}
from {{ ref('stg_customers') }}
```

### 4.3.2 分页宏

```sql
-- macros/pagination.sql
{% macro paginate(limit=100, offset=0) %}
  /*
  分页宏
  */
  
  limit {{ limit }}
  {% if offset > 0 %}
    offset {{ offset }}
  {% endif %}
{% endmacro %}

-- 使用示例
select * from {{ ref('dim_customers') }}
{{ paginate(limit=50, offset=100) }}
```

### 4.3.3 条件聚合宏

```sql
-- macros/conditional_sum.sql
{% macro conditional_sum(column, condition) %}
  /*
  条件求和宏
  */
  
  sum(case when {{ condition }} then {{ column }} else 0 end)
{% endmacro %}

-- 使用示例
select
    customer_id,
    {{ conditional_sum('total_amount', "status = 'completed'") }} as completed_revenue,
    {{ conditional_sum('total_amount', "status = 'pending'") }} as pending_revenue
from {{ ref('stg_orders') }}
group by customer_id
```

## 4.4 高级宏特性

### 4.4.1 宏参数验证

```sql
-- macros/validate_currency.sql
{% macro validate_currency(amount, currency) %}
  /*
  货币验证宏，带参数检查
  */
  
  {%- if currency not in ['USD', 'EUR', 'GBP', 'CNY'] -%}
    {{ exceptions.raise_compiler_error("不支持的货币类型: " ~ currency) }}
  {%- endif -%}
  
  case 
    when {{ currency }} = 'USD' then {{ amount }} * 1.0
    when {{ currency }} = 'EUR' then {{ amount }} * 1.1
    when {{ currency }} = 'GBP' then {{ amount }} * 1.3
    when {{ currency }} = 'CNY' then {{ amount }} * 0.15
  end
{% endmacro %}
```

### 4.4.2 宏返回值

```sql
-- macros/get_table_schema.sql
{% macro get_table_schema(table_name) %}
  /*
  获取表结构信息
  */
  
  {%- set relation = ref(table_name) -%}
  {%- set columns = adapter.get_columns_in_relation(relation) -%}
  
  {%- set schema_info = [] -%}
  
  {%- for column in columns -%}
    {%- set column_info = {
        'name': column.name,
        'data_type': column.data_type,
        'nullable': column.is_nullable
    } -%}
    {%- do schema_info.append(column_info) -%}
  {%- endfor -%}
  
  {{ return(schema_info) }}
{% endmacro %}

-- 在另一个宏中使用
{% macro compare_schemas(table1, table2) %}
  {%- set schema1 = get_table_schema(table1) %}
  {%- set schema2 = get_table_schema(table2) %}
  
  -- 比较两个表的结构差异
  -- ... 比较逻辑 ...
{% endmacro %}
```

## 4.5 宏包和模块化

### 4.5.1 创建宏包

```sql
-- macros/utils/date_utils.sql
{% macro current_timestamp() %}
  current_timestamp
{% endmacro %}

{% macro date_diff(date1, date2, unit='day') %}
  datediff({{ unit }}, {{ date1 }}, {{ date2 }})
{% endmacro %}

-- macros/utils/string_utils.sql
{% macro trim_string(column) %}
  trim({{ column }})
{% endmacro %}

{% macro substring(column, start, length) %}
  substring({{ column }}, {{ start }}, {{ length }})
{% endmacro %}
```

### 4.5.2 宏命名空间

```sql
-- 使用命名空间避免冲突
{% macro utils.current_timestamp() %}
  current_timestamp
{% endmacro %}

{% macro analytics.current_timestamp() %}
  current_timestamp at time zone 'UTC'
{% endmacro %}
```

## 4.6 动态SQL生成

### 4.6.1 动态字段选择

```sql
-- macros/generate_select.sql
{% macro generate_select(table_name, include_columns=[], exclude_columns=[]) %}
  /*
  动态生成SELECT语句
  */
  
  {%- set all_columns = adapter.get_columns_in_relation(ref(table_name)) -%}
  
  select
  {%- for column in all_columns -%}
    {%- set should_include = true -%}
    
    {%- if include_columns and column.name not in include_columns -%}
      {%- set should_include = false -%}
    {%- endif -%}
    
    {%- if exclude_columns and column.name in exclude_columns -%}
      {%- set should_include = false -%}
    {%- endif -%}
    
    {%- if should_include -%}
      {{ column.name }}{% if not loop.last %},{% endif %}
    {%- endif -%}
  {%- endfor -%}
  
  from {{ ref(table_name) }}
{% endmacro %}

-- 使用示例
{{ generate_select('stg_customers', exclude_columns=['deleted_at', 'phone']) }}
```

### 4.6.2 动态WHERE条件

```sql
-- macros/apply_filters.sql
{% macro apply_filters(filters={}) %}
  /*
  动态应用WHERE条件
  */
  
  {%- if filters -%}
    where
    {%- for column, value in filters.items() -%}
      {{ column }} = '{{ value }}'{% if not loop.last %} and{% endif %}
    {%- endfor -%}
  {%- endif -%}
{% endmacro %}

-- 使用示例
select * from {{ ref('stg_customers') }}
{{ apply_filters({'country_code': 'US', 'email_status': 'valid'}) }}
```

## 4.7 宏测试和调试

### 4.7.1 宏单元测试

```sql
-- 在测试文件中测试宏
-- tests/macros/test_currency_conversion.sql

{% set test_amount = 100 %}
{% set test_currency = 'EUR' %}

-- 测试货币转换宏
select 
    {{ validate_currency(test_amount, test_currency) }} as converted_amount,
    case 
        when {{ validate_currency(test_amount, test_currency) }} = 110 then 'PASS'
        else 'FAIL'
    end as test_result
```

### 4.7.2 宏调试技巧

```sql
-- 使用log输出调试信息
{% macro debug_macro() %}
  {%- set debug_info = {
      'current_model': this.name,
      'timestamp': current_timestamp()
  } -%}
  
  {{ log("调试信息: " ~ debug_info, info=true) }}
  
  -- 宏逻辑...
{% endmacro %}

-- 编译时查看生成的SQL
dbt compile --models your_model
```

## 4.8 宏最佳实践

### 4.8.1 命名规范

```sql
-- 好的命名
macros/format_date.sql
macros/calculate_metrics.sql
macros/utils/string_helpers.sql

-- 不好的命名
macros/helpers.sql  -- 太泛化
macros/func1.sql     -- 无意义
```

### 4.8.2 文档化

```sql
-- 为宏添加完整文档
{% macro calculate_age(birth_date, reference_date=current_date) %}
  /*
  计算年龄
  
  Args:
    birth_date: 出生日期
    reference_date: 参考日期，默认为当前日期
    
  Returns:
    年龄（整数）
    
  Example:
    {{ calculate_age('birth_date') }}
    {{ calculate_age('birth_date', '2023-12-31') }}
  */
  
  date_diff('year', {{ birth_date }}, {{ reference_date }})
{% endmacro %}
```

### 4.8.3 错误处理

```sql
-- 添加适当的错误处理
{% macro safe_divide(numerator, denominator) %}
  /*
  安全除法，避免除零错误
  */
  
  case 
    when {{ denominator }} = 0 then null
    else {{ numerator }} / {{ denominator }}
  end
{% endmacro %}
```

## 4.9 性能考虑

### 4.9.1 宏编译性能

```sql
-- 避免在循环中调用复杂宏
{% for i in range(1000) %}
  {{ expensive_macro() }}  -- 不推荐！
{% endfor %}

-- 预先计算并重用结果
{% set precomputed_value = expensive_macro() %}
{% for i in range(1000) %}
  {{ precomputed_value }}
{% endfor %}
```

### 4.9.2 数据库性能

```sql
-- 考虑宏生成的SQL对数据库性能的影响
{% macro complex_calculation() %}
  -- 复杂的计算逻辑可能影响查询性能
  -- 考虑是否应该在数据库层或应用层处理
{% endmacro %}
```

## 4.10 本章总结

本章深入探讨了dbt宏与Jinja模板的使用：

- Jinja模板引擎的基本语法和dbt特有函数
- 宏的创建、参数传递和返回值
- 常用宏模式和高级特性
- 宏包管理和模块化设计
- 动态SQL生成技术
- 宏测试、调试和最佳实践

通过本章学习，您应该能够：
- 创建可重用的宏来简化代码
- 使用Jinja模板实现动态SQL生成
- 设计模块化的宏包结构
- 调试和测试宏功能
- 遵循宏开发的最佳实践

---

**下一步**：[第5章：dbt数据源与连接配置](./5-dbt数据源与连接配置.md)