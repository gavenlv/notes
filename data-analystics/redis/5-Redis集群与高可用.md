# 第5章：Redis集群与高可用

## 5.1 Redis集群概述

### 5.1.1 集群的必要性

随着业务增长，单机Redis会遇到以下瓶颈：
- **内存限制**：单机内存有限，无法存储海量数据
- **性能瓶颈**：单线程模型下，CPU成为性能瓶颈
- **可用性问题**：单点故障导致服务不可用

Redis集群通过数据分片和主从复制解决这些问题。

### 5.1.2 集群架构

Redis集群采用去中心化架构：
- **数据分片**：将数据分布到多个节点
- **主从复制**：每个分片有主从节点保证高可用
- **自动故障转移**：主节点故障时从节点自动升级

```python
# Redis集群节点配置示例
# 节点1（主节点）
port 7000
cluster-enabled yes
cluster-config-file nodes-7000.conf
cluster-node-timeout 15000

# 节点2（从节点）
port 7001
cluster-enabled yes
cluster-config-file nodes-7001.conf
cluster-node-timeout 15000
```

## 5.2 Redis Cluster部署

### 5.2.1 集群部署准备

创建6个节点的Redis集群（3主3从）：

```python
# 创建集群目录结构
import os
import shutil

def create_cluster_directories():
    """创建集群节点目录"""
    base_dir = '/opt/redis-cluster'
    
    for port in range(7000, 7006):
        node_dir = os.path.join(base_dir, str(port))
        os.makedirs(node_dir, exist_ok=True)
        
        # 创建配置文件
        config_content = f"""
port {port}
cluster-enabled yes
cluster-config-file nodes-{port}.conf
cluster-node-timeout 15000
appendonly yes
appendfilename "appendonly-{port}.aof"
dbfilename dump-{port}.rdb
logfile "redis-{port}.log"
dir {node_dir}
"""
        
        config_path = os.path.join(node_dir, 'redis.conf')
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"创建节点目录: {node_dir}")

create_cluster_directories()
```

### 5.2.2 手动创建集群

```python
# 启动所有节点
import subprocess
import time

def start_cluster_nodes():
    """启动集群节点"""
    processes = []
    
    for port in range(7000, 7006):
        cmd = ['redis-server', f'/opt/redis-cluster/{port}/redis.conf']
        process = subprocess.Popen(cmd)
        processes.append(process)
        print(f"启动节点: {port}")
    
    time.sleep(3)  # 等待节点启动
    return processes

def create_cluster():
    """创建集群"""
    # 节点地址列表
    nodes = [f'127.0.0.1:{port}' for port in range(7000, 7006)]
    
    # 使用redis-cli创建集群
    cmd = ['redis-cli', '--cluster', 'create'] + nodes + ['--cluster-replicas', '1']
    
    # 自动确认配置
    process = subprocess.Popen(
        cmd, 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    # 输入yes确认配置
    stdout, stderr = process.communicate(input=b'yes\n')
    
    print("集群创建输出:")
    print(stdout.decode())
    
    if process.returncode == 0:
        print("集群创建成功")
    else:
        print(f"集群创建失败: {stderr.decode()}")

# 执行集群创建
processes = start_cluster_nodes()
time.sleep(5)
create_cluster()
```

### 5.2.3 使用redis-trib.rb工具

Redis 5.0之前使用redis-trib.rb工具：

```bash
# 安装Ruby和Redis gem
gem install redis

# 使用redis-trib创建集群
./redis-trib.rb create --replicas 1 \
    127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
    127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005
```

## 5.3 集群数据分片

### 5.3.1 哈希槽（Hash Slot）

Redis集群将数据划分为16384个哈希槽：

```python
# 哈希槽计算原理
import hashlib

def calculate_slot(key):
    """计算key对应的哈希槽"""
    # 使用CRC16算法计算哈希值
    def crc16(data):
        crc = 0x0000
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc = crc << 1
                crc &= 0xFFFF
        return crc
    
    # 计算key的哈希值
    key_bytes = key.encode('utf-8')
    hash_value = crc16(key_bytes)
    
    # 映射到0-16383的槽位
    slot = hash_value % 16384
    
    return slot

# 测试哈希槽计算
test_keys = ['user:1001', 'product:2001', 'order:3001']
for key in test_keys:
    slot = calculate_slot(key)
    print(f"Key: {key} -> Slot: {slot}")
```

