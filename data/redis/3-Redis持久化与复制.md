# 第3章：Redis持久化与复制

## 3.1 Redis持久化概述

### 3.1.1 持久化的必要性

Redis是基于内存的数据库，所有数据都存储在内存中。为了确保数据在服务器重启后不会丢失，Redis提供了两种持久化机制：

- **RDB（Redis Database）**：快照方式，定期将内存数据保存到磁盘
- **AOF（Append Only File）**：日志方式，记录所有写操作命令

### 3.1.2 持久化策略选择

根据应用场景选择合适的持久化策略：

| 场景 | 推荐策略 | 理由 |
|------|----------|------|
| 缓存 | RDB | 数据可以丢失，追求高性能 |
| 会话存储 | AOF | 需要保证会话数据不丢失 |
| 消息队列 | AOF | 保证消息可靠性 |
| 排行榜 | RDB + AOF | 数据重要且需要快速恢复 |

## 3.2 RDB持久化

### 3.2.1 RDB工作原理

RDB通过创建数据快照来实现持久化。当满足特定条件时，Redis会fork一个子进程，子进程将内存数据写入临时RDB文件，完成后替换旧文件。

```python
# RDB配置示例
# redis.conf

# 保存条件：900秒内至少有1个key被修改
save 900 1
# 保存条件：300秒内至少有10个key被修改
save 300 10
# 保存条件：60秒内至少有10000个key被修改
save 60 10000

# RDB文件名
dbfilename dump.rdb

# 工作目录
dir /var/lib/redis

# 是否压缩RDB文件
rdbcompression yes

# 是否校验RDB文件
rdbchecksum yes
```

### 3.2.2 RDB手动操作

```python
import redis

r = redis.Redis(decode_responses=True)

# 手动保存RDB（同步，会阻塞其他操作）
r.save()

# 后台保存RDB（异步，不阻塞）
r.bgsave()

# 检查最后一次保存状态
last_save = r.lastsave()
print(f"最后一次保存时间: {last_save}")

# 获取RDB相关信息
info = r.info('persistence')
print(f"RDB相关信息: {info}")
```

### 3.2.3 RDB优缺点分析

**优点**：
- 文件紧凑，适合备份和灾难恢复
- 恢复大数据集时速度比AOF快
- 对性能影响小（fork子进程处理）

**缺点**：
- 可能丢失最后一次保存后的数据
- fork操作在数据量大时可能阻塞主进程
- 不适合实时性要求极高的场景

## 3.3 AOF持久化

### 3.3.1 AOF工作原理

AOF通过记录所有写操作命令来保证数据持久性。Redis将所有修改数据的命令追加到AOF文件末尾，重启时重新执行这些命令来恢复数据。

```python
# AOF配置示例
# redis.conf

# 启用AOF持久化
appendonly yes

# AOF文件名
appendfilename "appendonly.aof"

# 同步策略
appendfsync everysec

# AOF重写时是否同步
no-appendfsync-on-rewrite no

# 自动重写条件
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# 加载损坏的AOF文件时是否继续
aof-load-truncated yes
```

### 3.3.2 AOF同步策略

Redis提供三种AOF同步策略：

```python
# appendfsync配置说明

# always: 每次写操作都同步到磁盘（最安全，性能最低）
# appendfsync always

# everysec: 每秒同步一次（推荐，平衡安全性和性能）
# appendfsync everysec

# no: 由操作系统决定同步时机（性能最好，可能丢失数据）
# appendfsync no
```

### 3.3.3 AOF重写机制

随着时间推移，AOF文件会越来越大。Redis通过AOF重写来压缩文件：

```python
# AOF重写相关操作

# 手动触发AOF重写
r.bgrewriteaof()

# 获取AOF相关信息
info = r.info('persistence')
print(f"AOF文件大小: {info.get('aof_current_size', 0)} bytes")
print(f"AOF基础大小: {info.get('aof_base_size', 0)} bytes")
print(f"AOF缓冲区大小: {info.get('aof_buffer_length', 0)} bytes")

# 检查AOF文件状态
aof_status = r.info('persistence').get('aof_enabled', 0)
if aof_status:
    print("AOF持久化已启用")
else:
    print("AOF持久化未启用")
```

### 3.3.4 AOF优缺点分析

**优点**：
- 数据安全性高，最多丢失1秒数据
- AOF文件易于理解和解析
- 支持后台重写，不影响主进程

**缺点**：
- AOF文件通常比RDB文件大
- 恢复速度比RDB慢
- 在写入频繁的场景下对性能有影响

## 3.4 混合持久化

### 3.4.1 混合持久化原理

Redis 4.0+支持RDB和AOF的混合持久化模式。在AOF重写时，先将内存数据以RDB格式写入AOF文件，然后再将重写期间的增量命令以AOF格式追加。

