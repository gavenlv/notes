-- PostgreSQL高级SQL特性示例
-- 本文件包含了各种高级SQL技术的实际应用示例

-- ================================
-- 1. 窗口函数示例
-- ================================

-- 示例数据：销售记录表
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    salesperson_id INTEGER,
    salesperson_name VARCHAR(100),
    product VARCHAR(100),
    sale_date DATE,
    amount DECIMAL(10, 2),
    region VARCHAR(50)
);

-- 插入示例数据
INSERT INTO sales (salesperson_id, salesperson_name, product, sale_date, amount, region) VALUES
(1, '张三', '笔记本电脑', '2023-01-15', 8500.00, '华北'),
(1, '张三', '台式电脑', '2023-01-17', 5200.00, '华北'),
(1, '张三', '显示器', '2023-01-20', 1800.00, '华北'),
(2, '李四', '笔记本电脑', '2023-01-16', 8800.00, '华东'),
(2, '李四', '平板电脑', '2023-01-18', 3200.00, '华东'),
(2, '李四', '智能手机', '2023-01-22', 4500.00, '华东'),
(3, '王五', '笔记本电脑', '2023-01-15', 9000.00, '华南'),
(3, '王五', '台式电脑', '2023-01-19', 6500.00, '华南'),
(3, '王五', '显示器', '2023-01-21', 2200.00, '华南');

-- 1.1 排名函数
-- ROW_NUMBER() - 为每行分配一个唯一的序号
SELECT 
    salesperson_name,
    product,
    amount,
    ROW_NUMBER() OVER (ORDER BY amount DESC) AS rank_desc,
    ROW_NUMBER() OVER (ORDER BY amount ASC) AS rank_asc
FROM sales;

-- RANK() - 排名，相同值会获得相同排名，跳过后续排名
SELECT 
    salesperson_name,
    amount,
    RANK() OVER (ORDER BY amount DESC) AS sales_rank
FROM sales;

-- DENSE_RANK() - 排名，相同值会获得相同排名，不跳过后续排名
SELECT 
    salesperson_name,
    amount,
    DENSE_RANK() OVER (ORDER BY amount DESC) AS sales_dense_rank
FROM sales;

-- 1.2 分区函数
-- 计算每个销售员内部的销售额排名
SELECT 
    salesperson_name,
    product,
    amount,
    ROW_NUMBER() OVER (PARTITION BY salesperson_id ORDER BY amount DESC) AS salesperson_rank
FROM sales
ORDER BY salesperson_name, salesperson_rank;

-- 1.3 聚合函数
-- 计算移动平均
SELECT 
    salesperson_name,
    sale_date,
    amount,
    AVG(amount) OVER (
        PARTITION BY salesperson_id 
        ORDER BY sale_date 
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) AS moving_avg
FROM sales
ORDER BY salesperson_name, sale_date;

-- 计算累计总和
SELECT 
    salesperson_name,
    sale_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY salesperson_id 
        ORDER BY sale_date 
        ROWS UNBOUNDED PRECEDING
    ) AS cumulative_sum
FROM sales
ORDER BY salesperson_name, sale_date;

-- 1.4 偏移函数
-- LAG和LEAD函数获取前一行和后一行的值
SELECT 
    salesperson_name,
    sale_date,
    amount,
    LAG(amount, 1) OVER (PARTITION BY salesperson_id ORDER BY sale_date) AS prev_sale,
    LEAD(amount, 1) OVER (PARTITION BY salesperson_id ORDER BY sale_date) AS next_sale
FROM sales
ORDER BY salesperson_name, sale_date;

-- 计算与上次销售的差异
SELECT 
    salesperson_name,
    sale_date,
    amount,
    amount - LAG(amount, 1, 0) OVER (PARTITION BY salesperson_id ORDER BY sale_date) AS diff_from_prev
FROM sales
ORDER BY salesperson_name, sale_date;

-- ================================
-- 2. CTE (通用表表达式) 示例
-- ================================

-- 2.1 基本CTE使用
WITH regional_sales AS (
    SELECT 
        region,
        SUM(amount) AS total_sales
    FROM sales
    GROUP BY region
)
SELECT 
    region,
    total_sales,
    total_sales * 100.0 / (SELECT SUM(total_sales) FROM regional_sales) AS percentage