### 5.3.2 数据分布策略

```python
# 集群数据分布示例
import redis

class ClusterClient:
    def __init__(self, startup_nodes):
        """初始化集群客户端"""
        self.cluster = redis.RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True
        )
    
    def get_key_info(self, key):
        """获取key的分布信息"""
        try:
            # 获取key所在的节点
            connection = self.cluster.get_redis_connection(key)
            
            # 获取集群信息
            cluster_info = self.cluster.cluster_info()
            slots_info = self.cluster.cluster_slots()
            
            # 计算key的槽位
            slot = self.cluster.keyslot(key)
            
            # 查找槽位对应的节点
            node_info = None
            for slot_range in slots_info:
                start_slot, end_slot, master = slot_range[:3]
                if start_slot <= slot <= end_slot:
                    node_info = {
                        'slot_range': (start_slot, end_slot),
                        'master': master,
                        'replicas': slot_range[3:]
                    }
                    break
            
            return {
                'key': key,
                'slot': slot,
                'node_info': node_info,
                'cluster_size': cluster_info.get('cluster_size')
            }
            
        except Exception as e:
            return {'error': str(e)}

# 使用示例
startup_nodes = [
    {"host": "127.0.0.1", "port": "7000"},
    {"host": "127.0.0.1", "port": "7001"}
]

cluster_client = ClusterClient(startup_nodes)

# 测试key分布
keys = ['user:1001', 'product:2001', 'order:3001']
for key in keys:
    info = cluster_client.get_key_info(key)
    print(f"Key分布信息: {info}")
```

### 5.3.3 哈希标签（Hash Tags）

使用哈希标签确保相关key分布到同一节点：

```python
# 哈希标签使用示例

def create_related_keys(user_id):
    """创建相关联的key"""
    # 使用哈希标签确保相关key在同一个槽位
    hash_tag = f"{{{user_id}}}"
    
    keys = {
        f'user{hash_tag}:profile': f'用户{user_id}的个人资料',
        f'user{hash_tag}:orders': f'用户{user_id}的订单',
        f'user{hash_tag}:preferences': f'用户{user_id}的偏好'
    }
    
    return keys

# 测试哈希标签
user_id = '1001'
related_keys = create_related_keys(user_id)

for key, value in related_keys.items():
    slot = calculate_slot(key)
    print(f"Key: {key} -> Slot: {slot} -> Value: {value}")

# 验证所有相关key都在同一个槽位
slots = [calculate_slot(key) for key in related_keys.keys()]
if len(set(slots)) == 1:
    print(f"所有相关key都在同一个槽位: {slots[0]}")
else:
    print("相关key分布在不同的槽位")
```

## 5.4 集群操作与管理

### 5.4.1 集群状态监控

