-- 第7章：SQL聚合与分组示例代码

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
-- 7.2 COUNT函数示例
-- =================================

-- COUNT(*)
SELECT COUNT(*) AS total_employees FROM employees;

-- COUNT(column)
SELECT COUNT(email) AS employees_with_email FROM employees;

-- COUNT(DISTINCT)
SELECT COUNT(DISTINCT position) AS distinct_positions FROM employees;

-- =================================
-- 7.3 SUM函数示例
-- =================================

-- 计算所有员工的总薪资
SELECT SUM(salary) AS total_salary FROM employees;

-- 计算各部门的总薪资
SELECT 
    d.name AS department,
    SUM(e.salary) AS department_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name;

-- 计算所有项目的总预算
SELECT SUM(budget) AS total_budget FROM projects;

-- 计算所有员工在所有项目上的总工作小时数
SELECT SUM(hours_worked) AS total_hours FROM employee_projects;

-- SUM函数与条件表达式结合
-- 计算每个部门中薪资高于10000的员工的总薪资
SELECT 
    d.name AS department,
    SUM(e.salary) AS total_salary,
    SUM(CASE WHEN e.salary > 10000 THEN e.salary ELSE 0 END) AS high_salary_total
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name;

-- =================================
-- 7.4 AVG函数示例
-- =================================

-- 计算所有员工的平均薪资
SELECT AVG(salary) AS average_salary FROM employees;

-- 计算各部门的平均薪资
SELECT 
    d.name AS department,
    AVG(e.salary) AS department_avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name;

-- 计算所有项目的平均预算
SELECT AVG(budget) AS average_budget FROM projects;

-- 计算所有员工在所有项目上的平均工作小时数
SELECT AVG(hours_worked) AS average_hours FROM employee_projects;

-- AVG函数与条件表达式结合
-- 计算每个部门中薪资高于10000的员工的平均薪资
SELECT 
    d.name AS department,
    AVG(e.salary) AS total_avg_salary,
    AVG(CASE WHEN e.salary > 10000 THEN e.salary ELSE NULL END) AS high_salary_avg
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name;

-- =================================
-- 7.5 MIN和MAX函数示例
-- =================================

-- 查找最低和最高薪资
SELECT MIN(salary) AS min_salary, MAX(salary) AS max_salary FROM employees;

-- 查找最早和最晚入职日期
SELECT MIN(hire_date) AS earliest_hire, MAX(hire_date) AS latest_hire FROM employees;

-- 查找最小和最大年龄
SELECT MIN(age) AS min_age, MAX(age) AS max_age FROM employees;

-- 查找最早开始和最晚结束的项目
SELECT MIN(start_date) AS earliest_start, MAX(end_date) AS latest_end FROM projects;

-- MIN和MAX函数与GROUP BY结合
-- 查找各部门的最低和最高薪资
SELECT 
    d.name AS department,
    MIN(e.salary) AS min_salary,
    MAX(e.salary) AS max_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name;

-- 查找各部门最早和最晚入职日期
SELECT 
    d.name AS department,
    MIN(e.hire_date) AS earliest_hire,
    MAX(e.hire_date) AS latest_hire
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name;

-- =================================
-- 7.6 GROUP_CONCAT函数示例
-- =================================

-- 连接所有员工姓名
SELECT GROUP_CONCAT(name) AS all_employees FROM employees;

-- 连接各部门的员工姓名
SELECT 
    d.name AS department,
    GROUP_CONCAT(e.name) AS employees
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name;

-- 连接各部门的员工姓名，按薪资降序排列
SELECT 
    d.name AS department,
    GROUP_CONCAT(e.name ORDER BY e.salary DESC) AS employees_by_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name;

-- 连接各部门的员工姓名，使用自定义分隔符
SELECT 
    d.name AS department,
    GROUP_CONCAT(e.name SEPARATOR ' | ') AS employees_with_separator
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name;

-- 连接各部门的不同职位
SELECT 
    d.name AS department,
    GROUP_CONCAT(DISTINCT e.position) AS positions
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name;

-- =================================
-- 7.7 GROUP BY子句示例
-- =================================

-- 单列分组
-- 按部门分组，计算每个部门的员工数量
SELECT 
    d.name AS department,
    COUNT(*) AS employee_count
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name;

