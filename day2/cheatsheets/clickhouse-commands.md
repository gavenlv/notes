# ClickHouse 命令速查表

## 🚀 基础命令

### 连接和客户端

```bash
# 基本连接
clickhouse-client

# 指定主机和端口
clickhouse-client --host localhost --port 9000

# 指定用户和密码
clickhouse-client --user admin --password admin123

# 指定数据库
clickhouse-client --database mydb

# 执行单条查询
clickhouse-client --query "SELECT version()"

# 从文件执行SQL
clickhouse-client --queries-file script.sql

# 批量模式（非交互）
clickhouse-client --multiquery < script.sql
```

### HTTP接口

```bash
# 基本查询
curl 'http://localhost:8123/' --data-urlencode 'query=SELECT 1'

# 带认证
curl 'http://localhost:8123/' --user admin:password --data-urlencode 'query=SELECT version()'

# 指定格式
curl 'http://localhost:8123/' --data-urlencode 'query=SELECT * FROM table FORMAT JSON'

# 上传数据
curl 'http://localhost:8123/' --data-binary @data.csv --header "INSERT INTO table FORMAT CSV"
```

## 📊 数据库操作

### 数据库管理

```sql
-- 显示所有数据库
SHOW DATABASES;

-- 创建数据库
CREATE DATABASE mydb;
CREATE DATABASE IF NOT EXISTS mydb;

-- 删除数据库
DROP DATABASE mydb;
DROP DATABASE IF EXISTS mydb;

-- 使用数据库
USE mydb;
```

### 表管理

```sql
-- 显示表
SHOW TABLES;
SHOW TABLES FROM mydb;

-- 表结构
DESCRIBE table_name;
DESC table_name;

-- 创建表语句
SHOW CREATE TABLE table_name;

-- 删除表
DROP TABLE table_name;
DROP TABLE IF EXISTS table_name;

-- 重命名表
RENAME TABLE old_name TO new_name;

-- 清空表
TRUNCATE TABLE table_name;
```

## 🏗️ 表引擎

### MergeTree 系列

```sql
-- 基础 MergeTree
CREATE TABLE events (
    date Date,
    user_id UInt32,
    event String
) ENGINE = MergeTree()
ORDER BY (date, user_id);

-- ReplacingMergeTree (去重)
CREATE TABLE users (
    id UInt32,
    name String,
    updated DateTime
) ENGINE = ReplacingMergeTree(updated)
ORDER BY id;

-- SummingMergeTree (预聚合)
CREATE TABLE metrics (
    date Date,
    metric String,
    value UInt32
) ENGINE = SummingMergeTree(value)
ORDER BY (date, metric);

-- AggregatingMergeTree
CREATE TABLE agg_table (
    date Date,
    key String,
    value AggregateFunction(sum, UInt64)
) ENGINE = AggregatingMergeTree()
ORDER BY (date, key);
```

### 其他引擎

```sql
-- Memory 引擎
CREATE TABLE temp_data (
    id UInt32,
    value String
) ENGINE = Memory;

-- Log 引擎
CREATE TABLE log_data (
    timestamp DateTime,
    message String
) ENGINE = Log;

-- Distributed 引擎
CREATE TABLE distributed_table (
    id UInt32,
    value String
) ENGINE = Distributed(cluster_name, database_name, table_name, rand());
```

## 🔢 数据类型

### 数值类型

```sql
-- 整数类型
UInt8, UInt16, UInt32, UInt64    -- 无符号整数
Int8, Int16, Int32, Int64        -- 有符号整数

-- 浮点类型
Float32, Float64

-- 定点数类型
Decimal(P, S)
Decimal32(S), Decimal64(S), Decimal128(S), Decimal256(S)
```

### 字符串类型

```sql
String                  -- 可变长度字符串
FixedString(N)         -- 固定长度字符串
LowCardinality(String) -- 低基数字符串优化
```

### 日期时间类型

```sql
Date                   -- 日期 (2字节, 1900-2299)
Date32                 -- 扩展日期 (4字节, 1900-2299)
DateTime               -- 日期时间 (4字节, 精度到秒)
DateTime64             -- 高精度日期时间 (可配置精度)
```

### 复合类型

```sql
Array(T)                    -- 数组
Tuple(T1, T2, ...)         -- 元组
Map(K, V)                  -- 映射
Nested(col1 T1, col2 T2)   -- 嵌套表
Nullable(T)                -- 可空类型
Enum8('a'=1, 'b'=2)       -- 枚举
JSON                       -- JSON对象
```

