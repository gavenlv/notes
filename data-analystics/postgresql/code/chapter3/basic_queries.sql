-- Chapter 3: Basic SQL Syntax Examples
-- This file contains practical examples of SELECT, INSERT, UPDATE, and DELETE operations

-- 1. Create sample tables
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE DEFAULT CURRENT_DATE,
    commission DECIMAL(5, 2) DEFAULT NULL
);

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    location VARCHAR(100)
);

-- 2. Insert sample data
INSERT INTO departments (name, location) VALUES
    ('Engineering', 'Building A'),
    ('Marketing', 'Building B'),
    ('Sales', 'Building C'),
    ('HR', 'Building A'),
    ('Finance', 'Building D');

INSERT INTO employees (name, department, salary, hire_date, commission) VALUES
    ('John Doe', 'Engineering', 75000.00, '2022-01-15', 5.0),
    ('Jane Smith', 'Marketing', 65000.00, '2022-03-20', NULL),
    ('Bob Johnson', 'Sales', 70000.00, '2021-11-10', 7.5),
    ('Alice Brown', 'Engineering', 80000.00, '2020-05-01', 3.0),
    ('Charlie Wilson', 'Sales', 68000.00, '2023-02-28', 6.0),
    ('Diana Prince', 'HR', 62000.00, '2021-08-15', NULL),
    ('Edward Davis', 'Finance', 72000.00, '2022-07-12', NULL),
    ('Frank Miller', 'Engineering', 78000.00, '2020-09-30', 4.0);

-- 3. SELECT Examples
-- Query all employees
SELECT * FROM employees;

-- Query specific columns
SELECT name, department, salary FROM employees;

-- Filter with WHERE clause
SELECT * FROM employees WHERE salary > 70000;
SELECT * FROM employees WHERE department = 'Engineering';
SELECT * FROM employees WHERE department = 'Sales' AND salary > 69000;

-- Sorting with ORDER BY
SELECT * FROM employees ORDER BY name;
SELECT * FROM employees ORDER BY salary DESC;
SELECT * FROM employees ORDER BY department, salary DESC;

-- Limiting results
SELECT * FROM employees LIMIT 5;
SELECT * FROM employees LIMIT 3 OFFSET 2;

-- Removing duplicates
SELECT DISTINCT department FROM employees;

-- Using aliases
SELECT name AS employee_name, salary AS monthly_salary FROM employees;
SELECT e.name, e.department FROM employees AS e WHERE e.salary > 70000;

-- 4. Advanced SELECT with functions
-- Aggregate functions
SELECT COUNT(*) AS total_employees FROM employees;
SELECT AVG(salary) AS average_salary FROM employees;
SELECT MAX(salary) AS highest_salary FROM employees;
SELECT MIN(salary) AS lowest_salary FROM employees;
SELECT SUM(salary) AS total_payroll FROM employees;

-- String functions
SELECT UPPER(name) AS uppercase_name FROM employees;
SELECT LENGTH(name) AS name_length FROM employees;
SELECT SUBSTRING(name, 1, 5) AS name_prefix FROM employees;

-- Date functions
SELECT CURRENT_DATE AS today;
SELECT EXTRACT(YEAR FROM hire_date) AS hire_year FROM employees;

-- Conditional expressions
SELECT name, salary,
    CASE 
        WHEN salary > 75000 THEN 'High'
        WHEN salary > 65000 THEN 'Medium'
        ELSE 'Low'
    END AS salary_level
FROM employees;

-- Handling NULL values
SELECT name, COALESCE(commission, 0) AS commission FROM employees;

-- 5. INSERT Examples
-- Insert single row
INSERT INTO employees (name, department, salary) 
VALUES ('Grace Hopper', 'Engineering', 85000.00);

-- Insert multiple rows
INSERT INTO employees (name, department, salary) 
VALUES 
    ('Alan Turing', 'Engineering', 90000.00),
    ('Ada Lovelace', 'Marketing', 70000.00);

-- Insert with RETURNING
INSERT INTO employees (name, department, salary) 
VALUES ('Tim Berners-Lee', 'Engineering', 88000.00)
RETURNING id, name, hire_date;

-- 6. UPDATE Examples
-- Update single column
UPDATE employees SET department = 'IT' WHERE name = 'Grace Hopper';

-- Update multiple columns
UPDATE employees 
SET department = 'IT', salary = 82000.00 
WHERE name = 'Grace Hopper';

-- Update multiple rows
UPDATE employees 
SET salary = salary * 1.05 
WHERE department = 'Sales';

-- Update with RETURNING
UPDATE employees 
SET salary = salary * 1.03 
WHERE department = 'Engineering'
RETURNING id, name, salary;

-- 7. DELETE Examples
-- Delete specific row
DELETE FROM employees WHERE name = 'Alan Turing';

-- Delete multiple rows
DELETE FROM employees WHERE hire_date < '2021-01-01';

-- Delete with RETURNING
DELETE FROM employees WHERE department = 'Marketing'
RETURNING id, name, department;

-- 8. Practice Exercises
-- Exercise 1: Create students table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    major VARCHAR(50),
    enrollment_date DATE DEFAULT CURRENT_DATE
);

-- Exercise 2: Insert sample student data
INSERT INTO students (student_id, name, age, major) VALUES
    ('STU001', '张三', 21, '计算机科学'),
    ('STU002', '李四', 23, '数学'),
    ('STU003', '王五', 20, '计算机科学'),
    ('STU004', '赵六', 22, '物理学'),
    ('STU005', '钱七', 24, '化学');

-- Exercise 3: Query computer science students older than 20
SELECT * FROM students WHERE major = '计算机科学' AND age > 20;

-- Exercise 4: Increase all students' age by 1
UPDATE students SET age = age + 1;

-- Exercise 5: Delete students enrolled before 2022
DELETE FROM students WHERE enrollment_date < '2022-01-01';

-- Clean up (optional)
-- DROP TABLE employees;
-- DROP TABLE departments;
-- DROP TABLE students;