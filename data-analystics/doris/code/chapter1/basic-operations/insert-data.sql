-- 插入数据示例
-- 连接方式: mysql -h 127.0.0.1 -P 9030 -uroot demo

USE demo;

-- 1. 向Duplicate模型表插入数据
INSERT INTO users_duplicate VALUES
(1, 'Alice', 25, 'Beijing', '2023-01-01', '2023-06-15 10:30:00'),
(2, 'Bob', 30, 'Shanghai', '2023-01-02', '2023-06-15 09:45:00'),
(3, 'Charlie', 35, 'Guangzhou', '2023-01-03', '2023-06-14 18:20:00'),
(4, 'David', 28, 'Shenzhen', '2023-01-04', '2023-06-15 11:15:00'),
(5, 'Eva', 32, 'Hangzhou', '2023-01-05', '2023-06-14 16:40:00'),
(6, 'Frank', 29, 'Nanjing', '2023-01-06', '2023-06-15 08:55:00'),
(7, 'Grace', 27, 'Wuhan', '2023-01-07', '2023-06-14 14:25:00'),
(8, 'Henry', 31, 'Chengdu', '2023-01-08', '2023-06-15 13:10:00'),
(9, 'Ivy', 26, 'Xian', '2023-01-09', '2023-06-14 17:35:00'),
(10, 'Jack', 33, 'Suzhou', '2023-01-10', '2023-06-15 12:05:00');

-- 批量插入Duplicate模型表数据
INSERT INTO users_duplicate (user_id, user_name, age, city, register_date, last_login_time)
VALUES
(11, 'Kate', 24, 'Tianjin', '2023-01-11', '2023-06-14 10:20:00'),
(12, 'Liam', 36, 'Qingdao', '2023-01-12', '2023-06-15 15:45:00'),
(13, 'Mia', 29, 'Dalian', '2023-01-13', '2023-06-14 09:30:00'),
(14, 'Noah', 34, 'Xiamen', '2023-01-14', '2023-06-15 14:15:00'),
(15, 'Olivia', 23, 'Changsha', '2023-01-15', '2023-06-14 16:50:00');

-- 2. 向Aggregate模型表插入数据
INSERT INTO sales_aggregate VALUES
('2023-06-15', 101, 'Laptop', 'Beijing', 10, 50000.00, 5500.00, 4500.00),
('2023-06-15', 102, 'Mouse', 'Beijing', 50, 2500.00, 60.00, 40.00),
('2023-06-15', 103, 'Keyboard', 'Shanghai', 30, 4500.00, 160.00, 120.00),
('2023-06-15', 104, 'Monitor', 'Shanghai', 20, 20000.00, 1200.00, 800.00),
('2023-06-15', 105, 'Headphone', 'Guangzhou', 40, 4000.00, 120.00, 80.00),
('2023-06-15', 106, 'Webcam', 'Shenzhen', 25, 2500.00, 110.00, 90.00),
('2023-06-15', 107, 'USB Hub', 'Hangzhou', 60, 3000.00, 55.00, 35.00),
('2023-06-15', 108, 'Docking Station', 'Nanjing', 15, 7500.00, 550.00, 450.00);

-- 再次插入相同产品的销售数据，验证聚合效果
INSERT INTO sales_aggregate VALUES
('2023-06-15', 101, 'Laptop', 'Beijing', 5, 27500.00, 5600.00, 4600.00),
('2023-06-15', 102, 'Mouse', 'Beijing', 30, 1500.00, 65.00, 45.00),
('2023-06-15', 103, 'Keyboard', 'Shanghai', 20, 3000.00, 170.00, 130.00);

-- 3. 向Unique模型表插入数据
INSERT INTO user_profiles_unique VALUES
(1, 'Alice', 'alice@example.com', '13812345678', 2, '1998-05-15', 'Beijing Haidian District', '2023-06-15 10:30:00'),
(2, 'Bob', 'bob@example.com', '13923456789', 1, '1993-08-22', 'Shanghai Pudong District', '2023-06-15 09:45:00'),
(3, 'Charlie', 'charlie@example.com', '13634567890', 1, '1988-12-10', 'Guangzhou Tianhe District', '2023-06-14 18:20:00'),
(4, 'David', 'david@example.com', '13745678901', 1, '1995-03-18', 'Shenzhen Nanshan District', '2023-06-15 11:15:00'),
(5, 'Eva', 'eva@example.com', '13856789012', 2, '1991-07-25', 'Hangzhou West Lake District', '2023-06-14 16:40:00');

