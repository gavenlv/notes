# ClickHouse Day 12: 备份恢复

## 学习目标
- 掌握 ClickHouse 数据备份策略和方法
- 理解灾难恢复的原理和实践
- 学习版本升级的安全流程
- 实践备份恢复的自动化管理

## 1. 数据备份

### 1.1 备份策略概述

#### 备份类型
1. **全量备份**: 完整的数据库备份
2. **增量备份**: 只备份变更的数据
3. **差异备份**: 自上次全量备份以来的所有变更
4. **逻辑备份**: 导出SQL语句和数据
5. **物理备份**: 直接复制数据文件

#### 备份频率规划
```
- 全量备份: 每周一次
- 增量备份: 每天一次
- 差异备份: 每小时一次（重要系统）
- 实时备份: 使用复制机制
```

### 1.2 内置备份功能

#### 使用 BACKUP 命令（ClickHouse 22.8+）
```sql
-- 备份整个数据库
BACKUP DATABASE my_database TO Disk('backup_disk', 'database_backup_20240101.zip');

-- 备份特定表
BACKUP TABLE my_database.my_table TO Disk('backup_disk', 'table_backup.zip');

-- 备份多个表
BACKUP TABLE db1.table1, db2.table2 TO Disk('backup_disk', 'multi_table_backup.zip');

-- 增量备份
BACKUP DATABASE my_database TO Disk('backup_disk', 'incremental_backup.zip') 
SETTINGS base_backup = Disk('backup_disk', 'base_backup.zip');

-- 异步备份
BACKUP DATABASE my_database TO Disk('backup_disk', 'async_backup.zip') ASYNC;

-- 查看备份进度
SELECT * FROM system.backups;
```

#### 备份配置
```xml
<!-- config.xml 中的备份配置 -->
<backup_engines>
    <disk>
        <type>local</type>
        <path>/var/lib/clickhouse/backups/</path>
    </disk>
    <s3>
        <type>s3</type>
        <endpoint>https://s3.amazonaws.com/my-backup-bucket/</endpoint>
        <access_key_id>your_access_key</access_key_id>
        <secret_access_key>your_secret_key</secret_access_key>
    </s3>
</backup_engines>
```

### 1.3 物理备份方法

#### 1. 冷备份（停机备份）
```bash
# 停止ClickHouse服务
sudo systemctl stop clickhouse-server

# 备份数据目录
sudo tar -czf /backup/clickhouse_full_backup_$(date +%Y%m%d).tar.gz \
    /var/lib/clickhouse/

# 启动ClickHouse服务
sudo systemctl start clickhouse-server
```

#### 2. 热备份（在线备份）
```bash
# 使用rsync进行热备份
rsync -av --exclude='tmp/' \
    /var/lib/clickhouse/ \
    /backup/clickhouse_hot_backup_$(date +%Y%m%d)/

# 使用硬链接备份（节省空间）
cp -al /var/lib/clickhouse/ \
    /backup/clickhouse_hardlink_backup_$(date +%Y%m%d)/
```

#### 3. 快照备份（LVM/ZFS）
```bash
# LVM快照备份
sudo lvcreate -L10G -s -n clickhouse_snapshot /dev/vg0/clickhouse_data
sudo mount /dev/vg0/clickhouse_snapshot /mnt/snapshot
sudo tar -czf /backup/snapshot_backup_$(date +%Y%m%d).tar.gz -C /mnt/snapshot .
sudo umount /mnt/snapshot
sudo lvremove -f /dev/vg0/clickhouse_snapshot

# ZFS快照备份
sudo zfs snapshot tank/clickhouse@backup_$(date +%Y%m%d)
sudo zfs send tank/clickhouse@backup_$(date +%Y%m%d) | \
    gzip > /backup/zfs_backup_$(date +%Y%m%d).gz
```

### 1.4 逻辑备份方法

#### 1. 使用 clickhouse-client 导出
```bash
# 导出整个数据库
clickhouse-client --query="SHOW TABLES FROM my_database" | \
while read table; do
    clickhouse-client --query="SELECT * FROM my_database.$table FORMAT Native" > \
        /backup/my_database_${table}_$(date +%Y%m%d).native
done

# 导出表结构
clickhouse-client --query="SHOW CREATE TABLE my_database.my_table" > \
    /backup/my_table_schema.sql

# 导出数据（CSV格式）
clickhouse-client --query="SELECT * FROM my_database.my_table FORMAT CSV" > \
    /backup/my_table_data.csv

# 导出数据（压缩格式）
clickhouse-client --query="SELECT * FROM my_database.my_table FORMAT Native" | \
    gzip > /backup/my_table_data.native.gz
```

