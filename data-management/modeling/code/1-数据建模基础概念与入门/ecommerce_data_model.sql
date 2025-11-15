-- =============================================
-- 数据建模基础概念与入门 - 电商系统数据模型示例
-- 完整可运行的SQL代码示例
-- =============================================

-- 1. 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 使用该数据库
USE ecommerce_db;

-- 3. 创建用户表
CREATE TABLE IF NOT EXISTS `User` (
    UserID INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID，主键，自增长',
    Username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名，唯一',
    Email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱，唯一',
    Password VARCHAR(100) NOT NULL COMMENT '密码（实际应用中应使用加密存储）',
    FirstName VARCHAR(50) COMMENT '名字',
    LastName VARCHAR(50) COMMENT '姓氏',
    Address TEXT COMMENT '地址',
    Phone VARCHAR(20) COMMENT '电话',
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间，默认当前时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 4. 创建产品表
CREATE TABLE IF NOT EXISTS Product (
    ProductID INT PRIMARY KEY AUTO_INCREMENT COMMENT '产品ID，主键，自增长',
    ProductName VARCHAR(100) NOT NULL COMMENT '产品名称',
    Description TEXT COMMENT '产品描述',
    Price DECIMAL(10, 2) NOT NULL COMMENT '产品价格，保留两位小数',
    Category VARCHAR(50) COMMENT '产品类别',
    Stock INT DEFAULT 0 COMMENT '库存数量，默认0',
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间，默认当前时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品表';

-- 5. 创建订单表
CREATE TABLE IF NOT EXISTS `Order` (
    OrderID INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID，主键，自增长',
    UserID INT NOT NULL COMMENT '用户ID，外键',
    OrderDate DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '订单日期，默认当前时间',
    TotalAmount DECIMAL(10, 2) NOT NULL COMMENT '订单总金额',
    Status VARCHAR(20) DEFAULT 'Pending' COMMENT '订单状态，默认待处理',
    FOREIGN KEY (UserID) REFERENCES `User`(UserID) ON DELETE CASCADE COMMENT '外键约束，关联用户表'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- 6. 创建订单详情表
CREATE TABLE IF NOT EXISTS OrderDetail (
    OrderDetailID INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单详情ID，主键，自增长',
    OrderID INT NOT NULL COMMENT '订单ID，外键',
    ProductID INT NOT NULL COMMENT '产品ID，外键',
    Quantity INT NOT NULL CHECK (Quantity > 0) COMMENT '数量，必须大于0',
    UnitPrice DECIMAL(10, 2) NOT NULL COMMENT '单价',
    FOREIGN KEY (OrderID) REFERENCES `Order`(OrderID) ON DELETE CASCADE COMMENT '外键约束，关联订单表',
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID) ON DELETE CASCADE COMMENT '外键约束，关联产品表'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单详情表';

-- 7. 插入测试用户数据
INSERT INTO `User` (Username, Email, Password, FirstName, LastName, Address, Phone) VALUES
('john_doe', 'john@example.com', 'password123', 'John', 'Doe', '123 Main St, New York, NY 10001', '123-456-7890'),
('jane_smith', 'jane@example.com', 'password456', 'Jane', 'Smith', '456 Oak Ave, Los Angeles, CA 90001', '987-654-3210'),
('bob_johnson', 'bob@example.com', 'password789', 'Bob', 'Johnson', '789 Pine St, Chicago, IL 60601', '555-123-4567'),
('alice_williams', 'alice@example.com', 'passwordabc', 'Alice', 'Williams', '321 Maple St, Houston, TX 77001', '555-987-6543'),
('charlie_brown', 'charlie@example.com', 'passworddef', 'Charlie', 'Brown', '654 Birch St, Phoenix, AZ 85001', '555-456-7890');

-- 8. 插入测试产品数据
INSERT INTO Product (ProductName, Description, Price, Category, Stock) VALUES
('Dell XPS 13 Laptop', '13.3-inch Ultrabook with Intel Core i7, 16GB RAM, 512GB SSD', 999.99, 'Electronics', 50),
('iPhone 14 Pro', '6.1-inch Super Retina XDR display, A16 Bionic chip', 999.00, 'Electronics', 100),
('Sony WH-1000XM5 Headphones', 'Industry-leading noise cancellation, 30-hour battery life', 399.99, 'Electronics', 200),
('Nike Air Max 270', 'Men\'s sneakers with Max Air cushioning', 150.00, 'Clothing', 500),
('Levi\'s 501 Original Fit Jeans', 'Classic straight-leg jeans for men', 69.50, 'Clothing', 300),
('KitchenAid Stand Mixer', '5-quart tilt-head stand mixer with 10 speeds', 349.99, 'Home & Kitchen', 150),
('Amazon Echo Dot (5th Gen)', 'Smart speaker with Alexa, improved sound', 49.99, 'Electronics', 1000),
('Cuisinart Coffee Maker', '12-cup programmable coffee maker', 79.99, 'Home & Kitchen', 250);

-- 9. 插入测试订单数据
INSERT INTO `Order` (UserID, TotalAmount, Status) VALUES
(1, 1199.98, 'Completed'),
(2, 899.99, 'Processing'),
(3, 219.99, 'Shipped'),
(4, 429.98, 'Completed'),
(5, 49.99, 'Pending');

-- 10. 插入测试订单详情数据
INSERT INTO OrderDetail (OrderID, ProductID, Quantity, UnitPrice) VALUES
(1, 1, 1, 999.99),  -- Dell XPS 13 Laptop
(1, 3, 1, 199.99),  -- Sony WH-1000XM5 Headphones
(2, 2, 1, 899.99),  -- iPhone 14 Pro
(3, 4, 1, 150.00),  -- Nike Air Max 270
(3, 5, 1, 69.50),   -- Levi\'s 501 Jeans
(4, 6, 1, 349.99),  -- KitchenAid Stand Mixer
(4, 8, 1, 79.99),   -- Cuisinart Coffee Maker
(5, 7, 1, 49.99);   -- Amazon Echo Dot

-- =============================================
-- 查询示例 - 用于验证数据模型和理解数据关系
-- =============================================

-- 1. 查询所有用户信息
SELECT * FROM `User`;

-- 2. 查询所有产品信息，按类别分组
SELECT Category, ProductName, Price, Stock FROM Product ORDER BY Category, Price;

-- 3. 查询特定用户（John Doe）的所有订单
SELECT o.OrderID, o.OrderDate, o.TotalAmount, o.Status
FROM `Order` o
JOIN `User` u ON o.UserID = u.UserID
WHERE u.Username = 'john_doe';

-- 4. 查询特定订单（订单ID=1）的所有产品详情
SELECT 
    o.OrderID, 
    o.OrderDate, 
    p.ProductName, 
    od.Quantity, 
    od.UnitPrice, 
    (od.Quantity * od.UnitPrice) AS Subtotal
FROM OrderDetail od
JOIN `Order` o ON od.OrderID = o.OrderID
JOIN Product p ON od.ProductID = p.ProductID
WHERE od.OrderID = 1;

-- 5. 查询每个用户的订单数量和总消费金额
SELECT 
    u.Username, 
    COUNT(o.OrderID) AS OrderCount, 
    SUM(o.TotalAmount) AS TotalSpent
FROM `User` u
LEFT JOIN `Order` o ON u.UserID = o.UserID
GROUP BY u.Username
ORDER BY TotalSpent DESC;

-- 6. 查询每个产品类别的销售情况（销售数量、总金额）
SELECT 
    p.Category, 
    COUNT(od.OrderDetailID) AS TotalOrders, 
    SUM(od.Quantity) AS TotalQuantity, 
    SUM(od.Quantity * od.UnitPrice) AS TotalSales
FROM Product p
LEFT JOIN OrderDetail od ON p.ProductID = od.ProductID
GROUP BY p.Category
ORDER BY TotalSales DESC;

-- 7. 查询库存不足的产品（库存少于100）
SELECT ProductName, Category, Stock, Price
FROM Product
WHERE Stock < 100
ORDER BY Stock ASC;

-- 8. 查询所有状态为"Completed"的订单及其用户信息
SELECT 
    u.Username, 
    u.Email, 
    o.OrderID, 
    o.OrderDate, 
    o.TotalAmount, 
    o.Status
FROM `Order` o
JOIN `User` u ON o.UserID = u.UserID
WHERE o.Status = 'Completed'
ORDER BY o.OrderDate DESC;

-- =============================================
-- 数据模型验证与最佳实践演示
-- =============================================

-- 1. 验证外键约束（尝试插入不存在的用户ID）
-- 这条语句会失败，因为UserID=999不存在
-- INSERT INTO `Order` (UserID, TotalAmount, Status) VALUES (999, 100.00, 'Pending');

-- 2. 验证CHECK约束（尝试插入数量为0的订单详情）
-- 这条语句会失败，因为Quantity必须大于0
-- INSERT INTO OrderDetail (OrderID, ProductID, Quantity, UnitPrice) VALUES (1, 1, 0, 999.99);

-- 3. 验证唯一约束（尝试插入重复的用户名）
-- 这条语句会失败，因为用户名必须唯一
-- INSERT INTO `User` (Username, Email, Password) VALUES ('john_doe', 'john2@example.com', 'password123');

-- =============================================
-- 清理数据（可选）
-- =============================================

-- 如果需要重新开始，可以取消注释以下语句
-- DROP DATABASE IF EXISTS ecommerce_db;