# Day 15: ClickHouse 数据迁移实战

## 概述

本章节专门讲解ClickHouse集群数据迁移的实际场景，特别是从多分片集群到单分片集群的迁移过程。我们将演示如何将2 replicas, 3 shards的集群数据迁移到2 replicas, 1 shard的集群，并进行完整的数据校验。

## 目录

1. [迁移场景分析](#迁移场景分析)
2. [迁移策略设计](#迁移策略设计)
3. [迁移前准备](#迁移前准备)
4. [迁移执行步骤](#迁移执行步骤)
5. [数据校验](#数据校验)
6. [故障处理与回滚](#故障处理与回滚)
7. [迁移监控](#迁移监控)
8. [最佳实践](#最佳实践)

## 迁移场景分析

### 当前架构
- **源集群**: 2 replicas × 3 shards = 6个节点
- **目标集群**: 2 replicas × 1 shard = 2个节点
- **IP重用**: 使用原有IP地址，减少配置变更

### 迁移挑战
1. **数据重分布**: 3个分片的数据需要合并到1个分片
2. **数据完整性**: 确保迁移过程中不丢失数据
3. **服务连续性**: 最小化停机时间
4. **配置管理**: 集群配置的调整
5. **性能影响**: 单分片的性能考虑

## 迁移策略设计

### 策略选择

#### 1. 停机迁移（推荐）
- **优点**: 数据一致性保证，操作简单
- **缺点**: 需要服务停机
- **适用**: 可以接受短时间停机的场景

#### 2. 在线迁移
- **优点**: 服务不中断
- **缺点**: 复杂度高，需要数据同步
- **适用**: 7×24小时服务场景

#### 3. 蓝绿部署
- **优点**: 可快速回滚，风险低
- **缺点**: 需要额外资源
- **适用**: 生产环境推荐

### 迁移时间估算

```sql
-- 估算数据量
SELECT 
    database,
    table,
    formatReadableSize(sum(bytes_on_disk)) as size,
    sum(rows) as rows,
    count(*) as parts
FROM system.parts 
WHERE active = 1
GROUP BY database, table
ORDER BY sum(bytes_on_disk) DESC;

-- 估算迁移时间（基于网络带宽和磁盘IO）
-- 假设: 网络带宽100MB/s, 磁盘IO 200MB/s
-- 迁移时间 ≈ 数据量 / min(网络带宽, 磁盘IO) × 2（安全系数）
```

## 迁移前准备

### 1. 环境检查

#### 源集群健康检查
```sql
-- 检查集群状态
SELECT * FROM system.clusters WHERE cluster = 'cluster_3s_2r';

-- 检查副本状态
SELECT 
    database,
    table,
    is_leader,
    total_replicas,
    active_replicas
FROM system.replicas;

-- 检查分片数据分布
SELECT 
    hostName() as host,
    database,
    table,
    count(*) as parts,
    formatReadableSize(sum(bytes_on_disk)) as size
FROM system.parts 
WHERE active = 1
GROUP BY hostName(), database, table;
```

#### 目标集群准备
```sql
-- 检查目标集群配置
SELECT * FROM system.clusters WHERE cluster = 'cluster_1s_2r';

-- 检查磁盘空间
SELECT 
    name,
    path,
    formatReadableSize(free_space) as free_space,
    formatReadableSize(total_space) as total_space,
    round(free_space/total_space*100, 2) as free_percent
FROM system.disks;
```

### 2. 配置准备

#### 目标集群配置文件
```xml
<!-- cluster_1s_2r.xml -->
<clickhouse>
    <remote_servers>
        <cluster_1s_2r>
            <shard>
                <replica>
                    <host>10.0.1.1</host>
                    <port>9000</port>
                </replica>
                <replica>
                    <host>10.0.1.2</host>
                    <port>9000</port>
                </replica>
            </shard>
        </cluster_1s_2r>
    </remote_servers>
</clickhouse>
```

### 3. 数据备份

```bash
# 创建完整备份
clickhouse-backup create migration_backup_$(date +%Y%m%d_%H%M%S)

# 导出表结构
clickhouse-client --query="SHOW CREATE TABLE db.table FORMAT TabSeparatedRaw" > table_schema.sql
```

## 迁移执行步骤

### Step 1: 停止写入服务

```sql
-- 设置只读模式
SET readonly = 1;

-- 或者通过配置文件设置
-- <readonly>1</readonly>
```

### Step 2: 数据一致性检查

```sql
-- 检查副本同步状态
SELECT 
    database,
    table,
    active_replicas,
    total_replicas,
    is_leader,
    absolute_delay,
    queue_size
FROM system.replicas
WHERE absolute_delay > 0 OR queue_size > 0;

-- 等待副本同步完成
-- OPTIMIZE TABLE ... FINAL 强制合并
```

### Step 3: 数据导出

#### 方法1: 使用 clickhouse-copier（推荐）

```xml
<!-- copier_config.xml -->
<clickhouse>
    <remote_servers>
        <source_cluster>
            <!-- 源集群配置 -->
        </source_cluster>
        <destination_cluster>
            <!-- 目标集群配置 -->
        </destination_cluster>
    </remote_servers>
    
    <max_workers>4</max_workers>
    <settings_pull>
        <max_execution_time>3600</max_execution_time>
    </settings_pull>
    <settings_push>
        <max_execution_time>3600</max_execution_time>
    </settings_push>
    
    <tables>
        <table_hits>
            <cluster_pull>source_cluster</cluster_pull>
            <database_pull>default</database_pull>
            <table_pull>hits</table_pull>
            
            <cluster_push>destination_cluster</cluster_push>
            <database_push>default</database_push>
            <table_push>hits</table_push>
            
            <engine>
                ENGINE = ReplicatedMergeTree('/clickhouse/tables/{layer}-{shard}/hits', '{replica}')
                PARTITION BY toYYYYMM(EventDate)
                ORDER BY (CounterID, EventDate, intHash32(UserID))
                SAMPLE BY intHash32(UserID)
            </engine>
            
            <sharding_key>rand()</sharding_key>
        </table_hits>
    </tables>
</clickhouse>
```

#### 方法2: 使用 INSERT INTO ... SELECT

```sql
-- 在目标集群创建表
CREATE TABLE target_db.table ON CLUSTER cluster_1s_2r AS source_db.table;

-- 数据迁移（对每个表执行）
INSERT INTO target_db.table 
SELECT * FROM remote('cluster_3s_2r', source_db.table);
```

#### 方法3: 使用备份恢复

```bash
# 在源集群创建备份
clickhouse-backup create migration_full_backup

# 将备份文件传输到目标集群
rsync -av /var/lib/clickhouse/backup/migration_full_backup/ target_host:/var/lib/clickhouse/backup/

# 在目标集群恢复
clickhouse-backup restore migration_full_backup
```

### Step 4: 配置更新

```bash
# 更新集群配置
cp cluster_1s_2r.xml /etc/clickhouse-server/config.d/

# 重启服务
systemctl restart clickhouse-server
```

### Step 5: 服务验证

```sql
-- 检查集群状态
SELECT * FROM system.clusters WHERE cluster = 'cluster_1s_2r';

-- 检查表状态
SELECT 
    database,
    table,
    engine,
    total_rows,
    total_bytes
FROM system.tables
WHERE database NOT IN ('system', 'information_schema');
```

## 数据校验

### 1. 行数校验

```sql
-- 创建校验脚本
WITH source_counts AS (
    SELECT 
        database,
        table,
        sum(rows) as source_rows
    FROM remote('old_cluster_3s_2r', system.parts)
    WHERE active = 1
    GROUP BY database, table
),
target_counts AS (
    SELECT 
        database,
        table,
        sum(rows) as target_rows
    FROM system.parts
    WHERE active = 1
    GROUP BY database, table
)
SELECT 
    s.database,
    s.table,
    s.source_rows,
    t.target_rows,
    s.source_rows - t.target_rows as diff,
    CASE 
        WHEN s.source_rows = t.target_rows THEN 'PASS'
        ELSE 'FAIL'
    END as status
FROM source_counts s
FULL OUTER JOIN target_counts t ON s.database = t.database AND s.table = t.table
ORDER BY abs(s.source_rows - t.target_rows) DESC;
```

### 2. 数据完整性校验

```sql
-- MD5校验（适用于小表）
WITH source_hash AS (
    SELECT MD5(toString(groupArray((*)))) as hash
    FROM remote('old_cluster_3s_2r', database.table)
),
target_hash AS (
    SELECT MD5(toString(groupArray((*)))) as hash
    FROM database.table
)
SELECT 
    s.hash as source_hash,
    t.hash as target_hash,
    s.hash = t.hash as is_match
FROM source_hash s, target_hash t;
```

### 3. 抽样校验

```sql
-- 随机抽样校验
WITH sample_data AS (
    SELECT * FROM database.table 
    SAMPLE 0.01  -- 1%抽样
    ORDER BY rand()
    LIMIT 1000
)
SELECT 
    count(*) as sample_count,
    count(DISTINCT primary_key) as unique_count,
    min(date_column) as min_date,
    max(date_column) as max_date
FROM sample_data;
```

### 4. 业务逻辑校验

```sql
-- 业务指标校验
SELECT 
    toYYYYMM(date_column) as month,
    count(*) as total_events,
    countDistinct(user_id) as unique_users,
    sum(amount) as total_amount
FROM database.table
WHERE date_column >= '2024-01-01'
GROUP BY toYYYYMM(date_column)
ORDER BY month;
```

## 故障处理与回滚

### 1. 常见问题处理

#### 磁盘空间不足
```bash
# 清理临时文件
rm -rf /var/lib/clickhouse/tmp/*

# 删除旧的备份
clickhouse-backup list | head -n -5 | xargs -I {} clickhouse-backup delete {}

# 压缩数据
OPTIMIZE TABLE database.table FINAL;
```

#### 副本同步失败
```sql
-- 检查副本状态
SELECT * FROM system.replicas WHERE is_readonly = 1;

-- 强制同步
SYSTEM RESTART REPLICA database.table;

-- 重新创建副本
DROP TABLE database.table;
CREATE TABLE database.table AS other_replica.database.table;
```

#### 性能问题
```sql
-- 监控查询性能
SELECT 
    query_id,
    user,
    query,
    query_duration_ms,
    read_rows,
    read_bytes
FROM system.query_log
WHERE event_date = today()
  AND query_duration_ms > 10000
ORDER BY query_duration_ms DESC;
```

### 2. 回滚策略

#### 快速回滚
```bash
# 恢复原始配置
cp cluster_3s_2r.xml.backup /etc/clickhouse-server/config.d/cluster.xml

# 重启服务
systemctl restart clickhouse-server

# 验证集群状态
clickhouse-client --query="SELECT * FROM system.clusters"
```

#### 数据回滚
```bash
# 从备份恢复
clickhouse-backup restore migration_backup_20240301_120000

# 验证数据
clickhouse-client --query="SELECT count(*) FROM database.table"
```

## 迁移监控

### 1. 系统监控

```bash
#!/bin/bash
# migration_monitor.sh

while true; do
    echo "=== $(date) ==="
    
    # CPU使用率
    echo "CPU Usage:"
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
    
    # 内存使用
    echo "Memory Usage:"
    free -h
    
    # 磁盘IO
    echo "Disk IO:"
    iostat -x 1 1 | tail -n +4
    
    # 网络流量
    echo "Network Traffic:"
    iftop -t -s 10
    
    # ClickHouse连接数
    echo "ClickHouse Connections:"
    clickhouse-client --query="SELECT count(*) FROM system.processes"
    
    sleep 60
done
```

### 2. 迁移进度监控

```sql
-- 监控迁移进度
SELECT 
    table,
    formatReadableSize(bytes_on_disk) as current_size,
    formatReadableSize(progress_bytes) as transferred,
    round(progress_bytes / bytes_on_disk * 100, 2) as progress_percent
FROM (
    SELECT 
        table,
        sum(bytes_on_disk) as bytes_on_disk,
        sum(progress_bytes) as progress_bytes
    FROM system.parts
    WHERE active = 1
    GROUP BY table
);
```

## 最佳实践

### 1. 迁移前检查清单

- [ ] 源集群健康状态检查
- [ ] 目标集群资源评估
- [ ] 完整数据备份
- [ ] 迁移脚本测试
- [ ] 回滚方案准备
- [ ] 监控工具部署
- [ ] 业务方通知

### 2. 迁移执行清单

- [ ] 停止写入服务
- [ ] 数据一致性确认
- [ ] 执行数据迁移
- [ ] 配置文件更新
- [ ] 服务重启验证
- [ ] 数据校验执行
- [ ] 性能测试
- [ ] 业务功能测试

### 3. 迁移后检查清单

- [ ] 所有表数据完整性
- [ ] 业务指标一致性
- [ ] 查询性能对比
- [ ] 监控告警配置
- [ ] 文档更新
- [ ] 团队培训

### 4. 性能优化建议

#### 单分片性能调优
```sql
-- 调整max_threads
SET max_threads = 16;

-- 优化内存使用
SET max_memory_usage = 10000000000;  -- 10GB

-- 并行处理
SET max_execution_time = 3600;
SET send_timeout = 600;
SET receive_timeout = 600;
```

#### 硬件建议
- **CPU**: 单分片建议32核心以上
- **内存**: 128GB以上，建议256GB
- **存储**: NVMe SSD，建议RAID10
- **网络**: 万兆网卡

### 5. 监控和告警

```sql
-- 创建监控视图
CREATE VIEW migration_monitor AS
SELECT 
    hostName() as host,
    database,
    table,
    formatReadableSize(sum(bytes_on_disk)) as size,
    sum(rows) as rows,
    count(*) as parts,
    min(min_date) as min_date,
    max(max_date) as max_date
FROM system.parts
WHERE active = 1
GROUP BY hostName(), database, table;
```

## 总结

本章节详细介绍了ClickHouse集群数据迁移的完整流程，特别是从多分片到单分片的迁移场景。关键要点：

1. **充分准备**: 详细的迁移计划和充分的测试
2. **数据安全**: 完整备份和多层次校验
3. **最小影响**: 合理的迁移策略减少业务影响
4. **持续监控**: 实时监控迁移进度和系统状态
5. **快速恢复**: 完善的回滚和故障处理机制

通过本章的学习，您应该能够安全、高效地完成ClickHouse集群的数据迁移任务。 