-- 第6章：SQL连接与子查询示例代码

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
-- 6.2 内连接（INNER JOIN）示例
-- =================================

-- 内连接：查询员工及其部门信息
SELECT 
    e.name AS '员工姓名',
    e.position AS '职位',
    d.name AS '部门名称',
    d.location AS '部门位置'
FROM employees e
INNER JOIN departments d ON e.department_id = d.id
ORDER BY d.name, e.name;

-- 内连接：查询员工参与的项目信息
SELECT 
    e.name AS '员工姓名',
    p.name AS '项目名称',
    ep.role AS '角色',
    ep.hours_worked AS '工作小时数'
FROM employees e
INNER JOIN employee_projects ep ON e.id = ep.employee_id
INNER JOIN projects p ON ep.project_id = p.id
ORDER BY e.name, p.name;

-- 使用WHERE实现相同效果
SELECT 
    e.name AS '员工姓名',
    e.position AS '职位',
    d.name AS '部门名称'
FROM employees e, departments d
WHERE e.department_id = d.id;

-- =================================
-- 6.3 外连接（OUTER JOIN）示例
-- =================================

-- 左连接：查询所有员工及其部门信息（即使没有部门）
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

-- 右连接：查询所有部门及其员工信息（即使没有员工）
SELECT 
    e.name AS '员工姓名',
    e.position AS '职位',
    d.name AS '部门名称'
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id;

-- 使用UNION模拟全外连接
SELECT 
    e.name AS '员工姓名',
    e.position AS '职位',
    d.name AS '部门名称'
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
UNION
SELECT 
    e.name AS '员工姓名',
    e.position AS '职位',
    d.name AS '部门名称'
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id
WHERE e.id IS NULL;

-- =================================
-- 6.4 自连接（SELF JOIN）示例
-- =================================

-- 自连接：查询员工及其经理信息
SELECT 
    e.name AS '员工姓名',
    e.position AS '员工职位',
    m.name AS '经理姓名',
    m.position AS '经理职位'
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id
ORDER BY e.name;

-- 查询同一部门中薪资高于其他员工的员工
SELECT 
    e1.name AS '员工姓名',
    e1.salary AS '员工薪资',
    e2.name AS '比较员工',
    e2.salary AS '比较员工薪资'
FROM employees e1
JOIN employees e2 ON e1.department_id = e2.department_id AND e1.salary > e2.salary
ORDER BY e1.name, e2.name;

-- 查找相同职位的员工
SELECT 
    e1.name AS '员工1',
    e1.position AS '职位',
    e2.name AS '员工2',
    e2.position AS '职位'
FROM employees e1
JOIN employees e2 ON e1.position = e2.position AND e1.id < e2.id
ORDER BY e1.position, e1.name;

-- =================================
-- 6.5 交叉连接（CROSS JOIN）示例
-- =================================

-- 创建颜色表
CREATE TABLE colors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL
);

INSERT INTO colors (name) VALUES ('红色'), ('蓝色'), ('绿色'), ('黄色');

-- 创建产品表
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

INSERT INTO products (name) VALUES ('T恤'), ('裤子'), ('帽子'), ('鞋子');

-- 交叉连接：生成产品与颜色的所有组合
SELECT 
    p.name AS '产品',
    c.name AS '颜色',
    CONCAT(p.name, '-', c.name) AS '产品-颜色组合'
FROM products p
CROSS JOIN colors c
ORDER BY p.name, c.name;

-- =================================
-- 6.7 标量子查询示例
-- =================================

-- 标量子查询在SELECT子句中使用
SELECT 
    name, 
    salary,
    (SELECT AVG(salary) FROM employees) AS '平均薪资',
    salary - (SELECT AVG(salary) FROM employees) AS '与平均薪资的差距'
FROM employees;

-- 标量子查询在WHERE子句中使用
SELECT name, position, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- 查询薪资最高的员工
SELECT name, position, salary
FROM employees
WHERE salary = (SELECT MAX(salary) FROM employees);

-- 标量子查询在HAVING子句中使用
SELECT 
    d.name AS '部门',
    AVG(e.salary) AS '平均薪资'
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name
HAVING AVG(e.salary) > (SELECT AVG(salary) FROM employees);

-- =================================
-- 6.8 列表子查询示例
-- =================================

-- 使用IN运算符查询技术部的员工
SELECT name, position, department_id
FROM employees
WHERE department_id IN (SELECT id FROM departments WHERE name = '技术部');

-- 查询参与项目的员工
SELECT name, position
FROM employees
WHERE id IN (SELECT DISTINCT employee_id FROM employee_projects);

