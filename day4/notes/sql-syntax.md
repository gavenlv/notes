# Day 4: ClickHouse SQL语法与数据类型

## 学习目标 🎯
- 掌握ClickHouse SQL语法特性和与标准SQL的差异
- 理解ClickHouse数据类型系统
- 学会数据库和表的创建管理
- 掌握数据插入、查询和更新操作
- 了解ClickHouse特有的SQL函数

## 为什么Day 4学SQL语法？ 🤔

前3天我们已经：
- ✅ Day 1: 搭建了环境
- ✅ Day 2: 理解了核心概念
- ✅ Day 3: 学会了云端部署

现在该系统学习如何使用ClickHouse了！SQL是与数据库交互的主要方式。

### 学习路径回顾
```
Day 1: 环境搭建 ✅ → Day 2: 理论基础 ✅ → Day 3: 云端部署 ✅ → Day 4: SQL语法
```

## 知识要点 📚

### 1. ClickHouse SQL语法概述

#### SQL兼容性
ClickHouse支持标准SQL语法，但有以下特点：
- **查询优先**: 针对OLAP场景优化
- **批量操作**: 适合大数据量处理
- **函数丰富**: 提供大量分析函数
- **扩展语法**: 增加了许多ClickHouse特有功能

#### 与标准SQL的差异
| 特性 | 标准SQL | ClickHouse |
|------|---------|------------|
| JOIN语法 | 完全支持 | 部分支持，性能导向 |
| 事务支持 | ACID | 最终一致性 |
| UPDATE/DELETE | 频繁使用 | 批量操作，谨慎使用 |
| 子查询 | 完全支持 | 优化有限 |
| 窗口函数 | 标准支持 | 增强功能 |

### 2. 数据类型系统

#### 2.1 数值类型

**整数类型**
```sql
-- 有符号整数
Int8    -- -128 到 127
Int16   -- -32,768 到 32,767  
Int32   -- -2,147,483,648 到 2,147,483,647
Int64   -- -9,223,372,036,854,775,808 到 9,223,372,036,854,775,807

-- 无符号整数
UInt8   -- 0 到 255
UInt16  -- 0 到 65,535
UInt32  -- 0 到 4,294,967,295
UInt64  -- 0 到 18,446,744,073,709,551,615

-- 使用示例
CREATE TABLE numbers_example (
    small_int Int8,
    medium_int Int32,
    big_int Int64,
    positive_int UInt32
) ENGINE = Memory;
```

**浮点类型**
```sql
-- 浮点数
Float32  -- IEEE 754 单精度
Float64  -- IEEE 754 双精度

-- 定点数（精确decimal）
Decimal(P, S)     -- P是精度，S是小数位数
Decimal32(S)      -- 相当于Decimal(9, S)
Decimal64(S)      -- 相当于Decimal(18, S)
Decimal128(S)     -- 相当于Decimal(38, S)

-- 示例
CREATE TABLE financial_data (
    amount Decimal(10, 2),    -- 金额，保留2位小数
    rate Float64,             -- 利率
    price Decimal64(4)        -- 价格，保留4位小数
) ENGINE = Memory;
```

#### 2.2 字符串类型

```sql
-- 变长字符串
String               -- 无长度限制

-- 定长字符串  
FixedString(N)      -- 固定N个字节

-- 使用示例
CREATE TABLE text_example (
    name String,                -- 姓名
    code FixedString(10),      -- 10字符编码
    description String          -- 描述
) ENGINE = Memory;

-- 插入数据
INSERT INTO text_example VALUES 
('张三', '0000000001', '这是一个测试用户'),
('李四', '0000000002', 'Another test user');
```

#### 2.3 日期时间类型

```sql
-- 日期类型
Date                 -- 日期：2000-01-01 到 2106-02-07
Date32               -- 扩展日期：1900-01-01 到 2299-12-31

-- 时间戳类型
DateTime             -- 时间戳：1970-01-01 00:00:00 到 2106-02-07 06:28:15
DateTime64(precision) -- 高精度时间戳

-- 时区支持
DateTime('timezone')
DateTime64(precision, 'timezone')

-- 示例
CREATE TABLE events (
    event_id UInt32,
    event_date Date,
    event_time DateTime,
    precise_time DateTime64(3),           -- 毫秒精度
    utc_time DateTime('UTC'),             -- UTC时区
    shanghai_time DateTime('Asia/Shanghai') -- 上海时区
) ENGINE = Memory;

-- 插入示例数据
INSERT INTO events VALUES
(1, '2024-01-01', '2024-01-01 10:30:00', '2024-01-01 10:30:00.123', '2024-01-01 02:30:00', '2024-01-01 10:30:00');
```

