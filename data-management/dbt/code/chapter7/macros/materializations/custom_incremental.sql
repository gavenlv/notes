-- 第7章：自定义增量物料化策略
-- 演示高级增量模型配置和自定义物料化策略

{% macro custom_incremental_strategy(
    unique_key,
    strategy='merge',
    incremental_predicates=None,
    on_schema_change='fail',
    full_refresh=false,
    partitions=None
) %}
  {#-
    自定义增量策略配置宏
    
    参数说明：
    - unique_key: 唯一键字段
    - strategy: 增量策略（merge/delete+insert/append）
    - incremental_predicates: 增量条件谓词
    - on_schema_change: 模式变更处理策略
    - full_refresh: 是否全量刷新
    - partitions: 分区配置
    
    返回：自定义增量配置
  -#}
  
  {{ config(
    materialized='incremental',
    unique_key=unique_key,
    strategy=strategy,
    incremental_predicates=incremental_predicates,
    on_schema_change=on_schema_change,
    full_refresh=full_refresh,
    tags=['custom', 'incremental', 'advanced']
  ) }}
  
  -- 分区配置（如果提供）
  {%- if partitions %}
    {%- for partition in partitions %}
      {{ "-- 分区配置: " ~ partition.field ~ " -> " ~ partition.type }}
    {%- endfor %}
  {%- endif %}
  
  -- 增量逻辑
  SELECT 
    *,
    CURRENT_TIMESTAMP AS _dbt_loaded_at
  FROM {{ this }}
  
  {% if is_incremental() %}
    -- 增量处理逻辑
    WHERE _dbt_loaded_at > (
      SELECT MAX(_dbt_loaded_at) 
      FROM {{ this }}
    )
    
    {%- if incremental_predicates %}
      AND (
        {%- for predicate in incremental_predicates %}
          {{ predicate }}{% if not loop.last %} OR{% endif %}
        {%- endfor %}
      )
    {%- endif %}
  {% endif %}
  
{% endmacro %}

{% macro partitioned_incremental(
    unique_key,
    partition_key,
    partition_type='date',
    retention_days=90,
    strategy='merge'
) %}
  {#-
    分区增量物料化策略
    
    参数说明：
    - unique_key: 唯一键字段
    - partition_key: 分区键字段
    - partition_type: 分区类型（date/range/list）
    - retention_days: 数据保留天数
    - strategy: 增量策略
    
    返回：分区增量配置
  -#}
  
  {{ config(
    materialized='incremental',
    unique_key=unique_key,
    strategy=strategy,
    partitions=[
      {"field": partition_key, "type": partition_type, "granularity": "day"}
    ],
    tags=['partitioned', 'incremental', 'performance']
  ) }}
  
  -- 主查询逻辑
  WITH source_data AS (
    SELECT 
      *,
      {{ partition_key }} AS partition_date,
      CURRENT_TIMESTAMP AS _dbt_loaded_at
    FROM {{ ref('stg_events') }}
    
    {% if is_incremental() %}
      -- 增量条件：只处理最近的数据
      WHERE {{ partition_key }} >= DATEADD(day, -{{ retention_days }}, CURRENT_DATE)
        AND {{ partition_key }} > (
          SELECT COALESCE(MAX({{ partition_key }}), '1900-01-01')
          FROM {{ this }}
        )
    {% endif %}
  )
  
  SELECT * FROM source_data
  
{% endmacro %}

{% macro materialized_view_strategy(
    view_name,
    refresh_schedule='daily',
    enable_auto_refresh=true,
    query_rewrite=true
) %}
  {#-
    物化视图策略
    
    参数说明：
    - view_name: 视图名称
    - refresh_schedule: 刷新计划
    - enable_auto_refresh: 是否自动刷新
    - query_rewrite: 是否启用查询重写
    
    返回：物化视图配置
  -#}
  
  {{ config(
    materialized='view',
    persist_docs={"relation": true, "columns": true},
    tags=['materialized-view', 'performance']
  ) }}
  
  -- 物化视图配置（数据库特定）
  {%- if target.type == 'snowflake' %}
    {{ "-- Snowflake物化视图配置" }}
    {{ "CREATE OR REPLACE MATERIALIZED VIEW " ~ view_name }}
    {{ "AS" }}
  {%- elif target.type == 'bigquery' %}
    {{ "-- BigQuery物化视图配置" }}
    {{ "CREATE OR REPLACE MATERIALIZED VIEW " ~ view_name }}
    {{ "OPTIONS(enable_refresh=" ~ enable_auto_refresh ~ ", refresh_interval_minutes=1440)" }}
    {{ "AS" }}
  {%- elif target.type == 'redshift' %}
    {{ "-- Redshift物化视图配置" }}
    {{ "CREATE MATERIALIZED VIEW " ~ view_name }}
    {{ "AUTO REFRESH " ~ enable_auto_refresh }}
    {{ "AS" }}
  {%- else %}
    {{ "-- 标准视图（不支持物化视图）" }}
    {{ "CREATE OR REPLACE VIEW " ~ view_name ~ " AS" }}
  {%- endif %}
  
  -- 视图查询逻辑
  SELECT 
    customer_id,
    COUNT(*) AS total_orders,
    SUM(order_amount) AS total_amount,
    AVG(order_amount) AS avg_amount,
    MAX(order_date) AS last_order_date
  FROM {{ ref('fct_orders') }}
  GROUP BY customer_id
  
{% endmacro %}

{% macro incremental_with_archiving(
    unique_key,
    archive_table,
    archive_condition,
    retention_period='90 days'
) %}
  {#-
    带归档功能的增量策略
    
    参数说明：
    - unique_key: 唯一键字段
    - archive_table: 归档表名称
    - archive_condition: 归档条件
    - retention_period: 保留期限
    
    返回：带归档的增量配置
  -#}
  
  {{ config(
    materialized='incremental',
    unique_key=unique_key,
    strategy='merge',
    pre_hook=[
      "{{ archive_old_data(this, archive_table, archive_condition) }}"
    ],
    tags=['incremental', 'archiving', 'data-management']
  ) }}
  
  -- 归档旧数据的宏
  {% macro archive_old_data(source_table, archive_table, condition) %}
    {% if is_incremental() %}
      INSERT INTO {{ archive_table }}
      SELECT * FROM {{ source_table }}
      WHERE {{ condition }}
        AND _dbt_loaded_at < DATEADD(day, -{{ retention_period | replace(' days', '') }}, CURRENT_DATE)
      
      DELETE FROM {{ source_table }}
      WHERE {{ condition }}
        AND _dbt_loaded_at < DATEADD(day, -{{ retention_period | replace(' days', '') }}, CURRENT_DATE)
    {% endif %}
  {% endmacro %}
  
  -- 主查询逻辑
  SELECT 
    *,
    CURRENT_TIMESTAMP AS _dbt_loaded_at
  FROM {{ ref('stg_events') }}
  
  {% if is_incremental() %}
    WHERE _dbt_loaded_at > (
      SELECT MAX(_dbt_loaded_at) 
      FROM {{ this }}
    )
  {% endif %}
  
{% endmacro %}

{% macro custom_table_materialization(
    table_type='standard',
    compression=true,
    clustering_keys=None,
    distribution_style='even',
    sort_keys=None
) %}
  {#-
    自定义表物料化策略
    
    参数说明：
    - table_type: 表类型（standard/optimized/analytical）
    - compression: 是否启用压缩
    - clustering_keys: 聚类键
    - distribution_style: 分布样式
    - sort_keys: 排序键
    
    返回：自定义表配置
  -#}
  
  {{ config(
    materialized='table',
    persist_docs={"relation": true, "columns": true},
    tags=['custom-table', table_type]
  ) }}
  
  -- 表优化配置
  {%- if target.type == 'snowflake' %}
    {{ "-- Snowflake表优化" }}
    {%- if clustering_keys %}
      {{ "CLUSTER BY (" ~ clustering_keys | join(', ') ~ ")" }}
    {%- endif %}
    
  {%- elif target.type == 'bigquery' %}
    {{ "-- BigQuery表优化" }}
    {%- if clustering_keys %}
      {{ "CLUSTER BY " ~ clustering_keys | join(', ') }}
    {%- endif %}
    {%- if sort_keys %}
      {{ "OPTIONS(sort_keys=[" ~ sort_keys | join(', ') ~ "])" }}
    {%- endif %}
    
  {%- elif target.type == 'redshift' %}
    {{ "-- Redshift表优化" }}
    {%- if distribution_style == 'key' and clustering_keys %}
      {{ "DISTKEY (" ~ clustering_keys[0] ~ ")" }}
    {%- endif %}
    {%- if sort_keys %}
      {{ "SORTKEY (" ~ sort_keys | join(', ') ~ ")" }}
    {%- endif %}
    
  {%- endif %}
  
  -- 压缩配置
  {%- if compression %}
    {{ "-- 启用数据压缩" }}
  {%- endif %}
  
  -- 主查询逻辑
  SELECT 
    *,
    CASE 
      WHEN table_type = 'optimized' THEN 'OPTIMIZED'
      WHEN table_type = 'analytical' THEN 'ANALYTICAL'
      ELSE 'STANDARD'
    END AS table_configuration
  FROM {{ ref('base_data') }}
  
{% endmacro %}

{% macro incremental_with_quality_checks(
    unique_key,
    quality_checks=None,
    error_threshold=0.01
) %}
  {#-
    带质量检查的增量策略
    
    参数说明：
    - unique_key: 唯一键字段
    - quality_checks: 质量检查规则
    - error_threshold: 错误阈值
    
    返回：带质量检查的增量配置
  -#}
  
  {{ config(
    materialized='incremental',
    unique_key=unique_key,
    strategy='merge',
    pre_hook=[
      "{{ validate_data_quality(quality_checks, error_threshold) }}"
    ],
    post_hook=[
      "{{ log_quality_metrics(this.name) }}"
    ],
    tags=['incremental', 'quality', 'validation']
  ) }}
  
  -- 数据质量验证宏
  {% macro validate_data_quality(checks, threshold) %}
    {% if checks %}
      {% for check in checks %}
        -- 执行质量检查: {{ check.name }}
        {%- set check_sql %}
          SELECT 
            COUNT(*) as total_rows,
            SUM(CASE WHEN {{ check.condition }} THEN 1 ELSE 0 END) as valid_rows
          FROM {{ this }}
        {%- endset %}
        
        {%- set result = run_query(check_sql) %}
        
        {%- if result and result[0][0] > 0 %}
          {%- set error_rate = (result[0][0] - result[0][1]) / result[0][0] %}
          
          {%- if error_rate > threshold %}
            {{ "-- 质量检查失败: " ~ check.name ~ " 错误率: " ~ error_rate }}
            {{ "RAISE EXCEPTION '数据质量检查失败: " ~ check.name ~ "'" }}
          {%- endif %}
        {%- endif %}
      {% endfor %}
    {% endif %}
  {% endmacro %}
  
  -- 质量指标日志宏
  {% macro log_quality_metrics(model_name) %}
    INSERT INTO dbt_quality_metrics (
      model_name, check_time, total_rows, valid_rows, error_rate
    )
    SELECT 
      '{{ model_name }}',
      CURRENT_TIMESTAMP,
      COUNT(*),
      SUM(CASE WHEN quality_check = 'PASS' THEN 1 ELSE 0 END),
      (COUNT(*) - SUM(CASE WHEN quality_check = 'PASS' THEN 1 ELSE 0 END)) / COUNT(*)
    FROM {{ this }}
  {% endmacro %}
  
  -- 主查询逻辑
  SELECT 
    *,
    CASE 
      WHEN data_quality_score > 0.9 THEN 'PASS'
      ELSE 'FAIL'
    END AS quality_check
  FROM {{ ref('stg_events') }}
  
  {% if is_incremental() %}
    WHERE _dbt_loaded_at > (
      SELECT MAX(_dbt_loaded_at) 
      FROM {{ this }}
    )
  {% endif %}
  
{% endmacro %}

-- 使用示例和文档
{##
  自定义物料化策略示例说明：
  
  1. 自定义增量策略：
     提供灵活的增量配置选项
     
     示例用法：
     {{ custom_incremental_strategy(
         unique_key='id',
         strategy='merge',
         incremental_predicates=['updated_at > (SELECT MAX(updated_at) FROM {{ this }})']
     ) }}
  
  2. 分区增量策略：
     结合分区技术优化增量性能
     
  3. 物化视图策略：
     利用数据库物化视图提升查询性能
     
  4. 带归档的增量策略：
     自动归档旧数据，保持表大小可控
     
  5. 自定义表物料化：
     根据数据库类型优化表结构
     
  6. 带质量检查的增量策略：
     在增量处理过程中进行数据质量验证
  
  最佳实践：
  - 根据数据特性和查询模式选择合适的策略
  - 考虑数据保留和归档需求
  - 实施数据质量检查
  - 监控性能指标并优化配置
  - 定期审查和调整策略
##}