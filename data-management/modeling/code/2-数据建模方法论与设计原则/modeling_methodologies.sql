-- =============================================
-- 数据建模方法论与设计原则 - 代码示例
-- 展示不同建模方法在电商系统中的应用
-- =============================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS ecommerce_modeling CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce_modeling;

-- =============================================
-- 2. ER模型实现 - 事务处理系统
-- =============================================

-- 2.1 创建ER模型的核心表
CREATE TABLE IF NOT EXISTS er_user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='ER模型：用户表';

CREATE TABLE IF NOT EXISTS er_product (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    stock INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='ER模型：产品表';

CREATE TABLE IF NOT EXISTS er_order (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES er_user(user_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='ER模型：订单表';

CREATE TABLE IF NOT EXISTS er_order_item (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES er_order(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES er_product(product_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='ER模型：订单详情表';

-- 2.2 插入ER模型测试数据
INSERT INTO er_user (username, email, password_hash, first_name, last_name, phone) VALUES
('john_doe', 'john@example.com', 'hashed_password_1', 'John', 'Doe', '123-456-7890'),
('jane_smith', 'jane@example.com', 'hashed_password_2', 'Jane', 'Smith', '987-654-3210');

INSERT INTO er_product (product_name, description, price, category, stock) VALUES
('iPhone 14 Pro', '6.1-inch Super Retina XDR display', 999.00, 'Electronics', 50),
('Dell XPS 13', '13.3-inch Ultrabook with Intel Core i7', 999.99, 'Electronics', 30),
('Nike Air Max', 'Men\'s sneakers with Max Air cushioning', 150.00, 'Clothing', 100);

INSERT INTO er_order (user_id, total_amount, status) VALUES
(1, 1998.99, 'Completed'),
(2, 150.00, 'Pending');

INSERT INTO er_order_item (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 999.00),
(1, 2, 1, 999.99),
(2, 3, 1, 150.00);

-- 2.3 ER模型查询示例
SELECT 
    u.username, 
    o.order_id, 
    o.order_date, 
    o.status, 
    p.product_name, 
    oi.quantity, 
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS subtotal
FROM er_order o
JOIN er_user u ON o.user_id = u.user_id
JOIN er_order_item oi ON o.order_id = oi.order_id
JOIN er_product p ON oi.product_id = p.product_id
WHERE u.username = 'john_doe';

-- =============================================
-- 3. 维度建模实现 - 数据仓库
-- =============================================

-- 3.1 创建维度表
CREATE TABLE IF NOT EXISTS dim_time (
    time_id INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
) ENGINE=InnoDB COMMENT='维度建模：时间维度表';

CREATE TABLE IF NOT EXISTS dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    brand VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    supplier VARCHAR(100),
    product_status VARCHAR(20) DEFAULT 'Active'
) ENGINE=InnoDB COMMENT='维度建模：产品维度表';

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(50) DEFAULT 'Unknown',
    state VARCHAR(50) DEFAULT 'Unknown',
    country VARCHAR(50) DEFAULT 'Unknown',
    membership_level VARCHAR(20) DEFAULT 'Standard'
) ENGINE=InnoDB COMMENT='维度建模：客户维度表';

-- 3.2 创建事实表
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_id INT PRIMARY KEY AUTO_INCREMENT,
    time_id INT NOT NULL,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
) ENGINE=InnoDB COMMENT='维度建模：销售事实表';

-- 3.3 插入维度建模测试数据
-- 插入时间维度数据
INSERT INTO dim_time (time_id, full_date, year, quarter, month, month_name, day, day_of_week, day_name, is_weekend) VALUES
(20230101, '2023-01-01', 2023, 1, 1, 'January', 1, 0, 'Sunday', TRUE),
(20230102, '2023-01-02', 2023, 1, 1, 'January', 2, 1, 'Monday', FALSE),
(20230103, '2023-01-03', 2023, 1, 1, 'January', 3, 2, 'Tuesday', FALSE);

-- 插入产品维度数据
INSERT INTO dim_product (product_id, product_name, category, brand, price, supplier) VALUES
(1, 'iPhone 14 Pro', 'Electronics', 'Apple', 999.00, 'Apple Inc.'),
(2, 'Dell XPS 13', 'Electronics', 'Dell', 999.99, 'Dell Inc.'),
(3, 'Nike Air Max', 'Clothing', 'Nike', 150.00, 'Nike Inc.');

-- 插入客户维度数据
INSERT INTO dim_customer (customer_id, customer_name, email, phone, city, state, country, membership_level) VALUES
(1, 'John Doe', 'john@example.com', '123-456-7890', 'New York', 'NY', 'USA', 'Premium'),
(2, 'Jane Smith', 'jane@example.com', '987-654-3210', 'Los Angeles', 'CA', 'USA', 'Standard');

-- 插入销售事实数据
INSERT INTO fact_sales (time_id, product_id, customer_id, quantity, unit_price, total_amount, discount_amount) VALUES
(20230101, 1, 1, 1, 999.00, 999.00, 0),
(20230101, 2, 1, 1, 999.99, 999.99, 0),
(20230102, 3, 2, 1, 150.00, 150.00, 15.00);  -- 10% discount

-- 3.4 维度建模查询示例 - 销售分析
SELECT 
    dt.month_name AS month,
    dp.category AS product_category,
    COUNT(fs.sales_id) AS total_orders,
    SUM(fs.quantity) AS total_quantity,
    SUM(fs.total_amount) AS total_sales,
    AVG(fs.total_amount) AS avg_order_value
FROM fact_sales fs
JOIN dim_time dt ON fs.time_id = dt.time_id
JOIN dim_product dp ON fs.product_id = dp.product_id
GROUP BY dt.month_name, dp.category
ORDER BY dt.month_name, dp.category;

-- =============================================
-- 4. Data Vault实现 - 企业数据仓库
-- =============================================

-- 4.1 创建Hub表
CREATE TABLE IF NOT EXISTS hub_customer (
    customer_hk VARCHAR(32) PRIMARY KEY COMMENT '客户哈希键',
    customer_id_src INT NOT NULL COMMENT '源系统客户ID',
    load_date DATETIME NOT NULL COMMENT '加载日期',
    record_source VARCHAR(50) NOT NULL COMMENT '数据来源'
) ENGINE=InnoDB COMMENT='Data Vault：客户中心表';

CREATE TABLE IF NOT EXISTS hub_product (
    product_hk VARCHAR(32) PRIMARY KEY COMMENT '产品哈希键',
    product_id_src INT NOT NULL COMMENT '源系统产品ID',
    load_date DATETIME NOT NULL COMMENT '加载日期',
    record_source VARCHAR(50) NOT NULL COMMENT '数据来源'
) ENGINE=InnoDB COMMENT='Data Vault：产品中心表';

CREATE TABLE IF NOT EXISTS hub_order (
    order_hk VARCHAR(32) PRIMARY KEY COMMENT '订单哈希键',
    order_id_src INT NOT NULL COMMENT '源系统订单ID',
    load_date DATETIME NOT NULL COMMENT '加载日期',
    record_source VARCHAR(50) NOT NULL COMMENT '数据来源'
) ENGINE=InnoDB COMMENT='Data Vault：订单中心表';

-- 4.2 创建Link表
CREATE TABLE IF NOT EXISTS link_sales (
    sales_lk VARCHAR(32) PRIMARY KEY COMMENT '销售链接哈希键',
    customer_hk VARCHAR(32) NOT NULL COMMENT '客户哈希键',
    product_hk VARCHAR(32) NOT NULL COMMENT '产品哈希键',
    order_hk VARCHAR(32) NOT NULL COMMENT '订单哈希键',
    load_date DATETIME NOT NULL COMMENT '加载日期',
    record_source VARCHAR(50) NOT NULL COMMENT '数据来源',
    FOREIGN KEY (customer_hk) REFERENCES hub_customer(customer_hk),
    FOREIGN KEY (product_hk) REFERENCES hub_product(product_hk),
    FOREIGN KEY (order_hk) REFERENCES hub_order(order_hk)
) ENGINE=InnoDB COMMENT='Data Vault：销售链接表';

-- 4.3 创建Satellite表
CREATE TABLE IF NOT EXISTS sat_customer_info (
    customer_hk VARCHAR(32) NOT NULL COMMENT '客户哈希键',
    load_date DATETIME NOT NULL COMMENT '加载日期',
    customer_name VARCHAR(100) NOT NULL COMMENT '客户姓名',
    email VARCHAR(100) NOT NULL COMMENT '电子邮箱',
    phone VARCHAR(20) COMMENT '电话号码',
    address TEXT COMMENT '地址',
    membership_level VARCHAR(20) DEFAULT 'Standard' COMMENT '会员等级',
    PRIMARY KEY (customer_hk, load_date),
    FOREIGN KEY (customer_hk) REFERENCES hub_customer(customer_hk)
) ENGINE=InnoDB COMMENT='Data Vault：客户信息卫星表';

CREATE TABLE IF NOT EXISTS sat_product_info (
    product_hk VARCHAR(32) NOT NULL COMMENT '产品哈希键',
    load_date DATETIME NOT NULL COMMENT '加载日期',
    product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
    category VARCHAR(50) COMMENT '产品类别',
    price DECIMAL(10, 2) NOT NULL COMMENT '产品价格',
    description TEXT COMMENT '产品描述',
    stock INT DEFAULT 0 COMMENT '库存数量',
    PRIMARY KEY (product_hk, load_date),
    FOREIGN KEY (product_hk) REFERENCES hub_product(product_hk)
) ENGINE=InnoDB COMMENT='Data Vault：产品信息卫星表';

CREATE TABLE IF NOT EXISTS sat_order_info (
    order_hk VARCHAR(32) NOT NULL COMMENT '订单哈希键',
    load_date DATETIME NOT NULL COMMENT '加载日期',
    order_date DATETIME NOT NULL COMMENT '订单日期',
    total_amount DECIMAL(10, 2) NOT NULL COMMENT '总金额',
    status VARCHAR(20) DEFAULT 'Pending' COMMENT '订单状态',
    PRIMARY KEY (order_hk, load_date),
    FOREIGN KEY (order_hk) REFERENCES hub_order(order_hk)
) ENGINE=InnoDB COMMENT='Data Vault：订单信息卫星表';

CREATE TABLE IF NOT EXISTS sat_sales_info (
    sales_lk VARCHAR(32) NOT NULL COMMENT '销售链接哈希键',
    load_date DATETIME NOT NULL COMMENT '加载日期',
    quantity INT NOT NULL COMMENT '销售数量',
    unit_price DECIMAL(10, 2) NOT NULL COMMENT '单价',
    discount DECIMAL(10, 2) DEFAULT 0 COMMENT '折扣金额',
    PRIMARY KEY (sales_lk, load_date),
    FOREIGN KEY (sales_lk) REFERENCES link_sales(sales_lk)
) ENGINE=InnoDB COMMENT='Data Vault：销售信息卫星表';

-- 4.4 插入Data Vault测试数据
-- 计算哈希值（实际应用中应使用MD5或SHA等哈希函数）
-- 这里为了简化，使用简单的字符串拼接
INSERT INTO hub_customer (customer_hk, customer_id_src, load_date, record_source) VALUES
('CUST_HK_1', 1, NOW(), 'ecommerce_system'),
('CUST_HK_2', 2, NOW(), 'ecommerce_system');

INSERT INTO hub_product (product_hk, product_id_src, load_date, record_source) VALUES
('PROD_HK_1', 1, NOW(), 'ecommerce_system'),
('PROD_HK_2', 2, NOW(), 'ecommerce_system'),
('PROD_HK_3', 3, NOW(), 'ecommerce_system');

INSERT INTO hub_order (order_hk, order_id_src, load_date, record_source) VALUES
('ORDER_HK_1', 1, NOW(), 'ecommerce_system'),
('ORDER_HK_2', 2, NOW(), 'ecommerce_system');

INSERT INTO link_sales (sales_lk, customer_hk, product_hk, order_hk, load_date, record_source) VALUES
('SALES_LK_1', 'CUST_HK_1', 'PROD_HK_1', 'ORDER_HK_1', NOW(), 'ecommerce_system'),
('SALES_LK_2', 'CUST_HK_1', 'PROD_HK_2', 'ORDER_HK_1', NOW(), 'ecommerce_system'),
('SALES_LK_3', 'CUST_HK_2', 'PROD_HK_3', 'ORDER_HK_2', NOW(), 'ecommerce_system');

INSERT INTO sat_customer_info (customer_hk, load_date, customer_name, email, phone, address, membership_level) VALUES
('CUST_HK_1', NOW(), 'John Doe', 'john@example.com', '123-456-7890', '123 Main St, NY', 'Premium'),
('CUST_HK_2', NOW(), 'Jane Smith', 'jane@example.com', '987-654-3210', '456 Oak Ave, CA', 'Standard');

INSERT INTO sat_product_info (product_hk, load_date, product_name, category, price, description, stock) VALUES
('PROD_HK_1', NOW(), 'iPhone 14 Pro', 'Electronics', 999.00, '6.1-inch display', 50),
('PROD_HK_2', NOW(), 'Dell XPS 13', 'Electronics', 999.99, '13.3-inch Ultrabook', 30),
('PROD_HK_3', NOW(), 'Nike Air Max', 'Clothing', 150.00, 'Men\'s sneakers', 100);

INSERT INTO sat_order_info (order_hk, load_date, order_date, total_amount, status) VALUES
('ORDER_HK_1', NOW(), '2023-01-01 10:30:00', 1998.99, 'Completed'),
('ORDER_HK_2', NOW(), '2023-01-02 14:45:00', 150.00, 'Pending');

INSERT INTO sat_sales_info (sales_lk, load_date, quantity, unit_price, discount) VALUES
('SALES_LK_1', NOW(), 1, 999.00, 0),
('SALES_LK_2', NOW(), 1, 999.99, 0),
('SALES_LK_3', NOW(), 1, 150.00, 15.00);

-- 4.5 Data Vault查询示例 - 获取客户的所有订单
SELECT 
    c.customer_name,
    c.email,
    o.order_date,
    o.total_amount,
    o.status,
    p.product_name,
    s.quantity,
    s.unit_price,
    (s.quantity * s.unit_price - s.discount) AS subtotal
FROM hub_customer hc
JOIN sat_customer_info c ON hc.customer_hk = c.customer_hk AND c.load_date = (
    SELECT MAX(load_date) FROM sat_customer_info WHERE customer_hk = hc.customer_hk
)
JOIN link_sales ls ON hc.customer_hk = ls.customer_hk
JOIN hub_order ho ON ls.order_hk = ho.order_hk
JOIN sat_order_info o ON ho.order_hk = o.order_hk AND o.load_date = (
    SELECT MAX(load_date) FROM sat_order_info WHERE order_hk = ho.order_hk
)
JOIN hub_product hp ON ls.product_hk = hp.product_hk
JOIN sat_product_info p ON hp.product_hk = p.product_hk AND p.load_date = (
    SELECT MAX(load_date) FROM sat_product_info WHERE product_hk = hp.product_hk
)
JOIN sat_sales_info s ON ls.sales_lk = s.sales_lk AND s.load_date = (
    SELECT MAX(load_date) FROM sat_sales_info WHERE sales_lk = ls.sales_lk
)
WHERE c.customer_name = 'John Doe';

-- =============================================
-- 5. 模型转换示例：ER模型到维度模型
-- =============================================

-- 创建一个视图，将ER模型转换为维度模型的形式
CREATE VIEW vw_sales_dimension AS
SELECT 
    DATE_FORMAT(o.order_date, '%Y%m%d') AS time_id,
    p.product_id,
    u.user_id AS customer_id,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS total_amount,
    0 AS discount_amount
FROM er_order o
JOIN er_user u ON o.user_id = u.user_id
JOIN er_order_item oi ON o.order_id = oi.order_id
JOIN er_product p ON oi.product_id = p.product_id;

-- 查询转换后的维度模型数据
SELECT * FROM vw_sales_dimension;

-- =============================================
-- 6. 规范化与反规范化示例
-- =============================================

-- 6.1 规范化表结构（第三范式）
CREATE TABLE IF NOT EXISTS normalized_customer (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    city_id INT NOT NULL
) ENGINE=InnoDB COMMENT='规范化：客户表';

CREATE TABLE IF NOT EXISTS normalized_city (
    city_id INT PRIMARY KEY AUTO_INCREMENT,
    city_name VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL
) ENGINE=InnoDB COMMENT='规范化：城市表';

-- 6.2 反规范化表结构
CREATE TABLE IF NOT EXISTS denormalized_customer (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    city_name VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL
) ENGINE=InnoDB COMMENT='反规范化：客户表';

-- 插入测试数据
INSERT INTO normalized_city (city_name, country) VALUES
('New York', 'USA'),
('Los Angeles', 'USA'),
('London', 'UK');

INSERT INTO normalized_customer (customer_name, email, city_id) VALUES
('John Doe', 'john@example.com', 1),
('Jane Smith', 'jane@example.com', 2),
('Bob Johnson', 'bob@example.com', 3);

INSERT INTO denormalized_customer (customer_name, email, city_name, country) VALUES
('John Doe', 'john@example.com', 'New York', 'USA'),
('Jane Smith', 'jane@example.com', 'Los Angeles', 'USA'),
('Bob Johnson', 'bob@example.com', 'London', 'UK');

-- 比较查询性能
-- 规范化查询需要连接表
SELECT c.customer_name, c.email, ct.city_name, ct.country
FROM normalized_customer c
JOIN normalized_city ct ON c.city_id = ct.city_id;

-- 反规范化查询直接从一个表获取所有数据
SELECT customer_name, email, city_name, country
FROM denormalized_customer;

-- =============================================
-- 7. 数据模型验证与测试
-- =============================================

-- 验证ER模型的外键约束
-- 这条语句会失败，因为user_id=999不存在
-- INSERT INTO er_order (user_id, total_amount, status) VALUES (999, 100.00, 'Pending');

-- 验证CHECK约束
-- 这条语句会失败，因为quantity必须大于0
-- INSERT INTO er_order_item (order_id, product_id, quantity, unit_price) VALUES (1, 1, 0, 999.00);

-- 验证唯一约束
-- 这条语句会失败，因为username必须唯一
-- INSERT INTO er_user (username, email, password_hash) VALUES ('john_doe', 'john_new@example.com', 'new_password');

-- =============================================
-- 8. 清理数据（可选）
-- =============================================

-- 如果需要重新开始，可以取消注释以下语句
-- DROP DATABASE IF EXISTS ecommerce_modeling;