-- 客户维度表 - 第5章：数据源与连接配置
-- 演示最终业务维度的构建和优化

{{ config(
    materialized='table',
    tags=['marts', 'dimension', 'customers', 'chapter5'],
    persist_docs={"relation": true, "columns": true},
    unique_key='customer_id'
) }}

-- 使用宏生成动态模型结构（演示高级特性）
{%- set base_columns = [
    'customer_id',
    'first_name', 
    'last_name',
    'email',
    'full_name',
    'customer_segment',
    'data_quality_level',
    'customer_created_at',
    'customer_updated_at'
] -%}

{%- set metric_columns = [
    'total_orders',
    'completed_orders',
    'pending_orders',
    'cancelled_orders',
    'total_spent',
    'avg_order_value',
    'max_order_value',
    'min_order_value',
    'first_order_date',
    'last_order_date',
    'high_value_orders',
    'medium_value_orders',
    'standard_value_orders',
    'orders_last_30_days',
    'orders_last_90_days',
    'orders_last_year',
    'spent_last_30_days',
    'spent_last_90_days',
    'spent_last_year'
] -%}

{%- set activity_columns = [
    'customer_lifetime_days',
    'purchase_frequency_per_day',
    'days_since_last_purchase',
    'avg_purchase_interval_days',
    'activity_level'
] -%}

{%- set segmentation_columns = [
    'recency_score',
    'frequency_score',
    'monetary_score',
    'rfm_segment'
] -%}

{%- set calculated_columns = [
    'customer_health_score',
    'customer_value_tier'
] -%}

-- 基础查询结构
with customer_metrics as (
    select
        {{ base_columns | join(', ') }},
        {{ metric_columns | join(', ') }},
        {{ activity_columns | join(', ') }},
        {{ segmentation_columns | join(', ') }},
        {{ calculated_columns | join(', ') }},
        _dbt_loaded_at,
        _dbt_invocation_id
    from {{ ref('int_customer_metrics') }}
),

-- 客户活跃度增强计算
customer_activity_enhanced as (
    select
        *,
        
        -- 客户活跃度分类（基于RFM和最近活动）
        case 
            when activity_level = '高活跃' and recency_score >= 4 then '核心活跃客户'
            when activity_level = '高活跃' then '新活跃客户'
            when activity_level = '中活跃' and recency_score >= 3 then '稳定客户'
            when activity_level = '中活跃' then '一般客户'
            when activity_level = '低活跃' and recency_score >= 2 then '潜在流失客户'
            when activity_level = '低活跃' then '流失风险客户'
            when activity_level = '休眠' then '已流失客户'
            else '未知状态'
        end as customer_activity_category,
        
        -- 购买行为模式
        case 
            when total_orders = 0 then '无购买记录'
            when total_orders = 1 then '单次购买'
            when total_orders between 2 and 5 then '多次购买'
            when total_orders between 6 and 20 then '频繁购买'
            when total_orders > 20 then '重度购买'
        end as purchase_behavior_pattern,
        
        -- 客户价值生命周期
        case 
            when total_orders = 0 then '潜在客户'
            when total_orders = 1 and days_since_last_purchase <= 30 then '新客户'
            when total_orders >= 2 and days_since_last_purchase <= 90 then '成长客户'
            when total_orders >= 5 and days_since_last_purchase <= 180 then '成熟客户'
            when days_since_last_purchase > 180 then '休眠客户'
            when days_since_last_purchase > 365 then '流失客户'
            else '稳定客户'
        end as customer_lifecycle_stage,
        
        -- 客户忠诚度评分（0-100）
        round(
            (recency_score * 25) +  -- 最近购买权重25%
            (frequency_score * 25) +  -- 购买频率权重25%
            (monetary_score * 25) +  -- 购买金额权重25%
            (case when customer_lifetime_days > 365 then 25 else customer_lifetime_days / 14.6 end)  -- 生命周期权重25%
        ) as customer_loyalty_score,
        
        -- 客户增长潜力
        case 
            when customer_lifecycle_stage = '潜在客户' then '高潜力'
            when customer_lifecycle_stage = '新客户' and avg_order_value > 100 then '高潜力'
            when customer_lifecycle_stage = '成长客户' and purchase_frequency_per_day > 0.1 then '高潜力'
            when customer_lifecycle_stage = '成熟客户' and total_spent > 1000 then '高价值维护'
            when customer_lifecycle_stage = '休眠客户' and total_spent > 500 then '唤醒潜力'
            when customer_lifecycle_stage = '流失客户' and total_spent > 1000 then '挽回价值'
            else '一般维护'
        end as growth_potential,
        
        -- 客户服务优先级
        case 
            when customer_value_tier = 'A级（高价值）' and customer_activity_category = '核心活跃客户' then '最高优先级'
            when customer_value_tier = 'A级（高价值）' then '高优先级'
            when customer_value_tier = 'B级（中价值）' and growth_potential = '高潜力' then '高优先级'
            when customer_value_tier in ('C级（一般价值）', 'D级（低价值）') and growth_potential = '高潜力' then '中等优先级'
            when customer_value_tier = 'E级（潜在流失）' and growth_potential = '挽回价值' then '挽回优先级'
            else '标准优先级'
        end as service_priority
        
    from customer_metrics
),