## 📝 SQL 查询

### 基础查询

```sql
-- 选择
SELECT column1, column2 FROM table_name;
SELECT * FROM table_name;
SELECT DISTINCT column FROM table_name;

-- 条件
WHERE column = value;
WHERE column IN (value1, value2);
WHERE column BETWEEN value1 AND value2;
WHERE column LIKE 'pattern';
WHERE column IS NULL;
WHERE column IS NOT NULL;

-- 排序
ORDER BY column ASC;
ORDER BY column DESC;
ORDER BY column1, column2 DESC;

-- 限制
LIMIT 10;
LIMIT 10 OFFSET 20;
LIMIT 20, 10;  -- 从第20行开始，取10行
```

### 聚合查询

```sql
-- 基础聚合
COUNT(*), COUNT(column)
SUM(column), AVG(column)
MIN(column), MAX(column)
uniq(column)  -- 精确去重计数
uniqHLL12(column)  -- 近似去重计数

-- 分组
GROUP BY column;
GROUP BY column1, column2;
HAVING condition;

-- 窗口函数
ROW_NUMBER() OVER (PARTITION BY col ORDER BY col2)
RANK() OVER (ORDER BY col)
LAG(col) OVER (PARTITION BY col ORDER BY col2)
SUM(col) OVER (PARTITION BY col ORDER BY col2)
```

### 连接查询

```sql
-- 内连接
SELECT * FROM t1 INNER JOIN t2 ON t1.id = t2.id;
SELECT * FROM t1 JOIN t2 USING(id);

-- 左连接
SELECT * FROM t1 LEFT JOIN t2 ON t1.id = t2.id;

-- 全连接
SELECT * FROM t1 FULL JOIN t2 ON t1.id = t2.id;

-- 交叉连接
SELECT * FROM t1 CROSS JOIN t2;
```

## 🔧 数据操作

### 插入数据

```sql
-- 基础插入
INSERT INTO table VALUES (value1, value2);
INSERT INTO table (col1, col2) VALUES (val1, val2);

-- 批量插入
INSERT INTO table VALUES 
    (val1, val2),
    (val3, val4);

-- 从查询插入
INSERT INTO table SELECT * FROM other_table;

-- 从文件插入
INSERT INTO table FORMAT CSV 'data.csv';
INSERT INTO table FORMAT JSONEachRow 'data.json';
```

### 更新和删除

```sql
-- 更新 (异步操作)
ALTER TABLE table UPDATE column = value WHERE condition;

-- 删除 (异步操作)
ALTER TABLE table DELETE WHERE condition;

-- 立即执行
ALTER TABLE table UPDATE column = value WHERE condition SETTINGS mutations_sync = 1;
```

## 📋 系统表

### 常用系统表

```sql
-- 数据库信息
SELECT * FROM system.databases;

-- 表信息
SELECT * FROM system.tables WHERE database = 'mydb';

-- 列信息
SELECT * FROM system.columns WHERE database = 'mydb' AND table = 'mytable';

-- 当前进程
SELECT * FROM system.processes;

-- 查询日志
SELECT * FROM system.query_log ORDER BY event_time DESC LIMIT 10;

-- 性能指标
SELECT * FROM system.metrics;
SELECT * FROM system.events;

-- 表统计
SELECT * FROM system.parts WHERE database = 'mydb';
```

## ⚙️ 配置和管理

### 系统设置

```sql
-- 查看设置
SELECT * FROM system.settings WHERE name LIKE '%memory%';

-- 修改会话设置
SET max_memory_usage = 8000000000;
SET max_threads = 8;

-- 查询时设置
SELECT * FROM table SETTINGS max_memory_usage = 4000000000;
```

### 用户管理

```sql
-- 创建用户
CREATE USER user_name IDENTIFIED BY 'password';

-- 授权
GRANT SELECT ON database.* TO user_name;
GRANT ALL ON *.* TO user_name;

-- 撤销权限
REVOKE SELECT ON database.* FROM user_name;

-- 删除用户
DROP USER user_name;
```

## 🕒 时间函数

### 日期时间函数

```sql
-- 当前时间
now()                    -- 当前时间
today()                  -- 今天日期
yesterday()              -- 昨天日期

-- 格式化
formatDateTime(dt, '%Y-%m-%d')
toString(dt)
toDate(dt)
toDateTime(dt)

-- 提取部分
toYear(dt), toMonth(dt), toDay(dt)
toHour(dt), toMinute(dt), toSecond(dt)
toDayOfWeek(dt), toDayOfYear(dt)

-- 时间计算
addDays(dt, 5)
subtractDays(dt, 5)
addHours(dt, 3)

-- 时间窗口
toStartOfHour(dt)
toStartOfDay(dt)
toStartOfWeek(dt)
toStartOfMonth(dt)
toStartOfYear(dt)
```