-- 尝试插入重复的user_id，验证唯一性约束
INSERT INTO user_profiles_unique VALUES
(1, 'Alice Smith', 'alice.smith@example.com', '13912345678', 2, '1998-05-15', 'Beijing Chaoyang District', '2023-06-15 20:30:00');

-- 4. 向Primary Key模型表插入数据
INSERT INTO user_metrics_pk VALUES
(1, 25, 1500.50, '2023-06-15 10:30:00', '2023-06-15 10:30:00'),
(2, 18, 850.25, '2023-06-14 15:20:00', '2023-06-14 15:20:00'),
(3, 32, 3200.75, '2023-06-15 09:15:00', '2023-06-15 09:15:00'),
(4, 12, 450.00, '2023-06-13 14:45:00', '2023-06-13 14:45:00'),
(5, 28, 2100.30, '2023-06-15 11:05:00', '2023-06-15 11:05:00');

-- 更新Primary Key模型表数据
INSERT INTO user_metrics_pk VALUES
(1, 26, 1800.50, '2023-06-15 20:30:00', '2023-06-15 20:30:00'),
(3, 33, 3500.75, '2023-06-15 19:45:00', '2023-06-15 19:45:00');

-- 5. 向分区表插入数据
INSERT INTO event_logs VALUES
('2023-01-01 08:30:00', 'page_view', 1, 'session_001', 'https://example.com/home', '', 'Mozilla/5.0...', '192.168.1.1', 'China', 'Beijing'),
('2023-01-01 08:31:15', 'click', 1, 'session_001', 'https://example.com/product/101', 'https://example.com/home', 'Mozilla/5.0...', '192.168.1.1', 'China', 'Beijing'),
('2023-01-01 08:32:30', 'page_view', 2, 'session_002', 'https://example.com/search', '', 'Mozilla/5.0...', '192.168.1.2', 'China', 'Shanghai'),
('2023-01-01 08:33:45', 'search', 2, 'session_002', 'https://example.com/search?q=laptop', 'https://example.com/search', 'Mozilla/5.0...', '192.168.1.2', 'China', 'Shanghai'),
('2023-01-01 08:35:00', 'page_view', 3, 'session_003', 'https://example.com/cart', '', 'Mozilla/5.0...', '192.168.1.3', 'China', 'Guangzhou'),
('2023-01-02 09:15:00', 'page_view', 1, 'session_004', 'https://example.com/home', '', 'Mozilla/5.0...', '192.168.1.1', 'China', 'Beijing'),
('2023-01-02 09:16:30', 'login', 1, 'session_004', 'https://example.com/login', 'https://example.com/home', 'Mozilla/5.0...', '192.168.1.1', 'China', 'Beijing'),
('2023-01-02 09:18:00', 'page_view', 4, 'session_005', 'https://example.com/product/205', '', 'Mozilla/5.0...', '192.168.1.4', 'China', 'Shenzhen'),
('2023-01-02 09:19:15', 'add_to_cart', 4, 'session_005', 'https://example.com/cart/add/205', 'https://example.com/product/205', 'Mozilla/5.0...', '192.168.1.4', 'China', 'Shenzhen'),
('2023-01-02 09:20:30', 'page_view', 5, 'session_006', 'https://example.com/checkout', '', 'Mozilla/5.0...', '192.168.1.5', 'China', 'Hangzhou');

-- 显示表中的数据量
SELECT COUNT(*) AS user_count FROM users_duplicate;
SELECT COUNT(*) AS sales_count FROM sales_aggregate;
SELECT COUNT(*) AS profile_count FROM user_profiles_unique;
SELECT COUNT(*) AS metrics_count FROM user_metrics_pk;
SELECT COUNT(*) AS event_count FROM event_logs;