#### 2. 使用 clickhouse-backup 工具
```bash
# 安装 clickhouse-backup
wget https://github.com/AlexAkulov/clickhouse-backup/releases/download/v2.4.25/clickhouse-backup-linux-amd64.tar.gz
tar -xzf clickhouse-backup-linux-amd64.tar.gz
sudo mv clickhouse-backup /usr/local/bin/

# 配置文件
cat > /etc/clickhouse-backup/config.yml << EOF
general:
  remote_storage: s3
  disable_progress_bar: false
  backups_to_keep_local: 3
  backups_to_keep_remote: 10

clickhouse:
  username: default
  password: ""
  host: localhost
  port: 9000
  
s3:
  access_key: your_access_key
  secret_key: your_secret_key
  bucket: your-backup-bucket
  region: us-east-1
  path: clickhouse-backups
EOF

# 创建备份
clickhouse-backup create my_backup_$(date +%Y%m%d)

# 上传到远程存储
clickhouse-backup upload my_backup_$(date +%Y%m%d)

# 列出备份
clickhouse-backup list local
clickhouse-backup list remote

# 删除旧备份
clickhouse-backup delete local old_backup_name
```

### 1.5 复制备份

#### 使用复制表进行实时备份
```sql
-- 创建复制表作为备份
CREATE TABLE backup_table
(
    id UInt64,
    data String,
    timestamp DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/backup_table', 'replica1')
ORDER BY id;

-- 从主表复制数据
INSERT INTO backup_table SELECT * FROM main_table;

-- 设置自动同步
CREATE MATERIALIZED VIEW backup_sync TO backup_table AS
SELECT * FROM main_table;
```

## 2. 数据恢复

### 2.1 使用 RESTORE 命令
```sql
-- 恢复整个数据库
RESTORE DATABASE my_database FROM Disk('backup_disk', 'database_backup.zip');

-- 恢复特定表
RESTORE TABLE my_database.my_table FROM Disk('backup_disk', 'table_backup.zip');

-- 恢复到不同的表名
RESTORE TABLE my_database.my_table AS my_database.restored_table 
FROM Disk('backup_disk', 'table_backup.zip');

-- 增量恢复
RESTORE DATABASE my_database FROM Disk('backup_disk', 'incremental_backup.zip');

-- 异步恢复
RESTORE DATABASE my_database FROM Disk('backup_disk', 'backup.zip') ASYNC;

-- 查看恢复进度
SELECT * FROM system.restores;
```

### 2.2 物理恢复

#### 1. 完全恢复
```bash
# 停止ClickHouse服务
sudo systemctl stop clickhouse-server

# 清理现有数据（谨慎操作）
sudo rm -rf /var/lib/clickhouse/data/*
sudo rm -rf /var/lib/clickhouse/metadata/*

# 恢复备份数据
sudo tar -xzf /backup/clickhouse_full_backup_20240101.tar.gz -C /

# 修复权限
sudo chown -R clickhouse:clickhouse /var/lib/clickhouse/

# 启动服务
sudo systemctl start clickhouse-server
```

#### 2. 选择性恢复
```bash
# 只恢复特定数据库
sudo tar -xzf /backup/clickhouse_backup.tar.gz \
    var/lib/clickhouse/data/my_database/ \
    var/lib/clickhouse/metadata/my_database.sql \
    -C /

# 恢复特定表
sudo tar -xzf /backup/clickhouse_backup.tar.gz \
    var/lib/clickhouse/data/my_database/my_table/ \
    var/lib/clickhouse/metadata/my_database/my_table.sql \
    -C /
```

### 2.3 逻辑恢复

#### 1. 从SQL文件恢复
```bash
# 恢复表结构
clickhouse-client < /backup/my_table_schema.sql

# 恢复数据
clickhouse-client --query="INSERT INTO my_database.my_table FORMAT CSV" < \
    /backup/my_table_data.csv

# 从Native格式恢复
clickhouse-client --query="INSERT INTO my_database.my_table FORMAT Native" < \
    /backup/my_table_data.native
```

#### 2. 使用 clickhouse-backup 恢复
```bash
# 下载远程备份
clickhouse-backup download my_backup_20240101

# 恢复备份
clickhouse-backup restore my_backup_20240101

# 恢复特定表
clickhouse-backup restore --table my_database.my_table my_backup_20240101
```

### 2.4 点时间恢复（PITR）

