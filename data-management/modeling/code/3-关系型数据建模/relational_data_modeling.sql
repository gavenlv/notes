-- =============================================
-- 关系型数据建模完整示例
-- 企业人力资源管理系统
-- =============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS HRManagement;
USE HRManagement;

-- =============================================
-- 1. 表结构设计
-- =============================================

-- 部门表
CREATE TABLE IF NOT EXISTS Department (
    DepartmentID INT PRIMARY KEY AUTO_INCREMENT,
    DepartmentName VARCHAR(50) NOT NULL,
    ManagerID INT,
    Location VARCHAR(100),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 职位表
CREATE TABLE IF NOT EXISTS Position (
    PositionID INT PRIMARY KEY AUTO_INCREMENT,
    PositionName VARCHAR(50) NOT NULL,
    Description TEXT,
    SalaryRangeMin DECIMAL(10, 2) NOT NULL CHECK (SalaryRangeMin > 0),
    SalaryRangeMax DECIMAL(10, 2) NOT NULL CHECK (SalaryRangeMax > SalaryRangeMin),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 员工表
CREATE TABLE IF NOT EXISTS Employee (
    EmployeeID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(20),
    HireDate DATE NOT NULL,
    DepartmentID INT,
    PositionID INT,
    ManagerID INT,
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID) ON DELETE SET NULL,
    FOREIGN KEY (PositionID) REFERENCES Position(PositionID) ON DELETE SET NULL,
    FOREIGN KEY (ManagerID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL
);

-- 更新部门表的外键约束（由于存在循环引用，需要先创建表再添加约束）
ALTER TABLE Department 
ADD FOREIGN KEY (ManagerID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL;

-- 工资表
CREATE TABLE IF NOT EXISTS Salary (
    SalaryID INT PRIMARY KEY AUTO_INCREMENT,
    EmployeeID INT NOT NULL,
    EffectiveDate DATE NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL CHECK (Amount > 0),
    Currency VARCHAR(10) DEFAULT 'USD',
    Notes TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE,
    UNIQUE KEY (EmployeeID, EffectiveDate) -- 确保每个员工在同一日期只有一个工资记录
);

-- 考勤表
CREATE TABLE IF NOT EXISTS Attendance (
    AttendanceID INT PRIMARY KEY AUTO_INCREMENT,
    EmployeeID INT NOT NULL,
    AttendanceDate DATE NOT NULL,
    Status ENUM('Present', 'Absent', 'Late', 'Leave') NOT NULL,
    HoursWorked DECIMAL(5, 2),
    Notes TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE,
    UNIQUE KEY (EmployeeID, AttendanceDate) -- 确保每个员工每天只有一条考勤记录
);

-- 培训表
CREATE TABLE IF NOT EXISTS Training (
    TrainingID INT PRIMARY KEY AUTO_INCREMENT,
    TrainingName VARCHAR(100) NOT NULL,
    Description TEXT,
    Trainer VARCHAR(100),
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL CHECK (EndDate >= StartDate),
    Location VARCHAR(100),
    MaxParticipants INT CHECK (MaxParticipants > 0),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 员工培训关联表（多对多关系）
CREATE TABLE IF NOT EXISTS EmployeeTraining (
    EmployeeID INT NOT NULL,
    TrainingID INT NOT NULL,
    EnrollmentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CompletionDate DATE,
    Score INT CHECK (Score BETWEEN 0 AND 100),
    Feedback TEXT,
    PRIMARY KEY (EmployeeID, TrainingID), -- 复合主键确保唯一性
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE,
    FOREIGN KEY (TrainingID) REFERENCES Training(TrainingID) ON DELETE CASCADE
);

-- =============================================
-- 2. 索引设计
-- =============================================

-- 为常用查询条件创建索引
CREATE INDEX idx_Employee_DepartmentID ON Employee(DepartmentID);
CREATE INDEX idx_Employee_PositionID ON Employee(PositionID);
CREATE INDEX idx_Employee_HireDate ON Employee(HireDate);
CREATE INDEX idx_Salary_EmployeeID_EffectiveDate ON Salary(EmployeeID, EffectiveDate DESC);
CREATE INDEX idx_Attendance_EmployeeID_AttendanceDate ON Attendance(EmployeeID, AttendanceDate DESC);
CREATE INDEX idx_Training_StartDate ON Training(StartDate);

-- =============================================
-- 3. 测试数据插入
-- =============================================

-- 插入部门数据
INSERT INTO Department (DepartmentName, Location) VALUES
('Human Resources', 'New York Office'),
('Engineering', 'San Francisco Office'),
('Sales', 'Chicago Office'),
('Marketing', 'Los Angeles Office'),
('Finance', 'Boston Office');

-- 插入职位数据
INSERT INTO Position (PositionName, Description, SalaryRangeMin, SalaryRangeMax) VALUES
('HR Manager', 'Manages HR department operations and staff', 80000, 120000),
('Software Engineer', 'Develops and maintains software applications', 60000, 110000),
('Sales Representative', 'Sells company products and services to clients', 45000, 90000),
('Marketing Specialist', 'Develops and executes marketing campaigns', 50000, 95000),
('Financial Analyst', 'Analyzes financial data and prepares reports', 55000, 100000),
('HR Generalist', 'Handles various HR administrative tasks', 40000, 75000),
('Senior Software Engineer', 'Leads software development projects', 80000, 130000),
('Sales Manager', 'Manages sales team and develops sales strategies', 70000, 120000);

-- 插入员工数据
INSERT INTO Employee (FirstName, LastName, Email, Phone, HireDate, DepartmentID, PositionID) VALUES
('John', 'Doe', 'john.doe@example.com', '123-456-7890', '2020-01-15', 2, 7),
('Jane', 'Smith', 'jane.smith@example.com', '987-654-3210', '2019-03-22', 1, 1),
('Bob', 'Johnson', 'bob.johnson@example.com', '555-123-4567', '2021-07-01', 3, 8),
('Alice', 'Williams', 'alice.williams@example.com', '444-555-6666', '2018-11-05', 4, 4),
('Charlie', 'Brown', 'charlie.brown@example.com', '333-222-1111', '2022-02-14', 5, 5),
('David', 'Wilson', 'david.wilson@example.com', '777-888-9999', '2020-06-30', 2, 2),
('Eva', 'Davis', 'eva.davis@example.com', '666-777-8888', '2021-09-15', 1, 6),
('Frank', 'Miller', 'frank.miller@example.com', '222-333-4444', '2019-08-20', 3, 3);

-- 更新部门经理
UPDATE Department SET ManagerID = 2 WHERE DepartmentID = 1;
UPDATE Department SET ManagerID = 1 WHERE DepartmentID = 2;
UPDATE Department SET ManagerID = 3 WHERE DepartmentID = 3;
UPDATE Department SET ManagerID = 4 WHERE DepartmentID = 4;
UPDATE Department SET ManagerID = 5 WHERE DepartmentID = 5;

-- 更新员工的经理ID
UPDATE Employee SET ManagerID = 1 WHERE EmployeeID IN (6);
UPDATE Employee SET ManagerID = 2 WHERE EmployeeID IN (7);
UPDATE Employee SET ManagerID = 3 WHERE EmployeeID IN (8);

-- 插入工资数据
INSERT INTO Salary (EmployeeID, EffectiveDate, Amount) VALUES
(1, '2020-01-15', 95000),
(1, '2021-01-15', 105000),
(1, '2022-01-15', 115000),
(2, '2019-03-22', 90000),
(2, '2020-03-22', 95000),
(3, '2021-07-01', 85000),
(4, '2018-11-05', 60000),
(4, '2019-11-05', 65000),
(4, '2020-11-05', 70000),
(5, '2022-02-14', 70000),
(6, '2020-06-30', 70000),
(6, '2021-06-30', 75000),
(7, '2021-09-15', 55000),
(8, '2019-08-20', 50000),
(8, '2020-08-20', 55000);

-- 插入考勤数据
INSERT INTO Attendance (EmployeeID, AttendanceDate, Status, HoursWorked) VALUES
-- 员工1的考勤
(1, '2023-05-01', 'Present', 8.0),
(1, '2023-05-02', 'Present', 8.0),
(1, '2023-05-03', 'Present', 8.0),
(1, '2023-05-04', 'Present', 8.0),
(1, '2023-05-05', 'Present', 8.0),
(1, '2023-05-08', 'Present', 8.0),
(1, '2023-05-09', 'Late', 7.5),
(1, '2023-05-10', 'Present', 8.0),
-- 员工2的考勤
(2, '2023-05-01', 'Present', 8.0),
(2, '2023-05-02', 'Present', 8.0),
(2, '2023-05-03', 'Leave', NULL),
(2, '2023-05-04', 'Present', 8.0),
(2, '2023-05-05', 'Present', 8.0),
-- 员工3的考勤
(3, '2023-05-01', 'Present', 8.0),
(3, '2023-05-02', 'Present', 8.0),
(3, '2023-05-03', 'Present', 8.0),
(3, '2023-05-04', 'Absent', NULL),
(3, '2023-05-05', 'Present', 8.0);

-- 插入培训数据
INSERT INTO Training (TrainingName, Description, Trainer, StartDate, EndDate, Location, MaxParticipants) VALUES
('SQL Fundamentals', 'Basic SQL querying and database design', 'Dr. Robert Brown', '2023-01-10', '2023-01-12', 'New York Office', 20),
('Project Management', 'Introduction to Agile and Scrum methodologies', 'Ms. Sarah Davis', '2023-02-15', '2023-02-17', 'San Francisco Office', 15),
('Leadership Skills', 'Developing effective leadership qualities', 'Mr. James Wilson', '2023-03-20', '2023-03-22', 'Chicago Office', 12),
('Data Analytics', 'Using data to drive business decisions', 'Dr. Emily Thompson', '2023-04-10', '2023-04-14', 'Los Angeles Office', 25),
('Advanced SQL', 'Complex queries, performance tuning, and optimization', 'Dr. Robert Brown', '2023-05-08', '2023-05-10', 'Boston Office', 18);

-- 插入员工培训数据
INSERT INTO EmployeeTraining (EmployeeID, TrainingID, CompletionDate, Score, Feedback) VALUES
(1, 1, '2023-01-12', 95, 'Excellent course! Learned a lot about SQL.'),
(1, 2, '2023-02-17', 88, 'Good introduction to Agile methodologies.'),
(2, 3, '2023-03-22', 92, 'Very insightful leadership training.'),
(3, 1, '2023-01-12', 79, 'Useful for beginners, but I knew most of it.'),
(3, 4, '2023-04-14', 85, 'Great course on data analytics.'),
(4, 4, '2023-04-14', 90, 'Excellent instructor and materials.'),
(5, 1, '2023-01-12', 88, 'Very helpful for my job.'),
(5, 5, NULL, NULL, NULL), -- 已报名但未完成
(6, 1, '2023-01-12', 91, 'Learned a lot of practical SQL techniques.'),
(6, 5, NULL, NULL, NULL), -- 已报名但未完成
(7, 2, '2023-02-17', 82, 'Good overview of project management.'),
(8, 4, '2023-04-14', 78, 'Useful, but a bit too technical for me.');

-- =============================================
-- 4. 查询示例
-- =============================================

-- 4.1 基本查询
SELECT * FROM Department;
SELECT * FROM Position;
SELECT * FROM Employee;

-- 4.2 连接查询

-- 查询所有员工及其部门和职位信息
SELECT 
    e.EmployeeID,
    CONCAT(e.FirstName, ' ', e.LastName) AS FullName,
    e.Email,
    e.Phone,
    e.HireDate,
    d.DepartmentName,
    p.PositionName,
    CONCAT(m.FirstName, ' ', m.LastName) AS ManagerName
FROM Employee e
LEFT JOIN Department d ON e.DepartmentID = d.DepartmentID
LEFT JOIN Position p ON e.PositionID = p.PositionID
LEFT JOIN Employee m ON e.ManagerID = m.EmployeeID;

-- 4.3 聚合查询

-- 统计每个部门的员工数量
SELECT 
    d.DepartmentName,
    COUNT(e.EmployeeID) AS EmployeeCount
FROM Department d
LEFT JOIN Employee e ON d.DepartmentID = e.DepartmentID AND e.IsActive = TRUE
GROUP BY d.DepartmentID, d.DepartmentName
ORDER BY EmployeeCount DESC;

-- 计算每个员工的平均工资
SELECT 
    CONCAT(e.FirstName, ' ', e.LastName) AS FullName,
    AVG(s.Amount) AS AverageSalary
FROM Employee e
JOIN Salary s ON e.EmployeeID = s.EmployeeID
GROUP BY e.EmployeeID, e.FirstName, e.LastName
ORDER BY AverageSalary DESC;

-- 4.4 子查询

-- 查询工资高于部门平均工资的员工
SELECT 
    CONCAT(e.FirstName, ' ', e.LastName) AS FullName,
    d.DepartmentName,
    s.Amount AS CurrentSalary
FROM Employee e
JOIN Department d ON e.DepartmentID = d.DepartmentID
JOIN Salary s ON e.EmployeeID = s.EmployeeID
WHERE s.EffectiveDate = (SELECT MAX(EffectiveDate) FROM Salary WHERE EmployeeID = e.EmployeeID)
AND s.Amount > (
    SELECT AVG(Amount)
    FROM Salary s2
    JOIN Employee e2 ON s2.EmployeeID = e2.EmployeeID
    WHERE e2.DepartmentID = e.DepartmentID
    AND s2.EffectiveDate = (SELECT MAX(EffectiveDate) FROM Salary WHERE EmployeeID = e2.EmployeeID)
);

-- 4.5 复杂查询

-- 查询2023年5月出勤率最高的部门
SELECT 
    d.DepartmentName,
    COUNT(a.AttendanceID) AS TotalDays,
    SUM(CASE WHEN a.Status = 'Present' OR a.Status = 'Late' THEN 1 ELSE 0 END) AS AttendedDays,
    ROUND((SUM(CASE WHEN a.Status = 'Present' OR a.Status = 'Late' THEN 1 ELSE 0 END) / COUNT(a.AttendanceID)) * 100, 2) AS AttendanceRate
FROM Department d
JOIN Employee e ON d.DepartmentID = e.DepartmentID
JOIN Attendance a ON e.EmployeeID = a.EmployeeID
WHERE a.AttendanceDate BETWEEN '2023-05-01' AND '2023-05-31'
GROUP BY d.DepartmentID, d.DepartmentName
ORDER BY AttendanceRate DESC;

-- =============================================
-- 5. 高级特性示例
-- =============================================

-- 5.1 视图

-- 创建员工信息视图
CREATE VIEW vw_EmployeeInfo AS
SELECT 
    e.EmployeeID,
    CONCAT(e.FirstName, ' ', e.LastName) AS FullName,
    e.Email,
    e.Phone,
    e.HireDate,
    e.IsActive,
    d.DepartmentName,
    p.PositionName,
    CONCAT(m.FirstName, ' ', m.LastName) AS ManagerName,
    s.Amount AS CurrentSalary,
    s.EffectiveDate AS SalaryEffectiveDate
FROM Employee e
LEFT JOIN Department d ON e.DepartmentID = d.DepartmentID
LEFT JOIN Position p ON e.PositionID = p.PositionID
LEFT JOIN Employee m ON e.ManagerID = m.EmployeeID
LEFT JOIN Salary s ON e.EmployeeID = s.EmployeeID AND s.EffectiveDate = (SELECT MAX(EffectiveDate) FROM Salary WHERE EmployeeID = e.EmployeeID);

-- 使用视图查询
SELECT * FROM vw_EmployeeInfo WHERE IsActive = TRUE ORDER BY DepartmentName, FullName;

-- 5.2 存储过程

-- 创建获取员工详细信息的存储过程
DELIMITER //
CREATE PROCEDURE GetEmployeeDetails(IN p_EmployeeID INT)
BEGIN
    SELECT * FROM vw_EmployeeInfo WHERE EmployeeID = p_EmployeeID;
END //
DELIMITER ;

-- 创建获取部门员工的存储过程
DELIMITER //
CREATE PROCEDURE GetDepartmentEmployees(IN p_DepartmentName VARCHAR(50))
BEGIN
    SELECT * FROM vw_EmployeeInfo WHERE DepartmentName = p_DepartmentName AND IsActive = TRUE ORDER BY FullName;
END //
DELIMITER ;

-- 调用存储过程
CALL GetEmployeeDetails(1);
CALL GetDepartmentEmployees('Engineering');

-- 5.3 触发器

-- 创建员工状态变更日志表
CREATE TABLE IF NOT EXISTS EmployeeStatusLog (
    LogID INT PRIMARY KEY AUTO_INCREMENT,
    EmployeeID INT NOT NULL,
    OldStatus BOOLEAN,
    NewStatus BOOLEAN,
    ChangedBy VARCHAR(50) DEFAULT 'System',
    ChangedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE
);

-- 创建员工状态变更触发器
DELIMITER //
CREATE TRIGGER trg_EmployeeStatusChange
AFTER UPDATE ON Employee
FOR EACH ROW
BEGIN
    IF OLD.IsActive != NEW.IsActive THEN
        INSERT INTO EmployeeStatusLog (EmployeeID, OldStatus, NewStatus) 
        VALUES (NEW.EmployeeID, OLD.IsActive, NEW.IsActive);
    END IF;
END //
DELIMITER ;

-- 测试触发器
UPDATE Employee SET IsActive = FALSE WHERE EmployeeID = 8;
SELECT * FROM EmployeeStatusLog;

-- 5.4 事务

-- 使用事务处理员工晋升
DELIMITER //
CREATE PROCEDURE PromoteEmployee(
    IN p_EmployeeID INT,
    IN p_NewPositionID INT,
    IN p_NewSalary DECIMAL(10, 2),
    IN p_EffectiveDate DATE
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Promotion failed. Please check the input values.';
    END;
    
    START TRANSACTION;
    
    -- 更新员工职位
    UPDATE Employee SET PositionID = p_NewPositionID WHERE EmployeeID = p_EmployeeID;
    
    -- 插入新工资记录
    INSERT INTO Salary (EmployeeID, EffectiveDate, Amount) VALUES (p_EmployeeID, p_EffectiveDate, p_NewSalary);
    
    COMMIT;
    
    SELECT 'Employee promoted successfully.' AS Result;
END //
DELIMITER ;

-- 测试事务
CALL PromoteEmployee(6, 7, 85000, '2023-06-01');
SELECT * FROM vw_EmployeeInfo WHERE EmployeeID = 6;

-- =============================================
-- 6. 数据模型验证
-- =============================================

-- 验证数据完整性
SELECT 
    'Department' AS TableName,
    COUNT(*) AS TotalRecords
FROM Department
UNION ALL
SELECT 
    'Position' AS TableName,
    COUNT(*) AS TotalRecords
FROM Position
UNION ALL
SELECT 
    'Employee' AS TableName,
    COUNT(*) AS TotalRecords
FROM Employee
UNION ALL
SELECT 
    'Salary' AS TableName,
    COUNT(*) AS TotalRecords
FROM Salary
UNION ALL
SELECT 
    'Attendance' AS TableName,
    COUNT(*) AS TotalRecords
FROM Attendance
UNION ALL
SELECT 
    'Training' AS TableName,
    COUNT(*) AS TotalRecords
FROM Training
UNION ALL
SELECT 
    'EmployeeTraining' AS TableName,
    COUNT(*) AS TotalRecords
FROM EmployeeTraining;

-- =============================================
-- 7. 清理与维护
-- =============================================

-- 注意：以下命令用于演示，实际使用时请谨慎

-- 删除创建的对象
-- DROP VIEW IF EXISTS vw_EmployeeInfo;
-- DROP PROCEDURE IF EXISTS GetEmployeeDetails;
-- DROP PROCEDURE IF EXISTS GetDepartmentEmployees;
-- DROP PROCEDURE IF EXISTS PromoteEmployee;
-- DROP TRIGGER IF EXISTS trg_EmployeeStatusChange;
-- DROP TABLE IF EXISTS EmployeeTraining;
-- DROP TABLE IF EXISTS Training;
-- DROP TABLE IF EXISTS Attendance;
-- DROP TABLE IF EXISTS Salary;
-- DROP TABLE IF EXISTS Employee;
-- DROP TABLE IF EXISTS Position;
-- DROP TABLE IF EXISTS Department;
-- DROP TABLE IF EXISTS EmployeeStatusLog;
-- DROP DATABASE IF EXISTS HRManagement;

-- =============================================
-- 8. 最佳实践总结
-- =============================================

/*
关系型数据建模最佳实践：

1. 表设计：
   - 使用有意义的表名和列名
   - 选择合适的数据类型
   - 为每个表定义主键
   - 建立适当的外键关系
   - 使用约束确保数据完整性

2. 索引设计：
   - 为常用查询条件创建索引
   - 为外键列创建索引
   - 避免为经常更新的列创建索引
   - 合理使用复合索引

3. 查询优化：
   - 使用连接代替子查询（在合适的情况下）
   - 避免使用SELECT *
   - 使用WHERE子句过滤数据
   - 合理使用GROUP BY和ORDER BY

4. 安全性：
   - 对敏感数据进行加密
   - 实现适当的访问控制
   - 使用参数化查询防止SQL注入

5. 维护：
   - 定期备份数据库
   - 定期优化表和索引
   - 监控数据库性能
   - 及时更新统计信息
*/