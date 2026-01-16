-- 第6章：dbt最佳实践与项目结构
-- 种子数据模型 - 客户分群配置
-- 演示种子数据的使用和管理最佳实践

{{ config(
    materialized='table',
    tags=['seeds', 'reference', 'customer-segments'],
    alias='seed_customer_segments',
    
    -- 种子数据特定配置
    persist_docs={'relation': true, 'columns': true},
    
    -- 性能优化
    indexes=[
        {'columns': ['segment_id'], 'unique': true},
        {'columns': ['segment_name']},
        {'columns': ['priority_level']}
    ]
) }}

-- 模型描述
-- 此模型加载客户分群配置数据，作为业务规则和分群逻辑的参考数据
-- 数据来源：data/customer_segments.csv
-- 输出：标准化的客户分群配置表

SELECT
    segment_id,
    segment_name,
    segment_description,
    min_value_score,
    max_value_score,
    min_health_score,
    max_health_score,
    priority_level,
    marketing_budget,
    retention_strategy,
    
    -- 计算字段：分群范围描述
    CONCAT(min_value_score, '-', max_value_score) as value_score_range,
    CONCAT(min_health_score, '-', max_health_score) as health_score_range,
    
    -- 计算字段：分群类型
    CASE 
        WHEN priority_level = 1 THEN 'strategic'
        WHEN priority_level = 2 THEN 'core'
        WHEN priority_level = 3 THEN 'growth'
        WHEN priority_level = 4 THEN 'developing'
        WHEN priority_level = 5 THEN 'exploratory'
        ELSE 'other'
    END as segment_category,
    
    -- 计算字段：预算等级
    CASE 
        WHEN marketing_budget >= 10000 THEN 'high'
        WHEN marketing_budget >= 5000 THEN 'medium'
        WHEN marketing_budget >= 1000 THEN 'low'
        ELSE 'minimal'
    END as budget_level,
    
    -- 技术字段
    CURRENT_TIMESTAMP as _dbt_loaded_at,
    '{{ invocation_id }}' as _dbt_invocation_id
    
FROM {{ ref('customer_segments') }}

-- 模型级文档
-- 此模型提供客户分群的业务配置数据，支持客户价值评估和营销策略制定

-- 关键字段说明：
-- segment_id: 分群唯一标识
-- segment_name: 分群名称
-- segment_description: 分群描述
-- min/max_value_score: 价值评分范围
-- min/max_health_score: 健康度评分范围
-- priority_level: 优先级（1-5，1为最高）
-- marketing_budget: 营销预算分配
-- retention_strategy: 保留策略

-- 使用场景：
-- 1. 客户分群规则配置
-- 2. 营销预算分配
-- 3. 客户服务策略制定
-- 4. 业务分析和报告

-- 数据质量保障：
-- 1. 唯一性约束：segment_id唯一
-- 2. 范围验证：评分范围合理
-- 3. 完整性检查：关键字段非空
-- 4. 一致性验证：优先级逻辑正确

-- 维护说明：
-- 1. 定期更新分群规则以适应业务变化
-- 2. 监控分群数据的使用情况
-- 3. 与业务团队协作维护分群策略
-- 4. 版本控制分群配置变更