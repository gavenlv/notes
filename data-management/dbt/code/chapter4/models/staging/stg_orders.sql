-- 订单数据清洗模型 - 演示宏的使用
{{ config(
    materialized='view',
    tags=['staging', 'orders', 'chapter4'],
    schema='staging'
) }}

with order_data as (
    select
        order_id,
        customer_id,
        {{ validate_not_null('order_id', '订单ID不能为空') }} as validated_order_id,
        {{ validate_not_null('customer_id', '客户ID不能为空') }} as validated_customer_id,
        {{ validate_numeric_range('total_amount', 0, 100000, '订单金额必须在0-100000之间') }} as validated_amount,
        {{ format_date('order_date') }} as order_date,
        {{ format_date('created_at') }} as created_date,
        {{ format_date('updated_at') }} as updated_date,
        status,
        {{ validate_enum_values('status', ['pending', 'processing', 'shipped', 'delivered', 'cancelled'], '订单状态无效') }} as validated_status,
        payment_method,
        shipping_address,
        {{ validate_string_length('shipping_address', 5, 200, '收货地址长度必须在5-200字符之间') }} as validated_shipping_address,
        {{ date_diff('order_date', 'created_at', 'day') }} as days_between_order_and_creation,
        {{ is_weekend('order_date') }} as ordered_on_weekend,
        {{ get_month_start('order_date') }} as order_month_start
    from {{ source('raw', 'orders') }}
),

order_metrics as (
    select
        *,
        case 
            when validated_amount > 1000 then 'HIGH_VALUE'
            when validated_amount > 100 then 'MEDIUM_VALUE'
            else 'LOW_VALUE'
        end as order_value_category,
        case 
            when validated_status in ('delivered', 'shipped') then 'COMPLETED'
            when validated_status = 'cancelled' then 'CANCELLED'
            else 'IN_PROGRESS'
        end as order_stage,
        {{ safe_divide('validated_amount', 'days_between_order_and_creation', 0) }} as daily_order_rate
    from order_data
)

select
    order_id,
    customer_id,
    validated_order_id,
    validated_customer_id,
    validated_amount as total_amount,
    order_date,
    created_date,
    updated_date,
    validated_status as status,
    payment_method,
    validated_shipping_address as shipping_address,
    days_between_order_and_creation,
    ordered_on_weekend,
    order_month_start,
    order_value_category,
    order_stage,
    daily_order_rate,
    {{ current_timestamp() }} as dbt_loaded_at
from order_metrics