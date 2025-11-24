# SQL高级专题：窗口函数与PostgreSQL高级特性

## 目录

1. [窗口函数基础](#窗口函数基础)
2. [聚合窗口函数](#聚合窗口函数)
3. [排序窗口函数](#排序窗口函数)
4. [偏移窗口函数](#偏移窗口函数)
5. [高级窗口应用](#高级窗口应用)
6. [PostgreSQL特有高级功能](#postgresql特有高级功能)
7. [高级查询优化技巧](#高级查询优化技巧)
8. [复杂查询案例](#复杂查询案例)
9. [性能调优与最佳实践](#性能调优与最佳实践)
10. [实战练习](#实战练习)

---

## 窗口函数基础

### 窗口函数概述

窗口函数(Window Functions)是一种特殊类型的SQL函数，它能够对与当前行有某种关联的一组表行进行计算。窗口函数与聚合函数不同，它不会将多行结果合并为一行，而是为每一行返回一个基于窗口计算的结果。

### 基本语法

```sql
窗口函数(参数) OVER (
    [PARTITION BY 分区列]
    [ORDER BY 排序列]
    [FRAME子句]
)
```

- **PARTITION BY**: 将结果集分成多个分区，窗口函数在每个分区内独立计算
- **ORDER BY**: 定义每个分区内的行顺序
- **FRAME子句**: 指定当前行的计算范围

### 示例准备数据

```sql
-- 创建示例表
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    sales_date DATE NOT NULL,
    region VARCHAR(50) NOT NULL,
    product VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL
);

-- 插入示例数据
INSERT INTO sales (sales_date, region, product, amount, quantity) VALUES
('2023-01-01', '华北', '产品A', 1200.00, 10),
('2023-01-02', '华北', '产品B', 800.00, 8),
('2023-01-03', '华北', '产品A', 1500.00, 12),
('2023-01-04', '华东', '产品B', 900.00, 9),
('2023-01-05', '华东', '产品A', 1100.00, 11),
('2023-01-06', '华北', '产品C', 700.00, 7),
('2023-01-07', '华东', '产品B', 1000.00, 10),
('2023-01-08', '华南', '产品A', 1300.00, 13),
('2023-01-09', '华南', '产品C', 600.00, 6),
('2023-01-10', '华北', '产品A', 1400.00, 14);
```

### 窗口框架(FRAME)子句

窗口框架定义了相对于当前行的计算范围：

```sql
-- ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW: 从分区开始到当前行
-- ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING: 前一行到后一行
-- ROWS BETWEEN 3 PRECEDING AND CURRENT ROW: 前三行到当前行
-- RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING: 整个分区
```

---

## 聚合窗口函数

### SUM() 窗口函数

计算累计总和：

```sql
-- 按日期顺序计算累计销售额
SELECT 
    sales_date,
    region,
    amount,
    SUM(amount) OVER (ORDER BY sales_date) AS cumulative_amount
FROM sales
ORDER BY sales_date;

-- 按区域分组计算每个区域内的累计销售额
SELECT 
    sales_date,
    region,
    amount,
    SUM(amount) OVER (PARTITION BY region ORDER BY sales_date) AS regional_cumulative_amount
FROM sales
ORDER BY region, sales_date;
```

### AVG() 窗口函数

计算移动平均：

```sql
-- 计算3日移动平均销售额
SELECT 
    sales_date,
    region,
    amount,
    AVG(amount) OVER (
        ORDER BY sales_date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3days
FROM sales
ORDER BY sales_date;

-- 按区域分组计算每个区域的移动平均
SELECT 
    sales_date,
    region,
    amount,
    AVG(amount) OVER (
        PARTITION BY region 
        ORDER BY sales_date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS regional_moving_avg
FROM sales
ORDER BY region, sales_date;
```

### COUNT() 窗口函数

计算累计计数：

```sql
-- 按日期顺序累计计数
SELECT 
    sales_date,
    region,
    COUNT(*) OVER (ORDER BY sales_date) AS cumulative_count
FROM sales
ORDER BY sales_date;

-- 按区域分组累计计数
SELECT 
    sales_date,
    region,
    COUNT(*) OVER (PARTITION BY region ORDER BY sales_date) AS regional_count
FROM sales
ORDER BY region, sales_date;
```

### MIN/MAX 窗口函数

计算窗口内的最小/最大值：

```sql
-- 计算每个区域内的最高销售额
SELECT 
    sales_date,
    region,
    amount,
    MAX(amount) OVER (PARTITION BY region) AS max_amount_in_region,
    MIN(amount) OVER (PARTITION BY region) AS min_amount_in_region
FROM sales;
```

---

## 排序窗口函数

### ROW_NUMBER()

为每个分区的行生成唯一的序列号：

```sql
-- 为每个区域的销售记录按日期排序
SELECT 
    sales_date,
    region,
    product,
    amount,
    ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) AS sales_rank_in_region
FROM sales;
```

### RANK()

为行生成排名，相同值会有相同排名，后续排名会跳过：

```sql
-- 按销售额排名
SELECT 
    sales_date,
    region,
    product,
    amount,
    RANK() OVER (ORDER BY amount DESC) AS sales_rank,
    RANK() OVER (PARTITION BY region ORDER BY amount DESC) AS sales_rank_in_region
FROM sales;
```

### DENSE_RANK()

与RANK()类似，但不会跳过后续排名：

```sql
-- 密集排名
SELECT 
    sales_date,
    region,
    product,
    amount,
    DENSE_RANK() OVER (ORDER BY amount DESC) AS dense_sales_rank
FROM sales;
```

### NTILE()

将分区内的行分为指定数量的组：

```sql
-- 将销售额分为4个等级（四分位数）
SELECT 
    sales_date,
    region,
    product,
    amount,
    NTILE(4) OVER (ORDER BY amount DESC) AS sales_quartile,
    NTILE(3) OVER (ORDER BY amount DESC) AS sales_tertile
FROM sales;
```

### PERCENT_RANK()

计算百分位排名：

```sql
-- 计算销售额的百分位排名
SELECT 
    sales_date,
    region,
    product,
    amount,
    PERCENT_RANK() OVER (ORDER BY amount DESC) AS sales_percent_rank,
    PERCENT_RANK() OVER (PARTITION BY region ORDER BY amount DESC) AS regional_percent_rank
FROM sales;
```

### CUME_DIST()

计算累积分布：

```sql
-- 计算销售额的累积分布
SELECT 
    sales_date,
    region,
    product,
    amount,
    CUME_DIST() OVER (ORDER BY amount DESC) AS sales_cume_dist,
    CUME_DIST() OVER (PARTITION BY region ORDER BY amount DESC) AS regional_cume_dist
FROM sales;
```

---

## 偏移窗口函数

### LAG() 和 LEAD()

访问前一行或后一行的数据：

```sql
-- 计算每日销售额与前一日的差值
SELECT 
    sales_date,
    region,
    amount,
    LAG(amount, 1, 0) OVER (ORDER BY sales_date) AS previous_amount,
    amount - LAG(amount, 1, 0) OVER (ORDER BY sales_date) AS amount_change
FROM sales;

-- 计算每个区域内每日销售额与前一日的差值
SELECT 
    sales_date,
    region,
    amount,
    LAG(amount, 1, 0) OVER (PARTITION BY region ORDER BY sales_date) AS previous_amount,
    amount - LAG(amount, 1, 0) OVER (PARTITION BY region ORDER BY sales_date) AS amount_change
FROM sales
ORDER BY region, sales_date;

-- 计算后一日的销售额
SELECT 
    sales_date,
    region,
    amount,
    LEAD(amount, 1, 0) OVER (ORDER BY sales_date) AS next_amount
FROM sales;
```

### FIRST_VALUE() 和 LAST_VALUE()

获取窗口内的第一行或最后一行值：

```sql
-- 获取每个区域的第一笔和最后一笔销售额
SELECT 
    sales_date,
    region,
    amount,
    FIRST_VALUE(amount) OVER (PARTITION BY region ORDER BY sales_date) AS first_amount_in_region,
    LAST_VALUE(amount) OVER (
        PARTITION BY region 
        ORDER BY sales_date 
        RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_amount_in_region
FROM sales;
```

### NTH_VALUE()

获取窗口内的第N行值：

```sql
-- 获取每个区域的第二笔销售额
SELECT 
    sales_date,
    region,
    amount,
    NTH_VALUE(amount, 2) OVER (
        PARTITION BY region 
        ORDER BY sales_date 
        RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS second_amount_in_region
FROM sales;
```

---

## 高级窗口应用

### 计算同比/环比增长率

```sql
-- 创建月度销售数据视图
CREATE VIEW monthly_sales AS
SELECT 
    DATE_TRUNC('month', sales_date) AS month,
    region,
    SUM(amount) AS monthly_amount
FROM sales
GROUP BY DATE_TRUNC('month', sales_date), region;

-- 计算环比增长率
SELECT 
    month,
    region,
    monthly_amount,
    LAG(monthly_amount, 1) OVER (PARTITION BY region ORDER BY month) AS previous_month_amount,
    ROUND(
        (monthly_amount - LAG(monthly_amount, 1) OVER (PARTITION BY region ORDER BY month)) * 100.0 / 
        LAG(monthly_amount, 1) OVER (PARTITION BY region ORDER BY month), 2
    ) AS month_over_month_growth
FROM monthly_sales
ORDER BY region, month;

-- 计算同比增长率
SELECT 
    month,
    region,
    monthly_amount,
    LAG(monthly_amount, 12) OVER (PARTITION BY region ORDER BY month) AS same_month_last_year,
    ROUND(
        (monthly_amount - LAG(monthly_amount, 12) OVER (PARTITION BY region ORDER BY month)) * 100.0 / 
        LAG(monthly_amount, 12) OVER (PARTITION BY region ORDER BY month), 2
    ) AS year_over_year_growth
FROM monthly_sales
ORDER BY region, month;
```

### 计算移动累计占比

```sql
-- 计算每个区域销售额占总销售额的累计百分比
SELECT 
    sales_date,
    region,
    amount,
    SUM(amount) OVER (PARTITION BY region ORDER BY sales_date) AS regional_cumulative_amount,
    SUM(amount) OVER (PARTITION BY region) AS total_region_amount,
    ROUND(
        SUM(amount) OVER (PARTITION BY region ORDER BY sales_date) * 100.0 / 
        SUM(amount) OVER (PARTITION BY region), 2
    ) AS regional_cumulative_percentage
FROM sales
ORDER BY region, sales_date;
```

### 计算排名变化趋势

```sql
-- 创建月度排名视图
CREATE VIEW monthly_ranking AS
SELECT 
    DATE_TRUNC('month', sales_date) AS month,
    region,
    SUM(amount) AS monthly_amount,
    RANK() OVER (PARTITION BY DATE_TRUNC('month', sales_date) ORDER BY SUM(amount) DESC) AS region_rank
FROM sales
GROUP BY DATE_TRUNC('month', sales_date), region;

-- 计算区域排名变化
SELECT 
    month,
    region,
    monthly_amount,
    region_rank,
    LAG(region_rank, 1) OVER (PARTITION BY region ORDER BY month) AS previous_month_rank,
    LAG(region_rank, 1) OVER (PARTITION BY region ORDER BY month) - region_rank AS rank_change
FROM monthly_ranking
ORDER BY region, month;
```

### 计算分组内占比

```sql
-- 计算每个产品占该区域销售额的比例
SELECT 
    sales_date,
    region,
    product,
    amount,
    SUM(amount) OVER (PARTITION BY region, product) AS product_region_total,
    SUM(amount) OVER (PARTITION BY region) AS region_total,
    ROUND(
        SUM(amount) OVER (PARTITION BY region, product) * 100.0 / 
        SUM(amount) OVER (PARTITION BY region), 2
    ) AS product_region_percentage
FROM sales
ORDER BY region, product, sales_date;
```

### 找出分组内的Top-N记录

```sql
-- 方法1: 使用窗口函数和子查询
SELECT sales_date, region, product, amount
FROM (
    SELECT 
        sales_date,
        region,
        product,
        amount,
        ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) AS rn
    FROM sales
) ranked_sales
WHERE rn <= 3
ORDER BY region, amount DESC;

-- 方法2: 使用WITH语句
WITH ranked_sales AS (
    SELECT 
        sales_date,
        region,
        product,
        amount,
        ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) AS rn
    FROM sales
)
SELECT sales_date, region, product, amount
FROM ranked_sales
WHERE rn <= 3
ORDER BY region, amount DESC;
```

### 计算分组内最大间隔

```sql
-- 计算每个区域连续销售记录之间的最大时间间隔
WITH date_intervals AS (
    SELECT 
        region,
        sales_date,
        sales_date - LAG(sales_date, 1) OVER (PARTITION BY region ORDER BY sales_date) AS interval_days
    FROM sales
)
SELECT 
    region,
    MAX(interval_days) AS max_interval_days,
    AVG(interval_days) AS avg_interval_days
FROM date_intervals
WHERE interval_days IS NOT NULL
GROUP BY region;
```

---

## PostgreSQL特有高级功能

### 窗口函数与FILTER子句结合

```sql
-- 计算每个区域内产品A和非产品A的销售额对比
SELECT 
    region,
    sales_date,
    amount,
    SUM(amount) FILTER (WHERE product = '产品A') OVER (PARTITION BY region ORDER BY sales_date) AS product_a_cumulative,
    SUM(amount) FILTER (WHERE product <> '产品A') OVER (PARTITION BY region ORDER BY sales_date) AS other_products_cumulative
FROM sales
ORDER BY region, sales_date;
```

### 生成序列与GROUPING SETS

```sql
-- 创建时间序列数据
SELECT 
    generate_series(
        '2023-01-01'::date, 
        '2023-01-31'::date, 
        '1 day'::interval
    ) AS date_series
LEFT JOIN (
    SELECT sales_date, SUM(amount) AS daily_amount
    FROM sales
    GROUP BY sales_date
) daily_sales ON date_series = daily_sales.sales_date;

-- 使用GROUPING SETS进行多维度分析
SELECT 
    region,
    product,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    GROUPING(region) AS is_region_grouped,
    GROUPING(product) AS is_product_grouped
FROM sales
GROUP BY GROUPING SETS ((region, product), (region), (product), ());
```

### PostgreSQL JSON函数与窗口函数结合

```sql
-- 创建包含JSON数据的示例表
CREATE TABLE sales_with_attributes (
    id SERIAL PRIMARY KEY,
    sales_date DATE NOT NULL,
    region VARCHAR(50) NOT NULL,
    product VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    attributes JSONB
);

-- 插入示例数据
INSERT INTO sales_with_attributes (sales_date, region, product, amount, attributes) VALUES
('2023-01-01', '华北', '产品A', 1200.00, '{"color": "red", "size": "large", "discount": true}'),
('2023-01-02', '华北', '产品B', 800.00, '{"color": "blue", "size": "medium", "discount": false}'),
('2023-01-03', '华北', '产品A', 1500.00, '{"color": "green", "size": "small", "discount": true}');

-- 结合JSON函数和窗口函数
SELECT 
    sales_date,
    region,
    product,
    amount,
    attributes->>'color' AS color,
    SUM(amount) OVER (PARTITION BY region, attributes->>'color') AS color_region_amount,
    RANK() OVER (PARTITION BY attributes->>'color' ORDER BY amount DESC) AS color_rank
FROM sales_with_attributes;
```

### PostgreSQL数组函数与窗口函数结合

```sql
-- 创建包含数组数据的示例表
CREATE TABLE sales_with_tags (
    id SERIAL PRIMARY KEY,
    sales_date DATE NOT NULL,
    region VARCHAR(50) NOT NULL,
    product VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    tags TEXT[]
);

-- 插入示例数据
INSERT INTO sales_with_tags (sales_date, region, product, amount, tags) VALUES
('2023-01-01', '华北', '产品A', 1200.00, ARRAY['electronics', 'popular', 'new']),
('2023-01-02', '华北', '产品B', 800.00, ARRAY['electronics', 'discount']),
('2023-01-03', '华北', '产品A', 1500.00, ARRAY['electronics', 'bestseller']);

-- 结合数组函数和窗口函数
SELECT 
    sales_date,
    region,
    product,
    amount,
    tags,
    array_length(tags, 1) AS tag_count,
    SUM(amount) OVER (PARTITION BY array_length(tags, 1)) AS same_tag_count_amount,
    RANK() OVER (PARTITION BY tags[1] ORDER BY amount DESC) AS first_tag_rank
FROM sales_with_tags;
```

### 高级日期时间函数与窗口函数

```sql
-- 使用日期时间函数与窗口函数
SELECT 
    sales_date,
    EXTRACT('month' FROM sales_date) AS sales_month,
    EXTRACT('day' FROM sales_date) AS sales_day,
    EXTRACT('quarter' FROM sales_date) AS sales_quarter,
    EXTRACT('dow' FROM sales_date) AS day_of_week, -- 0=Sunday, 6=Saturday
    amount,
    SUM(amount) OVER (PARTITION BY EXTRACT('month' FROM sales_date)) AS month_total,
    SUM(amount) OVER (PARTITION BY EXTRACT('dow' FROM sales_date)) AS same_weekday_total,
    RANK() OVER (PARTITION BY EXTRACT('month' FROM sales_date) ORDER BY amount DESC) AS month_rank
FROM sales;
```

---

## 高级查询优化技巧

### 窗口函数性能优化

```sql
-- 创建适当的索引
CREATE INDEX idx_sales_region_date ON sales(region, sales_date);
CREATE INDEX idx_sales_amount ON sales(amount DESC);

-- 使用EXPLAIN ANALYZE分析查询计划
EXPLAIN ANALYZE
SELECT 
    sales_date,
    region,
    amount,
    SUM(amount) OVER (PARTITION BY region ORDER BY sales_date) AS cumulative_amount
FROM sales;

-- 优化大型数据集的窗口查询
-- 1. 减少分区数量
-- 2. 限制排序字段数量
-- 3. 使用更精确的PARTITION BY子句
```

### 公共表表达式(CTE)优化复杂查询

```sql
-- 使用CTE分解复杂查询
WITH regional_sales AS (
    SELECT 
        region,
        DATE_TRUNC('month', sales_date) AS month,
        SUM(amount) AS monthly_amount
    FROM sales
    GROUP BY region, DATE_TRUNC('month', sales_date)
),
regional_ranks AS (
    SELECT 
        region,
        month,
        monthly_amount,
        RANK() OVER (PARTITION BY region ORDER BY monthly_amount DESC) AS month_rank
    FROM regional_sales
),
regional_top_months AS (
    SELECT 
        region,
        month,
        monthly_amount
    FROM regional_ranks
    WHERE month_rank <= 3
)
SELECT 
    rs.region,
    rs.month,
    rs.monthly_amount,
    rtm.monthly_amount AS top_month_amount,
    ROUND(rs.monthly_amount * 100.0 / rtm.monthly_amount, 2) AS percentage_of_top
FROM regional_sales rs
JOIN regional_top_months rtm ON rs.region = rtm.region
ORDER BY rs.region, rs.month;
```

### 物化视图优化重复计算

```sql
-- 创建物化视图存储复杂窗口计算结果
CREATE MATERIALIZED VIEW mv_sales_analytics AS
SELECT 
    sales_date,
    region,
    product,
    amount,
    ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) AS regional_rank,
    SUM(amount) OVER (PARTITION BY region ORDER BY sales_date) AS regional_cumulative,
    SUM(amount) OVER (PARTITION BY product ORDER BY sales_date) AS product_cumulative,
    AVG(amount) OVER (ORDER BY sales_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_3days
FROM sales;

-- 创建唯一索引
CREATE UNIQUE INDEX idx_mv_sales_analytics_pk ON mv_sales_analytics(sales_date, region, product);

-- 定期刷新物化视图
REFRESH MATERIALIZED VIEW mv_sales_analytics;
```

---

## 复杂查询案例

### 销售漏斗分析

```sql
-- 创建销售漏斗示例表
CREATE TABLE sales_funnel (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    event_date TIMESTAMP NOT NULL,
    event_stage VARCHAR(50) NOT NULL, -- 'visit', 'add_to_cart', 'checkout', 'purchase'
    event_value DECIMAL(10, 2)
);

-- 插入示例数据
INSERT INTO sales_funnel (user_id, event_date, event_stage, event_value) VALUES
(1, '2023-01-01 09:00:00', 'visit', NULL),
(1, '2023-01-01 09:15:00', 'add_to_cart', 50.00),
(1, '2023-01-01 09:30:00', 'checkout', 50.00),
(1, '2023-01-01 09:45:00', 'purchase', 50.00),
(2, '2023-01-01 10:00:00', 'visit', NULL),
(2, '2023-01-01 10:20:00', 'add_to_cart', 75.00),
(2, '2023-01-01 10:40:00', 'checkout', 75.00),
(3, '2023-01-01 11:00:00', 'visit', NULL),
(3, '2023-01-01 11:10:00', 'add_to_cart', 30.00),
(4, '2023-01-01 12:00:00', 'visit', NULL);

-- 计算漏斗转化率
WITH user_stages AS (
    SELECT 
        user_id,
        MAX(CASE WHEN event_stage = 'visit' THEN 1 ELSE 0 END) AS visited,
        MAX(CASE WHEN event_stage = 'add_to_cart' THEN 1 ELSE 0 END) AS added_to_cart,
        MAX(CASE WHEN event_stage = 'checkout' THEN 1 ELSE 0 END) AS checked_out,
        MAX(CASE WHEN event_stage = 'purchase' THEN 1 ELSE 0 END) AS purchased
    FROM sales_funnel
    GROUP BY user_id
),
stage_counts AS (
    SELECT 
        SUM(visited) AS visit_count,
        SUM(added_to_cart) AS add_to_cart_count,
        SUM(checked_out) AS checkout_count,
        SUM(purchased) AS purchase_count
    FROM user_stages
),
conversion_rates AS (
    SELECT 
        'Visit' AS stage,
        visit_count AS count,
        1.0 AS conversion_rate
    FROM stage_counts
    
    UNION ALL
    
    SELECT 
        'Add to Cart' AS stage,
        add_to_cart_count AS count,
        ROUND(add_to_cart_count * 1.0 / NULLIF(visit_count, 0), 2) AS conversion_rate
    FROM stage_counts
    
    UNION ALL
    
    SELECT 
        'Checkout' AS stage,
        checkout_count AS count,
        ROUND(checkout_count * 1.0 / NULLIF(add_to_cart_count, 0), 2) AS conversion_rate
    FROM stage_counts
    
    UNION ALL
    
    SELECT 
        'Purchase' AS stage,
        purchase_count AS count,
        ROUND(purchase_count * 1.0 / NULLIF(checkout_count, 0), 2) AS conversion_rate
    FROM stage_counts
)
SELECT 
    stage,
    count,
    conversion_rate,
    LAG(count, 1) OVER (ORDER BY count DESC) AS previous_stage_count,
    LAG(conversion_rate, 1) OVER (ORDER BY count DESC) AS previous_stage_conversion_rate
FROM conversion_rates
ORDER BY count DESC;
```

### 同期群分析

```sql
-- 创建用户注册表
CREATE TABLE user_registrations (
    user_id SERIAL PRIMARY KEY,
    registration_date DATE NOT NULL,
    acquisition_channel VARCHAR(50)
);

-- 创建用户活动表
CREATE TABLE user_activities (
    activity_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    activity_date DATE NOT NULL,
    activity_type VARCHAR(50)
);

-- 计算同期群留存率
WITH user_cohorts AS (
    SELECT 
        user_id,
        DATE_TRUNC('month', registration_date) AS cohort_month,
        acquisition_channel
    FROM user_registrations
),
user_activities_with_cohorts AS (
    SELECT 
        ua.user_id,
        ua.activity_date,
        uc.cohort_month,
        uc.acquisition_channel,
        EXTRACT('year' FROM ua.activity_date) * 12 + EXTRACT('month' FROM ua.activity_date) -
        EXTRACT('year' FROM uc.cohort_month) * 12 - EXTRACT('month' FROM uc.cohort_month) AS period_number
    FROM user_activities ua
    JOIN user_cohorts uc ON ua.user_id = uc.user_id
),
cohort_activity_counts AS (
    SELECT 
        cohort_month,
        acquisition_channel,
        period_number,
        COUNT(DISTINCT user_id) AS active_users
    FROM user_activities_with_cohorts
    GROUP BY cohort_month, acquisition_channel, period_number
),
cohort_sizes AS (
    SELECT 
        cohort_month,
        acquisition_channel,
        COUNT(DISTINCT user_id) AS cohort_size
    FROM user_cohorts
    GROUP BY cohort_month, acquisition_channel
),
retention_rates AS (
    SELECT 
        cac.cohort_month,
        cac.acquisition_channel,
        cac.period_number,
        cac.active_users,
        cs.cohort_size,
        ROUND(cac.active_users * 100.0 / cs.cohort_size, 2) AS retention_rate
    FROM cohort_activity_counts cac
    JOIN cohort_sizes cs ON cac.cohort_month = cs.cohort_month AND cac.acquisition_channel = cs.acquisition_channel
)
SELECT 
    TO_CHAR(cohort_month, 'YYYY-MM') AS cohort_month,
    acquisition_channel,
    period_number,
    cohort_size,
    active_users,
    retention_rate,
    LAG(retention_rate, 1) OVER (PARTITION BY cohort_month, acquisition_channel ORDER BY period_number) AS previous_period_retention
FROM retention_rates
ORDER BY cohort_month, acquisition_channel, period_number;
```

### 时间序列模式识别

```sql
-- 创建包含时间序列数据的表
CREATE TABLE time_series_data (
    id SERIAL PRIMARY KEY,
    series_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    value DECIMAL(10, 2) NOT NULL
);

-- 使用窗口函数识别趋势和季节性
WITH moving_averages AS (
    SELECT 
        series_id,
        timestamp,
        value,
        AVG(value) OVER (PARTITION BY series_id ORDER BY timestamp 
                        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7,
        AVG(value) OVER (PARTITION BY series_id ORDER BY timestamp 
                        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS ma_30
    FROM time_series_data
),
trend_analysis AS (
    SELECT 
        series_id,
        timestamp,
        value,
        ma_7,
        ma_30,
        CASE 
            WHEN value > ma_7 AND ma_7 > ma_30 THEN 'upward_trend'
            WHEN value < ma_7 AND ma_7 < ma_30 THEN 'downward_trend'
            ELSE 'stable'
        END AS trend_direction,
        CASE 
            WHEN value > ma_7 * 1.1 THEN 'spike'
            WHEN value < ma_7 * 0.9 THEN 'dip'
            ELSE 'normal'
        END AS anomaly_indicator
    FROM moving_averages
)
SELECT 
    series_id,
    timestamp,
    value,
    ma_7,
    ma_30,
    trend_direction,
    anomaly_indicator,
    LAG(trend_direction, 1) OVER (PARTITION BY series_id ORDER BY timestamp) AS previous_trend,
    CASE 
        WHEN trend_direction != LAG(trend_direction, 1) OVER (PARTITION BY series_id ORDER BY timestamp) 
        THEN 'trend_change'
        ELSE 'same_trend'
    END AS trend_change_indicator
FROM trend_analysis
ORDER BY series_id, timestamp;
```

---

## 性能调优与最佳实践

### 窗口函数使用注意事项

1. **分区键选择**：
   - 选择高基数列作为分区键，避免数据倾斜
   - 分区数量应适中，过多分区会增加开销

2. **排序优化**：
   - 为ORDER BY子句中的列创建索引
   - 考虑使用预排序表或物化视图

3. **内存使用**：
   - 大型窗口操作可能消耗大量内存
   - 考虑分批处理或增加work_mem配置

4. **查询计划分析**：
   - 使用EXPLAIN ANALYZE分析执行计划
   - 注意窗口函数的执行顺序和成本

### 实用优化技巧

```sql
-- 1. 使用更精确的分区
-- 避免: PARTITION BY region
-- 推荐: PARTITION BY region, product_category

-- 2. 预过滤数据
-- 避免: 先窗口函数后过滤
-- 推荐: 先过滤再窗口函数
WITH filtered_sales AS (
    SELECT * FROM sales WHERE sales_date >= '2023-01-01'
)
SELECT 
    sales_date,
    region,
    amount,
    SUM(amount) OVER (PARTITION BY region ORDER BY sales_date) AS cumulative_amount
FROM filtered_sales;

-- 3. 使用物化视图预计算复杂窗口函数
CREATE MATERIALIZED VIEW mv_sales_cumulative AS
SELECT 
    sales_date,
    region,
    amount,
    SUM(amount) OVER (PARTITION BY region ORDER BY sales_date) AS cumulative_amount
FROM sales;

-- 4. 合并多个窗口函数
-- 避免: 多个窗口函数分别计算
-- 推荐: 合并为一个窗口函数调用
SELECT 
    sales_date,
    region,
    amount,
    SUM(amount) OVER (PARTITION BY region ORDER BY sales_date) AS cumulative_amount,
    COUNT(*) OVER (PARTITION BY region ORDER BY sales_date) AS count
FROM sales;

-- 5. 适当使用窗口框架
-- 明确指定ROWS/RANGE范围，避免不必要的计算
SELECT 
    sales_date,
    region,
    amount,
    AVG(amount) OVER (PARTITION BY region ORDER BY sales_date 
                     ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_3days
FROM sales;
```

---

## 实战练习

### 练习1: 销售数据分析

创建一个查询，分析每个区域的销售情况，包括：
1. 每个区域的销售总额和平均销售额
2. 每个区域内销售额的排名
3. 每个区域的累计销售百分比
4. 每个区域与上月相比的销售额变化

### 练习2: 员工绩效分析

假设有一个员工销售表(employee_sales)，包含字段：employee_id, sale_date, amount, product_category

编写查询计算：
1. 每个员工的总销售额和排名
2. 每个员工每个产品类别的销售额占比
3. 每个员工3个月滚动平均销售额
4. 识别销售明星（前10%）和需要改进的员工（后20%）

### 练习3: 库存管理分析

假设有一个库存表(inventory)，包含字段：product_id, warehouse, date, quantity

编写查询计算：
1. 每个仓库的库存总量
2. 每个产品在所有仓库中的库存分布
3. 识别库存周转率低的产品
4. 计算每个仓库的库存安全水平（基于历史消耗量）

### 练习4: 用户行为分析

假设有一个用户行为表(user_behaviors)，包含字段：user_id, action_date, action_type, session_id

编写查询计算：
1. 每个用户的活跃度分数
2. 用户行为路径分析
3. 识别高价值用户和流失风险用户
4. 计算用户留存率和生命周期价值

### 练习5: 时间序列预测

使用窗口函数实现简单的时间序列分析：
1. 计算移动平均和趋势
2. 识别异常值和季节性模式
3. 基于历史数据进行简单预测
4. 评估预测准确性

---

## 总结

本教程详细介绍了SQL中的窗口函数及其在PostgreSQL中的高级应用，包括：

1. **窗口函数基础**：理解窗口函数的基本概念和语法
2. **聚合窗口函数**：使用SUM、AVG、COUNT等函数进行窗口计算
3. **排序窗口函数**：使用ROW_NUMBER、RANK、DENSE_RANK等进行排名
4. **偏移窗口函数**：使用LAG、LEAD、FIRST_VALUE等访问其他行数据
5. **高级窗口应用**：解决复杂业务问题如同比/环比、累计占比等
6. **PostgreSQL特有功能**：利用PostgreSQL特有的JSON、数组等高级特性
7. **查询优化技巧**：提高窗口函数查询的性能
8. **复杂查询案例**：通过实际案例展示窗口函数的强大功能

窗口函数是现代SQL中非常强大的工具，能够处理复杂的分析型查询，避免多次扫描数据和复杂的自连接。掌握窗口函数对于数据分析师和数据库开发人员来说是必不可少的高级技能。通过本教程的学习，您应该能够熟练使用窗口函数解决各种复杂的数据分析问题。