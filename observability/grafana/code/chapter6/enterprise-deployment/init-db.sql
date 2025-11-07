-- Grafana 企业版数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_user_login ON user (login);
CREATE INDEX IF NOT EXISTS idx_dashboard_org_id ON dashboard (org_id);
CREATE INDEX IF NOT EXISTS idx_data_source_org_id ON data_source (org_id);
CREATE INDEX IF NOT EXISTS idx_alert_org_id ON alert (org_id);
CREATE INDEX IF NOT EXISTS idx_annotation_time ON annotation (time_end, time_start);

-- 创建用户角色表（用于更精细的权限控制）
CREATE TABLE IF NOT EXISTS user_role (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    org_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, org_id)
);

-- 创建审计日志表（用于企业版安全审计）
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    org_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建用户会话表（用于会话管理）
CREATE TABLE IF NOT EXISTS user_session (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    session_token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    ip_address INET,
    user_agent TEXT,
    active BOOLEAN DEFAULT TRUE,
    UNIQUE(session_token)
);

-- 插入默认管理员角色
INSERT INTO user_role (user_id, org_id, role) 
SELECT u.id, o.id, 'Admin' 
FROM "user" u, org o 
WHERE u.login = 'admin' AND o.name = 'Main Org.'
ON CONFLICT (user_id, org_id) DO NOTHING;

-- 创建更新时间戳的函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建触发器，自动更新 updated_at 字段
CREATE TRIGGER update_user_role_updated_at BEFORE UPDATE
    ON user_role FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建清理过期会话的函数
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM user_session WHERE expires_at < NOW() OR active = FALSE;
END;
$$ LANGUAGE plpgsql;

-- 创建定时任务，每天清理过期会话
SELECT cron.schedule('cleanup-sessions', '0 3 * * *', 'SELECT cleanup_expired_sessions();');