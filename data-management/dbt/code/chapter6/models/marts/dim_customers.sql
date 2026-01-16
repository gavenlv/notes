-- 第6章：dbt最佳实践与项目结构
-- marts层 - 客户维度表
-- 演示维度建模和业务逻辑实现的最佳实践

{{ config(
    materialized='table',
    tags=['marts', 'dimension', 'customers', 'business-intelligence'],
    persist_docs={'relation': true, 'columns': true},
    alias='dim_customers',
    
    -- 高级配置选项
    indexes=[
        {'columns': ['customer_id'], 'unique': true},
        {'columns': ['customer_segment']},
        {'columns': ['customer_value_tier']},
        {'columns': ['last_order_date']},
        {'columns': ['customer_created_at']}
    ],
    
    -- 数据保留策略
    post_hook=[
        "GRANT SELECT ON {{ this }} TO analytics_team",
        "ANALYZE {{ this }}"
    ]
) }}

-- 模型描述
-- 此模型为客户维度表，整合客户基础信息、行为指标和业务分群
-- 输入：int_customer_metrics
-- 输出：面向业务分析的客户维度视图

WITH customer_metrics AS (
    -- 获取客户指标数据
    SELECT *
    FROM {{ ref('int_customer_metrics') }}
    WHERE customer_health_score >= 50  -- 只包含健康度合格的客户
),

customer_enhancements AS (
    -- 客户信息增强处理
    SELECT
        customer_id,
        full_name,
        email,
        customer_status,
        customer_type,
        customer_created_at,
        customer_age_years,
        
        -- 姓名标准化处理
        INITCAP(SPLIT_PART(full_name, ' ', 1)) as first_name_standardized,
        INITCAP(SPLIT_PART(full_name, ' ', -1)) as last_name_standardized,
        
        -- 邮箱域名提取
        SPLIT_PART(email, '@', 2) as email_domain,
        
        -- 客户状态增强
        CASE 
            WHEN customer_status = 'active' AND customer_health_score >= 80 THEN 'highly_active'
            WHEN customer_status = 'active' AND customer_health_score >= 60 THEN 'active'
            WHEN customer_status = 'active' THEN 'low_active'
            WHEN customer_status = 'inactive' AND customer_health_score >= 50 THEN 'dormant'
            ELSE 'inactive'
        END as enhanced_customer_status,
        
        -- 客户类型增强
        CASE 
            WHEN customer_type = 'premium' AND customer_value_score >= 80 THEN 'vip'
            WHEN customer_type = 'premium' THEN 'premium_standard'
            WHEN customer_type = 'standard' AND customer_value_score >= 70 THEN 'standard_plus'
            ELSE customer_type
        END as enhanced_customer_type
        
    FROM customer_metrics
),

behavioral_classification AS (
    -- 行为分类逻辑
    SELECT
        cm.*,
        
        -- 购买行为分类
        CASE 
            WHEN total_orders = 0 THEN 'no_purchase'
            WHEN total_orders = 1 THEN 'one_time_buyer'
            WHEN total_orders <= 5 THEN 'occasional_buyer'
            WHEN total_orders <= 20 THEN 'regular_buyer'
            ELSE 'frequent_buyer'
        END as purchase_frequency_class,
        
        -- 金额行为分类
        CASE 
            WHEN total_spent = 0 THEN 'no_spending'
            WHEN total_spent <= 100 THEN 'low_spender'
            WHEN total_spent <= 500 THEN 'medium_spender'
            WHEN total_spent <= 2000 THEN 'high_spender'
            ELSE 'vip_spender'
        END as spending_class,
        
        -- 时间行为分类
        CASE 
            WHEN days_since_last_order IS NULL THEN 'never_ordered'
            WHEN days_since_last_order <= 7 THEN 'very_recent'
            WHEN days_since_last_order <= 30 THEN 'recent'
            WHEN days_since_last_order <= 90 THEN 'moderate'
            WHEN days_since_last_order <= 365 THEN 'long_time'
            ELSE 'very_long_time'
        END as recency_class,
        
        -- 多样性行为分类
        CASE 
            WHEN unique_products_purchased = 0 THEN 'no_diversity'
            WHEN unique_products_purchased = 1 THEN 'single_product'
            WHEN unique_products_purchased <= 5 THEN 'low_diversity'
            WHEN unique_products_purchased <= 15 THEN 'medium_diversity'
            ELSE 'high_diversity'
        END as product_diversity_class
        
    FROM customer_metrics cm
),