#### 使用 WAL 和复制日志
```sql
-- 启用WAL（Write-Ahead Log）
ALTER TABLE my_table MODIFY SETTING enable_mixed_granularity_parts = 1;

-- 查看复制日志
SELECT * FROM system.replication_queue;

-- 恢复到特定时间点
RESTORE DATABASE my_database FROM Disk('backup_disk', 'base_backup.zip')
SETTINGS restore_to_time = '2024-01-01 12:00:00';
```

## 3. 灾难恢复

### 3.1 灾难恢复策略

#### RTO 和 RPO 目标
```
RTO (Recovery Time Objective): 恢复时间目标
- 关键系统: < 1小时
- 重要系统: < 4小时
- 一般系统: < 24小时

RPO (Recovery Point Objective): 恢复点目标
- 关键数据: < 15分钟
- 重要数据: < 1小时
- 一般数据: < 24小时
```

#### 灾难恢复等级
1. **冷备份站点**: 需要手动恢复，成本低
2. **温备份站点**: 部分自动化，中等成本
3. **热备份站点**: 实时同步，高成本

### 3.2 多地域备份

#### 跨地域复制配置
```xml
<!-- config.xml -->
<remote_servers>
    <disaster_recovery>
        <shard>
            <replica>
                <host>primary-site.company.com</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>backup-site.company.com</host>
                <port>9000</port>
            </replica>
        </shard>
    </disaster_recovery>
</remote_servers>
```

```sql
-- 创建跨地域复制表
CREATE TABLE disaster_recovery_table
(
    id UInt64,
    data String,
    timestamp DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/dr/disaster_recovery_table', '{replica}')
ORDER BY id;
```

### 3.3 自动故障切换

#### 使用 Keeper 集群
```xml
<!-- keeper_config.xml -->
<keeper_server>
    <tcp_port>9181</tcp_port>
    <server_id>1</server_id>
    
    <log_storage_path>/var/lib/clickhouse/coordination/log</log_storage_path>
    <snapshot_storage_path>/var/lib/clickhouse/coordination/snapshots</snapshot_storage_path>
    
    <coordination_settings>
        <operation_timeout_ms>10000</operation_timeout_ms>
        <session_timeout_ms>30000</session_timeout_ms>
        <raft_logs_level>warning</raft_logs_level>
    </coordination_settings>
    
    <raft_configuration>
        <server>
            <id>1</id>
            <hostname>keeper1.company.com</hostname>
            <port>9234</port>
        </server>
        <server>
            <id>2</id>
            <hostname>keeper2.company.com</hostname>
            <port>9234</port>
        </server>
        <server>
            <id>3</id>
            <hostname>keeper3.company.com</hostname>
            <port>9234</port>
        </server>
    </raft_configuration>
</keeper_server>
```

### 3.4 灾难恢复演练

#### 演练计划
```bash
#!/bin/bash
# 灾难恢复演练脚本

echo "=== 灾难恢复演练开始 ==="

# 1. 模拟主站点故障
echo "1. 模拟主站点故障..."
# 停止主站点服务（测试环境）

# 2. 检查备份站点状态
echo "2. 检查备份站点状态..."
clickhouse-client --host backup-site.company.com --query="SELECT version()"

# 3. 验证数据完整性
echo "3. 验证数据完整性..."
clickhouse-client --host backup-site.company.com \
    --query="SELECT count() FROM system.tables"

# 4. 执行故障切换
echo "4. 执行故障切换..."
# 更新DNS或负载均衡器配置

# 5. 验证应用连接
echo "5. 验证应用连接..."
# 测试应用程序连接

echo "=== 灾难恢复演练完成 ==="
```

## 4. 版本升级

### 4.1 升级前准备

#### 1. 版本兼容性检查
```sql
-- 检查当前版本
SELECT version();

-- 检查系统设置
SELECT * FROM system.settings WHERE changed;

-- 检查表引擎兼容性
SELECT 
    database,
    table,
    engine
FROM system.tables
WHERE engine IN ('Log', 'TinyLog', 'StripeLog'); -- 可能需要迁移的引擎
```

#### 2. 升级前备份
```bash
# 完整备份
clickhouse-backup create pre_upgrade_backup_$(date +%Y%m%d)
clickhouse-backup upload pre_upgrade_backup_$(date +%Y%m%d)

# 配置文件备份
sudo cp -r /etc/clickhouse-server /backup/config_backup_$(date +%Y%m%d)
```

### 4.2 滚动升级

