-- 第10章：SQL实战应用示例代码

-- =================================
-- 10.2 电商系统数据库设计与查询
-- =================================

-- 创建电商系统数据库
CREATE DATABASE IF NOT EXISTS ecommerce_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce_demo;

-- 用户表
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 用户地址表
CREATE TABLE user_addresses (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    address_type ENUM('billing', 'shipping') NOT NULL,
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 商品分类表
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);

-- 商品表
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2),
    sku VARCHAR(100) NOT NULL UNIQUE,
    stock_quantity INT DEFAULT 0,
    min_stock_level INT DEFAULT 0,
    category_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- 商品图片表
CREATE TABLE product_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    sort_order INT DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 订单表
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    shipping_amount DECIMAL(10, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    shipping_address_id INT,
    billing_address_id INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_date TIMESTAMP NULL,
    delivered_date TIMESTAMP NULL,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (shipping_address_id) REFERENCES user_addresses(address_id),
    FOREIGN KEY (billing_address_id) REFERENCES user_addresses(address_id)
);

-- 订单商品表
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 评价表
CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE KEY (product_id, user_id)
);

-- 插入示例数据
INSERT INTO categories (name, description) VALUES
('电子产品', '各类电子设备和配件'),
('服装', '男女服装和配饰'),
('家居用品', '家庭生活用品'),
('图书', '各类图书和出版物'),
('运动户外', '运动器材和户外用品');

INSERT INTO categories (name, description, parent_category_id) VALUES
('手机', '智能手机和配件', 1),
('电脑', '笔记本电脑和台式机', 1),
('男装', '男士服装', 2),
('女装', '女士服装', 2),
('厨房用品', '厨房烹饪用具', 3),
('床上用品', '床单被套等', 3),
('小说', '各类小说', 4),
('教育', '教育类书籍', 4),
('健身器材', '家用健身设备', 5),
('户外装备', '露营徒步装备', 5);

INSERT INTO products (name, description, price, cost_price, sku, stock_quantity, min_stock_level, category_id) VALUES
('iPhone 14 Pro', '苹果最新款智能手机', 7999.00, 6500.00, 'IP14P-128GB', 50, 10, 6),
('MacBook Pro 14', '苹果笔记本电脑', 14999.00, 12000.00, 'MBP14-16GB', 30, 5, 7),
('男士商务衬衫', '纯棉商务衬衫', 299.00, 150.00, 'MS-SHIRT-WHITE', 100, 20, 8),
('女士连衣裙', '夏季新款连衣裙', 399.00, 200.00, 'WS-DRESS-RED', 80, 15, 9),
('不粘锅套装', '5件套不粘锅', 599.00, 350.00, 'NP-PAN-SET5', 40, 10, 10),
('纯棉四件套', '全棉床上用品', 299.00, 180.00, 'CC-BED-SET', 60, 12, 11),
('三体全集', '刘慈欣科幻小说', 128.00, 80.00, '3BODY-SET', 200, 30, 12),
('Python编程入门', 'Python学习教程', 89.00, 50.00, 'PY-BEGIN', 150, 25, 13),
('哑铃套装', '可调节重量哑铃', 399.00, 250.00, 'DB-SET-20KG', 35, 8, 14),
('帐篷', '双人户外帐篷', 799.00, 500.00, 'TENT-2P', 25, 5, 15);

INSERT INTO users (username, email, password_hash, first_name, last_name, phone) VALUES
('john_doe', 'john@example.com', 'hashed_password', 'John', 'Doe', '13800138001'),
('jane_smith', 'jane@example.com', 'hashed_password', 'Jane', 'Smith', '13800138002'),
('bob_wilson', 'bob@example.com', 'hashed_password', 'Bob', 'Wilson', '13800138003'),
('alice_brown', 'alice@example.com', 'hashed_password', 'Alice', 'Brown', '13800138004'),
('charlie_davis', 'charlie@example.com', 'hashed_password', 'Charlie', 'Davis', '13800138005');

