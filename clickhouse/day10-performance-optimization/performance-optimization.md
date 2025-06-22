# ClickHouse Day 10: 性能优化

## 学习目标
- 掌握 ClickHouse 查询优化技巧
- 了解硬件调优最佳实践
- 学习容量规划方法
- 实践性能测试和监控

## 1. 查询优化

### 1.1 查询分析工具

#### EXPLAIN 语句
```sql
-- 查看查询执行计划
EXPLAIN SELECT count() FROM events WHERE date >= '2024-01-01';

-- 详细执行计划
EXPLAIN PIPELINE SELECT count() FROM events WHERE date >= '2024-01-01';

-- 查看查询统计信息
EXPLAIN ESTIMATE SELECT count() FROM events WHERE date >= '2024-01-01';
```

#### 查询日志分析
```sql
-- 查看慢查询
SELECT 
    query,
    query_duration_ms,
    read_rows,
    read_bytes,
    memory_usage
FROM system.query_log 
WHERE type = 'QueryFinish' AND query_duration_ms > 1000
ORDER BY query_duration_ms DESC
LIMIT 10;
```

### 1.2 索引优化

#### 主键选择原则
```sql
-- 好的主键设计
CREATE TABLE events_optimized (
    date Date,
    user_id UInt64,
    event_type String,
    timestamp DateTime
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, user_id, event_type);

-- 避免的主键设计
CREATE TABLE events_bad (
    id UUID,  -- 随机主键，不利于排序
    data String
) ENGINE = MergeTree()
ORDER BY id;
```

#### 跳数索引 (Skip Index)
```sql
-- 创建跳数索引
ALTER TABLE events ADD INDEX idx_event_type event_type TYPE set(100) GRANULARITY 4;
ALTER TABLE events ADD INDEX idx_timestamp timestamp TYPE minmax GRANULARITY 1;

-- Bloom Filter 索引
ALTER TABLE events ADD INDEX idx_url_bloom url TYPE bloom_filter() GRANULARITY 1;
```

### 1.3 查询优化技巧

#### 1. 合理使用 PREWHERE
```sql
-- 优化前
SELECT count() FROM events 
WHERE date >= '2024-01-01' AND user_id = 12345;

-- 优化后
SELECT count() FROM events 
PREWHERE date >= '2024-01-01' 
WHERE user_id = 12345;
```

#### 2. 避免 SELECT *
```sql
-- 避免
SELECT * FROM large_table WHERE condition;

-- 推荐
SELECT id, name, created_at FROM large_table WHERE condition;
```

#### 3. 使用合适的聚合函数
```sql
-- 对于近似计算，使用近似函数
SELECT uniq(user_id) FROM events;  -- 精确但慢
SELECT uniqHLL12(user_id) FROM events;  -- 近似但快

-- 对于分位数计算
SELECT quantile(0.95)(response_time) FROM requests;  -- 精确
SELECT quantileTDigest(0.95)(response_time) FROM requests;  -- 近似
```

#### 4. 分区裁剪
```sql
-- 确保查询条件包含分区键
SELECT count() FROM events 
WHERE date BETWEEN '2024-01-01' AND '2024-01-31'  -- 使用分区键
AND event_type = 'click';
```

## 2. 硬件调优

### 2.1 CPU 优化

#### CPU 核心数配置
```xml
<!-- config.xml -->
<max_threads>16</max_threads>  <!-- 通常设置为CPU核心数 -->
<max_concurrent_queries>100</max_concurrent_queries>
<background_pool_size>16</background_pool_size>
<background_move_pool_size>8</background_move_pool_size>
<background_schedule_pool_size>16</background_schedule_pool_size>
```

#### NUMA 优化
```bash
# 检查 NUMA 拓扑
numactl --hardware

# 绑定 ClickHouse 到特定 NUMA 节点
numactl --cpunodebind=0 --membind=0 clickhouse-server
```

### 2.2 内存优化

#### 内存配置
```xml
<max_memory_usage>10000000000</max_memory_usage>  <!-- 10GB -->
<max_memory_usage_for_user>5000000000</max_memory_usage_for_user>  <!-- 5GB -->
<max_memory_usage_for_all_queries>20000000000</max_memory_usage_for_all_queries>  <!-- 20GB -->

<!-- 内存映射文件配置 -->
<mmap_cache_size>1000000000</mmap_cache_size>  <!-- 1GB -->
<mark_cache_size>5368709120</mark_cache_size>  <!-- 5GB -->
<uncompressed_cache_size>8589934592</uncompressed_cache_size>  <!-- 8GB -->
```

