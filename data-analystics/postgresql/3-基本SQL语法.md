# 第3章：PostgreSQL基本SQL语法

## 本章概述

在本章中，我们将学习PostgreSQL中最基本也是最重要的SQL语法操作，包括数据查询(SELECT)、数据插入(INSERT)、数据更新(UPDATE)和数据删除(DELETE)。这些操作构成了数据库操作的核心，掌握它们对于使用PostgreSQL至关重要。

## 内容目录

1. [SQL语言基础](#sql语言基础)
2. [SELECT语句详解](#select语句详解)
3. [INSERT语句详解](#insert语句详解)
4. [UPDATE语句详解](#update语句详解)
5. [DELETE语句详解](#delete语句详解)
6. [数据查询高级用法](#数据查询高级用法)
7. [本章小结](#本章小结)

## SQL语言基础

SQL（Structured Query Language，结构化查询语言）是用于管理和操作关系型数据库的标准语言。SQL语言主要分为以下几类：

### 1. DDL（数据定义语言）
用于定义和修改数据库结构：
- CREATE：创建数据库对象（表、索引、视图等）
- ALTER：修改数据库对象结构
- DROP：删除数据库对象
- TRUNCATE：清空表数据

### 2. DML（数据操作语言）
用于操作数据：
- SELECT：查询数据
- INSERT：插入数据
- UPDATE：更新数据
- DELETE：删除数据

### 3. DCL（数据控制语言）
用于控制数据库访问权限：
- GRANT：授予权限
- REVOKE：撤销权限

### 4. TCL（事务控制语言）
用于管理事务：
- COMMIT：提交事务
- ROLLBACK：回滚事务
- SAVEPOINT：设置保存点

## SELECT语句详解

SELECT语句用于从数据库中查询数据，是SQL中最常用的语句之一。

### 基本语法
```sql
SELECT column1, column2, ...
FROM table_name
WHERE condition
ORDER BY column_name [ASC|DESC]
LIMIT number OFFSET number;
```

### 查询所有列
```sql
-- 查询employees表中的所有数据
SELECT * FROM employees;
```

### 查询指定列
```sql
-- 只查询员工姓名和部门
SELECT name, department FROM employees;
```

### 使用WHERE子句过滤数据
```sql
-- 查询工资大于70000的员工
SELECT * FROM employees WHERE salary > 70000;

-- 查询工程部门的员工
SELECT * FROM employees WHERE department = 'Engineering';

-- 查询多个条件
SELECT * FROM employees 
WHERE department = 'Engineering' AND salary > 70000;
```

### 使用ORDER BY排序
```sql
-- 按姓名升序排列
SELECT * FROM employees ORDER BY name ASC;

-- 按工资降序排列
SELECT * FROM employees ORDER BY salary DESC;

-- 多列排序
SELECT * FROM employees 
ORDER BY department ASC, salary DESC;
```

### 使用LIMIT限制结果数量
```sql
-- 只返回前3条记录
SELECT * FROM employees LIMIT 3;

-- 跳过前2条记录，返回接下来的3条记录
SELECT * FROM employees LIMIT 3 OFFSET 2;
```

### 使用DISTINCT去重
```sql
-- 查询所有不重复的部门
SELECT DISTINCT department FROM employees;
```

### 使用AS设置别名
```sql
-- 为列设置别名
SELECT name AS employee_name, salary AS monthly_salary 
FROM employees;

-- 为表设置别名
SELECT e.name, e.department 
FROM employees AS e 
WHERE e.salary > 70000;
```

## INSERT语句详解

INSERT语句用于向表中插入新数据。

### 基本语法
```sql
INSERT INTO table_name (column1, column2, column3, ...)
VALUES (value1, value2, value3, ...);
```

### 插入单行数据
```sql
-- 插入完整数据
INSERT INTO employees (name, department, salary) 
VALUES ('Alice Johnson', 'HR', 60000.00);

-- 插入部分数据（其他列使用默认值）
INSERT INTO employees (name, department) 
VALUES ('Bob Wilson', 'Finance');
```

### 插入多行数据
```sql
INSERT INTO employees (name, department, salary) 
VALUES 
    ('Charlie Brown', 'Marketing', 65000.00),
    ('Diana Prince', 'Engineering', 80000.00),
    ('Edward Smith', 'Sales', 72000.00);
```

### 从其他表插入数据
```sql
-- 将一个表的数据插入到另一个表中
INSERT INTO archived_employees (name, department, salary, hire_date)
SELECT name, department, salary, hire_date 
FROM employees 
WHERE hire_date < '2020-01-01';
```

### 使用RETURNING获取插入的数据
```sql
-- 插入数据并返回插入的记录
INSERT INTO employees (name, department, salary) 
VALUES ('Frank Miller', 'IT', 75000.00)
RETURNING id, name, hire_date;
```

## UPDATE语句详解

UPDATE语句用于修改表中已存在的数据。

### 基本语法
```sql
UPDATE table_name
SET column1 = value1, column2 = value2, ...
WHERE condition;
```

### 更新单列数据
```sql
-- 更新指定员工的部门
UPDATE employees 
SET department = 'IT' 
WHERE name = 'Alice Johnson';
```

### 更新多列数据
```sql
-- 同时更新部门和工资
UPDATE employees 
SET department = 'IT', salary = 78000.00 
WHERE name = 'Alice Johnson';
```

### 使用条件更新多行
```sql
-- 给所有工程部门的员工涨薪10%
UPDATE employees 
SET salary = salary * 1.1 
WHERE department = 'Engineering';
```

### 使用RETURNING获取更新的数据
```sql
-- 更新数据并返回更新后的记录
UPDATE employees 
SET salary = salary * 1.05 
WHERE department = 'Sales'
RETURNING id, name, salary;
```

## DELETE语句详解

DELETE语句用于删除表中的数据。

### 基本语法
```sql
DELETE FROM table_name WHERE condition;
```

### 删除指定行
```sql
-- 删除指定员工
DELETE FROM employees 
WHERE name = 'Bob Wilson';
```

### 删除多行数据
```sql
-- 删除离职日期在指定日期之前的员工
DELETE FROM employees 
WHERE hire_date < '2020-01-01';
```

### 清空整个表（谨慎使用）
```sql
-- 删除表中所有数据（保留表结构）
DELETE FROM employees;

-- 或者使用TRUNCATE（性能更好，但不能回滚）
TRUNCATE TABLE employees;
```

### 使用RETURNING获取删除的数据
```sql
-- 删除数据并返回被删除的记录
DELETE FROM employees 
WHERE department = 'Marketing'
RETURNING id, name, department;
```

## 数据查询高级用法

### 使用函数
```sql
-- 使用聚合函数
SELECT COUNT(*) AS total_employees FROM employees;
SELECT AVG(salary) AS average_salary FROM employees;
SELECT MAX(salary) AS highest_salary FROM employees;
SELECT MIN(salary) AS lowest_salary FROM employees;
SELECT SUM(salary) AS total_payroll FROM employees;

-- 使用字符串函数
SELECT UPPER(name) AS uppercase_name FROM employees;
SELECT LENGTH(name) AS name_length FROM employees;
SELECT SUBSTRING(name, 1, 5) AS name_prefix FROM employees;

-- 使用日期函数
SELECT CURRENT_DATE AS today;
SELECT EXTRACT(YEAR FROM hire_date) AS hire_year FROM employees;
```

### 使用CASE语句
```sql
-- 根据条件返回不同值
SELECT name, salary,
    CASE 
        WHEN salary > 75000 THEN 'High'
        WHEN salary > 60000 THEN 'Medium'
        ELSE 'Low'
    END AS salary_level
FROM employees;
```

### 使用COALESCE处理空值
```sql
-- 如果commission为NULL，则返回0
SELECT name, COALESCE(commission, 0) AS commission 
FROM employees;
```

## 本章小结

通过本章的学习，您已经掌握了PostgreSQL中最基本和最重要的SQL操作：
1. SELECT语句用于查询数据，支持各种过滤、排序和限制条件
2. INSERT语句用于插入新数据，支持单行和多行插入
3. UPDATE语句用于修改现有数据，可以精确更新特定记录
4. DELETE语句用于删除数据，支持条件删除和整表清空

这些基本操作是数据库操作的核心，熟练掌握它们对于后续学习更高级的数据库功能至关重要。在实际工作中，大部分数据库操作都是基于这些基本语句的组合和扩展。

在下一章中，我们将深入学习PostgreSQL的数据类型和约束，了解如何定义表结构和确保数据完整性。

## 实践练习

1. 创建一个学生表，包含学号、姓名、年龄、专业和入学日期字段
2. 插入5条学生记录
3. 查询所有计算机专业且年龄大于20的学生
4. 将所有学生的年龄增加1岁
5. 删除入学日期在2020年之前的学生记录

## 参考资料

1. PostgreSQL官方文档 - SQL命令: https://www.postgresql.org/docs/current/sql-commands.html
2. PostgreSQL数据类型: https://www.postgresql.org/docs/current/datatype.html
3. PostgreSQL函数和操作符: https://www.postgresql.org/docs/current/functions.html