INSERT INTO user_addresses (user_id, address_type, street_address, city, state, postal_code, country, is_default) VALUES
(1, 'shipping', '123 Main St', '北京', '北京市', '100000', '中国', TRUE),
(1, 'billing', '123 Main St', '北京', '北京市', '100000', '中国', TRUE),
(2, 'shipping', '456 Oak Ave', '上海', '上海市', '200000', '中国', TRUE),
(2, 'billing', '456 Oak Ave', '上海', '上海市', '200000', '中国', TRUE),
(3, 'shipping', '789 Pine Rd', '广州', '广东省', '510000', '中国', TRUE),
(3, 'billing', '789 Pine Rd', '广州', '广东省', '510000', '中国', TRUE);

INSERT INTO product_images (product_id, image_url, alt_text, is_primary) VALUES
(1, 'https://example.com/images/iphone14pro.jpg', 'iPhone 14 Pro', TRUE),
(2, 'https://example.com/images/macbookpro14.jpg', 'MacBook Pro 14', TRUE),
(3, 'https://example.com/images/mens_shirt.jpg', '男士商务衬衫', TRUE),
(4, 'https://example.com/images/womens_dress.jpg', '女士连衣裙', TRUE),
(5, 'https://example.com/images/nonstick_pan_set.jpg', '不粘锅套装', TRUE);

INSERT INTO orders (order_number, user_id, status, subtotal, tax_amount, shipping_amount, total_amount, shipping_address_id, billing_address_id) VALUES
('ORD2023001', 1, 'delivered', 8298.00, 829.80, 20.00, 9147.80, 1, 2),
('ORD2023002', 2, 'shipped', 698.00, 69.80, 15.00, 782.80, 3, 4),
('ORD2023003', 3, 'processing', 1498.00, 149.80, 18.00, 1665.80, 5, 6),
('ORD2023004', 1, 'pending', 398.00, 39.80, 12.00, 449.80, 1, 2),
('ORD2023005', 4, 'delivered', 998.00, 99.80, 16.00, 1113.80, 7, 8);

INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
(1, 1, 1, 7999.00, 7999.00),
(1, 5, 1, 299.00, 299.00),
(2, 3, 2, 299.00, 598.00),
(2, 6, 1, 100.00, 100.00),
(3, 2, 1, 14999.00, 14999.00),
(4, 4, 1, 398.00, 398.00),
(5, 7, 1, 128.00, 128.00),
(5, 8, 1, 89.00, 89.00),
(5, 9, 1, 399.00, 399.00),
(5, 10, 1, 382.00, 382.00);

INSERT INTO reviews (product_id, user_id, rating, title, comment) VALUES
(1, 1, 5, '非常满意', 'iPhone 14 Pro 真的很棒，拍照效果一流！'),
(2, 2, 4, '性能强劲', 'MacBook Pro 性能很好，就是价格有点贵'),
(3, 3, 4, '质量不错', '衬衫质量很好，尺码也合适'),
(4, 1, 3, '一般般', '连衣裙还可以，但颜色和图片有点差异'),
(5, 2, 5, '物超所值', '不粘锅套装质量很好，做饭很方便');

-- =================================
-- 10.2.2 电商系统常用查询示例
-- =================================

-- 1. 获取商品详情及评价信息
SELECT 
    p.product_id,
    p.name AS product_name,
    p.description,
    p.price,
    p.stock_quantity,
    c.name AS category_name,
    AVG(r.rating) AS average_rating,
    COUNT(r.review_id) AS review_count,
    pi.image_url AS primary_image_url
FROM 
    products p
LEFT JOIN 
    categories c ON p.category_id = c.category_id
LEFT JOIN 
    reviews r ON p.product_id = r.product_id
LEFT JOIN 
    product_images pi ON p.product_id = pi.product_id AND pi.is_primary = TRUE
WHERE 
    p.product_id = 1
GROUP BY 
    p.product_id;

-- 2. 获取用户订单历史
SELECT 
    o.order_id,
    o.order_number,
    o.order_date,
    o.status,
    o.total_amount,
    COUNT(oi.order_item_id) AS item_count,
    GROUP_CONCAT(
        CONCAT(p.name, ' (', oi.quantity, ' x ', oi.unit_price, ')')
        SEPARATOR ', '
    ) AS items
FROM 
    orders o
JOIN 
    order_items oi ON o.order_id = oi.order_id
JOIN 
    products p ON oi.product_id = p.product_id
WHERE 
    o.user_id = 1
GROUP BY 
    o.order_id
ORDER BY 
    o.order_date DESC;