```python
# 启用混合持久化
# redis.conf

aof-use-rdb-preamble yes
```

### 3.4.2 混合持久化优势

- **快速恢复**：使用RDB格式加载基础数据
- **数据完整性**：使用AOF格式保证增量数据不丢失
- **文件大小优化**：比纯AOF文件更紧凑

## 3.5 Redis复制原理

### 3.5.1 主从复制架构

Redis支持主从复制，一个主节点可以有多个从节点，从节点会复制主节点的数据：

```python
# 主从复制配置示例

# 主节点配置（通常无需特殊配置）
# redis-master.conf
bind 127.0.0.1
port 6379

# 从节点配置
# redis-slave.conf
bind 127.0.0.1
port 6380
slaveof 127.0.0.1 6379

# 如果主节点有密码
# masterauth your_password

# 从节点是否只读
slave-read-only yes
```

### 3.5.2 复制过程详解

Redis复制过程分为三个阶段：

1. **建立连接**：从节点连接到主节点
2. **同步数据**：主节点将数据同步到从节点
3. **命令传播**：主节点将后续写命令传播到从节点

```python
# 复制状态监控
import redis

# 主节点
master = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

# 从节点
slave = redis.Redis(host='127.0.0.1', port=6380, decode_responses=True)

# 检查复制状态
replication_info = master.info('replication')
print(f"主节点角色: {replication_info.get('role')}")
print(f"连接的从节点数: {replication_info.get('connected_slaves', 0)}")

# 从节点信息
slave_info = slave.info('replication')
print(f"从节点角色: {slave_info.get('role')}")
print(f"主节点地址: {slave_info.get('master_host')}:{slave_info.get('master_port')}")
print(f"复制偏移量: {slave_info.get('master_repl_offset')}")
```

### 3.5.3 全量复制与部分复制

**全量复制**：从节点第一次连接主节点时，主节点会生成RDB文件发送给从节点。

**部分复制**：网络中断后重连，主节点只发送中断期间的命令。

```python
# 复制缓冲区配置
# redis.conf

# 复制缓冲区大小
repl-backlog-size 1mb

# 复制缓冲区存活时间
repl-backlog-ttl 3600

# 从节点超时时间
repl-timeout 60

# 主节点无响应时从节点是否继续服务旧数据
slave-serve-stale-data yes

# 从节点与主节点失联时是否停止服务
slave-read-only yes
```

## 3.6 复制配置与管理

### 3.6.1 复制配置详解

```python
# 完整的复制配置示例
# redis.conf

# 复制相关配置
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-ping-slave-period 10
repl-timeout 60
repl-disable-tcp-nodelay no
repl-backlog-size 1mb
repl-backlog-ttl 3600

# 从节点优先级（用于哨兵选举）
slave-priority 100

# 最小从节点数
min-slaves-to-write 0
min-slaves-max-lag 10
```

### 3.6.2 复制管理命令

```python
# 复制管理操作
import redis

master = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
slave = redis.Redis(host='127.0.0.1', port=6380, decode_responses=True)

# 查看复制信息
repl_info = master.info('replication')
print("复制信息:", repl_info)

# 手动同步从节点
# 在从节点上执行
slave.slaveof('127.0.0.1', 6379)

# 将从节点提升为主节点
slave.slaveof()  # 不传递参数表示停止复制

# 检查复制延迟
master_repl_offset = master.info('replication')['master_repl_offset']
slave_repl_offset = slave.info('replication')['slave_repl_offset']
replication_lag = master_repl_offset - slave_repl_offset
print(f"复制延迟: {replication_lag} bytes")

# 安全地停止复制
# 1. 确保从节点数据已同步
# 2. 执行slaveof no one
# 3. 更新应用配置指向新主节点
```

### 3.6.3 复制故障处理

```python
# 复制故障检测与处理

def check_replication_health(master_host, master_port, slave_host, slave_port):
    """检查复制健康状态"""
    try:
        master = redis.Redis(host=master_host, port=master_port, decode_responses=True)
        slave = redis.Redis(host=slave_host, port=slave_port, decode_responses=True)
        
        # 检查连接状态
        master_info = master.info('replication')
        slave_info = slave.info('replication')
        
        # 检查主从角色
        if master_info.get('role') != 'master':
            return False, "主节点角色异常"
        
        if slave_info.get('role') != 'slave':
            return False, "从节点角色异常"
        
        # 检查复制状态
        if slave_info.get('master_link_status') != 'up':
            return False, "主从连接断开"
        
        # 检查复制延迟
        master_offset = master_info.get('master_repl_offset', 0)
        slave_offset = slave_info.get('slave_repl_offset', 0)
        lag = master_offset - slave_offset
        
        if lag > 1000000:  # 1MB延迟阈值
            return False, f"复制延迟过大: {lag} bytes"
        
        return True, "复制状态正常"
        
    except Exception as e:
        return False, f"检查失败: {str(e)}"

def handle_replication_failure(slave_host, slave_port, new_master_host, new_master_port):
    """处理复制故障"""
    try:
        slave = redis.Redis(host=slave_host, port=slave_port, decode_responses=True)
        
        # 停止当前复制
        slave.slaveof()
        
        # 连接到新的主节点
        slave.slaveof(new_master_host, new_master_port)
        
        return True, "复制故障处理成功"
        
    except Exception as e:
        return False, f"故障处理失败: {str(e)}"
```

