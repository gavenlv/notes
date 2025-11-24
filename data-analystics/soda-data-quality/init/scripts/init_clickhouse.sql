-- ClickHouse Database Initialization Script
-- Creates sample tables and views for data quality testing

-- Drop existing objects if they exist (with better error handling)
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

-- Insert valid sample events data first
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1001, 'page_view', now() - toIntervalHour(1), '{"page": "home"}', 'sess_001', '/home'),
    (1001, 'click', now() - toIntervalMinute(59), '{"element": "nav_menu"}', 'sess_001', '/home'),
    (1001, 'page_view', now() - toIntervalMinute(58), '{"page": "products"}', 'sess_001', '/products'),
    (1002, 'page_view', now() - toIntervalHour(2), '{"page": "home"}', 'sess_002', '/home'),
    (1002, 'signup', now() - toIntervalMinute(119), '{"method": "email"}', 'sess_002', '/signup'),
    (1003, 'login', now() - toIntervalHour(3), '{"method": "password"}', 'sess_003', '/login'),
    (1003, 'page_view', now() - toIntervalMinute(179), '{"page": "dashboard"}', 'sess_003', '/dashboard'),
    (1004, 'page_view', now() - toIntervalMinute(30), '{"page": "home"}', 'sess_004', '/home'),
    (1004, 'click', now() - toIntervalMinute(29), '{"element": "product_card"}', 'sess_004', '/home'),
    (1004, 'page_view', now() - toIntervalMinute(28), '{"page": "product_detail"}', 'sess_004', '/product/123'),
    (1005, 'purchase', now() - toIntervalHour(4), '{"amount": 99.99, "product": "laptop"}', 'sess_005', '/checkout'),
    (1001, 'page_view', now() - toIntervalMinute(10), '{"page": "profile"}', 'sess_006', '/profile'),
    (1002, 'click', now() - toIntervalMinute(45), '{"element": "search_button"}', 'sess_007', '/search'),
    (1003, 'view', now() - toIntervalMinute(15), '{"content": "video"}', 'sess_008', '/videos'),
    (1004, 'click', now() - toIntervalMinute(5), '{"element": "like_button"}', 'sess_009', '/posts'),
    (1005, 'page_view', now() - toIntervalMinute(20), '{"page": "settings"}', 'sess_010', '/settings'),
    (1006, 'signup', now() - toIntervalHour(6), '{"method": "google"}', 'sess_011', '/signup'),
    (1007, 'login', now() - toIntervalHour(7), '{"method": "facebook"}', 'sess_012', '/login'),
    (1008, 'purchase', now() - toIntervalHour(8), '{"amount": 149.99, "product": "phone"}', 'sess_013', '/checkout'),
    (1009, 'view', now() - toIntervalMinute(25), '{"content": "article"}', 'sess_014', '/blog'),
    (1010, 'click', now() - toIntervalMinute(35), '{"element": "share_button"}', 'sess_015', '/posts'),
    (1001, 'page_view', now() - toIntervalMinute(1), '{"page": "cart"}', 'sess_016', '/cart'),
    (1002, 'purchase', now() - toIntervalMinute(2), '{"amount": 29.99, "product": "book"}', 'sess_017', '/checkout'),
    (1003, 'click', now() - toIntervalMinute(3), '{"element": "download"}', 'sess_018', '/downloads'),
    (1004, 'view', now() - toIntervalMinute(4), '{"content": "image"}', 'sess_019', '/gallery');

-- Insert data quality test cases for events (problematic data for Soda to detect)
-- Duplicate event
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1001, 'page_view', now() - toIntervalHour(1), '{"page": "home"}', 'sess_001', '/home');

-- Invalid event name
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1002, 'invalid_event_type', now(), '{}', 'sess_issue_3', '/invalid');

-- Future timestamp
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1003, 'page_view', now() + toIntervalDay(1), '{}', 'sess_issue_4', '/future');

-- Invalid user_id (zero)
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (0, 'zero_user_event', now(), '{}', 'sess_zero', '/zero');

-- Empty event name
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1001, '', now(), '{}', 'sess_empty', '/empty');

-- Invalid JSON in properties
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1002, 'click', now(), 'invalid_json{', 'sess_bad_json', '/bad');

-- Empty session_id
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1003, 'view', now(), '{}', '', '/empty_session');

-- Empty page_url
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1004, 'purchase', now(), '{}', 'sess_no_url', '');

-- Very high user_id
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (999999, 'high_user_id', now(), '{}', 'sess_high', '/high');

-- Very long event name
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1001, 'very_long_event_name_that_exceeds_normal_limits_and_should_be_caught_by_validation', now(), '{}', 'sess_long', '/long');

-- Will be used for NULL testing
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1002, 'null_test', now(), '{}', 'sess_null', '/null');

-- Special characters in event name
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1003, 'special_chars_!@#$%^&*()', now(), '{}', 'sess_special', '/special');

-- Very old event
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (1004, 'old_event', now() - toIntervalDay(365), '{}', 'sess_old', '/old');

-- Negative user_id
INSERT INTO events (user_id, event_name, event_time, properties, session_id, page_url) VALUES
    (-1, 'negative_user', now(), '{}', 'sess_negative', '/negative');