#### 内存使用监控
```sql
-- 查看内存使用情况
SELECT 
    query,
    memory_usage,
    peak_memory_usage,
    read_rows,
    read_bytes
FROM system.processes
WHERE memory_usage > 1000000000;  -- 大于1GB的查询

-- 查看系统内存使用
SELECT 
    event,
    value
FROM system.events
WHERE event LIKE '%Memory%';
```

### 2.3 存储优化

#### SSD vs HDD 配置
```xml
<!-- 多磁盘配置 -->
<storage_configuration>
    <disks>
        <ssd>
            <path>/var/lib/clickhouse/ssd/</path>
        </ssd>
        <hdd>
            <path>/var/lib/clickhouse/hdd/</path>
        </hdd>
    </disks>
    <policies>
        <hot_cold>
            <volumes>
                <hot>
                    <disk>ssd</disk>
                    <max_data_part_size_bytes>1073741824</max_data_part_size_bytes>
                </hot>
                <cold>
                    <disk>hdd</disk>
                </cold>
            </volumes>
            <move_factor>0.2</move_factor>
        </hot_cold>
    </policies>
</storage_configuration>
```

#### 文件系统优化
```bash
# XFS 文件系统挂载选项
mount -t xfs -o noatime,nodiratime,logbsize=256k /dev/sdb1 /var/lib/clickhouse

# ext4 文件系统挂载选项
mount -t ext4 -o noatime,nodiratime,nobarrier /dev/sdb1 /var/lib/clickhouse
```

### 2.4 网络优化

#### TCP 配置
```bash
# 增加 TCP 缓冲区大小
echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 65536 134217728' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 65536 134217728' >> /etc/sysctl.conf

# 应用设置
sysctl -p
```

## 3. 容量规划

### 3.1 数据增长预测

#### 历史数据分析
```sql
-- 分析每日数据增长
SELECT 
    toDate(event_time) as date,
    count() as events_count,
    sum(length(toString(tuple(*)))) as size_bytes
FROM events
WHERE event_time >= today() - 30
GROUP BY date
ORDER BY date;

-- 分析表大小趋势
SELECT 
    table,
    sum(bytes_on_disk) as total_bytes,
    sum(rows) as total_rows,
    avg(bytes_on_disk / rows) as avg_row_size
FROM system.parts
WHERE active = 1
GROUP BY table
ORDER BY total_bytes DESC;
```

#### 容量预测模型
```sql
-- 基于线性增长的预测
WITH growth_data AS (
    SELECT 
        toDate(event_time) as date,
        count() as daily_count
    FROM events
    WHERE event_time >= today() - 90
    GROUP BY date
)
SELECT 
    avg(daily_count) as avg_daily_growth,
    avg(daily_count) * 365 as yearly_projection,
    avg(daily_count) * 365 * avg_row_size as yearly_size_bytes
FROM growth_data
CROSS JOIN (
    SELECT avg(bytes_on_disk / rows) as avg_row_size
    FROM system.parts
    WHERE table = 'events' AND active = 1
) row_info;
```

### 3.2 硬件容量规划

#### 存储容量计算
```sql
-- 当前存储使用情况
SELECT 
    formatReadableSize(sum(bytes_on_disk)) as used_space,
    formatReadableSize(sum(bytes_on_disk) * 1.5) as recommended_total_space
FROM system.parts
WHERE active = 1;

-- 按表统计存储需求
SELECT 
    table,
    formatReadableSize(sum(bytes_on_disk)) as current_size,
    formatReadableSize(sum(bytes_on_disk) * 2) as future_size_1year
FROM system.parts
WHERE active = 1
GROUP BY table
ORDER BY sum(bytes_on_disk) DESC;
```

#### 内存需求计算
```sql
-- 查询内存使用统计
SELECT 
    quantile(0.95)(memory_usage) as p95_memory,
    quantile(0.99)(memory_usage) as p99_memory,
    max(memory_usage) as max_memory
FROM system.query_log
WHERE type = 'QueryFinish' 
AND event_time >= today() - 7;

-- 并发查询内存需求
SELECT 
    max(concurrent_queries) * p95_memory_per_query as recommended_memory
FROM (
    SELECT count() as concurrent_queries
    FROM system.query_log
    WHERE type = 'QueryStart'
    GROUP BY toStartOfMinute(event_time)
) concurrent
CROSS JOIN (
    SELECT quantile(0.95)(memory_usage) as p95_memory_per_query
    FROM system.query_log
    WHERE type = 'QueryFinish'
) memory_stats;
```