```python
# 集群状态监控
class ClusterMonitor:
    def __init__(self, startup_nodes):
        self.cluster = redis.RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True
        )
    
    def get_cluster_info(self):
        """获取集群基本信息"""
        info = self.cluster.cluster_info()
        
        return {
            'cluster_state': info.get('cluster_state'),
            'cluster_slots_assigned': info.get('cluster_slots_assigned'),
            'cluster_slots_ok': info.get('cluster_slots_ok'),
            'cluster_slots_pfail': info.get('cluster_slots_pfail'),
            'cluster_slots_fail': info.get('cluster_slots_fail'),
            'cluster_known_nodes': info.get('cluster_known_nodes'),
            'cluster_size': info.get('cluster_size'),
            'cluster_current_epoch': info.get('cluster_current_epoch')
        }
    
    def get_nodes_info(self):
        """获取节点详细信息"""
        nodes = self.cluster.cluster_nodes()
        
        node_list = []
        for node_line in nodes.split('\n'):
            if node_line.strip():
                parts = node_line.split()
                if len(parts) >= 8:
                    node_info = {
                        'node_id': parts[0],
                        'address': parts[1],
                        'flags': parts[2],
                        'master_id': parts[3] if parts[3] != '-' else None,
                        'ping_sent': parts[4],
                        'pong_received': parts[5],
                        'config_epoch': parts[6],
                        'link_state': parts[7]
                    }
                    node_list.append(node_info)
        
        return node_list
    
    def get_slots_distribution(self):
        """获取槽位分布"""
        slots = self.cluster.cluster_slots()
        
        distribution = {}
        for slot_info in slots:
            start_slot = slot_info[0]
            end_slot = slot_info[1]
            master = slot_info[2]
            replicas = slot_info[3:] if len(slot_info) > 3 else []
            
            distribution[f"{start_slot}-{end_slot}"] = {
                'master': f"{master[0]}:{master[1]}",
                'replicas': [f"{replica[0]}:{replica[1]}" for replica in replicas]
            }
        
        return distribution
    
    def check_health(self):
        """检查集群健康状态"""
        cluster_info = self.get_cluster_info()
        
        health_status = {
            'overall': 'healthy',
            'issues': []
        }
        
        # 检查集群状态
        if cluster_info['cluster_state'] != 'ok':
            health_status['overall'] = 'unhealthy'
            health_status['issues'].append('集群状态异常')
        
        # 检查槽位分配
        assigned = cluster_info['cluster_slots_assigned']
        if assigned != 16384:
            health_status['overall'] = 'degraded'
            health_status['issues'].append(f'槽位分配不完整: {assigned}/16384')
        
        # 检查故障槽位
        if cluster_info['cluster_slots_fail'] > 0:
            health_status['overall'] = 'unhealthy'
            health_status['issues'].append(f'有{cluster_info["cluster_slots_fail"]}个故障槽位')
        
        return health_status

# 使用示例
monitor = ClusterMonitor(startup_nodes)

print("集群信息:", monitor.get_cluster_info())
print("节点信息:", monitor.get_nodes_info())
print("槽位分布:", monitor.get_slots_distribution())
print("健康状态:", monitor.check_health())
```

### 5.4.2 集群节点管理

```python
# 集群节点管理
class ClusterManager:
    def __init__(self, startup_nodes):
        self.cluster = redis.RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True
        )
    
    def add_node(self, new_node_host, new_node_port, existing_node_host, existing_node_port):
        """添加新节点到集群"""
        # 启动新节点
        # 这里简化处理，实际需要启动Redis进程
        
        # 使用redis-cli添加节点
        cmd = [
            'redis-cli', '--cluster', 'add-node',
            f'{new_node_host}:{new_node_port}',
            f'{existing_node_host}:{existing_node_port}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, "节点添加成功"
        else:
            return False, f"节点添加失败: {result.stderr}"
    
    def reshard_cluster(self, target_node_id, slots_count, from_nodes=None):
        """重新分片集群"""
        # 获取当前节点信息
        nodes_info = self.cluster.cluster_nodes()
        
        # 构建reshard命令
        cmd = ['redis-cli', '--cluster', 'reshard']
        
        # 添加目标节点
        cmd.extend(['--cluster-to', target_node_id])
        
        # 添加源节点
        if from_nodes:
            for node_id in from_nodes:
                cmd.extend(['--cluster-from', node_id])
        
        # 添加槽位数量
        cmd.extend(['--cluster-slots', str(slots_count)])
        
        # 添加集群节点
        cmd.append('127.0.0.1:7000')  # 任意集群节点
        
        # 执行reshard
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, "重新分片成功"
        else:
            return False, f"重新分片失败: {result.stderr}"
    
    def failover(self, target_node_id):
        """手动故障转移"""
        try:
            # 在目标从节点上执行故障转移
            target_node = None
            nodes_info = self.cluster.cluster_nodes()
            
            # 查找目标节点
            for node_line in nodes_info.split('\n'):
                if node_line.startswith(target_node_id):
                    parts = node_line.split()
                    if len(parts) >= 2:
                        address = parts[1].split('@')[0]  # 移除@后面的部分
                        target_node = address
                        break
            
            if target_node:
                # 连接到目标节点执行故障转移
                host, port = target_node.split(':')
                node_client = redis.Redis(host=host, port=int(port), decode_responses=True)
                
                # 执行故障转移
                node_client.cluster('failover')
                return True, "故障转移成功"
            else:
                return False, "未找到目标节点"
                
        except Exception as e:
            return False, f"故障转移失败: {str(e)}"

# 使用示例
manager = ClusterManager(startup_nodes)

# 添加节点（示例）
# success, message = manager.add_node('127.0.0.1', 7006, '127.0.0.1', 7000)
# print(f"添加节点: {success}, {message}")
```

