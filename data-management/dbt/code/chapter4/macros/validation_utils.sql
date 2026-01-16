-- 验证工具宏集合
-- 提供数据验证和错误处理功能

{% macro validate_not_null(column, custom_message='') %}
  /*
  验证字段不为空
  
  Args:
    column: 字段名
    custom_message: 自定义错误消息
    
  Returns:
    验证表达式
  */
  
  {%- set message = custom_message if custom_message else column ~ " cannot be null" -%}
  
  case 
    when {{ column }} is null then
      {{ exceptions.raise_compiler_error(message) }}
    else {{ column }}
  end
{% endmacro %}

{% macro validate_numeric_range(column, min_value, max_value, custom_message='') %}
  /*
  验证数值范围
  
  Args:
    column: 数值字段
    min_value: 最小值
    max_value: 最大值
    custom_message: 自定义错误消息
    
  Returns:
    验证表达式
  */
  
  {%- set message = custom_message if custom_message else column ~ " must be between " ~ min_value ~ " and " ~ max_value -%}
  
  case 
    when {{ column }} < {{ min_value }} or {{ column }} > {{ max_value }} then
      {{ exceptions.raise_compiler_error(message) }}
    else {{ column }}
  end
{% endmacro %}

{% macro validate_string_length(column, min_length=0, max_length=null, custom_message='') %}
  /*
  验证字符串长度
  
  Args:
    column: 字符串字段
    min_length: 最小长度
    max_length: 最大长度（可选）
    custom_message: 自定义错误消息
    
  Returns:
    验证表达式
  */
  
  {%- set message = custom_message if custom_message else column ~ " length validation failed" -%}
  
  case 
    when length({{ column }}) < {{ min_length }} then
      {{ exceptions.raise_compiler_error(message) }}
    {%- if max_length -%}
    when length({{ column }}) > {{ max_length }} then
      {{ exceptions.raise_compiler_error(message) }}
    {%- endif -%}
    else {{ column }}
  end
{% endmacro %}

{% macro validate_email_format(column, custom_message='') %}
  /*
  验证邮箱格式
  
  Args:
    column: 邮箱字段
    custom_message: 自定义错误消息
    
  Returns:
    验证表达式
  */
  
  {%- set message = custom_message if custom_message else column ~ " has invalid email format" -%}
  
  case 
    when {{ column }} !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$' then
      {{ exceptions.raise_compiler_error(message) }}
    else {{ column }}
  end
{% endmacro %}

{% macro validate_phone_format(column, country_code='+86', custom_message='') %}
  /*
  验证电话号码格式
  
  Args:
    column: 电话字段
    country_code: 国家代码
    custom_message: 自定义错误消息
    
  Returns:
    验证表达式
  */
  
  {%- set message = custom_message if custom_message else column ~ " has invalid phone format" -%}
  
  case 
    when {{ column }} !~ '^\\+?[0-9]{10,15}$' then
      {{ exceptions.raise_compiler_error(message) }}
    else {{ column }}
  end
{% endmacro %}

{% macro validate_date_range(date_column, start_date, end_date, custom_message='') %}
  /*
  验证日期范围
  
  Args:
    date_column: 日期字段
    start_date: 开始日期
    end_date: 结束日期
    custom_message: 自定义错误消息
    
  Returns:
    验证表达式
  */
  
  {%- set message = custom_message if custom_message else date_column ~ " must be between " ~ start_date ~ " and " ~ end_date -%}
  
  case 
    when {{ date_column }} < '{{ start_date }}' or {{ date_column }} > '{{ end_date }}' then
      {{ exceptions.raise_compiler_error(message) }}
    else {{ date_column }}
  end
{% endmacro %}

{% macro validate_enum_values(column, allowed_values, custom_message='') %}
  /*
  验证枚举值
  
  Args:
    column: 字段名
    allowed_values: 允许的值列表
    custom_message: 自定义错误消息
    
  Returns:
    验证表达式
  */
  
  {%- set message = custom_message if custom_message else column ~ " must be one of: " ~ allowed_values|join(', ') -%}
  
  case 
    when {{ column }} not in (
      {%- for value in allowed_values -%}
        '{{ value }}'{% if not loop.last %},{% endif %}
      {%- endfor -%}
    ) then
      {{ exceptions.raise_compiler_error(message) }}
    else {{ column }}
  end
{% endmacro %}