FROM regional_sales
ORDER BY total_sales DESC;

-- 2.2 递归CTE - 层级数据
-- 创建组织架构表
CREATE TABLE IF NOT EXISTS organization (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    position VARCHAR(100),
    manager_id INTEGER REFERENCES organization(id)
);

-- 插入示例数据
INSERT INTO organization (id, name, position, manager_id) VALUES
(1, '赵总', 'CEO', NULL),
(2, '钱副总', 'VP销售', 1),
(3, '孙副总', 'VP技术', 1),
(4, '李经理', '销售经理', 2),
(5, '周经理', '技术经理', 3),
(6, '吴工程师', '高级工程师', 5),
(7, '郑销售', '销售代表', 4);

-- 使用递归CTE显示组织层级
WITH RECURSIVE org_hierarchy AS (
    -- 基础查询：获取最高层级的员工（没有经理）
    SELECT 
        id,
        name,
        position,
        manager_id,
        1 AS level,
        ARRAY[name] AS path
    FROM organization
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- 递归查询：获取下属员工
    SELECT 
        e.id,
        e.name,
        e.position,
        e.manager_id,
        h.level + 1,
        h.path || e.name
    FROM organization e
    JOIN org_hierarchy h ON e.manager_id = h.id
)
SELECT 
    level,
    REPEAT('  ', level - 1) || name AS indented_name,
    position,
    array_to_string(path, ' > ') AS reporting_path
FROM org_hierarchy
ORDER BY path;

-- ================================
-- 3. JSON和JSONB函数示例
-- ================================

-- 创建包含JSON数据的表
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    attributes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入示例数据
INSERT INTO products (name, attributes) VALUES
('智能手机', '{"brand": "Apple", "model": "iPhone 15", "storage": "256GB", "price": 8999, "features": ["5G", "Face ID", "Wireless Charging"]}'),
('笔记本电脑', '{"brand": "Dell", "model": "XPS 13", "storage": "512GB SSD", "price": 12000, "features": ["Touch Screen", "Backlit Keyboard", "Fingerprint Reader"]}'),
('平板电脑', '{"brand": "Samsung", "model": "Galaxy Tab S9", "storage": "128GB", "price": 5999, "features": ["S Pen", "Water Resistant", "DeX Mode"]}');

-- 3.1 JSONB查询和提取
-- 提取JSON字段的特定值
SELECT 
    name,
    attributes->>'brand' AS brand,
    attributes->>'model' AS model,
    (attributes->>'price')::numeric AS price
FROM products;

-- 使用->>操作符获取特定键的值
SELECT name, attributes->>'brand' AS brand
FROM products
WHERE attributes->>'brand' = 'Apple';

-- 检查JSON字段中是否存在某个键
SELECT name, attributes
FROM products
WHERE attributes ? 'features';

-- 检查JSON字段中是否存在某个键值对
SELECT name, attributes
FROM products
WHERE attributes @> '{"brand": "Apple"}';

-- 使用JSON路径查询
SELECT name, jsonb_path_query_array(attributes, '$.features[*]') AS features
FROM products;

-- 3.2 JSONB更新和修改
-- 更新JSON字段的特定键
UPDATE products
SET attributes = jsonb_set(attributes, '{price}', '8499')
WHERE name = '智能手机';

-- 向JSON字段添加新的键
UPDATE products
SET attributes = attributes || '{"color": "Space Gray"}'::jsonb
WHERE name = '智能手机';

-- 从JSON字段删除键
UPDATE products
SET attributes = attributes - 'color'
WHERE name = '智能手机';

-- 更新JSON数组中的元素
UPDATE products
SET attributes = jsonb_set(attributes, '{features, 0}', '"5G+"')
WHERE name = '智能手机';

-- ================================
-- 4. 高级JOIN操作示例
-- ================================

-- 创建示例表
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    join_date DATE
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE,
    total_amount DECIMAL(10, 2),
    status VARCHAR(20)
);

-- 插入示例数据
INSERT INTO customers (name, email, join_date) VALUES
('张三', 'zhangsan@example.com', '2022-01-15'),
('李四', 'lisi@example.com', '2022-02-20'),
('王五', 'wangwu@example.com', '2022-03-10'),
('赵六', 'zhaoliu@example.com', '2022-04-05');

INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
(1, '2023-01-10', 1200.00, 'completed'),
(1, '2023-02-15', 2500.00, 'completed'),
(1, '2023-03-20', 800.00, 'pending'),
(2, '2023-01-25', 1800.00, 'completed'),
(2, '2023-02-28', 3200.00, 'shipped'),
(4, '2023-03-15', 1500.00, 'completed');

-- 4.1 使用LEFT JOIN查找所有客户及其订单
SELECT 
    c.id AS customer_id,
    c.name AS customer_name,
    o.id AS order_id,
    o.order_date,
    o.total_amount,
    o.status
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
ORDER BY c.id, o.order_date;

-- 4.2 使用子查询查找没有订单的客户
SELECT 
    id,
    name,
    email
FROM customers
WHERE id NOT IN (SELECT DISTINCT customer_id FROM orders);

-- 4.3 使用JOIN和聚合函数计算每个客户的订单总额
SELECT 
    c.id,
    c.name,
    COUNT(o.id) AS order_count,
    COALESCE(SUM(o.total_amount), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name
ORDER BY total_spent DESC;

-- 4.4 使用CTE和JOIN计算每月的订单统计
WITH monthly_orders AS (
    SELECT 
        DATE_TRUNC('month', order_date) AS month,
        customer_id,
        COUNT(*) AS order_count,
        SUM(total_amount) AS monthly_total
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date), customer_id
)
SELECT 
    TO_CHAR(month, 'YYYY-MM') AS month,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(order_count) AS total_orders,
    SUM(monthly_total) AS total_revenue,
    AVG(monthly_total) AS avg_order_value
FROM monthly_orders
GROUP BY month
ORDER BY month;

-- ================================
-- 5. 高级分析函数示例
-- ================================

-- 创建示例数据表：学生成绩
CREATE TABLE IF NOT EXISTS student_scores (
    id SERIAL PRIMARY KEY,
    student_id INTEGER,
    student_name VARCHAR(100),
    subject VARCHAR(50),
    score INTEGER,
    exam_date DATE
);

-- 插入示例数据
INSERT INTO student_scores (student_id, student_name, subject, score, exam_date) VALUES
(1, '张三', '数学', 85, '2023-01-15'),
(1, '张三', '语文', 92, '2023-01-17'),
(1, '张三', '英语', 88, '2023-01-20'),
(2, '李四', '数学', 90, '2023-01-15'),
(2, '李四', '语文', 85, '2023-01-17'),
(2, '李四', '英语', 95, '2023-01-20'),
(3, '王五', '数学', 78, '2023-01-15'),
(3, '王五', '语文', 82, '2023-01-17'),
(3, '王五', '英语', 80, '2023-01-20'),
(1, '张三', '数学', 90, '2023-02-15'),
(1, '张三', '语文', 88, '2023-02-17'),
(1, '张三', '英语', 92, '2023-02-20');

-- 5.1 使用NTILE函数计算百分位数
SELECT 
    student_name,
    subject,
    score,
    NTILE(4) OVER (PARTITION BY subject ORDER BY score DESC) AS quartile,
    NTILE(10) OVER (PARTITION BY subject ORDER BY score DESC) AS decile,
    NTILE(100) OVER (PARTITION BY subject ORDER BY score DESC) AS percentile
FROM student_scores
WHERE exam_date = '2023-01-20'
ORDER BY subject, score DESC;

-- 5.2 计算同科目内的成绩分布
SELECT 
    subject,
    COUNT(*) AS total_students,
    AVG(score) AS avg_score,
    STDDEV(score) AS std_dev,
    MIN(score) AS min_score,
    MAX(score) AS max_score,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY score) AS median,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY score) AS q1,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY score) AS q3
FROM student_scores
WHERE exam_date = '2023-01-20'
GROUP BY subject;

