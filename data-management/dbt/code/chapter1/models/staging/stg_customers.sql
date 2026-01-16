-- models/staging/stg_customers.sql
-- 第一个数据模型示例：客户基本信息表

{{ config(
    materialized='view',
    tags=['staging', 'customers']
) }}

-- 使用CTE（Common Table Expression）提高可读性
with source_data as (
    select
        id as customer_id,
        first_name,
        last_name,
        email,
        phone,
        created_at,
        updated_at,
        -- 添加计算字段：完整姓名
        first_name || ' ' || last_name as full_name,
        -- 添加数据质量检查字段
        case 
            when email is null then 'missing_email'
            when email not like '%@%.%' then 'invalid_email'
            else 'valid_email'
        end as email_status
    from {{ source('raw', 'customers') }}
    where deleted_at is null  -- 排除已删除的记录
)

select 
    customer_id,
    first_name,
    last_name,
    full_name,
    email,
    phone,
    email_status,
    created_at,
    updated_at,
    -- 添加时间戳字段
    current_timestamp as dbt_loaded_at
from source_data