-- Create user_sessions table
CREATE TABLE user_sessions (
    session_id String,
    user_id UInt64,
    start_time DateTime DEFAULT now(),
    end_time DateTime DEFAULT now(),
    duration_minutes UInt32 DEFAULT 0,
    page_views UInt32 DEFAULT 0,
    device_type String DEFAULT 'unknown',
    browser String DEFAULT 'unknown',
    created_date Date DEFAULT today()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(start_time)
ORDER BY (user_id, start_time)
SETTINGS index_granularity = 8192;

-- Insert sample user sessions
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_001', 1001, now() - toIntervalHour(2), now() - toIntervalHour(1), 60, 5, 'desktop', 'chrome'),
    ('sess_002', 1002, now() - toIntervalHour(3), now() - toIntervalHour(2), 45, 3, 'mobile', 'safari'),
    ('sess_003', 1003, now() - toIntervalHour(4), now() - toIntervalHour(3), 30, 7, 'desktop', 'firefox'),
    ('sess_004', 1004, now() - toIntervalMinute(45), now() - toIntervalMinute(15), 30, 4, 'tablet', 'chrome'),
    ('sess_005', 1005, now() - toIntervalHour(5), now() - toIntervalHour(4), 90, 12, 'desktop', 'edge'),
    ('sess_006', 1001, now() - toIntervalMinute(30), now() - toIntervalMinute(10), 20, 2, 'mobile', 'chrome'),
    ('sess_007', 1002, now() - toIntervalHour(1), now() - toIntervalMinute(45), 15, 1, 'desktop', 'safari'),
    ('sess_008', 1003, now() - toIntervalMinute(20), now() - toIntervalMinute(5), 15, 1, 'mobile', 'firefox'),
    ('sess_009', 1004, now() - toIntervalMinute(10), now() - toIntervalMinute(5), 5, 1, 'desktop', 'chrome'),
    ('sess_010', 1005, now() - toIntervalMinute(25), now() - toIntervalMinute(5), 20, 1, 'tablet', 'safari'),
    ('sess_011', 1006, now() - toIntervalHour(7), now() - toIntervalHour(6), 60, 8, 'desktop', 'chrome'),
    ('sess_012', 1007, now() - toIntervalHour(8), now() - toIntervalHour(7), 45, 6, 'mobile', 'safari'),
    ('sess_013', 1008, now() - toIntervalHour(9), now() - toIntervalHour(8), 30, 4, 'desktop', 'firefox'),
    ('sess_014', 1009, now() - toIntervalMinute(30), now() - toIntervalMinute(5), 25, 1, 'tablet', 'chrome'),
    ('sess_015', 1010, now() - toIntervalMinute(40), now() - toIntervalMinute(5), 35, 1, 'desktop', 'edge'),
    ('sess_016', 1001, now() - toIntervalMinute(5), now() - toIntervalMinute(1), 4, 1, 'mobile', 'chrome'),
    ('sess_017', 1002, now() - toIntervalMinute(5), now() - toIntervalMinute(2), 3, 1, 'desktop', 'safari'),
    ('sess_018', 1003, now() - toIntervalMinute(5), now() - toIntervalMinute(3), 2, 1, 'mobile', 'firefox'),
    ('sess_019', 1004, now() - toIntervalMinute(5), now() - toIntervalMinute(4), 1, 1, 'desktop', 'chrome');

-- Insert data quality test cases for user_sessions (problematic data for Soda to detect)

-- Empty session_id
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('', 1001, now() - toIntervalHour(1), now() - toIntervalMinute(30), 30, 3, 'desktop', 'chrome');

-- Negative duration (end before start)
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_negative_duration', 1002, now() - toIntervalMinute(30), now() - toIntervalHour(1), -30, 2, 'mobile', 'safari');

-- Zero duration and page views
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_zero_duration', 1003, now() - toIntervalMinute(30), now() - toIntervalMinute(30), 0, 0, 'tablet', 'firefox');

-- Negative page views
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_negative_views', 1004, now() - toIntervalMinute(45), now() - toIntervalMinute(15), 30, -5, 'desktop', 'chrome');

-- Extremely long session (24 hours)
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_high_duration', 1005, now() - toIntervalDay(1), now(), 1440, 999, 'mobile', 'safari');

-- Future session
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_future', 1006, now() + toIntervalHour(1), now() + toIntervalHour(2), 60, 5, 'desktop', 'chrome');

-- Invalid device type
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_invalid_device', 1007, now() - toIntervalMinute(30), now() - toIntervalMinute(10), 20, 3, 'invalid_device', 'chrome');

-- Empty browser
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_empty_browser', 1008, now() - toIntervalMinute(30), now() - toIntervalMinute(10), 20, 3, 'desktop', '');

-- Zero user_id
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_zero_user', 0, now() - toIntervalMinute(30), now() - toIntervalMinute(10), 20, 3, 'desktop', 'chrome');

-- Very high user_id
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_high_user', 999999, now() - toIntervalMinute(30), now() - toIntervalMinute(10), 20, 3, 'desktop', 'chrome');

-- Very old session
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_old', 1009, now() - toIntervalDay(365), now() - toIntervalDay(365) + toIntervalMinute(30), 30, 5, 'desktop', 'chrome');

-- Duration/page_views mismatch (5 min but 100 views)
INSERT INTO user_sessions (session_id, user_id, start_time, end_time, duration_minutes, page_views, device_type, browser) VALUES
    ('sess_mismatch_data', 1010, now() - toIntervalMinute(60), now() - toIntervalMinute(30), 5, 100, 'mobile', 'safari');

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
