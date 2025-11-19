-- 第9章：SQL性能优化示例代码

-- 创建示例数据库
CREATE DATABASE IF NOT EXISTS company_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE company_demo;

-- 创建部门表
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    manager_id INT,
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
    manager_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (manager_id) REFERENCES employees(id)
);

-- 创建项目表
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12, 2)
);

-- 创建员工项目关联表
CREATE TABLE employee_projects (
    employee_id INT,
    project_id INT,
    role VARCHAR(50),
    hours_worked INT DEFAULT 0,
    PRIMARY KEY (employee_id, project_id),
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- 插入部门数据
INSERT INTO departments (name, location, budget) VALUES
('技术部', '北京', 1000000.00),
('市场部', '上海', 800000.00),
('人事部', '广州', 500000.00),
('财务部', '深圳', 600000.00),
('研发部', '杭州', 1200000.00);

-- 插入员工数据
INSERT INTO employees (name, age, gender, department_id, position, salary, hire_date, email, phone) VALUES
('张三', 30, '男', 1, '高级工程师', 15000.00, '2020-01-15', 'zhangsan@example.com', '13800138001'),
('李四', 28, '女', 1, '工程师', 12000.00, '2020-03-20', 'lisi@example.com', '13800138002'),
('王五', 35, '男', 1, '工程师', 13000.00, '2019-06-10', 'wangwu@example.com', '13800138003'),
('赵六', 25, '女', 1, '初级工程师', 8000.00, '2021-02-28', 'zhaoliu@example.com', '13800138004'),
('钱七', 32, '男', 2, '市场经理', 18000.00, '2019-11-05', 'qianqi@example.com', '13800138005'),
('孙八', 27, '女', 2, '市场专员', 9000.00, '2020-07-12', 'sunba@example.com', '13800138006'),
('周九', 40, '男', 2, '市场专员', 8500.00, '2020-05-20', 'zhoujiu@example.com', '13800138007'),
('吴十', 29, '女', 3, '人事经理', 16000.00, '2018-09-15', 'wushi@example.com', '13800138008'),
('郑十一', 26, '男', 3, '人事专员', 7000.00, '2021-01-10', 'zhengshiyi@example.com', '13800138009'),
('陈十二', 33, '女', 4, '财务经理', 20000.00, '2019-03-15', 'chenshier@example.com', '13800138010'),
('林十三', 28, '男', 4, '会计', 10000.00, '2020-06-20', 'linshisan@example.com', '13800138011'),
('黄十四', 36, '男', 5, '研发经理', 25000.00, '2018-05-10', 'huangshisi@example.com', '13800138012'),
('刘十五', 31, '女', 5, '高级研究员', 18000.00, '2019-08-15', 'liushiwu@example.com', '13800138013'),
('徐十六', 29, '男', 5, '研究员', 14000.00, '2020-02-20', 'xushiliu@example.com', '13800138014');

-- 插入项目数据
INSERT INTO projects (name, start_date, end_date, budget) VALUES
('项目A', '2023-01-01', '2023-12-31', 500000.00),
('项目B', '2023-03-01', '2023-08-31', 200000.00),
('项目C', '2023-04-01', '2023-09-30', 150000.00),
('项目D', '2023-02-15', '2023-11-30', 300000.00),
('项目E', '2023-05-01', '2023-10-31', 250000.00);

-- 插入员工项目关联数据
INSERT INTO employee_projects (employee_id, project_id, role, hours_worked) VALUES
(1, 1, '项目经理', 320),
(2, 1, '开发工程师', 400),
(3, 2, '项目经理', 200),
(4, 2, '市场专员', 300),
(5, 3, '项目经理', 150),
(6, 3, '人事专员', 200),
(7, 4, '项目经理', 250),
(8, 4, '人事专员', 180),
(9, 5, '项目经理', 220),
(10, 5, '财务专员', 160),
(11, 1, '财务专员', 120),
(12, 2, '会计', 140),
(13, 3, '研发主管', 280),
(14, 4, '高级研究员', 350),
(15, 5, '研究员', 300);

-- 设置经理关系
UPDATE employees SET manager_id = 1 WHERE id IN (2, 3);
UPDATE employees SET manager_id = 5 WHERE id IN (6, 7);
UPDATE employees SET manager_id = 8 WHERE id IN (9);
UPDATE employees SET manager_id = 10 WHERE id IN (11, 12);
UPDATE employees SET manager_id = 13 WHERE id IN (14, 15);

-- =================================
-- 9.2 索引优化示例
-- =================================

-- 创建单列索引
CREATE INDEX idx_employee_name ON employees(name);
CREATE INDEX idx_employee_department ON employees(department_id);
CREATE INDEX idx_employee_salary ON employees(salary);

-- 创建复合索引
CREATE INDEX idx_employee_dept_salary ON employees(department_id, salary);

-- 创建唯一索引
CREATE UNIQUE INDEX idx_employee_email ON employees(email);

-- 查看表的索引
SHOW INDEX FROM employees;

-- 分析索引使用情况
EXPLAIN SELECT * FROM employees WHERE name = '张三';
EXPLAIN SELECT * FROM employees WHERE department_id = 1;
EXPLAIN SELECT * FROM employees WHERE department_id = 1 AND salary > 10000;

-- 测试复合索引的最左前缀原则
EXPLAIN SELECT * FROM employees WHERE department_id = 1;  -- 可以使用索引
EXPLAIN SELECT * FROM employees WHERE salary > 10000;     -- 无法使用索引
EXPLAIN SELECT * FROM employees WHERE salary > 10000 AND department_id = 1;  -- 无法使用索引

-- =================================
-- 9.3 查询优化示例
-- =================================

-- 避免SELECT *
EXPLAIN SELECT * FROM employees WHERE department_id = 1;  -- 不推荐
EXPLAIN SELECT id, name, position FROM employees WHERE department_id = 1;  -- 推荐

-- 使用LIMIT限制结果集
EXPLAIN SELECT * FROM employees ORDER BY salary DESC;  -- 不推荐
EXPLAIN SELECT * FROM employees ORDER BY salary DESC LIMIT 10;  -- 推荐

-- 避免在WHERE子句中对列使用函数
EXPLAIN SELECT * FROM employees WHERE YEAR(hire_date) = 2020;  -- 不推荐，无法使用索引
EXPLAIN SELECT * FROM employees WHERE hire_date >= '2020-01-01' AND hire_date < '2021-01-01';  -- 推荐，可以使用索引

-- 使用EXISTS代替IN
EXPLAIN SELECT * FROM departments d 
WHERE d.id IN (SELECT department_id FROM employees WHERE salary > 10000);  -- 不推荐

EXPLAIN SELECT * FROM departments d 
WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id AND e.salary > 10000);  -- 推荐