-- 按职位分组，计算每个职位的平均薪资
SELECT 
    position,
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary,
    MIN(salary) AS min_salary,
    MAX(salary) AS max_salary
FROM employees
GROUP BY position
ORDER BY avg_salary DESC;

-- 按性别分组，计算每个性别的员工数量
SELECT 
    gender,
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary
FROM employees
GROUP BY gender;

-- 多列分组
-- 按部门和职位分组，计算每个部门和职位的员工数量和平均薪资
SELECT 
    d.name AS department,
    e.position,
    COUNT(*) AS employee_count,
    AVG(e.salary) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name, e.position
ORDER BY d.name, avg_salary DESC;

-- GROUP BY与表达式
-- 按薪资范围分组
SELECT 
    CASE 
        WHEN e.salary < 10000 THEN '低薪'
        WHEN e.salary < 15000 THEN '中薪'
        ELSE '高薪'
    END AS salary_level,
    COUNT(*) AS employee_count,
    AVG(e.salary) AS avg_salary
FROM employees e
GROUP BY 
    CASE 
        WHEN e.salary < 10000 THEN '低薪'
        WHEN e.salary < 15000 THEN '中薪'
        ELSE '高薪'
    END
ORDER BY avg_salary;

-- 按入职年份分组
SELECT 
    YEAR(e.hire_date) AS hire_year,
    COUNT(*) AS employee_count,
    AVG(e.salary) AS avg_salary
FROM employees e
GROUP BY YEAR(e.hire_date)
ORDER BY hire_year;

-- =================================
-- 7.8 HAVING子句示例
-- =================================

-- 查询员工数量大于3的部门
SELECT 
    d.name AS department,
    COUNT(*) AS employee_count
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name
HAVING COUNT(*) > 3;

-- 查询平均薪资大于10000的部门
SELECT 
    d.name AS department,
    COUNT(*) AS employee_count,
    AVG(e.salary) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name
HAVING AVG(e.salary) > 10000;

-- 查询薪资范围大于5000的职位
SELECT 
    position,
    COUNT(*) AS employee_count,
    MIN(salary) AS min_salary,
    MAX(salary) AS max_salary,
    MAX(salary) - MIN(salary) AS salary_range
FROM employees
GROUP BY position
HAVING MAX(salary) - MIN(salary) > 5000;

-- HAVING子句与WHERE子句结合使用
-- 查询薪资大于10000的员工中，平均薪资大于12000的部门
SELECT 
    d.name AS department,
    COUNT(*) AS employee_count,
    AVG(e.salary) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.salary > 10000
GROUP BY d.id, d.name
HAVING AVG(e.salary) > 12000;

-- 查询2020年以后入职的员工中，平均薪资大于10000的部门
SELECT 
    d.name AS department,
    COUNT(*) AS employee_count,
    AVG(e.salary) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.hire_date >= '2020-01-01'
GROUP BY d.id, d.name
HAVING AVG(e.salary) > 10000;

-- =================================
-- 7.9 高级分组技巧示例
-- =================================

-- 使用ROLLUP生成分组汇总
SELECT 
    COALESCE(d.name, '总计') AS department,
    COALESCE(e.position, '小计') AS position,
    COUNT(*) AS employee_count,
    AVG(e.salary) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.name, e.position WITH ROLLUP;

-- 使用GROUPING SETS生成分组汇总
SELECT 
    COALESCE(d.name, '总计') AS department,
    COALESCE(e.position, '总计') AS position,
    COUNT(*) AS employee_count,
    AVG(e.salary) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY GROUPING SETS (
    (d.name),           -- 按部门分组
    (e.position),        -- 按职位分组
    (d.name, e.position), -- 按部门和职位分组
    ()                   -- 总计
);

-- =================================
-- 7.10 聚合函数与连接查询结合示例
-- =================================

-- 聚合函数与内连接
-- 查询各部门的员工数量和平均薪资
SELECT 
    d.name AS department,
    COUNT(e.id) AS employee_count,
    AVG(e.salary) AS avg_salary,
    MIN(e.salary) AS min_salary,
    MAX(e.salary) AS max_salary
FROM departments d
JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name
ORDER BY employee_count DESC;

-- 查询每个项目的参与人数和总工作小时数
SELECT 
    p.name AS project,
    COUNT(DISTINCT ep.employee_id) AS employee_count,
    SUM(ep.hours_worked) AS total_hours,
    AVG(ep.hours_worked) AS avg_hours