## 5.5 Redis Sentinel高可用

### 5.5.1 Sentinel架构

Redis Sentinel提供自动故障检测和故障转移：

```python
# Sentinel配置示例
# sentinel.conf

port 26379
daemonize yes
logfile "/var/log/redis/sentinel.log"

# 监控名为mymaster的主节点
# quorum为2表示需要2个Sentinel同意才能进行故障转移
sentinel monitor mymaster 127.0.0.1 6379 2

# 故障转移超时时间（毫秒）
sentinel down-after-milliseconds mymaster 30000

# 故障转移超时时间
sentinel failover-timeout mymaster 180000

# 并行同步的从节点数量
sentinel parallel-syncs mymaster 1
```

### 5.5.2 Sentinel部署

```python
# Sentinel部署脚本
import os
import subprocess

def setup_sentinel():
    """设置Sentinel"""
    
    # 创建Sentinel配置
    sentinel_config = """
port 26379
daemonize yes
logfile "/var/log/redis/sentinel.log"
pidfile "/var/run/redis/sentinel.pid"

# 监控配置
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 30000
sentinel failover-timeout mymaster 180000
sentinel parallel-syncs mymaster 1

# 安全配置（可选）
# sentinel auth-pass mymaster your_password
"""
    
    # 写入配置文件
    config_path = '/etc/redis/sentinel.conf'
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        f.write(sentinel_config)
    
    print(f"Sentinel配置文件已创建: {config_path}")
    
    # 启动Sentinel
    try:
        cmd = ['redis-sentinel', config_path]
        process = subprocess.Popen(cmd)
        print("Sentinel启动成功")
        return process
    except Exception as e:
        print(f"Sentinel启动失败: {e}")
        return None

def setup_sentinel_cluster():
    """设置Sentinel集群（3个节点）"""
    processes = []
    
    for port in [26379, 26380, 26381]:
        config = f"""
port {port}
daemonize yes
logfile "/var/log/redis/sentinel-{port}.log"
pidfile "/var/run/redis/sentinel-{port}.pid"

sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 30000
sentinel failover-timeout mymaster 180000
sentinel parallel-syncs mymaster 1

# Sentinel集群配置
sentinel known-sentinel mymaster 127.0.0.1 26379 \
    "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
"""
        
        config_path = f'/etc/redis/sentinel-{port}.conf'
        with open(config_path, 'w') as f:
            f.write(config)
        
        cmd = ['redis-sentinel', config_path]
        process = subprocess.Popen(cmd)
        processes.append(process)
        print(f"Sentinel节点 {port} 启动成功")
    
    return processes

# 部署Sentinel
# setup_sentinel()
# setup_sentinel_cluster()
```

### 5.5.3 Sentinel客户端

