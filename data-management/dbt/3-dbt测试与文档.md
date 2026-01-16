# 第3章：dbt测试与文档

## 3.1 dbt测试框架概述

dbt提供了强大的测试框架，用于确保数据质量和业务逻辑的正确性。测试是数据管道可靠性的关键保障。

### 3.1.1 测试的重要性

- **数据质量保障**：验证数据的完整性、准确性和一致性
- **业务逻辑验证**：确保转换逻辑符合业务规则
- **回归测试**：防止代码变更引入错误
- **文档化**：测试本身就是数据质量要求的文档

### 3.1.2 测试类型分类

| 测试类型 | 描述 | 适用场景 |
|---------|------|----------|
| **唯一性测试** | 验证字段值唯一 | 主键、业务键 |
| **非空测试** | 验证字段不为空 | 必填字段 |
| **关系测试** | 验证外键关系 | 数据完整性 |
| **接受值测试** | 验证枚举值 | 状态字段 |
| **自定义测试** | 自定义业务规则 | 复杂业务逻辑 |

## 3.2 内置测试的使用

### 3.2.1 唯一性测试（unique）

```yaml
# 在schema.yml中定义
version: 2

models:
  - name: dim_customers
    columns:
      - name: customer_id
        tests:
          - unique
```

### 3.2.2 非空测试（not_null）

```yaml
models:
  - name: dim_customers
    columns:
      - name: email
        tests:
          - not_null
```

### 3.2.3 关系测试（relationships）

```yaml
models:
  - name: fct_orders
    columns:
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id
```

### 3.2.4 接受值测试（accepted_values）

```yaml
models:
  - name: fct_orders
    columns:
      - name: status
        tests:
          - accepted_values:
              values: ['pending', 'completed', 'cancelled']
```

## 3.3 自定义测试

### 3.3.1 创建自定义测试

```sql
-- tests/custom/test_positive_amount.sql
-- 自定义测试：验证金额为正数

select 
    order_id,
    total_amount
from {{ ref('fct_orders') }}
where total_amount < 0
```

### 3.3.2 复杂业务规则测试

```sql
-- tests/custom/test_customer_lifetime_value.sql
-- 验证客户生命周期价值逻辑

with customer_metrics as (
    select
        customer_id,
        sum(case when status = 'completed' then total_amount else 0 end) as calculated_lifetime_value
    from {{ ref('fct_orders') }}
    group by customer_id
),

dim_data as (
    select
        customer_id,
        lifetime_value
    from {{ ref('dim_customers') }}
)

select 
    d.customer_id,
    d.lifetime_value as dim_value,
    c.calculated_lifetime_value as calculated_value
from dim_data d
join customer_metrics c on d.customer_id = c.customer_id
where abs(d.lifetime_value - c.calculated_lifetime_value) > 0.01  -- 允许微小差异
```

## 3.4 测试配置与执行

### 3.4.1 测试配置

```yaml
# dbt_project.yml中的测试配置
tests:
  chapter3_example:
    +severity: warn  # 测试失败级别：error/warn
    
    # 分层测试配置
    staging:
      +severity: error
    marts:
      +severity: warn
```

### 3.4.2 测试执行命令

```bash
# 运行所有测试
dbt test

# 运行特定模型的测试
dbt test --models dim_customers

# 运行特定标签的测试
dbt test --tag data_quality

# 运行自定义测试
dbt test --select test_type:custom

# 运行数据源测试
dbt test --select source:*
```

### 3.4.3 测试结果分析

```bash
# 查看测试详情
dbt test --store-failures

# 测试失败数据存储到数据库，便于分析
```

## 3.5 数据文档化

### 3.5.1 模型文档

```yaml
# models/schema.yml
version: 2

models:
  - name: dim_customers
    description: "客户维度表，包含客户基本信息和业务指标"
    
    columns:
      - name: customer_id
        description: "客户唯一标识符"
        tests:
          - unique
          - not_null
          
      - name: email
        description: "客户邮箱地址，用于联系和营销"
        tests:
          - not_null
          
      - name: lifetime_value
        description: "客户生命周期价值，基于已完成订单计算"
        meta:
          business_metric: true
          currency: USD
```

### 3.5.2 数据源文档

```yaml
# models/sources.yml
version: 2

sources:
  - name: raw
    description: "原始业务系统数据源"
    
    tables:
      - name: customers
        description: "客户主数据表，来自CRM系统"
        meta:
          source_system: crm
          refresh_frequency: daily
          
        columns:
          - name: id
            description: "系统生成的客户ID"
```

