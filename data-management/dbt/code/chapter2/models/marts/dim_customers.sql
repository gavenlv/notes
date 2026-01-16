-- models/marts/dim_customers.sql
-- Marts层：客户维度表

{{ config(
    materialized='table',
    tags=['marts', 'dimension', 'customers'],
    schema='marts',
    -- 添加索引优化查询性能
    indexes=[
        {'columns': ['customer_id'], 'type': 'btree'},
        {'columns': ['customer_segment'], 'type': 'btree'},
        {'columns': ['activity_status'], 'type': 'btree'}
    ]
) }}

select
    customer_id,
    first_name,
    last_name,
    full_name,
    email,
    country_code,
    customer_created_at,
    
    -- 订单相关指标
    order_count,
    completed_orders,
    cancelled_orders,
    lifetime_value,
    avg_order_value,
    first_order_date,
    last_order_date,
    
    -- 活动指标
    active_months,
    activity_status,
    days_since_last_order,
    
    -- 客户分群
    customer_segment,
    
    -- 计算客户价值等级
    case 
        when lifetime_value >= 5000 then 'Platinum'
        when lifetime_value >= 1000 then 'Gold'
        when lifetime_value >= 500 then 'Silver'
        when lifetime_value > 0 then 'Bronze'
        else 'Prospect'
    end as value_tier,
    
    -- 计算客户活跃度
    case 
        when days_since_last_order <= 30 then 'Highly Active'
        when days_since_last_order <= 90 then 'Moderately Active'
        when days_since_last_order <= 180 then 'Low Activity'
        when days_since_last_order > 180 then 'Inactive'
        else 'No Orders'
    end as engagement_level,
    
    -- 计算订单频率
    case 
        when order_count > 0 and 
             date_part('day', last_order_date - first_order_date) > 0 then
            order_count / date_part('day', last_order_date - first_order_date) * 30
        else 0
    end as monthly_order_frequency,
    
    -- 数据质量标记
    case 
        when email_status = 'valid' and phone_status = 'valid' then 'High Quality'
        when email_status = 'valid' or phone_status = 'valid' then 'Medium Quality'
        else 'Low Quality'
    end as data_quality,
    
    dbt_loaded_at
    
from {{ ref('int_customer_metrics') }}