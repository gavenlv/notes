-- 第7章：高级钩子函数与事件处理
-- 演示模型级和项目级钩子的高级用法

{% macro model_level_hooks(
    model_name,
    pre_hooks=None,
    post_hooks=None,
    error_hooks=None,
    audit_enabled=true
) %}
  {#-
    模型级钩子配置宏
    
    参数说明：
    - model_name: 模型名称
    - pre_hooks: 前置钩子列表
    - post_hooks: 后置钩子列表
    - error_hooks: 错误钩子列表
    - audit_enabled: 是否启用审计
    
    返回：配置了钩子的模型
  -#}
  
  {{ config(
    materialized='table',
    pre_hook=pre_hooks,
    post_hook=post_hooks,
    on_run_start=error_hooks,
    tags=['hooks', 'audit', 'advanced']
  ) }}
  
  -- 审计钩子（如果启用）
  {%- if audit_enabled %}
    {%- set audit_pre_hook %}
      INSERT INTO dbt_audit_log (
        model_name, event_type, event_time, event_data
      ) VALUES (
        '{{ model_name }}', 'START', CURRENT_TIMESTAMP, 
        '{"threads": {{ threads }}, "target": "{{ target.name }}"}'
      )
    {%- endset %}
    
    {%- set audit_post_hook %}
      INSERT INTO dbt_audit_log (
        model_name, event_type, event_time, event_data
      ) VALUES (
        '{{ model_name }}', 'COMPLETE', CURRENT_TIMESTAMP, 
        '{"rows_affected": {{ this.row_count }}}'
      )
    {%- endset %}
    
    {{ config(
      pre_hook=pre_hooks + [audit_pre_hook] if pre_hooks else [audit_pre_hook],
      post_hook=post_hooks + [audit_post_hook] if post_hooks else [audit_post_hook]
    ) }}
  {%- endif %}
  
  -- 错误处理钩子
  {%- if error_hooks %}
    {%- set error_handler %}
      BEGIN
        -- 错误处理逻辑
        EXCEPTION
          WHEN OTHERS THEN
            INSERT INTO dbt_error_log (
              model_name, error_time, error_message, stack_trace
            ) VALUES (
              '{{ model_name }}', CURRENT_TIMESTAMP, SQLERRM, SQLSTATE
            );
            RAISE;
      END;
    {%- endset %}
  {%- endif %}
  
  -- 模型查询逻辑
  SELECT 
    *,
    '{{ model_name }}' AS _dbt_model_name,
    CURRENT_TIMESTAMP AS _dbt_processed_at
  FROM {{ ref('base_data') }}
  
{% endmacro %}

{% macro project_level_hooks(
    hook_type='run_start',
    hooks_config=None,
    environment_specific=true
) %}
  {#-
    项目级钩子配置宏
    
    参数说明：
    - hook_type: 钩子类型（run_start/run_end/...）
    - hooks_config: 钩子配置
    - environment_specific: 是否环境特定
    
    返回：项目级钩子配置
  -#}
  
  {%- set hook_commands = [] %}
  
  -- 基础钩子命令
  {%- if hook_type == 'run_start' %}
    {%- set hook_commands = hook_commands + [
      "{{ log('dbt项目运行开始', info=true) }}",
      "{{ create_run_session() }}",
      "{{ validate_environment() }}"
    ] %}
    
  {%- elif hook_type == 'run_end' %}
    {%- set hook_commands = hook_commands + [
      "{{ log('dbt项目运行完成', info=true) }}",
      "{{ update_run_summary() }}",
      "{{ send_notification('Run completed') }}",
      "{{ cleanup_temp_resources() }}"
    ] %}
    
  {%- endif %}
  
  -- 添加自定义钩子配置
  {%- if hooks_config %}
    {%- for hook in hooks_config %}
      {%- set hook_commands = hook_commands + [hook.command] %}
    {%- endfor %}
  {%- endif %}
  
  -- 环境特定钩子
  {%- if environment_specific %}
    {%- if target.name == 'dev' %}
      {%- set hook_commands = hook_commands + [
        "{{ log('开发环境特定处理', info=true) }}",
        "{{ enable_debug_mode() }}"
      ] %}
      
    {%- elif target.name == 'prod' %}
      {%- set hook_commands = hook_commands + [
        "{{ log('生产环境特定处理', info=true) }}",
        "{{ disable_debug_mode() }}",
        "{{ backup_critical_tables() }}"
      ] %}
      
    {%- endif %}
  {%- endif %}
  
  -- 返回钩子配置
  {{ hook_commands | tojson }}
  
{% endmacro %}

{% macro create_run_session() %}
  {#-
    创建运行会话钩子
    
    返回：运行会话创建SQL
  -#}
  
  CREATE TABLE IF NOT EXISTS dbt_run_sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'RUNNING',
    models_processed INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    environment VARCHAR(50),
    dbt_version VARCHAR(20)
  );
  
  INSERT INTO dbt_run_sessions (
    session_id, start_time, environment, dbt_version
  ) VALUES (
    '{{ invocation_id }}', 
    CURRENT_TIMESTAMP, 
    '{{ target.name }}',
    '{{ dbt_version }}'
  );
  
{% endmacro %}

{% macro update_run_summary() %}
  {#-
    更新运行摘要钩子
    
    返回：运行摘要更新SQL
  -#}
  
  UPDATE dbt_run_sessions 
  SET 
    end_time = CURRENT_TIMESTAMP,
    status = 'COMPLETED',
    models_processed = (
      SELECT COUNT(*) 
      FROM dbt_audit_log 
      WHERE event_type = 'COMPLETE'
        AND event_time >= (
          SELECT start_time 
          FROM dbt_run_sessions 
          WHERE session_id = '{{ invocation_id }}'
        )
    )
  WHERE session_id = '{{ invocation_id }}';
  
  -- 记录性能指标
  INSERT INTO dbt_performance_metrics (
    session_id, metric_name, metric_value, recorded_at
  )
  SELECT 
    '{{ invocation_id }}',
    'total_execution_time',
    EXTRACT(EPOCH FROM (end_time - start_time)),
    CURRENT_TIMESTAMP
  FROM dbt_run_sessions
  WHERE session_id = '{{ invocation_id }}';
  
{% endmacro %}

{% macro validate_environment() %}
  {#-
    环境验证钩子
    
    返回：环境验证SQL
  -#}
  
  -- 检查必要的表是否存在
  {%- set required_tables = ['dbt_audit_log', 'dbt_run_sessions', 'dbt_error_log'] %}
  
  {%- for table in required_tables %}
    {%- set check_table_sql %}
      SELECT COUNT(*) as table_exists
      FROM information_schema.tables 
      WHERE table_schema = '{{ target.schema }}' 
        AND table_name = '{{ table }}'
    {%- endset %}
    
    {%- set result = run_query(check_table_sql) %}
    
    {%- if not result or result[0][0] == 0 %}
      {{ "-- 创建缺失的表: " ~ table }}
      
      {%- if table == 'dbt_audit_log' %}
        CREATE TABLE IF NOT EXISTS dbt_audit_log (
          id BIGSERIAL PRIMARY KEY,
          model_name VARCHAR(100) NOT NULL,
          event_type VARCHAR(20) NOT NULL,
          event_time TIMESTAMP NOT NULL,
          event_data JSONB
        );
        
      {%- elif table == 'dbt_run_sessions' %}
        CREATE TABLE IF NOT EXISTS dbt_run_sessions (
          session_id VARCHAR(50) PRIMARY KEY,
          start_time TIMESTAMP NOT NULL,
          end_time TIMESTAMP,
          status VARCHAR(20) DEFAULT 'RUNNING',
          models_processed INTEGER DEFAULT 0,
          errors_count INTEGER DEFAULT 0,
          environment VARCHAR(50),
          dbt_version VARCHAR(20)
        );
        
      {%- elif table == 'dbt_error_log' %}
        CREATE TABLE IF NOT EXISTS dbt_error_log (
          id BIGSERIAL PRIMARY KEY,
          model_name VARCHAR(100) NOT NULL,
          error_time TIMESTAMP NOT NULL,
          error_message TEXT,
          stack_trace TEXT,
          resolved BOOLEAN DEFAULT FALSE
        );
        
      {%- endif %}
    {%- endif %}
  {%- endfor %}
  
  -- 验证数据库连接和权限
  SELECT 
    CURRENT_DATABASE() as database_name,
    CURRENT_USER as current_user,
    VERSION() as db_version
  
{% endmacro %}

{% macro send_notification(message) %}
  {#-
    发送通知钩子
    
    参数说明：
    - message: 通知消息
    
    返回：通知逻辑
  -#}
  
  -- 记录通知到日志表
  INSERT INTO dbt_notifications (
    notification_type, message, sent_time, status
  ) VALUES (
    'RUN_COMPLETION', 
    '{{ message }} - Session: {{ invocation_id }}', 
    CURRENT_TIMESTAMP, 
    'SENT'
  );
  
  -- 集成外部通知系统（示例）
  {%- if target.name == 'prod' %}
    {{ "-- 生产环境：发送Slack通知" }}
    {{ "-- 调用外部API发送通知" }}
    
  {%- elif target.name == 'dev' %}
    {{ "-- 开发环境：记录到控制台" }}
    {{ log(message ~ " - Session: " ~ invocation_id, info=true) }}
    
  {%- endif %}
  
{% endmacro %}

{% macro cleanup_temp_resources() %}
  {#-
    清理临时资源钩子
    
    返回：资源清理SQL
  -#}
  
  -- 清理临时表
  DROP TABLE IF EXISTS temp_audit;
  DROP TABLE IF EXISTS temp_processing;
  
  -- 清理过期的会话记录（保留最近30天）
  DELETE FROM dbt_run_sessions 
  WHERE end_time < CURRENT_DATE - INTERVAL '30 days';
  
  -- 清理过期的审计日志（保留最近90天）
  DELETE FROM dbt_audit_log 
  WHERE event_time < CURRENT_DATE - INTERVAL '90 days';
  
  -- 清理已解决的错误记录（保留最近180天）
  DELETE FROM dbt_error_log 
  WHERE resolved = TRUE 
    AND error_time < CURRENT_DATE - INTERVAL '180 days';
  
{% endmacro %}

{% macro error_handler_hook(model_name, error_context) %}
  {#-
    错误处理钩子
    
    参数说明：
    - model_name: 模型名称
    - error_context: 错误上下文
    
    返回：错误处理逻辑
  -#}
  
  -- 记录错误详情
  INSERT INTO dbt_error_log (
    model_name, error_time, error_message, stack_trace
  ) VALUES (
    '{{ model_name }}', 
    CURRENT_TIMESTAMP, 
    '{{ error_context.error_message }}',
    '{{ error_context.stack_trace }}'
  );
  
  -- 根据错误类型采取不同措施
  {%- if 'timeout' in error_context.error_message.lower() %}
    {{ "-- 超时错误：记录并继续" }}
    {{ log("模型 " ~ model_name ~ " 执行超时", info=true) }}
    
  {%- elif 'memory' in error_context.error_message.lower() %}
    {{ "-- 内存错误：调整配置并重试" }}
    {{ log("模型 " ~ model_name ~ " 内存不足", info=true) }}
    
  {%- else %}
    {{ "-- 其他错误：记录并标记需要人工干预" }}
    {{ log("模型 " ~ model_name ~ " 执行失败，需要人工干预", info=true) }}
    
  {%- endif %}
  
  -- 返回错误处理结果
  SELECT 
    'ERROR_HANDLED' as status,
    '{{ model_name }}' as failed_model,
    CURRENT_TIMESTAMP as handled_at
  
{% endmacro %}

{% macro performance_monitoring_hook(model_name) %}
  {#-
    性能监控钩子
    
    参数说明：
    - model_name: 模型名称
    
    返回：性能监控逻辑
  -#}
  
  -- 记录执行时间
  INSERT INTO dbt_performance_metrics (
    session_id, model_name, metric_name, metric_value, recorded_at
  )
  SELECT 
    '{{ invocation_id }}',
    '{{ model_name }}',
    'execution_time_seconds',
    EXTRACT(EPOCH FROM (
      SELECT MAX(event_time) - MIN(event_time) 
      FROM dbt_audit_log 
      WHERE model_name = '{{ model_name }}'
        AND event_time >= (
          SELECT start_time 
          FROM dbt_run_sessions 
          WHERE session_id = '{{ invocation_id }}'
        )
    )),
    CURRENT_TIMESTAMP
  WHERE EXISTS (
    SELECT 1 FROM dbt_audit_log 
    WHERE model_name = '{{ model_name }}'
  );
  
  -- 记录行数统计
  INSERT INTO dbt_performance_metrics (
    session_id, model_name, metric_name, metric_value, recorded_at
  )
  SELECT 
    '{{ invocation_id }}',
    '{{ model_name }}',
    'rows_processed',
    COUNT(*),
    CURRENT_TIMESTAMP
  FROM {{ ref(model_name) }}
  WHERE _dbt_processed_at >= (
    SELECT start_time 
    FROM dbt_run_sessions 
    WHERE session_id = '{{ invocation_id }}'
  );
  
  -- 性能分析报告
  SELECT 
    '{{ model_name }}' as model_name,
    COUNT(*) as total_metrics,
    AVG(metric_value) as avg_performance,
    MAX(metric_value) as max_performance
  FROM dbt_performance_metrics
  WHERE model_name = '{{ model_name }}'
    AND session_id = '{{ invocation_id }}'
  GROUP BY model_name;
  
{% endmacro %}

-- 使用示例和文档
{##
  高级钩子函数与事件处理示例说明：
  
  1. 模型级钩子配置：
     为单个模型配置前置、后置和错误钩子
     
     示例用法：
     {{ model_level_hooks(
         model_name='fct_orders',
         pre_hooks=['{{ validate_data_quality() }}'],
         post_hooks=['{{ update_business_metrics() }}'],
         audit_enabled=true
     ) }}
  
  2. 项目级钩子配置：
     配置整个项目的运行开始和结束钩子
     
  3. 运行会话管理：
     跟踪dbt运行会话的完整生命周期
     
  4. 环境验证：
     在运行开始前验证环境和依赖
     
  5. 通知系统：
     集成外部通知服务
     
  6. 资源清理：
     自动清理临时资源和过期数据
     
  7. 错误处理：
     统一的错误处理和恢复机制
     
  8. 性能监控：
     详细的性能指标收集和分析
  
  最佳实践：
  - 保持钩子的轻量级和高效性
  - 实现适当的错误处理和恢复
  - 监控钩子的性能影响
  - 定期审查和优化钩子逻辑
  - 文档化钩子的用途和配置
##}