customer_lifecycle AS (
    -- 客户生命周期分析
    SELECT
        bc.*,
        
        -- 生命周期阶段
        CASE 
            WHEN total_orders = 0 THEN 'prospect'
            WHEN total_orders = 1 AND days_since_last_order <= 30 THEN 'new_customer'
            WHEN total_orders <= 3 AND customer_age_years <= 0.5 THEN 'developing_customer'
            WHEN total_orders >= 4 AND customer_age_years >= 0.5 THEN 'established_customer'
            WHEN customer_age_years >= 2 AND total_orders >= 10 THEN 'loyal_customer'
            WHEN days_since_last_order > 365 THEN 'lost_customer'
            ELSE 'active_customer'
        END as lifecycle_stage,
        
        -- 忠诚度评分
        CASE 
            WHEN customer_age_years = 0 THEN 0
            ELSE LEAST(
                (total_orders / customer_age_years) * 10 +  -- 购买频率
                (customer_value_score * 0.3) +  -- 价值贡献
                (CASE WHEN days_since_last_order <= 30 THEN 30 ELSE 0 END),  -- 最近活跃
                100
            )
        END as loyalty_score,
        
        -- 增长潜力评估
        CASE 
            WHEN lifecycle_stage = 'prospect' THEN 'high_potential'
            WHEN lifecycle_stage = 'new_customer' AND customer_value_score >= 60 THEN 'high_potential'
            WHEN lifecycle_stage = 'developing_customer' AND order_success_rate >= 80 THEN 'medium_potential'
            WHEN lifecycle_stage = 'established_customer' AND spending_class IN ('high_spender', 'vip_spender') THEN 'upsell_potential'
            WHEN lifecycle_stage = 'loyal_customer' AND product_diversity_class = 'low_diversity' THEN 'cross_sell_potential'
            ELSE 'maintain'
        END as growth_potential
        
    FROM behavioral_classification bc
),

business_segmentation AS (
    -- 业务分群逻辑
    SELECT
        cl.*,
        ce.enhanced_customer_status,
        ce.enhanced_customer_type,
        ce.first_name_standardized,
        ce.last_name_standardized,
        ce.email_domain,
        
        -- 业务价值分群
        CASE 
            WHEN customer_value_score >= 90 THEN 'strategic'
            WHEN customer_value_score >= 75 THEN 'core'
            WHEN customer_value_score >= 60 THEN 'growth'
            WHEN customer_value_score >= 40 THEN 'developing'
            ELSE 'exploratory'
        END as customer_value_tier,
        
        -- 营销活动标签
        CASE 
            WHEN lifecycle_stage = 'prospect' THEN 'lead_nurturing'
            WHEN lifecycle_stage = 'new_customer' THEN 'onboarding'
            WHEN lifecycle_stage = 'developing_customer' AND growth_potential = 'high_potential' THEN 'accelerated_growth'
            WHEN lifecycle_stage = 'established_customer' AND loyalty_score >= 80 THEN 'retention'
            WHEN lifecycle_stage = 'loyal_customer' THEN 'advocacy'
            WHEN lifecycle_stage = 'lost_customer' AND customer_value_score >= 60 THEN 'winback'
            ELSE 'maintenance'
        END as marketing_campaign_target,
        
        -- 客户健康度预警
        CASE 
            WHEN customer_health_score < 30 THEN 'critical'
            WHEN customer_health_score < 50 THEN 'warning'
            WHEN customer_health_score < 70 THEN 'monitoring'
            WHEN customer_health_score < 85 THEN 'healthy'
            ELSE 'excellent'
        END as health_alert_level,
        
        -- 客户价值预测
        CASE 
            WHEN lifecycle_stage = 'prospect' THEN total_spent * 0.1
            WHEN lifecycle_stage = 'new_customer' THEN total_spent * 1.5
            WHEN lifecycle_stage = 'developing_customer' THEN total_spent * 2.0
            WHEN lifecycle_stage = 'established_customer' THEN total_spent * 1.2
            WHEN lifecycle_stage = 'loyal_customer' THEN total_spent * 1.1
            ELSE total_spent
        END as predicted_lifetime_value
        
    FROM customer_lifecycle cl
    LEFT JOIN customer_enhancements ce ON cl.customer_id = ce.customer_id
),