{% macro validate_regex_pattern(column, pattern, custom_message='') %}
  /*
  使用正则表达式验证
  
  Args:
    column: 字段名
    pattern: 正则表达式模式
    custom_message: 自定义错误消息
    
  Returns:
    验证表达式
  */
  
  {%- set message = custom_message if custom_message else column ~ " does not match pattern: " ~ pattern -%}
  
  case 
    when {{ column }} !~ '{{ pattern }}' then
      {{ exceptions.raise_compiler_error(message) }}
    else {{ column }}
  end
{% endmacro %}

{% macro validate_unique_constraint(columns, table_name, custom_message='') %}
  /*
  验证唯一性约束
  
  Args:
    columns: 字段列表
    table_name: 表名
    custom_message: 自定义错误消息
    
  Returns:
    验证表达式
  */
  
  {%- set message = custom_message if custom_message else "Duplicate values found for columns: " ~ columns|join(', ') -%}
  
  {%- set column_list = columns|join(', ') -%}
  
  case 
    when (
      select count(*) 
      from {{ ref(table_name) }} t2 
      where 
        {%- for col in columns -%}
          t2.{{ col }} = t1.{{ col }}
          {%- if not loop.last %} and {% endif -%}
        {%- endfor -%}
    ) > 1 then
      {{ exceptions.raise_compiler_error(message) }}
    else 1
  end
{% endmacro %}

{% macro validate_foreign_key(local_column, foreign_table, foreign_column, custom_message='') %}
  /*
  验证外键约束
  
  Args:
    local_column: 本地字段
    foreign_table: 外键表
    foreign_column: 外键字段
    custom_message: 自定义错误消息
    
  Returns:
    验证表达式
  */
  
  {%- set message = custom_message if custom_message else "Foreign key violation: " ~ local_column ~ " not found in " ~ foreign_table ~ "." ~ foreign_column -%}
  
  case 
    when not exists (
      select 1 
      from {{ ref(foreign_table) }} f 
      where f.{{ foreign_column }} = t.{{ local_column }}
    ) then
      {{ exceptions.raise_compiler_error(message) }}
    else 1
  end
{% endmacro %}

{% macro validate_data_quality(column, rules) %}
  /*
  综合数据质量验证
  
  Args:
    column: 字段名
    rules: 验证规则列表 [{type: 规则类型, params: 参数}]
    
  Returns:
    验证结果
  */
  
  {%- for rule in rules -%}
    {%- if rule.type == 'not_null' -%}
      {{ validate_not_null(column, rule.params.message) }}
    {%- elif rule.type == 'numeric_range' -%}
      {{ validate_numeric_range(column, rule.params.min, rule.params.max, rule.params.message) }}
    {%- elif rule.type == 'string_length' -%}
      {{ validate_string_length(column, rule.params.min, rule.params.max, rule.params.message) }}
    {%- elif rule.type == 'email' -%}
      {{ validate_email_format(column, rule.params.message) }}
    {%- elif rule.type == 'enum' -%}
      {{ validate_enum_values(column, rule.params.values, rule.params.message) }}
    {%- elif rule.type == 'regex' -%}
      {{ validate_regex_pattern(column, rule.params.pattern, rule.params.message) }}
    {%- endif -%}
  {%- endfor -%}
{% endmacro %}

{% macro safe_divide(numerator, denominator, default_value=null) %}
  /*
  安全除法（避免除零错误）
  
  Args:
    numerator: 分子
    denominator: 分母
    default_value: 默认值（当分母为0时返回）
    
  Returns:
    除法结果
  */
  
  case 
    when {{ denominator }} = 0 then {{ default_value }}
    else {{ numerator }} / {{ denominator }}
  end
{% endmacro %}

{% macro coalesce_with_default(column, default_value) %}
  /*
  带默认值的COALESCE
  
  Args:
    column: 字段名
    default_value: 默认值
    
  Returns:
    COALESCE表达式
  */
  
  coalesce({{ column }}, {{ default_value }})
{% endmacro %}

{% macro validate_and_transform(column, transformation, validation_rules) %}
  /*
  验证并转换数据
  
  Args:
    column: 字段名
    transformation: 转换函数
    validation_rules: 验证规则
    
  Returns:
    转换后的值
  */
  
  {%- set transformed_value = transformation(column) -%}
  
  {{ validate_data_quality(transformed_value, validation_rules) }}
  
  {{ transformed_value }}
{% endmacro %}

