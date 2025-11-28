# PostgreSQL第10章：备份恢复与监控
## PostgreSQL Backup, Recovery and Monitoring

### 章节概述

PostgreSQL提供了一套完整的备份、恢复和监控解决方案，确保数据安全性和系统可观测性。本章将学习PostgreSQL的备份策略、恢复技术、监控指标和日常运维管理。

### 学习目标

- 掌握PostgreSQL各种备份方法（逻辑备份、物理备份）
- 理解PITR（时间点恢复）概念和配置
- 学会使用监控工具和性能指标
- 了解高可用配置和故障恢复
- 掌握日常运维任务和最佳实践

### 文件说明

1. **backup_strategies.sql** - PostgreSQL备份策略和实现示例
   - pg_dump和pg_dumpall使用
   - 物理备份和WAL归档
   - 压缩备份和并行备份
   - 备份恢复最佳实践

2. **recovery_pitr.sql** - 数据恢复和时间点恢复(PITR)示例
   - 基础恢复操作
   - PITR配置和管理
   - 恢复验证和测试
   - 灾难恢复演练

3. **monitoring_diagnostics.sql** - 系统监控和性能诊断函数
   - 系统性能监控
   - 慢查询分析
   - 锁监控和死锁处理
   - 连接和会话监控

4. **monitoring_diagnostics.py** - Python监控和诊断脚本
   - 数据库状态监控
   - 性能指标收集
   - 告警通知机制
   - 实时监控循环

5. **requirements.txt** - Python监控脚本依赖包
   - psycopg2-binary - PostgreSQL数据库连接
   - pandas - 数据分析和处理
   - numpy - 数值计算
   - matplotlib - 性能图表生成
   - seaborn - 统计可视化
   - psutil - 系统资源监控
   - plotly - 交互式图表
   - structlog - 结构化日志

### 环境准备

#### PostgreSQL配置
```sql
-- 确保wal_level配置为replica或logical
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET max_wal_senders = 10;
ALTER SYSTEM SET wal_keep_segments = 32;
ALTER SYSTEM SET archive_mode = on;
ALTER SYSTEM SET archive_command = 'cp %p /var/lib/postgresql/archive/%f';
SELECT pg_reload_conf();
```

#### 目录准备
```bash
# 创建备份目录
mkdir -p /var/lib/postgresql/backup/{daily,weekly,monthly,archive}
chown postgres:postgres /var/lib/postgresql/backup

# 创建日志目录
mkdir -p /var/log/postgresql/backup
mkdir -p /var/log/postgresql/monitoring
chown postgres:postgres /var/log/postgresql/*
```

### 运行指南

#### 1. 备份策略测试
```sql
-- 登录PostgreSQL
psql -U postgres -d your_database

-- 执行备份相关SQL文件
\i backup_strategies.sql
\i recovery_pitr.sql
```

#### 2. 监控脚本运行
```bash
# 安装Python依赖
pip install -r requirements.txt

# 运行监控脚本
python backup_monitoring.py

# 或单独运行监控组件
python -c "from backup_monitoring import BackupMonitor; BackupMonitor().check_backup_status()"
```

#### 3. 日常运维
```sql
-- 执行维护任务
\i maintenance_tasks.sql
\i monitoring_diagnostics.sql
```

### 关键命令示例

#### 备份命令
```bash
# 逻辑备份
pg_dump -U postgres -h localhost -p 5432 -Fc -Z 9 -f backup_$(date +%Y%m%d_%H%M%S).dump your_database

# 物理备份
pg_basebackup -U postgres -h localhost -p 5432 -D /backup/base -Ft -z -P -v

# WAL归档
psql -U postgres -c "SELECT pg_switch_wal();"
```

#### 监控命令
```sql
-- 查看数据库状态
SELECT 
    datname as database_name,
    pg_size_pretty(pg_database_size(datname)) as size,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit
FROM pg_stat_database;

-- 查看活跃连接
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    query
FROM pg_stat_activity
WHERE state = 'active';

-- 查看慢查询
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

#### 高可用测试
```bash
# 检查主从复制状态
psql -U postgres -h master -c "SELECT * FROM pg_stat_replication;"
psql -U postgres -h slave -c "SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();"
```

### 注意事项

1. **备份安全**
   - 确保备份文件的安全性，使用加密存储
   - 定期验证备份文件的完整性
   - 测试恢复流程，确保备份可用

2. **监控频率**
   - 系统监控：每5-10分钟
   - 性能监控：每小时
   - 备份监控：每次备份后
   - 安全审计：每周

3. **资源管理**
   - 合理配置监控间隔，避免对性能造成影响
   - 保留历史数据的时间窗口要适当
   - 监控数据存储要有合理的清理策略

4. **高可用配置**
   - 在测试环境中验证故障转移机制
   - 定期进行灾备演练
   - 监控复制延迟，及时处理异常

### 扩展学习资源

- [PostgreSQL官方备份文档](https://www.postgresql.org/docs/current/backup.html)
- [PostgreSQL监控指南](https://wiki.postgresql.org/wiki/Monitoring)
- [高可用配置手册](https://wiki.postgresql.org/wiki/Replication,_Clustering,_and_Connection_Pooling)
- [性能调优指南](https://wiki.postgresql.org/wiki/Performance_Optimization)

### 故障排查

#### 常见问题
1. **备份失败** - 检查磁盘空间和权限
2. **监控数据缺失** - 检查网络连接和权限
3. **复制延迟** - 检查网络性能和主库负载
4. **WAL归档失败** - 检查归档目录权限和磁盘空间

#### 应急处理
1. 立即启动备份恢复流程
2. 检查系统资源使用情况
3. 分析错误日志找出问题根源
4. 联系技术支持（如需要）
