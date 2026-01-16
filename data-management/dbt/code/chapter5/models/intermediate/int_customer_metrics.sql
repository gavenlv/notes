-- 客户指标计算模型 - 第5章：数据源与连接配置
-- 演示复杂指标计算和聚合逻辑

{{ config(
    materialized='table',
    tags=['intermediate', 'customers', 'metrics', 'chapter5'],
    persist_docs={"relation": true, "columns": true}
) }}

-- 基础客户数据
with base_customers as (
    select
        customer_id,
        first_name,
        last_name,
        email,
        full_name,
        customer_segment,
        data_quality_level,
        created_at,
        updated_at
    from {{ ref('stg_customers') }}
    where is_valid_record = true
),

-- 客户订单数据
customer_orders as (
    select
        customer_id,
        order_id,
        order_date,
        total_amount,
        status,
        order_value_category,
        order_stage
    from {{ ref('stg_orders') }}
    where is_valid_record = true
),

-- 客户订单聚合指标
order_metrics as (
    select
        customer_id,
        
        -- 订单数量指标
        count(*) as total_orders,
        count(case when order_stage = '已完成' then 1 end) as completed_orders,
        count(case when order_stage = '进行中' then 1 end) as pending_orders,
        count(case when order_stage = '已取消' then 1 end) as cancelled_orders,
        
        -- 金额指标
        sum(total_amount) as total_spent,
        avg(total_amount) as avg_order_value,
        max(total_amount) as max_order_value,
        min(total_amount) as min_order_value,
        
        -- 时间指标
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        
        -- 价值分类指标
        count(case when order_value_category = '高价值订单' then 1 end) as high_value_orders,
        count(case when order_value_category = '中价值订单' then 1 end) as medium_value_orders,
        count(case when order_value_category = '普通订单' then 1 end) as standard_value_orders,
        
        -- 最近活动指标
        count(case when order_date >= current_date - interval '30 days' then 1 end) as orders_last_30_days,
        count(case when order_date >= current_date - interval '90 days' then 1 end) as orders_last_90_days,
        count(case when order_date >= current_date - interval '365 days' then 1 end) as orders_last_year,
        
        -- 金额时间窗口指标
        sum(case when order_date >= current_date - interval '30 days' then total_amount else 0 end) as spent_last_30_days,
        sum(case when order_date >= current_date - interval '90 days' then total_amount else 0 end) as spent_last_90_days,
        sum(case when order_date >= current_date - interval '365 days' then total_amount else 0 end) as spent_last_year
        
    from customer_orders
    group by customer_id
),

-- 客户活动指标
activity_metrics as (
    select
        customer_id,
        
        -- 客户生命周期
        datediff('day', min(order_date), max(order_date)) as customer_lifetime_days,
        
        -- 购买频率
        case 
            when datediff('day', min(order_date), max(order_date)) > 0 then
                count(*) / datediff('day', min(order_date), max(order_date))::float
            else 0
        end as purchase_frequency_per_day,
        
        -- 最近购买间隔
        datediff('day', max(order_date), current_date) as days_since_last_purchase,
        
        -- 购买间隔统计
        avg(datediff('day', lag(order_date) over (partition by customer_id order by order_date), order_date)) 
            as avg_purchase_interval_days,
        
        -- 活跃度评分
        case 
            when datediff('day', max(order_date), current_date) <= 30 then '高活跃'
            when datediff('day', max(order_date), current_date) <= 90 then '中活跃'
            when datediff('day', max(order_date), current_date) <= 365 then '低活跃'
            else '休眠'
        end as activity_level
        
    from customer_orders
    group by customer_id
),

