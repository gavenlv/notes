-- 动态SQL生成宏集合
-- 提供动态生成SQL语句的功能

{% macro generate_select_statement(table_name, include_columns=[], exclude_columns=[]) %}
  /*
  动态生成SELECT语句
  
  Args:
    table_name: 表名
    include_columns: 包含的字段列表（可选）
    exclude_columns: 排除的字段列表（可选）
    
  Returns:
    完整的SELECT语句
  */
  
  {%- set relation = ref(table_name) -%}
  {%- set columns = adapter.get_columns_in_relation(relation) -%}
  
  select
  {%- for column in columns -%}
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

{% macro apply_where_filters(filters={}) %}
  /*
  动态应用WHERE条件
  
  Args:
    filters: 过滤条件字典 {字段名: 值}
    
  Returns:
    WHERE子句
  */
  
  {%- if filters -%}
    where
    {%- for column, value in filters.items() -%}
      {%- if value is none -%}
        {{ column }} is null
      {%- else -%}
        {{ column }} = '{{ value }}'
      {%- endif -%}
      {%- if not loop.last %} and{% endif -%}
    {%- endfor -%}
  {%- endif -%}
{% endmacro %}

{% macro generate_group_by(group_by_columns) %}
  /*
  动态生成GROUP BY子句
  
  Args:
    group_by_columns: 分组字段列表
    
  Returns:
    GROUP BY子句
  */
  
  {%- if group_by_columns -%}
    group by
    {%- for column in group_by_columns -%}
      {{ column }}{% if not loop.last %},{% endif %}
    {%- endfor -%}
  {%- endif -%}
{% endmacro %}

{% macro generate_order_by(order_by_columns, direction='asc') %}
  /*
  动态生成ORDER BY子句
  
  Args:
    order_by_columns: 排序字段列表
    direction: 排序方向（asc/desc）
    
  Returns:
    ORDER BY子句
  */
  
  {%- if order_by_columns -%}
    order by
    {%- for column in order_by_columns -%}
      {{ column }} {{ direction }}{% if not loop.last %},{% endif %}
    {%- endfor -%}
  {%- endif -%}
{% endmacro %}

{% macro generate_pagination(limit=100, offset=0) %}
  /*
  动态生成分页子句
  
  Args:
    limit: 每页记录数
    offset: 偏移量
    
  Returns:
    分页子句
  */
  
  limit {{ limit }}
  {%- if offset > 0 -%}
    offset {{ offset }}
  {%- endif -%}
{% endmacro %}

{% macro generate_join_clause(left_table, right_table, join_conditions, join_type='inner') %}
  /*
  动态生成JOIN子句
  
  Args:
    left_table: 左表
    right_table: 右表
    join_conditions: 连接条件列表
    join_type: 连接类型（inner/left/right/full）
    
  Returns:
    JOIN子句
  */
  
  {{ join_type }} join {{ ref(right_table) }} on
  {%- for condition in join_conditions -%}
    {{ condition.left_column }} = {{ condition.right_column }}
    {%- if not loop.last %} and{% endif -%}
  {%- endfor -%}
{% endmacro %}

{% macro generate_case_when(case_conditions, else_value=null) %}
  /*
  动态生成CASE WHEN语句
  
  Args:
    case_conditions: 条件列表 [{when: 条件, then: 结果}]
    else_value: ELSE值，默认为null
    
  Returns:
    CASE WHEN语句
  */
  
  case
    {%- for condition in case_conditions -%}
      when {{ condition.when }} then {{ condition.then }}
    {%- endfor -%}
    {%- if else_value is not none -%}
      else {{ else_value }}
    {%- endif -%}
  end
{% endmacro %}

{% macro generate_union_all(queries) %}
  /*
  动态生成UNION ALL语句
  
  Args:
    queries: 查询列表
    
  Returns:
    UNION ALL语句
  */
  
  {%- for query in queries -%}
    {{ query }}
    {%- if not loop.last %} union all{% endif -%}
  {%- endfor -%}
{% endmacro %}

{% macro generate_cte(cte_definitions) %}
  /*
  动态生成CTE定义
  
  Args:
    cte_definitions: CTE定义列表 [{name: CTE名, query: 查询语句}]
    
  Returns:
    CTE定义语句
  */
  
  with
  {%- for cte in cte_definitions -%}
    {{ cte.name }} as (
      {{ cte.query }}
    ){% if not loop.last %},{% endif %}
  {%- endfor -%}
{% endmacro %}

{% macro generate_aggregate_query(
    table_name, 
    group_by_columns, 
    aggregate_columns, 
    filters={}, 
    order_by_columns=[],
    limit=null
) %}
  /*
  动态生成聚合查询
  
  Args:
    table_name: 表名
    group_by_columns: 分组字段
    aggregate_columns: 聚合字段 [{column: 字段, alias: 别名, function: 聚合函数}]
    filters: 过滤条件
    order_by_columns: 排序字段
    limit: 限制记录数
    
  Returns:
    完整的聚合查询语句
  */
  
  select
    {%- for group_col in group_by_columns -%}
      {{ group_col }}{% if not loop.last %},{% endif %}
    {%- endfor -%}
    
    {%- if group_by_columns and aggregate_columns -%},{% endif -%}
    
    {%- for agg_col in aggregate_columns -%}
      {{ agg_col.function }}({{ agg_col.column }}) as {{ agg_col.alias }}
      {%- if not loop.last %},{% endif -%}
    {%- endfor -%}
    
  from {{ ref(table_name) }}
  
  {{ apply_where_filters(filters) }}
  
  {{ generate_group_by(group_by_columns) }}
  
  {%- if order_by_columns -%}
    {{ generate_order_by(order_by_columns) }}
  {%- endif -%}
  
  {%- if limit -%}
    {{ generate_pagination(limit) }}
  {%- endif -%}
{% endmacro %}

