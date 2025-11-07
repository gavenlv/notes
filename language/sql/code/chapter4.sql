-- 第4章：SQL高级查询示例代码

-- 创建示例数据库
CREATE DATABASE IF NOT EXISTS company_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE company_demo;

-- 删除已存在的表（确保环境干净）
DROP TABLE IF EXISTS employee_projects;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

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
UPDATE employees SET manager_id = 1 WHERE id IN (2, 3, 4);
UPDATE employees SET manager_id = 5 WHERE id IN (6, 7);
UPDATE employees SET manager_id = 8 WHERE id IN (9);
UPDATE employees SET manager_id = 10 WHERE id IN (11, 12);
UPDATE employees SET manager_id = 13 WHERE id IN (14, 15);

-- 4.1 GROUP BY子句与聚合函数示例

-- 单列分组：按部门分组，计算每个部门的员工数量
SELECT department_id, COUNT(*) AS '员工数量'
FROM employees
GROUP BY department_id;

-- 单列分组：按职位分组，计算每个职位的平均薪资
SELECT position, AVG(salary) AS '平均薪资'
FROM employees
GROUP BY position;

-- 多列分组：按部门和职位分组，计算每个部门和职位的员工数量和平均薪资
SELECT department_id, position, COUNT(*) AS '员工数量', AVG(salary) AS '平均薪资'
FROM employees
GROUP BY department_id, position
ORDER BY department_id, AVG(salary) DESC;

-- COUNT函数示例
-- 计算所有员工数量
SELECT COUNT(*) AS '总员工数' FROM employees;

-- 计算有电话的员工数量（排除NULL值）
SELECT COUNT(phone) AS '有电话的员工数' FROM employees;

-- 计算不同职位的数量
SELECT COUNT(DISTINCT position) AS '不同职位数量' FROM employees;

-- SUM函数示例
-- 计算所有员工的薪资总和
SELECT SUM(salary) AS '薪资总和' FROM employees;

-- 按部门计算薪资总和
SELECT department_id, SUM(salary) AS '部门薪资总和'
FROM employees
GROUP BY department_id;

-- AVG函数示例
-- 计算所有员工的平均薪资
SELECT AVG(salary) AS '平均薪资' FROM employees;

-- 按职位计算平均薪资
SELECT position, AVG(salary) AS '平均薪资'
FROM employees
GROUP BY position;

-- MAX和MIN函数示例
-- 计算最高和最低薪资
SELECT MAX(salary) AS '最高薪资', MIN(salary) AS '最低薪资' FROM employees;

-- 按部门计算最高和最低薪资
SELECT department_id, MAX(salary) AS '最高薪资', MIN(salary) AS '最低薪资'
FROM employees
GROUP BY department_id;

-- 综合示例：按部门分组，计算每个部门的员工数量、平均薪资、最高薪资和最低薪资
SELECT 
    d.name AS '部门名称',
    COUNT(e.id) AS '员工数量',
    AVG(e.salary) AS '平均薪资',
    MAX(e.salary) AS '最高薪资',
    MIN(e.salary) AS '最低薪资',
    SUM(e.salary) AS '薪资总和'
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY e.department_id, d.name
ORDER BY COUNT(e.id) DESC;

-- 按职位分组，计算每个职位的员工数量和平均薪资
SELECT 
    position AS '职位',
    COUNT(*) AS '员工数量',
    AVG(salary) AS '平均薪资',
    MAX(salary) AS '最高薪资',
    MIN(salary) AS '最低薪资'
FROM employees
GROUP BY position
ORDER BY AVG(salary) DESC;

-- 4.2 HAVING子句示例

-- 查询员工数量大于2的部门
SELECT department_id, COUNT(*) AS '员工数量'
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 2;

-- 查询平均薪资大于12000的职位
SELECT position, AVG(salary) AS '平均薪资'
FROM employees
GROUP BY position
HAVING AVG(salary) > 12000;

-- 查询薪资总和大于50000的部门
SELECT department_id, SUM(salary) AS '薪资总和'
FROM employees
GROUP BY department_id
HAVING SUM(salary) > 50000;

-- 复合条件：查询员工数量大于2且平均薪资大于10000的部门
SELECT department_id, COUNT(*) AS '员工数量', AVG(salary) AS '平均薪资'
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 2 AND AVG(salary) > 10000;

-- WHERE和HAVING结合使用
-- 先过滤年龄大于25的员工，再按部门分组，最后筛选平均薪资大于10000的部门
SELECT department_id, COUNT(*) AS '员工数量', AVG(salary) AS '平均薪资'
FROM employees
WHERE age > 25
GROUP BY department_id
HAVING AVG(salary) > 10000;

