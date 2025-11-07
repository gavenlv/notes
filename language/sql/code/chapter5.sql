-- 第5章：SQL数据操作示例代码

-- 创建示例数据库
CREATE DATABASE IF NOT EXISTS company_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE company_demo;

-- 删除已存在的表（确保环境干净）
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS employees_archive;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

-- 创建部门表
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    location VARCHAR(100),
    budget DECIMAL(12, 2)
);

-- 创建员工表
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    age INT,
    gender VARCHAR(10),
    department_id INT,
    position VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE,
    email VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 插入部门数据
INSERT INTO departments (name, location, budget) VALUES
('技术部', '北京', 1000000.00),
('市场部', '上海', 800000.00),
('人事部', '广州', 500000.00),
('财务部', '深圳', 600000.00);

-- 5.1 INSERT语句示例

-- 插入完整行数据
INSERT INTO employees (name, age, gender, department_id, position, salary, hire_date, email, phone)
VALUES ('张三', 30, '男', 1, '高级工程师', 15000.00, '2020-01-15', 'zhangsan@example.com', '13800138001');

-- 插入部分列数据
INSERT INTO employees (name, age, gender, department_id, position, salary)
VALUES ('李四', 28, '女', 1, '工程师', 12000.00);

-- 插入多行数据
INSERT INTO employees (name, age, gender, department_id, position, salary, hire_date)
VALUES 
    ('王五', 35, '男', 1, '工程师', 13000.00, '2019-06-10'),
    ('赵六', 25, '女', 1, '初级工程师', 8000.00, '2021-02-28'),
    ('钱七', 32, '男', 2, '市场经理', 18000.00, '2019-11-05');

-- 插入NULL值
INSERT INTO employees (name, age, gender, department_id, position, salary, phone)
VALUES ('孙八', 27, '女', 2, '市场专员', 9000.00, NULL);

-- 插入默认值
INSERT INTO employees (name, age, gender, department_id, position, salary, is_active)
VALUES ('周九', 40, '男', 2, '市场专员', 8500.00, DEFAULT);

-- 插入自动递增值
INSERT INTO employees (name, age, gender, department_id, position, salary)
VALUES ('吴十', 29, '女', 3, '人事经理', 16000.00);

-- 验证插入的数据
SELECT * FROM employees;

-- 创建员工归档表
CREATE TABLE employees_archive (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    position VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE
);

-- 从其他表插入数据
INSERT INTO employees_archive (id, name, position, salary, hire_date)
SELECT id, name, position, salary, hire_date
FROM employees
WHERE hire_date < '2020-01-01';

-- 验证归档数据
SELECT * FROM employees_archive;

-- 5.2 UPDATE语句示例

-- 更新单个员工的薪资
UPDATE employees
SET salary = 16000.00
WHERE name = '李四';

-- 同时更新多个列
UPDATE employees
SET salary = 14000.00, position = '高级工程师'
WHERE name = '赵六';

-- 给技术部（部门ID=1）的员工加薪10%
UPDATE employees
SET salary = salary * 1.1
WHERE department_id = 1;

-- 更新30岁以上的工程师为高级工程师
UPDATE employees
SET position = '高级工程师'
WHERE age >= 30 AND position = '工程师';

-- 根据职位给员工加薪
UPDATE employees
SET salary = CASE
    WHEN position LIKE '%经理%' THEN salary * 1.15
    WHEN position LIKE '%工程师%' THEN salary * 1.1
    ELSE salary * 1.05
END;

-- 更新邮箱格式
UPDATE employees
SET email = CONCAT(LOWER(name), '@company.com')
WHERE email IS NULL;

-- 验证更新结果
SELECT name, position, salary, department_id, email FROM employees;

-- 使用子查询更新数据
UPDATE employees
SET salary = (
    SELECT AVG(salary) * 1.2
    FROM employees
    WHERE department_id = 1
)
WHERE name = '张三';

-- 验证子查询更新结果
SELECT name, position, salary FROM employees WHERE name = '张三';

-- 5.3 DELETE语句示例

-- 创建一个临时表用于演示
CREATE TABLE temp_employees AS SELECT * FROM employees;

-- 查看临时表数据
SELECT * FROM temp_employees;

-- 删除单个员工
DELETE FROM temp_employees
WHERE name = '孙八';

-- 删除特定部门的员工
DELETE FROM temp_employees
WHERE department_id = 3;

