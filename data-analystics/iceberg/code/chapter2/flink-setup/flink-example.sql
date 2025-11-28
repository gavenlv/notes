-- Flink SQL 示例：Iceberg 表操作

-- 创建 Iceberg Catalog
CREATE CATALOG iceberg WITH (
  'type'='iceberg',
  'catalog-type'='hadoop',
  'warehouse'='file:///tmp/iceberg/warehouse'
);

-- 使用 Iceberg Catalog
USE CATALOG iceberg;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS iceberg_db;

-- 使用数据库
USE iceberg_db;

-- 创建 Iceberg 表
CREATE TABLE IF NOT EXISTS users (
  id BIGINT COMMENT '用户ID',
  name STRING COMMENT '用户名',
  age INT COMMENT '年龄',
  email STRING COMMENT '邮箱'
) WITH (
  'format-version'='2',
  'write.distribution-mode'='hash',
  'write.parquet.compression-codec'='zstd'
);

-- 插入示例数据
INSERT INTO users VALUES
  (1, 'Alice', 25, 'alice@example.com'),
  (2, 'Bob', 30, 'bob@example.com'),
  (3, 'Charlie', 35, 'charlie@example.com'),
  (4, 'David', 28, 'david@example.com'),
  (5, 'Eve', 22, 'eve@example.com');

-- 查询所有数据
SELECT * FROM users;

-- 条件查询
SELECT * FROM users WHERE age > 25;

-- 更新数据
UPDATE users SET email = 'alice.new@example.com' WHERE name = 'Alice';

-- 删除数据
DELETE FROM users WHERE age < 25;

-- 创建分区表
CREATE TABLE IF NOT EXISTS partitioned_users (
  id BIGINT,
  name STRING,
  age INT,
  email STRING,
  registration_date DATE
) PARTITIONED BY (registration_date) WITH (
  'format-version'='2'
);

-- 插入带分区的数据
INSERT INTO partitioned_users VALUES
  (1, 'Alice', 25, 'alice@example.com', DATE '2024-01-15'),
  (2, 'Bob', 30, 'bob@example.com', DATE '2024-01-16'),
  (3, 'Charlie', 35, 'charlie@example.com', DATE '2024-01-17');

-- 查询分区表
SELECT * FROM partitioned_users;

-- 查看表属性
SHOW TABLES;
DESCRIBE users;