### 3.3 性能基准测试

#### 写入性能测试
```sql
-- 测试批量插入性能
INSERT INTO test_table 
SELECT 
    number,
    toString(number),
    now()
FROM numbers(10000000);

-- 监控插入速度
SELECT 
    query,
    query_duration_ms,
    read_rows,
    written_rows,
    written_rows / (query_duration_ms / 1000) as rows_per_second
FROM system.query_log
WHERE query LIKE 'INSERT INTO test_table%'
ORDER BY event_time DESC
LIMIT 1;
```

#### 查询性能测试
```sql
-- 创建性能测试表
CREATE TABLE perf_test (
    id UInt64,
    category String,
    value Float64,
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY (category, timestamp);

-- 插入测试数据
INSERT INTO perf_test 
SELECT 
    number,
    ['A', 'B', 'C', 'D'][number % 4 + 1],
    rand() / 1000000,
    now() - number
FROM numbers(100000000);

-- 测试查询性能
SELECT category, avg(value) 
FROM perf_test 
WHERE timestamp >= now() - 3600 
GROUP BY category;
```

## 4. 性能监控和调优实践

### 4.1 关键性能指标

#### 系统级指标
```sql
-- CPU 使用率
SELECT 
    ProfileEvent_OSCPUVirtualTimeMicroseconds / 1000000 as cpu_seconds,
    ProfileEvent_RealTimeMicroseconds / 1000000 as real_seconds,
    ProfileEvent_OSCPUVirtualTimeMicroseconds / ProfileEvent_RealTimeMicroseconds as cpu_usage_ratio
FROM system.query_log
WHERE type = 'QueryFinish' AND event_time >= now() - 3600;

-- I/O 性能
SELECT 
    sum(ProfileEvent_ReadBufferFromFileDescriptorReadBytes) as bytes_read,
    sum(ProfileEvent_WriteBufferFromFileDescriptorWriteBytes) as bytes_written,
    avg(query_duration_ms) as avg_duration_ms
FROM system.query_log
WHERE type = 'QueryFinish' AND event_time >= now() - 3600;
```

#### 查询级指标
```sql
-- 慢查询分析
SELECT 
    left(query, 100) as query_snippet,
    count() as query_count,
    avg(query_duration_ms) as avg_duration,
    max(query_duration_ms) as max_duration,
    avg(memory_usage) as avg_memory,
    max(memory_usage) as max_memory
FROM system.query_log
WHERE type = 'QueryFinish' 
AND event_time >= now() - 24 * 3600
GROUP BY left(query, 100)
HAVING avg_duration > 1000
ORDER BY avg_duration DESC;
```

### 4.2 性能调优检查清单

#### 表结构优化
- [ ] 主键设计是否合理
- [ ] 分区策略是否有效
- [ ] 是否使用了合适的压缩算法
- [ ] 索引是否必要且有效

#### 查询优化
- [ ] 是否使用了 PREWHERE
- [ ] 是否避免了 SELECT *
- [ ] JOIN 顺序是否合理
- [ ] 是否使用了合适的聚合函数

#### 系统配置
- [ ] 内存配置是否合理
- [ ] CPU 核心数配置
- [ ] 磁盘 I/O 设置
- [ ] 网络配置优化

#### 监控告警
- [ ] 慢查询监控
- [ ] 资源使用监控
- [ ] 错误率监控
- [ ] 容量监控

## 5. 实践练习

### 练习1：查询优化
1. 创建一个大表并插入测试数据
2. 编写低效查询并分析执行计划
3. 应用优化技巧并对比性能

### 练习2：硬件调优
1. 监控当前系统资源使用情况
2. 根据监控结果调整配置参数
3. 进行性能测试验证效果

### 练习3：容量规划
1. 分析历史数据增长趋势
2. 预测未来6个月的存储需求
3. 制定硬件扩容计划

## 6. 总结

性能优化是一个持续的过程，需要：
1. **定期监控**：建立完善的监控体系
2. **持续优化**：根据监控结果不断调优
3. **容量规划**：提前规划硬件资源
4. **基准测试**：建立性能基准并定期验证

## 7. 下一步学习

- Day 11: 高可用架构设计
- 深入学习 ClickHouse 内部机制
- 学习更多性能优化工具和技巧 