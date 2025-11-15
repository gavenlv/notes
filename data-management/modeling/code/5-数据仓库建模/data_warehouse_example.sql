-- 电商销售数据仓库示例（星型模型）

-- 创建数据库
CREATE DATABASE ecommerce_data_warehouse;

-- 使用数据库
USE ecommerce_data_warehouse;

-- 创建日期维度表
CREATE TABLE date_dim (
    date_id INT PRIMARY KEY,
    full_date DATE,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR(20),
    day INT,
    day_name VARCHAR(20),
    week INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    holiday_name VARCHAR(50)
);

-- 创建产品维度表
CREATE TABLE product_dim (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    brand VARCHAR(50),
    price DECIMAL(10, 2),
    color VARCHAR(20),
    size VARCHAR(10),
    weight DECIMAL(8, 2),
    supplier VARCHAR(100),
    status VARCHAR(20)
);

-- 创建客户维度表
CREATE TABLE customer_dim (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    gender VARCHAR(10),
    age INT,
    birth_date DATE,
    registration_date DATE,
    customer_segment VARCHAR(50),
    country VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    address VARCHAR(200)
);

-- 创建商店维度表
CREATE TABLE store_dim (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(100),
    country VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    address VARCHAR(200),
    manager_name VARCHAR(100),
    opening_date DATE,
    square_feet INT
);

-- 创建销售事实表
CREATE TABLE sales_fact (
    order_id INT,
    date_id INT,
    product_id INT,
    customer_id INT,
    store_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    total_amount DECIMAL(10, 2),
    discount_amount DECIMAL(10, 2),
    net_amount DECIMAL(10, 2),
    tax_amount DECIMAL(10, 2),
    payment_method VARCHAR(20),
    order_status VARCHAR(20),
    PRIMARY KEY (order_id, date_id, product_id, customer_id, store_id),
    FOREIGN KEY (date_id) REFERENCES date_dim(date_id),
    FOREIGN KEY (product_id) REFERENCES product_dim(product_id),
    FOREIGN KEY (customer_id) REFERENCES customer_dim(customer_id),
    FOREIGN KEY (store_id) REFERENCES store_dim(store_id)
);

-- 创建索引以提高查询性能
CREATE INDEX idx_sales_date ON sales_fact(date_id);
CREATE INDEX idx_sales_product ON sales_fact(product_id);
CREATE INDEX idx_sales_customer ON sales_fact(customer_id);
CREATE INDEX idx_sales_store ON sales_fact(store_id);
CREATE INDEX idx_product_category ON product_dim(category);
CREATE INDEX idx_customer_country ON customer_dim(country);

-- 插入日期维度数据（2023年1月数据）
INSERT INTO date_dim (date_id, full_date, year, quarter, month, month_name, day, day_name, week, is_weekend, is_holiday, holiday_name)
VALUES
(20230101, '2023-01-01', 2023, 1, 1, 'January', 1, 'Sunday', 1, TRUE, TRUE, 'New Year'),
(20230102, '2023-01-02', 2023, 1, 1, 'January', 2, 'Monday', 1, FALSE, FALSE, NULL),
(20230103, '2023-01-03', 2023, 1, 1, 'January', 3, 'Tuesday', 1, FALSE, FALSE, NULL),
(20230104, '2023-01-04', 2023, 1, 1, 'January', 4, 'Wednesday', 1, FALSE, FALSE, NULL),
(20230105, '2023-01-05', 2023, 1, 1, 'January', 5, 'Thursday', 1, FALSE, FALSE, NULL),
(20230106, '2023-01-06', 2023, 1, 1, 'January', 6, 'Friday', 1, FALSE, FALSE, NULL),
(20230107, '2023-01-07', 2023, 1, 1, 'January', 7, 'Saturday', 2, TRUE, FALSE, NULL),
(20230108, '2023-01-08', 2023, 1, 1, 'January', 8, 'Sunday', 2, TRUE, FALSE, NULL),
(20230109, '2023-01-09', 2023, 1, 1, 'January', 9, 'Monday', 2, FALSE, FALSE, NULL),
(20230110, '2023-01-10', 2023, 1, 1, 'January', 10, 'Tuesday', 2, FALSE, FALSE, NULL);