-- 综合示例：查询员工数量大于2的部门
SELECT 
    d.name AS '部门名称',
    COUNT(e.id) AS '员工数量'
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY e.department_id, d.name
HAVING COUNT(e.id) > 2;

-- 查询平均薪资大于12000的职位
SELECT 
    position AS '职位',
    COUNT(*) AS '员工数量',
    AVG(salary) AS '平均薪资'
FROM employees
GROUP BY position
HAVING AVG(salary) > 12000;

-- 查询薪资总和大于50000的部门
SELECT 
    d.name AS '部门名称',
    SUM(e.salary) AS '薪资总和'
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY e.department_id, d.name
HAVING SUM(e.salary) > 50000;

-- 复合条件：查询员工数量大于2且平均薪资大于10000的部门
SELECT 
    d.name AS '部门名称',
    COUNT(e.id) AS '员工数量',
    AVG(e.salary) AS '平均薪资'
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY e.department_id, d.name
HAVING COUNT(e.id) > 2 AND AVG(e.salary) > 10000;

-- 4.3 连接查询（JOIN）示例

-- 内连接：查询员工及其部门信息
SELECT e.name, e.position, d.name AS department
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;

-- 使用WHERE实现相同效果
SELECT e.name, e.position, d.name AS department
FROM employees e, departments d
WHERE e.department_id = d.id;

-- 左连接：查询所有员工及其部门信息（即使没有部门）
SELECT e.name, e.position, d.name AS department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- 查询没有员工的部门
SELECT d.name AS department
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
WHERE e.id IS NULL;

-- 右连接：查询所有部门及其员工信息（即使没有员工）
SELECT e.name, e.position, d.name AS department
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id;

-- 多表连接：查询员工参与的项目信息
SELECT 
    e.name AS employee_name,
    p.name AS project_name,
    ep.role,
    ep.hours_worked
FROM employees e
JOIN employee_projects ep ON e.id = ep.employee_id
JOIN projects p ON ep.project_id = p.id
ORDER BY e.name, p.name;

-- 自连接：查询员工及其经理信息
SELECT 
    e.name AS employee_name,
    e.position AS employee_position,
    m.name AS manager_name,
    m.position AS manager_position
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id
ORDER BY e.name;

-- 综合示例：内连接查询员工及其部门信息
SELECT 
    e.name AS '员工姓名',
    e.position AS '职位',
    d.name AS '部门名称',
    d.location AS '部门位置'
FROM employees e
INNER JOIN departments d ON e.department_id = d.id
ORDER BY d.name, e.name;

-- 左连接查询所有员工及其部门信息
SELECT 
    e.name AS '员工姓名',
    e.position AS '职位',
    d.name AS '部门名称'
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- 查询没有员工的部门
SELECT 
    d.name AS '部门名称',
    d.location AS '部门位置'
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
WHERE e.id IS NULL;

-- 多表连接查询员工参与的项目信息
SELECT 
    e.name AS '员工姓名',
    p.name AS '项目名称',
    ep.role AS '角色',
    ep.hours_worked AS '工作小时数'
FROM employees e
JOIN employee_projects ep ON e.id = ep.employee_id
JOIN projects p ON ep.project_id = p.id
ORDER BY e.name, p.name;

-- 自连接查询员工及其经理信息
SELECT 
    e.name AS '员工姓名',
    e.position AS '员工职位',
    m.name AS '经理姓名',
    m.position AS '经理职位'
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id
ORDER BY e.name;

-- 4.4 子查询示例

-- 标量子查询：查询薪资高于平均薪资的员工
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- 查询每个员工的薪资与平均薪资的差距
SELECT 
    name, 
    salary,
    salary - (SELECT AVG(salary) FROM employees) AS '与平均薪资的差距'
FROM employees;

-- 列表子查询：查询技术部（部门ID=1）的员工
SELECT name, position, department_id
FROM employees
WHERE department_id IN (SELECT id FROM departments WHERE name = '技术部');

-- 使用ANY：查询薪资大于任何市场部员工薪资的技术部员工
SELECT name, position, salary
FROM employees
WHERE department_id = 1 AND salary > ANY (
    SELECT salary FROM employees WHERE department_id = 2
);

-- 使用ALL：查询薪资大于所有市场部员工薪资的技术部员工
SELECT name, position, salary
FROM employees
WHERE department_id = 1 AND salary > ALL (
    SELECT salary FROM employees WHERE department_id = 2
);

-- 行子查询：查询与张三职位和薪资相同的员工
SELECT name, position, salary
FROM employees
WHERE (position, salary) = (
    SELECT position, salary FROM employees WHERE name = '张三'
);

