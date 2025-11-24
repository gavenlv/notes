# PostgreSQL高级特性教程

## 目录

1. [JSON/JSONB数据类型与操作](#jsonjsonb数据类型与操作)
2. [数组类型与函数](#数组类型与函数)
3. [高级索引技术](#高级索引技术)
4. [窗口函数进阶](#窗口函数进阶)
5. [CTE与递归查询](#cte与递归查询)
6. [高级表分区](#高级表分区)
7. [物化视图](#物化视图)
8. [触发器与规则](#触发器与规则)
9. [全文搜索](#全文搜索)
10. [并发控制与锁](#并发控制与锁)
11. [性能调优](#性能调优)

---

## JSON/JSONB数据类型与操作

### JSON与JSONB的区别

PostgreSQL提供了两种JSON数据类型：

- **JSON**：存储文本格式的JSON数据，保留原始格式和空格
- **JSONB**：存储二进制格式的JSON数据，处理速度更快，支持索引

```sql
-- 创建包含JSON/JSONB的表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    attributes JSON,
    metadata JSONB
);

-- 插入数据
INSERT INTO products (name, attributes, metadata) VALUES
('智能手机', '{"color": "black", "storage": "128GB", "screen": "6.1英寸"}', 
 '{"brand": "TechCorp", "model": "X100", "price": 6999, "in_stock": true}'),
('笔记本电脑', '{"color": "silver", "ram": "16GB", "screen": "14英寸"}', 
 '{"brand": "DataWorks", "model": "ProBook", "price": 12999, "in_stock": false}');
```

### JSON/JSONB操作函数

```sql
-- 提取JSON值
SELECT 
    name,
    attributes -> 'color' AS color,         -- 返回JSON
    attributes ->> 'color' AS color_text,    -- 返回文本
    metadata -> 'price' AS price_json,
    (metadata ->> 'price')::numeric AS price_num
FROM products;

-- 检查JSON字段是否存在
SELECT 
    name,
    attributes ? 'storage' AS has_storage,
    metadata ? 'price' AS has_price
FROM products;

-- 检查JSON字段是否包含所有指定键
SELECT 
    name,
    attributes ?& array['color', 'storage'] AS has_all_keys,
    attributes ?| array['color', 'weight'] AS has_any_key
FROM products;

-- 获取JSON对象的所有键
SELECT 
    name,
    jsonb_object_keys(metadata) AS meta_keys
FROM products;

-- 更新JSONB字段
UPDATE products
SET metadata = jsonb_set(
    metadata, 
    '{price}', 
    '6499'::jsonb
)
WHERE name = '智能手机';

-- 向JSONB添加或更新字段
UPDATE products
SET metadata = metadata || '{"discount": 10}'::jsonb
WHERE name = '智能手机';

-- 从JSONB删除字段
UPDATE products
SET metadata = metadata - 'discount'
WHERE name = '智能手机';

-- 嵌套JSON访问
SELECT 
    name,
    metadata -> 'specifications' ->> 'cpu' AS cpu_type
FROM products
WHERE metadata ? 'specifications';

-- JSONB路径查询
SELECT 
    name,
    metadata #>> '{price}' AS price,
    metadata @> '{"in_stock": true}' AS in_stock,
    metadata <@ '{"brand": "TechCorp", "price": 6999}' AS matches_spec
FROM products;
```

### JSON/JSONB索引

```sql
-- 创建GIN索引用于高效JSONB查询
CREATE INDEX idx_products_metadata_gin ON products USING GIN (metadata);

-- 创建表达式索引用于特定JSON字段
CREATE INDEX idx_products_metadata_price ON products ((metadata ->> 'price'));

-- 使用索引优化查询
EXPLAIN ANALYZE
SELECT name FROM products WHERE metadata @> '{"in_stock": true}';

-- 复杂JSONB查询示例
SELECT 
    name,
    metadata ->> 'brand' AS brand,
    (metadata ->> 'price')::numeric AS price
FROM products
WHERE metadata @> '{"in_stock": true}' 
  AND (metadata ->> 'price')::numeric > 5000
ORDER BY (metadata ->> 'price')::numeric DESC;
```

---

## 数组类型与函数

### 数组数据类型

```sql
-- 创建包含数组的表
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    skills TEXT[],               -- 文本数组
    work_hours INTEGER[],        -- 整数数组
    phone_numbers VARCHAR(15)[],
    weekly_schedule INTEGER[7]   -- 固定大小数组(一周7天)
);

-- 插入数据
INSERT INTO employees (name, skills, work_hours, phone_numbers, weekly_schedule) VALUES
('张三', ARRAY['Python', 'Java', 'SQL'], ARRAY[8, 8, 8, 8, 8, 4, 0], 
 ARRAY['13812345678', '01012345678'], ARRAY[8, 8, 8, 8, 8, 4, 0]),
('李四', ARRAY['JavaScript', 'React', 'Node.js'], ARRAY[9, 9, 9, 9, 0, 0, 0], 
 ARRAY['13912345678'], ARRAY[9, 9, 9, 9, 0, 0, 0]);
```

### 数组操作

```sql
-- 访问数组元素
SELECT 
    name,
    skills[1] AS primary_skill,          -- 第一个元素(从1开始)
    skills[2] AS secondary_skill,
    skills[cardinality(skills)] AS last_skill,  -- 最后一个元素
    weekly_schedule[1] AS monday_hours
FROM employees;

-- 数组信息
SELECT 
    name,
    cardinality(skills) AS skill_count,
    array_dims(weekly_schedule) AS schedule_dims,
    array_length(weekly_schedule, 1) AS schedule_length
FROM employees;

-- 数组搜索
SELECT name FROM employees WHERE 'Python' = ANY(skills);
SELECT name FROM employees WHERE skills @> ARRAY['Python', 'SQL'];  -- 包含所有元素
SELECT name FROM employees WHERE skills && ARRAY['Python', 'Java', 'Go']; -- 包含任意元素

-- 数组修改
UPDATE employees
SET skills = array_append(skills, 'Git')
WHERE name = '张三';

UPDATE employees
SET skills = array_prepend('Docker', skills)
WHERE name = '李四';

UPDATE employees
SET skills = array_remove(skills, 'Java')
WHERE name = '张三';

UPDATE employees
SET skills = array_replace(skills, 'JavaScript', 'TypeScript')
WHERE name = '李四';

-- 数组连接
SELECT 
    name,
    skills || array['Project Management'] AS extended_skills,
    skills || skills AS doubled_skills,
    skills || ARRAY['soft_skill_1', 'soft_skill_2'] AS all_skills
FROM employees;

-- 数组聚合函数
SELECT 
    UNNEST(skills) AS skill,
    COUNT(*) AS employee_count
FROM employees
GROUP BY skill
ORDER BY employee_count DESC;

-- 将多行数据聚合为数组
SELECT 
    array_agg(name) AS employee_names,
    array_agg(DISTINCT UNNEST(skills)) AS all_skills
FROM employees;

-- 数组去重
SELECT name, array DISTINCT skills FROM employees;
```

### 数组索引

```sql
-- 创建GIN索引用于高效数组搜索
CREATE INDEX idx_employees_skills_gin ON employees USING GIN (skills);

-- 创建表达式索引
CREATE INDEX idx_employees_primary_skill ON employees ((skills[1]));

-- 使用索引优化查询
EXPLAIN ANALYZE
SELECT name FROM employees WHERE skills @> ARRAY['Python', 'SQL'];
```

---

## 高级索引技术

### 部分索引

```sql
-- 创建只索引部分数据的索引
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date) 
WHERE status = 'shipped';

-- 只为活跃用户创建索引
CREATE INDEX idx_users_email_active ON users(email) 
WHERE status = 'active';

-- 使用部分索引
SELECT * FROM orders WHERE customer_id = 123 AND status = 'shipped';
```

### 表达式索引

```sql
-- 为函数结果创建索引
CREATE INDEX idx_products_name_lower ON products(LOWER(name));
CREATE INDEX idx_users_email_domain ON users(SUBSTRING(email FROM POSITION('@' IN email) + 1));
CREATE INDEX idx_orders_monthly ON orders(DATE_TRUNC('month', order_date));

-- 使用表达式索引
SELECT * FROM products WHERE LOWER(name) = 'smartphone';
SELECT * FROM users WHERE SUBSTRING(email FROM POSITION('@' IN email) + 1) = 'example.com';
```

### 多列索引和索引顺序

```sql
-- 创建多列索引
CREATE INDEX idx_orders_customer_status_date ON orders(customer_id, status, order_date);

-- 不同列顺序优化不同查询
CREATE INDEX idx_orders_date_status ON orders(order_date, status);
CREATE INDEX idx_orders_status_date ON orders(status, order_date);

-- 覆盖索引包含查询所需的所有列
CREATE INDEX idx_orders_customer_covering ON orders(customer_id, status, order_date, total_amount);
```

### 唯一索引和条件唯一索引

```sql
-- 唯一索引
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- 条件唯一索引(只对满足条件的行要求唯一)
CREATE UNIQUE INDEX idx_active_users_email_unique ON users(email) WHERE status = 'active';

-- 多列条件唯一索引
CREATE UNIQUE INDEX idx_product_category_name_unique ON products(category, name) WHERE status = 'active';
```

### 哈希索引和B-树索引选择

```sql
-- 哈希索引(适合等值查询)
CREATE INDEX idx_users_email_hash ON users USING HASH(email);

-- B-树索引(默认，适合范围查询和排序)
CREATE INDEX idx_users_name_btree ON users USING BTREE(last_name, first_name);

-- GiST索引(支持几何数据、全文搜索)
CREATE INDEX idx_documents_gin ON documents USING GIN(to_tsvector('english', content));

-- SP-GiST索引(支持分区数据结构)
CREATE INDEX idx_locations_spgist ON locations USING SPGIST(coordinates);
```

---

## 窗口函数进阶

### 高级窗口框架

```sql
-- 窗口框架的灵活使用
SELECT 
    order_date,
    customer_id,
    total_amount,
    -- 移动平均: 当前行前后各1天
    AVG(total_amount) OVER (
        ORDER BY order_date 
        RANGE BETWEEN '1 day' PRECEDING AND '1 day' FOLLOWING
    ) AS moving_avg_3days,
    
    -- 累计总和: 从当前分区的第一行到当前行
    SUM(total_amount) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date 
        ROWS UNBOUNDED PRECEDING
    ) AS customer_cumulative_amount,
    
    -- 滚动总和: 当前行前3行到当前行
    SUM(total_amount) OVER (
        ORDER BY order_date 
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS rolling_sum_4days
FROM orders;
```

### 窗口函数与条件聚合

```sql
-- 条件聚合与窗口函数结合
SELECT 
    order_date,
    customer_id,
    total_amount,
    -- 计算同一客户前一笔订单金额
    LAG(total_amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_amount,
    
    -- 计算同一客户小于当前金额的订单数
    COUNT(CASE WHEN total_amount < o.total_amount THEN 1 END) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS smaller_orders_count
FROM orders o;
```

### 窗口函数与JSON/数组结合

```sql
-- 窗口函数处理JSON数据
SELECT 
    id,
    order_date,
    json_data,
    -- 提取JSON数组中的值并计算窗口函数
    json_array_length(json_data->'items') AS item_count,
    SUM((json_data->'items'->0->>'price')::NUMERIC) OVER (
        ORDER BY order_date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_first_item_price
FROM json_orders;

-- 窗口函数处理数组数据
SELECT 
    employee_id,
    work_hours,
    -- 计算工时标准差
    STDDEV(work_hours) OVER (
        PARTITION BY department_id 
        ORDER BY work_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS work_hours_stddev_7days,
    
    -- 计算工时排名
    PERCENT_RANK() OVER (
        PARTITION BY department_id 
        ORDER BY work_hours
    ) AS work_hours_percentile
FROM employee_attendance;
```

---

## CTE与递归查询

### 基本CTE(Common Table Expression)

```sql
-- 使用CTE简化复杂查询
WITH regional_sales AS (
    SELECT 
        region,
        SUM(total_amount) AS regional_total
    FROM orders
    GROUP BY region
),
top_regions AS (
    SELECT 
        region,
        regional_total,
        RANK() OVER (ORDER BY regional_total DESC) AS sales_rank
    FROM regional_sales
)
SELECT region, regional_total
FROM top_regions
WHERE sales_rank <= 3;

-- 多CTE连接
WITH 
sales_summary AS (
    SELECT 
        DATE_TRUNC('month', order_date) AS month,
        region,
        SUM(total_amount) AS monthly_amount
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date), region
),
regional_totals AS (
    SELECT 
        region,
        SUM(monthly_amount) AS total_amount
    FROM sales_summary
    GROUP BY region
),
monthly_performance AS (
    SELECT 
        s.month,
        s.region,
        s.monthly_amount,
        r.total_amount,
        ROUND(s.monthly_amount * 100.0 / r.total_amount, 2) AS percentage_of_total
    FROM sales_summary s
    JOIN regional_totals r ON s.region = r.region
)
SELECT 
    month,
    region,
    monthly_amount,
    percentage_of_total,
    LAG(percentage_of_total, 1) OVER (PARTITION BY region ORDER BY month) AS previous_month_percentage
FROM monthly_performance
ORDER BY region, month;
```

### 递归CTE

```sql
-- 递归查询处理层次结构数据
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    manager_id INTEGER REFERENCES employees(id),
    department VARCHAR(50)
);

-- 使用递归CTE查找员工层级
WITH RECURSIVE employee_hierarchy AS (
    -- 基础查询: 获取顶级员工(没有经理)
    SELECT 
        id, 
        name, 
        manager_id, 
        department,
        1 AS level,
        ARRAY[name] AS path,
        name::TEXT AS manager_name
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- 递归查询: 获取下属员工
    SELECT 
        e.id,
        e.name,
        e.manager_id,
        e.department,
        eh.level + 1,
        eh.path || e.name,
        eh.name
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT 
    level,
    name,
    department,
    manager_name,
    path
FROM employee_hierarchy
ORDER BY path;

-- 使用递归CTE处理产品类别层次
CREATE TABLE product_categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES product_categories(id)
);

-- 查询所有类别及其完整路径
WITH RECURSIVE category_paths AS (
    SELECT 
        id, 
        name, 
        parent_id,
        name AS full_path
    FROM product_categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT 
        pc.id, 
        pc.name, 
        pc.parent_id,
        cp.full_path || ' > ' || pc.name
    FROM product_categories pc
    JOIN category_paths cp ON pc.parent_id = cp.id
)
SELECT 
    id,
    name,
    full_path
FROM category_paths
ORDER BY full_path;
```

### CTE与窗口函数结合

```sql
-- CTE与窗口函数结合进行复杂分析
WITH monthly_sales AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', order_date) AS month,
        SUM(total_amount) AS monthly_amount
    FROM orders
    GROUP BY customer_id, DATE_TRUNC('month', order_date)
),
customer_monthly_ranking AS (
    SELECT 
        customer_id,
        month,
        monthly_amount,
        RANK() OVER (PARTITION BY customer_id ORDER BY monthly_amount DESC) AS customer_rank,
        PERCENT_RANK() OVER (ORDER BY monthly_amount DESC) AS global_percentile
    FROM monthly_sales
),
top_months AS (
    SELECT 
        customer_id,
        month,
        monthly_amount,
        customer_rank
    FROM customer_monthly_ranking
    WHERE customer_rank <= 3
)
SELECT 
    o.customer_id,
    c.name AS customer_name,
    t.month,
    t.monthly_amount,
    t.customer_rank,
    cmr.global_percentile
FROM top_months t
JOIN orders o ON DATE_TRUNC('month', o.order_date) = t.month
JOIN customers c ON o.customer_id = c.id
JOIN customer_monthly_ranking cmr ON t.customer_id = cmr.customer_id AND t.month = cmr.month
GROUP BY o.customer_id, c.name, t.month, t.monthly_amount, t.customer_rank, cmr.global_percentile
ORDER BY t.month, t.monthly_amount DESC;
```

---

## 高级表分区

### 表分区基础

```sql
-- 创建分区表
CREATE TABLE sales (
    id SERIAL,
    order_date DATE NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL
) PARTITION BY RANGE (order_date);

-- 创建分区
CREATE TABLE sales_2023_q1 PARTITION OF sales
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

CREATE TABLE sales_2023_q2 PARTITION OF sales
    FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');

CREATE TABLE sales_2023_q3 PARTITION OF sales
    FOR VALUES FROM ('2023-07-01') TO ('2023-10-01');

CREATE TABLE sales_2023_q4 PARTITION OF sales
    FOR VALUES FROM ('2023-10-01') TO ('2024-01-01');

-- 查看分区信息
SELECT 
    schemaname,
    tablename,
    partitionname,
    partitionbounds
FROM pg_partition_tables
WHERE schemaname = 'public';

-- 插入数据会自动路由到正确的分区
INSERT INTO sales (order_date, customer_id, product_id, amount) VALUES
('2023-02-15', 101, 201, 99.99),  -- 进入2023_q1分区
('2023-05-20', 102, 202, 149.99), -- 进入2023_q2分区
('2023-08-25', 103, 203, 199.99); -- 进入2023_q3分区
```

### 多级分区

```sql
-- 创建多级分区表
CREATE TABLE sales_multi (
    id SERIAL,
    order_date DATE NOT NULL,
    region VARCHAR(50) NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL
) PARTITION BY LIST (region);

-- 一级分区(按地区)
CREATE TABLE sales_north PARTITION OF sales_multi
    FOR VALUES IN ('华北', '东北');
    
CREATE TABLE sales_south PARTITION OF sales_multi
    FOR VALUES IN ('华南', '西南');

CREATE TABLE sales_eastwest PARTITION OF sales_multi
    DEFAULT;

-- 二级分区(在地区内按季度)
CREATE TABLE sales_north_q1 PARTITION OF sales_north
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01')
    PARTITION BY RANGE (order_date);

CREATE TABLE sales_north_q2 PARTITION OF sales_north
    FOR VALUES FROM ('2023-04-01') TO ('2023-07-01')
    PARTITION BY RANGE (order_date);

-- 进一步细分...
```

### 哈希分区

```sql
-- 创建哈希分区表
CREATE TABLE user_activities (
    id SERIAL,
    user_id INTEGER NOT NULL,
    activity_date TIMESTAMP NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    metadata JSONB
) PARTITION BY HASH (user_id);

-- 创建哈希分区
CREATE TABLE user_activities_0 PARTITION OF user_activities
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE user_activities_1 PARTITION OF user_activities
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE user_activities_2 PARTITION OF user_activities
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE user_activities_3 PARTITION OF user_activities
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

### 分区维护

```sql
-- 添加新分区
CREATE TABLE sales_2024_q1 PARTITION OF sales
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

-- 分离分区
ALTER TABLE sales DETACH PARTITION sales_2023_q1;

-- 附加分区
ALTER TABLE sales ATTACH PARTITION sales_2023_q1
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

-- 删除分区
DROP TABLE sales_2023_q1;

-- 分区裁剪(查询优化)
EXPLAIN ANALYZE
SELECT * FROM sales
WHERE order_date BETWEEN '2023-01-01' AND '2023-03-31';  -- 只会扫描sales_2023_q1分区
```

---

## 物化视图

### 基本物化视图

```sql
-- 创建物化视图
CREATE MATERIALIZED VIEW mv_monthly_sales AS
SELECT 
    DATE_TRUNC('month', order_date) AS month,
    region,
    COUNT(DISTINCT customer_id) AS customer_count,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount
FROM sales
GROUP BY DATE_TRUNC('month', order_date), region
WITH DATA;

-- 查询物化视图
SELECT * FROM mv_monthly_sales ORDER BY month, total_amount DESC;

-- 创建唯一索引(用于REFRESH CONCURRENTLY)
CREATE UNIQUE INDEX idx_mv_monthly_sales_unique 
ON mv_monthly_sales (month, region);

-- 刷新物化视图
REFRESH MATERIALIZED VIEW mv_monthly_sales;

-- 并发刷新(不阻塞查询)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_sales;
```

### 高级物化视图

```sql
-- 包含复杂计算的物化视图
CREATE MATERIALIZED VIEW mv_customer_segmentation AS
WITH customer_stats AS (
    SELECT 
        customer_id,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        COUNT(*) AS order_count,
        SUM(amount) AS total_spent,
        AVG(amount) AS avg_order_value
    FROM orders
    GROUP BY customer_id
),
customer_segments AS (
    SELECT 
        customer_id,
        first_order_date,
        last_order_date,
        order_count,
        total_spent,
        avg_order_value,
        CASE 
            WHEN total_spent > 10000 THEN 'VIP'
            WHEN total_spent > 5000 THEN 'Gold'
            WHEN total_spent > 2000 THEN 'Silver'
            ELSE 'Regular'
        END AS segment,
        -- 计算RFM指标
        NTILE(5) OVER (ORDER BY last_order_date DESC) AS recency_score,
        NTILE(5) OVER (ORDER BY order_count DESC) AS frequency_score,
        NTILE(5) OVER (ORDER BY total_spent DESC) AS monetary_score
    FROM customer_stats
)
SELECT 
    cs.*,
    customers.name,
    customers.email,
    -- 计算综合RFM分数
    (cs.recency_score + cs.frequency_score + cs.monetary_score) AS rfm_score
FROM customer_segments cs
JOIN customers ON cs.customer_id = customers.id
WITH DATA;

-- 增量刷新策略
-- 1. 创建增量更新表
CREATE TABLE monthly_sales_incremental (
    month DATE PRIMARY KEY,
    region VARCHAR(50),
    customer_count INTEGER,
    order_count INTEGER,
    total_amount DECIMAL(10,2),
    avg_amount DECIMAL(10,2)
);

-- 2. 定期将新数据插入增量表
INSERT INTO monthly_sales_incremental
SELECT 
    DATE_TRUNC('month', order_date) AS month,
    region,
    COUNT(DISTINCT customer_id) AS customer_count,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount
FROM sales
WHERE order_date >= '2023-06-01'  -- 只处理最近的数据
GROUP BY DATE_TRUNC('month', order_date), region
ON CONFLICT (month, region) DO UPDATE SET
    customer_count = EXCLUDED.customer_count,
    order_count = EXCLUDED.order_count,
    total_amount = EXCLUDED.total_amount,
    avg_amount = EXCLUDED.avg_amount;

-- 3. 合并增量数据到物化视图
CREATE MATERIALIZED VIEW mv_monthly_sales_v2 AS
SELECT * FROM mv_monthly_sales
WHERE month < '2023-06-01'
UNION ALL
SELECT * FROM monthly_sales_incremental
WITH DATA;
```

### 物化视图优化

```sql
-- 查询物化视图状态
SELECT 
    schemaname,
    matviewname,
    matviewowner,
    hasindexes,
    ispopulated
FROM pg_matviews
WHERE schemaname = 'public';

-- 查询物化视图大小
SELECT 
    matviewname,
    pg_size_pretty(pg_total_relation_size(matviewname::regclass)) AS size
FROM pg_matviews
WHERE schemaname = 'public';

-- 自动刷新策略(使用pg_cron扩展)
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 每日凌晨2点刷新物化视图
SELECT cron.schedule('refresh-monthly-sales', '0 2 * * *', 
    'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_sales');
```

---

## 触发器与规则

### 触发器基础

```sql
-- 创建审计表
CREATE TABLE order_audit (
    audit_id SERIAL PRIMARY KEY,
    order_id INTEGER,
    operation VARCHAR(10) NOT NULL,  -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建触发器函数
CREATE OR REPLACE FUNCTION audit_order_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO order_audit (order_id, operation, new_values, changed_by)
        VALUES (NEW.id, TG_OP, row_to_json(NEW), current_user);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO order_audit (order_id, operation, old_values, new_values, changed_by)
        VALUES (NEW.id, TG_OP, row_to_json(OLD), row_to_json(NEW), current_user);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO order_audit (order_id, operation, old_values, changed_by)
        VALUES (OLD.id, TG_OP, row_to_json(OLD), current_user);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_audit_orders
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION audit_order_changes();

-- 测试触发器
INSERT INTO orders (customer_id, order_date, amount) VALUES (101, CURRENT_DATE, 99.99);
UPDATE orders SET amount = 109.99 WHERE id = 1;
DELETE FROM orders WHERE id = 1;

-- 查看审计记录
SELECT * FROM order_audit ORDER BY changed_at DESC;
```

### 高级触发器

```sql
-- 自动更新时间戳的触发器
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_modified
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- 级联操作的触发器
CREATE OR REPLACE FUNCTION update_inventory_on_order()
RETURNS TRIGGER AS $$
DECLARE
    product_record RECORD;
BEGIN
    -- 检查每个产品库存
    FOR product_record IN 
        SELECT product_id, quantity FROM order_items WHERE order_id = NEW.id
    LOOP
        UPDATE products 
        SET stock = stock - product_record.quantity
        WHERE id = product_record.product_id;
        
        -- 如果库存低于阈值，创建补货提醒
        IF (SELECT stock FROM products WHERE id = product_record.product_id) < 10 THEN
            INSERT INTO restock_notifications (product_id, created_at)
            VALUES (product_record.product_id, CURRENT_TIMESTAMP);
        END IF;
    END LOOP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_inventory
    AFTER INSERT ON orders
    FOR EACH ROW EXECUTE FUNCTION update_inventory_on_order();
```

### 规则

```sql
-- 创建规则实现视图更新
CREATE VIEW active_products AS
SELECT * FROM products WHERE status = 'active';

-- 创建规则使视图可更新
CREATE OR REPLACE RULE update_active_products AS
ON UPDATE TO active_products
DO INSTEAD
    UPDATE products 
    SET name = NEW.name, 
        price = NEW.price, 
        status = NEW.status
    WHERE id = OLD.id AND status = 'active';

CREATE OR REPLACE RULE delete_active_products AS
ON DELETE TO active_products
DO INSTEAD
    UPDATE products 
    SET status = 'inactive'
    WHERE id = OLD.id;

-- 创建重定向规则
CREATE TABLE archived_orders (
    LIKE orders INCLUDING ALL
);

-- 将超过一年的订单自动归档
CREATE OR REPLACE RULE archive_old_orders AS
ON INSERT TO orders
WHERE NEW.order_date < CURRENT_DATE - INTERVAL '1 year'
DO INSTEAD
    INSERT INTO archived_orders VALUES (NEW.*);
```

---

## 全文搜索

### 基本全文搜索

```sql
-- 创建全文搜索配置
CREATE TEXT SEARCH CONFIGURATION english_unaccent (COPY = english);

-- 添加文档到全文搜索
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(100),
    publish_date DATE,
    -- 存储预处理后的搜索向量
    search_vector tsvector
);

-- 创建触发器自动更新搜索向量
CREATE OR REPLACE FUNCTION update_document_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english_unaccent', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english_unaccent', COALESCE(NEW.content, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_document_vector
    BEFORE INSERT OR UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_document_search_vector();

-- 插入示例数据
INSERT INTO documents (title, content, author, publish_date) VALUES
('PostgreSQL高级特性', 'PostgreSQL提供了强大的高级特性，包括窗口函数、JSONB支持等...', '张三', '2023-01-15'),
('SQL性能优化', '数据库性能优化需要从查询设计、索引策略、表结构等多方面考虑...', '李四', '2023-02-20'),
('NoSQL vs SQL', '关系型数据库和NoSQL数据库各有优势，选择哪种取决于应用场景...', '王五', '2023-03-10');
```

### 全文搜索查询

```sql
-- 基本全文搜索
SELECT title, author, publish_date
FROM documents
WHERE search_vector @@ to_tsquery('english_unaccent', 'PostgreSQL & 特性');

-- 排序搜索结果
SELECT 
    title, 
    author,
    ts_rank(search_vector, to_tsquery('english_unaccent', 'PostgreSQL & 特性')) AS rank
FROM documents
WHERE search_vector @@ to_tsquery('english_unaccent', 'PostgreSQL & 特性')
ORDER BY rank DESC;

-- 高亮搜索关键词
SELECT 
    title, 
    ts_headline('english_unaccent', title, to_tsquery('english_unaccent', '性能 & 优化')) AS title_highlight,
    ts_headline('english_unaccent', content, to_tsquery('english_unaccent', '性能 & 优化')) AS content_highlight
FROM documents
WHERE search_vector @@ to_tsquery('english_unaccent', '性能 & 优化');

-- 使用plainto_tsquery进行自然语言搜索
SELECT title, author
FROM documents
WHERE search_vector @@ plainto_tsquery('english_unaccent', '数据库性能优化');

-- 使用phraseto_tsquery进行短语搜索
SELECT title, author
FROM documents
WHERE search_vector @@ phraseto_tsquery('english_unaccent', 'SQL 优化');
```

### 全文搜索索引

```sql
-- 创建GIN索引
CREATE INDEX idx_documents_search_vector ON documents USING GIN (search_vector);

-- 创建包含权重的复合索引
CREATE INDEX idx_documents_vector_author ON documents 
USING GIN (search_vector) 
WHERE author = '张三';

-- 使用索引优化查询
EXPLAIN ANALYZE
SELECT title FROM documents 
WHERE search_vector @@ to_tsquery('english_unaccent', 'PostgreSQL & 特性');
```

---

## 并发控制与锁

### 事务隔离级别

```sql
-- 设置事务隔离级别
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 查看当前隔离级别
SHOW transaction_isolation;

-- 演示隔离级别差异
-- 终端1:
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE id = 1;  -- 假设返回1000

-- 终端2:
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- 终端1:
SELECT balance FROM accounts WHERE id = 1;  -- 仍返回1000，不受终端2影响
COMMIT;
```

### 锁类型与使用

```sql
-- 显式锁定
BEGIN WORK;
LOCK TABLE accounts IN SHARE MODE;  -- 共享锁(其他事务可读但不可写)
LOCK TABLE accounts IN EXCLUSIVE MODE;  -- 排他锁(其他事务不可读写)

-- 行级锁
BEGIN WORK;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;  -- 锁定特定行
SELECT * FROM accounts WHERE id = 1 FOR SHARE;   -- 共享行锁

-- 查看锁状态
SELECT 
    pid,
    relation::regclass AS table_name,
    mode,
    granted,
    query
FROM pg_locks
JOIN pg_stat_activity ON pid = pid
WHERE relation IS NOT NULL;
```

### 乐观并发控制

```sql
-- 使用version字段实现乐观并发控制
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    version INTEGER NOT NULL DEFAULT 0
);

-- 乐观并发更新
BEGIN WORK;
SELECT id, name, price, version FROM products WHERE id = 1;  -- 假设返回version=0

-- 在应用中修改数据
UPDATE products 
SET name = 'Updated Product', price = 99.99, version = version + 1
WHERE id = 1 AND version = 0;  -- 只有当version未被其他事务修改时才成功

-- 检查更新是否成功
IF ROW_COUNT = 0 THEN
    -- 处理冲突，例如重新获取数据并重试
    ROLLBACK;
ELSE
    COMMIT;
END IF;

-- 使用SELECT FOR UPDATE实现悲观并发控制
BEGIN WORK;
SELECT * FROM products WHERE id = 1 FOR UPDATE;  -- 锁定行
-- 修改数据
UPDATE products SET name = 'Updated Product', price = 99.99 WHERE id = 1;
COMMIT;
```

---

## 性能调优

### 查询性能分析

```sql
-- 使用EXPLAIN分析查询计划
EXPLAIN 
SELECT o.customer_id, c.name, SUM(o.amount) AS total_spent
FROM orders o
JOIN customers c ON o.customer_id = c.id
GROUP BY o.customer_id, c.name
HAVING SUM(o.amount) > 1000
ORDER BY total_spent DESC;

-- 使用EXPLAIN ANALYZE获取实际执行统计
EXPLAIN ANALYZE 
SELECT o.customer_id, c.name, SUM(o.amount) AS total_spent
FROM orders o
JOIN customers c ON o.customer_id = c.id
GROUP BY o.customer_id, c.name
HAVING SUM(o.amount) > 1000
ORDER BY total_spent DESC;

-- 使用EXPLAIN (ANALYZE, BUFFERS)获取缓存使用情况
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM orders WHERE order_date >= '2023-01-01';

-- 使用EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)获取详细JSON格式计划
EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON) 
SELECT * FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE region = '华北');
```

### 统计信息与自动分析

```sql
-- 查看表的统计信息
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE tablename = 'orders'
ORDER BY attname;

-- 手动更新表的统计信息
ANALYZE orders;

-- 为特定列收集统计信息
ANALYZE orders (order_date, customer_id);

-- 扩展统计信息(多列关联统计)
CREATE STATISTICS s_orders_customer_date (dependencies) 
ON customer_id, order_date FROM orders;

CREATE STATISTICS s_orders_region_amount (ndistinct) 
ON region, amount FROM orders;

-- 查看扩展统计信息
SELECT 
    stxname,
    stxnamespace::regnamespace AS schema,
    stxrel::regclass AS table,
    stxkeys,
    stxkind
FROM pg_statistic_ext;
```

### 服务器参数调优

```sql
-- 查看当前配置参数
SHOW shared_buffers;
SHOW work_mem;
SHOW maintenance_work_mem;
SHOW effective_cache_size;
SHOW random_page_cost;
SHOW cpu_tuple_cost;
SHOW cpu_index_tuple_cost;

-- 修改参数(临时，会话级别)
SET work_mem = '64MB';
SET maintenance_work_mem = '256MB';

-- 修改参数(永久，需要修改postgresql.conf文件)
-- shared_buffers = 256MB
-- work_mem = 4MB
-- maintenance_work_mem = 64MB
-- effective_cache_size = 1GB
-- random_page_cost = 1.1  -- SSD系统
-- random_page_cost = 4.0  -- 传统HDD系统
```

### 高级性能技术

```sql
-- 使用并行查询
SET max_parallel_workers_per_gather = 4;
SET parallel_tuple_cost = 0.1;
SET parallel_setup_cost = 1000.0;

-- 强制并行查询
SET max_parallel_workers_per_gather = 2;
EXPLAIN ANALYZE 
SELECT * FROM large_table WHERE condition;

-- 表空间优化
CREATE TABLESPACE fast_ssd LOCATION '/mnt/ssd/postgresql';
CREATE TABLESPACE archive_hdd LOCATION '/mnt/hdd/postgresql';

-- 将不同表放在不同表空间
CREATE TABLE active_data (
    id SERIAL,
    data TEXT
) TABLESPACE fast_ssd;

CREATE TABLE archived_data (
    id SERIAL,
    data TEXT
) TABLESPACE archive_hdd;

-- 表压缩
CREATE TABLE compressed_data (
    id SERIAL,
    data TEXT
) WITH (fillfactor = 80);

-- 使用TOAST压缩大字段
ALTER TABLE large_documents ALTER COLUMN document SET STORAGE EXTERNAL;
```

---

## 总结

本教程详细介绍了PostgreSQL的高级特性，包括：

1. **JSON/JSONB数据类型**：处理半结构化数据的能力和操作技巧
2. **数组类型**：处理数组数据的方法和函数
3. **高级索引技术**：部分索引、表达式索引、多列索引等优化技术
4. **窗口函数进阶**：复杂窗口框架和高级应用场景
5. **CTE与递归查询**：处理层次数据和复杂查询
6. **表分区**：提高大表查询和维护性能的技术
7. **物化视图**：预计算复杂查询结果的方法
8. **触发器与规则**：自动化数据库操作的技术
9. **全文搜索**：实现高效文本搜索功能
10. **并发控制与锁**：处理并发访问和保持数据一致性的机制
11. **性能调优**：分析查询性能和优化数据库的方法

PostgreSQL作为最先进的开源关系型数据库，提供了丰富的高级特性，使其能够应对各种复杂的数据处理需求。掌握这些高级特性，将使您能够：

- 设计更高效的数据结构
- 优化复杂查询性能
- 处理海量数据
- 实现高级数据分析
- 提高并发处理能力

通过本教程的学习，您应该能够充分利用PostgreSQL的强大功能，解决复杂的数据管理问题，构建高性能、可扩展的数据库应用。