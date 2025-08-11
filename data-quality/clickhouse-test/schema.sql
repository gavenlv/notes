-- ClickHouse 测试环境 DDL
-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS data_quality_test;

-- 使用测试数据库
USE data_quality_test;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users
(
    user_id UInt32,
    email String,
    name String,
    age UInt8,
    created_date Date DEFAULT today(),
    updated_date DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_date)
ORDER BY (user_id);

-- 创建客户表
CREATE TABLE IF NOT EXISTS customers
(
    customer_id UInt32,
    company_name String,
    contact_name String,
    email String,
    phone String,
    created_date Date DEFAULT today(),
    updated_date DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_date)
ORDER BY (customer_id);

-- 创建订单表
CREATE TABLE IF NOT EXISTS orders
(
    order_id UInt32,
    customer_id UInt32,
    order_date Date,
    total_amount Decimal(10,2),
    status Enum8('pending' = 1, 'processing' = 2, 'shipped' = 3, 'delivered' = 4, 'cancelled' = 5),
    created_date Date DEFAULT today(),
    updated_date DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_date)
ORDER BY (order_id, customer_id);

-- 创建产品表
CREATE TABLE IF NOT EXISTS products
(
    product_id UInt32,
    product_name String,
    category String,
    price Decimal(10,2),
    stock_quantity Int32,
    weight Decimal(10,2) NULL,
    created_date Date DEFAULT today(),
    updated_date DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_date)
ORDER BY (product_id);

-- 创建订单明细表
CREATE TABLE IF NOT EXISTS order_items
(
    order_item_id UInt32,
    order_id UInt32,
    product_id UInt32,
    quantity UInt16,
    unit_price Decimal(10,2),
    created_date Date DEFAULT today()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_date)
ORDER BY (order_item_id, order_id);