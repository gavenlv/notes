# BigQuery 实践案例 / BigQuery Practical Examples

## 中文版

### 电商数据分析案例

#### 1. 用户行为分析

```sql
-- 分析用户购买行为
WITH user_purchase_behavior AS (
  SELECT 
    user_id,
    COUNT(*) as purchase_count,
    SUM(amount) as total_spent,
    AVG(amount) as avg_order_value,
    MIN(created_at) as first_purchase,
    MAX(created_at) as last_purchase
  FROM `project.dataset.orders`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
  GROUP BY user_id
)
SELECT 
  CASE 
    WHEN total_spent >= 1000 THEN '高价值用户'
    WHEN total_spent >= 500 THEN '中价值用户'
    ELSE '低价值用户'
  END as user_segment,
  COUNT(*) as user_count,
  AVG(purchase_count) as avg_purchases,
  AVG(total_spent) as avg_total_spent
FROM user_purchase_behavior
GROUP BY user_segment
ORDER BY avg_total_spent DESC;
```

#### 2. 产品推荐系统

```sql
-- 基于协同过滤的产品推荐
WITH user_product_matrix AS (
  SELECT 
    user_id,
    product_id,
    COUNT(*) as interaction_count,
    SUM(amount) as total_spent
  FROM `project.dataset.orders`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
  GROUP BY user_id, product_id
),
product_similarity AS (
  SELECT 
    p1.product_id as product_1,
    p2.product_id as product_2,
    COUNT(DISTINCT p1.user_id) as common_users,
    SUM(p1.interaction_count * p2.interaction_count) as similarity_score
  FROM user_product_matrix p1
  JOIN user_product_matrix p2 ON p1.user_id = p2.user_id
  WHERE p1.product_id < p2.product_id
  GROUP BY p1.product_id, p2.product_id
  HAVING common_users >= 5
)
SELECT 
  product_1,
  product_2,
  similarity_score,
  common_users
FROM product_similarity
ORDER BY similarity_score DESC
LIMIT 20;
```

### 金融风控分析案例

#### 1. 异常交易检测

```sql
-- 检测异常交易模式
WITH transaction_stats AS (
  SELECT 
    user_id,
    COUNT(*) as transaction_count,
    AVG(amount) as avg_amount,
    STDDEV(amount) as amount_stddev,
    SUM(amount) as total_amount
  FROM `project.dataset.transactions`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY user_id
),
anomaly_detection AS (
  SELECT 
    t.user_id,
    t.amount,
    t.created_at,
    ts.avg_amount,
    ts.amount_stddev,
    -- Z-score 异常检测
    ABS(t.amount - ts.avg_amount) / ts.amount_stddev as z_score
  FROM `project.dataset.transactions` t
  JOIN transaction_stats ts ON t.user_id = ts.user_id
  WHERE t.created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    AND ts.amount_stddev > 0
)
SELECT 
  user_id,
  amount,
  created_at,
  z_score,
  CASE 
    WHEN z_score > 3 THEN '高风险'
    WHEN z_score > 2 THEN '中风险'
    ELSE '正常'
  END as risk_level
FROM anomaly_detection
WHERE z_score > 2
ORDER BY z_score DESC;
```

#### 2. 客户流失预测

```sql
-- 客户流失风险分析
WITH customer_activity AS (
  SELECT 
    customer_id,
    DATE(created_at) as activity_date,
    COUNT(*) as daily_transactions,
    SUM(amount) as daily_amount
  FROM `project.dataset.transactions`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
  GROUP BY customer_id, DATE(created_at)
),
customer_metrics AS (
  SELECT 
    customer_id,
    COUNT(DISTINCT activity_date) as active_days,
    AVG(daily_transactions) as avg_daily_transactions,
    AVG(daily_amount) as avg_daily_amount,
    MAX(activity_date) as last_activity,
    DATE_DIFF(CURRENT_DATE(), MAX(activity_date), DAY) as days_since_last_activity
  FROM customer_activity
  GROUP BY customer_id
)
SELECT 
  customer_id,
  active_days,
  avg_daily_transactions,
  avg_daily_amount,
  days_since_last_activity,
  CASE 
    WHEN days_since_last_activity > 30 THEN '已流失'
    WHEN days_since_last_activity > 14 THEN '流失风险高'
    WHEN days_since_last_activity > 7 THEN '流失风险中'
    ELSE '活跃客户'
  END as churn_risk
FROM customer_metrics
ORDER BY days_since_last_activity DESC;
```

### 物联网数据分析案例

#### 1. 设备性能监控

