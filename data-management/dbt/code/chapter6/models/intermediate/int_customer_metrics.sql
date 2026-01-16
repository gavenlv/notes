-- 第6章：dbt最佳实践与项目结构
-- intermediate层 - 客户指标计算模型
-- 演示业务逻辑实现和指标计算的最佳实践

{{ config(
    materialized='table',
    tags=['intermediate', 'customers', 'metrics', 'business-logic'],
    persist_docs={'relation': true, 'columns': true},
    alias='int_customer_metrics',
    
    -- 性能优化配置
    indexes=[
        {'columns': ['customer_id'], 'unique': true},
        {'columns': ['customer_segment']},
        {'columns': ['last_order_date']}
    ]
) }}

-- 模型描述
-- 此模型整合客户基础数据和订单数据，计算全面的客户指标
-- 输入：stg_customers, stg_orders
-- 输出：客户级别的综合指标数据

WITH customer_base AS (
    -- 客户基础数据
    SELECT
        customer_id,
        first_name,
        last_name,
        full_name,
        email,
        status as customer_status,
        customer_type,
        created_at as customer_created_at,
        customer_age_years,
        data_quality_score,
        final_validation_status
    FROM {{ ref('stg_customers') }}
    WHERE final_validation_status = 'passed'
),

order_metrics AS (
    -- 订单指标计算
    SELECT
        o.customer_id,
        
        -- 订单数量指标
        COUNT(*) as total_orders,
        COUNT(CASE WHEN o.status = 'completed' THEN 1 END) as completed_orders,
        COUNT(CASE WHEN o.status = 'cancelled' THEN 1 END) as cancelled_orders,
        
        -- 金额指标
        SUM(o.total_amount) as total_spent,
        AVG(o.total_amount) as avg_order_value,
        MAX(o.total_amount) as max_order_value,
        
        -- 时间指标
        MIN(o.order_date) as first_order_date,
        MAX(o.order_date) as last_order_date,
        
        -- 频率指标
        COUNT(DISTINCT DATE_TRUNC('month', o.order_date)) as active_months,
        
        -- 产品多样性指标
        COUNT(DISTINCT o.product_id) as unique_products_purchased,
        COUNT(DISTINCT o.category) as unique_categories_purchased
        
    FROM {{ ref('stg_orders') }} o
    WHERE o.final_validation_status = 'passed'
    GROUP BY o.customer_id
),

recency_metrics AS (
    -- 最近行为指标（RFM分析）
    SELECT
        customer_id,
        
        -- 最近购买时间（Recency）
        {{ date_diff('last_order_date', 'CURRENT_DATE', 'day') }} as days_since_last_order,
        
        -- 购买频率（Frequency）
        total_orders as frequency_score,
        
        -- 购买金额（Monetary）
        total_spent as monetary_score,
        
        -- RFM分群
        CASE 
            WHEN days_since_last_order <= 30 THEN 'active'
            WHEN days_since_last_order <= 90 THEN 'warm'
            WHEN days_since_last_order <= 365 THEN 'cold'
            ELSE 'inactive'
        END as recency_segment,
        
        CASE 
            WHEN frequency_score >= 10 THEN 'high'
            WHEN frequency_score >= 5 THEN 'medium'
            WHEN frequency_score >= 1 THEN 'low'
            ELSE 'new'
        END as frequency_segment,
        
        CASE 
            WHEN monetary_score >= 1000 THEN 'high'
            WHEN monetary_score >= 500 THEN 'medium'
            WHEN monetary_score >= 100 THEN 'low'
            ELSE 'minimal'
        END as monetary_segment
        
    FROM order_metrics
),

customer_segmentation AS (
    -- 客户分群逻辑
    SELECT
        cb.customer_id,
        
        -- 基础分群
        CASE 
            WHEN cb.customer_age_years <= 1 THEN 'new_customer'
            WHEN cb.customer_age_years <= 3 THEN 'established_customer'
            ELSE 'loyal_customer'
        END as tenure_segment,
        
        -- 价值分群
        CASE 
            WHEN om.total_spent >= 5000 THEN 'vip'
            WHEN om.total_spent >= 1000 THEN 'premium'
            WHEN om.total_spent >= 100 THEN 'standard'
            ELSE 'basic'
        END as value_segment,
        
        -- 活跃度分群
        CASE 
            WHEN rm.days_since_last_order <= 30 THEN 'highly_active'
            WHEN rm.days_since_last_order <= 90 THEN 'active'
            WHEN rm.days_since_last_order <= 180 THEN 'occasional'
            ELSE 'dormant'
        END as activity_segment,
        
        -- 综合分群
        CASE 
            WHEN rm.recency_segment = 'active' AND rm.frequency_segment = 'high' AND rm.monetary_segment = 'high' THEN 'champion'
            WHEN rm.recency_segment = 'active' AND rm.monetary_segment = 'high' THEN 'high_value_new'
            WHEN rm.frequency_segment = 'high' AND rm.monetary_segment = 'high' THEN 'loyal_high_value'
            WHEN rm.recency_segment = 'warm' THEN 'needs_attention'
            WHEN rm.recency_segment = 'cold' THEN 'at_risk'
            WHEN rm.recency_segment = 'inactive' THEN 'lost'
            ELSE 'regular'
        END as customer_segment
        
    FROM customer_base cb
    LEFT JOIN order_metrics om ON cb.customer_id = om.customer_id
    LEFT JOIN recency_metrics rm ON cb.customer_id = rm.customer_id
),

