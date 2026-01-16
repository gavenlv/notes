-- snapshots/customers_snapshot.sql
-- 客户数据快照：跟踪历史变化

{% snapshot customers_snapshot %}

{{ config(
    target_schema='snapshots',
    unique_key='customer_id',
    strategy='timestamp',
    updated_at='updated_at',
    invalidate_hard_deletes=True
) }}

select
    customer_id,
    first_name,
    last_name,
    email,
    phone,
    country_code,
    created_at,
    updated_at,
    dbt_loaded_at
from {{ ref('stg_customers') }}

{% endsnapshot %}