#### 集群滚动升级流程
```bash
#!/bin/bash
# 集群滚动升级脚本

NODES=("node1" "node2" "node3")
NEW_VERSION="23.8.1.94"

for node in "${NODES[@]}"; do
    echo "升级节点: $node"
    
    # 1. 停止节点上的ClickHouse
    ssh $node "sudo systemctl stop clickhouse-server"
    
    # 2. 升级软件包
    ssh $node "sudo apt update && sudo apt install clickhouse-server=$NEW_VERSION"
    
    # 3. 启动服务
    ssh $node "sudo systemctl start clickhouse-server"
    
    # 4. 验证节点状态
    ssh $node "clickhouse-client --query='SELECT version()'"
    
    # 5. 等待复制同步
    sleep 30
    
    # 6. 检查复制状态
    ssh $node "clickhouse-client --query='SELECT * FROM system.replicas WHERE is_leader=0 AND is_readonly=0'"
    
    echo "节点 $node 升级完成"
done
```

### 4.3 蓝绿部署升级

#### 蓝绿部署策略
```bash
#!/bin/bash
# 蓝绿部署升级

# 1. 准备绿色环境
echo "准备绿色环境..."
docker run -d --name clickhouse-green \
    -p 9001:9000 -p 8124:8123 \
    clickhouse/clickhouse-server:23.8

# 2. 数据同步到绿色环境
echo "同步数据到绿色环境..."
clickhouse-backup create blue_snapshot
clickhouse-backup restore --host localhost --port 9001 blue_snapshot

# 3. 验证绿色环境
echo "验证绿色环境..."
clickhouse-client --host localhost --port 9001 --query="SELECT count() FROM system.tables"

# 4. 切换流量到绿色环境
echo "切换流量..."
# 更新负载均衡器配置

# 5. 监控绿色环境
echo "监控新环境..."
sleep 300

# 6. 确认切换成功后清理蓝色环境
echo "清理蓝色环境..."
docker stop clickhouse-blue
docker rm clickhouse-blue
```

### 4.4 版本回滚

#### 快速回滚流程
```bash
#!/bin/bash
# 版本回滚脚本

echo "开始版本回滚..."

# 1. 停止当前版本
sudo systemctl stop clickhouse-server

# 2. 恢复旧版本软件包
sudo apt install clickhouse-server=22.8.1.2 --allow-downgrades

# 3. 恢复配置文件
sudo cp -r /backup/config_backup_20240101/* /etc/clickhouse-server/

# 4. 恢复数据（如果需要）
clickhouse-backup restore pre_upgrade_backup_20240101

# 5. 启动服务
sudo systemctl start clickhouse-server

# 6. 验证回滚
clickhouse-client --query="SELECT version()"

echo "版本回滚完成"
```

## 5. 自动化备份管理

### 5.1 备份自动化脚本

#### 完整的备份脚本
```bash
#!/bin/bash
# ClickHouse 自动化备份脚本

# 配置参数
BACKUP_DIR="/backup/clickhouse"
RETENTION_DAYS=30
LOG_FILE="/var/log/clickhouse-backup.log"
NOTIFICATION_EMAIL="admin@company.com"

# 日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# 错误处理
error_exit() {
    log "ERROR: $1"
    echo "ClickHouse备份失败: $1" | mail -s "备份失败告警" $NOTIFICATION_EMAIL
    exit 1
}

# 创建备份目录
mkdir -p $BACKUP_DIR/$(date +%Y%m%d)

# 执行备份
log "开始ClickHouse备份..."

# 1. 逻辑备份
log "执行逻辑备份..."
clickhouse-backup create logical_backup_$(date +%Y%m%d_%H%M%S) || error_exit "逻辑备份失败"

# 2. 配置文件备份
log "备份配置文件..."
tar -czf $BACKUP_DIR/$(date +%Y%m%d)/config_backup.tar.gz /etc/clickhouse-server/ || error_exit "配置备份失败"

# 3. 上传到远程存储
log "上传到远程存储..."
clickhouse-backup upload logical_backup_$(date +%Y%m%d_%H%M%S) || error_exit "远程上传失败"

# 4. 清理旧备份
log "清理旧备份..."
find $BACKUP_DIR -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;
clickhouse-backup delete local --keep-last $RETENTION_DAYS

# 5. 验证备份
log "验证备份完整性..."
BACKUP_COUNT=$(clickhouse-backup list local | wc -l)
if [ $BACKUP_COUNT -eq 0 ]; then
    error_exit "备份验证失败：没有找到备份文件"
fi

log "ClickHouse备份完成"
echo "ClickHouse备份成功完成" | mail -s "备份成功通知" $NOTIFICATION_EMAIL
```

### 5.2 定时任务配置

