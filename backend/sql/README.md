# SQL 学习笔记

## 概述

SQL（Structured Query Language，结构化查询语言）是一种用于管理关系数据库的标准语言。SQL用于查询、插入、更新和删除数据库中的数据，以及创建和管理数据库结构。SQL是声明式语言，用户只需指定"做什么"，而不需要指定"怎么做"。SQL广泛应用于各种数据库系统，包括MySQL、PostgreSQL、Oracle、SQL Server、SQLite等。掌握SQL对于数据分析师、后端开发人员、数据库管理员等职位至关重要。

## 章节内容

本SQL学习笔记包含以下章节：

1. **[SQL基础入门](1-基础入门.md)** - SQL概述、历史、特点和基本语法
2. **[SQL数据类型与表结构](2-数据类型与数据定义.md)** - 数据类型、表的定义、约束和索引
3. **[SQL基本查询](3-基本查询.md)** - SELECT语句、WHERE条件、排序和限制结果
4. **[SQL高级查询](4-高级查询.md)** - 模式匹配、NULL值处理、CASE表达式和运算符
5. **[SQL数据操作](5-数据操作.md)** - INSERT、UPDATE、DELETE和事务处理
6. **[SQL连接与子查询](6-连接与子查询.md)** - 内连接、外连接、自连接、交叉连接和各种子查询
7. **[SQL聚合与分组](7-聚合与分组.md)** - 聚合函数、GROUP BY、HAVING和高级分组技巧
8. **[SQL高级特性](8-高级特性.md)** - 视图、存储过程、函数、触发器、事务处理和窗口函数
9. **[SQL性能优化](9-性能优化.md)** - 索引优化、查询优化、数据库设计优化和监控诊断
10. **[SQL实战应用](10-实战应用.md)** - 电商系统、社交媒体数据分析、企业人力资源管理等实际应用

## 代码示例

每个章节都配有详细的代码示例，位于[code](code/)目录中：

- [第1章代码示例](code/chapter1.sql)
- [第2章代码示例](code/chapter2.sql)
- [第3章代码示例](code/chapter3.sql)
- [第4章代码示例](code/chapter4.sql)
- [第5章代码示例](code/chapter5.sql)
- [第6章代码示例](code/chapter6.sql)
- [第7章代码示例](code/chapter7.sql)
- [第8章代码示例](code/chapter8.sql)
- [第9章代码示例](code/chapter9.sql)
- [第10章代码示例](code/chapter10.sql)

## 学习资源

我们整理了全面的SQL学习资源，包括在线学习平台、书籍推荐、练习平台等，详见[学习资源汇总](学习资源汇总.md)。

## 目录结构