-- 表子查询：查询各部门的平均薪资
SELECT department_name, avg_salary
FROM (
    SELECT 
        d.name AS department_name,
        AVG(e.salary) AS avg_salary
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    GROUP BY d.name
) AS dept_avg
WHERE avg_salary > 10000;

-- 相关子查询：查询薪资高于其所在部门平均薪资的员工
SELECT name, salary, department_id
FROM employees e1
WHERE salary > (
    SELECT AVG(salary)
    FROM employees e2
    WHERE e2.department_id = e1.department_id
);

-- EXISTS：查询有员工的部门
SELECT name, location
FROM departments d
WHERE EXISTS (
    SELECT 1 FROM employees e WHERE e.department_id = d.id
);

-- NOT EXISTS：查询没有员工的部门
SELECT name, location
FROM departments d
WHERE NOT EXISTS (
    SELECT 1 FROM employees e WHERE e.department_id = d.id
);

-- 综合示例：标量子查询查询薪资高于平均薪资的员工
SELECT 
    name, 
    position, 
    salary,
    (SELECT AVG(salary) FROM employees) AS '平均薪资'
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- 列表子查询查询技术部的员工
SELECT name, position, department_id
FROM employees
WHERE department_id IN (SELECT id FROM departments WHERE name = '技术部');

-- 相关子查询查询薪资高于其所在部门平均薪资的员工
SELECT 
    e1.name, 
    e1.salary, 
    e1.department_id,
    (SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department_id = e1.department_id) AS '部门平均薪资'
FROM employees e1
WHERE e1.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e1.department_id
);

-- 表子查询查询各部门的平均薪资
SELECT department_name, avg_salary
FROM (
    SELECT 
        d.name AS department_name,
        AVG(e.salary) AS avg_salary
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    GROUP BY d.name
) AS dept_avg
WHERE avg_salary > 10000;

-- EXISTS查询有员工的部门
SELECT name, location
FROM departments d
WHERE EXISTS (
    SELECT 1 FROM employees e WHERE e.department_id = d.id
);

-- 4.5 集合运算示例

-- UNION：查询所有经理和工程师的姓名
SELECT name, position FROM employees WHERE position LIKE '%经理%'
UNION
SELECT name, position FROM employees WHERE position LIKE '%工程师%';

-- UNION ALL：查询所有经理和工程师的姓名（包括重复）
SELECT name, position FROM employees WHERE position LIKE '%经理%'
UNION ALL
SELECT name, position FROM employees WHERE position LIKE '%工程师%';

-- 查询所有员工和部门的名称
SELECT name AS '名称', '员工' AS '类型' FROM employees
UNION
SELECT name AS '名称', '部门' AS '类型' FROM departments;

-- 使用INNER JOIN模拟INTERSECT：查询既是经理又是高薪的员工
SELECT DISTINCT e1.name, e1.position, e1.salary
FROM employees e1
JOIN employees e2 ON e1.name = e2.name
WHERE e1.position LIKE '%经理%' AND e2.salary > 15000;

-- 使用LEFT JOIN模拟EXCEPT：查询是经理但不是高薪的员工
SELECT e1.name, e1.position, e1.salary
FROM employees e1
LEFT JOIN employees e2 ON e1.name = e2.name AND e2.salary > 15000
WHERE e1.position LIKE '%经理%' AND e2.name IS NULL;

-- 综合示例：UNION查询所有经理和工程师的姓名
SELECT name, position FROM employees WHERE position LIKE '%经理%'
UNION
SELECT name, position FROM employees WHERE position LIKE '%工程师%';

-- UNION ALL查询所有经理和工程师的姓名（包括重复）
SELECT name, position FROM employees WHERE position LIKE '%经理%'
UNION ALL
SELECT name, position FROM employees WHERE position LIKE '%工程师%';

-- 查询所有员工和部门的名称
SELECT name AS '名称', '员工' AS '类型' FROM employees
UNION
SELECT name AS '名称', '部门' AS '类型' FROM departments;

-- 使用INNER JOIN模拟INTERSECT查询既是经理又是高薪的员工
SELECT DISTINCT e1.name, e1.position, e1.salary
FROM employees e1
JOIN employees e2 ON e1.name = e2.name
WHERE e1.position LIKE '%经理%' AND e2.salary > 15000;

-- 使用LEFT JOIN模拟EXCEPT查询是经理但不是高薪的员工
SELECT e1.name, e1.position, e1.salary
FROM employees e1
LEFT JOIN employees e2 ON e1.name = e2.name AND e2.salary > 15000
WHERE e1.position LIKE '%经理%' AND e2.name IS NULL;