-- models/staging/stg_orders.sql
-- Staging层：订单数据清洗和基础转换

{{ config(
    materialized='view',
    tags=['staging', 'orders'],
    schema='staging'
) }}

with source_data as (
    select
        id as order_id,
        customer_id,
        order_date::date as order_date,
        status,
        total_amount::decimal(10,2) as total_amount,
        currency,
        -- 日期时间转换
        created_at::timestamp as created_at,
        updated_at::timestamp as updated_at,
        deleted_at::timestamp as deleted_at,
        -- 数据质量检查
        case 
            when total_amount < 0 then 'invalid'
            when order_date > current_date then 'future_date'
            else 'valid'
        end as amount_status,
        case 
            when status not in ('pending', 'completed', 'cancelled') then 'invalid'
            else 'valid'
        end as status_status
    from {{ source('raw', 'orders') }}
    where deleted_at is null
)

select 
    order_id,
    customer_id,
    order_date,
    status,
    total_amount,
    currency,
    amount_status,
    status_status,
    created_at,
    updated_at,
    current_timestamp as dbt_loaded_at
from source_data