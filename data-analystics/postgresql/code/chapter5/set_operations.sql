-- 第5章：高级查询技术 - 集合操作示例

-- 创建示例表和数据
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER,
    salary DECIMAL(10,2),
    position VARCHAR(100)
);

-- 插入示例数据
INSERT INTO employees (name, department_id, salary, position) VALUES
('John Doe', 1, 75000, 'Developer'),
('Jane Smith', 1, 80000, 'Senior Developer'),
('Bob Johnson', 2, 65000, 'Marketer'),
('Alice Brown', 1, 85000, 'Tech Lead'),
('Charlie Wilson', 3, 70000, 'Sales Rep'),
('Diana Prince', 2, 68000, 'Marketing Manager'),
('Eve Davis', 4, 60000, 'HR Specialist'),
('Frank Miller', 1, 72000, 'Developer'),
('Grace Lee', 2, 67000, 'Marketer'),
('Henry Taylor', 3, 75000, 'Sales Manager');

-- 1. UNION
-- 查询所有经理和高薪员工（薪资大于75000）
SELECT name, 'Manager' AS role
FROM employees
WHERE position LIKE '%Manager%'
UNION
SELECT name, 'High Earner' AS role
FROM employees
WHERE salary > 75000
ORDER BY name;

-- 2. UNION ALL
-- 查询工程部和市场部的所有员工（包括重复记录）
SELECT name, 'Engineering Dept' AS department_group
FROM employees
WHERE department_id = 1
UNION ALL
SELECT name, 'High Salary Group' AS department_group
FROM employees
WHERE salary > 70000
ORDER BY name;

-- 3. INTERSECT
-- 查询既是经理又薪资超过70000的员工
SELECT name
FROM employees
WHERE position LIKE '%Manager%'
INTERSECT
SELECT name
FROM employees
WHERE salary > 70000;

-- 4. EXCEPT
-- 查询不是经理的员工
SELECT name
FROM employees
EXCEPT
SELECT name
FROM employees
WHERE position LIKE '%Manager%'
ORDER BY name;

-- 查询薪资大于70000但不是技术岗位的员工
SELECT name
FROM employees
WHERE salary > 70000
EXCEPT
SELECT name
FROM employees
WHERE position LIKE '%Developer%' OR position LIKE '%Tech%'
ORDER BY name;

-- 5. 复杂的集合操作组合
-- 查询高薪员工（不包括经理）和资深员工的并集
(
    SELECT name, salary, 'High Earner' AS category
    FROM employees
    WHERE salary > 75000
    EXCEPT
    SELECT name, salary, 'High Earner' AS category
    FROM employees
    WHERE position LIKE '%Manager%'
)
UNION
(
    SELECT name, salary, 'Senior' AS category
    FROM employees
    WHERE position LIKE 'Senior%'
)
ORDER BY name;

-- 清理示例表
DROP TABLE IF EXISTS employees;