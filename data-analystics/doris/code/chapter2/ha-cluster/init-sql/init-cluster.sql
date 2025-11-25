-- Doris高可用集群初始化SQL脚本
-- 用于创建初始数据库、用户和权限配置

-- 创建数据库
CREATE DATABASE IF NOT EXISTS demo;
USE demo;

-- 创建管理员用户
CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'admin123';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%';

-- 创建只读用户
CREATE USER IF NOT EXISTS 'readonly'@'%' IDENTIFIED BY 'readonly123';
GRANT SELECT_PRIV ON *.* TO 'readonly'@'%';

-- 创建应用用户
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'appuser123';
GRANT SELECT_PRIV, INSERT_PRIV, UPDATE_PRIV, DELETE_PRIV, CREATE_PRIV, DROP_PRIV, ALTER_PRIV ON demo.* TO 'app_user'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 创建示例表
CREATE TABLE IF NOT EXISTS demo.users (
    user_id BIGINT,
    user_name VARCHAR(50),
    age INT,
    city VARCHAR(20),
    register_date DATE,
    last_login_time DATETIME
) DUPLICATE KEY(user_id, user_name)
DISTRIBUTED BY HASH(user_id) BUCKETS 10;

-- 创建示例数据表
CREATE TABLE IF NOT EXISTS demo.events (
    event_id BIGINT,
    user_id BIGINT,
    event_type VARCHAR(20),
    event_time DATETIME,
    properties VARCHAR(1024)
) DUPLICATE KEY(event_id, user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 20
PROPERTIES (
    "compression"="LZ4",
    "enable_unique_key_merge_on_write"="true"
);

-- 创建聚合模型表示例
CREATE TABLE IF NOT EXISTS demo.user_stats (
    user_id BIGINT,
    city VARCHAR(20),
    total_events BIGINT SUM DEFAULT '0',
    last_event_time DATETIME REPLACE,
    update_time DATETIME REPLACE_IF_NOT_NULL
) AGGREGATE KEY(user_id, city)
DISTRIBUTED BY HASH(user_id) BUCKETS 10;

-- 创建分区表示例
CREATE TABLE IF NOT EXISTS demo.daily_sales (
    sale_date DATE,
    region VARCHAR(20),
    product_id BIGINT,
    amount DECIMAL(18, 2) SUM DEFAULT '0.00',
    count BIGINT SUM DEFAULT '0'
) AGGREGATE KEY(sale_date, region, product_id)
DISTRIBUTED BY HASH(sale_date, region) BUCKETS 16
PROPERTIES (
    "compression"="LZ4",
    "dynamic_partition.enable"="true",
    "dynamic_partition.time_unit"="DAY",
    "dynamic_partition.start"="-30",
    "dynamic_partition.end"="7",
    "dynamic_partition.prefix"="p",
    "dynamic_partition.buckets"="16"
);

-- 创建唯一键模型表示例
CREATE TABLE IF NOT EXISTS demo.user_profiles (
    user_id BIGINT,
    user_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(200),
    update_time DATETIME
) UNIQUE KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 10
PROPERTIES (
    "enable_unique_key_merge_on_write"="true"
);

-- 创建主键模型表示例
CREATE TABLE IF NOT EXISTS demo.orders (
    order_id BIGINT,
    user_id BIGINT,
    product_id BIGINT,
    quantity INT,
    price DECIMAL(18, 2),
    order_time DATETIME,
    status VARCHAR(20)
) PRIMARY KEY(order_id)
DISTRIBUTED BY HASH(order_id) BUCKETS 20
PROPERTIES (
    "enable_unique_key_merge_on_write"="true",
    "compression"="LZ4"
);

-- 插入一些示例数据
INSERT INTO demo.users (user_id, user_name, age, city, register_date, last_login_time) VALUES
(1, 'Alice', 25, 'Beijing', '2023-01-15', '2023-11-20 10:30:00'),
(2, 'Bob', 30, 'Shanghai', '2023-02-20', '2023-11-21 14:45:00'),
(3, 'Charlie', 35, 'Guangzhou', '2023-03-10', '2023-11-22 09:15:00'),
(4, 'David', 28, 'Shenzhen', '2023-04-05', '2023-11-23 16:20:00'),
(5, 'Eva', 32, 'Hangzhou', '2023-05-12', '2023-11-24 11:30:00');

INSERT INTO demo.events (event_id, user_id, event_type, event_time, properties) VALUES
(1001, 1, 'login', '2023-11-20 10:30:00', '{"ip": "192.168.1.1", "device": "mobile"}'),
(1002, 2, 'click', '2023-11-21 14:45:00', '{"page": "home", "element": "button"}'),
(1003, 3, 'view', '2023-11-22 09:15:00', '{"page": "product", "product_id": "12345"}'),
(1004, 4, 'purchase', '2023-11-23 16:20:00', '{"order_id": "5001", "amount": "99.99"}'),
(1005, 5, 'logout', '2023-11-24 11:30:00', '{"session_duration": "3600"}');

INSERT INTO demo.user_stats (user_id, city, total_events, last_event_time, update_time) VALUES
(1, 'Beijing', 1, '2023-11-20 10:30:00', '2023-11-20 10:30:00'),
(2, 'Shanghai', 1, '2023-11-21 14:45:00', '2023-11-21 14:45:00'),
(3, 'Guangzhou', 1, '2023-11-22 09:15:00', '2023-11-22 09:15:00'),
(4, 'Shenzhen', 1, '2023-11-23 16:20:00', '2023-11-23 16:20:00'),
(5, 'Hangzhou', 1, '2023-11-24 11:30:00', '2023-11-24 11:30:00');

INSERT INTO demo.daily_sales (sale_date, region, product_id, amount, count) VALUES
('2023-11-20', 'North', 101, 1200.50, 25),
('2023-11-20', 'South', 102, 800.75, 18),
('2023-11-21', 'East', 103, 1500.00, 30),
('2023-11-21', 'West', 104, 950.25, 22),
('2023-11-22', 'North', 105, 1100.80, 28);

INSERT INTO demo.user_profiles (user_id, user_name, email, phone, address, update_time) VALUES
(1, 'Alice', 'alice@example.com', '13800138001', 'Beijing, China', '2023-11-20 10:30:00'),
(2, 'Bob', 'bob@example.com', '13800138002', 'Shanghai, China', '2023-11-21 14:45:00'),
(3, 'Charlie', 'charlie@example.com', '13800138003', 'Guangzhou, China', '2023-11-22 09:15:00'),
(4, 'David', 'david@example.com', '13800138004', 'Shenzhen, China', '2023-11-23 16:20:00'),
(5, 'Eva', 'eva@example.com', '13800138005', 'Hangzhou, China', '2023-11-24 11:30:00');

INSERT INTO demo.orders (order_id, user_id, product_id, quantity, price, order_time, status) VALUES
(5001, 4, 104, 2, 99.99, '2023-11-23 16:20:00', 'completed'),
(5002, 1, 101, 1, 120.00, '2023-11-24 09:30:00', 'shipped'),
(5003, 3, 103, 3, 45.50, '2023-11-24 14:15:00', 'processing'),
(5004, 2, 102, 1, 85.75, '2023-11-25 10:45:00', 'completed'),
(5005, 5, 105, 2, 65.25, '2023-11-25 16:30:00', 'pending');

-- 创建视图
CREATE VIEW IF NOT EXISTS demo.user_event_summary AS
SELECT 
    u.user_id,
    u.user_name,
    u.city,
    COUNT(e.event_id) AS event_count,
    MAX(e.event_time) AS last_event_time
FROM demo.users u
LEFT JOIN demo.events e ON u.user_id = e.user_id
GROUP BY u.user_id, u.user_name, u.city;

-- 创建物化视图
CREATE MATERIALIZED VIEW IF NOT EXISTS demo.daily_sales_region_mv AS
SELECT 
    sale_date,
    region,
    SUM(amount) AS total_amount,
    SUM(count) AS total_count
FROM demo.daily_sales
GROUP BY sale_date, region;

-- 显示创建的表
SHOW TABLES FROM demo;

-- 显示创建的视图
SHOW VIEWS FROM demo;

-- 显示创建的物化视图
SHOW MATERIALIZED VIEWS FROM demo;

-- 显示集群状态
SHOW FRONTENDS;
SHOW BACKENDS;

-- 显示用户权限
SHOW ALL GRANTS;

-- 显示数据库信息
SHOW DATABASES;

-- 显示当前数据库
SELECT DATABASE();

-- 显示当前用户
SELECT CURRENT_USER();

-- 显示示例数据
SELECT 'Users table sample data:' AS info;
SELECT * FROM demo.users LIMIT 5;

SELECT 'Events table sample data:' AS info;
SELECT * FROM demo.events LIMIT 5;

SELECT 'User stats table sample data:' AS info;
SELECT * FROM demo.user_stats LIMIT 5;

SELECT 'Daily sales table sample data:' AS info;
SELECT * FROM demo.daily_sales LIMIT 5;

SELECT 'User profiles table sample data:' AS info;
SELECT * FROM demo.user_profiles LIMIT 5;

SELECT 'Orders table sample data:' AS info;
SELECT * FROM demo.orders LIMIT 5;

SELECT 'User event summary view sample data:' AS info;
SELECT * FROM demo.user_event_summary LIMIT 5;

SELECT 'Daily sales region materialized view sample data:' AS info;
SELECT * FROM demo.daily_sales_region_mv LIMIT 5;