```sql
-- 设备性能趋势分析
WITH device_metrics AS (
  SELECT 
    device_id,
    TIMESTAMP_TRUNC(created_at, HOUR) as hour_bucket,
    AVG(temperature) as avg_temperature,
    AVG(humidity) as avg_humidity,
    COUNT(*) as data_points,
    MAX(created_at) as last_reading
  FROM `project.dataset.sensor_data`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  GROUP BY device_id, TIMESTAMP_TRUNC(created_at, HOUR)
),
device_health AS (
  SELECT 
    device_id,
    hour_bucket,
    avg_temperature,
    avg_humidity,
    data_points,
    CASE 
      WHEN avg_temperature > 80 OR avg_humidity > 90 THEN '异常'
      WHEN avg_temperature > 70 OR avg_humidity > 80 THEN '警告'
      ELSE '正常'
    END as health_status
  FROM device_metrics
)
SELECT 
  device_id,
  COUNT(*) as total_hours,
  COUNTIF(health_status = '异常') as abnormal_hours,
  COUNTIF(health_status = '警告') as warning_hours,
  AVG(avg_temperature) as overall_avg_temp,
  AVG(avg_humidity) as overall_avg_humidity
FROM device_health
GROUP BY device_id
ORDER BY abnormal_hours DESC;
```

#### 2. 预测性维护

```sql
-- 设备故障预测
WITH device_failure_history AS (
  SELECT 
    device_id,
    created_at,
    CASE 
      WHEN error_code IS NOT NULL THEN 1
      ELSE 0
    END as failure_flag,
    LAG(created_at) OVER (PARTITION BY device_id ORDER BY created_at) as prev_reading
  FROM `project.dataset.device_logs`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
),
failure_patterns AS (
  SELECT 
    device_id,
    COUNT(*) as total_readings,
    SUM(failure_flag) as failure_count,
    AVG(failure_flag) as failure_rate,
    AVG(DATE_DIFF(created_at, prev_reading, HOUR)) as avg_interval_hours
  FROM device_failure_history
  WHERE prev_reading IS NOT NULL
  GROUP BY device_id
)
SELECT 
  device_id,
  total_readings,
  failure_count,
  failure_rate,
  avg_interval_hours,
  CASE 
    WHEN failure_rate > 0.1 THEN '高风险'
    WHEN failure_rate > 0.05 THEN '中风险'
    ELSE '低风险'
  END as maintenance_priority
FROM failure_patterns
ORDER BY failure_rate DESC;
```

---

## English Version

### E-commerce Analytics Case Study

#### 1. User Behavior Analysis

```sql
-- Analyze user purchase behavior
WITH user_purchase_behavior AS (
  SELECT 
    user_id,
    COUNT(*) as purchase_count,
    SUM(amount) as total_spent,
    AVG(amount) as avg_order_value,
    MIN(created_at) as first_purchase,
    MAX(created_at) as last_purchase
  FROM `project.dataset.orders`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
  GROUP BY user_id
)
SELECT 
  CASE 
    WHEN total_spent >= 1000 THEN 'High Value'
    WHEN total_spent >= 500 THEN 'Medium Value'
    ELSE 'Low Value'
  END as user_segment,
  COUNT(*) as user_count,
  AVG(purchase_count) as avg_purchases,
  AVG(total_spent) as avg_total_spent
FROM user_purchase_behavior
GROUP BY user_segment
ORDER BY avg_total_spent DESC;
```

#### 2. Product Recommendation System

```sql
-- Collaborative filtering product recommendations
WITH user_product_matrix AS (
  SELECT 
    user_id,
    product_id,
    COUNT(*) as interaction_count,
    SUM(amount) as total_spent
  FROM `project.dataset.orders`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
  GROUP BY user_id, product_id
),
product_similarity AS (
  SELECT 
    p1.product_id as product_1,
    p2.product_id as product_2,
    COUNT(DISTINCT p1.user_id) as common_users,
    SUM(p1.interaction_count * p2.interaction_count) as similarity_score
  FROM user_product_matrix p1
  JOIN user_product_matrix p2 ON p1.user_id = p2.user_id
  WHERE p1.product_id < p2.product_id
  GROUP BY p1.product_id, p2.product_id
  HAVING common_users >= 5
)
SELECT 
  product_1,
  product_2,
  similarity_score,
  common_users
FROM product_similarity
ORDER BY similarity_score DESC
LIMIT 20;
```

### Financial Risk Analysis Case Study

#### 1. Anomaly Transaction Detection

