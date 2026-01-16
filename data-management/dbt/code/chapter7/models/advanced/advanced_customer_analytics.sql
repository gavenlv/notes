-- 第7章：高级客户分析模型
-- 演示复杂宏、自定义物料化策略和钩子函数的综合应用

{{ config(
    materialized='table',
    tags=['advanced', 'customer-analytics', 'complex-macros'],
    persist_docs={"relation": true, "columns": true}
) }}

-- 使用动态SQL生成器宏
{%- set customer_segments_query = generate_dynamic_query(
    base_table='customers',
    select_columns=['customer_id', 'segment', 'lifetime_value'],
    where_conditions=['status = \'active\'', 'lifetime_value > 1000'],
    group_by_columns=['segment'],
    order_by_columns=['lifetime_value DESC']
) %}

-- 使用递归CTE生成器宏（组织层级分析）
{%- set org_hierarchy_cte = recursive_cte_generator(
    cte_name='org_hierarchy',
    base_query='SELECT employee_id, manager_id, 1 as depth FROM employees WHERE manager_id IS NULL',
    recursive_query='e.manager_id = org_hierarchy.employee_id',
    anchor_columns=['employee_id', 'manager_id', 'depth'],
    recursive_columns=['e.employee_id', 'e.manager_id', 'org_hierarchy.depth + 1']
) %}

-- 使用动态透视表宏
{%- set customer_pivot_table = dynamic_pivot_table(
    source_table='customer_activities',
    pivot_column='activity_type',
    value_column='activity_count',
    aggregate_function='SUM',
    where_conditions=['activity_date >= DATEADD(month, -3, CURRENT_DATE)']
) %}

-- 主查询：综合客户分析
WITH 
-- 客户基础数据增强
enhanced_customers AS (
    SELECT 
        c.*,
        -- 使用条件物料化宏
        {{ conditional_materialization(
            model_name='customers',
            materialization_type='table',
            conditions=[target.name == 'prod', 'c.status = \'active\'']
        ) }}
        
        -- 客户价值评分（使用复杂业务逻辑）
        CASE 
            WHEN lifetime_value > 5000 THEN 'VIP'
            WHEN lifetime_value > 1000 THEN 'Premium' 
            WHEN lifetime_value > 500 THEN 'Standard'
            ELSE 'Basic'
        END AS value_tier,
        
        -- RFM评分计算
        (
            CASE WHEN recency_score = 5 THEN 3
                 WHEN recency_score >= 3 THEN 2
                 ELSE 1
            END +
            CASE WHEN frequency_score = 5 THEN 3
                 WHEN frequency_score >= 3 THEN 2
                 ELSE 1
            END +
            CASE WHEN monetary_score = 5 THEN 3
                 WHEN monetary_score >= 3 THEN 2
                 ELSE 1
            END
        ) AS rfm_composite_score,
        
        -- 客户生命周期阶段
        CASE 
            WHEN customer_age_days < 30 THEN 'New'
            WHEN customer_age_days < 180 THEN 'Growing'
            WHEN customer_age_days < 365 THEN 'Established'
            ELSE 'Mature'
        END AS lifecycle_stage,
        
        -- 行为模式分析
        CASE 
            WHEN avg_order_value > 200 AND order_frequency > 4 THEN 'High Value Frequent'
            WHEN avg_order_value > 200 THEN 'High Value Occasional'
            WHEN order_frequency > 4 THEN 'Low Value Frequent'
            ELSE 'Low Value Occasional'
        END AS behavior_pattern
        
    FROM {{ ref('stg_customers') }} c
    WHERE status = 'active'
),

-- 客户互动分析
customer_interactions AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT interaction_id) AS total_interactions,
        COUNT(DISTINCT CASE WHEN interaction_type = 'purchase' THEN interaction_id END) AS purchase_count,
        COUNT(DISTINCT CASE WHEN interaction_type = 'support' THEN interaction_id END) AS support_count,
        COUNT(DISTINCT CASE WHEN interaction_type = 'feedback' THEN interaction_id END) AS feedback_count,
        
        -- 互动频率分析
        AVG(DATEDIFF(day, LAG(interaction_date) OVER (PARTITION BY customer_id ORDER BY interaction_date), interaction_date)) AS avg_interaction_interval,
        
        -- 最近互动分析
        MAX(interaction_date) AS last_interaction_date,
        DATEDIFF(day, MAX(interaction_date), CURRENT_DATE) AS days_since_last_interaction
        
    FROM {{ ref('stg_customer_interactions') }}
    GROUP BY customer_id
),

-- 客户价值预测
customer_value_prediction AS (
    SELECT 
        customer_id,
        -- 使用机器学习宏进行价值预测
        {{ ml_predict_customer_value('customer_features') }} AS predicted_lifetime_value,
        
        -- 流失风险评分
        {{ ml_calculate_churn_risk('customer_behavior') }} AS churn_risk_score,
        
        -- 交叉销售潜力
        {{ ml_cross_sell_potential('purchase_history') }} AS cross_sell_potential,
        
        -- 推荐产品匹配度
        {{ ml_product_recommendation('preference_profile') }} AS recommended_products
        
    FROM {{ ref('stg_customer_features') }}
),

-- 客户社交网络分析
customer_network_analysis AS (
    SELECT 
        customer_id,
        -- 网络中心度指标
        {{ network_centrality_metrics('customer_network') }} AS network_metrics,
        
        -- 影响力评分
        {{ influence_score_calculation('social_interactions') }} AS influence_score,
        
        -- 社区检测
        {{ community_detection('network_graph') }} AS community_id
        
    FROM {{ ref('stg_customer_network') }}
),

