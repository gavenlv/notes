-- 初始化数据库和用户
-- 连接方式: mysql -h 127.0.0.1 -P 9030 -uroot

-- 创建示例数据库
CREATE DATABASE IF NOT EXISTS demo;
USE demo;

-- 创建管理员用户
CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%';

-- 创建只读用户
CREATE USER IF NOT EXISTS 'readonly'@'%' IDENTIFIED BY 'readonly123';
GRANT SELECT_PRIV ON demo.* TO 'readonly'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 显示当前用户
SELECT CURRENT_USER();

-- 显示所有数据库
SHOW DATABASES;

-- 显示所有用户
SHOW ALL GRANTS;