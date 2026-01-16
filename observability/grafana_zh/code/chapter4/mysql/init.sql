-- 第4章：查询语言和数据处理 - MySQL数据库初始化

-- 创建数据库
CREATE DATABASE IF NOT EXISTS query_demo;
USE query_demo;

-- 创建系统指标表
CREATE TABLE IF NOT EXISTS system_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    hostname VARCHAR(50) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    tags JSON,
    INDEX idx_timestamp (timestamp),
    INDEX idx_hostname (hostname),
    INDEX idx_metric_name (metric_name)
);

-- 创建应用日志表
CREATE TABLE IF NOT EXISTS application_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    app_name VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL,
    message TEXT,
    duration_ms INT,
    INDEX idx_timestamp (timestamp),
    INDEX idx_app_name (app_name),
    INDEX idx_level (level)
);

-- 创建业务指标表
CREATE TABLE IF NOT EXISTS business_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    product VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    revenue DECIMAL(10,2) NOT NULL,
    users_count INT NOT NULL,
    conversion_rate DECIMAL(5,4) NOT NULL,
    INDEX idx_timestamp (timestamp),
    INDEX idx_product (product),
    INDEX idx_region (region)
);

-- 插入系统指标示例数据
INSERT INTO system_metrics (timestamp, hostname, metric_name, metric_value, tags) VALUES
('2023-01-01 00:00:00', 'web-01', 'cpu_usage', 25.5, '{"environment": "production", "team": "infra"}'),
('2023-01-01 00:00:00', 'web-01', 'memory_usage', 45.2, '{"environment": "production", "team": "infra"}'),
('2023-01-01 00:00:00', 'web-01', 'disk_usage', 60.1, '{"environment": "production", "team": "infra"}'),
('2023-01-01 00:15:00', 'web-01', 'cpu_usage', 30.2, '{"environment": "production", "team": "infra"}'),
('2023-01-01 00:15:00', 'web-01', 'memory_usage', 50.1, '{"environment": "production", "team": "infra"}'),
('2023-01-01 00:15:00', 'web-01', 'disk_usage', 55.3, '{"environment": "production", "team": "infra"}'),
('2023-01-01 00:00:00', 'db-01', 'cpu_usage', 15.8, '{"environment": "production", "team": "dba"}'),
('2023-01-01 00:00:00', 'db-01', 'memory_usage', 65.7, '{"environment": "production", "team": "dba"}'),
('2023-01-01 00:00:00', 'db-01', 'disk_usage', 75.2, '{"environment": "production", "team": "dba"}');

-- 插入应用日志示例数据
INSERT INTO application_logs (timestamp, app_name, level, message, duration_ms) VALUES
('2023-01-01 00:00:00', 'web-api', 'INFO', 'Application started successfully', 0),
('2023-01-01 00:05:00', 'web-api', 'INFO', 'Processing request from 192.168.1.100', 125),
('2023-01-01 00:10:00', 'web-api', 'WARN', 'Slow database query detected', 450),
('2023-01-01 00:15:00', 'web-api', 'ERROR', 'Database connection timeout', 5000),
('2023-01-01 00:20:00', 'auth-service', 'INFO', 'User authentication successful', 45),
('2023-01-01 00:25:00', 'auth-service', 'ERROR', 'Invalid credentials provided', 30),
('2023-01-01 00:30:00', 'payment-service', 'INFO', 'Payment processed successfully', 120),
('2023-01-01 00:35:00', 'payment-service', 'WARN', 'Payment gateway slow response', 800);

-- 插入业务指标示例数据
INSERT INTO business_metrics (timestamp, product, region, revenue, users_count, conversion_rate) VALUES
('2023-01-01 00:00:00', 'Product A', 'North America', 12500.50, 1250, 0.0250),
('2023-01-01 00:00:00', 'Product A', 'Europe', 9800.75, 980, 0.0225),
('2023-01-01 00:00:00', 'Product B', 'North America', 8500.25, 850, 0.0185),
('2023-01-01 00:00:00', 'Product B', 'Asia', 11200.00, 1120, 0.0210),
('2023-01-01 01:00:00', 'Product A', 'North America', 13200.80, 1320, 0.0265),
('2023-01-01 01:00:00', 'Product A', 'Europe', 10100.25, 1010, 0.0230),
('2023-01-01 01:00:00', 'Product C', 'Global', 15600.80, 1560, 0.0280);

-- 创建聚合视图
CREATE VIEW system_metrics_hourly AS
SELECT 
    DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
    hostname,
    metric_name,
    AVG(metric_value) as avg_value,
    MAX(metric_value) as max_value,
    MIN(metric_value) as min_value,
    COUNT(*) as data_points
FROM system_metrics
GROUP BY hour, hostname, metric_name;

CREATE VIEW application_performance AS
SELECT 
    DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
    app_name,
    level,
    COUNT(*) as log_count,
    AVG(duration_ms) as avg_duration,
    MAX(duration_ms) as max_duration
FROM application_logs
GROUP BY hour, app_name, level;

CREATE VIEW business_metrics_daily AS
SELECT 
    DATE(timestamp) as date,
    product,
    region,
    SUM(revenue) as total_revenue,
    SUM(users_count) as total_users,
    AVG(conversion_rate) as avg_conversion_rate
FROM business_metrics
GROUP BY date, product, region;

-- 创建用户并授权
CREATE USER IF NOT EXISTS 'grafana'@'%' IDENTIFIED BY 'grafana123';
GRANT SELECT ON query_demo.* TO 'grafana'@'%';
FLUSH PRIVILEGES;

-- 显示创建结果
SELECT 'Database initialization completed successfully!' as status;
SELECT COUNT(*) as system_metrics_count FROM system_metrics;
SELECT COUNT(*) as application_logs_count FROM application_logs;
SELECT COUNT(*) as business_metrics_count FROM business_metrics;

SHOW TABLES;