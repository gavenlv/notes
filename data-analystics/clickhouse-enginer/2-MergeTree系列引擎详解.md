# MergeTree系列引擎详解

MergeTree系列是ClickHouse中最核心的引擎系列，专为OLAP场景设计。本节详细介绍MergeTree系列的各种引擎及其使用场景。

## 1. MergeTree基础引擎

### 1.1 引擎特点

MergeTree是ClickHouse中最通用的表引擎，具有以下特点：

- **数据分区**：支持按任意表达式分区数据
- **数据排序**：每个分区内的数据按主键排序
- **稀疏索引**：基于主键的稀疏索引，加速数据查询
- **数据合并**：后台定期合并数据块，优化存储和查询性能
- **TTL支持**：支持数据的自动过期处理

### 1.2 基本语法

```sql
CREATE TABLE table_name (
    column1 Type1,
    column2 Type2,
    ...
) ENGINE = MergeTree()
[PARTITION BY expr]
[ORDER BY expr]
[PRIMARY KEY expr]
[SAMPLE BY expr]
[TTL expr]
[SETTINGS name=value, ...]
```

### 1.3 参数说明

- **PARTITION BY**：分区键，决定数据如何分区
- **ORDER BY**：排序键，决定每个分区内数据的排序方式
- **PRIMARY KEY**：主键，如果不指定则默认与ORDER BY相同
- **SAMPLE BY**：抽样键，用于数据抽样
- **TTL**：数据生存时间规则
- **SETTINGS**：表级别的设置

### 1.4 实例：创建基础MergeTree表

```sql
CREATE TABLE events (
    event_date Date,
    event_time DateTime,
    user_id UInt64,
    event_type String,
    platform String,
    revenue Decimal(10, 2),
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, event_type, user_id)
PRIMARY KEY (event_date, event_type)
TTL event_date + INTERVAL 90 DAY
SETTINGS index_granularity = 8192;
```

## 2. ReplacingMergeTree引擎

### 2.1 引擎特点

ReplacingMergeTree用于去重场景，具有以下特点：

- 相同排序键的记录在合并时会保留最新版本
- 支持版本列，用于决定保留哪条记录
- 不会立即删除重复数据，只在合并时生效

### 2.2 基本语法

```sql
CREATE TABLE table_name (
    column1 Type1,
    column2 Type2,
    version_column Type
) ENGINE = ReplacingMergeTree([version_column])
[PARTITION BY expr]
[ORDER BY expr]
[PRIMARY KEY expr]
[SAMPLE BY expr]
[TTL expr]
[SETTINGS name=value, ...]
```

### 2.3 版本列说明

- 如果指定了版本列，则保留版本号最大的记录
- 如果未指定版本列，则保留最后插入的记录

### 2.4 实例：用户状态表

```sql
CREATE TABLE user_status (
    user_id UInt64,
    status String,
    update_time DateTime,
    version UInt64 DEFAULT toUnixTimestamp(update_time)
) ENGINE = ReplacingMergeTree(version)
PARTITION BY toYYYYMM(update_time)
ORDER BY user_id
PRIMARY KEY user_id;

-- 插入数据
INSERT INTO user_status VALUES (1, 'active', '2023-01-01 10:00:00', 1672567200);
INSERT INTO user_status VALUES (1, 'inactive', '2023-01-02 12:00:00', 1672665600);

-- 手动触发合并
OPTIMIZE TABLE user_status FINAL;
```

## 3. SummingMergeTree引擎

### 3.1 引擎特点

SummingMergeTree用于预聚合场景，具有以下特点：

- 相同排序键的记录在合并时对数值列求和
- 只对数值类型列进行求和
- 非数值列保留第一条记录的值

### 3.2 基本语法

```sql
CREATE TABLE table_name (
    column1 Type1,
    column2 Type2,
    sum_column1 Type,
    sum_column2 Type,
    ...
) ENGINE = SummingMergeTree([columns_to_sum])
[PARTITION BY expr]
[ORDER BY expr]
[PRIMARY KEY expr]
[SAMPLE BY expr]
[TTL expr]
[SETTINGS name=value, ...]
```

### 3.3 参数说明

- columns_to_sum：指定哪些列需要求和，如果未指定则对所有数值类型列求和

### 3.4 实例：小时级指标汇总

```sql
CREATE TABLE hourly_stats (
    event_date Date,
    event_hour UInt8,
    metric_name String,
    value UInt64
) ENGINE = SummingMergeTree(value)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, event_hour, metric_name);

-- 插入数据
INSERT INTO hourly_stats VALUES 
    ('2023-01-01', 10, 'page_views', 100),
    ('2023-01-01', 10, 'page_views', 150),
    ('2023-01-01', 10, 'clicks', 30),
    ('2023-01-01', 10, 'clicks', 20);

-- 手动触发合并
OPTIMIZE TABLE hourly_stats FINAL;
```

## 4. AggregatingMergeTree引擎

### 4.1 引擎特点

AggregatingMergeTree用于高级聚合场景，支持任意聚合函数：

