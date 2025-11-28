-- 第5章：高级查询技术 - 窗口函数示例

-- 创建示例表和数据
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER,
    sale_date DATE,
    amount DECIMAL(10,2),
    region VARCHAR(50)
);

-- 插入示例数据
INSERT INTO sales (employee_id, sale_date, amount, region) VALUES
(1, '2023-01-15', 1500.00, 'North'),
(2, '2023-01-20', 2000.00, 'South'),
(3, '2023-02-10', 1800.00, 'East'),
(1, '2023-02-15', 2200.00, 'North'),
(4, '2023-03-05', 1700.00, 'West'),
(2, '2023-03-10', 2500.00, 'South'),
(5, '2023-03-20', 1900.00, 'North'),
(3, '2023-04-01', 2100.00, 'East'),
(1, '2023-04-15', 2300.00, 'North'),
(4, '2023-04-20', 1600.00, 'West');

-- 1. 基本窗口函数 - 排名函数
-- 按销售额对所有销售记录进行排名
SELECT 
    employee_id,
    amount,
    sale_date,
    ROW_NUMBER() OVER (ORDER BY amount DESC) AS row_num,
    RANK() OVER (ORDER BY amount DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY amount DESC) AS dense_rank
FROM sales
ORDER BY amount DESC;

-- 2. 分区窗口函数
-- 按地区对销售记录进行排名
SELECT 
    employee_id,
    amount,
    region,
    RANK() OVER (PARTITION BY region ORDER BY amount DESC) AS regional_rank
FROM sales
ORDER BY region, regional_rank;

-- 3. 聚合函数作为窗口函数
-- 计算每个销售记录占总销售额和区域销售额的比例
SELECT 
    employee_id,
    amount,
    region,
    SUM(amount) OVER () AS total_sales,
    SUM(amount) OVER (PARTITION BY region) AS regional_total,
    ROUND(amount * 100.0 / SUM(amount) OVER (), 2) AS pct_of_total,
    ROUND(amount * 100.0 / SUM(amount) OVER (PARTITION BY region), 2) AS pct_of_regional
FROM sales
ORDER BY region, amount DESC;

-- 4. 前后行函数
-- 比较每个员工的销售记录与其前一笔和后一笔销售
SELECT 
    employee_id,
    amount,
    sale_date,
    LAG(amount) OVER (PARTITION BY employee_id ORDER BY sale_date) AS prev_sale,
    LEAD(amount) OVER (PARTITION BY employee_id ORDER BY sale_date) AS next_sale,
    amount - LAG(amount) OVER (PARTITION BY employee_id ORDER BY sale_date) AS diff_from_prev
FROM sales
ORDER BY employee_id, sale_date;

-- 5. 移动平均
-- 计算每个区域的7天移动平均销售额
SELECT 
    region,
    sale_date,
    amount,
    AVG(amount) OVER (
        PARTITION BY region 
        ORDER BY sale_date 
        RANGE BETWEEN INTERVAL '3 days' PRECEDING AND INTERVAL '3 days' FOLLOWING
    ) AS moving_avg_7days
FROM sales
ORDER BY region, sale_date;

-- 6. 累计计算
-- 计算每个员工的累计销售额
SELECT 
    employee_id,
    sale_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY employee_id 
        ORDER BY sale_date 
        ROWS UNBOUNDED PRECEDING
    ) AS cumulative_sales
FROM sales
ORDER BY employee_id, sale_date;

-- 7. 复杂窗口函数示例
-- 查询每个区域销售额排名前3的员工及其占比
WITH ranked_sales AS (
    SELECT 
        employee_id,
        region,
        SUM(amount) AS total_amount,
        RANK() OVER (PARTITION BY region ORDER BY SUM(amount) DESC) AS region_rank
    FROM sales
    GROUP BY employee_id, region
),
regional_totals AS (
    SELECT 
        region,
        SUM(total_amount) AS region_total
    FROM ranked_sales
    GROUP BY region
)
SELECT 
    rs.employee_id,
    rs.region,
    rs.total_amount,
    rt.region_total,
    ROUND(rs.total_amount * 100.0 / rt.region_total, 2) AS percentage_of_region,
    rs.region_rank
FROM ranked_sales rs
JOIN regional_totals rt ON rs.region = rt.region
WHERE rs.region_rank <= 3
ORDER BY rs.region, rs.region_rank;

-- 清理示例表
DROP TABLE IF EXISTS sales;