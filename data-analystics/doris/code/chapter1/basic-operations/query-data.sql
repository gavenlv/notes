-- 查询数据示例
-- 连接方式: mysql -h 127.0.0.1 -P 9030 -uroot demo

USE demo;

-- 1. 基本SELECT查询
-- 查询所有用户
SELECT * FROM users_duplicate LIMIT 5;

-- 查询特定列
SELECT user_id, user_name, age, city FROM users_duplicate;

-- 使用别名
SELECT user_id AS "用户ID", user_name AS "用户名", age AS "年龄", city AS "城市" 
FROM users_duplicate;

-- 2. 条件查询
-- 使用WHERE子句
SELECT * FROM users_duplicate WHERE age > 30;

-- 多条件查询
SELECT * FROM users_duplicate WHERE age >= 25 AND city IN ('Beijing', 'Shanghai');

-- 使用LIKE进行模糊查询
SELECT * FROM users_duplicate WHERE user_name LIKE 'A%';

-- 使用BETWEEN进行范围查询
SELECT * FROM users_duplicate WHERE age BETWEEN 25 AND 30;

-- 3. 排序和限制
-- 按年龄升序排序
SELECT * FROM users_duplicate ORDER BY age ASC;

-- 按年龄降序排序
SELECT * FROM users_duplicate ORDER BY age DESC;

-- 多字段排序
SELECT * FROM users_duplicate ORDER BY city ASC, age DESC;

-- 限制返回行数
SELECT * FROM users_duplicate ORDER BY age DESC LIMIT 3;

-- 分页查询
SELECT * FROM users_duplicate ORDER BY user_id LIMIT 5 OFFSET 5;

-- 4. 聚合查询
-- 统计用户总数
SELECT COUNT(*) AS total_users FROM users_duplicate;

-- 按城市统计用户数
SELECT city, COUNT(*) AS user_count FROM users_duplicate GROUP BY city;

-- 计算平均年龄
SELECT AVG(age) AS avg_age FROM users_duplicate;

-- 按城市计算平均年龄
SELECT city, AVG(age) AS avg_age, COUNT(*) AS user_count 
FROM users_duplicate 
GROUP BY city;

-- 使用HAVING过滤分组结果
SELECT city, AVG(age) AS avg_age, COUNT(*) AS user_count 
FROM users_duplicate 
GROUP BY city 
HAVING COUNT(*) > 2;

-- 5. 连接查询
-- 创建订单表示例
CREATE TABLE IF NOT EXISTS orders (
    order_id BIGINT,
    user_id BIGINT,
    product_id INT,
    order_amount DECIMAL(10,2),
    order_date DATE
) DUPLICATE KEY(order_id)
DISTRIBUTED BY HASH(order_id) BUCKETS 8;

-- 插入订单数据
INSERT INTO orders VALUES
(1001, 1, 101, 5500.00, '2023-06-15'),
(1002, 2, 103, 150.00, '2023-06-14'),
(1003, 3, 101, 5200.00, '2023-06-15'),
(1004, 1, 105, 110.00, '2023-06-13'),
(1005, 4, 104, 1000.00, '2023-06-15'),
(1006, 5, 102, 50.00, '2023-06-14'),
(1007, 2, 107, 45.00, '2023-06-15'),
(1008, 3, 108, 500.00, '2023-06-12');

-- 内连接查询
SELECT u.user_name, u.city, o.order_id, o.order_amount, o.order_date
FROM users_duplicate u
INNER JOIN orders o ON u.user_id = o.user_id;

-- 左连接查询
SELECT u.user_name, u.city, o.order_id, o.order_amount, o.order_date
FROM users_duplicate u
LEFT JOIN orders o ON u.user_id = o.user_id;

-- 6. 子查询
-- 使用子查询查找年龄大于平均年龄的用户
SELECT user_name, age
FROM users_duplicate
WHERE age > (SELECT AVG(age) FROM users_duplicate);

-- 使用IN子查询
SELECT user_name, city
FROM users_duplicate
WHERE user_id IN (SELECT DISTINCT user_id FROM orders WHERE order_amount > 1000);

-- 7. 聚合模型表查询
-- 查询销售数据
SELECT * FROM sales_aggregate;

-- 按地区统计销售额
SELECT region, SUM(total_amount) AS total_sales_amount, SUM(total_sales) AS total_sales_count
FROM sales_aggregate
GROUP BY region;

-- 查询Aggregate模型表的聚合效果
SELECT product_name, region, total_sales, total_amount, max_price, min_price
FROM sales_aggregate
WHERE sale_date = '2023-06-15' AND product_id = 101;

-- 8. Unique模型表查询
-- 查询用户档案
SELECT * FROM user_profiles_unique;

-- 按性别统计用户数
SELECT 
  CASE gender 
    WHEN 0 THEN '未知'
    WHEN 1 THEN '男'
    WHEN 2 THEN '女'
    ELSE '其他'
  END AS gender_name,
  COUNT(*) AS user_count
FROM user_profiles_unique
GROUP BY gender;

-- 9. Primary Key模型表查询
-- 查询用户指标
SELECT * FROM user_metrics_pk;

-- 查询登录次数超过20次的用户
SELECT user_id, login_count, total_order_amount
FROM user_metrics_pk
WHERE login_count > 20;

-- 10. 分区表查询
-- 查询事件日志
SELECT * FROM event_logs LIMIT 5;

-- 按事件类型统计
SELECT event_type, COUNT(*) AS event_count
FROM event_logs
GROUP BY event_type;

-- 按日期和事件类型统计
SELECT DATE(event_time) AS event_date, event_type, COUNT(*) AS event_count
FROM event_logs
GROUP BY DATE(event_time), event_type
ORDER BY event_date, event_type;

-- 11. 高级查询示例
-- 窗口函数示例
SELECT 
  user_id,
  user_name,
  age,
  city,
  ROW_NUMBER() OVER (ORDER BY age DESC) AS age_rank,
  DENSE_RANK() OVER (PARTITION BY city ORDER BY age DESC) AS age_rank_in_city
FROM users_duplicate;

-- CTE (Common Table Expression) 示例
WITH user_stats AS (
  SELECT 
    city,
    COUNT(*) AS user_count,
    AVG(age) AS avg_age,
    MIN(age) AS min_age,
    MAX(age) AS max_age
  FROM users_duplicate
  GROUP BY city
)
SELECT 
  city,
  user_count,
  avg_age,
  max_age - min_age AS age_range
FROM user_stats
WHERE user_count > 2
ORDER BY user_count DESC;

-- 12. 性能测试查询
-- 大数据量聚合查询
SELECT 
  city,
  COUNT(*) AS user_count,
  AVG(age) AS avg_age,
  MIN(age) AS min_age,
  MAX(age) AS max_age
FROM users_duplicate
GROUP BY city
ORDER BY user_count DESC;

-- 复杂连接查询
SELECT 
  u.user_name,
  u.city,
  COUNT(o.order_id) AS order_count,
  SUM(o.order_amount) AS total_amount,
  AVG(o.order_amount) AS avg_amount
FROM users_duplicate u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.user_name, u.city
HAVING COUNT(o.order_id) > 0
ORDER BY total_amount DESC;