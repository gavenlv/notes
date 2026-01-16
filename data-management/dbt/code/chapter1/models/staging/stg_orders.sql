-- models/staging/stg_orders.sql
-- 订单数据模型示例

{{ config(
    materialized='view',
    tags=['staging', 'orders']
) }}

with source_data as (
    select
        id as order_id,
        customer_id,
        order_date,
        status,
        total_amount,
        currency,
        created_at,
        updated_at,
        -- 添加数据验证
        case 
            when total_amount < 0 then 'invalid_amount'
            when order_date > current_date then 'future_date'
            else 'valid'
        end as data_status
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
    data_status,
    created_at,
    updated_at,
    current_timestamp as dbt_loaded_at
from source_data