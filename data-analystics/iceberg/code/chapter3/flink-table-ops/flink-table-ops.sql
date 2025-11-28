-- Flink SQL 示例：Iceberg 表操作详解

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

-- 1. 创建基础表
CREATE TABLE IF NOT EXISTS users (
  id BIGINT COMMENT '用户ID',
  name STRING COMMENT '用户名',
  age INT COMMENT '年龄',
  email STRING COMMENT '邮箱'
) WITH (
  'format-version'='2',
  'write.distribution-mode'='hash'
);

-- 2. 插入初始数据
INSERT INTO users VALUES
  (1, 'Alice', 25, 'alice@example.com'),
  (2, 'Bob', 30, 'bob@example.com'),
  (3, 'Charlie', 35, 'charlie@example.com'),
  (4, 'David', 28, 'david@example.com'),
  (5, 'Eve', 22, 'eve@example.com');

-- 3. 查询所有数据
SELECT * FROM users;

-- 4. 条件查询
SELECT * FROM users WHERE age > 25;

-- 5. 聚合查询
SELECT age, COUNT(*) as user_count FROM users GROUP BY age ORDER BY age;

-- 6. 更新数据
UPDATE users SET email = 'alice.updated@example.com' WHERE name = 'Alice';

-- 验证更新结果
SELECT * FROM users WHERE name = 'Alice';

-- 7. 删除数据
DELETE FROM users WHERE age < 25;

-- 验证删除结果
SELECT * FROM users;

-- 8. 创建分区表
CREATE TABLE IF NOT EXISTS sales (
  id BIGINT,
  product STRING,
  amount DECIMAL(10,2),
  sale_date DATE
) PARTITIONED BY (sale_date) WITH (
  'format-version'='2'
);

-- 9. 插入分区表数据
INSERT INTO sales VALUES
  (1, 'Product A', 100.50, DATE '2024-01-15'),
  (2, 'Product B', 200.75, DATE '2024-01-16'),
  (3, 'Product A', 150.25, DATE '2024-01-17'),
  (4, 'Product C', 300.00, DATE '2024-01-15');

-- 10. 分区查询
SELECT * FROM sales WHERE sale_date = '2024-01-15';

-- 11. Schema演变 - 添加列
ALTER TABLE users ADD COLUMN phone STRING COMMENT '电话号码';

-- 12. 更新新增列的数据
UPDATE users SET phone = '+1-555-0123' WHERE name = 'Alice';

-- 验证新增列
SELECT * FROM users;

-- 13. 查看表结构
DESCRIBE users;

-- 14. 查看表属性
SHOW TABLES;