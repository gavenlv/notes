-- 第3章：SQL基本查询 示例代码

-- 创建数据库
CREATE DATABASE IF NOT EXISTS company_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE company_demo;

-- 删除已存在的表（用于重新运行示例）
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

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
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 插入部门数据
INSERT INTO departments (name, location, budget) VALUES
('技术部', '北京', 1000000.00),
('市场部', '上海', 800000.00),
('人事部', '广州', 500000.00),
('财务部', '深圳', 600000.00);

-- 插入员工数据
INSERT INTO employees (name, age, gender, department_id, position, salary, hire_date, email, phone) VALUES
('张三', 30, '男', 1, '高级工程师', 15000.00, '2020-01-15', 'zhangsan@example.com', '13800138001'),
('李四', 28, '女', 1, '工程师', 12000.00, '2020-03-20', 'lisi@example.com', '13800138002'),
('王五', 35, '男', 2, '市场经理', 18000.00, '2019-06-10', 'wangwu@example.com', '13800138003'),
('赵六', 25, '女', 2, '市场专员', 8000.00, '2021-02-28', 'zhaoliu@example.com', '13800138004'),
('钱七', 32, '男', 3, '人事经理', 16000.00, '2019-11-05', 'qianqi@example.com', '13800138005'),
('孙八', 27, '女', 3, '人事专员', 9000.00, '2020-07-12', 'sunba@example.com', '13800138006'),
('周九', 40, '男', 4, '财务经理', 20000.00, '2018-09-15', 'zhoujiu@example.com', '13800138007'),
('吴十', 29, '女', 4, '会计', 10000.00, '2020-05-20', 'wushi@example.com', '13800138008');

-- 3.1 SELECT语句基础示例

-- 查询所有员工的所有信息
SELECT * FROM employees;

-- 查询员工的姓名、职位和薪资
SELECT name, position, salary FROM employees;

-- 使用别名查询
SELECT name AS '员工姓名', position AS '职位', salary AS '薪资' FROM employees;

-- 查询部门的所有信息
SELECT * FROM departments;

-- 查询部门的名称和位置
SELECT name, location FROM departments;

-- 3.2 WHERE子句示例

-- 查询薪资大于12000的员工
SELECT name, position, salary FROM employees WHERE salary > 12000;

-- 查询年龄小于30的员工
SELECT name, age, position FROM employees WHERE age < 30;

-- 查询职位为'工程师'的员工
SELECT name, position, department_id FROM employees WHERE position = '工程师';

-- 查询部门ID不等于1的员工
SELECT name, department_id FROM employees WHERE department_id <> 1;

-- 查询薪资大于12000且年龄小于35的员工
SELECT name, age, salary FROM employees WHERE salary > 12000 AND age < 35;

-- 查询部门ID为1或2的员工
SELECT name, department_id FROM employees WHERE department_id = 1 OR department_id = 2;

-- 查询部门ID不为1的员工（使用NOT）
SELECT name, department_id FROM employees WHERE NOT department_id = 1;

-- 复合条件：查询薪资大于10000且（部门ID为1或2）的员工
SELECT name, salary, department_id FROM employees 
WHERE salary > 10000 AND (department_id = 1 OR department_id = 2);

-- 查询年龄在25到30之间的员工
SELECT name, age FROM employees WHERE age BETWEEN 25 AND 30;

-- 查询薪资在10000到15000之间的员工
SELECT name, salary FROM employees WHERE salary BETWEEN 10000 AND 15000;

-- 查询入职日期在2020年之间的员工
SELECT name, hire_date FROM employees WHERE hire_date BETWEEN '2020-01-01' AND '2020-12-31';

-- 查询部门ID为1、2或3的员工
SELECT name, department_id FROM employees WHERE department_id IN (1, 2, 3);

-- 查询职位为'工程师'或'市场专员'的员工
SELECT name, position FROM employees WHERE position IN ('工程师', '市场专员');

-- 使用NOT IN
SELECT name, department_id FROM employees WHERE department_id NOT IN (1, 2);

-- 查询姓名以'张'开头的员工
SELECT name FROM employees WHERE name LIKE '张%';

-- 查询姓名以'三'结尾的员工
SELECT name FROM employees WHERE name LIKE '%三';

-- 查询姓名包含'五'的员工
SELECT name FROM employees WHERE name LIKE '%五%';

-- 查询姓名第二个字为'五'的员工
SELECT name FROM employees WHERE name LIKE '_五%';

-- 查询姓名为三个字且第二个字为'五'的员工
SELECT name FROM employees WHERE name LIKE '_五_';

-- 使用NOT LIKE
SELECT name FROM employees WHERE name NOT LIKE '张%';

-- 3.3 ORDER BY子句示例