-- 5.3 计算学生的成绩变化趋势
WITH score_changes AS (
    SELECT 
        student_id,
        student_name,
        subject,
        exam_date,
        score,
        LAG(score, 1) OVER (PARTITION BY student_id, subject ORDER BY exam_date) AS prev_score,
        score - LAG(score, 1) OVER (PARTITION BY student_id, subject ORDER BY exam_date) AS score_change
    FROM student_scores
)
SELECT 
    student_name,
    subject,
    exam_date,
    score,
    prev_score,
    score_change,
    CASE 
        WHEN score_change > 0 THEN '进步'
        WHEN score_change < 0 THEN '退步'
        ELSE '持平'
    END AS trend
FROM score_changes
WHERE prev_score IS NOT NULL
ORDER BY student_name, subject, exam_date;

-- ================================
-- 6. 高级数据类型示例
-- ================================

-- 6.1 数组类型
CREATE TABLE IF NOT EXISTS products_tags (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    tags TEXT[],
    categories TEXT[]
);

-- 插入包含数组的示例数据
INSERT INTO products_tags (product_name, tags, categories) VALUES
('笔记本电脑', ['便携', '高性能', '商务'], ['电子产品', '电脑']),
('智能手机', ['便携', '拍照', '5G'], ['电子产品', '手机']),
('无线耳机', ['无线', '降噪', '便携'], ['电子产品', '音频设备']);

-- 查询数组数据
SELECT 
    product_name,
    tags,
    categories,
    ARRAY_LENGTH(tags, 1) AS tag_count,
    tags[1] AS first_tag
FROM products_tags;

-- 搜索包含特定标签的产品
SELECT product_name, tags
FROM products_tags
WHERE '便携' = ANY(tags);

-- 6.2 枚举类型
-- 创建枚举类型
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');
CREATE TYPE priority AS ENUM ('low', 'medium', 'high', 'urgent');

-- 使用枚举类型创建表
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    description TEXT,
    status order_status DEFAULT 'pending',
    priority priority DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入示例数据
INSERT INTO tickets (title, description, status, priority) VALUES
('网站无法访问', '用户反映公司网站无法打开', 'processing', 'high'),
('软件更新', '需要更新办公软件到最新版本', 'pending', 'medium'),
('服务器维护', '定期服务器维护', 'delivered', 'low');

-- 查询枚举数据
SELECT * FROM tickets WHERE priority = 'high';

-- 6.3 网络地址类型
CREATE TABLE IF NOT EXISTS network_devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    ip INET,
    mac MACADDR,
    subnet CIDR
);

-- 插入网络地址示例数据
INSERT INTO network_devices (name, ip, mac, subnet) VALUES
('服务器-01', '192.168.1.10', '08:00:2b:01:02:03', '192.168.1.0/24'),
('路由器-01', '192.168.1.1', '08:00:2b:01:02:04', '192.168.1.0/24'),
('交换机-01', '192.168.1.2', '08:00:2b:01:02:05', '192.168.1.0/24');

-- 查询网络设备信息
SELECT 
    name,
    ip,
    mac,
    subnet,
    HOST(ip) AS ip_address,
    NETMASK(subnet) AS netmask,
    NETWORK(subnet) AS network_address
FROM network_devices;

-- 检查IP是否在子网内
SELECT name, ip 
FROM network_devices 
WHERE ip <<= '192.168.1.0/24';

-- ================================
-- 7. 高级查询优化技术示例
-- ================================

