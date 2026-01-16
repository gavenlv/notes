# 第5章：dbt数据源与连接配置

## 5.1 数据源（Sources）概念

### 5.1.1 什么是数据源？

数据源是dbt中表示外部数据表的对象，它们不是由dbt创建的模型，而是已经存在于数据库中的表。

### 5.1.2 数据源的作用

- **声明依赖关系**：明确数据来自哪个外部表
- **数据血缘追踪**：建立完整的数据流水线
- **测试和文档**：为外部数据表添加测试和描述
- **环境管理**：在不同环境间切换数据源

## 5.2 数据源定义

### 5.2.1 基本数据源定义

```yaml
# sources.yml
version: 2

sources:
  - name: raw_data           # 数据源名称
    description: "原始业务数据表"
    database: production     # 数据库名
    schema: raw              # Schema名
    
    tables:
      - name: customers      # 表名
        description: "客户基本信息表"
        
      - name: orders         # 表名
        description: "订单信息表"
```

### 5.2.2 在模型中使用数据源

```sql
-- 使用source()函数引用数据源
select * from {{ source('raw_data', 'customers') }}

-- 等同于直接写表名
select * from production.raw.customers
```

## 5.3 数据源配置

### 5.3.1 字段级配置

```yaml
sources:
  - name: raw_data
    tables:
      - name: customers
        description: "客户基本信息表"
        columns:
          - name: customer_id
            description: "客户唯一标识"
            tests:
              - not_null
              - unique
          
          - name: email
            description: "客户邮箱地址"
            tests:
              - not_null
              - dbt_utils.email_address
```

### 5.3.2 数据源级测试

```yaml
sources:
  - name: raw_data
    description: "原始业务数据表"
    tests:
      - dbt_utils.equal_rowcount:
          compare_model: ref('stg_customers')
    
    tables:
      - name: customers
        tests:
          - dbt_utils.accepted_range:
              field: created_at
              min_value: '2020-01-01'
              max_value: '2023-12-31'
```

## 5.4 多环境数据源管理

### 5.4.1 环境特定配置

```yaml
# 开发环境配置
sources:
  - name: raw_data
    database: dev_database
    schema: raw
    
# 生产环境配置  
sources:
  - name: raw_data
    database: prod_database
    schema: raw
```

### 5.4.2 使用环境变量

```yaml
sources:
  - name: raw_data
    database: "{{ env_var('DB_DATABASE', 'dev_database') }}"
    schema: "{{ env_var('DB_SCHEMA', 'raw') }}"
```

## 5.5 数据库连接配置

### 5.5.1 profiles.yml文件结构

```yaml
# ~/.dbt/profiles.yml
dbt_macros_example:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5432
      user: "{{ env_var('DB_USER') }}"
      pass: "{{ env_var('DB_PASSWORD') }}"
      dbname: dbt_dev
      schema: dbt_user
      threads: 4
      
    prod:
      type: postgres
      host: prod-db.company.com
      port: 5432
      user: "{{ env_var('PROD_DB_USER') }}"
      pass: "{{ env_var('PROD_DB_PASSWORD') }}"
      dbname: dbt_prod
      schema: analytics
      threads: 8
```

### 5.5.2 支持的数据库类型

| 数据库 | 类型 | 特点 |
|--------|------|------|
| PostgreSQL | postgres | 官方支持，功能最完整 |
| Snowflake | snowflake | 云数据仓库，性能优秀 |
| BigQuery | bigquery | Google云数据仓库 |
| Redshift | redshift | AWS数据仓库 |
| Databricks | databricks | Spark-based数据平台 |

## 5.6 连接参数详解

### 5.6.1 基本连接参数

```yaml
type: postgres
host: localhost          # 数据库主机
port: 5432              # 端口号
user: dbt_user          # 用户名
pass: password          # 密码
dbname: my_database     # 数据库名
schema: analytics       # 默认schema
```

### 5.6.2 高级连接参数

```yaml
# 连接池配置
threads: 4              # 并发线程数
keepalives_idle: 0      # 保持连接活跃

# SSL配置
sslmode: require        # SSL模式
sslcert: /path/to/cert  # SSL证书
sslkey: /path/to/key    # SSL密钥

# 超时配置
connect_timeout: 10     # 连接超时(秒)
retries: 1              # 重试次数
```

## 5.7 多数据库连接

### 5.7.1 跨数据库查询

```yaml
# 连接多个数据库
outputs:
  dw:
    type: snowflake
    account: my_account
    user: dbt_user
    ...
    
  operational:
    type: postgres
    host: ops-db.company.com
    ...
```

### 5.7.2 跨数据库数据源

```yaml
sources:
  - name: operational_data
    database: operational_db
    schema: public
    
  - name: warehouse_data
    database: warehouse_db
    schema: analytics
```

## 5.8 连接安全最佳实践

### 5.8.1 密码管理

