-- 第6章：dbt最佳实践与项目结构
-- 自定义测试：数据质量评分范围验证
-- 演示数值范围验证的自定义测试实现

{% test data_quality_range(model, column_name, min_value=0, max_value=100) %}
    -- 数据质量评分范围验证测试
    -- 验证数据质量评分在指定范围内
    
    -- 测试逻辑：评分应在[min_value, max_value]范围内
    -- 支持自定义最小值和最大值
    
    SELECT
        {{ column_name }} as out_of_range_score,
        '{{ column_name }}' as column_name,
        {{ min_value }} as expected_min,
        {{ max_value }} as expected_max
    FROM {{ model }}
    WHERE 
        {{ column_name }} IS NOT NULL
        AND (
            {{ column_name }} < {{ min_value }}
            OR {{ column_name }} > {{ max_value }}
        )
        
        -- 可选：排除特定条件的记录
        {% if 'final_validation_status' in adapter.get_columns_in_relation(model) | map(attribute='name') %}
            AND final_validation_status != 'failed'
        {% endif %}
        
{% endtest %}

-- 测试说明：
-- 1. 验证数值字段在指定范围内
-- 2. 支持自定义最小值和最大值参数
-- 3. 处理空值情况
-- 4. 支持条件排除

-- 参数说明：
-- min_value: 允许的最小值（默认0）
-- max_value: 允许的最大值（默认100）

-- 使用场景：
-- 1. 评分字段范围验证
-- 2. 百分比字段范围验证
-- 3. 业务指标范围验证
-- 4. 数据质量监控

-- 测试覆盖：
-- 1. 数值范围边界测试
-- 2. 空值处理
-- 3. 参数化配置
-- 4. 业务条件排除