-- 避免在WHERE子句中使用OR
EXPLAIN SELECT * FROM employees WHERE department_id = 1 OR department_id = 2;  -- 不推荐
EXPLAIN SELECT * FROM employees WHERE department_id IN (1, 2);  -- 推荐

-- =================================
-- 9.4 数据库设计优化示例
-- =================================

-- 创建分区表示例（MySQL 8.0+）
CREATE TABLE sales (
    id INT AUTO_INCREMENT,
    sale_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    PRIMARY KEY (id, sale_date)
) PARTITION BY RANGE (YEAR(sale_date)) (
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);

-- 插入销售数据
INSERT INTO sales (sale_date, amount, customer_id, product_id) VALUES
('2020-01-15', 1000.00, 1, 1),
('2020-03-20', 1500.00, 2, 2),
('2021-05-10', 2000.00, 3, 1),
('2021-07-15', 1200.00, 1, 3),
('2022-02-28', 1800.00, 2, 2),
('2022-09-30', 2500.00, 3, 3);

-- 测试分区查询
EXPLAIN SELECT * FROM sales WHERE sale_date >= '2021-01-01' AND sale_date < '2022-01-01';

-- 垂直分表示例
-- 主表：存储常用信息
CREATE TABLE employees_basic (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    position VARCHAR(50),
    department_id INT,
    salary DECIMAL(10, 2)
);