-- 3. 获取热门商品
SELECT 
    p.product_id,
    p.name AS product_name,
    p.price,
    c.name AS category_name,
    SUM(oi.quantity) AS total_sold,
    SUM(oi.total_price) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS order_count,
    AVG(r.rating) AS average_rating
FROM 
    products p
JOIN 
    order_items oi ON p.product_id = oi.product_id
JOIN 
    orders o ON oi.order_id = o.order_id
JOIN 
    categories c ON p.category_id = c.category_id
LEFT JOIN 
    reviews r ON p.product_id = r.product_id
WHERE 
    o.status IN ('delivered', 'shipped')
GROUP BY 
    p.product_id
ORDER BY 
    total_sold DESC
LIMIT 10;

-- =================================
-- 10.3 社交媒体数据分析
-- =================================

-- 创建社交媒体数据库
CREATE DATABASE IF NOT EXISTS social_media_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE social_media_demo;

-- 用户表
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    bio TEXT,
    profile_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 关注关系表
CREATE TABLE follows (
    follower_id INT NOT NULL,
    following_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id) REFERENCES users(user_id),
    FOREIGN KEY (following_id) REFERENCES users(user_id)
);

-- 帖子表
CREATE TABLE posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 点赞表
CREATE TABLE likes (
    like_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    post_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    UNIQUE KEY (user_id, post_id)
);

-- 评论表
CREATE TABLE comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    parent_comment_id INT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    like_count INT DEFAULT 0,
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments(comment_id)
);

