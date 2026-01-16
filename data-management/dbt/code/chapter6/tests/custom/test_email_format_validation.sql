-- 第6章：dbt最佳实践与项目结构
-- 自定义测试：邮箱格式验证
-- 演示自定义测试的设计和实现最佳实践

{% test email_format_validation(model, column_name) %}
    -- 邮箱格式验证测试
    -- 验证邮箱地址是否符合标准格式
    
    -- 测试逻辑：邮箱应包含@符号，且域名部分应包含点号
    -- 排除空值和已删除的记录
    
    SELECT
        {{ column_name }} as invalid_email
    FROM {{ model }}
    WHERE 
        {{ column_name }} IS NOT NULL
        AND {{ column_name }} != ''
        AND (
            -- 基本格式验证：必须包含@符号
            POSITION('@' IN {{ column_name }}) = 0
            OR 
            -- 域名验证：@后必须包含点号
            POSITION('.' IN SUBSTRING({{ column_name }}, POSITION('@' IN {{ column_name }}) + 1)) = 0
            OR
            -- 特殊字符验证：不能包含空格
            POSITION(' ' IN {{ column_name }}) > 0
            OR
            -- 长度验证：邮箱长度应在合理范围内
            LENGTH({{ column_name }}) < 5
            OR LENGTH({{ column_name }}) > 254
            OR
            -- 本地部分验证：@前不能为空
            POSITION('@' IN {{ column_name }}) = 1
            OR
            -- 域名部分验证：@后不能为空
            POSITION('@' IN {{ column_name }}) = LENGTH({{ column_name }})
        )
        
        -- 可选：排除特定状态的记录
        {% if 'status' in adapter.get_columns_in_relation(model) | map(attribute='name') %}
            AND status != 'deleted'
        {% endif %}
        
{% endtest %}

-- 测试说明：
-- 1. 验证邮箱基本格式：必须包含@符号
-- 2. 验证域名格式：@后必须包含点号
-- 3. 排除常见格式错误：空格、长度异常等
-- 4. 支持条件排除：如已删除的记录
-- 5. 可扩展性：可根据业务需求添加更多验证规则

-- 使用场景：
-- 1. 客户数据质量验证
-- 2. 用户注册数据验证
-- 3. 营销活动数据验证
-- 4. 数据导入质量检查

-- 测试覆盖：
-- 1. 标准邮箱格式验证
-- 2. 边界条件测试
-- 3. 异常格式检测
-- 4. 业务规则验证