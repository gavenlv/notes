-- models/staging/stg_customers.sql
-- Staging层：客户数据清洗和基础转换

{{ config(
    materialized='view',
    tags=['staging', 'customers'],
    schema='staging'
) }}

with source_data as (
    select
        id as customer_id,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        lower(email) as email,
        phone,
        country_code,
        -- 日期时间转换
        created_at::timestamp as created_at,
        updated_at::timestamp as updated_at,
        deleted_at::timestamp as deleted_at,
        -- 计算字段
        first_name || ' ' || last_name as full_name,
        -- 数据质量检查
        case 
            when email is null then 'missing'
            when email not like '%@%.%' then 'invalid'
            else 'valid'
        end as email_status,
        case 
            when phone is null then 'missing'
            when length(phone) < 10 then 'invalid'
            else 'valid'
        end as phone_status
    from {{ source('raw', 'customers') }}
    -- 排除已删除的记录
    where deleted_at is null
)

select 
    customer_id,
    first_name,
    last_name,
    full_name,
    email,
    phone,
    country_code,
    email_status,
    phone_status,
    created_at,
    updated_at,
    -- 添加处理时间戳
    current_timestamp as dbt_loaded_at
from source_data