```python
# Sentinel客户端实现
import redis
from redis.sentinel import Sentinel

class SentinelClient:
    def __init__(self, sentinel_nodes, service_name='mymaster'):
        """初始化Sentinel客户端"""
        self.sentinel = Sentinel(
            sentinel_nodes,
            socket_timeout=0.1,
            decode_responses=True
        )
        self.service_name = service_name
    
    def get_master(self):
        """获取主节点连接"""
        return self.sentinel.master_for(self.service_name)
    
    def get_slave(self):
        """获取从节点连接"""
        return self.sentinel.slave_for(self.service_name)
    
    def get_sentinel_info(self):
        """获取Sentinel信息"""
        try:
            # 获取主节点地址
            master_address = self.sentinel.discover_master(self.service_name)
            
            # 获取从节点地址
            slaves = self.sentinel.discover_slaves(self.service_name)
            
            # 获取Sentinel节点信息
            sentinels = self.sentinel.discover_sentinels(self.service_name)
            
            return {
                'master': master_address,
                'slaves': slaves,
                'sentinels': sentinels,
                'service_name': self.service_name
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_failover_status(self):
        """检查故障转移状态"""
        try:
            # 检查主节点是否可访问
            master = self.get_master()
            master.ping()
            
            # 获取Sentinel监控状态
            sentinel_client = redis.Redis(
                host=self.sentinel.sentinels[0].connection_pool.connection_kwargs['host'],
                port=26379,
                decode_responses=True
            )
            
            sentinel_info = sentinel_client.sentinel('master', self.service_name)
            
            return {
                'status': 'healthy',
                'master_ok': True,
                'num_slaves': int(sentinel_info.get('num-slaves', 0)),
                'last_ping_reply': int(sentinel_info.get('last-ping-reply', 0))
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

# 使用示例
sentinel_nodes = [
    ('127.0.0.1', 26379),
    ('127.0.0.1', 26380),
    ('127.0.0.1', 26381)
]

sentinel_client = SentinelClient(sentinel_nodes)

print("Sentinel信息:", sentinel_client.get_sentinel_info())
print("故障转移状态:", sentinel_client.check_failover_status())

# 使用主节点进行写操作
master = sentinel_client.get_master()
master.set('key', 'value')

# 使用从节点进行读操作
slave = sentinel_client.get_slave()
value = slave.get('key')
print(f"读取的值: {value}")
```

## 5.6 集群故障处理

### 5.6.1 故障检测与恢复

```python
# 集群故障处理
class ClusterFailoverHandler:
    def __init__(self, startup_nodes):
        self.cluster = redis.RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True
        )
    
    def detect_failures(self):
        """检测集群故障"""
        failures = []
        
        # 获取集群节点信息
        nodes_info = self.cluster.cluster_nodes()
        
        for node_line in nodes_info.split('\n'):
            if node_line.strip() and not node_line.startswith('#'):
                parts = node_line.split()
                if len(parts) >= 8:
                    node_id = parts[0]
                    flags = parts[2]
                    
                    # 检查节点状态
                    if 'fail' in flags or 'pfail' in flags:
                        failures.append({
                            'node_id': node_id,
                            'flags': flags,
                            'status': 'failed'
                        })
                    elif 'master' in flags and 'slave' not in flags:
                        # 检查主节点是否正常
                        try:
                            address = parts[1].split('@')[0]
                            host, port = address.split(':')
                            
                            node_client = redis.Redis(
                                host=host, 
                                port=int(port), 
                                decode_responses=True,
                                socket_connect_timeout=2
                            )
                            node_client.ping()
                        except:
                            failures.append({
                                'node_id': node_id,
                                'flags': flags,
                                'status': 'unreachable'
                            })
        
        return failures
    
    def handle_failover(self, failed_node_id):
        """处理故障转移"""
        try:
            # 获取故障节点信息
            nodes_info = self.cluster.cluster_nodes()
            
            # 查找故障节点的从节点
            failed_node = None
            replicas = []
            
            for node_line in nodes_info.split('\n'):
                if node_line.strip():
                    parts = node_line.split()
                    if len(parts) >= 8:
                        if parts[0] == failed_node_id:
                            failed_node = parts
                        elif parts[3] == failed_node_id:
                            replicas.append(parts)
            
            if not failed_node:
                return False, "未找到故障节点"
            
            if not replicas:
                return False, "故障节点没有从节点"
            
            # 选择第一个从节点进行故障转移
            replica = replicas[0]
            replica_address = replica[1].split('@')[0]
            host, port = replica_address.split(':')
            
            # 在从节点上执行故障转移
            replica_client = redis.Redis(host=host, port=int(port), decode_responses=True)
            replica_client.cluster('failover')
            
            return True, f"故障转移成功: {replica_address}"
            
        except Exception as e:
            return False, f"故障转移失败: {str(e)}"
    
    def recover_failed_slots(self):
        """恢复故障槽位"""
        try:
            # 获取故障槽位信息
            cluster_info = self.cluster.cluster_info()
            failed_slots = cluster_info.get('cluster_slots_fail', 0)
            
            if failed_slots == 0:
                return True, "没有故障槽位需要恢复"
            
            # 执行集群修复
            # 在实际环境中，这可能需要手动干预
            
            return True, f"开始恢复 {failed_slots} 个故障槽位"
            
        except Exception as e:
            return False, f"槽位恢复失败: {str(e)}"

# 使用示例
handler = ClusterFailoverHandler(startup_nodes)

# 检测故障
failures = handler.detect_failures()
print("检测到的故障:", failures)

# 处理故障
if failures:
    for failure in failures:
        if failure['status'] in ['failed', 'unreachable']:
            success, message = handler.handle_failover(failure['node_id'])
            print(f"故障处理结果: {success}, {message}")
```

