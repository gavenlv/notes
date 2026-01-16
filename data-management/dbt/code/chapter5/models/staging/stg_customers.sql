-- 客户数据清洗模型 - 第5章：数据源与连接配置
-- 演示如何使用source()函数引用外部数据源

{{ config(
    materialized='view',
    tags=['staging', 'customers', 'chapter5'],
    persist_docs={"relation": true, "columns": true}
) }}

-- 使用source()函数引用原始数据源
with raw_customers as (
    select
        customer_id,
        first_name,
        last_name,
        email,
        phone_number,
        created_at,
        updated_at
    from {{ source('raw_data', 'customers') }}
    where created_at >= '2020-01-01'  -- 数据过滤示例
),

-- 数据清洗和转换
cleaned_customers as (
    select
        -- 基础字段
        customer_id,
        
        -- 姓名处理
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        
        -- 邮箱标准化
        lower(trim(email)) as email,
        
        -- 电话号码格式化
        case 
            when phone_number is not null then 
                regexp_replace(phone_number, '[^0-9]', '', 'g')
            else null
        end as phone_number,
        
        -- 时间字段
        created_at,
        updated_at,
        
        -- 计算字段
        concat(trim(first_name), ' ', trim(last_name)) as full_name,
        
        -- 数据质量标记
        case 
            when customer_id is null then 'ERROR: customer_id为空'
            when first_name is null then 'ERROR: first_name为空'
            when last_name is null then 'ERROR: last_name为空'
            when email is null then 'ERROR: email为空'
            when created_at is null then 'ERROR: created_at为空'
            when updated_at is null then 'ERROR: updated_at为空'
            when email not like '%@%.%' then 'WARNING: 邮箱格式异常'
            when length(trim(first_name)) = 0 then 'WARNING: first_name为空字符串'
            when length(trim(last_name)) = 0 then 'WARNING: last_name为空字符串'
            else 'VALID'
        end as data_quality_status,
        
        -- 数据质量评分（0-100）
        case 
            when customer_id is null then 0
            when first_name is null then 20
            when last_name is null then 40
            when email is null then 60
            when created_at is null then 80
            when updated_at is null then 90
            when email not like '%@%.%' then 95
            when length(trim(first_name)) = 0 then 98
            when length(trim(last_name)) = 0 then 99
            else 100
        end as data_quality_score,
        
        -- 元数据字段
        current_timestamp as _dbt_loaded_at,
        '{{ invocation_id }}' as _dbt_invocation_id
        
    from raw_customers
),

-- 数据验证和业务规则应用
validated_customers as (
    select
        *,
        
        -- 业务规则验证
        case 
            when data_quality_status = 'VALID' then true
            else false
        end as is_valid_record,
        
        -- 客户分类
        case 
            when created_at >= current_date - interval '1 year' then '新客户'
            when created_at >= current_date - interval '3 years' then '活跃客户'
            else '老客户'
        end as customer_segment,
        
        -- 客户状态（基于数据质量）
        case 
            when data_quality_score >= 90 then '优质数据'
            when data_quality_score >= 70 then '一般数据'
            else '需要修复'
        end as data_quality_level
        
    from cleaned_customers
)

-- 最终输出
select
    customer_id,
    first_name,
    last_name,
    email,
    phone_number,
    created_at,
    updated_at,
    full_name,
    data_quality_status,
    data_quality_score,
    is_valid_record,
    customer_segment,
    data_quality_level,
    _dbt_loaded_at,
    _dbt_invocation_id
    
from validated_customers

-- 数据过滤（可选）
where is_valid_record = true  -- 只保留有效记录