dim_customer_final AS (
    -- 最终维度表结构
    SELECT
        -- 基础标识字段
        customer_id,
        
        -- 个人信息字段
        full_name,
        first_name_standardized,
        last_name_standardized,
        email,
        email_domain,
        
        -- 状态与类型字段
        customer_status,
        enhanced_customer_status,
        customer_type,
        enhanced_customer_type,
        
        -- 时间字段
        customer_created_at,
        customer_age_years,
        first_order_date,
        last_order_date,
        days_since_last_order,
        customer_lifetime_days,
        
        -- 指标字段
        total_orders,
        completed_orders,
        cancelled_orders,
        total_spent,
        avg_order_value,
        max_order_value,
        active_months,
        orders_per_active_month,
        unique_products_purchased,
        unique_categories_purchased,
        order_success_rate,
        
        -- 评分字段
        customer_value_score,
        customer_health_score,
        loyalty_score,
        data_quality_score,
        
        -- 分群字段
        customer_segment,
        tenure_segment,
        value_segment,
        activity_segment,
        recency_segment,
        frequency_segment,
        monetary_segment,
        
        -- 分类字段
        purchase_frequency_class,
        spending_class,
        recency_class,
        product_diversity_class,
        
        -- 生命周期字段
        lifecycle_stage,
        growth_potential,
        
        -- 业务字段
        customer_value_tier,
        marketing_campaign_target,
        health_alert_level,
        predicted_lifetime_value,
        
        -- 技术字段
        _dbt_processed_at,
        _dbt_invocation_id,
        
        -- 计算字段：客户维度键（用于数据仓库）
        {{ dbt_utils.surrogate_key(['customer_id', 'customer_created_at']) }} as customer_dim_key,
        
        -- 计算字段：是否有效记录
        CASE 
            WHEN customer_health_score >= 50 AND customer_status != 'deleted' THEN true
            ELSE false
        END as is_active_record
        
    FROM business_segmentation
)

SELECT *
FROM dim_customer_final

-- 模型级文档
-- 此模型为客户维度表，提供全面的客户画像和业务分析能力
-- 适用于客户分析、营销自动化、业务决策支持等场景

-- 关键特性：
-- 1. 完整的客户生命周期管理
-- 2. 多维度客户分群
-- 3. 健康度监控和预警
-- 4. 价值评估和预测
-- 5. 营销活动目标定位

-- 使用场景：
-- 1. 客户细分和精准营销
-- 2. 客户流失预警和干预
-- 3. 客户价值最大化
-- 4. 业务绩效分析和报告
-- 5. 数据驱动的决策支持

-- 数据质量保障：
-- 1. 只包含健康度合格的客户记录
-- 2. 标准化姓名和邮箱处理
-- 3. 数据验证和清洗逻辑
-- 4. 一致性检查和边界处理

-- 性能优化：
-- 1. 表物化提升查询性能
-- 2. 多维度索引优化
-- 3. 数据分区策略（按时间或分群）
-- 4. 定期分析和维护

-- 安全考虑：
-- 1. 敏感信息处理（邮箱域名提取）
-- 2. 访问权限控制
-- 3. 数据脱敏策略
-- 4. 合规性检查

-- 扩展性设计：
-- 1. 模块化结构便于维护
-- 2. 标准化字段命名规范
-- 3. 预留扩展字段
-- 4. 兼容多种业务场景