-- 7.1 索引使用示例
-- 在常用查询字段上创建索引
CREATE INDEX IF NOT EXISTS idx_sales_salesperson_date ON sales(salesperson_id, sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_amount ON sales(amount);
CREATE INDEX IF NOT EXISTS idx_sales_region ON sales(region);

-- 7.2 使用EXPLAIN分析查询计划
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
SELECT 
    salesperson_name,
    SUM(amount) AS total_sales
FROM sales
WHERE region = '华北'
GROUP BY salesperson_name
ORDER BY total_sales DESC;

-- 7.3 物化视图示例
-- 创建物化视图存储销售汇总数据
CREATE MATERIALIZED VIEW IF NOT EXISTS sales_summary AS
SELECT 
    salesperson_id,
    salesperson_name,
    region,
    COUNT(*) AS total_sales,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    MIN(sale_date) AS first_sale,
    MAX(sale_date) AS last_sale
FROM sales
GROUP BY salesperson_id, salesperson_name, region
WITH DATA;

-- 查询物化视图
SELECT * FROM sales_summary ORDER BY total_amount DESC;

-- 刷新物化视图（更新数据）
REFRESH MATERIALIZED VIEW sales_summary;

-- 7.4 窗口函数优化查询
-- 使用窗口函数代替自连接提高查询性能
SELECT 
    DISTINCT s1.salesperson_name,
    s1.sale_date,
    s1.amount,
    (SELECT COUNT(*) FROM sales s2 
     WHERE s2.salesperson_id = s1.salesperson_id 
     AND s2.sale_date <= s1.sale_date) AS cumulative_sales
FROM sales s1
ORDER BY s1.salesperson_name, s1.sale_date;

-- 使用窗口函数的优化版本
SELECT 
    salesperson_name,
    sale_date,
    amount,
    COUNT(*) OVER (PARTITION BY salesperson_id ORDER BY sale_date) AS cumulative_sales
FROM sales
ORDER BY salesperson_name, sale_date;

-- ================================
-- 8. 高级数据操作示例
-- ================================

-- 8.1 UPSERT操作（INSERT ON CONFLICT）
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(100),
    theme VARCHAR(20) DEFAULT 'light',
    notifications BOOLEAN DEFAULT true,
    language VARCHAR(10) DEFAULT 'en'
);

-- 插入初始数据
INSERT INTO user_preferences (user_id, username, theme, notifications, language)
VALUES (1, '张三', 'dark', true, 'zh'),
       (2, '李四', 'light', false, 'en');

-- 使用UPSERT更新或插入数据
INSERT INTO user_preferences (user_id, username, theme, notifications, language)
VALUES (1, '张三', 'light', false, 'zh'),
       (3, '王五', 'dark', true, 'en')
ON CONFLICT (user_id) 
DO UPDATE SET 
    theme = EXCLUDED.theme,
    notifications = EXCLUDED.notifications,
    language = EXCLUDED.language;

-- 8.2 批量更新
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    quantity INTEGER,
    price DECIMAL(10, 2)
);

-- 插入示例数据
INSERT INTO inventory (product_name, quantity, price) VALUES
('产品A', 100, 29.99),
('产品B', 50, 49.99),
('产品C', 75, 19.99);

-- 使用VALUES子句进行批量更新
UPDATE inventory
SET quantity = v.quantity, price = v.price
FROM (VALUES 
    (1, 150, 31.99),
    (3, 60, 17.99)
) AS v(id, quantity, price)
WHERE inventory.id = v.id;

-- 8.3 条件更新
-- 根据条件更新不同的值
UPDATE inventory
SET 
    price = CASE 
        WHEN product_name = '产品A' THEN price * 1.1
        WHEN product_name = '产品B' THEN price * 1.05
        WHEN product_name = '产品C' THEN price * 0.95
        ELSE price
    END,
    updated_at = CURRENT_TIMESTAMP
WHERE product_name IN ('产品A', '产品B', '产品C');

-- 8.4 使用CTE进行复杂更新
-- 创建表存储销售目标
CREATE TABLE IF NOT EXISTS sales_targets (
    salesperson_id INTEGER PRIMARY KEY,
    salesperson_name VARCHAR(100),
    target_amount DECIMAL(10, 2),
    period VARCHAR(20)
);

INSERT INTO sales_targets (salesperson_id, salesperson_name, target_amount, period)
VALUES (1, '张三', 15000.00, '2023-01'),
       (2, '李四', 12000.00, '2023-01'),
       (3, '王五', 18000.00, '2023-01');

-- 使用CTE更新销售目标完成情况
WITH actual_sales AS (
    SELECT 
        salesperson_id,
        SUM(amount) AS actual_amount
    FROM sales
    WHERE TO_CHAR(sale_date, 'YYYY-MM') = '2023-01'
    GROUP BY salesperson_id
)
UPDATE sales_targets
SET 
    target_amount = st.actual_amount * 1.1
FROM actual_sales st
WHERE sales_targets.salesperson_id = st.salesperson_id;

-- ================================
-- 9. 高级分析技术示例
-- ================================

-- 9.1 时间序列分析
-- 创建时间序列数据表
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    price_date DATE,
    open_price DECIMAL(10, 2),
    high_price DECIMAL(10, 2),
    low_price DECIMAL(10, 2),
    close_price DECIMAL(10, 2),
    volume INTEGER
);