-- 客户情感分析
customer_sentiment_analysis AS (
    SELECT 
        customer_id,
        -- 情感评分（基于评论和反馈）
        {{ sentiment_analysis('customer_feedback') }} AS sentiment_score,
        
        -- 满意度指标
        {{ satisfaction_metrics('survey_responses') }} AS satisfaction_metrics,
        
        -- 情感趋势分析
        {{ sentiment_trend_analysis('historical_feedback') }} AS sentiment_trend
        
    FROM {{ ref('stg_customer_feedback') }}
),

-- 综合客户画像
final_customer_profiles AS (
    SELECT 
        ec.customer_id,
        ec.customer_name,
        ec.email,
        ec.value_tier,
        ec.rfm_composite_score,
        ec.lifecycle_stage,
        ec.behavior_pattern,
        
        -- 互动指标
        ci.total_interactions,
        ci.purchase_count,
        ci.support_count,
        ci.feedback_count,
        ci.avg_interaction_interval,
        ci.days_since_last_interaction,
        
        -- 预测指标
        cvp.predicted_lifetime_value,
        cvp.churn_risk_score,
        cvp.cross_sell_potential,
        cvp.recommended_products,
        
        -- 网络指标
        cna.network_metrics,
        cna.influence_score,
        cna.community_id,
        
        -- 情感指标
        csa.sentiment_score,
        csa.satisfaction_metrics,
        csa.sentiment_trend,
        
        -- 综合健康度评分
        (
            (ec.rfm_composite_score * 0.3) +
            (CASE WHEN ci.days_since_last_interaction < 30 THEN 1.0 
                  WHEN ci.days_since_last_interaction < 90 THEN 0.5 
                  ELSE 0.1 END * 0.2) +
            (csa.sentiment_score * 0.2) +
            ((1 - cvp.churn_risk_score) * 0.3)
        ) AS customer_health_score,
        
        -- 行动建议
        CASE 
            WHEN cvp.churn_risk_score > 0.7 THEN 'High Risk - Proactive Retention'
            WHEN ec.rfm_composite_score >= 8 AND ci.days_since_last_interaction > 60 THEN 'At Risk - Re-engagement'
            WHEN ec.rfm_composite_score >= 8 AND csa.sentiment_score > 0.7 THEN 'High Value - Loyalty Program'
            WHEN cvp.cross_sell_potential > 0.8 THEN 'High Potential - Cross-sell'
            ELSE 'Monitor - Standard Engagement'
        END AS recommended_action,
        
        -- 优先级分类
        CASE 
            WHEN customer_health_score >= 0.8 THEN 'Tier 1 - Critical'
            WHEN customer_health_score >= 0.6 THEN 'Tier 2 - High'
            WHEN customer_health_score >= 0.4 THEN 'Tier 3 - Medium'
            ELSE 'Tier 4 - Low'
        END AS priority_tier,
        
        -- 技术字段
        CURRENT_TIMESTAMP AS _dbt_processed_at,
        '{{ invocation_id }}' AS _dbt_batch_id
        
    FROM enhanced_customers ec
    LEFT JOIN customer_interactions ci ON ec.customer_id = ci.customer_id
    LEFT JOIN customer_value_prediction cvp ON ec.customer_id = cvp.customer_id
    LEFT JOIN customer_network_analysis cna ON ec.customer_id = cna.customer_id
    LEFT JOIN customer_sentiment_analysis csa ON ec.customer_id = csa.customer_id
    
    -- 使用动态WHERE条件
    {%- if is_incremental() %}
    WHERE ec._dbt_loaded_at > (
        SELECT MAX(_dbt_loaded_at) 
        FROM {{ this }}
    )
    {%- endif %}
)

-- 最终选择
SELECT 
    *,
    
    -- 数据质量检查标记
    CASE 
        WHEN customer_health_score BETWEEN 0 AND 1 THEN 'VALID'
        ELSE 'INVALID'
    END AS data_quality_flag,
    
    -- 版本标记
    'v1.0' AS model_version
    
FROM final_customer_profiles

-- 使用钩子函数进行后处理
{{ config(
    post_hook=[
        "{{ update_customer_analytics_summary() }}",
        "{{ log_customer_segmentation_metrics() }}",
        "{{ notify_business_team('Customer analytics updated') }}"
    ]
) }}

-- 模型级文档
{##
  高级客户分析模型说明：
  
  此模型演示了dbt高级特性的综合应用：
  
  1. 复杂宏使用：
     - 动态SQL生成器
     - 递归CTE处理
     - 机器学习预测宏
     - 网络分析宏
     
  2. 自定义物料化策略：
     - 条件物料化
     - 增量处理优化
     - 性能优化配置
     
  3. 钩子函数集成：
     - 数据质量验证
     - 业务指标更新
     - 通知系统集成
     
  4. 高级分析功能：
     - 客户价值预测
     - 流失风险分析
     - 社交网络分析
     - 情感分析
     
  业务价值：
  - 360度客户视图
  - 精准的客户分群
  - 预测性分析能力
  - 自动化行动建议
  
  技术特性：
  - 模块化设计
  - 可扩展架构
  - 性能优化
  - 质量保证
  
  使用建议：
  - 定期运行以保持数据新鲜度
  - 监控模型性能指标
  - 根据业务需求调整算法参数
  - 集成到业务工作流中
##}