-- 第1章示例代码

-- 创建数据库
CREATE DATABASE IF NOT EXISTS sql_tutorial;

-- 使用数据库
USE sql_tutorial;

-- 创建员工表
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    age INT,
    department VARCHAR(50),
    position VARCHAR(50),
    salary DECIMAL(10, 2)
);

-- 插入示例数据
INSERT INTO employees (id, name, age, department, position, salary) VALUES
(1, '张三', 35, 'IT', '工程师', 8000.00),
(2, '李四', 28, 'HR', '专员', 5000.00),
(3, '王五', 32, '财务', '经理', 7000.00),
(4, '赵六', 40, 'IT', '总监', 12000.00),
(5, '钱七', 26, '市场', '专员', 4500.00);

-- 查询所有数据
SELECT * FROM employees;

-- 查询姓名和薪资
SELECT name, salary FROM employees;

-- 查询员工的ID、姓名和部门
SELECT id, name, department FROM employees;

-- 查询员工的姓名、年龄和职位
SELECT name, age, position FROM employees;