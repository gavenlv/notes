-- 字符串工具宏集合
-- 提供常用的字符串处理和格式化功能

{% macro trim_string(column) %}
  /*
  去除字符串两端空格
  
  Args:
    column: 字符串字段
    
  Returns:
    去除空格后的字符串表达式
  */
  
  trim({{ column }})
{% endmacro %}

{% macro substring(column, start, length) %}
  /*
  截取子字符串
  
  Args:
    column: 字符串字段
    start: 开始位置
    length: 截取长度
    
  Returns:
    子字符串表达式
  */
  
  substring({{ column }}, {{ start }}, {{ length }})
{% endmacro %}

{% macro concat_strings(strings, separator='') %}
  /*
  连接多个字符串
  
  Args:
    strings: 字符串列表
    separator: 分隔符，默认为空
    
  Returns:
    连接后的字符串表达式
  */
  
  {%- if strings is string -%}
    {{ strings }}
  {%- else -%}
    {%- for str in strings -%}
      {{ str }}{% if not loop.last %} || '{{ separator }}' || {% endif %}
    {%- endfor -%}
  {%- endif -%}
{% endmacro %}

{% macro replace_string(column, old_str, new_str) %}
  /*
  替换字符串
  
  Args:
    column: 字符串字段
    old_str: 要替换的字符串
    new_str: 替换后的字符串
    
  Returns:
    替换后的字符串表达式
  */
  
  replace({{ column }}, '{{ old_str }}', '{{ new_str }}')
{% endmacro %}

{% macro upper_case(column) %}
  /*
  转换为大写
  
  Args:
    column: 字符串字段
    
  Returns:
    大写字符串表达式
  */
  
  upper({{ column }})
{% endmacro %}

{% macro lower_case(column) %}
  /*
  转换为小写
  
  Args:
    column: 字符串字段
    
  Returns:
    小写字符串表达式
  */
  
  lower({{ column }})
{% endmacro %}

{% macro proper_case(column) %}
  /*
  转换为首字母大写
  
  Args:
    column: 字符串字段
    
  Returns:
    首字母大写字符串表达式
  */
  
  initcap({{ column }})
{% endmacro %}

{% macro string_length(column) %}
  /*
  计算字符串长度
  
  Args:
    column: 字符串字段
    
  Returns:
    字符串长度表达式
  */
  
  length({{ column }})
{% endmacro %}

{% macro extract_email_domain(email_column) %}
  /*
  提取邮箱域名
  
  Args:
    email_column: 邮箱字段
    
  Returns:
    邮箱域名表达式
  */
  
  split_part({{ email_column }}, '@', 2)
{% endmacro %}

{% macro mask_string(column, visible_chars=4, mask_char='*') %}
  /*
  字符串脱敏（保留前几个字符）
  
  Args:
    column: 字符串字段
    visible_chars: 可见字符数，默认为4
    mask_char: 脱敏字符，默认为*
    
  Returns:
    脱敏后的字符串表达式
  */
  
  case 
    when {{ string_length(column) }} <= {{ visible_chars }}
    then {{ column }}
    else 
      {{ substring(column, 1, visible_chars) }} || 
      repeat('{{ mask_char }}', {{ string_length(column) }} - {{ visible_chars }})
  end
{% endmacro %}

{% macro normalize_phone(phone_column, country_code='+86') %}
  /*
  标准化电话号码
  
  Args:
    phone_column: 电话号码字段
    country_code: 国家代码，默认为+86
    
  Returns:
    标准化后的电话号码表达式
  */
  
  case 
    when {{ phone_column }} is null then null
    when {{ phone_column }} like '{{ country_code }}%' then {{ phone_column }}
    when {{ phone_column }} like '0%' then '{{ country_code }}' || {{ substring(phone_column, 2) }}
    else '{{ country_code }}' || {{ replace_string(phone_column, '-', '') }}
  end
{% endmacro %}

{% macro generate_random_string(length=10, chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') %}
  /*
  生成随机字符串（用于测试数据）
  
  Args:
    length: 字符串长度，默认为10
    chars: 字符集，默认为字母数字
    
  Returns:
    随机字符串生成表达式
  */
  
  array_to_string(
    array(
      select substr('{{ chars }}', floor(random() * {{ string_length(chars) }}) + 1, 1)
      from generate_series(1, {{ length }})
    ),
    ''
  )
{% endmacro %}

{% macro parse_json_field(json_column, field_path) %}
  /*
  解析JSON字段
  
  Args:
    json_column: JSON字段
    field_path: 字段路径（如 'user.name'）
    
  Returns:
    JSON字段解析表达式
  */
  
  {%- set path_parts = field_path.split('.') -%}
  {%- set json_expr = json_column -%}
  
  {%- for part in path_parts -%}
    {%- set json_expr = json_expr ~ "['" ~ part ~ "']" -%}
  {%- endfor -%}
  
  {{ json_expr }}
{% endmacro %}

{% macro validate_email_format(email_column) %}
  /*
  验证邮箱格式
  
  Args:
    email_column: 邮箱字段
    
  Returns:
    邮箱格式验证表达式
  */
  
  {{ email_column }} ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
{% endmacro %}

{% macro extract_numbers_from_string(column) %}
  /*
  从字符串中提取数字
  
  Args:
    column: 字符串字段
    
  Returns:
    提取的数字表达式
  */
  
  regexp_replace({{ column }}, '[^0-9]', '', 'g')
{% endmacro %}

{% macro coalesce_strings(columns, default_value='') %}
  /*
  多个字符串字段的COALESCE
  
  Args:
    columns: 字符串字段列表
    default_value: 默认值，默认为空字符串
    
  Returns:
    COALESCE表达式
  */
  
  coalesce(
    {%- for col in columns -%}
      {{ col }}{% if not loop.last %}, {% endif %}
    {%- endfor -%},
    '{{ default_value }}'
  )
{% endmacro %}