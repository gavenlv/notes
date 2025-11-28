# 第6章：集群部署与高可用代码示例

## 📖 概述

本目录包含了第6章"集群部署与高可用"的完整代码示例，演示了RabbitMQ集群的部署、管理、监控和故障处理等核心功能。

## 📁 文件结构

```
chapter6/
├── cluster_management.py      # 集群管理与配置
├── cluster_monitoring.py      # 集群监控与告警
├── fault_tolerance.py         # 故障处理与自动恢复
└── README.md                  # 本文档
```

## 🔧 功能特性

### 1. cluster_management.py - 集群管理与配置

**主要功能：**
- 🏗️ 集群节点连接管理
- 📋 镜像队列配置
- ⚖️ 负载均衡策略设置
- 🔍 故障检测与恢复
- 📊 性能监控与分析

**核心类：**
- `ClusterNode`: 集群节点管理
- `RabbitMQClusterManager`: 集群管理器主类

**演示场景：**
- 集群连接测试
- 镜像队列设置
- 消息发布/消费测试
- 健康监控
- 故障转移测试
- 性能优化

### 2. cluster_monitoring.py - 集群监控与告警

**主要功能：**
- 📡 实时节点状态监控
- 📈 队列性能指标收集
- 🚨 告警规则配置
- 📊 性能报告生成
- 📋 历史数据分析

**核心类：**
- `ClusterNodeMonitor`: 节点监控器
- `ClusterAlertManager`: 告警管理器
- `ClusterMonitor`: 集群监控主类

**演示场景：**
- 多节点监控
- 告警规则测试
- 性能报告生成
- 自动扩缩容测试

### 3. fault_tolerance.py - 故障处理与自动恢复

**主要功能：**
- 🔍 故障检测与分类
- 🔄 自动故障转移
- 💾 灾难恢复方案
- 📊 故障分析报告
- 🛡️ 优雅降级策略

**核心类：**
- `NodeHealthChecker`: 节点健康检查器
- `FaultDetector`: 故障检测器
- `AutomaticFailoverManager`: 自动故障转移管理器
- `DisasterRecovery`: 灾难恢复管理器

**演示场景：**
- 健康监控演示
- 故障检测演示
- 自动故障转移演示
- 灾难恢复演示
- 集成测试演示

## 🛠️ 环境要求

### 系统要求
- **操作系统**: Linux/macOS/Windows
- **Python**: 3.8+
- **RabbitMQ**: 3.8+
- **内存**: 最小 4GB，推荐 8GB+
- **磁盘**: 最小 10GB 可用空间

### 依赖包
```bash
pip install pika requests psutil
```

### RabbitMQ配置
```bash
# 启用管理插件
rabbitmq-plugins enable rabbitmq_management

# 创建管理员用户
rabbitmqctl add_user admin admin123
rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

## 🚀 使用方法

### 基本使用

```python
# 1. 集群管理
from cluster_management import RabbitMQClusterManager

cluster_config = [
    {'name': 'node1', 'host': 'rabbitmq-node1'},
    {'name': 'node2', 'host': 'rabbitmq-node2'},
    {'name': 'node3', 'host': 'rabbitmq-node3'}
]

manager = RabbitMQClusterManager(cluster_config)
manager.connect_to_cluster()
manager.setup_mirrored_queue('my_queue')
```

### 监控使用

```python
# 2. 集群监控
from cluster_monitoring import ClusterMonitor

monitor = ClusterMonitor(cluster_config, alert_config)
monitor.connect_all_nodes()
monitor.start_monitoring()
```

### 故障处理

```python
# 3. 故障容错
from fault_tolerance import FaultToleranceDemo

demo = FaultToleranceDemo()
demo.demo_health_monitoring()
demo.demo_fault_detection()
```

### 运行完整演示

```bash
# 集群管理演示
python cluster_management.py

# 集群监控演示
python cluster_monitoring.py

# 故障容错演示
python fault_tolerance.py
```

## ⚙️ 性能调优参数

### 集群调优
```python
# 镜像队列设置
ha_sync_mode = 'automatic'  # 'automatic' | 'manual'
ha_sync_batch_size = 1000
ha_maximum_queues = 0  # 无限制

# 内存阈值
memory_high_watermark = 0.6  # 60%
memory_alarm_low_watermark = 0.4  # 40%

# 磁盘阈值
disk_free_limit = "1GB"  # 最小1GB可用空间
```

### 网络调优
```python
# 心跳间隔
heartbeat_interval = 60  # 秒