-- 话题标签表
CREATE TABLE hashtags (
    hashtag_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 帖子标签关联表
CREATE TABLE post_hashtags (
    post_id INT NOT NULL,
    hashtag_id INT NOT NULL,
    PRIMARY KEY (post_id, hashtag_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (hashtag_id) REFERENCES hashtags(hashtag_id)
);

-- 插入示例数据
INSERT INTO users (username, email, password_hash, display_name, bio) VALUES
('john_doe', 'john@example.com', 'hashed_password', 'John Doe', '热爱生活的程序员'),
('jane_smith', 'jane@example.com', 'hashed_password', 'Jane Smith', '摄影师，旅行爱好者'),
('bob_wilson', 'bob@example.com', 'hashed_password', 'Bob Wilson', '美食博主'),
('alice_brown', 'alice@example.com', 'hashed_password', 'Alice Brown', '健身教练'),
('charlie_davis', 'charlie@example.com', 'hashed_password', 'Charlie Davis', '音乐制作人');

INSERT INTO follows (follower_id, following_id) VALUES
(1, 2),
(1, 3),
(2, 1),
(2, 4),
(3, 1),
(3, 5),
(4, 2),
(4, 3),
(5, 1),
(5, 4);

INSERT INTO posts (user_id, content, like_count, comment_count) VALUES
(1, '今天学习了新的SQL优化技巧，感觉收获很大！', 5, 2),
(2, '分享一张今天拍的照片，夕阳真的很美', 12, 4),
(3, '尝试做了一道新菜，味道出乎意料的好', 8, 3),
(4, '晨跑5公里，感觉精神焕发！#健康生活', 15, 5),
(5, '新歌制作完成，期待大家的反馈', 20, 7),
(1, 'SQL窗口函数真的很强大，可以解决很多复杂问题', 10, 3),
(2, '旅行中遇到的风景，每一帧都是壁纸', 18, 6),
(3, '分享一个简单又美味的家常菜谱', 7, 2);

INSERT INTO likes (user_id, post_id) VALUES
(2, 1),
(3, 1),
(4, 1),
(5, 1),
(1, 2),
(3, 2),
(4, 2),
(5, 2),
(1, 3),
(2, 3),
(4, 3),
(5, 3),
(1, 4),
(2, 4),
(3, 4),
(5, 4),
(1, 5),
(2, 5),
(3, 5),
(4, 5);

INSERT INTO comments (post_id, user_id, content, like_count) VALUES
(1, 2, '能分享一些具体的优化技巧吗？', 2),
(1, 3, '我也在学习SQL，一起进步！', 1),
(2, 1, '拍得真好，能分享一下拍摄参数吗？', 3),
(2, 3, '这个地方看起来很美，是在哪里？', 2),
(3, 1, '菜谱可以分享一下吗？', 1),
(3, 4, '看起来很美味，我也想试试', 2);

INSERT INTO hashtags (name) VALUES
('SQL'),
('健康生活'),
('美食'),
('摄影'),
('旅行'),
('音乐');

INSERT INTO post_hashtags (post_id, hashtag_id) VALUES
(1, 1),
(4, 2),
(4, 3),
(2, 4),
(2, 5),
(5, 6),
(6, 1),
(7, 4),
(7, 5),
(8, 3);

-- =================================
-- 10.3.2 社交媒体数据分析查询
-- =================================

-- 1. 获取用户动态流
SELECT 
    p.post_id,
    p.content,
    p.created_at,
    p.like_count,
    p.comment_count,
    p.share_count,
    u.user_id,
    u.username,
    u.display_name,
    u.profile_image_url,
    CASE 
        WHEN l.user_id IS NOT NULL THEN TRUE 
        ELSE FALSE 
    END AS is_liked_by_current_user
FROM 
    posts p
JOIN 
    users u ON p.user_id = u.user_id
LEFT JOIN 
    follows f ON f.following_id = p.user_id AND f.follower_id = 1
LEFT JOIN 
    likes l ON l.post_id = p.post_id AND l.user_id = 1
WHERE 
    p.user_id = 1 OR f.follower_id IS NOT NULL
ORDER BY 
    p.created_at DESC
LIMIT 20;

-- 2. 获取热门话题
SELECT 
    h.hashtag_id,
    h.name AS hashtag_name,
    COUNT(ph.post_id) AS post_count,
    COUNT(DISTINCT p.user_id) AS user_count,
    SUM(p.like_count) AS total_likes
FROM 
    hashtags h
JOIN 
    post_hashtags ph ON h.hashtag_id = ph.hashtag_id
JOIN 
    posts p ON ph.post_id = p.post_id
GROUP BY 
    h.hashtag_id
ORDER BY 
    post_count DESC
LIMIT 10;

-- 3. 获取用户影响力分析
SELECT 
    u.user_id,
    u.username,
    u.display_name,
    COUNT(DISTINCT f1.following_id) AS following_count,
    COUNT(DISTINCT f2.follower_id) AS follower_count,
    COUNT(DISTINCT p.post_id) AS post_count,
    SUM(p.like_count) AS total_likes_received,
    SUM(p.comment_count) AS total_comments_received,
    AVG(p.like_count) AS avg_likes_per_post,
    CASE 
        WHEN COUNT(DISTINCT f2.follower_id) > 0 
        THEN (COUNT(DISTINCT f2.follower_id) / NULLIF(COUNT(DISTINCT f1.following_id), 0)) 
        ELSE 0 
    END AS follower_to_following_ratio
FROM 
    users u
LEFT JOIN 
    follows f1 ON u.user_id = f1.follower_id
LEFT JOIN 
    follows f2 ON u.user_id = f2.following_id
LEFT JOIN 
    posts p ON u.user_id = p.user_id
GROUP BY 
    u.user_id
ORDER BY 
    follower_count DESC
LIMIT 10;

-- =================================
-- 10.4 企业人力资源管理系统
-- =================================

-- 创建HR系统数据库
CREATE DATABASE IF NOT EXISTS hr_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hr_demo;

-- 部门表
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    manager_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 员工表
CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_number VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    hire_date DATE NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    salary DECIMAL(10, 2),
    department_id INT,
    manager_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

-- 考勤记录表
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    check_in TIME,
    check_out TIME,
    break_duration INT DEFAULT 0, -- 休息时间（分钟）
    work_hours DECIMAL(4, 2), -- 实际工作小时数
    overtime_hours DECIMAL(4, 2) DEFAULT 0, -- 加班小时数
    status ENUM('present', 'absent', 'late', 'early_leave', 'holiday', 'sick_leave', 'annual_leave') NOT NULL,
    notes TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    UNIQUE KEY (employee_id, attendance_date)
);

-- 请假申请表
CREATE TABLE leave_requests (
    leave_request_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    leave_type ENUM('annual_leave', 'sick_leave', 'personal_leave', 'maternity_leave', 'paternity_leave') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_count DECIMAL(3, 1) NOT NULL,
    reason TEXT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    approver_id INT,
    approver_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (approver_id) REFERENCES employees(employee_id)
);

-- 绩效评估表
CREATE TABLE performance_reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    review_period_start DATE NOT NULL,
    review_period_end DATE NOT NULL,
    overall_rating DECIMAL(3, 2) CHECK (overall_rating >= 1 AND overall_rating <= 5),
    strengths TEXT,
    areas_for_improvement TEXT,
    goals TEXT,
    comments TEXT,
    status ENUM('draft', 'submitted', 'approved') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (reviewer_id) REFERENCES employees(employee_id)
);