```
sql/
├── basics/                 # SQL基础
│   ├── introduction.md    # SQL介绍
│   ├── database-systems.md # 数据库系统
│   ├── sql-standards.md   # SQL标准
│   ├── tools.md           # SQL工具
│   └── first-query.md     # 第一个查询
├── data-types/             # 数据类型
│   ├── numeric.md         # 数值类型
│   ├── string.md          # 字符串类型
│   ├── date-time.md       # 日期时间类型
│   ├── boolean.md         # 布尔类型
│   └── json.md            # JSON类型
├── ddl/                    # 数据定义语言
│   ├── create-database.md # 创建数据库
│   ├── create-table.md    # 创建表
│   ├── alter-table.md     # 修改表
│   ├── drop-table.md      # 删除表
│   ├── constraints.md     # 约束
│   └── indexes.md         # 索引
├── dml/                    # 数据操作语言
│   ├── insert.md          # 插入数据
│   ├── update.md          # 更新数据
│   ├── delete.md          # 删除数据
│   ├── merge.md           # 合并数据
│   └── transactions.md    # 事务
├── queries/                # 查询
│   ├── select-basic.md    # 基本查询
│   ├── where.md           # WHERE子句
│   ├── order-by.md        # ORDER BY子句
│   ├── limit-offset.md    # LIMIT和OFFSET
│   └── distinct.md        # DISTINCT
├── joins/                  # 连接
│   ├── inner-join.md      # 内连接
│   ├── left-join.md       # 左连接
│   ├── right-join.md      # 右连接
│   ├── full-join.md       # 全连接
│   ├── cross-join.md      # 交叉连接
│   └── self-join.md       # 自连接
├── aggregation/             # 聚合
│   ├── group-by.md        # GROUP BY子句
│   ├── having.md          # HAVING子句
│   ├── count.md           # COUNT函数
│   ├── sum.md             # SUM函数
│   ├── avg.md             # AVG函数
│   ├── min-max.md         # MIN和MAX函数
│   └── rollup-cube.md     # ROLLUP和CUBE
├── subqueries/             # 子查询
│   ├── basic-subquery.md  # 基本子查询
│   ├── correlated.md       # 相关子查询
│   ├── exists.md          # EXISTS子查询
│   ├── in.md              # IN子查询
│   ├── any-all.md         # ANY和ALL
│   └── derived-table.md   # 派生表
├── functions/              # 函数
│   ├── string-functions.md # 字符串函数
│   ├── numeric-functions.md # 数值函数
│   ├── date-functions.md  # 日期函数
│   ├── conditional.md     # 条件函数
│   ├── conversion.md      # 转换函数
│   └── window-functions.md # 窗口函数
├── views/                  # 视图
│   ├── create-view.md     # 创建视图
│   ├── update-view.md     # 更新视图
│   ├── materialized-view.md # 物化视图
│   └── drop-view.md       # 删除视图
├── stored-procedures/      # 存储过程
│   ├── create-procedure.md # 创建存储过程
│   ├── parameters.md      # 参数
│   ├── control-flow.md    # 控制流
│   ├── error-handling.md  # 错误处理
│   └── cursors.md         # 游标
├── triggers/               # 触发器
│   ├── create-trigger.md  # 创建触发器
│   ├── before-after.md    # BEFORE和AFTER触发器
│   ├── instead-of.md      # INSTEAD OF触发器
│   └── drop-trigger.md    # 删除触发器
├── security/               # 安全
│   ├── users.md           # 用户管理
│   ├── roles.md           # 角色管理
│   ├── privileges.md      # 权限管理
│   ├── grants.md          # 授权
│   └── encryption.md       # 加密
├── performance/             # 性能优化
│   ├── indexing.md        # 索引优化
│   ├── query-plan.md      # 查询计划
│   ├── statistics.md      # 统计信息
│   ├── partitioning.md    # 分区
│   └── optimization.md    # 优化技巧
├── advanced/               # 高级主题
│   ├── recursive-cte.md   # 递归CTE
│   ├── pivoting.md        # 数据透视
│   ├── hierarchical.md     # 层次数据
│   ├── temporal.md         # 时态数据
│   └── graph.md           # 图数据
└── databases/              # 特定数据库
    ├── mysql.md           # MySQL特性
    ├── postgresql.md      # PostgreSQL特性
    ├── oracle.md          # Oracle特性
    ├── sql-server.md      # SQL Server特性
    ├── sqlite.md          # SQLite特性
    └── nosql.md           # NoSQL对比
```

## 学习路径

### 初学者路径
1. **SQL基础** - 了解SQL的概念、历史和基本用途
2. **数据类型** - 学习SQL中的基本数据类型
3. **基本查询** - 掌握SELECT、FROM、WHERE等基本查询语法
4. **数据操作** - 学习INSERT、UPDATE、DELETE等数据操作语句
5. **简单连接** - 掌握基本的表连接操作

### 进阶路径
1. **聚合函数** - 学习GROUP BY、HAVING和聚合函数
2. **子查询** - 掌握各种类型的子查询
3. **高级连接** - 学习各种连接类型和自连接
4. **函数应用** - 掌握常用的内置函数
5. **视图和索引** - 学习创建和使用视图和索引