# 连接池配置
max_connections = 100
max_channels = 1000

# 超时设置
connection_timeout = 30
recovery_interval = 5
```

### 队列调优
```python
# 队列配置
max_length = 1000000  # 最大消息数
max_length_bytes = "2GB"  # 最大队列大小

# 消费者预取
prefetch_count = 100  # 每个消费者预取消息数
```

## 📊 监控指标

### 系统指标
- **CPU使用率**: 节点CPU占用百分比
- **内存使用率**: 节点内存占用百分比
- **磁盘使用率**: 磁盘空间占用百分比
- **网络流量**: 入站/出站网络字节数

### RabbitMQ指标
- **队列消息数**: 各队列积压消息数量
- **消费者数量**: 活跃消费者数量
- **连接数**: 当前建立的连接数
- **通道数**: 当前打开的通道数
- **镜像同步状态**: 队列镜像同步进度

### 健康检查指标
- **节点响应时间**: 节点API响应延迟
- **连接成功率**: 连接建立成功率
- **操作失败率**: 操作失败频率
- **故障转移次数**: 故障转移触发次数

### 告警阈值
```python
ALERT_RULES = {
    'high_memory': {'threshold': 85, 'duration': 60},
    'high_cpu': {'threshold': 80, 'duration': 120},
    'queue_backup': {'threshold': 10000, 'duration': 300},
    'node_offline': {'threshold': 1, 'duration': 30},
    'disk_full': {'threshold': 95, 'duration': 60}
}
```

## 🐛 故障排查

### 常见问题

#### 1. 节点连接失败
```bash
# 检查RabbitMQ服务状态
sudo systemctl status rabbitmq-server

# 检查网络连接
telnet rabbitmq-node1 5672

# 检查防火墙设置
sudo ufw status
```

#### 2. 镜像队列同步问题
```python
# 检查镜像状态
rabbitmqctl list_queues name policy master slave synchronised_slaves

# 强制同步队列
rabbitmqctl sync_queue queue_name

# 取消镜像
rabbitmqctl clear_policy queue_name
```

#### 3. 内存使用过高
```bash
# 查看内存使用情况
rabbitmqctl status | grep memory

# 清理队列
rabbitmqctl purge_queue queue_name

# 重启内存告警
rabbitmqctl forget_cluster_node node_name
```

#### 4. 磁盘空间不足
```bash
# 查看磁盘使用
df -h

# 清理日志文件
find /var/log/rabbitmq -name "*.log*" -type f -mtime +7 -delete

# 设置磁盘阈值
rabbitmqctl set_disk_limit 1000000000  # 1GB
```

### 日志分析

#### 关键日志位置
```bash
# RabbitMQ主日志
/var/log/rabbitmq/rabbitmq@hostname.log

# 集群Erlang日志
/var/log/rabbitmq/rabbitmq@hostname-sasl.log

# 系统日志
journalctl -u rabbitmq-server
```

#### 常用日志命令
```bash
# 查看错误日志
tail -f /var/log/rabbitmq/rabbitmq@hostname.log | grep ERROR

# 统计错误数量
grep ERROR /var/log/rabbitmq/rabbitmq@hostname.log | wc -l

