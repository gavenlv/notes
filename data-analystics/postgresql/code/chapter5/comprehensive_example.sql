-- 第5章：高级查询技术 - 综合示例

-- 创建示例表结构
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    salary DECIMAL(10,2),
    hire_date DATE,
    position VARCHAR(100)
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    start_date DATE,
    end_date DATE
);

CREATE TABLE employee_projects (
    employee_id INTEGER REFERENCES employees(id),
    project_id INTEGER REFERENCES projects(id),
    hours_worked INTEGER,
    assignment_date DATE,
    PRIMARY KEY (employee_id, project_id)
);

-- 插入示例数据
INSERT INTO departments (name) VALUES 
('Engineering'), ('Marketing'), ('Sales'), ('HR');

INSERT INTO employees (name, department_id, salary, hire_date, position) VALUES
('John Doe', 1, 75000, '2020-01-15', 'Developer'),
('Jane Smith', 1, 80000, '2019-03-20', 'Senior Developer'),
('Bob Johnson', 2, 65000, '2021-05-10', 'Marketer'),
('Alice Brown', 1, 85000, '2018-07-01', 'Tech Lead'),
('Charlie Wilson', 3, 70000, '2020-11-28', 'Sales Rep'),
('Diana Prince', 2, 68000, '2019-09-15', 'Marketing Manager'),
('Eve Davis', 4, 60000, '2021-02-01', 'HR Specialist'),
('Frank Miller', 1, 72000, '2020-06-10', 'Developer'),
('Grace Lee', 2, 67000, '2021-01-20', 'Marketer'),
('Henry Taylor', 3, 75000, '2019-12-05', 'Sales Manager');

INSERT INTO projects (name, department_id, start_date, end_date) VALUES
('Project Alpha', 1, '2023-01-01', '2023-06-30'),
('Project Beta', 1, '2023-02-01', '2023-08-31'),
('Project Gamma', 2, '2023-03-01', '2023-09-30'),
('Project Delta', 3, '2023-04-01', '2023-10-31'),
('Project Epsilon', 1, '2023-05-01', '2023-11-30');

INSERT INTO employee_projects (employee_id, project_id, hours_worked, assignment_date) VALUES
(1, 1, 120, '2023-01-01'),
(1, 2, 80, '2023-02-01'),
(2, 1, 100, '2023-01-01'),
(3, 3, 90, '2023-03-01'),
(4, 1, 150, '2023-01-01'),
(5, 4, 110, '2023-04-01'),
(6, 3, 85, '2023-03-01'),
(7, 5, 70, '2023-05-01'),
(8, 2, 95, '2023-02-01'),
(9, 3, 75, '2023-03-01');

-- 综合查询示例

-- 1. 查询每个部门的员工数量和平均薪资，包括没有员工的部门
SELECT 
    d.name AS department_name,
    COUNT(e.id) AS employee_count,
    COALESCE(ROUND(AVG(e.salary), 2), 0) AS avg_salary
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name
ORDER BY avg_salary DESC;

-- 2. 查询参与项目的员工及其总工时，只显示工时超过100的员工
SELECT 
    e.name AS employee_name,
    d.name AS department_name,
    SUM(ep.hours_worked) AS total_hours
FROM employees e
JOIN employee_projects ep ON e.id = ep.employee_id
JOIN departments d ON e.department_id = d.id
GROUP BY e.id, e.name, d.name
HAVING SUM(ep.hours_worked) > 100
ORDER BY total_hours DESC;

-- 3. 使用窗口函数查询每个部门薪资排名前三的员工
WITH ranked_employees AS (
    SELECT 
        e.name,
        d.name AS department_name,
        e.salary,
        ROW_NUMBER() OVER (PARTITION BY d.id ORDER BY e.salary DESC) AS salary_rank
    FROM employees e
    JOIN departments d ON e.department_id = d.id
)
SELECT 
    name,
    department_name,
    salary,
    salary_rank
FROM ranked_employees
WHERE salary_rank <= 3
ORDER BY department_name, salary_rank;

-- 4. 查询各部门薪资最高的员工（使用子查询）
SELECT 
    e.name,
    d.name AS department_name,
    e.salary
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.salary = (
    SELECT MAX(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e.department_id
)
ORDER BY e.salary DESC;

-- 5. 使用集合操作查询高薪员工和项目负责人
WITH high_earners AS (
    SELECT DISTINCT e.name, 'High Earner' AS category
    FROM employees e
    WHERE e.salary > 75000
),
project_leads AS (
    SELECT DISTINCT e.name, 'Project Lead' AS category
    FROM employees e
    JOIN employee_projects ep ON e.id = ep.employee_id
    JOIN projects p ON ep.project_id = p.id
    WHERE e.id IN (
        SELECT ep2.employee_id
        FROM employee_projects ep2
        WHERE ep2.project_id = p.id
        ORDER BY ep2.assignment_date
        LIMIT 1
    )
)
SELECT name, category FROM high_earners
UNION
SELECT name, category FROM project_leads
ORDER BY name;

-- 6. 复杂查询：查询每个项目的信息，包括项目经理、参与员工数、总工时和平均工时
SELECT 
    p.name AS project_name,
    d.name AS department_name,
    mgr.name AS project_manager,
    proj_stats.employee_count,
    proj_stats.total_hours,
    ROUND(proj_stats.avg_hours, 2) AS avg_hours_per_employee
FROM projects p
JOIN departments d ON p.department_id = d.id
LEFT JOIN (
    -- 获取项目经理（最早分配到项目的员工）
    SELECT 
        ep.project_id,
        e.name
    FROM employee_projects ep
    JOIN employees e ON ep.employee_id = e.id
    WHERE (ep.project_id, ep.assignment_date) IN (
        SELECT project_id, MIN(assignment_date)
        FROM employee_projects
        GROUP BY project_id
    )
) mgr ON p.id = mgr.project_id
LEFT JOIN (
    -- 计算项目统计信息
    SELECT 
        project_id,
        COUNT(employee_id) AS employee_count,
        SUM(hours_worked) AS total_hours,
        AVG(hours_worked) AS avg_hours
    FROM employee_projects
    GROUP BY project_id
) proj_stats ON p.id = proj_stats.project_id
ORDER BY p.start_date;

-- 7. 查询员工参与项目的详细信息，包括项目名称、工时和在项目中的排名
SELECT 
    e.name AS employee_name,
    p.name AS project_name,
    ep.hours_worked,
    RANK() OVER (PARTITION BY p.id ORDER BY ep.hours_worked DESC) AS hours_rank_in_project,
    ROUND(
        ep.hours_worked * 100.0 / SUM(ep.hours_worked) OVER (PARTITION BY p.id), 
        2
    ) AS pct_of_project_hours
FROM employee_projects ep
JOIN employees e ON ep.employee_id = e.id
JOIN projects p ON ep.project_id = p.id
ORDER BY p.name, hours_rank_in_project;

-- 清理示例表
-- DROP TABLE IF EXISTS employee_projects, projects, employees, departments;