-- 客户分群和标签系统
customer_segmentation as (
    select
        *,
        
        -- 综合客户分群
        case 
            when customer_value_tier = 'A级（高价值）' and customer_activity_category = '核心活跃客户' 
                then 'VIP客户'
            when customer_value_tier = 'A级（高价值）' 
                then '高价值客户'
            when customer_value_tier = 'B级（中价值）' and growth_potential = '高潜力'
                then '潜力客户'
            when customer_lifecycle_stage = '新客户' and avg_order_value > 50
                then '优质新客'
            when customer_lifecycle_stage = '休眠客户' and total_spent > 500
                then '沉睡高价值客户'
            when customer_lifecycle_stage = '流失客户' and total_spent > 1000
                then '流失高价值客户'
            when total_orders = 0
                then '潜在客户'
            else '一般客户'
        end as comprehensive_segment,
        
        -- 营销活动标签
        case 
            when days_since_last_purchase between 30 and 90 then '近期流失风险'
            when days_since_last_purchase > 90 and total_spent > 200 then '高价值唤醒'
            when customer_lifecycle_stage = '新客户' then '新客培育'
            when purchase_behavior_pattern = '重度购买' then '忠诚度计划'
            when growth_potential = '高潜力' then '增长培育'
            else '常规维护'
        end as marketing_campaign_tag,
        
        -- 客户健康度预警
        case 
            when days_since_last_purchase > 180 and customer_value_tier in ('A级（高价值）', 'B级（中价值）') 
                then '高价值客户流失预警'
            when customer_health_score < 20 then '健康度严重预警'
            when activity_level = '休眠' and total_spent > 500 then '沉睡客户唤醒机会'
            when purchase_frequency_per_day < 0.01 and total_orders > 5 then '购买频率下降'
            else '正常'
        end as health_alert,
        
        -- 客户价值预测（简化版）
        round(
            total_spent * 
            case 
                when customer_lifecycle_stage = '新客户' then 3.0
                when customer_lifecycle_stage = '成长客户' then 2.5
                when customer_lifecycle_stage = '成熟客户' then 2.0
                when customer_lifecycle_stage = '稳定客户' then 1.8
                when customer_lifecycle_stage = '休眠客户' then 1.2
                when customer_lifecycle_stage = '流失客户' then 1.0
                else 1.5
            end
        ) as predicted_lifetime_value
        
    from customer_activity_enhanced
)

-- 最终客户维度表
select
    -- 基础信息
    customer_id,
    first_name,
    last_name,
    email,
    full_name,
    
    -- 原始分群
    customer_segment,
    data_quality_level,
    customer_created_at,
    customer_updated_at,
    
    -- 订单指标
    total_orders,
    completed_orders,
    pending_orders,
    cancelled_orders,
    total_spent,
    avg_order_value,
    max_order_value,
    min_order_value,
    first_order_date,
    last_order_date,
    high_value_orders,
    medium_value_orders,
    standard_value_orders,
    orders_last_30_days,
    orders_last_90_days,
    orders_last_year,
    spent_last_30_days,
    spent_last_90_days,
    spent_last_year,
    
    -- 活动指标
    customer_lifetime_days,
    purchase_frequency_per_day,
    days_since_last_purchase,
    avg_purchase_interval_days,
    activity_level,
    
    -- RFM分群
    recency_score,
    frequency_score,
    monetary_score,
    rfm_segment,
    
    -- 计算指标
    customer_health_score,
    customer_value_tier,
    
    -- 增强计算字段
    customer_activity_category,
    purchase_behavior_pattern,
    customer_lifecycle_stage,
    customer_loyalty_score,
    growth_potential,
    service_priority,
    comprehensive_segment,
    marketing_campaign_tag,
    health_alert,
    predicted_lifetime_value,
    
    -- 元数据
    _dbt_loaded_at,
    _dbt_invocation_id,
    
    -- 时间戳字段（用于增量更新）
    current_timestamp as dim_updated_at
    
from customer_segmentation

-- 排序优化：按业务重要性排序
order by 
    customer_value_tier,
    customer_health_score desc,
    total_spent desc,
    last_order_date desc

-- 注释：此维度表为业务分析提供全面的客户视图
-- 包含基础信息、行为指标、分群标签和业务洞察