-- 第5章：高级查询技术 - 子查询示例

-- 创建示例表和数据
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    salary DECIMAL(10,2),
    position VARCHAR(100)
);

-- 插入示例数据
INSERT INTO departments (name) VALUES 
('Engineering'), ('Marketing'), ('Sales'), ('HR');

INSERT INTO employees (name, department_id, salary, position) VALUES
('John Doe', 1, 75000, 'Developer'),
('Jane Smith', 1, 80000, 'Senior Developer'),
('Bob Johnson', 2, 65000, 'Marketer'),
('Alice Brown', 1, 85000, 'Tech Lead'),
('Charlie Wilson', 3, 70000, 'Sales Rep'),
('Diana Prince', 2, 68000, 'Marketing Manager'),
('Eve Davis', NULL, 60000, 'Intern');

-- 1. 非关联子查询
-- 查询薪资高于平均薪资的员工
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- 查询薪资最高的员工
SELECT name, salary
FROM employees
WHERE salary = (SELECT MAX(salary) FROM employees);

-- 2. 关联子查询
-- 查询每个部门薪资最高的员工
SELECT 
    e1.name,
    e1.salary,
    d.name AS department_name
FROM employees e1
INNER JOIN departments d ON e1.department_id = d.id
WHERE e1.salary = (
    SELECT MAX(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e1.department_id
);

-- 查询薪资高于所在部门平均薪资的员工
SELECT 
    e1.name,
    e1.salary,
    d.name AS department_name
FROM employees e1
INNER JOIN departments d ON e1.department_id = d.id
WHERE e1.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e1.department_id
);

-- 3. EXISTS 和 NOT EXISTS
-- 查询有员工的部门
SELECT name
FROM departments d
WHERE EXISTS (
    SELECT 1
    FROM employees e
    WHERE e.department_id = d.id
);

-- 查询没有员工的部门
-- 在这个示例中，所有部门都有员工，所以不会有结果
SELECT name
FROM departments d
WHERE NOT EXISTS (
    SELECT 1
    FROM employees e
    WHERE e.department_id = d.id
);

-- 查询至少有一个高薪员工（薪资大于80000）的部门
SELECT name
FROM departments d
WHERE EXISTS (
    SELECT 1
    FROM employees e
    WHERE e.department_id = d.id AND e.salary > 80000
);

-- 4. 在SELECT子句中使用子查询
-- 查询每个员工及其所在部门的平均薪资
SELECT 
    e.name,
    e.salary,
    (SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department_id = e.department_id) AS dept_avg_salary
FROM employees e
WHERE e.department_id IS NOT NULL;

-- 清理示例表
DROP TABLE IF EXISTS employees, departments;