#### Crontab 配置
```bash
# 编辑crontab
crontab -e

# 添加定时任务
# 每天凌晨2点执行全量备份
0 2 * * * /opt/scripts/clickhouse-backup.sh full

# 每4小时执行增量备份
0 */4 * * * /opt/scripts/clickhouse-backup.sh incremental

# 每周日执行配置备份
0 1 * * 0 /opt/scripts/clickhouse-backup.sh config

# 每月第一天执行备份清理
0 3 1 * * /opt/scripts/clickhouse-backup.sh cleanup
```

### 5.3 监控和告警

#### 备份监控脚本
```bash
#!/bin/bash
# 备份监控脚本

BACKUP_AGE_THRESHOLD=86400  # 24小时
ALERT_EMAIL="admin@company.com"

# 检查最新备份时间
LATEST_BACKUP=$(clickhouse-backup list local | head -1 | awk '{print $1}')
BACKUP_TIME=$(stat -c %Y /var/lib/clickhouse/backup/$LATEST_BACKUP 2>/dev/null || echo 0)
CURRENT_TIME=$(date +%s)
BACKUP_AGE=$((CURRENT_TIME - BACKUP_TIME))

if [ $BACKUP_AGE -gt $BACKUP_AGE_THRESHOLD ]; then
    echo "警告：ClickHouse备份过期，最后备份时间：$(date -d @$BACKUP_TIME)" | \
        mail -s "ClickHouse备份告警" $ALERT_EMAIL
fi

# 检查备份空间
BACKUP_USAGE=$(df /backup | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $BACKUP_USAGE -gt 80 ]; then
    echo "警告：备份存储空间不足，当前使用率：${BACKUP_USAGE}%" | \
        mail -s "备份存储告警" $ALERT_EMAIL
fi
```

## 6. 最佳实践

### 6.1 备份策略最佳实践

1. **3-2-1 备份原则**
   - 3个副本：原始数据 + 2个备份
   - 2种介质：本地存储 + 远程存储
   - 1个异地：至少一个备份在异地

2. **备份验证**
   - 定期恢复测试
   - 自动化验证脚本
   - 备份完整性检查

3. **备份安全**
   - 备份数据加密
   - 访问权限控制
   - 传输过程加密

### 6.2 恢复策略最佳实践

1. **恢复时间规划**
   - 制定恢复时间目标（RTO）
   - 准备恢复环境
   - 文档化恢复流程

2. **数据一致性**
   - 事务一致性检查
   - 数据完整性验证
   - 关联数据同步

### 6.3 升级策略最佳实践

1. **测试环境验证**
   - 完整的升级测试
   - 性能对比测试
   - 功能兼容性测试

2. **分阶段升级**
   - 先升级从节点
   - 再升级主节点
   - 最后升级应用层

## 7. 实践练习

### 练习1：备份恢复演练
1. 创建测试数据
2. 执行各种类型的备份
3. 模拟数据丢失
4. 执行恢复操作

### 练习2：灾难恢复演练
1. 搭建主备环境
2. 配置数据同步
3. 模拟主站点故障
4. 执行故障切换

### 练习3：版本升级演练
1. 准备升级环境
2. 执行滚动升级
3. 验证升级结果
4. 练习版本回滚

## 8. 故障排除

### 8.1 常见备份问题

#### 问题1：备份失败
```bash
# 检查磁盘空间
df -h /backup

# 检查权限
ls -la /backup

# 查看日志
tail -f /var/log/clickhouse-server/clickhouse-server.log
```

#### 问题2：恢复失败
```bash
# 检查备份文件完整性
tar -tzf backup.tar.gz > /dev/null

# 验证数据格式
clickhouse-client --query="SELECT * FROM backup_table LIMIT 1"
```

### 8.2 常见升级问题

#### 问题1：版本不兼容
```sql
-- 检查不兼容的设置
SELECT * FROM system.settings WHERE name LIKE '%compatibility%';

-- 检查已弃用的功能
SHOW WARNINGS;
```

#### 问题2：升级后性能下降
```sql
-- 检查查询性能
SELECT * FROM system.query_log 
WHERE type = 'QueryFinish' 
AND event_time > now() - INTERVAL 1 HOUR
ORDER BY query_duration_ms DESC;
```

## 9. 总结

ClickHouse 备份恢复的核心要点：

1. **多层次备份策略**：结合物理备份和逻辑备份
2. **自动化管理**：定时备份、监控告警、自动清理
3. **灾难恢复准备**：多地域备份、故障切换机制
4. **安全升级流程**：测试验证、滚动升级、快速回滚

## 10. 下一步学习

- Day 13: 运维监控系统
- 深入学习企业级备份解决方案
- 了解云原生备份恢复方案 