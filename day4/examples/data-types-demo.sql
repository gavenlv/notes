-- ClickHouse数据类型综合演示
-- Day 4 学习示例

-- 切换到tutorial数据库（如果不存在则创建）
CREATE DATABASE IF NOT EXISTS tutorial;
USE tutorial;

-- 1. 数值类型演示
DROP TABLE IF EXISTS numeric_types_demo;
CREATE TABLE numeric_types_demo (
    -- 整数类型
    tiny_int Int8,
    small_int Int16,
    medium_int Int32,
    big_int Int64,
    unsigned_int UInt32,
    
    -- 浮点类型
    float_val Float32,
    double_val Float64,
    
    -- 精确小数类型
    price Decimal(10, 2),
    rate Decimal64(4)
) ENGINE = Memory;

-- 插入数值类型数据
INSERT INTO numeric_types_demo VALUES
(127, 32767, 2147483647, 9223372036854775807, 4294967295, 3.14159, 2.718281828, 999.99, 0.0525),
(-128, -32768, -2147483648, -9223372036854775808, 0, -1.5, -2.5, 0.01, 1.2345),
(0, 0, 0, 0, 12345, 0.0, 0.0, 500.00, 0.0001);

-- 查看数值类型数据
SELECT '=== 数值类型演示 ===' as demo_section;
SELECT * FROM numeric_types_demo;

-- 2. 字符串类型演示
DROP TABLE IF EXISTS string_types_demo;
CREATE TABLE string_types_demo (
    id UInt32,
    name String,
    code FixedString(8),
    description String,
    category LowCardinality(String)
) ENGINE = Memory;

-- 插入字符串数据
INSERT INTO string_types_demo VALUES
(1, '张三', '00000001', '这是一个测试用户', '管理员'),
(2, '李四', '00000002', 'This is another test user', '普通用户'),
(3, '王五', '00000003', '第三个测试用户', '管理员'),
(4, 'John', '00000004', 'English user example', '普通用户');

-- 查看字符串类型数据和操作
SELECT '=== 字符串类型演示 ===' as demo_section;
SELECT 
    id,
    name,
    code,
    length(name) as name_length,
    upper(name) as name_upper,
    concat(name, '-', code) as name_code,
    category
FROM string_types_demo;

-- 3. 日期时间类型演示
DROP TABLE IF EXISTS datetime_types_demo;
CREATE TABLE datetime_types_demo (
    id UInt32,
    birth_date Date,
    created_at DateTime,
    precise_time DateTime64(3),
    utc_time DateTime('UTC'),
    local_time DateTime('Asia/Shanghai')
) ENGINE = Memory;

-- 插入日期时间数据
INSERT INTO datetime_types_demo VALUES
(1, '1990-01-01', '2024-01-01 10:30:00', '2024-01-01 10:30:00.123', '2024-01-01 02:30:00', '2024-01-01 10:30:00'),
(2, '1985-05-15', '2024-01-02 14:45:30', '2024-01-02 14:45:30.456', '2024-01-02 06:45:30', '2024-01-02 14:45:30'),
(3, '2000-12-31', '2024-01-03 09:15:45', '2024-01-03 09:15:45.789', '2024-01-03 01:15:45', '2024-01-03 09:15:45');

-- 查看日期时间数据和操作
SELECT '=== 日期时间类型演示 ===' as demo_section;
SELECT 
    id,
    birth_date,
    toYear(birth_date) as birth_year,
    toAge(birth_date) as current_age,
    created_at,
    formatDateTime(created_at, '%Y-%m-%d %H:%M:%S') as formatted_time,
    precise_time,
    dateDiff('day', birth_date, toDate(created_at)) as days_lived
FROM datetime_types_demo;

-- 4. 数组类型演示
DROP TABLE IF EXISTS array_types_demo;
CREATE TABLE array_types_demo (
    id UInt32,
    numbers Array(Int32),
    tags Array(String),
    scores Array(Float64)
) ENGINE = Memory;

-- 插入数组数据
INSERT INTO array_types_demo VALUES
(1, [1, 2, 3, 4, 5], ['红色', '蓝色', '绿色'], [95.5, 87.2, 92.8]),
(2, [10, 20, 30], ['大', '中', '小'], [88.0, 90.5]),
(3, [100], ['特殊'], [100.0, 95.0, 88.5, 92.3]);

-- 查看数组操作
SELECT '=== 数组类型演示 ===' as demo_section;
SELECT 
    id,
    numbers,
    length(numbers) as numbers_count,
    numbers[1] as first_number,
    arraySum(numbers) as numbers_sum,
    tags,
    arrayStringConcat(tags, ',') as tags_joined,
    scores,
    arrayMax(scores) as max_score,
    arrayAvg(scores) as avg_score
FROM array_types_demo;

-- 高级数组操作
SELECT '=== 数组高级操作 ===' as demo_section;
SELECT 
    id,
    arrayFilter(x -> x > 2, numbers) as filtered_numbers,
    arrayMap(x -> x * 2, numbers) as doubled_numbers,
    arrayExists(x -> x > 90, scores) as has_high_score
FROM array_types_demo;

-- 5. 元组类型演示
DROP TABLE IF EXISTS tuple_types_demo;
CREATE TABLE tuple_types_demo (
    id UInt32,
    coordinates Tuple(Float64, Float64),
    person_info Tuple(String, UInt8, String, String)
) ENGINE = Memory;

-- 插入元组数据
INSERT INTO tuple_types_demo VALUES
(1, (39.9042, 116.4074), ('张三', 25, '北京', '软件工程师')),
(2, (31.2304, 121.4737), ('李四', 30, '上海', '数据分析师')),
(3, (22.3193, 114.1694), ('王五', 28, '深圳', '产品经理'));

