-- 第6章：dbt最佳实践与项目结构
-- 日期工具宏集合
-- 演示可复用宏的设计和实现最佳实践

{% macro date_diff(date_part, start_date, end_date) -%}
    -- 计算两个日期之间的差值
    -- 参数：date_part - 时间单位（year, month, day等）
    --       start_date - 开始日期
    --       end_date - 结束日期
    
    {%- if target.type == 'postgres' -%}
        DATE_PART('{{ date_part }}', {{ end_date }} - {{ start_date }})
    {%- elif target.type == 'snowflake' -%}
        DATEDIFF('{{ date_part }}', {{ start_date }}, {{ end_date }})
    {%- elif target.type == 'bigquery' -%}
        DATE_DIFF({{ end_date }}, {{ start_date }}, {{ date_part }})
    {%- elif target.type == 'redshift' -%}
        DATEDIFF('{{ date_part }}', {{ start_date }}, {{ end_date }})
    {%- else -%}
        {{ exceptions.raise_compiler_error("Unsupported database type: " ~ target.type) }}
    {%- endif -%}
{%- endmacro %}

{% macro date_trunc(date_part, date_column) -%}
    -- 日期截断函数，兼容多种数据库
    -- 参数：date_part - 时间单位
    --       date_column - 日期字段
    
    {%- if target.type == 'postgres' -%}
        DATE_TRUNC('{{ date_part }}', {{ date_column }})
    {%- elif target.type == 'snowflake' -%}
        DATE_TRUNC('{{ date_part }}', {{ date_column }})
    {%- elif target.type == 'bigquery' -%}
        DATE_TRUNC({{ date_column }}, {{ date_part }})
    {%- elif target.type == 'redshift' -%}
        DATE_TRUNC('{{ date_part }}', {{ date_column }})
    {%- else -%}
        {{ exceptions.raise_compiler_error("Unsupported database type: " ~ target.type) }}
    {%- endif -%}
{%- endmacro %}

{% macro get_current_timestamp() -%}
    -- 获取当前时间戳，兼容多种数据库
    
    {%- if target.type == 'postgres' -%}
        CURRENT_TIMESTAMP
    {%- elif target.type == 'snowflake' -%}
        CURRENT_TIMESTAMP()
    {%- elif target.type == 'bigquery' -%}
        CURRENT_TIMESTAMP()
    {%- elif target.type == 'redshift' -%}
        GETDATE()
    {%- else -%}
        {{ exceptions.raise_compiler_error("Unsupported database type: " ~ target.type) }}
    {%- endif -%}
{%- endmacro %}

{% macro format_date(date_column, format_string) -%}
    -- 日期格式化函数
    -- 参数：date_column - 日期字段
    --       format_string - 格式字符串
    
    {%- if target.type == 'postgres' -%}
        TO_CHAR({{ date_column }}, '{{ format_string }}')
    {%- elif target.type == 'snowflake' -%}
        TO_CHAR({{ date_column }}, '{{ format_string }}')
    {%- elif target.type == 'bigquery' -%}
        FORMAT_DATE('{{ format_string }}', {{ date_column }})
    {%- elif target.type == 'redshift' -%}
        TO_CHAR({{ date_column }}, '{{ format_string }}')
    {%- else -%}
        {{ date_column }}
    {%- endif -%}
{%- endmacro %}

{% macro add_days(date_column, days) -%}
    -- 日期加减函数
    -- 参数：date_column - 日期字段
    --       days - 天数（可为负数）
    
    {%- if target.type == 'postgres' -%}
        {{ date_column }} + INTERVAL '{{ days }} days'
    {%- elif target.type == 'snowflake' -%}
        DATEADD(day, {{ days }}, {{ date_column }})
    {%- elif target.type == 'bigquery' -%}
        DATE_ADD({{ date_column }}, INTERVAL {{ days }} DAY)
    {%- elif target.type == 'redshift' -%}
        DATEADD(day, {{ days }}, {{ date_column }})
    {%- else -%}
        {{ exceptions.raise_compiler_error("Unsupported database type: " ~ target.type) }}
    {%- endif -%}
{%- endmacro %}

{% macro is_weekend(date_column) -%}
    -- 判断是否为周末
    -- 参数：date_column - 日期字段
    
    {%- if target.type == 'postgres' -%}
        EXTRACT(DOW FROM {{ date_column }}) IN (0, 6)
    {%- elif target.type == 'snowflake' -%}
        DAYOFWEEK({{ date_column }}) IN (1, 7)
    {%- elif target.type == 'bigquery' -%}
        EXTRACT(DAYOFWEEK FROM {{ date_column }}) IN (1, 7)
    {%- elif target.type == 'redshift' -%}
        EXTRACT(DOW FROM {{ date_column }}) IN (0, 6)
    {%- else -%}
        {{ exceptions.raise_compiler_error("Unsupported database type: " ~ target.type) }}
    {%- endif -%}
{%- endmacro %}

{% macro get_fiscal_year(date_column, fiscal_start_month=4) -%}
    -- 获取财年
    -- 参数：date_column - 日期字段
    --       fiscal_start_month - 财年开始月份（默认4月）
    
    {%- if target.type in ['postgres', 'snowflake', 'bigquery', 'redshift'] -%}
        CASE 
            WHEN EXTRACT(MONTH FROM {{ date_column }}) >= {{ fiscal_start_month }}
            THEN EXTRACT(YEAR FROM {{ date_column }})
            ELSE EXTRACT(YEAR FROM {{ date_column }}) - 1
        END
    {%- else -%}
        {{ exceptions.raise_compiler_error("Unsupported database type: " ~ target.type) }}
    {%- endif -%}
{%- endmacro %}

{% macro get_quarter(date_column) -%}
    -- 获取季度
    -- 参数：date_column - 日期字段
    
    {%- if target.type in ['postgres', 'snowflake', 'bigquery', 'redshift'] -%}
        EXTRACT(QUARTER FROM {{ date_column }})
    {%- else -%}
        {{ exceptions.raise_compiler_error("Unsupported database type: " ~ target.type) }}
    {%- endif -%}
{%- endmacro %}

{% macro generate_date_series(start_date, end_date, date_part='day') -%}
    -- 生成日期序列
    -- 参数：start_date - 开始日期
    --       end_date - 结束日期
    --       date_part - 时间单位
    
    {%- if target.type == 'postgres' -%}
        SELECT generate_series(
            '{{ start_date }}'::date,
            '{{ end_date }}'::date,
            '1 {{ date_part }}'::interval
        ) as date_value
    {%- elif target.type == 'snowflake' -%}
        SELECT dateadd('{{ date_part }}', row_number() over (order by 1) - 1, '{{ start_date }}') as date_value
        FROM table(generator(rowcount => {{ "datediff('" ~ date_part ~ "', '" ~ start_date ~ "', '" ~ end_date ~ "') + 1" }}))
    {%- elif target.type == 'bigquery' -%}
        SELECT date_add('{{ start_date }}', INTERVAL n DAY) as date_value
        FROM unnest(generate_array(0, date_diff('{{ end_date }}', '{{ start_date }}', DAY))) as n
    {%- else -%}
        {{ exceptions.raise_compiler_error("Date series generation not supported for: " ~ target.type) }}
    {%- endif -%}
{%- endmacro %}