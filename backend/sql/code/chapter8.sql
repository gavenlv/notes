-- 第8章：SQL高级特性示例代码

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
-- 8.1 视图（Views）示例
-- =================================

-- 创建员工基本信息视图
CREATE VIEW employee_basic_info AS
SELECT 
    id, 
    name, 
    position, 
    department_id,
    salary
FROM employees;

-- 查询视图
SELECT * FROM employee_basic_info;

-- 对视图进行条件查询
SELECT * FROM employee_basic_info WHERE salary > 10000;

-- 修改视图，添加部门名称
CREATE OR REPLACE VIEW employee_basic_info AS
SELECT 
    e.id, 
    e.name, 
    e.position, 
    d.name AS department_name,
    e.salary
FROM employees e
JOIN departments d ON e.department_id = d.id;

-- 查询修改后的视图
SELECT * FROM employee_basic_info;

-- =================================
-- 8.2 存储过程（Stored Procedures）示例
-- =================================

-- 创建根据部门ID查询员工信息的存储过程
DELIMITER //
CREATE PROCEDURE GetEmployeesByDepartment(
    IN DeptId INT
)
BEGIN
    SELECT 
        e.id,
        e.name,
        e.position,
        e.salary,
        d.name AS department
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE e.department_id = DeptId;
END //
DELIMITER ;

-- 调用存储过程
CALL GetEmployeesByDepartment(1);

-- 创建带输出参数的存储过程
DELIMITER //
CREATE PROCEDURE GetEmployeeCountByDepartment(
    IN DeptId INT,
    OUT EmployeeCount INT
)
BEGIN
    SELECT COUNT(*) INTO EmployeeCount
    FROM employees
    WHERE department_id = DeptId;
END //
DELIMITER ;

-- 调用带输出参数的存储过程
SET @Count = 0;
CALL GetEmployeeCountByDepartment(1, @Count);
SELECT @Count AS employee_count;

-- =================================
-- 8.3 函数（Functions）示例
-- =================================

-- 创建计算员工年薪的标量函数
DELIMITER //
CREATE FUNCTION CalculateAnnualSalary(
    Salary DECIMAL(10, 2),
    Bonus DECIMAL(10, 2)
) 
RETURNS DECIMAL(12, 2)
DETERMINISTIC
BEGIN
    DECLARE AnnualSalary DECIMAL(12, 2);
    SET AnnualSalary = (Salary * 12) + Bonus;
    RETURN AnnualSalary;
END //
DELIMITER ;

-- 使用标量函数
SELECT 
    name,
    salary,
    CalculateAnnualSalary(salary, 5000) AS annual_salary
FROM employees;

-- 创建表值函数
DELIMITER //
CREATE FUNCTION GetEmployeesByDepartmentFunc(
    DeptId INT
) 
RETURNS TABLE
RETURN
(
    SELECT 
        e.id,
        e.name,
        e.position,
        e.salary,
        d.name AS department
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE e.department_id = DeptId
) //
DELIMITER ;

-- 使用表值函数
SELECT * FROM GetEmployeesByDepartmentFunc(1);

-- =================================
-- 8.4 触发器（Triggers）示例
-- =================================

-- 创建薪资变更记录表
CREATE TABLE salary_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    old_salary DECIMAL(10, 2),
    new_salary DECIMAL(10, 2),
    change_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(50)
);

-- 创建记录薪资变更的触发器
DELIMITER //
CREATE TRIGGER tr_SalaryChange
AFTER UPDATE ON employees
FOR EACH ROW
BEGIN
    -- 检查是否更新了薪资
    IF OLD.salary <> NEW.salary THEN
        INSERT INTO salary_history (employee_id, old_salary, new_salary)
        VALUES (NEW.id, OLD.salary, NEW.salary);
    END IF;
END //
DELIMITER ;

-- 测试触发器：更新员工薪资
UPDATE employees SET salary = salary * 1.1 WHERE id = 1;

-- 查看薪资变更记录
SELECT * FROM salary_history;

-- =================================
-- 8.5 事务处理（Transactions）示例
-- =================================

-- 创建账户表用于转账示例
CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    balance DECIMAL(12, 2) NOT NULL
);