```sql
-- Detect anomalous transaction patterns
WITH transaction_stats AS (
  SELECT 
    user_id,
    COUNT(*) as transaction_count,
    AVG(amount) as avg_amount,
    STDDEV(amount) as amount_stddev,
    SUM(amount) as total_amount
  FROM `project.dataset.transactions`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY user_id
),
anomaly_detection AS (
  SELECT 
    t.user_id,
    t.amount,
    t.created_at,
    ts.avg_amount,
    ts.amount_stddev,
    -- Z-score anomaly detection
    ABS(t.amount - ts.avg_amount) / ts.amount_stddev as z_score
  FROM `project.dataset.transactions` t
  JOIN transaction_stats ts ON t.user_id = ts.user_id
  WHERE t.created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    AND ts.amount_stddev > 0
)
SELECT 
  user_id,
  amount,
  created_at,
  z_score,
  CASE 
    WHEN z_score > 3 THEN 'High Risk'
    WHEN z_score > 2 THEN 'Medium Risk'
    ELSE 'Normal'
  END as risk_level
FROM anomaly_detection
WHERE z_score > 2
ORDER BY z_score DESC;
```

#### 2. Customer Churn Prediction

```sql
-- Customer churn risk analysis
WITH customer_activity AS (
  SELECT 
    customer_id,
    DATE(created_at) as activity_date,
    COUNT(*) as daily_transactions,
    SUM(amount) as daily_amount
  FROM `project.dataset.transactions`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
  GROUP BY customer_id, DATE(created_at)
),
customer_metrics AS (
  SELECT 
    customer_id,
    COUNT(DISTINCT activity_date) as active_days,
    AVG(daily_transactions) as avg_daily_transactions,
    AVG(daily_amount) as avg_daily_amount,
    MAX(activity_date) as last_activity,
    DATE_DIFF(CURRENT_DATE(), MAX(activity_date), DAY) as days_since_last_activity
  FROM customer_activity
  GROUP BY customer_id
)
SELECT 
  customer_id,
  active_days,
  avg_daily_transactions,
  avg_daily_amount,
  days_since_last_activity,
  CASE 
    WHEN days_since_last_activity > 30 THEN 'Churned'
    WHEN days_since_last_activity > 14 THEN 'High Risk'
    WHEN days_since_last_activity > 7 THEN 'Medium Risk'
    ELSE 'Active'
  END as churn_risk
FROM customer_metrics
ORDER BY days_since_last_activity DESC;
```

### IoT Data Analytics Case Study

#### 1. Device Performance Monitoring

```sql
-- Device performance trend analysis
WITH device_metrics AS (
  SELECT 
    device_id,
    TIMESTAMP_TRUNC(created_at, HOUR) as hour_bucket,
    AVG(temperature) as avg_temperature,
    AVG(humidity) as avg_humidity,
    COUNT(*) as data_points,
    MAX(created_at) as last_reading
  FROM `project.dataset.sensor_data`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  GROUP BY device_id, TIMESTAMP_TRUNC(created_at, HOUR)
),
device_health AS (
  SELECT 
    device_id,
    hour_bucket,
    avg_temperature,
    avg_humidity,
    data_points,
    CASE 
      WHEN avg_temperature > 80 OR avg_humidity > 90 THEN 'Critical'
      WHEN avg_temperature > 70 OR avg_humidity > 80 THEN 'Warning'
      ELSE 'Normal'
    END as health_status
  FROM device_metrics
)
SELECT 
  device_id,
  COUNT(*) as total_hours,
  COUNTIF(health_status = 'Critical') as critical_hours,
  COUNTIF(health_status = 'Warning') as warning_hours,
  AVG(avg_temperature) as overall_avg_temp,
  AVG(avg_humidity) as overall_avg_humidity
FROM device_health
GROUP BY device_id
ORDER BY critical_hours DESC;
```

#### 2. Predictive Maintenance

```sql
-- Device failure prediction
WITH device_failure_history AS (
  SELECT 
    device_id,
    created_at,
    CASE 
      WHEN error_code IS NOT NULL THEN 1
      ELSE 0
    END as failure_flag,
    LAG(created_at) OVER (PARTITION BY device_id ORDER BY created_at) as prev_reading
  FROM `project.dataset.device_logs`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
),
failure_patterns AS (
  SELECT 
    device_id,
    COUNT(*) as total_readings,
    SUM(failure_flag) as failure_count,
    AVG(failure_flag) as failure_rate,
    AVG(DATE_DIFF(created_at, prev_reading, HOUR)) as avg_interval_hours
  FROM device_failure_history
  WHERE prev_reading IS NOT NULL
  GROUP BY device_id
)
SELECT 
  device_id,
  total_readings,
  failure_count,
  failure_rate,
  avg_interval_hours,
  CASE 
    WHEN failure_rate > 0.1 THEN 'High Priority'
    WHEN failure_rate > 0.05 THEN 'Medium Priority'
    ELSE 'Low Priority'
  END as maintenance_priority
FROM failure_patterns
ORDER BY failure_rate DESC;
```