### 高级路径
1. **存储过程和触发器** - 学习编写存储过程和触发器
2. **事务处理** - 掌握事务的概念和使用
3. **性能优化** - 学习查询优化和索引策略
4. **高级主题** - 探索递归查询、层次数据等高级概念
5. **特定数据库特性** - 了解不同数据库系统的特有功能

## 常见问题

### Q: SQL和NoSQL有什么区别？
A: SQL和NoSQL的主要区别：
- **数据模型**：SQL使用关系模型，NoSQL使用文档、键值、列族或图模型
- **模式**：SQL通常需要预定义模式，NoSQL通常模式灵活或无模式
- **扩展性**：NoSQL通常更容易水平扩展，SQL通常垂直扩展
- **一致性**：SQL强调ACID一致性，NoSQL可能采用最终一致性
- **查询语言**：SQL使用标准SQL语言，NoSQL各有不同的查询API
- **适用场景**：SQL适合结构化数据和复杂查询，NoSQL适合大数据和高并发

### Q: 什么是SQL注入？如何防止？
A: SQL注入是一种安全漏洞：
- **定义**：攻击者通过输入恶意SQL代码来操纵数据库查询
- **危害**：可能导致数据泄露、数据篡改或数据库被控制
- **预防方法**：
  - 使用参数化查询或预编译语句
  - 对用户输入进行验证和过滤
  - 使用最小权限原则
  - 避免直接拼接SQL字符串
  - 使用ORM框架或安全的数据库访问库

### Q: 什么是数据库索引？如何优化索引？
A: 数据库索引是提高查询性能的重要工具：
- **作用**：索引类似于书的目录，加速数据检索
- **类型**：B树索引、哈希索引、全文索引等
- **优化策略**：
  - 为经常查询的列创建索引
  - 避免过多索引影响写入性能
  - 使用复合索引优化多列查询
  - 定期分析和重建索引
  - 使用覆盖索引减少表访问
  - 考虑索引的选择性和基数

## 资源链接