## 🔤 字符串函数

```sql
-- 长度和检查
length(str)
empty(str)
notEmpty(str)

-- 大小写转换
upper(str), lower(str)
upperUTF8(str), lowerUTF8(str)

-- 截取和替换
substring(str, pos, len)
left(str, len), right(str, len)
replace(str, search, replace)
replaceAll(str, search, replace)

-- 分割和连接
splitByChar(sep, str)
arrayStringConcat(arr, sep)
concat(str1, str2, ...)

-- 模式匹配
match(str, pattern)
extract(str, pattern)
like(str, pattern)
```

## 📊 数组函数

```sql
-- 创建数组
[1, 2, 3]
array(1, 2, 3)
range(10)  -- [0,1,2,...,9]

-- 数组操作
length(arr)
has(arr, elem)
indexOf(arr, elem)
arrayConcat(arr1, arr2)
arraySlice(arr, offset, length)

-- 数组聚合
arraySum(arr)
arrayMin(arr), arrayMax(arr)
arrayUniq(arr)

-- 数组变换
arrayMap(func, arr)
arrayFilter(func, arr)
arraySort(arr)
arrayReverse(arr)
```

## 🚨 性能优化

### 查询优化

```sql
-- 使用 PREWHERE 替代 WHERE (在 MergeTree 中)
SELECT * FROM table PREWHERE date = today() WHERE user_id = 123;

-- 使用 SAMPLE 进行采样
SELECT * FROM table SAMPLE 0.1;  -- 10% 采样

-- 使用 FINAL 获取最新数据 (ReplacingMergeTree)
SELECT * FROM table FINAL;

-- 并行查询
SELECT * FROM table SETTINGS max_threads = 16;
```

### 监控查询

```sql
-- 查看正在运行的查询
SELECT query_id, user, query, elapsed 
FROM system.processes 
WHERE query != '';

-- 终止查询
KILL QUERY WHERE query_id = 'query_id';

-- 查询统计
SELECT 
    type,
    query_duration_ms,
    memory_usage,
    read_rows,
    read_bytes
FROM system.query_log 
WHERE event_time >= now() - INTERVAL 1 HOUR
ORDER BY query_duration_ms DESC
LIMIT 10;
```

## 🔧 运维命令

### 服务管理

```bash
# 启动/停止服务
sudo systemctl start clickhouse-server
sudo systemctl stop clickhouse-server
sudo systemctl restart clickhouse-server
sudo systemctl status clickhouse-server

# 查看日志
sudo tail -f /var/log/clickhouse-server/clickhouse-server.log
sudo tail -f /var/log/clickhouse-server/clickhouse-server.err.log

# 配置检查
clickhouse-server --config-file=/etc/clickhouse-server/config.xml --check-config
```

### 备份和恢复

```sql
-- 冻结表（创建硬链接备份）
ALTER TABLE table FREEZE;

-- 创建表的备份
BACKUP TABLE table TO DISK 'backup_disk';

-- 从备份恢复
RESTORE TABLE table FROM DISK 'backup_disk';
```

## 📈 常用查询模式

### 日志分析

```sql
-- 错误日志统计
SELECT 
    toStartOfHour(timestamp) as hour,
    level,
    COUNT(*) as count
FROM logs 
WHERE timestamp >= now() - INTERVAL 24 HOUR
GROUP BY hour, level
ORDER BY hour, count DESC;

-- Top N 查询
SELECT 
    ip,
    COUNT(*) as requests
FROM access_logs 
WHERE timestamp >= today()
GROUP BY ip
ORDER BY requests DESC
LIMIT 10;
```

### 时间序列分析

```sql
-- 移动平均
SELECT 
    timestamp,
    value,
    avg(value) OVER (
        ORDER BY timestamp 
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) as moving_avg
FROM metrics
ORDER BY timestamp;

-- 环比增长
SELECT 
    date,
    value,
    LAG(value) OVER (ORDER BY date) as prev_value,
    (value - prev_value) / prev_value * 100 as growth_rate
FROM daily_metrics
ORDER BY date;
```

---

💡 **提示**: 这个速查表涵盖了 ClickHouse 的常用命令和语法。建议根据实际使用情况添加更多特定于业务的查询模式。 