```yaml
# 使用环境变量（推荐）
pass: "{{ env_var('DB_PASSWORD') }}"

# 使用密钥管理服务
pass: "{{ env_var('AWS_SECRET_DB_PASSWORD') }}"
```

### 5.8.2 网络安全性

```yaml
# 使用私有网络
host: internal-db.company.com

# 启用SSL
sslmode: verify-full
sslrootcert: /path/to/ca.crt
```

## 5.9 连接测试和验证

### 5.9.1 连接测试命令

```bash
# 测试连接
dbt debug

# 测试特定profile
dbt debug --profile my_profile

# 测试连接但不运行模型
dbt compile --target dev
```

### 5.9.2 连接健康检查

```sql
-- 在dbt中创建连接测试模型
{{ config(materialized='test') }}

select 
    case 
        when count(*) > 0 then 'SUCCESS'
        else 'FAILURE'
    end as connection_status
from information_schema.tables
where table_schema = '{{ target.schema }}'
```

## 5.10 环境配置管理

### 5.10.1 多环境配置

```yaml
# profiles.yml
dbt_macros_example:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      dbname: dbt_dev
      schema: dev_{{ target.name }}
      
    staging:
      type: postgres  
      host: staging-db.company.com
      dbname: dbt_staging
      schema: staging_{{ target.name }}
      
    prod:
      type: postgres
      host: prod-db.company.com
      dbname: dbt_prod
      schema: prod_{{ target.name }}
```

### 5.10.2 环境切换

```bash
# 切换到开发环境
dbt run --target dev

# 切换到生产环境
dbt run --target prod

# 使用环境变量
export DBT_TARGET=prod
dbt run
```

## 5.11 数据源版本控制

### 5.11.1 数据源变更管理

```yaml
sources:
  - name: raw_data
    description: "原始业务数据表"
    meta:
      version: "1.0.0"
      last_updated: "2023-12-01"
      owner: "data_team"
    
    tables:
      - name: customers
        description: "客户基本信息表"
        meta:
          version: "2.1.0"
          change_log:
            - date: "2023-11-15"
              change: "新增phone_number字段"
            - date: "2023-10-01"
              change: "修改email字段约束"
```

### 5.11.2 数据源依赖管理

```yaml
# 声明数据源依赖关系
sources:
  - name: crm_system
    description: "CRM系统数据"
    depends_on:
      - ref('erp_system.customers')
      - ref('marketing_system.leads')
```

## 5.12 数据源监控和告警

### 5.12.1 数据新鲜度监控

```sql
-- 监控数据源新鲜度
{{ config(materialized='table') }}

select
    'customers' as table_name,
    max(updated_at) as last_updated,
    current_timestamp as check_time,
    datediff('hour', max(updated_at), current_timestamp) as hours_since_update
from {{ source('raw_data', 'customers') }}
```

### 5.12.2 数据质量监控

```yaml
sources:
  - name: raw_data
    tables:
      - name: customers
        freshness:
          warn_after: {count: 24, period: hour}
          error_after: {count: 48, period: hour}
        
        loaded_at_field: updated_at
```

## 5.13 高级连接特性

### 5.13.1 连接池优化

```yaml
# 连接池配置
outputs:
  prod:
    type: postgres
    # 连接池大小
    pool_size: 10
    max_overflow: 20
    # 连接超时
    pool_timeout: 30
    # 连接回收
    pool_recycle: 3600
```

### 5.13.2 读写分离

```yaml
# 读写分离配置
outputs:
  read:
    type: postgres
    host: read-replica.company.com
    role: read_only
    
  write:
    type: postgres  
    host: master.company.com
    role: read_write
```

## 5.14 故障排除和调试

### 5.14.1 常见连接问题

```bash
# 查看详细错误信息
dbt debug --verbose

# 检查网络连接
telnet db-host 5432

# 测试数据库连接
psql -h db-host -U username -d database
```

### 5.14.2 连接日志分析

```yaml
# 启用详细日志
outputs:
  dev:
    type: postgres
    # 日志级别
    log_level: debug
    # 连接跟踪
    log_connections: true
    log_disconnections: true
```

## 5.15 本章总结

本章详细介绍了dbt数据源与连接配置的各个方面：

- **数据源定义和管理**：如何声明和使用外部数据表
- **数据库连接配置**：profiles.yml文件的详细配置
- **多环境管理**：开发、测试、生产环境的配置切换
- **安全最佳实践**：密码管理、网络安全性
- **高级特性**：连接池、读写分离、监控告警

通过本章学习，您应该能够：
- 正确配置dbt与各种数据库的连接
- 管理多环境的数据源配置
- 实施安全的数据连接策略
- 监控和调试数据库连接问题
- 优化连接性能和提高可靠性

---

**下一步**：[第6章：dbt最佳实践与项目结构](./6-dbt最佳实践与项目结构.md)