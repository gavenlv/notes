-- 创建Grafana数据库和用户
CREATE DATABASE IF NOT EXISTS grafana CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建Grafana用户并授权
GRANT ALL PRIVILEGES ON grafana.* TO 'grafana'@'%' IDENTIFIED BY 'grafana123';
GRANT ALL PRIVILEGES ON grafana.* TO 'grafana'@'localhost' IDENTIFIED BY 'grafana123';

-- 刷新权限
FLUSH PRIVILEGES;

-- 创建性能监控表
CREATE TABLE IF NOT EXISTS grafana.performance_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instance_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tags JSON,
    INDEX idx_instance_metric (instance_name, metric_name),
    INDEX idx_timestamp (timestamp)
);

-- 创建用户活动表
CREATE TABLE IF NOT EXISTS grafana.user_activity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    dashboard_id INT,
    panel_id INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details JSON,
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_action (action)
);

-- 创建插件管理表
CREATE TABLE IF NOT EXISTS grafana.plugin_management (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plugin_id VARCHAR(200) NOT NULL,
    plugin_name VARCHAR(200) NOT NULL,
    version VARCHAR(50) NOT NULL,
    status ENUM('active', 'inactive', 'pending') DEFAULT 'active',
    installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    configuration JSON,
    UNIQUE KEY uk_plugin_id (plugin_id)
);

-- 插入示例数据
INSERT IGNORE INTO grafana.performance_metrics (instance_name, metric_name, metric_value, tags) VALUES
('grafana-primary', 'dashboard_load_time', 0.85, '{"environment": "production", "dashboard": "system-overview"}'),
('grafana-primary', 'query_execution_time', 0.12, '{"environment": "production", "datasource": "prometheus"}'),
('grafana-secondary', 'dashboard_load_time', 0.92, '{"environment": "production", "dashboard": "system-overview"}'),
('grafana-secondary', 'query_execution_time', 0.15, '{"environment": "production", "datasource": "prometheus"}');

INSERT IGNORE INTO grafana.user_activity (user_id, user_name, action, dashboard_id, panel_id, details) VALUES
(1, 'admin', 'view_dashboard', 1, NULL, '{"dashboard_title": "System Overview"}'),
(1, 'admin', 'edit_panel', 1, 1, '{"panel_title": "CPU Usage", "changes": ["updated_query"]}'),
(2, 'viewer', 'view_dashboard', 1, NULL, '{"dashboard_title": "System Overview"}');

INSERT IGNORE INTO grafana.plugin_management (plugin_id, plugin_name, version, status, configuration) VALUES
('grafana-clock-panel', 'Clock Panel', '2.1.2', 'active', '{"timezone": "Asia/Shanghai", "format": "YYYY-MM-DD HH:mm:ss"}'),
('grafana-piechart-panel', 'Pie Chart Panel', '1.6.4', 'active', '{"showLegend": true, "legendType": "right"}'),
('grafana-worldmap-panel', 'Worldmap Panel', '0.3.5', 'inactive', '{"centerLat": 0, "centerLon": 0}');