-- 插入示例数据
INSERT INTO departments (name, description) VALUES
('技术部', '负责公司产品研发和技术支持'),
('市场部', '负责市场推广和客户关系'),
('人事部', '负责人力资源管理和行政事务'),
('财务部', '负责公司财务管理和会计核算'),
('销售部', '负责产品销售和业务拓展');

INSERT INTO employees (employee_number, first_name, last_name, email, phone, hire_date, job_title, salary, department_id) VALUES
('EMP001', '张', '三', 'zhangsan@example.com', '13800138001', '2020-01-15', '高级工程师', 15000.00, 1),
('EMP002', '李', '四', 'lisi@example.com', '13800138002', '2020-03-20', '工程师', 12000.00, 1),
('EMP003', '王', '五', 'wangwu@example.com', '13800138003', '2019-06-10', '技术经理', 20000.00, 1),
('EMP004', '赵', '六', 'zhaoliu@example.com', '13800138004', '2021-02-28', '市场专员', 9000.00, 2),
('EMP005', '钱', '七', 'qianqi@example.com', '13800138005', '2019-11-05', '市场经理', 18000.00, 2),
('EMP006', '孙', '八', 'sunba@example.com', '13800138006', '2020-07-12', '人事专员', 8000.00, 3),
('EMP007', '周', '九', 'zhoujiu@example.com', '13800138007', '2020-05-20', '人事经理', 16000.00, 3),
('EMP008', '吴', '十', 'wushi@example.com', '13800138008', '2018-09-15', '财务经理', 19000.00, 4),
('EMP009', '郑', '十一', 'zhengshiyi@example.com', '13800138009', '2021-01-10', '会计', 10000.00, 4),
('EMP010', '陈', '十二', 'chenshier@example.com', '13800138010', '2019-03-15', '销售经理', 22000.00, 5);

-- 设置经理关系
UPDATE employees SET manager_id = 3 WHERE id IN (1, 2);
UPDATE employees SET manager_id = 5 WHERE id IN (4);
UPDATE employees SET manager_id = 7 WHERE id IN (6);
UPDATE employees SET manager_id = 8 WHERE id IN (9);
UPDATE departments SET manager_id = 3 WHERE id = 1;
UPDATE departments SET manager_id = 5 WHERE id = 2;
UPDATE departments SET manager_id = 7 WHERE id = 3;
UPDATE departments SET manager_id = 8 WHERE id = 4;
UPDATE departments SET manager_id = 10 WHERE id = 5;

-- 插入考勤记录
INSERT INTO attendance (employee_id, attendance_date, check_in, check_out, work_hours, status) VALUES
(1, '2023-06-01', '09:00:00', '18:00:00', 8.5, 'present'),
(1, '2023-06-02', '08:45:00', '18:15:00', 9.0, 'present'),
(1, '2023-06-03', '09:15:00', '18:30:00', 8.5, 'late'),
(2, '2023-06-01', '09:00:00', '18:00:00', 8.5, 'present'),
(2, '2023-06-02', '09:00:00', '18:00:00', 8.5, 'present'),
(2, '2023-06-03', '09:00:00', '17:30:00', 8.0, 'early_leave'),
(3, '2023-06-01', '08:30:00', '18:00:00', 9.0, 'present'),
(3, '2023-06-02', '08:30:00', '18:00:00', 9.0, 'present'),
(3, '2023-06-03', '08:30:00', '18:00:00', 9.0, 'present');

-- 插入请假申请
INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, days_count, reason, status, approver_id) VALUES
(1, 'annual_leave', '2023-07-10', '2023-07-14', 5.0, '家庭旅行', 'approved', 3),
(2, 'sick_leave', '2023-06-15', '2023-06-16', 2.0, '感冒发烧', 'approved', 3),
(4, 'personal_leave', '2023-06-20', '2023-06-20', 1.0, '个人事务', 'pending', 5),
(6, 'annual_leave', '2023-08-01', '2023-08-05', 5.0, '探亲', 'approved', 7);