-- 插入账户数据
INSERT INTO accounts (name, balance) VALUES
('账户A', 10000.00),
('账户B', 5000.00);

-- 转账事务示例
START TRANSACTION;

-- 从账户A扣款
UPDATE accounts SET balance = balance - 1000 WHERE id = 1;

-- 向账户B加款
UPDATE accounts SET balance = balance + 1000 WHERE id = 2;

-- 检查操作是否成功
-- 在实际应用中，这里应该有错误检查逻辑

-- 提交事务
COMMIT;

-- 查看转账结果
SELECT * FROM accounts;

-- 回滚事务示例
START TRANSACTION;

-- 尝试转账，但账户余额不足
UPDATE accounts SET balance = balance - 20000 WHERE id = 1;

-- 检查余额是否足够
SELECT balance FROM accounts WHERE id = 1;

-- 回滚事务
ROLLBACK;

-- 查看回滚后的结果
SELECT * FROM accounts;

-- =================================
-- 8.6 游标（Cursors）示例
-- =================================

-- 使用游标更新员工薪资
DELIMITER //
CREATE PROCEDURE UpdateLowSalaryEmployees()
BEGIN
    -- 声明变量
    DECLARE done INT DEFAULT FALSE;
    DECLARE EmployeeId INT;
    DECLARE Salary DECIMAL(10, 2);
    DECLARE NewSalary DECIMAL(10, 2);
    
    -- 声明游标
    DECLARE employee_cursor CURSOR FOR
        SELECT id, salary FROM employees WHERE salary < 10000;
    
    -- 声明异常处理
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- 打开游标
    OPEN employee_cursor;
    
    -- 循环读取
    read_loop: LOOP
        -- 获取下一行
        FETCH employee_cursor INTO EmployeeId, Salary;
        
        -- 检查是否结束
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- 计算新薪资（增加10%）
        SET NewSalary = Salary * 1.1;
        
        -- 更新员工薪资
        UPDATE employees 
        SET salary = NewSalary 
        WHERE id = EmployeeId;
        
        -- 输出信息
        SELECT CONCAT('员工ID: ', EmployeeId, 
                     ', 原薪资: ', Salary, 
                     ', 新薪资: ', NewSalary) AS message;
    END LOOP;
    
    -- 关闭游标
    CLOSE employee_cursor;
END //
DELIMITER ;

-- 调用存储过程
CALL UpdateLowSalaryEmployees();

-- 查看更新后的结果
SELECT id, name, salary FROM employees WHERE salary < 11000;

-- =================================
-- 8.7 窗口函数（Window Functions）示例
-- =================================

-- ROW_NUMBER()示例
SELECT 
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;

-- RANK()示例
SELECT 
    name,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;

-- DENSE_RANK()示例
SELECT 
    name,
    salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;

-- NTILE()示例
SELECT 
    name,
    salary,
    NTILE(4) OVER (ORDER BY salary DESC) AS salary_quartile
FROM employees;

-- 聚合函数作为窗口函数
SELECT 
    e.name,
    e.salary,
    d.name AS department,
    SUM(e.salary) OVER (PARTITION BY d.id) AS dept_total_salary,
    AVG(e.salary) OVER (PARTITION BY d.id) AS dept_avg_salary
FROM employees e
JOIN departments d ON e.department_id = d.id;

-- LAG()和LEAD()示例
SELECT 
    name,
    salary,
    LAG(salary, 1, 0) OVER (ORDER BY salary DESC) AS prev_salary,
    LEAD(salary, 1, 0) OVER (ORDER BY salary DESC) AS next_salary
FROM employees;

-- FIRST_VALUE()和LAST_VALUE()示例
SELECT 
    name,
    salary,
    FIRST_VALUE(salary) OVER (ORDER BY salary DESC) AS highest_salary,
    LAST_VALUE(salary) OVER (ORDER BY salary DESC) AS lowest_salary
FROM employees;

-- =================================
-- 8.8 公用表表达式（CTE）示例
-- =================================