#### 2.4 复合数据类型

**数组类型**
```sql
-- 数组语法
Array(T)             -- T类型的数组

-- 示例
CREATE TABLE array_example (
    id UInt32,
    numbers Array(Int32),        -- 整数数组
    names Array(String),         -- 字符串数组
    scores Array(Float64)        -- 浮点数组组
) ENGINE = Memory;

-- 插入数组数据
INSERT INTO array_example VALUES
(1, [1, 2, 3, 4, 5], ['a', 'b', 'c'], [95.5, 87.2, 92.8]),
(2, [10, 20], ['hello', 'world'], [88.0, 90.5]);

-- 数组操作函数
SELECT 
    id,
    length(numbers) as array_length,
    numbers[1] as first_number,
    arraySum(scores) as total_score
FROM array_example;
```

**元组类型**
```sql
-- 元组语法
Tuple(T1, T2, ...)   -- 多种类型组合

-- 示例
CREATE TABLE tuple_example (
    id UInt32,
    coordinate Tuple(Float64, Float64),    -- 坐标点
    person_info Tuple(String, UInt8, String) -- 姓名,年龄,城市
) ENGINE = Memory;

-- 插入元组数据
INSERT INTO tuple_example VALUES
(1, (39.9042, 116.4074), ('张三', 25, '北京')),
(2, (31.2304, 121.4737), ('李四', 30, '上海'));

-- 访问元组元素
SELECT 
    id,
    coordinate.1 as latitude,
    coordinate.2 as longitude,
    person_info.1 as name,
    person_info.2 as age
FROM tuple_example;
```

**嵌套类型（已弃用，但了解概念）**
```sql
-- 使用Array(Tuple(...))替代
CREATE TABLE nested_example (
    id UInt32,
    users Array(Tuple(String, UInt8, Array(String))) -- 用户列表
) ENGINE = Memory;
```

#### 2.5 特殊类型

**可空类型**
```sql
-- 允许NULL值
Nullable(T)

-- 示例
CREATE TABLE nullable_example (
    id UInt32,
    name String,
    age Nullable(UInt8),        -- 年龄可以为空
    email Nullable(String)      -- 邮箱可以为空
) ENGINE = Memory;

-- 插入包含NULL的数据
INSERT INTO nullable_example VALUES
(1, '张三', 25, 'zhang@example.com'),
(2, '李四', NULL, NULL),
(3, '王五', 30, 'wang@example.com');

-- 处理NULL值
SELECT 
    name,
    isNull(age) as age_is_null,
    ifNull(age, 0) as age_or_zero,
    coalesce(email, 'no-email') as email_or_default
FROM nullable_example;
```

**低基数类型**
```sql
-- 优化重复值存储
LowCardinality(T)

-- 适用场景：枚举值、分类数据
CREATE TABLE user_analytics (
    user_id UInt32,
    country LowCardinality(String),     -- 国家（重复值多）
    browser LowCardinality(String),     -- 浏览器（重复值多）
    event_type LowCardinality(String),  -- 事件类型（重复值多）
    timestamp DateTime
) ENGINE = Memory;
```

### 3. 数据库和表管理

#### 3.1 数据库操作

```sql
-- 创建数据库
CREATE DATABASE tutorial;
CREATE DATABASE IF NOT EXISTS tutorial;

-- 查看数据库
SHOW DATABASES;

-- 使用数据库
USE tutorial;

-- 删除数据库（谨慎使用）
DROP DATABASE tutorial;
DROP DATABASE IF EXISTS tutorial;
```

#### 3.2 表操作