-- 插入绩效评估
INSERT INTO performance_reviews (employee_id, reviewer_id, review_period_start, review_period_end, overall_rating, strengths, areas_for_improvement, goals, status) VALUES
(1, 3, '2023-01-01', '2023-06-30', 4.5, '技术能力强，解决问题效率高', '需要加强团队协作能力', '提升项目管理能力', 'approved'),
(2, 3, '2023-01-01', '2023-06-30', 4.0, '工作认真负责，代码质量高', '需要提高创新能力', '学习新技术框架', 'approved'),
(4, 5, '2023-01-01', '2023-06-30', 3.5, '沟通能力强，客户关系维护好', '需要提高数据分析能力', '掌握市场分析工具', 'approved'),
(6, 7, '2023-01-01', '2023-06-30', 4.0, '工作细致，执行力强', '需要提高战略思维能力', '参与公司战略规划', 'approved');

-- =================================
-- 10.4.2 HR系统常用查询示例
-- =================================

-- 1. 获取员工详细信息
SELECT 
    e.employee_id,
    e.employee_number,
    CONCAT(e.first_name, ' ', e.last_name) AS full_name,
    e.email,
    e.phone,
    e.hire_date,
    e.job_title,
    e.salary,
    d.name AS department_name,
    CONCAT(m.first_name, ' ', m.last_name) AS manager_name,
    TIMESTAMPDIFF(YEAR, e.hire_date, CURDATE()) AS years_of_service,
    CASE 
        WHEN e.is_active THEN '在职'
        ELSE '离职'
    END AS employment_status
FROM 
    employees e
LEFT JOIN 
    departments d ON e.department_id = d.department_id
LEFT JOIN 
    employees m ON e.manager_id = m.employee_id
WHERE 
    e.employee_id = 1;

-- 2. 获取部门员工列表
SELECT 
    e.employee_id,
    e.employee_number,
    CONCAT(e.first_name, ' ', e.last_name) AS full_name,
    e.job_title,
    e.email,
    e.hire_date,
    TIMESTAMPDIFF(YEAR, e.hire_date, CURDATE()) AS years_of_service,
    CASE 
        WHEN e.is_active THEN '在职'
        ELSE '离职'
    END AS employment_status
FROM 
    employees e
WHERE 
    e.department_id = 1 AND e.is_active = TRUE
ORDER BY 
    e.hire_date DESC;

-- 3. 获取员工月度考勤统计
SELECT 
    e.employee_id,
    CONCAT(e.first_name, ' ', e.last_name) AS full_name,
    COUNT(a.attendance_id) AS total_days,
    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS present_days,
    SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) AS absent_days,
    SUM(CASE WHEN a.status = 'late' THEN 1 ELSE 0 END) AS late_days,
    SUM(CASE WHEN a.status = 'early_leave' THEN 1 ELSE 0 END) AS early_leave_days,
    SUM(CASE WHEN a.status IN ('sick_leave', 'annual_leave') THEN 1 ELSE 0 END) AS leave_days,
    SUM(a.work_hours) AS total_work_hours,
    SUM(a.overtime_hours) AS total_overtime_hours
FROM 
    employees e
LEFT JOIN 
    attendance a ON e.employee_id = a.employee_id
WHERE 
    e.is_active = TRUE
    AND a.attendance_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    AND a.attendance_date < DATE_ADD(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 1 MONTH)
GROUP BY 
    e.employee_id
ORDER BY 
    e.employee_id;

-- 4. 获取部门薪资统计
SELECT 
    d.department_id,
    d.name AS department_name,
    COUNT(e.employee_id) AS employee_count,
    MIN(e.salary) AS min_salary,
    MAX(e.salary) AS max_salary,
    AVG(e.salary) AS avg_salary,
    SUM(e.salary) AS total_salary
FROM 
    departments d
LEFT JOIN 
    employees e ON d.department_id = e.department_id AND e.is_active = TRUE
GROUP BY 
    d.department_id
ORDER BY 
    avg_salary DESC;