-- 客户分群指标
segmentation_metrics as (
    select
        customer_id,
        
        -- RFM分群（简化版）
        case 
            when datediff('day', max(order_date), current_date) <= 30 then 5
            when datediff('day', max(order_date), current_date) <= 90 then 4
            when datediff('day', max(order_date), current_date) <= 180 then 3
            when datediff('day', max(order_date), current_date) <= 365 then 2
            else 1
        end as recency_score,
        
        case 
            when count(*) >= 10 then 5
            when count(*) >= 5 then 4
            when count(*) >= 3 then 3
            when count(*) >= 2 then 2
            else 1
        end as frequency_score,
        
        case 
            when sum(total_amount) >= 1000 then 5
            when sum(total_amount) >= 500 then 4
            when sum(total_amount) >= 200 then 3
            when sum(total_amount) >= 100 then 2
            else 1
        end as monetary_score,
        
        -- 综合RFM分群
        case 
            when recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4 then '高价值客户'
            when recency_score >= 3 and frequency_score >= 3 and monetary_score >= 3 then '中价值客户'
            when recency_score <= 2 and frequency_score <= 2 and monetary_score <= 2 then '低价值客户'
            else '一般客户'
        end as rfm_segment
        
    from customer_orders
    group by customer_id
)

-- 最终客户指标整合
select
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.full_name,
    c.customer_segment,
    c.data_quality_level,
    c.created_at as customer_created_at,
    c.updated_at as customer_updated_at,
    
    -- 订单指标
    coalesce(o.total_orders, 0) as total_orders,
    coalesce(o.completed_orders, 0) as completed_orders,
    coalesce(o.pending_orders, 0) as pending_orders,
    coalesce(o.cancelled_orders, 0) as cancelled_orders,
    
    -- 金额指标
    coalesce(o.total_spent, 0) as total_spent,
    coalesce(o.avg_order_value, 0) as avg_order_value,
    coalesce(o.max_order_value, 0) as max_order_value,
    coalesce(o.min_order_value, 0) as min_order_value,
    
    -- 时间指标
    o.first_order_date,
    o.last_order_date,
    
    -- 价值分类指标
    coalesce(o.high_value_orders, 0) as high_value_orders,
    coalesce(o.medium_value_orders, 0) as medium_value_orders,
    coalesce(o.standard_value_orders, 0) as standard_value_orders,
    
    -- 最近活动指标
    coalesce(o.orders_last_30_days, 0) as orders_last_30_days,
    coalesce(o.orders_last_90_days, 0) as orders_last_90_days,
    coalesce(o.orders_last_year, 0) as orders_last_year,
    
    coalesce(o.spent_last_30_days, 0) as spent_last_30_days,
    coalesce(o.spent_last_90_days, 0) as spent_last_90_days,
    coalesce(o.spent_last_year, 0) as spent_last_year,
    
    -- 活动指标
    coalesce(a.customer_lifetime_days, 0) as customer_lifetime_days,
    coalesce(a.purchase_frequency_per_day, 0) as purchase_frequency_per_day,
    coalesce(a.days_since_last_purchase, 0) as days_since_last_purchase,
    coalesce(a.avg_purchase_interval_days, 0) as avg_purchase_interval_days,
    a.activity_level,
    
    -- 分群指标
    s.recency_score,
    s.frequency_score,
    s.monetary_score,
    s.rfm_segment,
    
    -- 综合健康度评分（0-100）
    case 
        when o.total_orders = 0 then 0
        else 
            round(
                (coalesce(o.completed_orders, 0) * 30 / o.total_orders) +  -- 完成率权重30%
                (case when a.days_since_last_purchase <= 90 then 30 else 0 end) +  -- 最近活跃权重30%
                (case when o.avg_order_value > 100 then 20 else o.avg_order_value / 5 end) +  -- 平均订单价值权重20%
                (case when o.total_orders >= 3 then 20 else o.total_orders * 6.67 end)  -- 订单数量权重20%
            )
    end as customer_health_score,
    
    -- 客户价值等级
    case 
        when customer_health_score >= 80 then 'A级（高价值）'
        when customer_health_score >= 60 then 'B级（中价值）'
        when customer_health_score >= 40 then 'C级（一般价值）'
        when customer_health_score >= 20 then 'D级（低价值）'
        else 'E级（潜在流失）'
    end as customer_value_tier,
    
    -- 元数据
    current_timestamp as _dbt_loaded_at,
    '{{ invocation_id }}' as _dbt_invocation_id
    
from base_customers c
left join order_metrics o on c.customer_id = o.customer_id
left join activity_metrics a on c.customer_id = a.customer_id
left join segmentation_metrics s on c.customer_id = s.customer_id

-- 排序：按客户价值和活跃度排序
order by customer_health_score desc, total_spent desc, last_order_date desc