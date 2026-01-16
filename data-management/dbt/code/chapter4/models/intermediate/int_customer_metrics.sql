-- 客户指标计算模型 - 演示条件聚合宏的使用
{{ config(
    materialized='table',
    tags=['intermediate', 'customers', 'metrics', 'chapter4'],
    schema='intermediate'
) }}

with customer_orders as (
    select
        c.customer_id,
        c.full_name,
        c.email,
        c.country,
        c.city,
        c.age,
        c.data_quality_status,
        {{ count_by_category('o.status', ['pending', 'processing', 'shipped', 'delivered', 'cancelled']) }},
        {{ conditional_count('o.order_id', "o.status = 'delivered'") }} as completed_orders,
        {{ conditional_sum('o.total_amount', "o.status = 'delivered'") }} as total_revenue,
        {{ conditional_avg('o.total_amount', "o.status = 'delivered'") }} as avg_order_value,
        {{ conditional_min('o.total_amount', "o.status = 'delivered'") }} as min_order_value,
        {{ conditional_max('o.total_amount', "o.status = 'delivered'") }} as max_order_value,
        min(o.order_date) as first_order_date,
        max(o.order_date) as last_order_date,
        {{ date_diff('min(o.order_date)', 'max(o.order_date)', 'day') }} as customer_lifetime_days
    from {{ ref('stg_customers') }} c
    left join {{ ref('stg_orders') }} o on c.customer_id = o.customer_id
    group by 
        c.customer_id, c.full_name, c.email, c.country, c.city, c.age, c.data_quality_status
),

customer_activity as (
    select
        customer_id,
        {{ running_total('total_amount', 'customer_id', 'order_date') }} as cumulative_revenue,
        {{ moving_average('total_amount', 'customer_id', 'order_date', 3) }} as three_month_avg_revenue,
        {{ lag_difference('total_amount', 'customer_id', 'order_date', 1) }} as revenue_growth,
        {{ first_value_in_partition('order_date', 'customer_id', 'order_date') }} as cohort_date,
        {{ rank_within_partition('total_amount', 'customer_id', 'desc') }} as revenue_rank
    from {{ ref('stg_orders') }}
    where status = 'delivered'
),

customer_segmentation as (
    select
        co.customer_id,
        co.total_revenue,
        co.completed_orders,
        co.avg_order_value,
        co.customer_lifetime_days,
        
        -- 客户价值分群
        case 
            when co.total_revenue > 1000 then 'VIP'
            when co.total_revenue > 500 then 'PREMIUM'
            when co.total_revenue > 100 then 'STANDARD'
            else 'BASIC'
        end as value_segment,
        
        -- 客户活跃度分群
        case 
            when co.customer_lifetime_days > 365 then 'LONG_TERM'
            when co.customer_lifetime_days > 180 then 'MEDIUM_TERM'
            when co.customer_lifetime_days > 30 then 'SHORT_TERM'
            else 'NEW'
        end as tenure_segment,
        
        -- 购买频率分群
        case 
            when co.completed_orders > 10 then 'FREQUENT'
            when co.completed_orders > 5 then 'REGULAR'
            when co.completed_orders > 1 then 'OCCASIONAL'
            else 'ONE_TIME'
        end as frequency_segment,
        
        -- 客户生命周期价值 (CLV)
        co.total_revenue / nullif(co.customer_lifetime_days, 0) * 365 as estimated_clv,
        
        -- 客户健康度评分 (0-100)
        case 
            when co.data_quality_status = 'VALID' then 20 else 0
        end +
        case 
            when co.completed_orders > 0 then 30 else 0
        end +
        case 
            when co.customer_lifetime_days > 90 then 25 else 0
        end +
        case 
            when co.avg_order_value > 100 then 25 else 0
        end as health_score
        
    from customer_orders co
)

select
    co.customer_id,
    co.full_name,
    co.email,
    co.country,
    co.city,
    co.age,
    co.data_quality_status,
    
    -- 订单指标
    co.pending_count,
    co.processing_count,
    co.shipped_count,
    co.delivered_count as completed_orders,
    co.cancelled_count,
    co.total_revenue,
    co.avg_order_value,
    co.min_order_value,
    co.max_order_value,
    
    -- 时间指标
    co.first_order_date,
    co.last_order_date,
    co.customer_lifetime_days,
    
    -- 活动指标
    ca.cumulative_revenue,
    ca.three_month_avg_revenue,
    ca.revenue_growth,
    ca.cohort_date,
    ca.revenue_rank,
    
    -- 分群指标
    cs.value_segment,
    cs.tenure_segment,
    cs.frequency_segment,
    cs.estimated_clv,
    cs.health_score,
    
    -- 综合指标
    case 
        when cs.health_score >= 80 then 'EXCELLENT'
        when cs.health_score >= 60 then 'GOOD'
        when cs.health_score >= 40 then 'FAIR'
        else 'POOR'
    end as overall_health_status,
    
    {{ current_timestamp() }} as dbt_loaded_at
    
from customer_orders co
left join customer_activity ca on co.customer_id = ca.customer_id
left join customer_segmentation cs on co.customer_id = cs.customer_id