FROM projects p
JOIN employee_projects ep ON p.id = ep.project_id
GROUP BY p.id, p.name
ORDER BY total_hours DESC;

-- 聚合函数与左连接
-- 查询所有部门的员工数量（包括没有员工的部门）
SELECT 
    d.name AS department,
    COUNT(e.id) AS employee_count,
    AVG(e.salary) AS avg_salary
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name
ORDER BY employee_count DESC;

-- 查询所有项目的参与人数（包括没有参与者的项目）
SELECT 
    p.name AS project,
    COUNT(DISTINCT ep.employee_id) AS employee_count,
    SUM(ep.hours_worked) AS total_hours
FROM projects p
LEFT JOIN employee_projects ep ON p.id = ep.project_id
GROUP BY p.id, p.name
ORDER BY employee_count DESC;

-- 聚合函数与多表连接
-- 查询各部门中不同职位的员工数量和平均薪资
SELECT 
    d.name AS department,
    e.position,
    COUNT(*) AS employee_count,
    AVG(e.salary) AS avg_salary
FROM departments d
JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name, e.position
ORDER BY d.name, employee_count DESC;

-- 查询各部门员工参与的项目数量和总工作小时数
SELECT 
    d.name AS department,
    COUNT(DISTINCT p.id) AS project_count,
    SUM(ep.hours_worked) AS total_hours
FROM departments d
JOIN employees e ON d.id = e.department_id
LEFT JOIN employee_projects ep ON e.id = ep.employee_id
LEFT JOIN projects p ON ep.project_id = p.id
GROUP BY d.id, d.name
ORDER BY total_hours DESC;

-- =================================
-- 综合示例：复杂聚合与分组查询
-- =================================

-- 查询各部门中薪资排名前2的员工
SELECT 
    d.name AS department,
    e.name AS employee,
    e.position,
    e.salary
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE (
    SELECT COUNT(*) 
    FROM employees e2 
    WHERE e2.department_id = e.department_id AND e2.salary > e.salary
) < 2
ORDER BY d.name, e.salary DESC;

-- 查询每个部门中薪资高于平均薪资的员工，并显示部门平均薪资
SELECT 
    d.name AS department,
    e.name AS employee,
    e.position,
    e.salary,
    (SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department_id = d.id) AS dept_avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.salary > (
    SELECT AVG(e2.salary) 
    FROM employees e2 
    WHERE e2.department_id = d.id
)
ORDER BY d.name, e.salary DESC;

-- 查询参与项目数量最多的员工
SELECT 
    e.name,
    e.position,
    COUNT(DISTINCT ep.project_id) AS project_count
FROM employees e
JOIN employee_projects ep ON e.id = ep.employee_id
GROUP BY e.id, e.name, e.position
HAVING COUNT(DISTINCT ep.project_id) = (
    SELECT MAX(project_count)
    FROM (
        SELECT COUNT(DISTINCT ep2.project_id) AS project_count
        FROM employee_projects ep2
        GROUP BY ep2.employee_id
    ) AS counts
);

-- 查询每个项目中工作小时数最多的员工及其经理
SELECT 
    p.name AS project,
    e.name AS employee,
    e.position AS employee_position,
    m.name AS manager,
    m.position AS manager_position,
    ep.hours_worked
FROM employees e
JOIN employee_projects ep ON e.id = ep.employee_id
JOIN projects p ON ep.project_id = p.id
LEFT JOIN employees m ON e.manager_id = m.id
WHERE ep.hours_worked = (
    SELECT MAX(ep2.hours_worked)
    FROM employee_projects ep2
    WHERE ep2.project_id = p.id
)
ORDER BY p.name;

-- 查询各部门的薪资分布情况
SELECT 
    d.name AS department,
    SUM(CASE WHEN e.salary < 10000 THEN 1 ELSE 0 END) AS low_salary_count,
    SUM(CASE WHEN e.salary >= 10000 AND e.salary < 15000 THEN 1 ELSE 0 END) AS medium_salary_count,
    SUM(CASE WHEN e.salary >= 15000 THEN 1 ELSE 0 END) AS high_salary_count,
    COUNT(*) AS total_count,
    AVG(e.salary) AS avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name
ORDER BY d.name;