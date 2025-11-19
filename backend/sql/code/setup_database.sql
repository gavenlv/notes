-- 创建示例数据库
CREATE DATABASE IF NOT EXISTS sql_tutorial;

-- 使用数据库
USE sql_tutorial;

-- 创建员工表
CREATE TABLE employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    age INT,
    gender VARCHAR(10),
    department VARCHAR(50),
    position VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE,
    email VARCHAR(100),
    phone VARCHAR(20)
);

-- 创建部门表
CREATE TABLE departments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    manager_id INT,
    location VARCHAR(100),
    budget DECIMAL(12, 2)
);

-- 创建项目表
CREATE TABLE projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12, 2),
    status VARCHAR(20)
);

-- 创建员工项目关联表
CREATE TABLE employee_projects (
    employee_id INT,
    project_id INT,
    role VARCHAR(50),
    hours_worked INT,
    PRIMARY KEY (employee_id, project_id),
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- 插入部门数据
INSERT INTO departments (id, name, manager_id, location, budget) VALUES
(1, 'IT', 1, 'Building A, Floor 3', 500000.00),
(2, 'HR', 2, 'Building A, Floor 2', 200000.00),
(3, 'Finance', 4, 'Building B, Floor 1', 300000.00),
(4, 'Marketing', 7, 'Building B, Floor 2', 400000.00),
(5, 'Sales', 10, 'Building C, Floor 1', 600000.00);

-- 插入员工数据
INSERT INTO employees (id, name, age, gender, department, position, salary, hire_date, email, phone) VALUES
(1, '张三', 35, '男', 'IT', '技术总监', 85000.00, '2018-01-15', 'zhangsan@company.com', '13800138001'),
(2, '李四', 32, '女', 'HR', '人事经理', 65000.00, '2019-03-20', 'lisi@company.com', '13800138002'),
(3, '王五', 28, '男', 'IT', '高级工程师', 75000.00, '2020-05-10', 'wangwu@company.com', '13800138003'),
(4, '赵六', 40, '女', 'Finance', '财务总监', 90000.00, '2017-08-12', 'zhaoliu@company.com', '13800138004'),
(5, '钱七', 26, '男', 'IT', '软件工程师', 60000.00, '2021-02-28', 'qianqi@company.com', '13800138005'),
(6, '孙八', 30, '女', 'HR', '人事专员', 45000.00, '2021-06-15', 'sunba@company.com', '13800138006'),
(7, '周九', 38, '男', 'Marketing', '市场总监', 80000.00, '2018-11-05', 'zhoujiu@company.com', '13800138007'),
(8, '吴十', 25, '女', 'Marketing', '市场专员', 40000.00, '2022-01-10', 'wushi@company.com', '13800138008'),
(9, '郑十一', 33, '男', 'Finance', '财务经理', 70000.00, '2019-09-18', 'zhengshiyi@company.com', '13800138009'),
(10, '陈十二', 42, '女', 'Sales', '销售总监', 95000.00, '2016-12-03', 'chenshier@company.com', '13800138010'),
(11, '林十三', 29, '男', 'Sales', '销售经理', 68000.00, '2020-04-22', 'linshisan@company.com', '13800138011'),
(12, '黄十四', 27, '女', 'Sales', '销售代表', 42000.00, '2021-07-30', 'huangshisi@company.com', '13800138012');

-- 插入项目数据
INSERT INTO projects (id, name, start_date, end_date, budget, status) VALUES
(1, '公司官网改版', '2023-01-01', '2023-06-30', 150000.00, '进行中'),
(2, '客户管理系统', '2023-02-15', '2023-12-31', 300000.00, '进行中'),
(3, '财务报表系统', '2023-03-10', '2023-09-15', 200000.00, '计划中'),
(4, '市场推广活动', '2023-04-01', '2023-05-31', 80000.00, '已完成'),
(5, '员工培训计划', '2023-05-01', '2023-12-31', 120000.00, '计划中');

-- 插入员工项目关联数据
INSERT INTO employee_projects (employee_id, project_id, role, hours_worked) VALUES
(1, 1, '项目经理', 200),
(3, 1, '前端开发', 300),
(5, 1, '后端开发', 280),
(1, 2, '项目经理', 150),
(3, 2, '系统架构师', 250),
(5, 2, '后端开发', 320),
(4, 3, '项目经理', 180),
(9, 3, '业务分析师', 220),
(7, 4, '项目经理', 120),
(8, 4, '市场执行', 200),
(2, 5, '项目经理', 100),
(6, 5, '培训执行', 150),
(10, 4, '项目顾问', 50),
(11, 4, '销售支持', 80);