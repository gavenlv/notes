-- 条件聚合宏集合
-- 提供基于条件的聚合计算功能

{% macro conditional_sum(column, condition) %}
  /*
  条件求和
  
  Args:
    column: 数值字段
    condition: 条件表达式
    
  Returns:
    条件求和表达式
  */
  
  sum(case when {{ condition }} then {{ column }} else 0 end)
{% endmacro %}

{% macro conditional_count(column, condition) %}
  /*
  条件计数
  
  Args:
    column: 字段（可为null）
    condition: 条件表达式
    
  Returns:
    条件计数表达式
  */
  
  count(case when {{ condition }} then {{ column }} else null end)
{% endmacro %}

{% macro conditional_avg(column, condition) %}
  /*
  条件平均值
  
  Args:
    column: 数值字段
    condition: 条件表达式
    
  Returns:
    条件平均值表达式
  */
  
  avg(case when {{ condition }} then {{ column }} else null end)
{% endmacro %}

{% macro conditional_min(column, condition) %}
  /*
  条件最小值
  
  Args:
    column: 数值字段
    condition: 条件表达式
    
  Returns:
    条件最小值表达式
  */
  
  min(case when {{ condition }} then {{ column }} else null end)
{% endmacro %}

{% macro conditional_max(column, condition) %}
  /*
  条件最大值
  
  Args:
    column: 数值字段
    condition: 条件表达式
    
  Returns:
    条件最大值表达式
  */
  
  max(case when {{ condition }} then {{ column }} else null end)
{% endmacro %}

{% macro sum_by_category(column, category_column, categories) %}
  /*
  按类别分类求和
  
  Args:
    column: 数值字段
    category_column: 类别字段
    categories: 类别列表
    
  Returns:
    按类别分类的求和表达式列表
  */
  
  {%- for category in categories -%}
    {{ conditional_sum(column, category_column ~ " = '" ~ category ~ "'") }} as {{ category }}_sum{% if not loop.last %},{% endif %}
  {%- endfor -%}
{% endmacro %}

{% macro count_by_category(category_column, categories) %}
  /*
  按类别分类计数
  
  Args:
    category_column: 类别字段
    categories: 类别列表
    
  Returns:
    按类别分类的计数表达式列表
  */
  
  {%- for category in categories -%}
    {{ conditional_count(category_column, category_column ~ " = '" ~ category ~ "'") }} as {{ category }}_count{% if not loop.last %},{% endif %}
  {%- endfor -%}
{% endmacro %}

{% macro running_total(column, partition_by, order_by) %}
  /*
  计算运行总计
  
  Args:
    column: 数值字段
    partition_by: 分区字段
    order_by: 排序字段
    
  Returns:
    运行总计表达式
  */
  
  sum({{ column }}) over (
    partition by {{ partition_by }}
    order by {{ order_by }}
    rows unbounded preceding
  )
{% endmacro %}

{% macro moving_average(column, partition_by, order_by, window_size=7) %}
  /*
  计算移动平均
  
  Args:
    column: 数值字段
    partition_by: 分区字段
    order_by: 排序字段
    window_size: 窗口大小，默认为7
    
  Returns:
    移动平均表达式
  */
  
  avg({{ column }}) over (
    partition by {{ partition_by }}
    order by {{ order_by }}
    rows between {{ window_size - 1 }} preceding and current row
  )
{% endmacro %}

{% macro percent_of_total(column, total_column) %}
  /*
  计算占总数的百分比
  
  Args:
    column: 部分数值
    total_column: 总数数值
    
  Returns:
    百分比表达式
  */
  
  case 
    when {{ total_column }} = 0 then 0
    else ({{ column }} / {{ total_column }} * 100)
  end
{% endmacro %}

