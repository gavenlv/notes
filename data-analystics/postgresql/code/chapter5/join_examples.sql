-- 第5章：高级查询技术 - 连接查询示例

-- 创建示例表和数据
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    salary DECIMAL(10,2)
);

-- 插入示例数据
INSERT INTO departments (name) VALUES 
('Engineering'), ('Marketing'), ('Sales'), ('HR');

INSERT INTO employees (name, department_id, salary) VALUES
('John Doe', 1, 75000),
('Jane Smith', 1, 80000),
('Bob Johnson', 2, 65000),
('Alice Brown', 1, 85000),
('Charlie Wilson', 3, 70000),
('Diana Prince', 2, 68000),
('Eve Davis', NULL, 60000);  -- 未分配部门的员工

-- 1. 内连接 (INNER JOIN)
-- 查询员工及其所属部门信息
SELECT 
    e.name AS employee_name,
    e.salary,
    d.name AS department_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;

-- 2. 左连接 (LEFT JOIN)
-- 查询所有员工及其部门信息（包括未分配部门的员工）
SELECT 
    e.name AS employee_name,
    e.salary,
    d.name AS department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- 3. 右连接 (RIGHT JOIN)
-- 查询所有部门及其员工信息（包括没有员工的部门）
-- 注意：在这个示例中，所有部门都有员工，所以效果与INNER JOIN相同
SELECT 
    e.name AS employee_name,
    e.salary,
    d.name AS department_name
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id;

-- 4. 全外连接 (FULL OUTER JOIN)
-- 查询所有员工和部门信息
SELECT 
    e.name AS employee_name,
    e.salary,
    d.name AS department_name
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.id;

-- 5. 交叉连接 (CROSS JOIN)
-- 创建一个简单的颜色表用于演示
CREATE TABLE colors (
    id SERIAL PRIMARY KEY,
    color_name VARCHAR(50)
);

INSERT INTO colors (color_name) VALUES 
('Red'), ('Blue'), ('Green');

-- 生成产品和颜色的所有可能组合
SELECT 
    d.name AS department_name,
    c.color_name
FROM departments d
CROSS JOIN colors c;

-- 清理示例表
DROP TABLE IF EXISTS employees, departments, colors;