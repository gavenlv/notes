-- 初始化SQL脚本
-- 用于在Docker容器启动后初始化Doris集群

-- 创建示例数据库
CREATE DATABASE IF NOT EXISTS demo;

-- 创建管理员用户
CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%';

-- 创建只读用户
CREATE USER IF NOT EXISTS 'readonly'@'%' IDENTIFIED BY 'readonly123';
GRANT SELECT_PRIV ON demo.* TO 'readonly'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 显示集群状态
SHOW FRONTENDS;
SHOW BACKENDS;