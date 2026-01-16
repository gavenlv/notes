-- 客户数据清洗模型 - 演示宏的使用
{{ config(
    materialized='view',
    tags=['staging', 'customers', 'chapter4'],
    schema='staging'
) }}

with customer_data as (
    select
        customer_id,
        {{ trim_string('first_name') }} as first_name,
        {{ trim_string('last_name') }} as last_name,
        {{ concat_strings(['first_name', 'last_name'], ' ') }} as full_name,
        {{ lower_case('email') }} as email,
        {{ normalize_phone('phone_number') }} as phone_number,
        {{ validate_email_format('email') }} as is_valid_email,
        {{ validate_string_length('first_name', 1, 50) }} as validated_first_name,
        {{ validate_string_length('last_name', 1, 50) }} as validated_last_name,
        country,
        city,
        {{ format_date('created_at') }} as created_date,
        {{ format_date('updated_at') }} as updated_date,
        {{ date_diff('created_at', 'updated_at', 'day') }} as days_since_update,
        {{ age_in_years('birth_date') }} as age,
        {{ is_weekend('created_at') }} as created_on_weekend,
        {{ business_days_between('created_at', 'updated_at') }} as business_days_between_updates
    from {{ source('raw', 'customers') }}
),

validated_customers as (
    select
        *,
        case 
            when is_valid_email and validated_first_name is not null and validated_last_name is not null
            then 'VALID'
            else 'INVALID'
        end as data_quality_status
    from customer_data
)

select
    customer_id,
    first_name,
    last_name,
    full_name,
    email,
    phone_number,
    is_valid_email,
    validated_first_name,
    validated_last_name,
    country,
    city,
    created_date,
    updated_date,
    days_since_update,
    age,
    created_on_weekend,
    business_days_between_updates,
    data_quality_status,
    {{ current_timestamp() }} as dbt_loaded_at
from validated_customers