**创建表**
```sql
-- 基本语法
CREATE TABLE [IF NOT EXISTS] [db.]table_name (
    column1 Type1,
    column2 Type2,
    ...
) ENGINE = engine_name
[ORDER BY (...)]
[PARTITION BY (...)]
[SETTINGS setting = value, ...];

-- 示例：用户行为分析表
CREATE TABLE user_behavior (
    user_id UInt32,
    event_time DateTime,
    event_type LowCardinality(String),
    page_url String,
    referrer Nullable(String),
    user_agent String,
    ip_address IPv4,
    country LowCardinality(String),
    city String,
    session_id String
) ENGINE = MergeTree()
ORDER BY (user_id, event_time)
PARTITION BY toYYYYMM(event_time);
```

**查看表结构**
```sql
-- 查看表列表
SHOW TABLES;
SHOW TABLES FROM database_name;

-- 查看表结构
DESCRIBE table_name;
DESC table_name;

-- 查看建表语句
SHOW CREATE TABLE table_name;

-- 查看表统计信息
SELECT 
    database,
    table,
    engine,
    total_rows,
    total_bytes
FROM system.tables 
WHERE database = currentDatabase();
```

**修改表结构**
```sql
-- 添加列
ALTER TABLE table_name ADD COLUMN column_name Type;
ALTER TABLE table_name ADD COLUMN IF NOT EXISTS column_name Type;

-- 删除列
ALTER TABLE table_name DROP COLUMN column_name;
ALTER TABLE table_name DROP COLUMN IF EXISTS column_name;

-- 修改列类型
ALTER TABLE table_name MODIFY COLUMN column_name NewType;

-- 重命名列
ALTER TABLE table_name RENAME COLUMN old_name TO new_name;

-- 示例
ALTER TABLE user_behavior ADD COLUMN device_type LowCardinality(String);
ALTER TABLE user_behavior MODIFY COLUMN city LowCardinality(String);
```

### 4. 数据操作

#### 4.1 插入数据

**基本插入**
```sql
-- 插入单行
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...);

-- 插入多行
INSERT INTO table_name VALUES 
(value1, value2, ...),
(value1, value2, ...),
...;

-- 示例
INSERT INTO user_behavior VALUES
(1001, '2024-01-01 10:00:00', 'page_view', '/home', NULL, 'Mozilla/5.0...', '192.168.1.1', 'China', 'Beijing', 'sess_001'),
(1002, '2024-01-01 10:01:00', 'click', '/product/123', '/home', 'Mozilla/5.0...', '192.168.1.2', 'China', 'Shanghai', 'sess_002');
```

**从文件插入**
```sql
-- 从CSV文件插入
INSERT INTO table_name FROM INFILE 'path/to/file.csv' FORMAT CSV;

-- 从TSV文件插入
INSERT INTO table_name FROM INFILE 'path/to/file.tsv' FORMAT TSV;
```

**从查询结果插入**
```sql
-- 插入查询结果
INSERT INTO target_table 
SELECT column1, column2, ... 
FROM source_table 
WHERE condition;

-- 创建表并插入数据
CREATE TABLE daily_summary AS 
SELECT 
    toDate(event_time) as date,
    country,
    count() as page_views,
    uniq(user_id) as unique_users
FROM user_behavior 
WHERE event_type = 'page_view'
GROUP BY date, country;
```

#### 4.2 查询数据

**基本查询**
```sql
-- 基本SELECT
SELECT * FROM table_name;
SELECT column1, column2 FROM table_name;

-- 条件查询
SELECT * FROM user_behavior 
WHERE country = 'China' 
  AND event_time >= '2024-01-01'
  AND event_time < '2024-01-02';

-- 排序
SELECT * FROM user_behavior 
ORDER BY event_time DESC 
LIMIT 10;

-- 去重
SELECT DISTINCT country FROM user_behavior;
```

**聚合查询**
```sql
-- 基本聚合
SELECT 
    country,
    count() as total_events,
    uniq(user_id) as unique_users,
    avg(if(event_type = 'page_view', 1, 0)) as page_view_rate
FROM user_behavior 
GROUP BY country
ORDER BY total_events DESC;

-- 时间维度聚合
SELECT 
    toDate(event_time) as date,
    toHour(event_time) as hour,
    count() as events_count
FROM user_behavior 
GROUP BY date, hour
ORDER BY date, hour;
```