## 3.7 读写分离架构

### 3.7.1 读写分离实现

利用Redis主从复制实现读写分离：

```python
class ReadWriteSeparation:
    def __init__(self, master_config, slave_configs):
        self.master = redis.Redis(**master_config, decode_responses=True)
        self.slaves = [redis.Redis(**config, decode_responses=True) for config in slave_configs]
        self.slave_index = 0
    
    def write(self, key, value):
        """写操作（只发送到主节点）"""
        return self.master.set(key, value)
    
    def read(self, key):
        """读操作（轮询从节点）"""
        # 简单的轮询负载均衡
        slave = self.slaves[self.slave_index]
        self.slave_index = (self.slave_index + 1) % len(self.slaves)
        
        return slave.get(key)
    
    def pipeline_write(self):
        """获取主节点的管道用于批量写"""
        return self.master.pipeline()
    
    def pipeline_read(self):
        """获取从节点的管道用于批量读"""
        slave = self.slaves[self.slave_index]
        self.slave_index = (self.slave_index + 1) % len(self.slaves)
        return slave.pipeline()

# 使用示例
config = {
    'master_config': {'host': '127.0.0.1', 'port': 6379},
    'slave_configs': [
        {'host': '127.0.0.1', 'port': 6380},
        {'host': '127.0.0.1', 'port': 6381}
    ]
}

rw_sep = ReadWriteSeparation(**config)

# 写操作
rw_sep.write('user:1001:name', 'Alice')

# 读操作
name = rw_sep.read('user:1001:name')
print(f"用户名: {name}")
```

### 3.7.2 读写分离注意事项

1. **数据一致性**：从节点可能有复制延迟
2. **故障转移**：主节点故障时需要手动或自动切换
3. **连接管理**：合理管理主从节点的连接池
4. **监控告警**：实时监控复制状态和延迟

## 3.8 持久化与复制的最佳实践

### 3.8.1 生产环境配置

```python
# 生产环境Redis配置模板
# redis-production.conf

# 基本配置
bind 0.0.0.0
port 6379
daemonize yes
pidfile /var/run/redis/redis-server.pid
logfile /var/log/redis/redis-server.log

# 内存配置
maxmemory 16gb
maxmemory-policy allkeys-lru

# 持久化配置 - 混合模式
save 900 1
save 300 10
save 60 10000

appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
aof-use-rdb-preamble yes

# 复制配置
repl-backlog-size 512mb
repl-backlog-ttl 3600
repl-timeout 60

# 安全配置
requirepass your_secure_password
masterauth your_secure_password

# 性能优化
tcp-keepalive 60
timeout 0
tcp-backlog 511
```

### 3.8.2 备份与恢复策略

```python
import os
import shutil
from datetime import datetime

class RedisBackup:
    def __init__(self, redis_config, backup_dir='/backup/redis'):
        self.redis = redis.Redis(**redis_config, decode_responses=True)
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self):
        """创建Redis备份"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'redis_backup_{timestamp}')
        
        try:
            # 创建RDB快照
            self.redis.bgsave()
            
            # 等待备份完成
            import time
            while True:
                info = self.redis.info('persistence')
                if info.get('rdb_bgsave_in_progress') == 0:
                    break
                time.sleep(1)
            
            # 复制RDB文件
            rdb_path = self.redis.config_get('dir')['dir'] + '/' + self.redis.config_get('dbfilename')['dbfilename']
            shutil.copy2(rdb_path, f"{backup_path}.rdb")
            
            # 如果启用了AOF，也备份AOF文件
            if self.redis.config_get('appendonly')['appendonly'] == 'yes':
                aof_path = self.redis.config_get('dir')['dir'] + '/' + self.redis.config_get('appendfilename')['appendfilename']
                shutil.copy2(aof_path, f"{backup_path}.aof")
            
            return True, f"备份成功: {backup_path}"
            
        except Exception as e:
            return False, f"备份失败: {str(e)}"
    
    def restore_backup(self, backup_file):
        """恢复Redis备份"""
        try:
            # 停止Redis服务（在实际生产环境中需要谨慎操作）
            # 这里只是演示流程
            
            # 复制备份文件到Redis数据目录
            data_dir = self.redis.config_get('dir')['dir']
            shutil.copy2(backup_file, data_dir)
            
            # 重启Redis服务
            # 在实际环境中需要重启Redis进程
            
            return True, "恢复成功"
            
        except Exception as e:
            return False, f"恢复失败: {str(e)}"

# 使用示例
backup_manager = RedisBackup({
    'host': '127.0.0.1',
    'port': 6379,
    'password': 'your_password'
})

# 创建备份
success, message = backup_manager.create_backup()
print(f"备份结果: {success}, 消息: {message}")
```

