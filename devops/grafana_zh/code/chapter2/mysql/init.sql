-- 初始化MySQL数据库，用于Grafana数据源演示

-- 创建示例数据库
CREATE DATABASE IF NOT EXISTS grafana_demo;
USE grafana_demo;

-- 创建示例表：系统指标
CREATE TABLE IF NOT EXISTS system_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    hostname VARCHAR(50) NOT NULL,
    cpu_usage DECIMAL(5,2) DEFAULT 0.0,
    memory_usage DECIMAL(5,2) DEFAULT 0.0,
    disk_usage DECIMAL(5,2) DEFAULT 0.0,
    network_rx BIGINT DEFAULT 0,
    network_tx BIGINT DEFAULT 0
);

-- 创建示例表：应用指标
CREATE TABLE IF NOT EXISTS application_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_name VARCHAR(50) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    response_time DECIMAL(8,3) DEFAULT 0.0,
    status_code INT DEFAULT 200,
    request_count INT DEFAULT 1
);

-- 创建示例表：业务指标
CREATE TABLE IF NOT EXISTS business_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    product VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    revenue DECIMAL(10,2) DEFAULT 0.0,
    users_count INT DEFAULT 0,
    conversion_rate DECIMAL(5,4) DEFAULT 0.0
);

-- 插入示例数据：系统指标
INSERT INTO system_metrics (hostname, cpu_usage, memory_usage, disk_usage, network_rx, network_tx) VALUES
('server-01', 25.5, 45.2, 60.1, 1024000, 512000),
('server-02', 30.2, 50.1, 55.3, 1536000, 768000),
('server-03', 22.8, 42.7, 62.5, 896000, 448000);

-- 插入示例数据：应用指标
INSERT INTO application_metrics (app_name, endpoint, response_time, status_code, request_count) VALUES
('web-api', '/api/users', 125.5, 200, 150),
('web-api', '/api/products', 89.3, 200, 200),
('web-api', '/api/orders', 156.7, 200, 75),
('auth-service', '/auth/login', 45.2, 200, 300),
('auth-service', '/auth/verify', 32.1, 200, 250);

-- 插入示例数据：业务指标
INSERT INTO business_metrics (product, region, revenue, users_count, conversion_rate) VALUES
('Product A', 'North America', 12500.50, 1250, 0.0250),
('Product A', 'Europe', 9800.75, 980, 0.0225),
('Product B', 'North America', 8500.25, 850, 0.0185),
('Product B', 'Asia', 11200.00, 1120, 0.0210),
('Product C', 'Global', 15600.80, 1560, 0.0280);

-- 创建视图：按时间聚合的指标
CREATE VIEW system_metrics_hourly AS
SELECT 
    DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
    hostname,
    AVG(cpu_usage) as avg_cpu_usage,
    AVG(memory_usage) as avg_memory_usage,
    AVG(disk_usage) as avg_disk_usage,
    SUM(network_rx) as total_network_rx,
    SUM(network_tx) as total_network_tx
FROM system_metrics
GROUP BY hour, hostname;

-- 创建视图：应用性能指标
CREATE VIEW application_performance AS
SELECT 
    DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
    app_name,
    endpoint,
    AVG(response_time) as avg_response_time,
    COUNT(*) as total_requests,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
FROM application_metrics
GROUP BY hour, app_name, endpoint;

-- 创建用户并授权
CREATE USER IF NOT EXISTS 'grafana'@'%' IDENTIFIED BY 'grafana123';
GRANT SELECT ON grafana_demo.* TO 'grafana'@'%';
FLUSH PRIVILEGES;

-- 显示创建的表和视图
SHOW TABLES;
SELECT 'Database initialization completed successfully!' as status;