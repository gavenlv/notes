-- 第7章：动态SQL生成器宏
-- 演示高级宏开发中的动态SQL生成技术

{% macro generate_dynamic_query(
    base_table,
    select_columns=None,
    where_conditions=None,
    group_by_columns=None,
    order_by_columns=None,
    limit_count=None,
    distinct_flag=false
) %}
  {#-
    动态SQL查询生成器
    
    参数说明：
    - base_table: 基础表名
    - select_columns: 选择列列表（可选，默认所有列）
    - where_conditions: WHERE条件列表（可选）
    - group_by_columns: GROUP BY列列表（可选）
    - order_by_columns: ORDER BY列列表（可选）
    - limit_count: 限制行数（可选）
    - distinct_flag: 是否使用DISTINCT（默认false）
    
    返回：动态生成的SQL查询
  -#}
  
  -- 构建SELECT子句
  {%- set select_clause -%}
    SELECT
    {%- if distinct_flag %} DISTINCT{%- endif %}
    {%- if select_columns %}
      {%- for column in select_columns %}
        {{ column }}{% if not loop.last %},{% endif %}
      {%- endfor %}
    {%- else %}
      *
    {%- endif %}
  {%- endset -%}
  
  -- 构建FROM子句
  {%- set from_clause -%}
    FROM {{ base_table }}
  {%- endset -%}
  
  -- 构建WHERE子句
  {%- set where_clause -%}
    {%- if where_conditions %}
      WHERE
      {%- for condition in where_conditions %}
        {{ condition }}{% if not loop.last %} AND{% endif %}
      {%- endfor %}
    {%- endif %}
  {%- endset -%}
  
  -- 构建GROUP BY子句
  {%- set group_by_clause -%}
    {%- if group_by_columns %}
      GROUP BY
      {%- for column in group_by_columns %}
        {{ column }}{% if not loop.last %},{% endif %}
      {%- endfor %}
    {%- endif %}
  {%- endset -%}
  
  -- 构建ORDER BY子句
  {%- set order_by_clause -%}
    {%- if order_by_columns %}
      ORDER BY
      {%- for column in order_by_columns %}
        {{ column }}{% if not loop.last %},{% endif %}
      {%- endfor %}
    {%- endif %}
  {%- endset -%}
  
  -- 构建LIMIT子句
  {%- set limit_clause -%}
    {%- if limit_count %}
      LIMIT {{ limit_count }}
    {%- endif %}
  {%- endset -%}
  
  -- 组合完整的SQL查询
  {{ select_clause }}
  {{ from_clause }}
  {{ where_clause }}
  {{ group_by_clause }}
  {{ order_by_clause }}
  {{ limit_clause }}
  
{% endmacro %}

{% macro recursive_cte_generator(
    cte_name,
    base_query,
    recursive_query,
    anchor_columns,
    recursive_columns,
    max_depth=100
) %}
  {#-
    递归CTE生成器
    
    参数说明：
    - cte_name: CTE名称
    - base_query: 基础查询（锚点部分）
    - recursive_query: 递归查询部分
    - anchor_columns: 锚点查询返回的列
    - recursive_columns: 递归查询返回的列
    - max_depth: 最大递归深度（默认100）
    
    返回：递归CTE查询
  -#}
  
  WITH RECURSIVE {{ cte_name }} AS (
    -- 锚点部分
    {{ base_query }}
    
    UNION ALL
    
    -- 递归部分
    SELECT
      {%- for column in recursive_columns %}
        {{ column }}{% if not loop.last %},{% endif %}
      {%- endfor %}
    FROM {{ cte_name }}
    WHERE depth < {{ max_depth }}
      AND {{ recursive_query }}
  )
  
  SELECT * FROM {{ cte_name }}
  
{% endmacro %}

{% macro dynamic_pivot_table(
    source_table,
    pivot_column,
    value_column,
    aggregate_function='SUM',
    where_conditions=None
) %}
  {#-
    动态透视表生成器
    
    参数说明：
    - source_table: 源表
    - pivot_column: 透视列
    - value_column: 值列
    - aggregate_function: 聚合函数（默认SUM）
    - where_conditions: 过滤条件（可选）
    
    返回：动态生成的透视表查询
  -#}
  
  {%- set get_distinct_values_sql -%}
    SELECT DISTINCT {{ pivot_column }} 
    FROM {{ source_table }}
    {%- if where_conditions %}
      WHERE
      {%- for condition in where_conditions %}
        {{ condition }}{% if not loop.last %} AND{% endif %}
      {%- endfor %}
    {%- endif %}
    ORDER BY {{ pivot_column }}
  {%- endset -%}
  
  {%- set distinct_values = run_query(get_distinct_values_sql) -%}
  
  {%- if distinct_values -%}
    SELECT
      -- 非透视列（需要手动指定）
      id,
      category,
      
      -- 动态透视列
      {%- for row in distinct_values %}
        {{ aggregate_function }}(
          CASE WHEN {{ pivot_column }} = '{{ row[0] }}' 
               THEN {{ value_column }} 
               ELSE NULL 
          END
        ) AS {{ pivot_column }}_{{ row[0] | replace(" ", "_") | lower }}{% if not loop.last %},{% endif %}
      {%- endfor %}
      
    FROM {{ source_table }}
    {%- if where_conditions %}
      WHERE
      {%- for condition in where_conditions %}
        {{ condition }}{% if not loop.last %} AND{% endif %}
      {%- endfor %}
    {%- endif %}
    GROUP BY id, category
    
  {%- else -%}
    -- 如果没有数据，返回空结果
    SELECT NULL AS no_data
    FROM {{ source_table }}
    WHERE 1=0
  {%- endif %}
  
{% endmacro %}

{% macro conditional_materialization(
    model_name,
    materialization_type='table',
    conditions=None
) %}
  {#-
    条件物料化策略
    
    参数说明：
    - model_name: 模型名称
    - materialization_type: 物料化类型
    - conditions: 条件列表
    
    返回：条件物料化配置
  -#}
  
  {%- set should_materialize = true -%}
  
  -- 检查条件
  {%- if conditions %}
    {%- for condition in conditions %}
      {%- if not condition %}
        {%- set should_materialize = false -%}
      {%- endif %}
    {%- endfor %}
  {%- endif %}
  
  {%- if should_materialize %}
    {{ config(
      materialized=materialization_type,
      tags=['conditional', 'dynamic']
    ) }}
  {%- else %}
    {{ config(
      materialized='ephemeral',
      tags=['conditional', 'skipped']
    ) }}
  {%- endif %}
  
  -- 模型查询逻辑
  SELECT * FROM {{ ref(model_name) }}
  
{% endmacro %}

{% macro template_inheritance(base_model, extensions=None) %}
  {#-
    模板继承宏
    
    参数说明：
    - base_model: 基础模型
    - extensions: 扩展配置
    
    返回：继承后的模型
  -#}
  
  -- 基础配置继承
  {{ config(
    materialized=base_model.config.get('materialized', 'table'),
    tags=base_model.config.get('tags', []) + ['inherited']
  ) }}
  
  -- 基础查询
  WITH base_data AS (
    SELECT * FROM {{ ref(base_model.name) }}
  )
  
  -- 扩展处理
  {%- if extensions %}
    , extended_data AS (
      SELECT
        b.*,
        {%- for extension in extensions %}
          {{ extension.expression }} AS {{ extension.column_name }}{% if not loop.last %},{% endif %}
        {%- endfor %}
      FROM base_data b
    )
    
    SELECT * FROM extended_data
    
  {%- else %}
    SELECT * FROM base_data
  {%- endif %}
  
{% endmacro %}

{% macro macro_package_loader(package_name, macro_names=None) %}
  {#-
    宏包加载器
    
    参数说明：
    - package_name: 包名称
    - macro_names: 需要加载的宏名称列表
    
    返回：宏包加载配置
  -#}
  
  {%- if macro_names %}
    -- 选择性加载宏
    {%- for macro_name in macro_names %}
      {%- set macro_ref = package_name ~ "." ~ macro_name %}
      {{ "-- 加载宏: " ~ macro_ref }}
    {%- endfor %}
  {%- else %}
    -- 加载整个包
    {{ "-- 加载宏包: " ~ package_name }}
  {%- endif %}
  
  -- 返回加载状态
  SELECT 
    'package_loaded' AS status,
    '{{ package_name }}' AS package_name,
    CURRENT_TIMESTAMP AS load_time
  
{% endmacro %}

-- 使用示例和文档
{##
  高级宏开发示例说明：
  
  1. 动态SQL生成器：
     适用于需要根据参数动态构建查询的场景
     
     示例用法：
     {{ generate_dynamic_query(
         base_table='customers',
         select_columns=['id', 'name', 'email'],
         where_conditions=['status = \'active\'', 'created_at > \'2023-01-01\''],
         order_by_columns=['created_at DESC']
     ) }}
  
  2. 递归CTE生成器：
     适用于层次结构数据（如组织架构、分类树）
     
  3. 动态透视表：
     适用于需要将行转列的报表场景
     
  4. 条件物料化：
     根据条件动态决定模型物料化策略
     
  5. 模板继承：
     实现模型配置和逻辑的复用
     
  6. 宏包加载器：
     管理复杂的宏依赖关系
  
  最佳实践：
  - 保持宏的单一职责原则
  - 提供清晰的参数文档
  - 处理边界条件和错误情况
  - 进行充分的测试
##}