-- 插入产品维度数据
INSERT INTO product_dim (product_id, product_name, category, subcategory, brand, price, color, size, weight, supplier, status)
VALUES
(1, 'Dell XPS 13', 'Electronics', 'Laptops', 'Dell', 999.99, 'Silver', '13.4-inch', 2.7, 'Dell Inc.', 'Active'),
(2, 'MacBook Air M2', 'Electronics', 'Laptops', 'Apple', 1199.99, 'Space Gray', '13-inch', 2.7, 'Apple Inc.', 'Active'),
(3, 'iPhone 14', 'Electronics', 'Smartphones', 'Apple', 799.99, 'Midnight', '6.1-inch', 0.4, 'Apple Inc.', 'Active'),
(4, 'Samsung Galaxy S23', 'Electronics', 'Smartphones', 'Samsung', 799.99, 'Phantom Black', '6.1-inch', 0.4, 'Samsung Electronics', 'Active'),
(5, 'Sony WH-1000XM5', 'Electronics', 'Headphones', 'Sony', 399.99, 'Black', NULL, 0.3, 'Sony Corporation', 'Active'),
(6, 'Nike Air Max 270', 'Clothing', 'Shoes', 'Nike', 150.00, 'White/Black', '10', 1.2, 'Nike Inc.', 'Active'),
(7, 'Adidas Ultraboost 22', 'Clothing', 'Shoes', 'Adidas', 180.00, 'Black/Red', '9', 1.1, 'Adidas AG', 'Active'),
(8, 'Levi's 501 Original Fit Jeans', 'Clothing', 'Pants', 'Levi Strauss', 69.99, 'Blue', '32x32', 1.5, 'Levi Strauss & Co.', 'Active');

-- 插入客户维度数据
INSERT INTO customer_dim (customer_id, first_name, last_name, full_name, email, phone, gender, age, birth_date, registration_date, customer_segment, country, city, state, zip_code, address)
VALUES
(1, 'John', 'Doe', 'John Doe', 'john.doe@example.com', '123-456-7890', 'Male', 30, '1993-05-15', '2022-01-10', 'Premium', 'USA', 'New York', 'NY', '10001', '123 Main St'),
(2, 'Jane', 'Smith', 'Jane Smith', 'jane.smith@example.com', '987-654-3210', 'Female', 28, '1995-08-22', '2022-03-15', 'Standard', 'USA', 'Los Angeles', 'CA', '90001', '456 Oak Ave'),
(3, 'Bob', 'Johnson', 'Bob Johnson', 'bob.johnson@example.com', '555-123-4567', 'Male', 35, '1988-12-05', '2021-11-20', 'Premium', 'Canada', 'Toronto', 'ON', 'M5V 2T6', '789 Maple Rd'),
(4, 'Alice', 'Williams', 'Alice Williams', 'alice.williams@example.com', '555-987-6543', 'Female', 25, '1998-03-18', '2023-01-05', 'New', 'UK', 'London', NULL, 'SW1A 1AA', '10 Downing St'),
(5, 'Charlie', 'Brown', 'Charlie Brown', 'charlie.brown@example.com', '555-456-7890', 'Male', 32, '1991-07-30', '2022-05-25', 'Standard', 'USA', 'Chicago', 'IL', '60601', '200 W Madison St');

-- 插入商店维度数据
INSERT INTO store_dim (store_id, store_name, country, city, state, zip_code, address, manager_name, opening_date, square_feet)
VALUES
(1, 'New York Store', 'USA', 'New York', 'NY', '10001', '123 Main St', 'Michael Johnson', '2020-01-15', 10000),
(2, 'Los Angeles Store', 'USA', 'Los Angeles', 'CA', '90001', '456 Oak Ave', 'Sarah Williams', '2020-03-20', 8000),
(3, 'Chicago Store', 'USA', 'Chicago', 'IL', '60601', '789 Maple Rd', 'David Brown', '2020-05-10', 12000),
(4, 'Toronto Store', 'Canada', 'Toronto', 'ON', 'M5V 2T6', '10 King St W', 'Jennifer Lee', '2021-02-15', 9000),
(5, 'London Store', 'UK', 'London', NULL, 'SW1A 1AA', '1 Regent St', 'Robert Smith', '2021-06-30', 7000);

-- 插入销售事实数据
INSERT INTO sales_fact (order_id, date_id, product_id, customer_id, store_id, quantity, unit_price, total_amount, discount_amount, net_amount, tax_amount, payment_method, order_status)
VALUES
(1, 20230101, 1, 1, 1, 1, 999.99, 999.99, 100.00, 899.99, 89.99, 'Credit Card', 'Completed'),
(1, 20230101, 5, 1, 1, 1, 399.99, 399.99, 40.00, 359.99, 35.99, 'Credit Card', 'Completed'),
(2, 20230102, 2, 2, 2, 1, 1199.99, 1199.99, 120.00, 1079.99, 107.99, 'PayPal', 'Completed'),
(3, 20230103, 3, 3, 4, 1, 799.99, 799.99, 80.00, 719.99, 71.99, 'Credit Card', 'Completed'),
(4, 20230104, 4, 4, 5, 1, 799.99, 799.99, 0.00, 799.99, 79.99, 'Debit Card', 'Completed'),
(5, 20230105, 6, 5, 3, 2, 150.00, 300.00, 30.00, 270.00, 27.00, 'Credit Card', 'Completed'),
(6, 20230106, 7, 1, 2, 1, 180.00, 180.00, 0.00, 180.00, 18.00, 'PayPal', 'Completed'),
(7, 20230107, 8, 2, 1, 1, 69.99, 69.99, 7.00, 62.99, 6.29, 'Credit Card', 'Completed'),
(8, 20230108, 1, 3, 3, 1, 999.99, 999.99, 100.00, 899.99, 89.99, 'Credit Card', 'Completed'),
(9, 20230109, 2, 4, 4, 1, 1199.99, 1199.99, 120.00, 1079.99, 107.99, 'Debit Card', 'Completed'),
(10, 20230110, 3, 5, 5, 1, 799.99, 799.99, 80.00, 719.99, 71.99, 'Credit Card', 'Completed');

-- 查询示例1：每日销售额统计
SELECT 
    dd.full_date,
    SUM(sf.total_amount) AS total_sales,
    SUM(sf.discount_amount) AS total_discount,
    SUM(sf.net_amount) AS net_sales,
    SUM(sf.quantity) AS total_quantity
FROM 
    sales_fact sf
JOIN 
    date_dim dd ON sf.date_id = dd.date_id
GROUP BY 
    dd.full_date
ORDER BY 
    dd.full_date;

-- 查询示例2：按产品类别统计销售额
SELECT 
    pd.category,
    pd.subcategory,
    SUM(sf.total_amount) AS total_sales,
    SUM(sf.quantity) AS total_quantity
FROM 
    sales_fact sf
JOIN 
    product_dim pd ON sf.product_id = pd.product_id
GROUP BY 
    pd.category, pd.subcategory
ORDER BY 
    pd.category, pd.subcategory;

-- 查询示例3：按客户所在国家统计销售额
SELECT 
    cd.country,
    SUM(sf.total_amount) AS total_sales,
    COUNT(DISTINCT sf.customer_id) AS unique_customers,
    SUM(sf.quantity) AS total_quantity
FROM 
    sales_fact sf
JOIN 
    customer_dim cd ON sf.customer_id = cd.customer_id
GROUP BY 
    cd.country
ORDER BY 
    total_sales DESC;

-- 查询示例4：按商店统计销售额和利润
SELECT 
    sd.store_name,
    sd.city,
    sd.country,
    SUM(sf.total_amount) AS total_sales,
    SUM(sf.discount_amount) AS total_discount,
    SUM(sf.net_amount) AS net_sales,
    SUM(sf.tax_amount) AS total_tax
FROM 
    sales_fact sf
JOIN 
    store_dim sd ON sf.store_id = sd.store_id
GROUP BY 
    sd.store_name, sd.city, sd.country
ORDER BY 
    net_sales DESC;

-- 查询示例5：按月份统计电子产品销售额
SELECT 
    dd.month_name,
    dd.year,
    SUM(sf.total_amount) AS total_sales,
    SUM(sf.quantity) AS total_quantity
FROM 
    sales_fact sf
JOIN 
    date_dim dd ON sf.date_id = dd.date_id
JOIN 
    product_dim pd ON sf.product_id = pd.product_id
WHERE 
    pd.category = 'Electronics'
GROUP BY 
    dd.month_name, dd.year
ORDER BY 
    dd.year, dd.month;

-- 查询示例6：客户购买行为分析
SELECT 
    cd.customer_segment,
    COUNT(DISTINCT sf.order_id) AS total_orders,
    SUM(sf.total_amount) AS total_spent,
    AVG(sf.total_amount) AS avg_order_value,
    SUM(sf.quantity) AS total_items_purchased
FROM 
    sales_fact sf
JOIN 
    customer_dim cd ON sf.customer_id = cd.customer_id
GROUP BY 
    cd.customer_segment
ORDER BY 
    total_spent DESC;

-- 查询示例7：产品销售排名
SELECT 
    pd.product_name,
    pd.brand,
    SUM(sf.quantity) AS total_sold,
    SUM(sf.net_amount) AS total_revenue,
    RANK() OVER (ORDER BY SUM(sf.net_amount) DESC) AS revenue_rank,
    RANK() OVER (ORDER BY SUM(sf.quantity) DESC) AS quantity_rank
FROM 
    sales_fact sf
JOIN 
    product_dim pd ON sf.product_id = pd.product_id
GROUP BY 
    pd.product_name, pd.brand
ORDER BY 
    total_revenue DESC;

-- 查询示例8：周末与工作日销售对比
SELECT 
    CASE 
        WHEN dd.is_weekend = TRUE THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(DISTINCT sf.order_id) AS total_orders,
    SUM(sf.total_amount) AS total_sales,
    AVG(sf.total_amount) AS avg_order_value
FROM 
    sales_fact sf
JOIN 
    date_dim dd ON sf.date_id = dd.date_id
GROUP BY 
    dd.is_weekend
ORDER BY 
    total_sales DESC;

-- 创建物化视图以提高查询性能（可选）
CREATE MATERIALIZED VIEW monthly_sales_by_category AS
SELECT 
    dd.year,
    dd.month,
    dd.month_name,
    pd.category,
    pd.subcategory,
    SUM(sf.total_amount) AS total_sales,
    SUM(sf.discount_amount) AS total_discount,
    SUM(sf.net_amount) AS net_sales,
    SUM(sf.quantity) AS total_quantity
FROM 
    sales_fact sf
JOIN 
    date_dim dd ON sf.date_id = dd.date_id
JOIN 
    product_dim pd ON sf.product_id = pd.product_id
GROUP BY 
    dd.year, dd.month, dd.month_name, pd.category, pd.subcategory;

-- 查询物化视图
SELECT * FROM monthly_sales_by_category ORDER BY year, month, category;

-- 定期刷新物化视图（可选，根据数据库系统不同实现方式不同）
-- REFRESH MATERIALIZED VIEW monthly_sales_by_category;

-- 创建分区表（可选，根据数据库系统不同实现方式不同）
-- 以下示例为PostgreSQL语法
-- CREATE TABLE sales_fact_partitioned (
--     order_id INT,
--     date_id INT,
--     product_id INT,
--     customer_id INT,
--     store_id INT,
--     quantity INT,
--     unit_price DECIMAL(10, 2),
--     total_amount DECIMAL(10, 2),
--     discount_amount DECIMAL(10, 2),
--     net_amount DECIMAL(10, 2),
--     tax_amount DECIMAL(10, 2),
--     payment_method VARCHAR(20),
--     order_status VARCHAR(20),
--     PRIMARY KEY (order_id, date_id, product_id, customer_id, store_id),
--     FOREIGN KEY (date_id) REFERENCES date_dim(date_id),
--     FOREIGN KEY (product_id) REFERENCES product_dim(product_id),
--     FOREIGN KEY (customer_id) REFERENCES customer_dim(customer_id),
--     FOREIGN KEY (store_id) REFERENCES store_dim(store_id)
-- ) PARTITION BY RANGE (date_id);

-- CREATE TABLE sales_fact_202301 PARTITION OF sales_fact_partitioned
--     FOR VALUES FROM (20230101) TO (20230201);

-- 总结：
-- 1. 我们创建了一个电商销售数据仓库的星型模型
-- 2. 包含4个维度表（日期、产品、客户、商店）和1个事实表（销售）
-- 3. 插入了示例数据以演示数据仓库的使用
-- 4. 提供了8个查询示例，展示了如何进行数据分析
-- 5. 介绍了物化视图和分区表等性能优化技术

-- 运行说明：
-- 1. 本代码适用于支持标准SQL的关系型数据库（如PostgreSQL、MySQL、Oracle等）
-- 2. 某些高级特性（如物化视图、分区表）可能需要特定数据库系统支持
-- 3. 可以使用任何SQL客户端工具执行本代码
-- 4. 运行顺序：先创建数据库和表结构，然后插入数据，最后执行查询示例

-- 扩展思考：
-- 1. 如何扩展这个模型以支持更多的业务分析需求？
-- 2. 如何处理缓慢变化维（如产品价格变化、客户地址变化）？
-- 3. 如何实现数据的增量加载和定期更新？
-- 4. 如何优化查询性能以处理更大规模的数据？