### 5.6.2 备份与恢复策略

```python
# 集群备份与恢复
class ClusterBackup:
    def __init__(self, startup_nodes, backup_dir='/backup/redis-cluster'):
        self.cluster = redis.RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True
        )
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self):
        """创建集群备份"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'cluster_backup_{timestamp}')
        
        try:
            # 获取所有主节点
            nodes_info = self.cluster.cluster_nodes()
            master_nodes = []
            
            for node_line in nodes_info.split('\n'):
                if node_line.strip() and 'master' in node_line and 'slave' not in node_line:
                    parts = node_line.split()
                    address = parts[1].split('@')[0]
                    master_nodes.append(address)
            
            # 备份每个主节点
            backup_results = []
            for address in master_nodes:
                host, port = address.split(':')
                
                node_client = redis.Redis(host=host, port=int(port), decode_responses=True)
                
                # 创建备份
                node_client.bgsave()
                
                # 等待备份完成
                import time
                while True:
                    info = node_client.info('persistence')
                    if info.get('rdb_bgsave_in_progress') == 0:
                        break
                    time.sleep(1)
                
                # 复制备份文件
                rdb_path = node_client.config_get('dir')['dir'] + '/' + node_client.config_get('dbfilename')['dbfilename']
                backup_file = f"{backup_path}_{host}_{port}.rdb"
                shutil.copy2(rdb_path, backup_file)
                
                backup_results.append({
                    'node': address,
                    'backup_file': backup_file,
                    'status': 'success'
                })
            
            # 备份集群配置
            config_backup = f"{backup_path}_cluster_config.json"
            cluster_info = {
                'timestamp': timestamp,
                'nodes': master_nodes,
                'cluster_info': self.cluster.cluster_info()
            }
            
            with open(config_backup, 'w') as f:
                json.dump(cluster_info, f, indent=2)
            
            return True, {
                'backup_path': backup_path,
                'node_backups': backup_results,
                'config_backup': config_backup
            }
            
        except Exception as e:
            return False, f"备份失败: {str(e)}"
    
    def restore_backup(self, backup_data):
        """恢复集群备份"""
        try:
            # 这里简化处理，实际恢复需要更复杂的逻辑
            # 包括停止集群、恢复数据、重新启动等步骤
            
            return True, "恢复流程开始（实际实现需要更多步骤）"
            
        except Exception as e:
            return False, f"恢复失败: {str(e)}"

# 使用示例
backup_manager = ClusterBackup(startup_nodes)

# 创建备份
# success, result = backup_manager.create_backup()
# if success:
#     print("备份成功:", result)
# else:
#     print("备份失败:", result)
```

## 总结

本章深入探讨了Redis集群和高可用方案。通过学习本章，您应该能够：

1. 理解Redis集群的架构和工作原理
2. 掌握Redis Cluster的部署和管理
3. 熟悉数据分片和哈希槽机制
4. 了解Sentinel高可用方案
5. 掌握集群故障检测和处理方法
6. 实施集群备份和恢复策略

Redis集群和高可用是构建大规模、高并发应用的关键技术。在下一章中，我们将学习Redis性能优化和监控，确保Redis在生产环境中稳定高效运行。