{% macro log_validation_errors(column, validation_type, error_count) %}
  /*
  记录验证错误日志
  
  Args:
    column: 字段名
    validation_type: 验证类型
    error_count: 错误数量
    
  Returns:
    日志记录
  */
  
  {%- if error_count > 0 -%}
    {{ log("验证错误 - 字段: " ~ column ~ ", 类型: " ~ validation_type ~ ", 错误数: " ~ error_count, info=true) }}
  {%- endif -%}
{% endmacro %}

{% macro create_validation_summary(validations) %}
  /*
  创建验证摘要
  
  Args:
    validations: 验证结果列表 [{field: 字段, type: 类型, passed: 是否通过, errors: 错误数}]
    
  Returns:
    验证摘要
  */
  
  {%- set summary = {
      'total_validations': validations|length,
      'passed_validations': validations|selectattr('passed')|list|length,
      'failed_validations': validations|rejectattr('passed')|list|length,
      'total_errors': validations|sum(attribute='errors')
  } -%}
  
  {{ log("验证摘要: " ~ summary, info=true) }}
  
  {{ return(summary) }}
{% endmacro %}

{% macro validate_model_completeness(model_name, required_columns) %}
  /*
  验证模型完整性
  
  Args:
    model_name: 模型名
    required_columns: 必需字段列表
    
  Returns:
    完整性验证结果
  */
  
  {%- set model_columns = adapter.get_columns_in_relation(ref(model_name)) -%}
  {%- set model_column_names = model_columns|map(attribute='name')|list -%}
  
  {%- set missing_columns = [] -%}
  
  {%- for required_col in required_columns -%}
    {%- if required_col not in model_column_names -%}
      {%- do missing_columns.append(required_col) -%}
    {%- endif -%}
  {%- endfor -%}
  
  {%- if missing_columns -%}
    {{ exceptions.raise_compiler_error("模型 " ~ model_name ~ " 缺少必需字段: " ~ missing_columns|join(', ')) }}
  {%- endif -%}
  
  {{ return(missing_columns|length == 0) }}
{% endmacro %}

{% macro validate_data_freshness(table_name, timestamp_column, max_age_hours=24) %}
  /*
  验证数据新鲜度
  
  Args:
    table_name: 表名
    timestamp_column: 时间戳字段
    max_age_hours: 最大允许小时数
    
  Returns:
    新鲜度验证结果
  */
  
  {%- set max_age_timestamp = "dateadd('hour', -" ~ max_age_hours ~ ", current_timestamp)" -%}
  
  case 
    when max({{ timestamp_column }}) < {{ max_age_timestamp }} then
      {{ exceptions.raise_compiler_error("数据表 " ~ table_name ~ " 的数据已过期（超过 " ~ max_age_hours ~ " 小时）") }}
    else 1
  end
{% endmacro %}

{% macro create_data_quality_report(model_name, validation_rules) %}
  /*
  创建数据质量报告
  
  Args:
    model_name: 模型名
    validation_rules: 验证规则
    
  Returns:
    数据质量报告
  */
  
  {%- set report_columns = [] -%}
  
  {%- for rule in validation_rules -%}
    {%- set validation_result = "case when " ~ rule.condition ~ " then 'PASS' else 'FAIL' end as " ~ rule.field ~ "_validation" -%}
    {%- do report_columns.append(validation_result) -%}
  {%- endfor -%}
  
  select
    '{{ model_name }}' as model_name,
    current_timestamp as validation_timestamp,
    {{ report_columns|join(', ') }}
  from {{ ref(model_name) }}
  limit 1
{% endmacro %}

{% macro validate_business_rules(model_name, rules) %}
  /*
  验证业务规则
  
  Args:
    model_name: 模型名
    rules: 业务规则列表 [{name: 规则名, condition: 条件, message: 错误消息}]
    
  Returns:
    业务规则验证结果
  */
  
  {%- for rule in rules -%}
    case 
      when not ({{ rule.condition }}) then
        {{ exceptions.raise_compiler_error("业务规则验证失败 - " ~ rule.name ~ ": " ~ rule.message) }}
      else 1
    end
  {%- endfor -%}
{% endmacro %}