-- 查看元组操作
SELECT '=== 元组类型演示 ===' as demo_section;
SELECT 
    id,
    coordinates,
    coordinates.1 as latitude,
    coordinates.2 as longitude,
    person_info,
    person_info.1 as name,
    person_info.2 as age,
    person_info.3 as city,
    person_info.4 as job
FROM tuple_types_demo;

-- 6. 可空类型演示
DROP TABLE IF EXISTS nullable_types_demo;
CREATE TABLE nullable_types_demo (
    id UInt32,
    name String,
    age Nullable(UInt8),
    email Nullable(String),
    phone Nullable(String)
) ENGINE = Memory;

-- 插入包含NULL的数据
INSERT INTO nullable_types_demo VALUES
(1, '张三', 25, 'zhang@example.com', '13800138001'),
(2, '李四', NULL, NULL, '13800138002'),
(3, '王五', 30, 'wang@example.com', NULL),
(4, '赵六', 35, NULL, NULL);

-- 查看NULL值处理
SELECT '=== 可空类型演示 ===' as demo_section;
SELECT 
    id,
    name,
    age,
    isNull(age) as age_is_null,
    isNotNull(age) as age_is_not_null,
    ifNull(age, 0) as age_or_zero,
    email,
    coalesce(email, 'no-email@example.com') as email_with_default,
    phone,
    if(isNull(phone), '无电话', phone) as phone_display
FROM nullable_types_demo;

-- 7. 综合查询演示 - 电商订单分析
DROP TABLE IF EXISTS ecommerce_orders;
CREATE TABLE ecommerce_orders (
    order_id UInt64,
    user_id UInt32,
    order_time DateTime,
    products Array(Tuple(String, UInt16, Decimal(10,2))), -- 商品名,数量,单价
    total_amount Decimal(10, 2),
    status LowCardinality(String),
    shipping_address Tuple(String, String, String), -- 省,市,详细地址
    tags Array(String)
) ENGINE = MergeTree()
ORDER BY (user_id, order_time)
PARTITION BY toYYYYMM(order_time);

-- 插入电商订单数据
INSERT INTO ecommerce_orders VALUES
(1001, 1, '2024-01-15 10:30:00', [('iPhone 15', 1, 999.99), ('手机壳', 1, 29.99)], 1029.98, '已完成', ('北京市', '朝阳区', '望京街道1号'), ['电子产品', '手机']),
(1002, 2, '2024-01-15 14:20:00', [('MacBook Pro', 1, 1999.99)], 1999.99, '已完成', ('上海市', '浦东新区', '陆家嘴金融区'), ['电子产品', '电脑']),
(1003, 1, '2024-01-16 09:15:00', [('Nike鞋', 1, 129.99), ('袜子', 3, 9.99)], 159.97, '处理中', ('北京市', '朝阳区', '望京街道1号'), ['服装', '运动']),
(1004, 3, '2024-01-16 16:45:00', [('书籍', 5, 19.99), ('笔记本', 2, 15.99)], 131.93, '已完成', ('广州市', '天河区', '天河路123号'), ['文具', '教育']);

-- 综合分析查询
SELECT '=== 电商订单综合分析 ===' as demo_section;

-- 用户订单统计
SELECT 
    user_id,
    count() as order_count,
    sum(total_amount) as total_spent,
    avg(total_amount) as avg_order_value,
    arrayStringConcat(arrayDistinct(arrayFlatten(groupArray(tags))), ',') as all_categories
FROM ecommerce_orders 
GROUP BY user_id
ORDER BY total_spent DESC;

-- 产品销售分析
SELECT '=== 产品销售分析 ===' as demo_section;
SELECT 
    product_name,
    sum(quantity) as total_sold,
    sum(quantity * price) as total_revenue,
    avg(price) as avg_price
FROM (
    SELECT 
        arrayJoin(products).1 as product_name,
        arrayJoin(products).2 as quantity,
        arrayJoin(products).3 as price
    FROM ecommerce_orders
    WHERE status = '已完成'
)
GROUP BY product_name
ORDER BY total_revenue DESC;

-- 地区分析
SELECT '=== 地区订单分析 ===' as demo_section;
SELECT 
    shipping_address.1 as province,
    shipping_address.2 as city,
    count() as order_count,
    sum(total_amount) as total_revenue,
    avg(total_amount) as avg_order_value
FROM ecommerce_orders 
WHERE status = '已完成'
GROUP BY province, city
ORDER BY total_revenue DESC;

-- 时间趋势分析
SELECT '=== 时间趋势分析 ===' as demo_section;
SELECT 
    toDate(order_time) as order_date,
    toHour(order_time) as order_hour,
    count() as order_count,
    sum(total_amount) as daily_revenue,
    uniq(user_id) as unique_customers
FROM ecommerce_orders 
GROUP BY order_date, order_hour
ORDER BY order_date, order_hour;

-- 清理演示表
SELECT '=== 演示完成，清理数据 ===' as demo_section;
DROP TABLE IF EXISTS numeric_types_demo;
DROP TABLE IF EXISTS string_types_demo;  
DROP TABLE IF EXISTS datetime_types_demo;
DROP TABLE IF EXISTS array_types_demo;
DROP TABLE IF EXISTS tuple_types_demo;
DROP TABLE IF EXISTS nullable_types_demo;
DROP TABLE IF EXISTS ecommerce_orders;

SELECT '✅ Day 4 数据类型演示完成！' as completion_message; 