-- 插入示例数据
INSERT INTO stock_prices (symbol, price_date, open_price, high_price, low_price, close_price, volume) VALUES
('AAPL', '2023-01-02', 130.28, 130.90, 124.17, 129.93, 112117471),
('AAPL', '2023-01-03', 127.89, 130.29, 124.76, 125.07, 111033714),
('AAPL', '2023-01-04', 126.89, 128.66, 125.08, 126.36, 89124662),
('AAPL', '2023-01-05', 127.13, 130.29, 126.82, 129.61, 93346815),
('MSFT', '2023-01-02', 245.73, 246.76, 239.22, 239.78, 33759789),
('MSFT', '2023-01-03', 240.17, 241.95, 236.36, 240.01, 27926163),
('MSFT', '2023-01-04', 238.91, 241.18, 235.82, 239.58, 26616332),
('MSFT', '2023-01-05', 241.45, 241.85, 238.51, 239.78, 25239543);

-- 计算移动平均
SELECT 
    symbol,
    price_date,
    close_price,
    AVG(close_price) OVER (
        PARTITION BY symbol 
        ORDER BY price_date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3day,
    AVG(close_price) OVER (
        PARTITION BY symbol 
        ORDER BY price_date 
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) AS moving_avg_5day
FROM stock_prices
ORDER BY symbol, price_date;

-- 计算价格变化和百分比变化
SELECT 
    symbol,
    price_date,
    close_price,
    close_price - LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY price_date) AS price_change,
    (close_price - LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY price_date)) / 
        LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY price_date) * 100 AS pct_change
FROM stock_prices
ORDER BY symbol, price_date;

-- 9.2 同期比较分析
-- 创建销售数据表
CREATE TABLE IF NOT EXISTS monthly_sales (
    id SERIAL PRIMARY KEY,
    product_id INTEGER,
    product_name VARCHAR(100),
    sales_month DATE,
    sales_amount DECIMAL(10, 2)
);

-- 插入示例数据
INSERT INTO monthly_sales (product_id, product_name, sales_month, sales_amount) VALUES
(1, '产品A', '2022-10-01', 10000.00),
(1, '产品A', '2022-11-01', 12000.00),
(1, '产品A', '2022-12-01', 15000.00),
(1, '产品A', '2023-01-01', 13000.00),
(1, '产品A', '2023-02-01', 14000.00),
(1, '产品A', '2023-03-01', 16000.00),
(2, '产品B', '2022-10-01', 8000.00),
(2, '产品B', '2022-11-01', 8500.00),
(2, '产品B', '2022-12-01', 9000.00),
(2, '产品B', '2023-01-01', 9500.00),
(2, '产品B', '2023-02-01', 10000.00),
(2, '产品B', '2023-03-01', 10500.00);

-- 同期比较查询
WITH current_month AS (
    SELECT 
        product_id,
        product_name,
        EXTRACT(MONTH FROM sales_month) AS month,
        EXTRACT(YEAR FROM sales_month) AS year,
        sales_amount
    FROM monthly_sales
),
previous_year AS (
    SELECT 
        product_id,
        EXTRACT(MONTH FROM sales_month) AS month,
        sales_amount AS prev_year_amount
    FROM monthly_sales
    WHERE EXTRACT(YEAR FROM sales_month) = EXTRACT(YEAR FROM CURRENT_DATE) - 1
)
SELECT 
    cm.product_name,
    TO_CHAR(DATE '2023-01-01' + INTERVAL '1 month' * (cm.month - 1), 'Month') AS month_name,
    cm.sales_amount AS current_year,
    py.prev_year_amount,
    cm.sales_amount - py.prev_year_amount AS absolute_change,
    ((cm.sales_amount - py.prev_year_amount) / py.prev_year_amount * 100) AS percentage_change
FROM current_month cm
JOIN previous_year py ON cm.product_id = py.product_id AND cm.month = py.month
WHERE cm.year = 2023
ORDER BY cm.product_name, cm.month;

-- 9.3 漏斗分析
-- 创建用户行为表
CREATE TABLE IF NOT EXISTS user_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    event_type VARCHAR(50),
    event_timestamp TIMESTAMP
);