**窗口函数**
```sql
-- 排名函数
SELECT 
    user_id,
    event_time,
    row_number() OVER (PARTITION BY user_id ORDER BY event_time) as event_sequence,
    rank() OVER (ORDER BY event_time DESC) as time_rank
FROM user_behavior;

-- 累计计算
SELECT 
    date,
    daily_users,
    sum(daily_users) OVER (ORDER BY date) as cumulative_users
FROM (
    SELECT 
        toDate(event_time) as date,
        uniq(user_id) as daily_users
    FROM user_behavior 
    GROUP BY date
);
```

#### 4.3 更新和删除数据

> ⚠️ **注意**: ClickHouse不建议频繁UPDATE/DELETE，这些操作成本较高

**更新数据**
```sql
-- ALTER UPDATE（异步操作）
ALTER TABLE user_behavior 
UPDATE country = 'CN' 
WHERE country = 'China';

-- 需要等待操作完成
-- 检查操作状态
SELECT * FROM system.mutations WHERE table = 'user_behavior';
```

**删除数据**
```sql
-- ALTER DELETE（异步操作）
ALTER TABLE user_behavior 
DELETE WHERE event_time < '2024-01-01';

-- 轻量级删除（推荐）
DELETE FROM user_behavior WHERE user_id = 1001;
```

**分区操作（推荐的数据管理方式）**
```sql
-- 删除整个分区（高效）
ALTER TABLE user_behavior DROP PARTITION '202312';

-- 查看分区
SELECT 
    partition,
    rows,
    bytes_on_disk
FROM system.parts 
WHERE table = 'user_behavior' 
  AND active;
```

### 5. ClickHouse特有函数

#### 5.1 字符串函数

```sql
-- 字符串操作
SELECT 
    lower('Hello World') as lowercase,                    -- hello world
    upper('hello world') as uppercase,                    -- HELLO WORLD
    length('中文测试') as str_length,                      -- 4
    substring('ClickHouse', 1, 5) as substr,             -- Click
    concat('Hello', ' ', 'World') as concatenated,       -- Hello World
    splitByChar(',', 'a,b,c') as split_result;          -- ['a','b','c']

-- URL函数
SELECT 
    protocol('https://example.com/path?query=1') as protocol,        -- https
    domain('https://example.com/path?query=1') as domain,           -- example.com
    path('https://example.com/path?query=1') as path;              -- /path
```

#### 5.2 日期时间函数

```sql
-- 日期时间操作
SELECT 
    now() as current_time,
    today() as current_date,
    toYear(now()) as current_year,
    toMonth(now()) as current_month,
    toDayOfWeek(now()) as day_of_week,
    formatDateTime(now(), '%Y-%m-%d %H:%M:%S') as formatted;

-- 日期计算
SELECT 
    addDays(today(), 7) as next_week,
    addMonths(today(), 1) as next_month,
    dateDiff('day', '2024-01-01', today()) as days_passed;

-- 时间截断
SELECT 
    toStartOfMonth(now()) as month_start,
    toStartOfWeek(now()) as week_start,
    toStartOfHour(now()) as hour_start;
```

#### 5.3 数组函数

```sql
-- 数组操作
SELECT 
    [1, 2, 3, 4, 5] as arr,
    length([1, 2, 3]) as array_length,                   -- 3
    arraySum([1, 2, 3, 4, 5]) as sum_result,            -- 15
    arrayMax([1, 2, 3, 4, 5]) as max_value,             -- 5
    arrayFilter(x -> x > 3, [1, 2, 3, 4, 5]) as filtered, -- [4, 5]
    arrayMap(x -> x * 2, [1, 2, 3]) as doubled;         -- [2, 4, 6]
```

#### 5.4 聚合函数

```sql
-- 基本聚合
SELECT 
    count() as total_rows,
    sum(user_id) as sum_user_ids,
    avg(user_id) as avg_user_id,
    min(event_time) as earliest_event,
    max(event_time) as latest_event;

-- 高级聚合
SELECT 
    uniq(user_id) as unique_users,                       -- 精确去重
    uniqHLL12(user_id) as approx_unique_users,          -- 近似去重
    quantile(0.5)(user_id) as median_user_id,           -- 中位数
    quantiles(0.25, 0.5, 0.75)(user_id) as quartiles;   -- 四分位数
```

## 实践练习 🛠️

### 练习1：创建完整的电商分析表

