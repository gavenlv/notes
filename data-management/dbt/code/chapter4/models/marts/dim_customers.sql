-- 客户维度表 - 演示动态SQL生成宏的使用
{{ config(
    materialized='table',
    tags=['marts', 'dimension', 'customers', 'chapter4'],
    schema='marts',
    indexes=[
      {'columns': ['customer_id'], 'unique': true},
      {'columns': ['email']},
      {'columns': ['country', 'city']}
    ]
) }}

-- 使用动态SQL生成宏创建完整的维度表
{{ generate_dynamic_model(
    model_name='dim_customers',
    source_tables=[
        {'name': 'customer_metrics', 'ref': 'int_customer_metrics'}
    ],
    select_columns=[
        'customer_id',
        'full_name',
        'email',
        'country',
        'city',
        'age',
        'data_quality_status',
        'pending_count',
        'processing_count',
        'shipped_count',
        'completed_orders',
        'cancelled_count',
        'total_revenue',
        'avg_order_value',
        'min_order_value',
        'max_order_value',
        'first_order_date',
        'last_order_date',
        'customer_lifetime_days',
        'cumulative_revenue',
        'three_month_avg_revenue',
        'revenue_growth',
        'cohort_date',
        'revenue_rank',
        'value_segment',
        'tenure_segment',
        'frequency_segment',
        'estimated_clv',
        'health_score',
        'overall_health_status'
    ],
    where_conditions='data_quality_status = \'VALID\'',
    order_by_columns=['total_revenue desc']
) }}

-- 添加计算字段和业务逻辑
select
    cm.*,
    
    -- 客户活跃度指标
    case 
        when cm.customer_lifetime_days <= 30 then 'NEW_CUSTOMER'
        when cm.last_order_date >= {{ add_days('current_date', -90) }} then 'ACTIVE'
        when cm.last_order_date >= {{ add_days('current_date', -180) }} then 'DORMANT'
        else 'INACTIVE'
    end as activity_status,
    
    -- 客户价值等级
    case 
        when cm.total_revenue > 5000 then 'PLATINUM'
        when cm.total_revenue > 2000 then 'GOLD'
        when cm.total_revenue > 500 then 'SILVER'
        when cm.total_revenue > 100 then 'BRONZE'
        else 'STANDARD'
    end as value_tier,
    
    -- 购买频率分析
    case 
        when cm.completed_orders = 0 then 'NO_PURCHASE'
        when cm.completed_orders = 1 then 'ONE_TIME'
        when cm.completed_orders between 2 and 5 then 'OCCASIONAL'
        when cm.completed_orders between 6 and 10 then 'REGULAR'
        else 'FREQUENT'
    end as purchase_frequency,
    
    -- 客户忠诚度评分 (0-100)
    (
        case when cm.completed_orders >= 1 then 20 else 0 end +
        case when cm.customer_lifetime_days >= 180 then 20 else 0 end +
        case when cm.avg_order_value >= 100 then 20 else 0 end +
        case when cm.revenue_growth > 0 then 20 else 0 end +
        case when cm.activity_status = 'ACTIVE' then 20 else 0 end
    ) as loyalty_score,
    
    -- 客户生命周期阶段
    case 
        when cm.completed_orders = 0 then 'PROSPECT'
        when cm.completed_orders = 1 then 'FIRST_TIME'
        when cm.completed_orders between 2 and 5 then 'GROWING'
        when cm.completed_orders > 5 and cm.activity_status = 'ACTIVE' then 'LOYAL'
        when cm.activity_status = 'DORMANT' then 'AT_RISK'
        else 'CHURNED'
    end as lifecycle_stage,
    
    -- 地域分析
    case 
        when cm.country in ('US', 'CA') then 'NORTH_AMERICA'
        when cm.country in ('GB', 'DE', 'FR', 'IT', 'ES') then 'EUROPE'
        when cm.country in ('CN', 'JP', 'KR', 'IN') then 'ASIA'
        when cm.country in ('AU', 'NZ') then 'OCEANIA'
        else 'OTHER'
    end as region,
    
    -- 年龄分组
    case 
        when cm.age < 18 then 'UNDER_18'
        when cm.age between 18 and 25 then '18_25'
        when cm.age between 26 and 35 then '26_35'
        when cm.age between 36 and 45 then '36_45'
        when cm.age between 46 and 55 then '46_55'
        when cm.age between 56 and 65 then '56_65'
        else 'OVER_65'
    end as age_group,
    
    -- 数据质量指标
    case 
        when cm.email is not null and cm.full_name is not null and cm.country is not null 
        then 'COMPLETE'
        else 'INCOMPLETE'
    end as profile_completeness,
    
    -- 业务优先级
    case 
        when cm.value_tier = 'PLATINUM' and cm.activity_status = 'ACTIVE' then 'HIGHEST_PRIORITY'
        when cm.value_tier in ('GOLD', 'SILVER') and cm.activity_status = 'ACTIVE' then 'HIGH_PRIORITY'
        when cm.value_tier = 'PLATINUM' and cm.activity_status = 'DORMANT' then 'MEDIUM_PRIORITY'
        when cm.lifecycle_stage = 'AT_RISK' then 'RETENTION_PRIORITY'
        else 'STANDARD_PRIORITY'
    end as business_priority,
    
    -- 时间维度字段
    {{ get_month_start('cm.first_order_date') }} as first_order_month,
    {{ get_month_start('cm.last_order_date') }} as last_order_month,
    {{ fiscal_year('cm.first_order_date') }} as first_order_fiscal_year,
    
    {{ current_timestamp() }} as dbt_loaded_at
    
from customer_metrics cm
where cm.data_quality_status = 'VALID'