-- 扩展表：存储不常用信息
CREATE TABLE employees_extended (
    employee_id INT PRIMARY KEY,
    biography TEXT,
    education TEXT,
    experience TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees_basic(id)
);

-- 插入数据
INSERT INTO employees_basic (name, position, department_id, salary) VALUES
('张三', '高级工程师', 1, 15000.00),
('李四', '工程师', 1, 12000.00);

INSERT INTO employees_extended (employee_id, biography, education, experience) VALUES
(1, '经验丰富的高级工程师', '计算机科学硕士', '5年开发经验'),
(2, '专注后端开发', '软件工程学士', '3年开发经验');

-- 查询常用信息（无需JOIN）
SELECT * FROM employees_basic WHERE id = 1;

-- 查询完整信息（需要JOIN）
SELECT b.*, e.biography, e.education, e.experience
FROM employees_basic b
JOIN employees_extended e ON b.id = e.employee_id
WHERE b.id = 1;

-- =================================
-- 9.5 配置优化示例
-- =================================

-- 查看当前配置
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
SHOW VARIABLES LIKE 'query_cache_size';
SHOW VARIABLES LIKE 'max_connections';

-- 修改配置（需要管理员权限）
-- SET GLOBAL innodb_buffer_pool_size = 1073741824;  -- 1GB
-- SET GLOBAL query_cache_size = 268435456;  -- 256MB
-- SET GLOBAL max_connections = 200;

-- =================================
-- 9.6 监控与诊断示例
-- =================================

-- 查看慢查询日志设置
SHOW VARIABLES LIKE 'slow_query%';

-- 启用慢查询日志（需要管理员权限）
-- SET GLOBAL slow_query_log = 'ON';
-- SET GLOBAL slow_query_log_file = '/var/log/mysql/mysql-slow.log';
-- SET GLOBAL long_query_time = 2;

-- 查看查询缓存状态
SHOW STATUS LIKE 'Qcache%';

-- 查看表状态信息
SHOW TABLE STATUS LIKE 'employees';

-- 分析表
ANALYZE TABLE employees;

-- 优化表
OPTIMIZE TABLE employees;

-- 检查表
CHECK TABLE employees;

-- =================================
-- 9.7 高级优化技术示例
-- =================================

-- 创建视图简化复杂查询
CREATE VIEW employee_department_view AS
SELECT 
    e.id,
    e.name,
    e.position,
    e.salary,
    d.name AS department_name,
    d.location AS department_location
FROM employees e
JOIN departments d ON e.department_id = d.id;

-- 使用视图
SELECT * FROM employee_department_view WHERE department_name = '技术部';

-- 创建存储过程封装复杂逻辑
DELIMITER //
CREATE PROCEDURE GetDepartmentStats(IN dept_id INT)
BEGIN
    SELECT 
        d.name AS department,
        COUNT(e.id) AS employee_count,
        AVG(e.salary) AS avg_salary,
        MIN(e.salary) AS min_salary,
        MAX(e.salary) AS max_salary
    FROM departments d
    LEFT JOIN employees e ON d.id = e.department_id
    WHERE d.id = dept_id
    GROUP BY d.id, d.name;
END //
DELIMITER ;

-- 调用存储过程
CALL GetDepartmentStats(1);

-- 创建函数计算年薪
DELIMITER //
CREATE FUNCTION CalculateAnnualSalary(salary DECIMAL(10, 2), bonus DECIMAL(10, 2))
RETURNS DECIMAL(12, 2)
DETERMINISTIC
BEGIN
    RETURN (salary * 12) + bonus;
END //
DELIMITER ;

-- 使用函数
SELECT 
    name,
    salary,
    CalculateAnnualSalary(salary, 5000) AS annual_salary
FROM employees
LIMIT 5;

-- =================================
-- 9.8 常见性能问题与解决方案示例
-- =================================