```sql
-- 创建商品表
CREATE TABLE products (
    product_id UInt32,
    product_name String,
    category LowCardinality(String),
    price Decimal(10, 2),
    created_at DateTime
) ENGINE = MergeTree()
ORDER BY product_id;

-- 创建订单表
CREATE TABLE orders (
    order_id UInt64,
    user_id UInt32,
    product_id UInt32,
    quantity UInt16,
    order_amount Decimal(10, 2),
    order_time DateTime,
    status LowCardinality(String)
) ENGINE = MergeTree()
ORDER BY (user_id, order_time)
PARTITION BY toYYYYMM(order_time);

-- 插入测试数据
INSERT INTO products VALUES
(1, 'iPhone 15', 'Electronics', 999.99, '2024-01-01 00:00:00'),
(2, 'MacBook Pro', 'Electronics', 1999.99, '2024-01-01 00:00:00'),
(3, 'Nike Shoes', 'Fashion', 129.99, '2024-01-01 00:00:00');

INSERT INTO orders VALUES
(1001, 1, 1, 1, 999.99, '2024-01-15 10:30:00', 'completed'),
(1002, 2, 2, 1, 1999.99, '2024-01-15 11:00:00', 'completed'),
(1003, 1, 3, 2, 259.98, '2024-01-16 14:20:00', 'pending');
```

### 练习2：复杂查询分析

```sql
-- 查询每日销售统计
SELECT 
    toDate(order_time) as date,
    count() as order_count,
    sum(order_amount) as total_revenue,
    avg(order_amount) as avg_order_value,
    uniq(user_id) as unique_customers
FROM orders 
WHERE status = 'completed'
GROUP BY date
ORDER BY date;

-- 查询用户购买行为分析
WITH user_stats AS (
    SELECT 
        user_id,
        count() as order_count,
        sum(order_amount) as total_spent,
        min(order_time) as first_order,
        max(order_time) as last_order
    FROM orders 
    WHERE status = 'completed'
    GROUP BY user_id
)
SELECT 
    user_id,
    order_count,
    total_spent,
    total_spent / order_count as avg_order_value,
    dateDiff('day', first_order, last_order) as customer_lifetime_days
FROM user_stats
ORDER BY total_spent DESC;
```

### 练习3：数据类型综合应用

运行day4的示例文件：
```bash
clickhouse-client < day4/examples/data-types-demo.sql
```

## 最佳实践 💡

### 1. 数据类型选择
- **选择合适的整数类型**: 不要过度使用UInt64，UInt32通常足够
- **使用LowCardinality**: 对于重复值多的字符串字段
- **谨慎使用Nullable**: 只在必要时使用，影响性能
- **利用数组类型**: 减少JOIN操作

### 2. 表结构设计
- **合理选择ORDER BY**: 根据查询模式优化排序键
- **适当分区**: 按时间或其他维度分区，便于数据管理
- **避免过多小列**: 合并相关字段到复合类型

### 3. 查询优化
- **利用分区裁剪**: WHERE条件包含分区键
- **减少SELECT ***: 只查询需要的列
- **合理使用索引**: 理解ClickHouse的稀疏索引
- **批量操作**: 避免频繁的小批量INSERT

## 常见问题 ❓

### Q1: 为什么我的UPDATE很慢？
**A**: ClickHouse不适合频繁更新，考虑：
- 使用INSERT新数据替代UPDATE
- 批量UPDATE而不是逐行更新
- 考虑重新设计数据模型

### Q2: 如何处理重复数据？
**A**: 几种方法：
- 使用ReplacingMergeTree引擎
- 业务层去重
- 查询时使用DISTINCT

### Q3: 字符串类型选择困惑？
**A**: 选择指南：
- 一般情况用String
- 固定长度且性能要求高用FixedString
- 重复值多用LowCardinality(String)

## 今日总结 📋

今天我们学习了：
- ✅ ClickHouse SQL语法特性
- ✅ 完整的数据类型系统
- ✅ 数据库和表管理操作
- ✅ 数据的增删改查
- ✅ ClickHouse特有函数
- ✅ 实际案例练习

**下一步**: Day 5 - 表引擎详解，深入理解ClickHouse的存储核心

---
*学习进度: Day 4/14 完成* 🎉 