-- 插入示例数据
INSERT INTO user_events (user_id, event_type, event_timestamp) VALUES
(1, 'page_view', '2023-01-01 08:00:00'),
(1, 'add_to_cart', '2023-01-01 08:05:00'),
(1, 'checkout', '2023-01-01 08:10:00'),
(1, 'purchase', '2023-01-01 08:15:00'),
(2, 'page_view', '2023-01-01 09:00:00'),
(2, 'add_to_cart', '2023-01-01 09:05:00'),
(2, 'checkout', '2023-01-01 09:10:00'),
(3, 'page_view', '2023-01-01 10:00:00'),
(3, 'add_to_cart', '2023-01-01 10:05:00'),
(4, 'page_view', '2023-01-01 11:00:00'),
(5, 'page_view', '2023-01-01 12:00:00'),
(5, 'add_to_cart', '2023-01-01 12:05:00'),
(5, 'checkout', '2023-01-01 12:10:00'),
(5, 'purchase', '2023-01-01 12:15:00'),
(6, 'page_view', '2023-01-01 13:00:00'),
(6, 'add_to_cart', '2023-01-01 13:05:00'),
(6, 'purchase', '2023-01-01 13:15:00');

-- 漏斗分析查询
WITH funnel_events AS (
    SELECT 
        user_id,
        MAX(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END) AS viewed_page,
        MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS added_to_cart,
        MAX(CASE WHEN event_type = 'checkout' THEN 1 ELSE 0 END) AS started_checkout,
        MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS completed_purchase
    FROM user_events
    WHERE event_timestamp >= '2023-01-01' AND event_timestamp < '2023-01-02'
    GROUP BY user_id
),
funnel_counts AS (
    SELECT 
        SUM(viewed_page) AS viewed_page_count,
        SUM(added_to_cart) AS added_to_cart_count,
        SUM(started_checkout) AS started_checkout_count,
        SUM(completed_purchase) AS completed_purchase_count
    FROM funnel_events
)
SELECT 
    'Viewed Page' AS funnel_stage,
    viewed_page_count AS user_count,
    viewed_page_count * 100.0 / viewed_page_count AS conversion_rate
FROM funnel_counts

UNION ALL

SELECT 
    'Added to Cart' AS funnel_stage,
    added_to_cart_count AS user_count,
    added_to_cart_count * 100.0 / viewed_page_count AS conversion_rate
FROM funnel_counts

UNION ALL

SELECT 
    'Started Checkout' AS funnel_stage,
    started_checkout_count AS user_count,
    started_checkout_count * 100.0 / viewed_page_count AS conversion_rate
FROM funnel_counts

UNION ALL

SELECT 
    'Completed Purchase' AS funnel_stage,
    completed_purchase_count AS user_count,
    completed_purchase_count * 100.0 / viewed_page_count AS conversion_rate
FROM funnel_counts;

-- ================================
-- 10. 清理示例数据
-- ================================

-- 删除创建的示例表（可选）
-- DROP TABLE IF EXISTS sales CASCADE;
-- DROP TABLE IF EXISTS organization CASCADE;
-- DROP TABLE IF EXISTS products CASCADE;
-- DROP TABLE IF EXISTS customers CASCADE;
-- DROP TABLE IF EXISTS orders CASCADE;
-- DROP TABLE IF EXISTS student_scores CASCADE;
-- DROP TABLE IF EXISTS products_tags CASCADE;
-- DROP TABLE IF EXISTS tickets CASCADE;
-- DROP TABLE IF EXISTS network_devices CASCADE;
-- DROP TABLE IF EXISTS user_preferences CASCADE;
-- DROP TABLE IF EXISTS inventory CASCADE;
-- DROP TABLE IF EXISTS sales_targets CASCADE;
-- DROP TABLE IF EXISTS stock_prices CASCADE;
-- DROP TABLE IF EXISTS monthly_sales CASCADE;
-- DROP TABLE IF EXISTS user_events CASCADE;

-- 删除物化视图（可选）
-- DROP MATERIALIZED VIEW IF EXISTS sales_summary CASCADE;

-- 删除自定义类型（可选）
-- DROP TYPE IF EXISTS order_status CASCADE;
-- DROP TYPE IF EXISTS priority CASCADE;