- [SQL标准](https://www.iso.org/standard/63555.html)
- [W3Schools SQL教程](https://www.w3schools.com/sql/)
- [SQL Fiddle - 在线SQL测试](http://sqlfiddle.com/)
- [DB-Fiddle - 在线数据库测试](https://www.db-fiddle.com/)
- [SQL Style Guide](https://www.sqlstyle.guide/)

## 代码示例

### 基本查询

```sql
-- 创建示例表
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE
);

-- 插入示例数据
INSERT INTO employees (id, name, age, department, salary, hire_date)
VALUES 
    (1, 'Alice Johnson', 30, 'IT', 75000.00, '2020-01-15'),
    (2, 'Bob Smith', 35, 'HR', 65000.00, '2018-03-22'),
    (3, 'Charlie Brown', 28, 'IT', 70000.00, '2021-06-10'),
    (4, 'Diana Prince', 32, 'Finance', 80000.00, '2019-11-05'),
    (5, 'Eva Green', 40, 'Management', 95000.00, '2015-07-18');

-- 基本SELECT查询
SELECT * FROM employees;

-- 选择特定列
SELECT name, department, salary FROM employees;

-- 使用WHERE子句过滤数据
SELECT * FROM employees WHERE department = 'IT';

-- 使用多个条件
SELECT * FROM employees 
WHERE department = 'IT' AND salary > 70000;

-- 使用OR条件
SELECT * FROM employees 
WHERE department = 'IT' OR department = 'Finance';

-- 使用IN操作符
SELECT * FROM employees 
WHERE department IN ('IT', 'Finance', 'HR');

-- 使用BETWEEN操作符
SELECT * FROM employees 
WHERE age BETWEEN 30 AND 40;

-- 使用LIKE操作符进行模式匹配
SELECT * FROM employees 
WHERE name LIKE 'A%';  -- 以A开头的名字

-- 使用ORDER BY排序
SELECT * FROM employees 
ORDER BY salary DESC;  -- 按薪资降序排列

-- 使用LIMIT限制结果数量
SELECT * FROM employees 
ORDER BY salary DESC 
LIMIT 3;  -- 只返回前3条记录

-- 使用DISTINCT去除重复值
SELECT DISTINCT department FROM employees;

-- 使用AS为列指定别名
SELECT 
    name AS 'Employee Name',
    department AS 'Department',
    salary AS 'Annual Salary'
FROM employees;

-- 使用计算列
SELECT 
    name,
    salary,
    salary * 12 AS 'Annual Salary',
    salary * 0.1 AS 'Bonus'
FROM employees;

-- 使用CASE语句创建条件列
SELECT 
    name,
    salary,
    CASE 
        WHEN salary >= 90000 THEN 'High'
        WHEN salary >= 70000 THEN 'Medium'
        ELSE 'Low'
    END AS 'Salary Level'
FROM employees;
```

### 连接查询

```sql
-- 创建部门表
CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    manager_id INT,
    location VARCHAR(100)
);

-- 插入部门数据
INSERT INTO departments (id, name, manager_id, location)
VALUES 
    (1, 'IT', 5, 'Building A'),
    (2, 'HR', 2, 'Building B'),
    (3, 'Finance', 4, 'Building A'),
    (4, 'Management', 5, 'Building C');

-- 内连接 (INNER JOIN)
SELECT 
    e.name AS employee_name,
    e.department,
    d.name AS department_name,
    d.location
FROM employees e
INNER JOIN departments d ON e.department = d.name;

-- 左连接 (LEFT JOIN)
SELECT 
    e.name AS employee_name,
    e.department,
    d.name AS department_name,
    d.location
FROM employees e
LEFT JOIN departments d ON e.department = d.name;

-- 右连接 (RIGHT JOIN)
SELECT 
    e.name AS employee_name,
    e.department,
    d.name AS department_name,
    d.location
FROM employees e
RIGHT JOIN departments d ON e.department = d.name;

-- 全连接 (FULL JOIN) - 注意：MySQL不支持FULL JOIN，可以使用UNION模拟
SELECT 
    e.name AS employee_name,
    e.department,
    d.name AS department_name,
    d.location
FROM employees e
LEFT JOIN departments d ON e.department = d.name
UNION
SELECT 
    e.name AS employee_name,
    e.department,
    d.name AS department_name,
    d.location
FROM employees e
RIGHT JOIN departments d ON e.department = d.name;

-- 自连接
SELECT 
    e1.name AS employee_name,
    e2.name AS manager_name
FROM employees e1
LEFT JOIN employees e2 ON e1.id = e2.id;

-- 多表连接
SELECT 
    e.name AS employee_name,
    e.department,
    d.name AS department_name,
    d.location,
    m.name AS manager_name
FROM employees e
LEFT JOIN departments d ON e.department = d.name
LEFT JOIN employees m ON d.manager_id = m.id;

-- 交叉连接 (CROSS JOIN)
SELECT 
    e.name AS employee_name,
    d.name AS department_name
FROM employees e
CROSS JOIN departments d;

-- 使用USING简化连接条件（当连接列名相同时）
SELECT 
    e.name,
    department
FROM employees e
JOIN departments d USING (name);

-- 使用表别名简化查询
SELECT 
    emp.name,
    emp.salary,
    dept.name AS dept_name,
    dept.location
FROM employees AS emp
JOIN departments AS dept ON emp.department = dept.name;
```

### 聚合函数和分组

```sql
-- COUNT函数 - 计算行数
SELECT COUNT(*) AS total_employees FROM employees;

SELECT COUNT(DISTINCT department) AS unique_departments FROM employees;

SELECT department, COUNT(*) AS employee_count 
FROM employees 
GROUP BY department;

-- SUM函数 - 计算总和
SELECT SUM(salary) AS total_salary FROM employees;

SELECT department, SUM(salary) AS total_salary 
FROM employees 
GROUP BY department;

-- AVG函数 - 计算平均值
SELECT AVG(salary) AS average_salary FROM employees;

SELECT department, AVG(salary) AS average_salary 
FROM employees 
GROUP BY department;

-- MIN和MAX函数 - 计算最小值和最大值
SELECT MIN(salary) AS min_salary, MAX(salary) AS max_salary FROM employees;

SELECT department, MIN(salary) AS min_salary, MAX(salary) AS max_salary 
FROM employees 
GROUP BY department;

-- GROUP BY与多个列
SELECT department, age, COUNT(*) AS count 
FROM employees 
GROUP BY department, age 
ORDER BY department, age;

-- HAVING子句 - 过滤分组结果
SELECT department, AVG(salary) AS avg_salary 
FROM employees 
GROUP BY department 
HAVING AVG(salary) > 70000;

-- 复杂聚合查询
SELECT 
    department,
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary,
    MIN(salary) AS min_salary,
    MAX(salary) AS max_salary,
    SUM(salary) AS total_salary
FROM employees 
GROUP BY department 
ORDER BY avg_salary DESC;

-- 使用ROLLUP进行多级聚合
SELECT 
    department,
    age,
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary
FROM employees 
GROUP BY department, age WITH ROLLUP;

-- 使用CUBE进行多维聚合（MySQL不支持，其他数据库可能支持）
SELECT 
    department,
    age,
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary
FROM employees 
GROUP BY CUBE (department, age);

-- 使用GROUPING SETS指定特定分组组合（MySQL不支持，其他数据库可能支持）
SELECT 
    department,
    age,
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary
FROM employees 
GROUP BY GROUPING SETS ((department), (age), (department, age), ());
```

### 子查询

```sql
-- 基本子查询
SELECT name, salary 
FROM employees 
WHERE salary > (SELECT AVG(salary) FROM employees);

-- 使用IN的子查询
SELECT name, department 
FROM employees 
WHERE department IN (SELECT name FROM departments WHERE location = 'Building A');

-- 使用ANY的子查询
SELECT name, salary 
FROM employees 
WHERE salary > ANY (SELECT salary FROM employees WHERE department = 'IT');

-- 使用ALL的子查询
SELECT name, salary 
FROM employees 
WHERE salary > ALL (SELECT salary FROM employees WHERE department = 'HR');

-- 相关子查询
SELECT 
    e1.name,
    e1.salary,
    (SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department = e1.department) AS avg_dept_salary
FROM employees e1;

-- EXISTS子查询
SELECT name, department 
FROM employees e
WHERE EXISTS (
    SELECT 1 FROM departments d 
    WHERE d.name = e.department AND d.location = 'Building A'
);

-- NOT EXISTS子查询
SELECT name, department 
FROM employees e
WHERE NOT EXISTS (
    SELECT 1 FROM departments d 
    WHERE d.name = e.department
);

-- 派生表（FROM子句中的子查询）
SELECT 
    dept_name,
    avg_salary,
    CASE 
        WHEN avg_salary > 80000 THEN 'High'
        WHEN avg_salary > 60000 THEN 'Medium'
        ELSE 'Low'
    END AS salary_level
FROM (
    SELECT 
        department AS dept_name,
        AVG(salary) AS avg_salary
    FROM employees 
    GROUP BY department
) AS dept_avg;

-- CTE (Common Table Expression) - 公共表表达式
WITH dept_avg AS (
    SELECT 
        department,
        AVG(salary) AS avg_salary
    FROM employees 
    GROUP BY department
)
SELECT 
    e.name,
    e.department,
    e.salary,
    d.avg_salary,
    e.salary - d.avg_salary AS salary_difference
FROM employees e
JOIN dept_avg d ON e.department = d.department
WHERE e.salary > d.avg_salary;

-- 多个CTE
WITH dept_avg AS (
    SELECT 
        department,
        AVG(salary) AS avg_salary
    FROM employees 
    GROUP BY department
),
high_salary_employees AS (
    SELECT 
        name,
        department,
        salary
    FROM employees 
    WHERE salary > 70000
)
SELECT 
    h.name,
    h.department,
    h.salary,
    d.avg_salary
FROM high_salary_employees h
JOIN dept_avg d ON h.department = d.department
ORDER BY h.salary DESC;

-- 递归CTE（层次数据查询）
WITH RECURSIVE employee_hierarchy AS (
    -- 基础查询：选择顶级员工（经理）
    SELECT id, name, department, salary, 0 AS level
    FROM employees
    WHERE id IN (SELECT manager_id FROM departments)
    
    UNION ALL
    
    -- 递归查询：选择下属员工
    SELECT 
        e.id, 
        e.name, 
        e.department, 
        e.salary, 
        eh.level + 1
    FROM employees e
    JOIN employee_hierarchy eh ON e.id = eh.id
    WHERE eh.level < 5  -- 限制递归深度
)
SELECT 
    name,
    department,
    salary,
    level,
    REPEAT('  ', level) || name AS indented_name
FROM employee_hierarchy
ORDER BY level, name;
```

### 窗口函数

```sql
-- ROW_NUMBER() - 为每行分配一个唯一的序号
SELECT 
    name,
    department,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;

-- 按部门分组排名
SELECT 
    name,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
FROM employees;

-- RANK() - 排名，相同值有相同排名
SELECT 
    name,
    department,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;

-- DENSE_RANK() - 密集排名，相同值有相同排名，但不跳过后续排名
SELECT 
    name,
    department,
    salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;

-- NTILE() - 将行分成指定数量的组
SELECT 
    name,
    department,
    salary,
    NTILE(4) OVER (ORDER BY salary DESC) AS salary_quartile
FROM employees;

-- LAG() - 获取前一行的值
SELECT 
    name,
    salary,
    LAG(salary, 1, 0) OVER (ORDER BY salary DESC) AS prev_salary,
    salary - LAG(salary, 1, 0) OVER (ORDER BY salary DESC) AS salary_diff
FROM employees;

-- LEAD() - 获取后一行的值
SELECT 
    name,
    salary,
    LEAD(salary, 1, 0) OVER (ORDER BY salary DESC) AS next_salary,
    LEAD(salary, 1, 0) OVER (ORDER BY salary DESC) - salary AS next_diff
FROM employees;

-- FIRST_VALUE() 和 LAST_VALUE() - 获取分组中的第一个和最后一个值
SELECT 
    name,
    department,
    salary,
    FIRST_VALUE(salary) OVER (PARTITION BY department ORDER BY salary DESC) AS highest_dept_salary,
    LAST_VALUE(salary) OVER (PARTITION BY department ORDER BY salary DESC 
                             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS lowest_dept_salary
FROM employees;

-- 聚合窗口函数
SELECT 
    name,
    department,
    salary,
    AVG(salary) OVER (PARTITION BY department) AS avg_dept_salary,
    salary - AVG(salary) OVER (PARTITION BY department) AS salary_diff_from_avg,
    SUM(salary) OVER (PARTITION BY department ORDER BY salary DESC 
                     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM employees;

-- 窗口框架子句
SELECT 
    name,
    salary,
    AVG(salary) OVER (ORDER BY salary DESC 
                     ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS moving_avg,
    SUM(salary) OVER (ORDER BY salary DESC 
                     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM employees;

-- 复杂窗口函数示例
WITH ranked_employees AS (
    SELECT 
        name,
        department,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank,
        COUNT(*) OVER (PARTITION BY department) AS dept_count,
        AVG(salary) OVER (PARTITION BY department) AS dept_avg,
        salary - AVG(salary) OVER (PARTITION BY department) AS salary_diff
    FROM employees
)
SELECT 
    name,
    department,
    salary,
    dept_rank,
    dept_count,
    dept_avg,
    salary_diff,
    CASE 
        WHEN dept_rank <= 2 THEN 'Top Performer'
        WHEN salary_diff > 10000 THEN 'Above Average'
        WHEN salary_diff < -10000 THEN 'Below Average'
        ELSE 'Average'
    END AS performance_category
FROM ranked_employees
ORDER BY department, dept_rank;
```

### 事务处理

```sql
-- 开始事务
START TRANSACTION;

-- 或者使用 BEGIN
BEGIN;

-- 执行一系列SQL操作
INSERT INTO employees (id, name, age, department, salary, hire_date)
VALUES (6, 'Frank Miller', 45, 'IT', 85000.00, '2022-02-28');

UPDATE employees 
SET salary = salary * 1.05 
WHERE department = 'IT';

DELETE FROM employees 
WHERE age > 60;

-- 检查操作结果
SELECT COUNT(*) FROM employees WHERE department = 'IT';

-- 提交事务
COMMIT;

-- 或者回滚事务
-- ROLLBACK;

-- 保存点示例
START TRANSACTION;

INSERT INTO employees (id, name, age, department, salary, hire_date)
VALUES (7, 'Grace Lee', 38, 'Finance', 72000.00, '2023-01-15');

-- 设置保存点
SAVEPOINT after_insert;

UPDATE employees 
SET salary = salary * 1.03 
WHERE department = 'Finance';

-- 检查更新结果
SELECT name, salary FROM employees WHERE department = 'Finance';

-- 决定回滚到保存点
ROLLBACK TO SAVEPOINT after_insert;

-- 提交事务（只保留插入操作）
COMMIT;

-- 隔离级别设置
-- 查看当前隔离级别
SELECT @@transaction_isolation;

-- 设置隔离级别
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 事务隔离级别示例
-- 会话1
START TRANSACTION;
UPDATE employees SET salary = salary * 1.1 WHERE id = 1;
-- 不提交，保持事务打开

-- 会话2（在不同隔离级别下行为不同）
-- READ UNCOMMITTED: 可以看到未提交的更改（脏读）
-- READ COMMITTED: 看不到未提交的更改，但可以看到已提交的更改
-- REPEATABLE READ: 在同一事务中多次读取结果一致
-- SERIALIZABLE: 完全隔离，行为如同串行执行

-- 死锁示例
-- 会话1
START TRANSACTION;
UPDATE employees SET salary = 90000 WHERE id = 1;
-- 等待会话2释放资源

-- 会话2
START TRANSACTION;
UPDATE employees SET salary = 80000 WHERE id = 2;
-- 尝试更新会话1锁定的行
UPDATE employees SET salary = 85000 WHERE id = 1;
-- 可能导致死锁

-- 自动提交设置
-- 查看自动提交状态
SELECT @@autocommit;

-- 禁用自动提交
SET autocommit = 0;

-- 启用自动提交
SET autocommit = 1;
```

## 最佳实践

1. **查询编写**
   - 使用有意义的表和列别名
   - 避免使用SELECT *，只查询需要的列
   - 使用适当的WHERE条件过滤数据
   - 考虑查询的可读性和维护性

2. **性能优化**
   - 为经常查询的列创建索引
   - 避免在WHERE子句中对列使用函数
   - 使用EXISTS代替IN处理大数据集
   - 定期分析和优化查询计划

3. **数据完整性**
   - 使用适当的约束确保数据完整性
   - 正确使用外键约束
   - 考虑使用触发器实现复杂业务规则
   - 定期备份数据

4. **安全性**
   - 使用参数化查询防止SQL注入
   - 实施最小权限原则
   - 对敏感数据进行加密
   - 定期审计数据库访问

5. **事务管理**
   - 保持事务简短
   - 正确处理事务错误
   - 选择适当的隔离级别
   - 避免长时间锁定资源

## 贡献指南

欢迎对本学习笔记进行贡献！请遵循以下指南：

1. 确保内容准确、清晰、实用
2. 使用规范的Markdown格式
3. 代码示例需要完整且可运行
4. 添加适当的注释和说明
5. 保持目录结构的一致性

## 注意事项

- 注意不同数据库系统的SQL语法差异
- 考虑SQL的版本兼容性
- 注意SQL的性能影响
- 考虑数据的安全性和隐私
- 注意事务的ACID特性

---

*最后更新: 2023年*