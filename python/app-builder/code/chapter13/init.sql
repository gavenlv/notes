-- 数据库初始化脚本
-- 创建数据库扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建应用角色和权限（如果需要）
-- CREATE ROLE flask_app_role;
-- GRANT CONNECT ON DATABASE flaskdb TO flask_app_role;

-- 可以在这里添加其他数据库初始化逻辑