behavioral_metrics AS (
    -- 行为指标计算
    SELECT
        cb.customer_id,
        
        -- 购买行为指标
        COALESCE(om.total_orders, 0) as total_orders,
        COALESCE(om.completed_orders, 0) as completed_orders,
        COALESCE(om.cancelled_orders, 0) as cancelled_orders,
        
        -- 金额行为指标
        COALESCE(om.total_spent, 0) as total_spent,
        COALESCE(om.avg_order_value, 0) as avg_order_value,
        COALESCE(om.max_order_value, 0) as max_order_value,
        
        -- 时间行为指标
        om.first_order_date,
        om.last_order_date,
        COALESCE({{ date_diff('om.first_order_date', 'om.last_order_date', 'day') }}, 0) as customer_lifetime_days,
        
        -- 频率行为指标
        COALESCE(om.active_months, 0) as active_months,
        CASE 
            WHEN COALESCE(om.active_months, 0) > 0 
            THEN COALESCE(om.total_orders, 0)::decimal / om.active_months 
            ELSE 0 
        END as orders_per_active_month,
        
        -- 多样性行为指标
        COALESCE(om.unique_products_purchased, 0) as unique_products_purchased,
        COALESCE(om.unique_categories_purchased, 0) as unique_categories_purchased,
        
        -- 成功率指标
        CASE 
            WHEN COALESCE(om.total_orders, 0) > 0 
            THEN (om.completed_orders::decimal / om.total_orders) * 100 
            ELSE 0 
        END as order_success_rate
        
    FROM customer_base cb
    LEFT JOIN order_metrics om ON cb.customer_id = om.customer_id
),

comprehensive_metrics AS (
    -- 综合指标计算
    SELECT
        cb.customer_id,
        cb.full_name,
        cb.email,
        cb.customer_status,
        cb.customer_type,
        cb.customer_created_at,
        cb.customer_age_years,
        cb.data_quality_score,
        
        -- 基础指标
        bm.total_orders,
        bm.completed_orders,
        bm.cancelled_orders,
        bm.total_spent,
        bm.avg_order_value,
        bm.max_order_value,
        bm.first_order_date,
        bm.last_order_date,
        bm.customer_lifetime_days,
        bm.active_months,
        bm.orders_per_active_month,
        bm.unique_products_purchased,
        bm.unique_categories_purchased,
        bm.order_success_rate,
        
        -- RFM指标
        rm.days_since_last_order,
        rm.frequency_score,
        rm.monetary_score,
        rm.recency_segment,
        rm.frequency_segment,
        rm.monetary_segment,
        
        -- 分群指标
        cs.tenure_segment,
        cs.value_segment,
        cs.activity_segment,
        cs.customer_segment,
        
        -- 计算字段：客户价值评分（0-100）
        CASE 
            WHEN bm.total_orders = 0 THEN 0
            ELSE LEAST(
                (bm.total_spent / 1000) * 25 +  -- 金额权重25%
                (bm.total_orders / 10) * 25 +   -- 频率权重25%
                (CASE WHEN rm.days_since_last_order <= 30 THEN 25 ELSE 0 END) +  -- 最近性权重25%
                (bm.order_success_rate * 0.25),  -- 成功率权重25%
                100
            )
        END as customer_value_score,
        
        -- 计算字段：客户健康度（0-100）
        CASE 
            WHEN bm.total_orders = 0 THEN cb.data_quality_score
            ELSE LEAST(
                cb.data_quality_score * 0.3 +  -- 数据质量权重30%
                bm.order_success_rate * 0.3 +  -- 成功率权重30%
                (CASE WHEN rm.days_since_last_order <= 90 THEN 40 ELSE 0 END),  -- 活跃度权重40%
                100
            )
        END as customer_health_score,
        
        -- 技术字段
        CURRENT_TIMESTAMP as _dbt_processed_at,
        '{{ invocation_id }}' as _dbt_invocation_id
        
    FROM customer_base cb
    INNER JOIN behavioral_metrics bm ON cb.customer_id = bm.customer_id
    LEFT JOIN recency_metrics rm ON cb.customer_id = rm.customer_id
    LEFT JOIN customer_segmentation cs ON cb.customer_id = cs.customer_id
)

SELECT *
FROM comprehensive_metrics

-- 模型级文档
-- 此模型提供客户级别的全面指标分析，支持客户分群、价值评估和健康度监控
-- 适用于客户分析、营销自动化和业务决策支持

-- 关键指标说明：
-- customer_value_score: 客户价值综合评分（0-100）
-- customer_health_score: 客户健康度评分（0-100）
-- customer_segment: 基于RFM的综合客户分群
-- order_success_rate: 订单成功率（%）

-- 使用场景：
-- 1. 客户生命周期管理
-- 2. 精准营销活动
-- 3. 客户流失预警
-- 4. 业务绩效分析

-- 测试覆盖：
-- 1. 指标计算逻辑验证
-- 2. 分群规则测试
-- 3. 数据一致性测试
-- 4. 边界条件测试

-- 性能优化：
-- 1. 使用表物化提升查询性能
-- 2. 创建索引优化常用查询
-- 3. 考虑分区策略（按时间或分群）
-- 4. 监控数据更新频率和性能