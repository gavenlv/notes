-- 日期工具宏集合
-- 提供常用的日期处理和格式化功能

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

{% macro date_diff(date1, date2, unit='day') %}
  /*
  计算两个日期的差值
  
  Args:
    date1: 第一个日期
    date2: 第二个日期
    unit: 时间单位（day, month, year）
    
  Returns:
    日期差值表达式
  */
  
  datediff({{ unit }}, {{ date1 }}, {{ date2 }})
{% endmacro %}

{% macro add_days(date_column, days) %}
  /*
  日期加减天数
  
  Args:
    date_column: 日期字段
    days: 要加减的天数
    
  Returns:
    加减后的日期表达式
  */
  
  dateadd('day', {{ days }}, {{ date_column }})
{% endmacro %}

{% macro get_week_start(date_column) %}
  /*
  获取周开始日期（周一）
  
  Args:
    date_column: 日期字段
    
  Returns:
    周开始日期表达式
  */
  
  date_trunc('week', {{ date_column }})
{% endmacro %}

{% macro get_month_start(date_column) %}
  /*
  获取月开始日期
  
  Args:
    date_column: 日期字段
    
  Returns:
    月开始日期表达式
  */
  
  date_trunc('month', {{ date_column }})
{% endmacro %}

{% macro is_weekend(date_column) %}
  /*
  判断是否为周末
  
  Args:
    date_column: 日期字段
    
  Returns:
    布尔表达式（true/false）
  */
  
  dayofweek({{ date_column }}) in (1, 7)  -- 1=周日, 7=周六
{% endmacro %}

{% macro business_days_between(start_date, end_date) %}
  /*
  计算两个日期之间的工作日天数
  
  Args:
    start_date: 开始日期
    end_date: 结束日期
    
  Returns:
    工作日天数计算表达式
  */
  
  {{ date_diff(start_date, end_date, 'day') }} - 
  (floor({{ date_diff(start_date, end_date, 'day') }} / 7) * 2) -
  case 
    when dayofweek({{ start_date }}) = 1 then 1 
    when dayofweek({{ start_date }}) = 7 then 1 
    else 0 
  end +
  case 
    when dayofweek({{ end_date }}) = 1 then 1 
    when dayofweek({{ end_date }}) = 7 then 1 
    else 0 
  end
{% endmacro %}

{% macro age_in_years(birth_date, reference_date=current_date) %}
  /*
  计算年龄（按年）
  
  Args:
    birth_date: 出生日期
    reference_date: 参考日期，默认为当前日期
    
  Returns:
    年龄计算表达式
  */
  
  floor({{ date_diff(birth_date, reference_date, 'day') }} / 365.25)
{% endmacro %}

{% macro fiscal_year(date_column, fiscal_start_month=4) %}
  /*
  获取财年（默认4月为财年开始）
  
  Args:
    date_column: 日期字段
    fiscal_start_month: 财年开始月份，默认为4月
    
  Returns:
    财年表达式
  */
  
  case 
    when month({{ date_column }}) >= {{ fiscal_start_month }}
    then year({{ date_column }})
    else year({{ date_column }}) - 1
  end
{% endmacro %}

{% macro generate_date_series(start_date, end_date, interval='day') %}
  /*
  生成日期序列（CTE格式）
  
  Args:
    start_date: 开始日期
    end_date: 结束日期
    interval: 间隔单位
    
  Returns:
    日期序列CTE
  */
  
  {%- set date_series = [] -%}
  {%- set current_date = start_date -%}
  
  {%- while current_date <= end_date -%}
    {%- do date_series.append(current_date) -%}
    {%- set current_date = "dateadd('" ~ interval ~ "', 1, " ~ current_date ~ ")" -%}
  {%- endwhile -%}
  
  {{ return(date_series) }}
{% endmacro %}