# 查看特定时间范围日志
grep "2024-01-01" /var/log/rabbitmq/rabbitmq@hostname.log
```

## 🎯 最佳实践

### 1. 集群部署最佳实践

#### 节点规划
- **奇数节点**: 使用奇数个节点(3/5/7)确保仲裁
- **硬件均衡**: 确保各节点硬件配置一致
- **网络稳定**: 使用低延迟、稳定的网络连接
- **地域分布**: 跨数据中心部署时考虑网络延迟

#### 集群配置
```python
# 推荐配置
cluster_config = {
    'cluster_nodes': [
        {'name': 'rabbit@node1', 'host': '10.0.1.10'},
        {'name': 'rabbit@node2', 'host': '10.0.1.11'},
        {'name': 'rabbit@node3', 'host': '10.0.1.12'}
    ],
    'mirroring': {
        'mode': 'automatic',
        'sync_threshold': 1000,
        'ha_policy': 'all'  # 镜像到所有节点
    }
}
```

### 2. 监控最佳实践

#### 监控策略
- **多层次监控**: 系统、RabbitMQ、应用三层监控
- **实时告警**: 关键指标实时监控和告警
- **历史趋势**: 保存历史数据用于趋势分析
- **容量规划**: 基于历史数据预测容量需求

#### 监控工具
```python
# 监控工具集成
MONITORING_TOOLS = {
    'prometheus': 'Prometheus + Grafana',
    'datadog': 'Datadog APM',
    'newrelic': 'New Relic监控',
    'custom': '自定义监控脚本'
}
```

### 3. 故障处理最佳实践

#### 故障响应流程
1. **自动检测**: 监控系统自动检测故障
2. **告警通知**: 立即通知相关技术人员
3. **自动恢复**: 尝试自动故障转移
4. **人工介入**: 必要时进行人工处理
5. **事后分析**: 分析故障原因，优化预防措施

#### 故障演练
```python
# 定期故障演练计划
DRILL_SCHEDULE = {
    'node_failure': 'monthly',
    'network_partition': 'quarterly',
    'data_center_failure': 'annually',
    'full_cluster_recovery': 'annually'
}
```

### 4. 性能优化最佳实践

#### 消息处理优化
```python
# 优化的消费者配置
CONSUMER_CONFIG = {
    'prefetch_count': 50,  # 适度的预取
    'auto_ack': False,     # 手动确认
    'no_local': True,      # 不接收本地消息
    'exclusive': False,    # 非独占消费
    'arguments': {
        'x-priority': 10,      # 优先级队列
        'x-max-length': 100000, # 队列长度限制
        'x-queue-mode': 'lazy'  # 懒加载模式
    }
}
```

#### 集群性能调优
```bash
# 系统参数调优
echo 'net.core.somaxconn = 4096' >> /etc/sysctl.conf
echo 'vm.swappiness = 10' >> /etc/sysctl.conf
echo 'fs.file-max = 2097152' >> /etc/sysctl.conf
sysctl -p

# RabbitMQ配置优化
echo 'RABBITMQ_NODE_MAX_MEMORY=6G' >> /etc/rabbitmq/rabbitmq-env.conf
echo 'RABBITMQ_MAX_MESSAGE_SIZE=134217728' >> /etc/rabbitmq/rabbitmq-env.conf
```

## 📝 示例输出

### 集群监控输出
```
🔍 开始集群监控...
📊 节点连接结果: 3/3 连接成功
📊 集群监控摘要: {
    'total_nodes': 3,
    'connected_nodes': 3,
    'total_messages': 1250,
    'total_consumers': 6,
    'average_memory': 45.2,
    'average_cpu': 23.8
}
🚨 告警: 高内存使用 - node1: 85.2%
```

### 故障转移输出
```
🔄 开始为故障节点 node2 执行故障转移
🔌 隔离故障节点: node2
🔋 激活备份节点: node1, node3
🔄 重定向流量到: node1, node3
✅ 验证节点健康状态: node1, node3
📢 通知客户端节点故障: node2
✅ 故障转移完成: node2
```

### 灾难恢复输出
```
💾 开始创建集群备份: cluster_backup_20241201_143000
✅ 集群备份创建成功: cluster_backup_20241201_143000
🔥 模拟灾难事件...
🔄 从备份 cluster_backup_20241201_143000 开始恢复...
🔧 执行恢复步骤 1/6: 停止所有集群节点
🔧 执行恢复步骤 2/6: 从备份恢复数据目录
🔧 执行恢复步骤 3/6: 重新配置集群
🔧 执行恢复步骤 4/6: 启动节点并重新加入集群
🔧 执行恢复步骤 5/6: 验证数据一致性
🔧 执行恢复步骤 6/6: 恢复客户端连接
✅ 灾难恢复成功完成
```

## 🔗 相关资源

### 官方文档
- [RabbitMQ集群指南](https://www.rabbitmq.com/clustering.html)
- [镜像队列](https://www.rabbitmq.com/ha.html)
- [集群故障转移](https://www.rabbitmq.com/clustering.html#failure-handling)

### 社区资源
- [RabbitMQ GitHub仓库](https://github.com/rabbitmq/rabbitmq-server)
- [RabbitMQ社区插件](https://www.rabbitmq.com/community-plugins.html)
- [RabbitMQ社区论坛](https://groups.google.com/forum/#!forum/rabbitmq-users)

### 监控工具
- [Prometheus RabbitMQ Exporter](https://github.com/kbudde/rabbitmq_exporter)
- [Grafana RabbitMQ Dashboard](https://grafana.com/grafana/dashboards/4376-rabbitmq-overview/)
- [RabbitMQ Management UI](https://www.rabbitmq.com/management.html)

---

## 🤝 贡献

如果您发现任何问题或有改进建议，请创建Issue或提交Pull Request。

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

---

*最后更新: 2024年12月*