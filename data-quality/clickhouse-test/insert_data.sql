-- ClickHouse 测试数据插入
-- 使用测试数据库
USE data_quality_test;

-- 插入用户数据
-- 邮箱大写，用于测试大小写敏感性
-- 空邮箱，用于测试完整性
-- 年龄超出范围，用于测试数据范围
-- 空名称，用于测试完整性
-- 重复用户ID，用于测试唯一性
INSERT INTO users (user_id, email, name, age) VALUES
(1, 'john.doe@example.com', 'John Doe', 30),
(2, 'jane.smith@example.com', 'Jane Smith', 25),
(3, 'bob.johnson@example.com', 'Bob Johnson', 40),
(4, 'alice.williams@example.com', 'Alice Williams', 35),
(5, 'charlie.brown@example.com', 'Charlie Brown', 28),
(6, 'DAVID.MILLER@example.com', 'David Miller', 45),
(7, '', 'Empty Email', 22),
(8, 'invalid.age@example.com', 'Invalid Age', 150),
(9, 'null.name@example.com', '', 33),
(10, 'duplicate@example.com', 'Duplicate User', 29),
(10, 'duplicate@example.com', 'Duplicate User', 29);

-- 插入客户数据
INSERT INTO customers (customer_id, company_name, contact_name, email, phone) VALUES
(101, 'ABC Corporation', 'John Manager', 'contact@abccorp.com', '+1-123-456-7890'),
(102, 'XYZ Ltd', 'Jane Director', 'info@xyzltd.com', '+1-234-567-8901'),
(103, 'Acme Inc', 'Bob CEO', 'hello@acmeinc.com', '+1-345-678-9012'),
(104, 'Tech Solutions', 'Alice CTO', 'support@techsolutions.com', '+1-456-789-0123'),
(105, 'Global Services', 'Charlie Manager', 'info@globalservices.com', '+1-567-890-1234');

-- 插入订单数据
-- 无效的客户ID，用于测试引用完整性
-- 空客户ID，用于测试非空约束
-- 负金额，用于测试数据范围
-- 无效状态，用于测试枚举约束（注释掉无效值）
INSERT INTO orders (order_id, customer_id, order_date, total_amount, status) VALUES
(1001, 101, '2023-01-15', 1250.50, 'delivered'),
(1002, 102, '2023-01-20', 890.25, 'shipped'),
(1003, 103, '2023-01-25', 1500.75, 'processing'),
(1004, 104, '2023-01-30', 2100.00, 'pending'),
(1005, 105, '2023-02-05', 950.30, 'delivered'),
(1006, 999, '2023-02-10', 1200.00, 'shipped'),
(1007, NULL, '2023-02-15', 800.50, 'processing'),
(1008, 103, '2023-02-20', -500.25, 'pending');

-- 以下行包含无效的枚举值'unknown'，已注释掉
-- (1009, 104, '2023-02-25', 1800.75, 'unknown');

-- 插入产品数据
-- 价格超出范围，用于测试数据范围
-- 负库存，用于测试数据范围
-- 重量超出范围，用于测试数据范围
-- 零价格，用于测试数据范围
-- 空重量，用于测试可空字段
INSERT INTO products (product_id, product_name, category, price, stock_quantity, weight) VALUES
(201, 'Laptop', 'Electronics', 1200.00, 50, 2.5),
(202, 'Smartphone', 'Electronics', 800.50, 100, 0.3),
(203, 'Desk Chair', 'Furniture', 150.75, 30, 15.0),
(204, 'Coffee Table', 'Furniture', 250.25, 20, 25.0),
(205, 'Headphones', 'Electronics', 100.00, 200, 0.2),
(206, 'Expensive Item', 'Luxury', 15000.00, 5, 1.0),
(207, 'Out of Stock', 'Electronics', 500.00, -10, 0.5),
(208, 'Heavy Item', 'Furniture', 300.00, 10, 1500.0),
(209, 'Free Item', 'Promotion', 0.00, 1000, 1.0),
(210, 'Digital Product', 'Software', 50.00, 999999, NULL);

-- 插入订单明细数据
-- 无效的订单ID，用于测试引用完整性
-- 无效的产品ID，用于测试引用完整性
-- 零数量，用于测试数据范围
-- 负单价，用于测试数据范围
INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price) VALUES
(10001, 1001, 201, 1, 1200.00),
(10002, 1001, 205, 2, 100.00),
(10003, 1002, 202, 1, 800.50),
(10004, 1002, 205, 1, 100.00),
(10005, 1003, 203, 4, 150.75),
(10006, 1003, 204, 2, 250.25),
(10007, 1004, 201, 1, 1200.00),
(10008, 1004, 202, 1, 800.50),
(10009, 1005, 205, 5, 100.00),
(10010, 9999, 201, 1, 1200.00),
(10011, 1006, 999, 2, 500.00),
(10012, 1007, 203, 0, 150.75),
(10013, 1008, 204, 1, -50.00);