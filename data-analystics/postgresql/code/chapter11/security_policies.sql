-- ================================================
-- PostgreSQL第11章：安全策略管理
-- ================================================
-- 本文件演示PostgreSQL的安全策略管理功能

-- ================================================
-- 1. 基础安全策略测试环境
-- ================================================

-- 1.1 创建安全策略测试环境
DROP TABLE IF EXISTS security_test.audit_events CASCADE;
DROP TABLE IF EXISTS security_test.sensitive_data CASCADE;
DROP TABLE IF EXISTS security_test.user_sessions CASCADE;
DROP TABLE IF EXISTS security_test.data_access_log CASCADE;
DROP SCHEMA IF EXISTS security_test CASCADE;

-- 创建测试模式
CREATE SCHEMA security_test;

-- 创建审计事件表
CREATE TABLE security_test.audit_events (
    event_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(100),
    table_name VARCHAR(100),
    operation VARCHAR(20), -- INSERT, UPDATE, DELETE, SELECT
    record_id VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    risk_level VARCHAR(20) DEFAULT 'LOW',
    reviewed BOOLEAN DEFAULT FALSE,
    reviewer VARCHAR(100),
    review_notes TEXT
);

-- 创建敏感数据表
CREATE TABLE security_test.sensitive_data (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(200) NOT NULL,
    credit_card_hash VARCHAR(128),
    social_security_hash VARCHAR(128),
    birth_date DATE,
    salary_grade VARCHAR(20),
    performance_rating INTEGER CHECK (performance_rating BETWEEN 1 AND 5),
    medical_info JSONB,
    financial_info JSONB,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建用户会话表
CREATE TABLE security_test.user_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failure_count INTEGER DEFAULT 0,
    lockout_time TIMESTAMP,
    risk_score INTEGER DEFAULT 0,
    session_token VARCHAR(256)
);

-- 创建数据访问日志表
CREATE TABLE security_test.data_access_log (
    access_id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    table_name VARCHAR(100),
    access_type VARCHAR(20), -- READ, WRITE, DELETE
    record_count INTEGER,
    ip_address INET,
    user_agent TEXT,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_classification VARCHAR(20), -- PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    encryption_status VARCHAR(20), -- ENCRYPTED, PLAINTEXT, HASHED
    compliance_flags TEXT[],
    retention_period INTEGER, -- days
    anonymization_applied BOOLEAN DEFAULT FALSE
);

-- 插入测试数据
INSERT INTO security_test.sensitive_data (user_email, credit_card_hash, social_security_hash, birth_date, salary_grade, performance_rating, medical_info, financial_info) VALUES
    ('user1@example.com', 'cc_hash_001', 'ssn_hash_001', '1980-05-15', 'SENIOR', 4, '{"allergies": ["penicillin"], "conditions": ["diabetes"]}', '{"annual_income": 75000, "investments": ["401k", "stocks"]}'),
    ('user2@example.com', 'cc_hash_002', 'ssn_hash_002', '1975-08-22', 'MIDDLE', 3, '{"allergies": ["none"], "conditions": []}', '{"annual_income": 65000, "investments": ["401k"]}'),
    ('user3@example.com', 'cc_hash_003', 'ssn_hash_003', '1990-12-03', 'JUNIOR', 5, '{"allergies": ["shellfish"], "conditions": ["hypertension"]}', '{"annual_income": 55000, "investments": []}'),
    ('user4@example.com', 'cc_hash_004', 'ssn_hash_004', '1985-03-18', 'SENIOR', 2, '{"allergies": ["none"], "conditions": ["asthma"]}', '{"annual_income": 80000, "investments": ["401k", "stocks", "bonds"]}'),
    ('user5@example.com', 'cc_hash_005', 'ssn_hash_005', '1978-09-27', 'MIDDLE', 4, '{"allergies": ["latex"], "conditions": []}', '{"annual_income": 70000, "investments": ["401k"]}');

