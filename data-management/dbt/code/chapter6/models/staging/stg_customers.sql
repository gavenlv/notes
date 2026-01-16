-- 第6章：dbt最佳实践与项目结构
-- staging层 - 客户数据清洗模型
-- 演示标准化的数据清洗和转换流程

{{ config(
    materialized='view',
    tags=['staging', 'customers', 'data-cleaning'],
    persist_docs={'relation': true, 'columns': true},
    alias='stg_customers'
) }}

-- 模型描述
-- 此模型负责客户数据的标准化清洗和基础转换
-- 输入：raw_data.customers 源表
-- 输出：标准化的客户数据，包含数据质量标记

WITH source_data AS (
    SELECT
        -- 基础字段（保持原样）
        customer_id,
        first_name,
        last_name,
        email,
        phone,
        
        -- 地址信息标准化
        {{ standardize_address(address) }} as standardized_address,
        city,
        state,
        postal_code,
        country,
        
        -- 时间字段标准化
        created_at,
        updated_at,
        
        -- 业务状态字段
        status,
        customer_type,
        
        -- 元数据字段
        _source_system,
        _etl_loaded_at
        
    FROM {{ source('raw_data', 'customers') }}
    
    -- 数据过滤条件（可选）
    WHERE _etl_loaded_at >= DATEADD(day, -30, CURRENT_DATE)
),

cleaned_data AS (
    SELECT
        -- 标识字段
        customer_id,
        
        -- 个人信息清洗
        {{ trim_and_title_case('first_name') }} as first_name,
        {{ trim_and_title_case('last_name') }} as last_name,
        {{ standardize_email('email') }} as email,
        {{ format_phone_number('phone') }} as phone,
        
        -- 计算字段：全名
        {{ concat_names('first_name', 'last_name') }} as full_name,
        
        -- 地址信息清洗
        standardized_address,
        {{ trim_and_title_case('city') }} as city,
        UPPER(TRIM(state)) as state,
        {{ format_postal_code('postal_code', 'country') }} as postal_code,
        {{ standardize_country('country') }} as country,
        
        -- 时间字段处理
        created_at,
        updated_at,
        
        -- 计算字段：客户年龄（基于创建时间）
        {{ date_diff('created_at', 'CURRENT_DATE', 'year') }} as customer_age_years,
        
        -- 业务状态标准化
        {{ map_customer_status('status') }} as status,
        customer_type,
        
        -- 数据质量标记
        CASE 
            WHEN customer_id IS NULL THEN 'missing_customer_id'
            WHEN email IS NULL OR email = '' THEN 'missing_email'
            WHEN created_at IS NULL THEN 'missing_created_at'
            ELSE 'valid'
        END as data_quality_status,
        
        -- 数据质量评分（0-100）
        CASE 
            WHEN customer_id IS NULL THEN 0
            WHEN email IS NULL OR email = '' THEN 50
            WHEN created_at IS NULL THEN 75
            ELSE 100
        END as data_quality_score,
        
        -- 业务规则验证标记
        CASE 
            WHEN status = 'inactive' AND updated_at < DATEADD(year, -1, CURRENT_DATE) THEN 'potentially_archivable'
            WHEN customer_age_years < 0 THEN 'invalid_age'
            ELSE 'valid'
        END as business_validation_status,
        
        -- 元数据
        _source_system,
        _etl_loaded_at,
        
        -- 技术字段
        CURRENT_TIMESTAMP as _dbt_processed_at,
        '{{ invocation_id }}' as _dbt_invocation_id
        
    FROM source_data
),

final_validation AS (
    SELECT
        *,
        
        -- 最终数据验证
        CASE 
            WHEN data_quality_status != 'valid' THEN 'failed_quality_check'
            WHEN business_validation_status != 'valid' THEN 'failed_business_rule'
            ELSE 'passed'
        END as final_validation_status
        
    FROM cleaned_data
)

SELECT
    -- 标识字段
    customer_id,
    
    -- 个人信息
    first_name,
    last_name,
    full_name,
    email,
    phone,
    
    -- 地址信息
    standardized_address,
    city,
    state,
    postal_code,
    country,
    
    -- 时间信息
    created_at,
    updated_at,
    customer_age_years,
    
    -- 业务信息
    status,
    customer_type,
    
    -- 数据质量信息
    data_quality_status,
    data_quality_score,
    business_validation_status,
    final_validation_status,
    
    -- 元数据
    _source_system,
    _etl_loaded_at,
    _dbt_processed_at,
    _dbt_invocation_id
    
FROM final_validation

-- 模型级文档（自动生成到dbt文档中）
-- 此模型提供标准化的客户数据，包含完整的数据质量评估
-- 适用于下游的客户分析和报表需求

-- 字段说明：
-- customer_id: 客户唯一标识
-- first_name/last_name: 标准化后的姓名
-- email: 格式化的邮箱地址
-- phone: 标准化的电话号码
-- data_quality_status: 数据质量状态标记
-- data_quality_score: 数据质量评分（0-100）
-- business_validation_status: 业务规则验证状态
-- final_validation_status: 最终验证状态

-- 使用说明：
-- 1. 此模型应作为客户数据处理的起点
-- 2. 下游模型应基于final_validation_status过滤数据
-- 3. 数据质量评分可用于优先级处理

-- 测试覆盖：
-- 1. 数据完整性测试（非空、唯一性）
-- 2. 数据格式验证（邮箱、电话格式）
-- 3. 业务规则验证（状态、时间逻辑）

-- 性能考虑：
-- 1. 使用视图物化以减少存储
-- 2. 考虑对大表使用增量模型
-- 3. 监控查询性能和数据新鲜度