-- 基本CTE示例
WITH DeptMaxSalary AS (
    SELECT 
        department_id,
        MAX(salary) AS max_salary
    FROM employees
    GROUP BY department_id
)
SELECT 
    e.name,
    e.position,
    e.salary,
    d.name AS department
FROM employees e
JOIN departments d ON e.department_id = d.id
JOIN DeptMaxSalary dms ON e.department_id = dms.department_id AND e.salary = dms.max_salary;

-- 多个CTE示例
WITH DeptAvgSalary AS (
    SELECT 
        department_id,
        AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department_id
),
HighSalaryDepts AS (
    SELECT 
        department_id,
        avg_salary
    FROM DeptAvgSalary
    WHERE avg_salary > 10000
)
SELECT 
    d.name AS department,
    das.avg_salary,
    COUNT(e.id) AS employee_count
FROM departments d
JOIN DeptAvgSalary das ON d.id = das.department_id
JOIN employees e ON d.id = e.department_id
WHERE d.id IN (SELECT department_id FROM HighSalaryDepts)
GROUP BY d.id, d.name, das.avg_salary;

-- 递归CTE示例（MySQL 8.0+）
WITH RECURSIVE EmployeeHierarchy AS (
    -- 锚点查询：获取顶级员工（没有经理的员工）
    SELECT 
        id,
        name,
        position,
        manager_id,
        0 AS level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- 递归查询：获取下属员工
    SELECT 
        e.id,
        e.name,
        e.position,
        e.manager_id,
        eh.level + 1
    FROM employees e
    JOIN EmployeeHierarchy eh ON e.manager_id = eh.id
)
SELECT 
    CONCAT(REPEAT('  ', level), name) AS employee_name,
    position,
    level
FROM EmployeeHierarchy
ORDER BY level, name;

-- =================================
-- 8.9 JSON数据处理示例（MySQL 5.7+）
-- =================================

-- 创建包含JSON列的表
CREATE TABLE employee_details (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    details JSON
);

-- 插入JSON数据
INSERT INTO employee_details (id, name, details) VALUES
(1, '张三', '{"age": 30, "skills": ["Java", "Python", "SQL"], "address": {"city": "北京", "district": "朝阳区"}}'),
(2, '李四', '{"age": 28, "skills": ["JavaScript", "React", "Node.js"], "address": {"city": "上海", "district": "浦东新区"}}');

-- 查询JSON数据
SELECT 
    name,
    JSON_EXTRACT(details, '$.age') AS age,
    JSON_EXTRACT(details, '$.skills') AS skills,
    JSON_EXTRACT(details, '$.address.city') AS city
FROM employee_details;

-- 使用简化语法
SELECT 
    name,
    details->'$.age' AS age,
    details->'$.skills' AS skills,
    details->'$.address.city' AS city
FROM employee_details;

-- 提取无引号的值
SELECT 
    name,
    details->>'$.age' AS age,
    details->>'$.address.city' AS city
FROM employee_details;

-- 修改JSON数据
UPDATE employee_details
SET details = JSON_SET(details, '$.age', 31)
WHERE id = 1;

-- 添加JSON属性
UPDATE employee_details
SET details = JSON_INSERT(details, '$.email', 'zhangsan@example.com')
WHERE id = 1;

-- 删除JSON属性
UPDATE employee_details
SET details = JSON_REMOVE(details, '$.email')
WHERE id = 1;

-- 合并JSON对象
UPDATE employee_details
SET details = JSON_MERGE(details, '{"department": "技术部", "experience": 5}')
WHERE id = 1;

-- 查看修改后的结果
SELECT * FROM employee_details;

-- JSON函数示例
-- 检查JSON路径是否存在
SELECT 
    name,
    JSON_CONTAINS_PATH(details, 'one', '$.skills') AS has_skills
FROM employee_details;

-- 搜索JSON值
SELECT 
    name,
    details
FROM employee_details
WHERE JSON_CONTAINS(details, '"Java"', '$.skills');

-- 获取JSON键
SELECT 
    name,
    JSON_KEYS(details) AS keys
FROM employee_details;

-- 获取JSON数组长度
SELECT 
    name,
    JSON_LENGTH(details, '$.skills') AS skill_count
FROM employee_details;