-- 使用ANY运算符查询薪资大于任何市场部员工薪资的技术部员工
SELECT name, position, salary
FROM employees
WHERE department_id = 1 AND salary > ANY (
    SELECT salary FROM employees WHERE department_id = 2
);

-- 使用ALL运算符查询薪资大于所有市场部员工薪资的技术部员工
SELECT name, position, salary
FROM employees
WHERE department_id = 1 AND salary > ALL (
    SELECT salary FROM employees WHERE department_id = 2
);

-- =================================
-- 6.9 行子查询示例
-- =================================

-- 查询与张三职位和薪资相同的员工
SELECT name, position, salary
FROM employees
WHERE (position, salary) = (
    SELECT position, salary FROM employees WHERE name = '张三'
);

-- 查询与李四部门和职位相同的员工
SELECT name, department_id, position
FROM employees
WHERE (department_id, position) = (
    SELECT department_id, position FROM employees WHERE name = '李四'
);

-- 使用行子查询进行范围比较
SELECT name, position, salary, age
FROM employees
WHERE (salary, age) > (
    SELECT salary, age FROM employees WHERE name = '赵六'
);

-- =================================
-- 6.10 表子查询示例
-- =================================

-- 表子查询在FROM子句中使用
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

-- 查询薪资高于其部门平均薪资的员工
SELECT e.name, e.salary, e.department_id, d.avg_salary
FROM employees e
JOIN (
    SELECT department_id, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department_id
) AS d ON e.department_id = d.department_id
WHERE e.salary > d.avg_salary;

-- 查询各部门中薪资最高的员工
SELECT e.name, e.salary, e.department_id, d.name AS department
FROM employees e
JOIN departments d ON e.department_id = d.id
JOIN (
    SELECT department_id, MAX(salary) AS max_salary
    FROM employees
    GROUP BY department_id
) AS max_sal ON e.department_id = max_sal.department_id AND e.salary = max_sal.max_salary;

-- =================================
-- 6.11 相关子查询示例
-- =================================

-- 查询薪资高于其所在部门平均薪资的员工
SELECT 
    e1.name, 
    e1.salary, 
    e1.department_id,
    (SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department_id = e1.department_id) AS dept_avg_salary
FROM employees e1
WHERE e1.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e1.department_id
);

-- 查询每个部门中薪资最高的员工
SELECT name, salary, department_id
FROM employees e1
WHERE salary = (
    SELECT MAX(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e1.department_id
);

-- 查询每个项目中工作小时数最多的员工
SELECT e.name, p.name AS project, ep.hours_worked
FROM employees e
JOIN employee_projects ep ON e.id = ep.employee_id
JOIN projects p ON ep.project_id = p.id
WHERE ep.hours_worked = (
    SELECT MAX(ep2.hours_worked)
    FROM employee_projects ep2
    WHERE ep2.project_id = ep.project_id
);

-- =================================
-- 6.12 EXISTS和NOT EXISTS示例
-- =================================

-- EXISTS查询有员工的部门
SELECT name, location
FROM departments d
WHERE EXISTS (
    SELECT 1 FROM employees e WHERE e.department_id = d.id
);

-- NOT EXISTS查询没有员工的部门
SELECT name, location
FROM departments d
WHERE NOT EXISTS (
    SELECT 1 FROM employees e WHERE e.department_id = d.id
);

-- EXISTS查询有项目的员工
SELECT name, position
FROM employees e
WHERE EXISTS (
    SELECT 1 FROM employee_projects ep WHERE ep.employee_id = e.id
);

-- NOT EXISTS查询没有参与项目的员工
SELECT name, position
FROM employees e
WHERE NOT EXISTS (
    SELECT 1 FROM employee_projects ep WHERE ep.employee_id = e.id
);

-- EXISTS vs IN比较
-- 使用IN
SELECT name, position
FROM employees
WHERE department_id IN (SELECT id FROM departments WHERE location = '北京');

-- 使用EXISTS
SELECT e.name, e.position
FROM employees e
WHERE EXISTS (
    SELECT 1 FROM departments d WHERE d.id = e.department_id AND d.location = '北京'
);

-- =================================
-- 综合示例：复杂连接与子查询
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

-- 查询没有下属的经理
SELECT 
    e.name AS manager,
    e.position,
    d.name AS department
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.id IN (
    SELECT DISTINCT manager_id 
    FROM employees 
    WHERE manager_id IS NOT NULL
) AND NOT EXISTS (
    SELECT 1 
    FROM employees e2 
    WHERE e2.manager_id = e.id
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