-- 按薪资升序排序（默认）
SELECT name, salary FROM employees ORDER BY salary;

-- 按薪资降序排序
SELECT name, salary FROM employees ORDER BY salary DESC;

-- 按年龄升序排序
SELECT name, age FROM employees ORDER BY age ASC;

-- 先按部门ID升序，再按薪资降序排序
SELECT name, department_id, salary FROM employees ORDER BY department_id, salary DESC;

-- 先按职位升序，再按年龄降序排序
SELECT name, position, age FROM employees ORDER BY position, age DESC;

-- 按列位置排序
SELECT name, age, salary FROM employees ORDER BY 1; -- 按第一列（name）排序
SELECT name, age, salary FROM employees ORDER BY 3 DESC; -- 按第三列（salary）降序排序

-- 3.4 LIMIT子句示例

-- 只获取前5条记录
SELECT name, position, salary FROM employees LIMIT 5;

-- 获取薪资最高的3名员工
SELECT name, position, salary FROM employees ORDER BY salary DESC LIMIT 3;

-- 分页查询：第1页，每页3条记录
SELECT name, position, salary FROM employees LIMIT 0, 3;

-- 分页查询：第2页，每页3条记录
SELECT name, position, salary FROM employees LIMIT 3, 3;

-- 分页查询：第3页，每页2条记录
SELECT name, position, salary FROM employees LIMIT 4, 2;

-- 3.5 数据处理与转换示例

-- 字符串函数示例
-- 连接字符串
SELECT CONCAT(name, '(', position, ')') AS '员工信息' FROM employees;

-- 转换为大写
SELECT UPPER(name) AS '大写姓名' FROM employees;

-- 转换为小写
SELECT LOWER(name) AS '小写姓名' FROM employees;

-- 获取姓名长度
SELECT name, LENGTH(name) AS '姓名长度' FROM employees;

-- 提取子字符串（从第1个字符开始，取2个字符）
SELECT name, SUBSTRING(name, 1, 2) AS '姓氏' FROM employees;

-- 替换字符串
SELECT REPLACE(name, '张', '王') AS '替换后姓名' FROM employees;

-- 数值函数示例
-- 计算年薪（月薪*12）
SELECT name, salary, salary * 12 AS '年薪' FROM employees;

-- 计算薪资的千位数
SELECT name, salary, FLOOR(salary/1000) AS '薪资千位数' FROM employees;

-- 计算薪资的百分比（相对于最高薪资）
SELECT name, salary, ROUND(salary / (SELECT MAX(salary) FROM employees) * 100, 2) AS '薪资百分比' FROM employees;

-- 计算年龄除以10的余数
SELECT name, age, MOD(age, 10) AS '年龄余数' FROM employees;

-- 日期时间函数示例
-- 获取当前日期和时间
SELECT NOW() AS '当前日期时间', CURDATE() AS '当前日期', CURTIME() AS '当前时间';

-- 提取年、月、日
SELECT name, hire_date, YEAR(hire_date) AS '入职年份', 
       MONTH(hire_date) AS '入职月份', DAY(hire_date) AS '入职日期' 
FROM employees;

-- 计算工作天数
SELECT name, hire_date, DATEDIFF(NOW(), hire_date) AS '工作天数' FROM employees;

-- 格式化日期
SELECT name, DATE_FORMAT(hire_date, '%Y年%m月%d日') AS '格式化入职日期' FROM employees;

-- 条件表达式示例
-- 使用简单CASE表达式
SELECT name, position,
    CASE position
        WHEN '高级工程师' THEN '技术专家'
        WHEN '工程师' THEN '技术人员'
        WHEN '市场经理' THEN '管理人员'
        ELSE '其他人员'
    END AS '人员类别'
FROM employees;

-- 使用搜索CASE表达式
SELECT name, salary,
    CASE
        WHEN salary >= 15000 THEN '高薪'
        WHEN salary >= 10000 THEN '中薪'
        ELSE '普通薪资'
    END AS '薪资等级'
FROM employees;

-- 使用IF函数
SELECT name, salary,
    IF(salary >= 12000, '高薪', '普通薪资') AS '薪资等级'
FROM employees;

-- 使用IFNULL函数
SELECT name, phone, IFNULL(phone, '未提供') AS '联系电话' FROM employees;

-- 综合示例
-- 查询薪资大于10000的员工，按薪资降序排序，只显示前5名
SELECT name, position, salary,
    CASE
        WHEN salary >= 15000 THEN '高薪'
        WHEN salary >= 12000 THEN '中高薪'
        ELSE '普通薪资'
    END AS '薪资等级',
    CONCAT(name, '(', position, ')') AS '员工信息'
FROM employees
WHERE salary > 10000
ORDER BY salary DESC
LIMIT 5;