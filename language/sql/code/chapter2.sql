-- 第2章：SQL数据类型与数据定义 示例代码

-- 创建数据库
CREATE DATABASE IF NOT EXISTS company_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE company_demo;

-- 删除已存在的表（用于重新运行示例）
DROP TABLE IF EXISTS employee_projects;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

-- 2.1 SQL数据类型示例

-- 创建一个包含各种数据类型的表
CREATE TABLE data_type_examples (
    -- 整数类型
    tiny_col TINYINT,
    small_col SMALLINT,
    medium_col MEDIUMINT,
    int_col INT,
    big_col BIGINT,
    
    -- 浮点类型
    float_col FLOAT,
    double_col DOUBLE,
    decimal_col DECIMAL(10, 2),
    
    -- 字符串类型
    char_col CHAR(10),
    varchar_col VARCHAR(50),
    text_col TEXT,
    
    -- 日期时间类型
    date_col DATE,
    time_col TIME,
    datetime_col DATETIME,
    timestamp_col TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    year_col YEAR,
    
    -- 布尔类型
    bool_col BOOLEAN,
    
    -- 二进制类型
    binary_col BINARY(10),
    varbinary_col VARBINARY(50)
);

-- 插入数据
INSERT INTO data_type_examples VALUES (
    10, 1000, 100000, 1000000, 1000000000,
    3.14159, 2.718281828, 12345.67,
    '固定长度', '可变长度', '这是一段文本内容',
    '2023-05-15', '14:30:00', '2023-05-15 14:30:00', '2023-05-15 14:30:00', 2023,
    TRUE,
    '1234567890', 0x48656C6C6F
);

-- 查询数据
SELECT * FROM data_type_examples;

-- 2.2 创建数据库和表示例

-- 创建部门表
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    manager_id INT,
    location VARCHAR(100),
    budget DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建员工表
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    age INT CHECK (age >= 18 AND age <= 65),
    gender ENUM('男', '女', '其他'),
    department_id INT,
    position VARCHAR(50),
    salary DECIMAL(10, 2) CHECK (salary >= 0),
    hire_date DATE NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 创建项目表
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12, 2),
    status ENUM('计划中', '进行中', '已完成', '已取消') DEFAULT '计划中',
    manager_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES employees(id)
);

-- 创建员工项目关联表
CREATE TABLE employee_projects (
    employee_id INT,
    project_id INT,
    role VARCHAR(50),
    hours_worked INT DEFAULT 0,
    start_date DATE,
    end_date DATE,
    PRIMARY KEY (employee_id, project_id),
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- 插入示例数据
INSERT INTO departments (name, location, budget) VALUES
('技术部', '北京', 1000000.00),
('市场部', '上海', 800000.00),
('人事部', '广州', 500000.00),
('财务部', '深圳', 600000.00);

INSERT INTO employees (name, age, gender, department_id, position, salary, hire_date, email, phone) VALUES
('张三', 30, '男', 1, '高级工程师', 15000.00, '2020-01-15', 'zhangsan@example.com', '13800138001'),
('李四', 28, '女', 1, '工程师', 12000.00, '2020-03-20', 'lisi@example.com', '13800138002'),
('王五', 35, '男', 2, '市场经理', 18000.00, '2019-06-10', 'wangwu@example.com', '13800138003'),
('赵六', 25, '女', 2, '市场专员', 8000.00, '2021-02-28', 'zhaoliu@example.com', '13800138004'),
('钱七', 32, '男', 3, '人事经理', 16000.00, '2019-11-05', 'qianqi@example.com', '13800138005'),
('孙八', 27, '女', 3, '人事专员', 9000.00, '2020-07-12', 'sunba@example.com', '13800138006'),
('周九', 40, '男', 4, '财务经理', 20000.00, '2018-09-15', 'zhoujiu@example.com', '13800138007'),
('吴十', 29, '女', 4, '会计', 10000.00, '2020-05-20', 'wushi@example.com', '13800138008');

-- 更新部门经理
UPDATE departments SET manager_id = 1 WHERE id = 1;
UPDATE departments SET manager_id = 3 WHERE id = 2;
UPDATE departments SET manager_id = 5 WHERE id = 3;
UPDATE departments SET manager_id = 7 WHERE id = 4;

INSERT INTO projects (name, description, start_date, end_date, budget, manager_id) VALUES
('项目A', '开发新的电商平台', '2023-01-01', '2023-12-31', 500000.00, 1),
('项目B', '市场推广活动', '2023-03-01', '2023-08-31', 200000.00, 3),
('项目C', '人力资源系统升级', '2023-04-01', '2023-09-30', 150000.00, 5),
('项目D', '财务报表自动化', '2023-02-01', '2023-07-31', 100000.00, 7);

INSERT INTO employee_projects (employee_id, project_id, role, hours_worked, start_date, end_date) VALUES
(1, 1, '项目经理', 320, '2023-01-01', '2023-12-31'),
(2, 1, '开发工程师', 400, '2023-01-01', '2023-12-31'),
(3, 2, '项目经理', 200, '2023-03-01', '2023-08-31'),
(4, 2, '市场专员', 300, '2023-03-01', '2023-08-31'),
(5, 3, '项目经理', 150, '2023-04-01', '2023-09-30'),
(6, 3, '人事专员', 200, '2023-04-01', '2023-09-30'),
(7, 4, '项目经理', 120, '2023-02-01', '2023-07-31'),
(8, 4, '会计', 180, '2023-02-01', '2023-07-31');

-- 2.3 修改表示例

-- 添加列
ALTER TABLE employees ADD COLUMN middle_name VARCHAR(50);
ALTER TABLE employees ADD COLUMN birth_date DATE AFTER age;

-- 修改列
ALTER TABLE employees MODIFY COLUMN name VARCHAR(100) NOT NULL;
ALTER TABLE employees MODIFY COLUMN salary DECIMAL(12, 2);

-- 重命名列
ALTER TABLE employees CHANGE COLUMN middle_name second_name VARCHAR(50);
ALTER TABLE employees CHANGE COLUMN age employee_age SMALLINT;

-- 删除列
ALTER TABLE employees DROP COLUMN second_name;

-- 2.4 约束与索引示例

-- 创建唯一索引
CREATE UNIQUE INDEX idx_email ON employees(email);

-- 创建普通索引
CREATE INDEX idx_name ON employees(name);

-- 创建复合索引
CREATE INDEX idx_department_salary ON employees(department_id, salary);

-- 创建全文索引
CREATE FULLTEXT INDEX idx_description ON projects(description);

-- 查看索引
SHOW INDEX FROM employees;

-- 查看表结构
DESCRIBE employees;
DESCRIBE departments;
DESCRIBE projects;
DESCRIBE employee_projects;

-- 查询数据验证
SELECT * FROM departments;
SELECT * FROM employees;
SELECT * FROM projects;
SELECT * FROM employee_projects;

-- 查询部门及其员工
SELECT d.name AS department, e.name AS employee, e.position 
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
ORDER BY d.name, e.name;

-- 查询项目及其参与员工
SELECT p.name AS project, e.name AS employee, ep.role, ep.hours_worked
FROM projects p
JOIN employee_projects ep ON p.id = ep.project_id
JOIN employees e ON ep.employee_id = e.id
ORDER BY p.name, e.name;