-- 订单数据清洗模型 - 第5章：数据源与连接配置
-- 演示多数据源引用和复杂数据转换

{{ config(
    materialized='view',
    tags=['staging', 'orders', 'chapter5'],
    persist_docs={"relation": true, "columns": true}
) }}

-- 引用多个数据源：订单数据和产品数据
with raw_orders as (
    select
        order_id,
        customer_id,
        order_date,
        total_amount,
        status
    from {{ source('raw_data', 'orders') }}
    where order_date >= '2020-01-01'
),

-- 外部产品数据（演示跨数据源引用）
product_info as (
    select
        product_id,
        product_name,
        category,
        price
    from {{ source('external_system', 'product_catalog') }}
    where last_updated >= current_date - interval '30 days'
),

-- 基础数据清洗
cleaned_orders as (
    select
        -- 订单基本信息
        order_id,
        customer_id,
        
        -- 日期处理
        cast(order_date as date) as order_date,
        
        -- 金额处理
        round(cast(total_amount as numeric), 2) as total_amount,
        
        -- 状态标准化
        lower(trim(status)) as status,
        
        -- 计算字段
        extract(year from order_date) as order_year,
        extract(month from order_date) as order_month,
        extract(quarter from order_date) as order_quarter,
        
        -- 业务分类
        case 
            when total_amount < 50 then '小额订单'
            when total_amount < 200 then '中等订单'
            when total_amount < 1000 then '大额订单'
            else '超大额订单'
        end as order_size_category,
        
        -- 订单阶段
        case 
            when status in ('pending', 'processing') then '进行中'
            when status in ('shipped', 'delivered') then '已完成'
            when status in ('cancelled', 'refunded') then '已取消'
            else '未知状态'
        end as order_stage,
        
        -- 数据质量检查
        case 
            when order_id is null then 'ERROR: order_id为空'
            when customer_id is null then 'ERROR: customer_id为空'
            when order_date is null then 'ERROR: order_date为空'
            when total_amount is null then 'ERROR: total_amount为空'
            when status is null then 'ERROR: status为空'
            when total_amount < 0 then 'WARNING: 金额为负数'
            when total_amount > 100000 then 'WARNING: 金额异常大'
            when order_date > current_date then 'WARNING: 订单日期在未来'
            when status not in ('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded') 
                then 'WARNING: 状态值异常'
            else 'VALID'
        end as data_quality_status,
        
        -- 数据质量评分
        case 
            when order_id is null then 0
            when customer_id is null then 20
            when order_date is null then 40
            when total_amount is null then 60
            when status is null then 80
            when total_amount < 0 then 85
            when total_amount > 100000 then 90
            when order_date > current_date then 95
            when status not in ('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded') then 98
            else 100
        end as data_quality_score,
        
        -- 元数据
        current_timestamp as _dbt_loaded_at,
        '{{ invocation_id }}' as _dbt_invocation_id
        
    from raw_orders
),

-- 关联客户信息（演示模型间引用）
customer_info as (
    select
        customer_id,
        first_name,
        last_name,
        email,
        full_name,
        customer_segment
    from {{ ref('stg_customers') }}
    where is_valid_record = true
),

-- 订单增强信息
enhanced_orders as (
    select
        o.*,
        
        -- 客户信息
        c.first_name as customer_first_name,
        c.last_name as customer_last_name,
        c.email as customer_email,
        c.full_name as customer_full_name,
        c.customer_segment,
        
        -- 业务逻辑增强
        case 
            when o.data_quality_status = 'VALID' then true
            else false
        end as is_valid_record,
        
        -- 订单价值分类
        case 
            when o.total_amount > 1000 then '高价值订单'
            when o.total_amount > 200 then '中价值订单'
            else '普通订单'
        end as order_value_category,
        
        -- 季节性标记
        case 
            when extract(month from o.order_date) in (12, 1, 2) then '冬季'
            when extract(month from o.order_date) in (3, 4, 5) then '春季'
            when extract(month from o.order_date) in (6, 7, 8) then '夏季'
            when extract(month from o.order_date) in (9, 10, 11) then '秋季'
        end as order_season,
        
        -- 工作日/周末标记
        case 
            when extract(dow from o.order_date) in (0, 6) then '周末'
            else '工作日'
        end as order_day_type
        
    from cleaned_orders o
    left join customer_info c
        on o.customer_id = c.customer_id
),

-- 最终数据验证
final_orders as (
    select
        *,
        
        -- 最终验证逻辑
        case 
            when customer_id is not null and customer_first_name is null then 'WARNING: 客户信息缺失'
            when order_date < '2020-01-01' then 'WARNING: 历史订单数据'
            else 'VALID'
        end as final_validation_status,
        
        -- 数据新鲜度
        case 
            when order_date >= current_date - interval '7 days' then '最近7天'
            when order_date >= current_date - interval '30 days' then '最近30天'
            when order_date >= current_date - interval '90 days' then '最近90天'
            else '历史数据'
        end as data_recency
        
    from enhanced_orders
)

-- 输出最终结果
select
    order_id,
    customer_id,
    order_date,
    total_amount,
    status,
    order_year,
    order_month,
    order_quarter,
    order_size_category,
    order_stage,
    data_quality_status,
    data_quality_score,
    customer_first_name,
    customer_last_name,
    customer_email,
    customer_full_name,
    customer_segment,
    is_valid_record,
    order_value_category,
    order_season,
    order_day_type,
    final_validation_status,
    data_recency,
    _dbt_loaded_at,
    _dbt_invocation_id
    
from final_orders

-- 过滤条件：只保留有效记录
where is_valid_record = true

-- 按日期排序，便于增量处理
order by order_date desc, order_id