-- 删除薪资低于平均薪资的员工
DELETE FROM temp_employees
WHERE salary < (SELECT AVG(salary) FROM temp_employees);

-- 验证删除结果
SELECT * FROM temp_employees;

-- 清空临时表
TRUNCATE TABLE temp_employees;

-- 验证清空结果
SELECT * FROM temp_employees;

-- 删除没有部门的员工（示例，实际不会有这样的员工）
DELETE FROM employees
WHERE department_id NOT IN (SELECT id FROM departments);

-- 5.4 事务处理示例

-- 创建一个测试表
CREATE TABLE account (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);

-- 插入测试数据
INSERT INTO account (name, balance) VALUES
('张三', 1000.00),
('李四', 2000.00),
('王五', 1500.00);

-- 查看初始状态
SELECT * FROM account;

-- 开始事务
START TRANSACTION;

-- 张三向李四转账500
UPDATE account SET balance = balance - 500 WHERE name = '张三';
UPDATE account SET balance = balance + 500 WHERE name = '李四';

-- 查看事务中的状态
SELECT * FROM account;

-- 提交事务
COMMIT;

-- 查看最终状态
SELECT * FROM account;

-- 开始另一个事务
START TRANSACTION;

-- 王五向张三转账200，但中间出错
UPDATE account SET balance = balance - 200 WHERE name = '王五';
-- 假设这里出现错误
UPDATE account SET balance = balance + 200 WHERE name = '张三';

-- 回滚事务
ROLLBACK;

-- 查看回滚后的状态
SELECT * FROM account;

-- 使用保存点
START TRANSACTION;

-- 张三向李四转账300
UPDATE account SET balance = balance - 300 WHERE name = '张三';
UPDATE account SET balance = balance + 300 WHERE name = '李四';

-- 设置保存点
SAVEPOINT point1;

-- 王五向张三转账100
UPDATE account SET balance = balance - 100 WHERE name = '王五';
UPDATE account SET balance = balance + 100 WHERE name = '张三';

-- 查看当前状态
SELECT * FROM account;

-- 回滚到保存点
ROLLBACK TO SAVEPOINT point1;

-- 查看回滚后的状态
SELECT * FROM account;

-- 提交事务
COMMIT;

-- 查看最终状态
SELECT * FROM account;

-- 5.5 数据完整性示例

-- 创建分类表
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- 创建带约束的产品表
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) CHECK (price > 0),
    stock INT CHECK (stock >= 0),
    category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 插入分类数据
INSERT INTO categories (name) VALUES
('电子产品'),
('服装'),
('食品');

-- 尝试插入违反NOT NULL约束的数据（会失败）
-- INSERT INTO products (price, stock, category_id) VALUES (100.00, 10, 1);

-- 尝试插入违反CHECK约束的数据（会失败）
-- INSERT INTO products (name, price, stock, category_id) VALUES ('测试产品', -10.00, 10, 1);

-- 插入有效数据
INSERT INTO products (name, price, stock, category_id) VALUES ('手机', 2999.00, 50, 1);
INSERT INTO products (name, price, stock, category_id) VALUES ('T恤', 99.00, 100, 2);
INSERT INTO products (name, price, stock, category_id) VALUES ('笔记本电脑', 5999.00, 30, 1);

-- 验证数据
SELECT * FROM products;

-- 使用事务确保转账操作的完整性
START TRANSACTION;

-- 扣除转账方金额
UPDATE account SET balance = balance - 500 WHERE name = '张三';

-- 确保转账方余额足够
-- 注意：MySQL不直接支持IF语句在事务中，这里仅作示例
-- 实际应用中，可以在应用层检查或使用存储过程
SELECT balance FROM account WHERE name = '张三';

-- 如果余额足够，增加收款方金额
UPDATE account SET balance = balance + 500 WHERE name = '李四';

-- 提交事务
COMMIT;

-- 查看最终状态
SELECT * FROM account;

-- 尝试插入违反UNIQUE约束的数据（会失败）
-- INSERT INTO categories (name) VALUES ('电子产品');

-- 尝试插入违反FOREIGN KEY约束的数据（会失败）
-- INSERT INTO products (name, price, stock, category_id) VALUES ('测试产品', 100.00, 10, 99);

-- 验证数据完整性
SELECT * FROM categories;
SELECT * FROM products;