- 存储聚合函数的中间状态
- 合并时正确合并聚合状态
- 支持多种聚合函数：count, sum, avg, uniq, min, max等

### 4.2 基本语法

```sql
CREATE TABLE table_name (
    column1 Type1,
    column2 Type2,
    agg_state_col AggregateFunction(agg_func, param_type),
    ...
) ENGINE = AggregatingMergeTree()
[PARTITION BY expr]
[ORDER BY expr]
[PRIMARY KEY expr]
[SAMPLE BY expr]
[TTL expr]
[SETTINGS name=value, ...]
```

### 4.3 聚合函数类型

- `AggregateFunction(count, Type)`：计数
- `AggregateFunction(sum, Type)`：求和
- `AggregateFunction(avg, Type)`：平均值
- `AggregateFunction(uniq, Type)`：唯一值计数
- `AggregateFunction(any, Type)`：任意值

### 4.4 实例：用户行为统计

```sql
-- 创建预聚合表
CREATE TABLE user_activity_agg (
    date Date,
    user_group String,
    activity_type String,
    users AggregateFunction(uniq, UInt64),
    page_views AggregateFunction(sum, UInt64),
    session_time AggregateFunction(avg, UInt64)
) ENGINE = AggregatingMergeTree()
PARTITION BY date
ORDER BY (date, user_group, activity_type);

-- 插入聚合数据
INSERT INTO user_activity_agg SELECT
    toDate(event_time) AS date,
    CASE WHEN user_id % 1000 < 500 THEN 'group_a' ELSE 'group_b' END AS user_group,
    event_type AS activity_type,
    uniqState(user_id) AS users,
    sumState(toUInt64(revenue * 100)) AS page_views,
    avgState(session_duration) AS session_time
FROM events
WHERE event_time >= today() - INTERVAL 1 DAY
GROUP BY date, user_group, event_type;

-- 查询聚合结果
SELECT
    date,
    user_group,
    activity_type,
    uniqMerge(users) AS unique_users,
    sumMerge(page_views) / 100.0 AS total_revenue,
    avgMerge(session_time) AS avg_session_time
FROM user_activity_agg
WHERE date = today() - INTERVAL 1 DAY
GROUP BY date, user_group, activity_type
ORDER BY date, user_group, activity_type;
```

## 5. CollapsingMergeTree引擎

### 5.1 引擎特点

CollapsingMergeTree用于数据删除和更新场景：

- 通过符号列标识记录的增删
- 合并时正确处理成对的记录
- 适合频繁更新的场景

### 5.2 基本语法

```sql
CREATE TABLE table_name (
    column1 Type1,
    column2 Type2,
    sign Column Int8
) ENGINE = CollapsingMergeTree(sign)
[PARTITION BY expr]
[ORDER BY expr]
[PRIMARY KEY expr]
[SAMPLE BY expr]
[TTL expr]
[SETTINGS name=value, ...]
```

### 5.3 符号列说明

- sign = 1：表示记录应保留
- sign = -1：表示记录应删除
- 对于相同排序键的记录，sign=1和sign=-1成对出现时会被删除

### 5.4 实例：产品库存管理

```sql
CREATE TABLE product_inventory (
    product_id UInt64,
    warehouse_id UInt64,
    quantity Int32,
    update_time DateTime,
    sign Int8 MATERIALIZED 1  -- 默认为1（插入）
) ENGINE = CollapsingMergeTree(sign)
PARTITION BY toYYYYMM(update_time)
ORDER BY (product_id, warehouse_id);

-- 插入初始库存
INSERT INTO product_inventory (product_id, warehouse_id, quantity, update_time) VALUES 
    (1, 100, 100, '2023-01-01 08:00:00'),
    (2, 100, 200, '2023-01-01 08:00:00');

-- 更新库存：插入删除记录 + 插入新记录
INSERT INTO product_inventory VALUES (1, 100, 100, '2023-01-02 09:00:00', -1);  -- 删除旧记录
INSERT INTO product_inventory VALUES (1, 100, 150, '2023-01-02 09:00:00', 1);   -- 插入新记录

-- 查询当前库存
SELECT 
    product_id, 
    warehouse_id, 
    sum(quantity * sign) AS current_quantity
FROM product_inventory
GROUP BY product_id, warehouse_id
HAVING current_quantity > 0;
```

## 6. VersionedCollapsingMergeTree引擎

### 6.1 引擎特点

VersionedCollapsingMergeTree是CollapsingMergeTree的改进版：

- 通过版本列处理不成对的删除记录
- 在合并时根据版本正确处理记录
- 避免了CollapsingMergeTree中可能出现的数据不一致问题

### 6.2 基本语法

```sql
CREATE TABLE table_name (
    column1 Type1,
    column2 Type2,
    sign Int8,
    version UInt64
) ENGINE = VersionedCollapsingMergeTree(sign, version)
[PARTITION BY expr]
[ORDER BY expr]
[PRIMARY KEY expr]
[SAMPLE BY expr]
[TTL expr]
[SETTINGS name=value, ...]
```

### 6.3 实例：订单状态管理

