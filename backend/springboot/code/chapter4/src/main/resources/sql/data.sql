-- 插入用户数据
INSERT INTO users (username, email, created_at) VALUES
('张三', 'zhangsan@example.com', '2022-01-01 10:00:00'),
('李四', 'lisi@example.com', '2022-01-02 11:00:00'),
('王五', 'wangwu@example.com', '2022-01-03 12:00:00'),
('赵六', 'zhaoliu@example.com', '2022-01-04 13:00:00'),
('钱七', 'qianqi@example.com', '2022-01-05 14:00:00');

-- 插入订单数据
INSERT INTO orders (user_id, product_name, price, quantity, total_amount, created_at) VALUES
(1, 'iPhone 13', 999.99, 1, 999.99, '2022-01-10 10:30:00'),
(1, 'MacBook Pro', 1999.99, 1, 1999.99, '2022-01-11 11:30:00'),
(2, 'iPad Air', 599.99, 2, 1199.98, '2022-01-12 12:30:00'),
(3, 'Apple Watch', 399.99, 1, 399.99, '2022-01-13 13:30:00'),
(4, 'AirPods Pro', 249.99, 3, 749.97, '2022-01-14 14:30:00');