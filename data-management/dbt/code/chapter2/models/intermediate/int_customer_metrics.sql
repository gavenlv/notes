-- models/intermediate/int_customer_metrics.sql
-- Intermediate层：客户指标计算

{{ config(
    materialized='table',
    tags=['intermediate', 'customers', 'metrics'],
    schema='intermediate'
) }}

with customer_orders as (
    select
        customer_id,
        count(*) as order_count,
        count(case when status = 'completed' then 1 end) as completed_orders,
        count(case when status = 'cancelled' then 1 end) as cancelled_orders,
        sum(case when status = 'completed' then total_amount else 0 end) as lifetime_value,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        avg(total_amount) as avg_order_value
    from {{ ref('stg_orders') }}
    group by customer_id
),

customer_activity as (
    select
        customer_id,
        count(distinct date_trunc('month', order_date)) as active_months,
        case 
            when max(order_date) >= current_date - interval '30 days' then 'active'
            when max(order_date) >= current_date - interval '90 days' then 'dormant'
            else 'inactive'
        end as activity_status
    from {{ ref('stg_orders') }}
    where status = 'completed'
    group by customer_id
)

select 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.full_name,
    c.email,
    c.country_code,
    c.created_at as customer_created_at,
    
    -- 订单指标
    coalesce(co.order_count, 0) as order_count,
    coalesce(co.completed_orders, 0) as completed_orders,
    coalesce(co.cancelled_orders, 0) as cancelled_orders,
    coalesce(co.lifetime_value, 0) as lifetime_value,
    coalesce(co.avg_order_value, 0) as avg_order_value,
    co.first_order_date,
    co.last_order_date,
    
    -- 活动指标
    coalesce(ca.active_months, 0) as active_months,
    coalesce(ca.activity_status, 'no_orders') as activity_status,
    
    -- 计算字段
    case 
        when co.lifetime_value > 1000 then 'VIP'
        when co.lifetime_value > 100 then 'Regular'
        when co.lifetime_value > 0 then 'New'
        else 'Prospect'
    end as customer_segment,
    
    case 
        when co.order_count > 0 then 
            date_part('day', current_date - co.last_order_date)
        else null
    end as days_since_last_order,
    
    current_timestamp as dbt_loaded_at
    
from {{ ref('stg_customers') }} c
left join customer_orders co on c.customer_id = co.customer_id
left join customer_activity ca on c.customer_id = ca.customer_id