### 3.8.3 监控与告警

```python
import time
import logging
from typing import Dict, Any

class RedisMonitor:
    def __init__(self, redis_configs: Dict[str, Any]):
        self.redis_instances = {}
        for name, config in redis_configs.items():
            self.redis_instances[name] = redis.Redis(**config, decode_responses=True)
    
    def check_persistence_health(self, instance_name: str) -> Dict[str, Any]:
        """检查持久化健康状态"""
        r = self.redis_instances[instance_name]
        
        try:
            info = r.info('persistence')
            
            return {
                'instance': instance_name,
                'rdb_last_save': info.get('rdb_last_save_time', 0),
                'aof_enabled': info.get('aof_enabled', 0) == 1,
                'aof_last_rewrite_time': info.get('aof_last_rewrite_time_sec', -1),
                'aof_current_size': info.get('aof_current_size', 0),
                'aof_base_size': info.get('aof_base_size', 0),
                'loading': info.get('loading', 0) == 1,
                'status': 'healthy'
            }
            
        except Exception as e:
            return {
                'instance': instance_name,
                'status': 'error',
                'error': str(e)
            }
    
    def check_replication_health(self, instance_name: str) -> Dict[str, Any]:
        """检查复制健康状态"""
        r = self.redis_instances[instance_name]
        
        try:
            info = r.info('replication')
            
            health = {
                'instance': instance_name,
                'role': info.get('role'),
                'connected_slaves': info.get('connected_slaves', 0),
                'master_repl_offset': info.get('master_repl_offset', 0),
                'status': 'healthy'
            }
            
            if info.get('role') == 'slave':
                health.update({
                    'master_link_status': info.get('master_link_status'),
                    'slave_repl_offset': info.get('slave_repl_offset', 0),
                    'master_last_io_seconds_ago': info.get('master_last_io_seconds_ago', -1)
                })
                
                # 检查复制延迟
                if info.get('master_link_status') != 'up':
                    health['status'] = 'warning'
                    health['warning'] = '主从连接断开'
                elif info.get('master_last_io_seconds_ago', 0) > 60:
                    health['status'] = 'warning'
                    health['warning'] = '复制延迟过大'
            
            return health
            
        except Exception as e:
            return {
                'instance': instance_name,
                'status': 'error',
                'error': str(e)
            }
    
    def start_monitoring(self, interval: int = 60):
        """开始监控"""
        while True:
            try:
                # 检查所有实例的持久化状态
                for instance_name in self.redis_instances:
                    persistence_health = self.check_persistence_health(instance_name)
                    replication_health = self.check_replication_health(instance_name)
                    
                    # 记录日志或发送告警
                    if persistence_health['status'] != 'healthy':
                        logging.warning(f"持久化异常: {persistence_health}")
                    
                    if replication_health['status'] != 'healthy':
                        logging.warning(f"复制异常: {replication_health}")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error(f"监控异常: {str(e)}")
                time.sleep(interval)

# 使用示例
monitor_configs = {
    'master': {'host': '127.0.0.1', 'port': 6379, 'password': 'your_password'},
    'slave1': {'host': '127.0.0.1', 'port': 6380, 'password': 'your_password'},
    'slave2': {'host': '127.0.0.1', 'port': 6381, 'password': 'your_password'}
}

monitor = RedisMonitor(monitor_configs)

# 单次检查
health_report = monitor.check_replication_health('master')
print(f"健康报告: {health_report}")

# 开始持续监控（在实际应用中通常作为后台服务运行）
# monitor.start_monitoring(interval=60)
```

## 总结

本章深入探讨了Redis的持久化机制和复制功能。通过学习本章，您应该能够：

1. 理解RDB和AOF两种持久化机制的工作原理和适用场景
2. 掌握持久化配置的最佳实践
3. 理解Redis主从复制的原理和配置方法
4. 实现读写分离架构并处理相关挑战
5. 设计备份恢复策略和监控告警系统
6. 在生产环境中正确配置和管理Redis持久化与复制

在下一章中，我们将学习Redis的高级特性，包括事务、Lua脚本、发布订阅等，这些功能将帮助您构建更复杂的应用系统。