INSERT INTO security_test.user_sessions (session_id, user_id, ip_address, user_agent, risk_score) VALUES
    ('sess_001', 'admin_user', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 10),
    ('sess_002', 'regular_user', '192.168.1.101', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', 30),
    ('sess_003', 'sensitive_user', '192.168.1.102', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36', 80),
    ('sess_004', 'hr_user', '192.168.1.103', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 25),
    ('sess_005', 'finance_user', '192.168.1.104', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', 45);

-- 1.2 创建安全策略角色
CREATE ROLE security_admin NOLOGIN;
CREATE ROLE security_auditor NOLOGIN;
CREATE ROLE data_protection_officer NOLOGIN;
CREATE ROLE compliance_officer NOLOGIN;
CREATE ROLE security_operator NOLOGIN;

-- 1.3 授予基础权限
GRANT CONNECT ON DATABASE postgres TO security_admin, security_auditor, data_protection_officer, compliance_officer, security_operator;
GRANT USAGE ON SCHEMA security_test TO security_admin, security_auditor, data_protection_officer, compliance_officer, security_operator;
GRANT SELECT ON ALL TABLES IN SCHEMA security_test TO security_auditor, compliance_officer, security_operator;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA security_test TO security_admin, data_protection_officer;

-- ================================================
-- 2. 数据分类和访问控制策略
-- ================================================

-- 2.1 创建数据分类视图
CREATE VIEW security_test.data_classification_view AS
SELECT 
    schemaname,
    tablename,
    tableowner,
    CASE 
        WHEN tablename IN ('sensitive_data', 'audit_events') THEN 'RESTRICTED'
        WHEN tablename IN ('user_sessions', 'data_access_log') THEN 'CONFIDENTIAL'
        ELSE 'INTERNAL'
    END as classification_level,
    CASE 
        WHEN tablename IN ('sensitive_data', 'audit_events') THEN 'Personal data, financial information, medical records'
        WHEN tablename IN ('user_sessions', 'data_access_log') THEN 'User authentication and access tracking data'
        ELSE 'Standard business data'
    END as description,
    CASE 
        WHEN tablename IN ('sensitive_data', 'audit_events') THEN 90
        WHEN tablename IN ('user_sessions', 'data_access_log') THEN 365
        ELSE 2555
    END as retention_days
FROM pg_tables 
WHERE schemaname = 'security_test';

-- 2.2 创建数据分类管理函数
CREATE OR REPLACE FUNCTION get_data_classification(
    p_table_name TEXT
)
RETURNS TEXT AS $$
DECLARE
    classification TEXT;
BEGIN
    SELECT classification_level INTO classification
    FROM security_test.data_classification_view
    WHERE tablename = p_table_name;
    
    RETURN COALESCE(classification, 'UNCLASSIFIED');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2.3 创建基于分类的访问控制函数
CREATE OR REPLACE FUNCTION check_data_access_permission(
    p_user_id TEXT,
    p_table_name TEXT,
    p_operation TEXT,
    p_user_classification TEXT DEFAULT 'INTERNAL'
)
RETURNS BOOLEAN AS $$
DECLARE
    table_classification TEXT;
    has_permission BOOLEAN := FALSE;
BEGIN
    -- 获取表的分类级别
    SELECT classification_level INTO table_classification
    FROM security_test.data_classification_view
    WHERE tablename = p_table_name;
    
    -- 根据用户权限级别和表分类级别检查访问权限
    CASE p_user_classification
        WHEN 'SECURITY_ADMIN' THEN
            has_permission := TRUE; -- 安全管理员可以访问所有数据
            
        WHEN 'DATA_PROTECTION_OFFICER' THEN
            has_permission := table_classification IN ('RESTRICTED', 'CONFIDENTIAL', 'INTERNAL');
            
        WHEN 'SECURITY_AUDITOR' THEN
            has_permission := p_operation = 'SELECT';
            
        WHEN 'COMPLIANCE_OFFICER' THEN
            has_permission := p_operation IN ('SELECT', 'UPDATE');
            
        WHEN 'USER' THEN
            CASE table_classification
                WHEN 'PUBLIC' THEN has_permission := TRUE;
                WHEN 'INTERNAL' THEN has_permission := p_operation IN ('SELECT', 'UPDATE');
                WHEN 'CONFIDENTIAL' THEN has_permission := p_operation = 'SELECT';
                WHEN 'RESTRICTED' THEN has_permission := FALSE;
                ELSE has_permission := FALSE;
            END CASE;
            
        ELSE
            has_permission := FALSE;
    END CASE;
    
    -- 记录访问尝试
    INSERT INTO security_test.data_access_log (
        user_id, table_name, access_type, ip_address, access_time, 
        data_classification, compliance_flags
    ) VALUES (
        p_user_id, p_table_name, p_operation, inet_client_addr(), 
        CURRENT_TIMESTAMP, table_classification,
        ARRAY[ CASE WHEN has_permission THEN 'ALLOWED' ELSE 'DENIED' END ]
    );
    
    RETURN has_permission;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 3. 审计和监控策略
-- ================================================

-- 3.1 创建审计策略触发器函数
CREATE OR REPLACE FUNCTION security_audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    current_user_role TEXT;
    risk_level TEXT;
    audit_data JSONB;
BEGIN
    -- 确定当前用户角色
    current_user_role := current_user;
    
    -- 确定风险级别
    CASE TG_OP
        WHEN 'DELETE' THEN
            risk_level := 'HIGH';
            audit_data := row_to_json(OLD);
        WHEN 'UPDATE' THEN
            risk_level := 'MEDIUM';
            audit_data := jsonb_build_object('old', row_to_json(OLD), 'new', row_to_json(NEW));
        WHEN 'INSERT' THEN
            risk_level := 'LOW';
            audit_data := row_to_json(NEW);
        ELSE
            risk_level := 'INFO';
            audit_data := NULL;
    END CASE;
    
    -- 插入审计记录
    INSERT INTO security_test.audit_events (
        event_type,
        user_id,
        table_name,
        operation,
        record_id,
        old_values,
        new_values,
        ip_address,
        user_agent,
        session_id,
        risk_level
    ) VALUES (
        TG_OP,
        current_user_role,
        TG_TABLE_NAME,
        TG_OP,
        COALESCE(NEW.id::TEXT, OLD.id::TEXT),
        CASE WHEN TG_OP = 'UPDATE' THEN row_to_json(OLD) WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN row_to_json(NEW) ELSE NULL END,
        inet_client_addr(),
        current_setting('request.headers', true),
        current_setting('request.jwt.claims', true),
        risk_level
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3.2 创建高风险操作检测函数
CREATE OR REPLACE FUNCTION detect_high_risk_operations(
    p_time_window INTERVAL DEFAULT '1 hour'
)
RETURNS TABLE(
    user_id TEXT,
    table_name TEXT,
    operation_count BIGINT,
    risk_pattern TEXT,
    last_operation TIMESTAMP,
    recommendation TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ae.user_id,
        ae.table_name,
        COUNT(*) as operation_count,
        'MULTIPLE_' || ae.operation || '_OPERATIONS' as risk_pattern,
        MAX(ae.timestamp) as last_operation,
        CASE 
            WHEN COUNT(*) > 10 THEN 'Review user activities - high frequency operations'
            WHEN COUNT(*) > 5 THEN 'Monitor user activities - elevated frequency'
            ELSE 'Normal activity pattern'
        END as recommendation
    FROM security_test.audit_events ae
    WHERE ae.timestamp > CURRENT_TIMESTAMP - p_time_window
    AND ae.risk_level = 'HIGH'
    GROUP BY ae.user_id, ae.table_name, ae.operation
    HAVING COUNT(*) >= 3
    ORDER BY operation_count DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3.3 创建异常访问模式检测函数
CREATE OR REPLACE FUNCTION detect_anomalous_access(
    p_user_id TEXT DEFAULT NULL,
    p_hours_back INTEGER DEFAULT 24
)
RETURNS TABLE(
    access_type TEXT,
    description TEXT,
    severity TEXT,
    user_id TEXT,
    detection_time TIMESTAMP,
    details JSONB
) AS $$
DECLARE
    user_filter TEXT;
BEGIN
    -- 构建用户过滤条件
    IF p_user_id IS NOT NULL THEN
        user_filter := ' AND user_id = ' || quote_literal(p_user_id);
    ELSE
        user_filter := '';
    END IF;
    
    -- 检测异常时间段访问
    RETURN QUERY
    SELECT 
        'TIME_BASED_ANOMALY'::TEXT as access_type,
        'Access during unusual hours (outside 8AM-6PM)'::TEXT as description,
        'MEDIUM'::TEXT as severity,
        user_sessions.user_id::TEXT,
        CURRENT_TIMESTAMP as detection_time,
        jsonb_build_object(
            'session_time', user_sessions.login_time,
            'ip_address', user_sessions.ip_address,
            'usual_hours_violation', 
            EXTRACT(hour FROM user_sessions.login_time) NOT BETWEEN 8 AND 18
        ) as details
    FROM security_test.user_sessions
    WHERE EXTRACT(hour FROM login_time) NOT BETWEEN 8 AND 18
    AND user_sessions.login_time > CURRENT_TIMESTAMP - (p_hours_back || ' hours')::INTERVAL
    AND user_sessions.risk_score > 50;
    
    -- 检测IP异常
    RETURN QUERY
    SELECT 
        'IP_BASED_ANOMALY'::TEXT as access_type,
        'Access from multiple different IP addresses'::TEXT as description,
        'HIGH'::TEXT as severity,
        ip_anomaly.user_id::TEXT,
        CURRENT_TIMESTAMP as detection_time,
        jsonb_build_object(
            'ip_addresses', ip_anomaly.ip_list,
            'location_variance', 'Multiple geographic locations detected'
        ) as details
    FROM (
        SELECT 
            user_id,
            array_agg(DISTINCT ip_address) as ip_list,
            COUNT(DISTINCT ip_address) as ip_count
        FROM security_test.user_sessions
        WHERE user_sessions.login_time > CURRENT_TIMESTAMP - (p_hours_back || ' hours')::INTERVAL
        GROUP BY user_id
        HAVING COUNT(DISTINCT ip_address) > 1
        AND COUNT(DISTINCT ip_address) >= 3
    ) ip_anomaly;
    
    -- 检测高频率访问
    RETURN QUERY
    SELECT 
        'FREQUENCY_ANOMALY'::TEXT as access_type,
        'Unusually high number of data access requests'::TEXT as description,
        'MEDIUM'::TEXT as severity,
        freq_anomaly.user_id::TEXT,
        CURRENT_TIMESTAMP as detection_time,
        jsonb_build_object(
            'access_count', freq_anomaly.access_count,
            'time_period', p_hours_back || ' hours',
            'threshold_exceeded', freq_anomaly.access_count > (p_hours_back * 10)
        ) as details
    FROM (
        SELECT 
            user_id,
            COUNT(*) as access_count
        FROM security_test.data_access_log
        WHERE access_time > CURRENT_TIMESTAMP - (p_hours_back || ' hours')::INTERVAL
        GROUP BY user_id
        HAVING COUNT(*) > (p_hours_back * 5)
    ) freq_anomaly;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 4. 数据脱敏和隐私保护策略
-- ================================================

-- 4.1 创建数据脱敏函数
CREATE OR REPLACE FUNCTION anonymize_sensitive_data(
    p_table_name TEXT,
    p_column_name TEXT,
    p_anonymization_type TEXT
)
RETURNS TEXT AS $$
DECLARE
    sql_statement TEXT;
    result_message TEXT;
    record_count INTEGER;
BEGIN
    -- 检查权限
    IF NOT check_data_access_permission(current_user, p_table_name, 'UPDATE', 'SECURITY_ADMIN') THEN
        RETURN 'Error: Insufficient permissions for data anonymization';
    END IF;
    
    -- 根据脱敏类型构建SQL
    CASE p_anonymization_type
        WHEN 'EMAIL_MASK' THEN
            sql_statement := format(
                'UPDATE %I SET %I = regexp_replace(%I, ''([^@]+)@'', ''***@'')',
                p_table_name, p_column_name, p_column_name
            );
            
        WHEN 'PHONE_MASK' THEN
            sql_statement := format(
                'UPDATE %I SET %I = regexp_replace(%I, ''(\d{3})\d{3}(\d{4})'', ''\1-***-\2'')',
                p_table_name, p_column_name, p_column_name
            );
            
        WHEN 'CREDIT_CARD_MASK' THEN
            sql_statement := format(
                'UPDATE %I SET %I = regexp_replace(%I, ''(\d{4})\d{8,}(\d{4})'', ''\1-***-****-****-\2'')',
                p_table_name, p_column_name, p_column_name
            );
            
        WHEN 'SSN_MASK' THEN
            sql_statement := format(
                'UPDATE %I SET %I = regexp_replace(%I, ''(\d{3})\d{2}(\d{4})'', ''\1-**-\2'')',
                p_table_name, p_column_name, p_column_name
            );
            
        WHEN 'HASH' THEN
            sql_statement := format(
                'UPDATE %I SET %I = encode(digest(%I::TEXT || ''salt'', ''sha256''), ''hex'')',
                p_table_name, p_column_name, p_column_name
            );
            
        WHEN 'RANDOM' THEN
            sql_statement := format(
                'UPDATE %I SET %I = ''ANONYMIZED_'' || id::TEXT',
                p_table_name, p_column_name
            );
            
        ELSE
            RETURN 'Error: Unknown anonymization type: ' || p_anonymization_type;
    END CASE;
    
    -- 执行脱敏操作
    BEGIN
        EXECUTE sql_statement;
        
        -- 获取影响的行数
        GET DIAGNOSTICS record_count = ROW_COUNT;
        
        -- 记录脱敏操作
        INSERT INTO security_test.audit_events (
            event_type,
            user_id,
            table_name,
            operation,
            risk_level
        ) VALUES (
            'DATA_ANONYMIZATION',
            current_user,
            p_table_name,
            'UPDATE',
            'HIGH'
        );
        
        result_message := 'Success: Anonymized ' || record_count || ' records using ' || p_anonymization_type;
        
    EXCEPTION WHEN OTHERS THEN
        result_message := 'Error: ' || SQLERRM;
    END;
    
    RETURN result_message;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4.2 创建隐私合规检查函数
CREATE OR REPLACE FUNCTION check_privacy_compliance(
    p_table_name TEXT DEFAULT NULL
)
RETURNS TABLE(
    compliance_area TEXT,
    status TEXT,
    details TEXT,
    action_required TEXT,
    priority TEXT
) AS $$
BEGIN
    -- 检查加密状态
    RETURN QUERY
    SELECT 
        'DATA_ENCRYPTION'::TEXT as compliance_area,
        CASE 
            WHEN EXISTS(
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'security_test' 
                AND table_name = p_table_name 
                AND data_type IN ('bytea', 'text')
                AND column_name LIKE '%_hash'
            ) THEN 'COMPLIANT'
            ELSE 'NON_COMPLIANT'
        END as status,
        'Hashed sensitive fields detected: ' || 
        string_agg(column_name, ', ' ORDER BY column_name) as details,
        'Implement field-level encryption for sensitive data' as action_required,
        'HIGH'::TEXT as priority
    FROM information_schema.columns
    WHERE table_schema = 'security_test'
    AND (p_table_name IS NULL OR table_name = p_table_name)
    AND column_name LIKE '%_hash'
    GROUP BY table_name;
    
    -- 检查访问日志记录
    RETURN QUERY
    SELECT 
        'AUDIT_LOGGING'::TEXT as compliance_area,
        CASE 
            WHEN EXISTS(
                SELECT 1 FROM security_test.audit_events 
                WHERE table_name = COALESCE(p_table_name, table_name)
                AND timestamp > CURRENT_DATE - INTERVAL '30 days'
            ) THEN 'COMPLIANT'
            ELSE 'NON_COMPLIANT'
        END as status,
        'Audit events logged for table: ' || COALESCE(p_table_name, 'ALL TABLES') as details,
        'Ensure all data access is logged and monitored' as action_required,
        'MEDIUM'::TEXT as priority;
    
    -- 检查数据保留策略
    RETURN QUERY
    SELECT 
        'DATA_RETENTION'::TEXT as compliance_area,
        CASE 
            WHEN EXISTS(
                SELECT 1 FROM security_test.data_access_log
                WHERE table_name = COALESCE(p_table_name, table_name)
                AND access_time < CURRENT_DATE - INTERVAL '1 year'
            ) THEN 'NON_COMPLIANT'
            ELSE 'COMPLIANT'
        END as status,
        'Check data retention policy compliance' as details,
        'Implement automated data retention and deletion' as action_required,
        'LOW'::TEXT as priority;
    
    -- 检查匿名化处理
    RETURN QUERY
    SELECT 
        'DATA_ANONYMIZATION'::TEXT as compliance_area,
        CASE 
            WHEN EXISTS(
                SELECT 1 FROM security_test.sensitive_data
                WHERE user_email LIKE '***@%'
                OR credit_card_hash = 'ANONYMIZED'
            ) THEN 'PARTIAL'
            ELSE 'NOT_IMPLEMENTED'
        END as status,
        'Anonymization status for sensitive fields' as details,
        'Apply data anonymization for non-production environments' as action_required,
        'MEDIUM'::TEXT as priority;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 5. 访问控制策略
-- ================================================

-- 5.1 创建基于时间的访问控制
CREATE OR REPLACE FUNCTION check_time_based_access(
    p_user_id TEXT,
    p_allowed_hours INTEGER[] DEFAULT ARRAY[8,9,10,11,12,13,14,15,16,17]
)
RETURNS BOOLEAN AS $$
DECLARE
    current_hour INTEGER;
    is_allowed BOOLEAN;
BEGIN
    current_hour := EXTRACT(hour FROM CURRENT_TIMESTAMP);
    
    -- 检查用户权限级别
    IF current_user IN ('security_admin', 'data_protection_officer') THEN
        RETURN TRUE; -- 管理员不受时间限制
    END IF;
    
    -- 检查当前时间是否在允许的时间段内
    is_allowed := current_hour = ANY(p_allowed_hours);
    
    -- 记录访问尝试
    INSERT INTO security_test.data_access_log (
        user_id, access_type, access_time, 
        data_classification, compliance_flags
    ) VALUES (
        p_user_id, 'TIME_CHECK', CURRENT_TIMESTAMP,
        'CONTROL', ARRAY[ CASE WHEN is_allowed THEN 'ALLOWED' ELSE 'DENIED' END ]
    );
    
    RETURN is_allowed;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5.2 创建基于地理位置的访问控制
CREATE OR REPLACE FUNCTION check_geographic_access(
    p_user_id TEXT,
    p_allowed_countries TEXT[] DEFAULT ARRAY['US', 'CA', 'UK', 'DE', 'FR']
)
RETURNS BOOLEAN AS $$
DECLARE
    user_ip INET;
    country_code TEXT;
    is_allowed BOOLEAN;
BEGIN
    -- 获取用户IP地址
    user_ip := inet_client_addr();
    
    -- 简化的地理位置检查（实际应用中应该使用IP地理位置数据库）
    -- 这里模拟基于IP的地理位置判断
    country_code := CASE 
        WHEN family(user_ip) = 4 AND host(user_ip) LIKE '192.168.%' THEN 'US'
        WHEN family(user_ip) = 4 AND host(user_ip) LIKE '10.%' THEN 'US'
        WHEN family(user_ip) = 4 AND host(user_ip) LIKE '172.%' THEN 'US'
        ELSE 'UNKNOWN'
    END;
    
    -- 检查地理位置是否允许
    is_allowed := country_code = ANY(p_allowed_countries);
    
    -- 记录地理位置访问尝试
    INSERT INTO security_test.data_access_log (
        user_id, access_type, access_time, 
        data_classification, compliance_flags
    ) VALUES (
        p_user_id, 'GEO_CHECK', CURRENT_TIMESTAMP,
        'CONTROL', ARRAY[ 
            CASE WHEN is_allowed THEN 'ALLOWED' ELSE 'DENIED' END,
            'COUNTRY:' || country_code 
        ]
    );
    
    RETURN is_allowed;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 6. 安全策略管理和报告
-- ================================================

-- 6.1 创建安全策略状态报告函数
CREATE OR REPLACE FUNCTION generate_security_policy_report(
    p_days_back INTEGER DEFAULT 30
)
RETURNS TABLE(
    policy_name TEXT,
    policy_status TEXT,
    compliance_score DECIMAL(3,2),
    total_violations INTEGER,
    critical_issues INTEGER,
    recommendations TEXT
) AS $$
BEGIN
    -- 数据加密策略
    RETURN QUERY
    SELECT 
        'DATA_ENCRYPTION'::TEXT as policy_name,
        CASE 
            WHEN (SELECT COUNT(*) FROM security_test.sensitive_data WHERE credit_card_hash IS NOT NULL) > 0
            THEN 'ACTIVE'
            ELSE 'NON_COMPLIANT'
        END as policy_status,
        CASE 
            WHEN (SELECT COUNT(*) FROM security_test.sensitive_data WHERE credit_card_hash IS NOT NULL) > 0
            THEN 1.0
            ELSE 0.0
        END as compliance_score,
        (SELECT COUNT(*) FROM security_test.audit_events WHERE risk_level = 'HIGH')::INTEGER as total_violations,
        (SELECT COUNT(*) FROM security_test.audit_events WHERE risk_level = 'HIGH' AND timestamp > CURRENT_DATE - (p_days_back || ' days')::INTERVAL)::INTEGER as critical_issues,
        'Ensure all sensitive fields are encrypted or hashed'::TEXT as recommendations;
    
    -- 访问控制策略
    RETURN QUERY
    SELECT 
        'ACCESS_CONTROL'::TEXT as policy_name,
        CASE 
            WHEN EXISTS(SELECT 1 FROM security_test.user_sessions WHERE risk_score > 70)
            THEN 'ACTIVE_WITH_ISSUES'
            ELSE 'ACTIVE'
        END as policy_status,
        CASE 
            WHEN EXISTS(SELECT 1 FROM security_test.user_sessions WHERE risk_score > 70)
            THEN 0.75
            ELSE 0.95
        END as compliance_score,
        (SELECT COUNT(*) FROM security_test.data_access_log WHERE 'DENIED' = ANY(compliance_flags))::INTEGER as total_violations,
        (SELECT COUNT(*) FROM security_test.user_sessions WHERE risk_score > 70)::INTEGER as critical_issues,
        'Review high-risk user sessions and implement additional controls'::TEXT as recommendations;
    
    -- 审计日志策略
    RETURN QUERY
    SELECT 
        'AUDIT_LOGGING'::TEXT as policy_name,
        'ACTIVE'::TEXT as policy_status,
        CASE 
            WHEN (SELECT COUNT(*) FROM security_test.audit_events WHERE timestamp > CURRENT_DATE - (p_days_back || ' days')::INTERVAL) > 0
            THEN 1.0
            ELSE 0.0
        END as compliance_score,
        0::INTEGER as total_violations,
        0::INTEGER as critical_issues,
        'Continue monitoring all audit events'::TEXT as recommendations;
    
    -- 数据保留策略
    RETURN QUERY
    SELECT 
        'DATA_RETENTION'::TEXT as policy_name,
        CASE 
            WHEN (SELECT COUNT(*) FROM security_test.audit_events WHERE timestamp < CURRENT_DATE - INTERVAL '1 year') > 0
            THEN 'NEEDS_REVIEW'
            ELSE 'COMPLIANT'
        END as policy_status,
        CASE 
            WHEN (SELECT COUNT(*) FROM security_test.audit_events WHERE timestamp < CURRENT_DATE - INTERVAL '1 year') > 0
            THEN 0.6
            ELSE 1.0
        END as compliance_score,
        (SELECT COUNT(*) FROM security_test.audit_events WHERE timestamp < CURRENT_DATE - INTERVAL '1 year')::INTEGER as total_violations,
        (SELECT COUNT(*) FROM security_test.audit_events WHERE timestamp < CURRENT_DATE - INTERVAL '1 year' AND risk_level = 'HIGH')::INTEGER as critical_issues,
        'Implement automated data archival and deletion procedures'::TEXT as recommendations;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 6.2 创建策略违规检测函数
CREATE OR REPLACE FUNCTION detect_policy_violations(
    p_violation_type TEXT DEFAULT 'ALL',
    p_severity_threshold TEXT DEFAULT 'MEDIUM'
)
RETURNS TABLE(
    violation_id BIGINT,
    violation_type TEXT,
    severity TEXT,
    description TEXT,
    affected_objects TEXT[],
    detected_at TIMESTAMP,
    recommendation TEXT
) AS $$
BEGIN
    -- 检测数据访问违规
    IF p_violation_type IN ('ALL', 'ACCESS') THEN
        RETURN QUERY
        SELECT 
            audit_events.event_id as violation_id,
            'UNAUTHORIZED_ACCESS'::TEXT as violation_type,
            audit_events.risk_level as severity,
            'Access attempt without proper authorization'::TEXT as description,
            ARRAY[audit_events.table_name] as affected_objects,
            audit_events.timestamp as detected_at,
            'Review user permissions and implement additional access controls'::TEXT as recommendation
        FROM security_test.audit_events
        WHERE audit_events.risk_level >= CASE p_severity_threshold
            WHEN 'LOW' THEN 'LOW'
            WHEN 'MEDIUM' THEN 'MEDIUM'
            WHEN 'HIGH' THEN 'HIGH'
            ELSE 'HIGH'
        END
        AND audit_events.timestamp > CURRENT_DATE - INTERVAL '1 day'
        ORDER BY audit_events.timestamp DESC
        LIMIT 10;
    END IF;
    
    -- 检测时间访问违规
    IF p_violation_type IN ('ALL', 'TIME_ACCESS') THEN
        RETURN QUERY
        SELECT 
            access_log.access_id as violation_id,
            'AFTER_HOURS_ACCESS'::TEXT as violation_type,
            'MEDIUM'::TEXT as severity,
            'Access during non-business hours'::TEXT as description,
            ARRAY[access_log.table_name] as affected_objects,
            access_log.access_time as detected_at,
            'Implement time-based access restrictions'::TEXT as recommendation
        FROM security_test.data_access_log access_log
        WHERE EXTRACT(hour FROM access_log.access_time) NOT BETWEEN 8 AND 18
        AND access_log.access_time > CURRENT_DATE - INTERVAL '1 day'
        ORDER BY access_log.access_time DESC
        LIMIT 5;
    END IF;
    
    -- 检测数据保留违规
    IF p_violation_type IN ('ALL', 'DATA_RETENTION') THEN
        RETURN QUERY
        SELECT 
            audit_events.event_id as violation_id,
            'EXCESSIVE_DATA_RETENTION'::TEXT as violation_type,
            'LOW'::TEXT as severity,
            'Data retained beyond policy limits'::TEXT as description,
            ARRAY[audit_events.table_name] as affected_objects,
            audit_events.timestamp as detected_at,
            'Implement data archival and deletion policies'::TEXT as recommendation
        FROM security_test.audit_events
        WHERE audit_events.timestamp < CURRENT_DATE - INTERVAL '7 years'
        AND audit_events.table_name = 'audit_events'
        ORDER BY audit_events.timestamp ASC
        LIMIT 3;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- 7. 安全策略实施和测试
-- ================================================

-- 创建策略触发器
CREATE TRIGGER sensitive_data_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON security_test.sensitive_data
    FOR EACH ROW EXECUTE FUNCTION security_audit_trigger();

CREATE TRIGGER audit_events_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON security_test.audit_events
    FOR EACH ROW EXECUTE FUNCTION security_audit_trigger();

-- 测试数据脱敏
-- SELECT anonymize_sensitive_data('sensitive_data', 'user_email', 'EMAIL_MASK');
-- SELECT anonymize_sensitive_data('sensitive_data', 'credit_card_hash', 'HASH');

-- 测试权限检查
-- SELECT check_data_access_permission('security_admin', 'sensitive_data', 'SELECT', 'SECURITY_ADMIN');
-- SELECT check_data_access_permission('regular_user', 'sensitive_data', 'SELECT', 'USER');

-- 测试合规检查
-- SELECT * FROM check_privacy_compliance('sensitive_data');

-- 测试异常检测
-- SELECT * FROM detect_anomalous_access();

-- 测试安全策略报告
-- SELECT * FROM generate_security_policy_report(30);

-- 测试违规检测
-- SELECT * FROM detect_policy_violations();

-- ================================================
-- 8. 安全策略维护函数
-- ================================================

-- 8.1 创建策略更新函数
CREATE OR REPLACE FUNCTION update_security_policies(
    p_policy_name TEXT,
    p_policy_config JSONB
)
RETURNS TEXT AS $$
DECLARE
    current_setting_value TEXT;
BEGIN
    -- 这里可以实现策略配置的动态更新
    -- 实际实现中需要根据具体的策略类型来处理
    
    -- 记录策略变更
    INSERT INTO security_test.audit_events (
        event_type,
        user_id,
        table_name,
        operation,
        new_values
    ) VALUES (
        'POLICY_UPDATE',
        current_user,
        'security_policies',
        'UPDATE',
        jsonb_build_object(
            'policy_name', p_policy_name,
            'config', p_policy_config,
            'updated_by', current_user
        )
    );
    
    RETURN 'Success: Policy ' || p_policy_name || ' updated';
EXCEPTION WHEN OTHERS THEN
    RETURN 'Error updating policy: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8.2 创建策略验证函数
CREATE OR REPLACE FUNCTION validate_security_policies()
RETURNS TABLE(
    policy_name TEXT,
    validation_status TEXT,
    issues_found TEXT[],
    recommendations TEXT
) AS $$
BEGIN
    -- 验证行级安全策略
    RETURN QUERY
    SELECT 
        'ROW_LEVEL_SECURITY'::TEXT as policy_name,
        CASE 
            WHEN EXISTS(
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'security_test' 
                AND row_security = 'YES'
            )
            THEN 'VALID'
            ELSE 'MISSING'
        END as validation_status,
        CASE 
            WHEN EXISTS(
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'security_test' 
                AND row_security = 'YES'
            )
            THEN ARRAY['Row-level security is properly enabled']
            ELSE ARRAY['Row-level security is not enabled on sensitive tables']
        END as issues_found,
        'Enable RLS on all sensitive tables'::TEXT as recommendations;
    
    -- 验证审计日志策略
    RETURN QUERY
    SELECT 
        'AUDIT_LOGGING'::TEXT as policy_name,
        CASE 
            WHEN EXISTS(SELECT 1 FROM security_test.audit_events WHERE timestamp > CURRENT_DATE - INTERVAL '1 hour')
            THEN 'VALID'
            ELSE 'NEEDS_VERIFICATION'
        END as validation_status,
        ARRAY['Audit logging is active'] as issues_found,
        'Continue monitoring audit events'::TEXT as recommendations;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

/*
安全策略管理最佳实践：

1. 数据分类
   - 建立清晰的数据分类标准
   - 根据分类实施相应的访问控制
   - 定期审查和更新分类策略

2. 访问控制
   - 实施最小权限原则
   - 使用基于角色的访问控制(RBAC)
   - 实施多因素身份认证

3. 审计和监控
   - 启用全面的审计日志记录
   - 监控异常访问模式
   - 建立实时告警机制

4. 数据保护
   - 对敏感数据进行加密或脱敏
   - 实施数据保留和删除策略
   - 确保数据完整性和可用性

5. 合规性管理
   - 定期进行合规性检查
   - 维护合规性文档
   - 建立合规性报告流程

6. 策略管理
   - 建立策略版本控制
   - 定期审查和更新安全策略
   - 确保策略的一致性实施
*/
