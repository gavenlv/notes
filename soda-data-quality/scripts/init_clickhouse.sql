-- ClickHouse Database Initialization Script
-- Creates sample tables and views for data quality testing

-- Drop existing objects if they exist
DROP VIEW IF EXISTS daily_events_summary;
DROP VIEW IF EXISTS user_activity_view;
DROP TABLE IF EXISTS user_sessions;
DROP TABLE IF EXISTS events;

-- Create events table (MergeTree engine for better performance)
CREATE TABLE events (
    user_id UInt64,
    event_name String,
    event_time DateTime DEFAULT now(),
    properties String DEFAULT '{}',
    session_id String,
    page_url String DEFAULT '',
    user_agent String DEFAULT '',
    ip_address String DEFAULT '',
    created_date Date DEFAULT today()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (user_id, event_time)
SETTINGS index_granularity = 8192;

-- Create user_sessions table
CREATE TABLE user_sessions (
    session_id String,
    user_id UInt64,
    start_time DateTime,
    end_time DateTime DEFAULT now(),
    duration_seconds UInt32,
    page_views UInt32 DEFAULT 1,
    session_date Date DEFAULT today(),
    device_type String DEFAULT 'desktop',
    browser String DEFAULT 'unknown'
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(start_time)
ORDER BY (user_id, start_time)
SETTINGS index_granularity = 8192;

-- Insert sample events data
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1001, 'page_view', now() - INTERVAL 1 HOUR, '{"page": "home"}', 'sess_001', '/home'),
    (1001, 'click', now() - INTERVAL 59 MINUTE, '{"element": "nav_menu"}', 'sess_001', '/home'),
    (1001, 'page_view', now() - INTERVAL 58 MINUTE, '{"page": "products"}', 'sess_001', '/products'),
    (1002, 'page_view', now() - INTERVAL 2 HOUR, '{"page": "home"}', 'sess_002', '/home'),
    (1002, 'signup', now() - INTERVAL 119 MINUTE, '{"method": "email"}', 'sess_002', '/signup'),
    (1003, 'login', now() - INTERVAL 3 HOUR, '{"method": "password"}', 'sess_003', '/login'),
    (1003, 'page_view', now() - INTERVAL 179 MINUTE, '{"page": "dashboard"}', 'sess_003', '/dashboard'),
    (1004, 'page_view', now() - INTERVAL 30 MINUTE, '{"page": "home"}', 'sess_004', '/home'),
    (1004, 'click', now() - INTERVAL 29 MINUTE, '{"element": "product_card"}', 'sess_004', '/home'),
    (1004, 'page_view', now() - INTERVAL 28 MINUTE, '{"page": "product_detail"}', 'sess_004', '/product/123'),
    (1005, 'purchase', now() - INTERVAL 4 HOUR, '{"amount": 99.99, "product": "laptop"}', 'sess_005', '/checkout'),
    (1001, 'page_view', now() - INTERVAL 10 MINUTE, '{"page": "profile"}', 'sess_006', '/profile'),
    (1002, 'click', now() - INTERVAL 45 MINUTE, '{"element": "search_button"}', 'sess_007', '/search'),
    (1003, 'view', now() - INTERVAL 15 MINUTE, '{"content": "video"}', 'sess_008', '/videos'),
    (1004, 'click', now() - INTERVAL 5 MINUTE, '{"element": "like_button"}', 'sess_009', '/posts'),
    (1005, 'page_view', now() - INTERVAL 20 MINUTE, '{"page": "settings"}', 'sess_010', '/settings'),
    (1006, 'signup', now() - INTERVAL 6 HOUR, '{"method": "google"}', 'sess_011', '/signup'),
    (1007, 'login', now() - INTERVAL 7 HOUR, '{"method": "facebook"}', 'sess_012', '/login'),
    (1008, 'purchase', now() - INTERVAL 8 HOUR, '{"amount": 149.99, "product": "phone"}', 'sess_013', '/checkout'),
    (1009, 'view', now() - INTERVAL 25 MINUTE, '{"content": "article"}', 'sess_014', '/blog'),
    (1010, 'click', now() - INTERVAL 35 MINUTE, '{"element": "share_button"}', 'sess_015', '/posts'),
    (1001, 'page_view', now() - INTERVAL 1 MINUTE, '{"page": "cart"}', 'sess_016', '/cart'),
    (1002, 'purchase', now() - INTERVAL 2 MINUTE, '{"amount": 29.99, "product": "book"}', 'sess_017', '/checkout'),
    (1003, 'click', now() - INTERVAL 3 MINUTE, '{"element": "download"}', 'sess_018', '/downloads'),
    (1004, 'view', now() - INTERVAL 4 MINUTE, '{"content": "image"}', 'sess_019', '/gallery');

-- Insert sample session data
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_seconds, page_views, device_type, browser) VALUES
    ('sess_001', 1001, now() - INTERVAL 1 HOUR, now() - INTERVAL 55 MINUTE, 300, 3, 'desktop', 'chrome'),
    ('sess_002', 1002, now() - INTERVAL 2 HOUR, now() - INTERVAL 115 MINUTE, 300, 2, 'mobile', 'safari'),
    ('sess_003', 1003, now() - INTERVAL 3 HOUR, now() - INTERVAL 175 MINUTE, 300, 2, 'desktop', 'firefox'),
    ('sess_004', 1004, now() - INTERVAL 30 MINUTE, now() - INTERVAL 25 MINUTE, 300, 3, 'tablet', 'chrome'),
    ('sess_005', 1005, now() - INTERVAL 4 HOUR, now() - INTERVAL 235 MINUTE, 300, 1, 'desktop', 'edge'),
    ('sess_006', 1001, now() - INTERVAL 10 MINUTE, now() - INTERVAL 8 MINUTE, 120, 1, 'desktop', 'chrome'),
    ('sess_007', 1002, now() - INTERVAL 45 MINUTE, now() - INTERVAL 40 MINUTE, 300, 1, 'mobile', 'safari'),
    ('sess_008', 1003, now() - INTERVAL 15 MINUTE, now() - INTERVAL 12 MINUTE, 180, 1, 'desktop', 'firefox'),
    ('sess_009', 1004, now() - INTERVAL 5 MINUTE, now() - INTERVAL 3 MINUTE, 120, 1, 'tablet', 'chrome'),
    ('sess_010', 1005, now() - INTERVAL 20 MINUTE, now() - INTERVAL 18 MINUTE, 120, 1, 'desktop', 'edge'),
    ('sess_011', 1006, now() - INTERVAL 6 HOUR, now() - INTERVAL 355 MINUTE, 300, 1, 'mobile', 'chrome'),
    ('sess_012', 1007, now() - INTERVAL 7 HOUR, now() - INTERVAL 415 MINUTE, 300, 1, 'desktop', 'safari'),
    ('sess_013', 1008, now() - INTERVAL 8 HOUR, now() - INTERVAL 475 MINUTE, 300, 1, 'tablet', 'firefox'),
    ('sess_014', 1009, now() - INTERVAL 25 MINUTE, now() - INTERVAL 22 MINUTE, 180, 1, 'desktop', 'chrome'),
    ('sess_015', 1010, now() - INTERVAL 35 MINUTE, now() - INTERVAL 32 MINUTE, 180, 1, 'mobile', 'edge'),
    ('sess_016', 1001, now() - INTERVAL 1 MINUTE, now(), 60, 1, 'desktop', 'chrome'),
    ('sess_017', 1002, now() - INTERVAL 2 MINUTE, now(), 120, 1, 'mobile', 'safari'),
    ('sess_018', 1003, now() - INTERVAL 3 MINUTE, now(), 180, 1, 'desktop', 'firefox'),
    ('sess_019', 1004, now() - INTERVAL 4 MINUTE, now(), 240, 1, 'tablet', 'chrome');

-- Create view for daily events summary
CREATE VIEW daily_events_summary AS
SELECT 
    toDate(event_time) as event_date,
    event_name,
    count() as event_count,
    uniq(user_id) as unique_users,
    uniq(session_id) as unique_sessions
FROM events
WHERE event_time >= today() - 7
GROUP BY event_date, event_name
ORDER BY event_date DESC, event_count DESC;

-- Create view for user activity
CREATE VIEW user_activity_view AS
SELECT 
    user_id,
    count() as total_events,
    uniq(event_name) as unique_event_types,
    uniq(session_id) as total_sessions,
    min(event_time) as first_event,
    max(event_time) as last_event,
    dateDiff('hour', min(event_time), max(event_time)) as activity_span_hours
FROM events
GROUP BY user_id
ORDER BY total_events DESC;

-- Display summary
SELECT 'ClickHouse Database Initialized Successfully' as status;
SELECT 'Events created: ' || toString(count()) as summary FROM events;
SELECT 'Sessions created: ' || toString(count()) as summary FROM user_sessions;
SELECT 'Views created: 2 (daily_events_summary, user_activity_view)' as summary;