```sql
CREATE TABLE orders_status (
    order_id UInt64,
    status String,
    update_time DateTime,
    sign Int8,
    version UInt64
) ENGINE = VersionedCollapsingMergeTree(sign, version)
PARTITION BY toYYYYMM(update_time)
ORDER BY order_id;

-- 插入订单状态
INSERT INTO orders_status VALUES 
    (1001, 'pending', '2023-01-01 10:00:00', 1, 1),
    (1002, 'pending', '2023-01-01 11:00:00', 1, 1);

-- 更新订单状态
INSERT INTO orders_status VALUES 
    (1001, 'processing', '2023-01-02 09:00:00', -1, 1),  -- 删除旧状态
    (1001, 'processing', '2023-01-02 09:00:00', 1, 2);   -- 插入新状态

-- 查询当前订单状态
SELECT *
FROM (
    SELECT 
        order_id, 
        status, 
        update_time,
        row_number() OVER (PARTITION BY order_id ORDER BY version DESC, update_time DESC) AS rn
    FROM orders_status
)
WHERE rn = 1;
```

## 7. GraphiteMergeTree引擎

### 7.1 引擎特点

GraphiteMergeTree专为Graphite时间序列数据设计：

- 自动降低时间序列数据的精度
- 支持不同的数据保留策略
- 优化存储和查询性能

### 7.2 基本语法

```sql
CREATE TABLE table_name (
    path String,
    time DateTime,
    value Float64,
    timestamp Float64
) ENGINE = GraphiteMergeTree(config_section)
[PARTITION BY expr]
[ORDER BY expr]
[PRIMARY KEY expr]
[SAMPLE BY expr]
[TTL expr]
[SETTINGS name=value, ...]
```

### 7.3 实例：系统指标存储

```sql
CREATE TABLE graphite_metrics (
    path String,
    time DateTime,
    value Float64,
    timestamp Float64 MATERIALIZED time
) ENGINE = GraphiteMergeTree('graphite_rollup')
PARTITION BY toYYYYMMDD(time)
ORDER BY (path, time);

-- 插入指标数据
INSERT INTO graphite_metrics (path, time, value) VALUES
    ('servers.cpu.usage', '2023-01-01 00:00:00', 45.2),
    ('servers.cpu.usage', '2023-01-01 01:00:00', 48.7),
    ('servers.cpu.usage', '2023-01-01 02:00:00', 52.1),
    ('servers.memory.usage', '2023-01-01 00:00:00', 65.3),
    ('servers.memory.usage', '2023-01-01 01:00:00', 67.8);
```

## 8. MergeTree系列引擎对比

| 引擎类型 | 主要用途 | 优点 | 缺点 | 适用场景 |
|---------|---------|------|------|----------|
| MergeTree | 通用分析 | 功能全面，性能均衡 | 无特殊优化 | 一般分析查询 |
| ReplacingMergeTree | 数据去重 | 自动处理重复数据 | 合并时才生效 | 用户状态，配置信息 |
| SummingMergeTree | 预聚合 | 自动求和聚合 | 只适用于数值列 | 指标统计，计数器 |
| AggregatingMergeTree | 高级聚合 | 支持多种聚合函数 | 使用复杂 | 预聚合，高级统计 |
| CollapsingMergeTree | 数据更新 | 支持删除/更新 | 容易出错 | 库存管理，状态跟踪 |
| VersionedCollapsingMergeTree | 版本化更新 | 避免数据不一致 | 复杂度高 | 订单状态，版本控制 |
| GraphiteMergeTree | 时间序列 | 自动数据降精度 | 仅适用于Graphite | 监控指标，时序数据 |

## 9. 最佳实践

### 9.1 选择合适的引擎

- **通用分析**：使用MergeTree
- **去重场景**：使用ReplacingMergeTree
- **预聚合**：使用SummingMergeTree或AggregatingMergeTree
- **频繁更新**：使用CollapsingMergeTree或VersionedCollapsingMergeTree

### 9.2 分区策略

- 使用时间字段作为分区键
- 避免分区过细（建议每个分区1-10GB）
- 考虑查询模式，将常用查询条件作为分区键

### 9.3 排序键设计

- 将常用查询条件放在前面
- 区分度高的字段放在前面
- 避免使用低基数字段作为排序键

### 9.4 数据合并

- 定期执行OPTIMIZE TABLE触发合并
- 监控合并过程，避免影响查询性能
- 调整后台合并参数

### 9.5 TTL策略

- 为历史数据设置TTL规则
- 考虑业务需求，避免过早删除数据
- 可以使用TTL将数据移动到冷存储

## 10. 总结

MergeTree系列引擎是ClickHouse的核心优势，通过选择合适的引擎和优化参数，可以构建高性能的分析型数据库系统。关键是要根据具体的业务场景和数据特点，选择最适合的引擎，并合理设计分区键和排序键。

在下一节中，我们将详细介绍ClickHouse的物化视图和投影功能，这些功能与MergeTree系列引擎结合使用，可以进一步提升查询性能和数据转换能力。