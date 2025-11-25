-- 创建表示例
-- 连接方式: mysql -h 127.0.0.1 -P 9030 -uroot demo

USE demo;

-- 1. 创建Duplicate模型表（明细模型）
-- 适用于需要保留所有明细数据的场景
CREATE TABLE IF NOT EXISTS users_duplicate (
    user_id BIGINT COMMENT '用户ID',
    user_name VARCHAR(50) COMMENT '用户名',
    age INT COMMENT '年龄',
    city VARCHAR(20) COMMENT '城市',
    register_date DATE COMMENT '注册日期',
    last_login_time DATETIME COMMENT '最后登录时间'
) DUPLICATE KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 10
PROPERTIES (
    "replication_num" = "1"
);

-- 2. 创建Aggregate模型表（聚合模型）
-- 适用于需要预聚合数据的场景
CREATE TABLE IF NOT EXISTS sales_aggregate (
    sale_date DATE COMMENT '销售日期',
    product_id INT COMMENT '产品ID',
    product_name VARCHAR(100) COMMENT '产品名称',
    region VARCHAR(50) COMMENT '地区',
    total_sales BIGINT SUM DEFAULT '0' COMMENT '总销售量',
    total_amount DECIMAL(18,2) SUM DEFAULT '0.00' COMMENT '总销售额',
    max_price DECIMAL(10,2) MAX DEFAULT '0.00' COMMENT '最高价格',
    min_price DECIMAL(10,2) MIN DEFAULT '999999.99' COMMENT '最低价格'
) AGGREGATE KEY(sale_date, product_id, product_name, region)
DISTRIBUTED BY HASH(product_id) BUCKETS 8
PROPERTIES (
    "replication_num" = "1"
);

-- 3. 创建Unique模型表（唯一模型）
-- 适用于需要保证数据唯一性的场景
CREATE TABLE IF NOT EXISTS user_profiles_unique (
    user_id BIGINT COMMENT '用户ID',
    user_name VARCHAR(50) COMMENT '用户名',
    email VARCHAR(100) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    gender TINYINT COMMENT '性别: 0-未知, 1-男, 2-女',
    birthday DATE COMMENT '生日',
    address VARCHAR(200) COMMENT '地址',
    update_time DATETIME COMMENT '更新时间'
) UNIQUE KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 10
PROPERTIES (
    "replication_num" = "1"
);

-- 4. 创建Primary Key模型表（主键模型）
-- 适用于需要频繁更新和删除的场景
CREATE TABLE IF NOT EXISTS user_metrics_pk (
    user_id BIGINT COMMENT '用户ID',
    login_count BIGINT DEFAULT '0' COMMENT '登录次数',
    total_order_amount DECIMAL(18,2) DEFAULT '0.00' COMMENT '总订单金额',
    last_order_time DATETIME COMMENT '最后下单时间',
    last_update_time DATETIME COMMENT '最后更新时间'
) PRIMARY KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 10
PROPERTIES (
    "replication_num" = "1"
);

-- 5. 创建分区表示例
-- 按时间分区，提高查询效率
CREATE TABLE IF NOT EXISTS event_logs (
    event_time DATETIME COMMENT '事件时间',
    event_type VARCHAR(50) COMMENT '事件类型',
    user_id BIGINT COMMENT '用户ID',
    session_id VARCHAR(100) COMMENT '会话ID',
    page_url VARCHAR(500) COMMENT '页面URL',
    referrer_url VARCHAR(500) COMMENT '来源URL',
    user_agent TEXT COMMENT '用户代理',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    country VARCHAR(50) COMMENT '国家',
    city VARCHAR(50) COMMENT '城市'
) DUPLICATE KEY(event_time, event_type, user_id)
PARTITION BY RANGE(event_time) (
    PARTITION p20230101 VALUES [('2023-01-01'), ('2023-01-02')),
    PARTITION p20230102 VALUES [('2023-01-02'), ('2023-01-03')),
    PARTITION p20230103 VALUES [('2023-01-03'), ('2023-01-04'))
)
DISTRIBUTED BY HASH(user_id) BUCKETS 16
PROPERTIES (
    "replication_num" = "1",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.end" = "7",
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "16"
);

-- 显示所有表
SHOW TABLES;

-- 显示表结构
DESC users_duplicate;
DESC sales_aggregate;
DESC user_profiles_unique;
DESC user_metrics_pk;
DESC event_logs;