-- 问题1：全表扫描
-- 解决方案：创建适当的索引
EXPLAIN SELECT * FROM employees WHERE name = '张三';  -- 全表扫描
CREATE INDEX idx_employee_name ON employees(name);  -- 创建索引
EXPLAIN SELECT * FROM employees WHERE name = '张三';  -- 使用索引

-- 问题2：索引失效
-- 解决方案：避免在索引列上使用函数
EXPLAIN SELECT * FROM employees WHERE YEAR(hire_date) = 2020;  -- 索引失效
EXPLAIN SELECT * FROM employees WHERE hire_date >= '2020-01-01' AND hire_date < '2021-01-01';  -- 使用索引

-- 问题3：锁竞争
-- 解决方案：缩短事务持续时间
-- 不推荐：长事务
START TRANSACTION;
UPDATE employees SET salary = salary * 1.1 WHERE department_id = 1;
-- 执行其他操作...
COMMIT;

-- 推荐：短事务
START TRANSACTION;
UPDATE employees SET salary = salary * 1.1 WHERE department_id = 1;
COMMIT;
-- 执行其他操作...

-- 问题4：大数据量处理
-- 解决方案：使用分页查询
-- 不推荐：一次性加载大量数据
SELECT * FROM employees ORDER BY salary DESC;

-- 推荐：使用分页查询
SELECT * FROM employees ORDER BY salary DESC LIMIT 10 OFFSET 0;  -- 第一页
SELECT * FROM employees ORDER BY salary DESC LIMIT 10 OFFSET 10; -- 第二页

-- =================================
-- 9.9 性能优化最佳实践示例
-- =================================

-- 1. 合理设计表结构
-- 使用适当的数据类型
CREATE TABLE optimized_employees (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,  -- 使用UNSIGNED增加范围
    name VARCHAR(50) NOT NULL,
    age TINYINT UNSIGNED,  -- 使用TINYINT存储年龄
    gender ENUM('男', '女'),  -- 使用ENUM存储性别
    department_id TINYINT UNSIGNED,  -- 假设部门数量不超过255
    position VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE,
    email VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    manager_id INT UNSIGNED,
    INDEX idx_department (department_id),
    INDEX idx_salary (salary),
    INDEX idx_name (name),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (manager_id) REFERENCES employees(id)
);

-- 2. 编写高效的SQL
-- 使用批量插入代替单条插入
-- 不推荐：单条插入
INSERT INTO employees (name, position, department_id, salary) VALUES ('员工1', '工程师', 1, 10000);
INSERT INTO employees (name, position, department_id, salary) VALUES ('员工2', '工程师', 1, 11000);
INSERT INTO employees (name, position, department_id, salary) VALUES ('员工3', '工程师', 1, 12000);

-- 推荐：批量插入
INSERT INTO employees (name, position, department_id, salary) VALUES
('员工1', '工程师', 1, 10000),
('员工2', '工程师', 1, 11000),
('员工3', '工程师', 1, 12000);

-- 3. 合理使用事务
-- 不推荐：大事务
START TRANSACTION;
UPDATE employees SET salary = salary * 1.1 WHERE department_id = 1;
UPDATE departments SET budget = budget * 1.1 WHERE id = 1;
-- 其他操作...
COMMIT;

-- 推荐：小事务
START TRANSACTION;
UPDATE employees SET salary = salary * 1.1 WHERE department_id = 1;
COMMIT;

START TRANSACTION;
UPDATE departments SET budget = budget * 1.1 WHERE id = 1;
COMMIT;

-- 4. 使用适当的JOIN类型
-- INNER JOIN：只返回匹配的行
SELECT e.name, d.name AS department
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;

-- LEFT JOIN：返回左表所有行，即使右表没有匹配
SELECT e.name, d.name AS department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- 5. 使用窗口函数代替自连接
-- 不推荐：使用自连接
SELECT e1.name, e1.salary, 
       (SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department_id = e1.department_id) AS dept_avg_salary
FROM employees e1;

-- 推荐：使用窗口函数
SELECT name, salary, AVG(salary) OVER (PARTITION BY department_id) AS dept_avg_salary
FROM employees;