{% macro generate_dynamic_column_list(columns, prefix='', suffix='') %}
  /*
  动态生成字段列表
  
  Args:
    columns: 字段列表
    prefix: 字段前缀
    suffix: 字段后缀
    
  Returns:
    字段列表字符串
  */
  
  {%- for column in columns -%}
    {{ prefix }}{{ column }}{{ suffix }}{% if not loop.last %},{% endif %}
  {%- endfor -%}
{% endmacro %}

{% macro generate_insert_statement(target_table, source_table, column_mapping) %}
  /*
  动态生成INSERT语句
  
  Args:
    target_table: 目标表
    source_table: 源表
    column_mapping: 字段映射 {目标字段: 源字段}
    
  Returns:
    INSERT语句
  */
  
  insert into {{ ref(target_table) }} (
    {{ generate_dynamic_column_list(column_mapping.keys()) }}
  )
  select
    {{ generate_dynamic_column_list(column_mapping.values()) }}
  from {{ ref(source_table) }}
{% endmacro %}

{% macro generate_update_statement(table_name, set_values, where_conditions) %}
  /*
  动态生成UPDATE语句
  
  Args:
    table_name: 表名
    set_values: 设置值字典 {字段: 新值}
    where_conditions: WHERE条件
    
  Returns:
    UPDATE语句
  */
  
  update {{ ref(table_name) }}
  set
    {%- for column, value in set_values.items() -%}
      {{ column }} = {{ value }}
      {%- if not loop.last %},{% endif -%}
    {%- endfor -%}
  where {{ where_conditions }}
{% endmacro %}

{% macro generate_delete_statement(table_name, where_conditions) %}
  /*
  动态生成DELETE语句
  
  Args:
    table_name: 表名
    where_conditions: WHERE条件
    
  Returns:
    DELETE语句
  */
  
  delete from {{ ref(table_name) }}
  where {{ where_conditions }}
{% endmacro %}

{% macro generate_window_function(
    function_name, 
    column, 
    partition_by=[], 
    order_by=[], 
    frame_clause=''
) %}
  /*
  动态生成窗口函数
  
  Args:
    function_name: 函数名
    column: 字段
    partition_by: 分区字段
    order_by: 排序字段
    frame_clause: 窗口框架
    
  Returns:
    窗口函数表达式
  */
  
  {{ function_name }}({{ column }}) over (
    {%- if partition_by -%}
      partition by {{ generate_dynamic_column_list(partition_by) }}
    {%- endif -%}
    
    {%- if order_by -%}
      {%- if partition_by %} {% endif -%}order by {{ generate_dynamic_column_list(order_by) }}
    {%- endif -%}
    
    {%- if frame_clause -%}
      {{ frame_clause }}
    {%- endif -%}
  )
{% endmacro %}

{% macro generate_dynamic_model(
    model_name, 
    source_tables, 
    select_columns, 
    join_conditions=[], 
    where_conditions='',
    group_by_columns=[],
    order_by_columns=[]
) %}
  /*
  动态生成完整模型
  
  Args:
    model_name: 模型名
    source_tables: 源表列表
    select_columns: 选择字段
    join_conditions: 连接条件
    where_conditions: WHERE条件
    group_by_columns: 分组字段
    order_by_columns: 排序字段
    
  Returns:
    完整模型定义
  */
  
  {{ config(materialized='table', alias=model_name) }}
  
  with
  {%- for table in source_tables -%}
    {{ table.name }} as (
      select * from {{ ref(table.ref) }}
    ){% if not loop.last %},{% endif %}
  {%- endfor -%}
  
  select
    {{ generate_dynamic_column_list(select_columns) }}
  from {{ source_tables[0].name }}
  
  {%- for join in join_conditions -%}
    {{ generate_join_clause(
        join.left_table, 
        join.right_table, 
        join.conditions, 
        join.type
    ) }}
  {%- endfor -%}
  
  {%- if where_conditions -%}
    where {{ where_conditions }}
  {%- endif -%}
  
  {%- if group_by_columns -%}
    {{ generate_group_by(group_by_columns) }}
  {%- endif -%}
  
  {%- if order_by_columns -%}
    {{ generate_order_by(order_by_columns) }}
  {%- endif -%}
{% endmacro %}

{% macro debug_sql_generation(sql_statement) %}
  /*
  调试SQL生成过程
  
  Args:
    sql_statement: SQL语句
    
  Returns:
    调试信息
  */
  
  {%- set debug_info = {
      'generated_sql': sql_statement,
      'timestamp': current_timestamp(),
      'model': this.name if this else 'unknown'
  } -%}
  
  {{ log("动态SQL生成调试: " ~ debug_info, info=true) }}
  
  {{ sql_statement }}
{% endmacro %}