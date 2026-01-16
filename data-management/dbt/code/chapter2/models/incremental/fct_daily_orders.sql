-- models/incremental/fct_daily_orders.sql
-- 增量模型：每日订单事实表

{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='fail',
    tags=['incremental', 'fact', 'orders'],
    schema='marts'
) }}

with order_details as (
    select
        o.order_id,
        o.customer_id,
        o.order_date,
        o.status,
        o.total_amount,
        o.currency,
        o.created_at,
        o.updated_at,
        
        -- 客户信息
        c.first_name,
        c.last_name,
        c.country_code,
        c.customer_segment,
        
        -- 时间维度
        date_trunc('day', o.order_date) as order_day,
        date_trunc('week', o.order_date) as order_week,
        date_trunc('month', o.order_date) as order_month,
        date_trunc('quarter', o.order_date) as order_quarter,
        date_trunc('year', o.order_date) as order_year,
        
        -- 业务逻辑
        case 
            when o.status = 'completed' then o.total_amount
            else 0
        end as revenue,
        
        case 
            when o.status = 'completed' then 1
            else 0
        end as completed_order_flag,
        
        -- 汇率转换（示例）
        case 
            when o.currency = 'USD' then o.total_amount * 1.0
            when o.currency = 'EUR' then o.total_amount * 1.1
            when o.currency = 'GBP' then o.total_amount * 1.3
            else o.total_amount
        end as total_amount_usd
        
    from {{ ref('stg_orders') }} o
    left join {{ ref('dim_customers') }} c on o.customer_id = c.customer_id
    
    {% if is_incremental() %}
        -- 增量模式：只处理新数据
        where o.updated_at >= (
            select max(updated_at) from {{ this }}
        )
    {% endif %}
)

select
    order_id,
    customer_id,
    order_date,
    status,
    total_amount,
    currency,
    first_name,
    last_name,
    country_code,
    customer_segment,
    order_day,
    order_week,
    order_month,
    order_quarter,
    order_year,
    revenue,
    completed_order_flag,
    total_amount_usd,
    created_at,
    updated_at,
    current_timestamp as dbt_loaded_at
    
from order_details