### 3.5.3 宏文档

```sql
-- macros/currency_conversion.sql
{% macro currency_conversion(amount, from_currency, to_currency='USD') %}
  /*
  货币转换宏
  
  Args:
    amount: 要转换的金额
    from_currency: 原始货币代码
    to_currency: 目标货币代码，默认为USD
    
  Returns:
    转换后的金额
  */
  
  case 
    when {{ from_currency }} = '{{ to_currency }}' then {{ amount }}
    when {{ from_currency }} = 'EUR' then {{ amount }} * 1.1
    when {{ from_currency }} = 'GBP' then {{ amount }} * 1.3
    else {{ amount }}
  end
{% endmacro %}
```

## 3.6 文档生成与查看

### 3.6.1 生成文档

```bash
# 生成文档
dbt docs generate

# 文档包含：
# - 数据模型关系图（DAG）
# - 模型和列的详细描述
# - 测试定义和结果
# - 数据血缘分析
```

### 3.6.2 查看文档

```bash
# 启动文档服务器
dbt docs serve

# 访问 http://localhost:8080 查看文档
```

### 3.6.3 文档功能特性

1. **数据血缘分析**：追踪数据从源到目标的完整路径
2. **依赖关系可视化**：显示模型间的依赖关系
3. **测试覆盖率**：展示测试覆盖情况
4. **搜索功能**：快速查找模型和列
5. **导出功能**：支持文档导出

## 3.7 测试最佳实践

### 3.7.1 测试策略

```yaml
# 分层测试策略
models:
  - name: stg_customers
    description: "客户数据清洗层"
    tests:
      - unique: [customer_id]
      - not_null: [customer_id, email]
      
  - name: dim_customers  
    description: "客户维度表"
    tests:
      - relationships:
          from: customer_id
          to: ref('stg_customers')
          field: customer_id
```

### 3.7.2 测试数据管理

```sql
-- 使用种子数据创建测试用例
-- seeds/test_cases/customer_test_data.csv
customer_id,first_name,last_name,email,expected_segment
1,John,Doe,john@example.com,VIP
2,Jane,Smith,jane@example.com,Regular

-- 在测试中使用种子数据
select 
    t.customer_id,
    t.expected_segment,
    c.customer_segment as actual_segment
from {{ ref('test_cases_customer_test_data') }} t
left join {{ ref('dim_customers') }} c on t.customer_id = c.customer_id
where c.customer_segment != t.expected_segment
```

### 3.7.3 性能测试

```sql
-- 测试数据量增长
-- tests/performance/test_model_performance.sql

{% set row_count = ref('dim_customers') | count_rows %}

{% if row_count > 1000000 %}
    -- 如果数据量超过100万行，检查性能
    select 1 as performance_check
    where false  -- 这里可以添加具体的性能检查逻辑
{% else %}
    select 0 as performance_check
    where false
{% endif %}
```

## 3.8 集成测试与CI/CD

### 3.8.1 自动化测试流程

```yaml
# .github/workflows/dbt-tests.yml
name: dbt Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install dbt-postgres
    
    - name: Run dbt tests
      run: |
        dbt deps
        dbt compile
        dbt test --store-failures
```

### 3.8.2 测试环境管理

```bash
# 使用不同的测试环境
# 开发环境
dbt test --target dev

# 测试环境  
dbt test --target test

# 生产环境（只读）
dbt test --target prod --read-only
```

## 3.9 常见问题与解决方案

### 3.9.1 测试失败分析

**问题**：测试频繁失败
**解决方案**：分析失败数据，调整测试阈值或修复数据质量问题

### 3.9.2 性能问题

**问题**：测试运行时间过长
**解决方案**：优化测试SQL，使用增量测试，并行执行

### 3.9.3 文档同步

**问题**：文档与实际代码不同步
**解决方案**：将文档生成集成到CI/CD流程中

## 3.10 本章总结

本章深入探讨了dbt的测试与文档功能：

- 内置测试类型和使用方法
- 自定义测试的创建和执行
- 数据文档化的最佳实践
- 文档生成和查看
- 测试集成到CI/CD流程

通过本章学习，您应该能够：
- 设计全面的数据质量测试策略
- 创建自定义业务规则测试
- 生成和维护数据文档
- 将测试集成到自动化流程中

---

**下一步**：[第4章：dbt宏与Jinja模板](./4-dbt宏与Jinja模板.md)