{% macro year_over_year_growth(current_value, previous_value) %}
  /*
  计算同比增长率
  
  Args:
    current_value: 当前期数值
    previous_value: 上期数值
    
  Returns:
    同比增长率表达式
  */
  
  case 
    when {{ previous_value }} = 0 then null
    else (({{ current_value }} - {{ previous_value }}) / {{ previous_value }} * 100)
  end
{% endmacro %}

{% macro cumulative_percentage(column, partition_by, order_by) %}
  /*
  计算累积百分比
  
  Args:
    column: 数值字段
    partition_by: 分区字段
    order_by: 排序字段
    
  Returns:
    累积百分比表达式
  */
  
  (sum({{ column }}) over (
    partition by {{ partition_by }}
    order by {{ order_by }}
    rows unbounded preceding
  ) / sum({{ column }}) over (
    partition by {{ partition_by }}
  ) * 100
{% endmacro %}

{% macro rank_within_partition(column, partition_by, order_direction='desc') %}
  /*
  在分区内排名
  
  Args:
    column: 排名依据字段
    partition_by: 分区字段
    order_direction: 排序方向（asc/desc），默认为desc
    
  Returns:
    排名表达式
  */
  
  rank() over (
    partition by {{ partition_by }}
    order by {{ column }} {{ order_direction }}
  )
{% endmacro %}

{% macro percentile_within_partition(column, partition_by, percentile=0.5) %}
  /*
  在分区内计算百分位数
  
  Args:
    column: 数值字段
    partition_by: 分区字段
    percentile: 百分位数，默认为0.5（中位数）
    
  Returns:
    百分位数表达式
  */
  
  percentile_cont({{ percentile }}) within group (
    order by {{ column }}
  ) over (
    partition by {{ partition_by }}
  )
{% endmacro %}

{% macro lag_difference(column, partition_by, order_by, lag_periods=1) %}
  /*
  计算与前期的差值
  
  Args:
    column: 数值字段
    partition_by: 分区字段
    order_by: 排序字段
    lag_periods: 滞后周期数，默认为1
    
  Returns:
    差值表达式
  */
  
  {{ column }} - lag({{ column }}, {{ lag_periods }}) over (
    partition by {{ partition_by }}
    order by {{ order_by }}
  )
{% endmacro %}

{% macro first_value_in_partition(column, partition_by, order_by) %}
  /*
  获取分区内的第一个值
  
  Args:
    column: 数值字段
    partition_by: 分区字段
    order_by: 排序字段
    
  Returns:
    第一个值表达式
  */
  
  first_value({{ column }}) over (
    partition by {{ partition_by }}
    order by {{ order_by }}
    rows unbounded preceding
  )
{% endmacro %}

{% macro last_value_in_partition(column, partition_by, order_by) %}
  /*
  获取分区内的最后一个值
  
  Args:
    column: 数值字段
    partition_by: 分区字段
    order_by: 排序字段
    
  Returns:
    最后一个值表达式
  */
  
  last_value({{ column }}) over (
    partition by {{ partition_by }}
    order by {{ order_by }}
    rows between unbounded preceding and unbounded following
  )
{% endmacro %}

{% macro aggregate_by_time_period(column, time_column, period='month') %}
  /*
  按时间周期聚合
  
  Args:
    column: 数值字段
    time_column: 时间字段
    period: 时间周期（day, week, month, quarter, year）
    
  Returns:
    时间周期聚合表达式
  */
  
  {%- set period_expr = "date_trunc('" ~ period ~ "', " ~ time_column ~ ")" -%}
  
  {{ period_expr }} as {{ period }}_period,
  sum({{ column }}) as {{ column }}_sum
{% endmacro %}

{% macro calculate_growth_rate(current_period, previous_period) %}
  /*
  计算增长率
  
  Args:
    current_period: 当前期数值
    previous_period: 上期数值
    
  Returns:
    增长率表达式
  */
  
  case 
    when {{ previous_period }} = 0 then null
    else (({{ current_period }} - {{ previous_period }}) / {{ previous_period }} * 100)
  end
{% endmacro %}