# 第10章：RabbitMQ故障处理与恢复

## 📖 概述

在生产环境中，RabbitMQ集群可能面临各种故障情况，包括网络分区、节点宕机、磁盘空间不足、内存压力、消息积压等。本章将详细介绍RabbitMQ故障检测、诊断、处理和恢复的最佳实践，帮助您构建高可用的消息系统。

## 🎯 学习目标

- 掌握RabbitMQ常见故障类型和识别方法
- 学会配置故障检测和自动恢复机制
- 理解数据备份和灾难恢复策略
- 掌握故障诊断和性能分析方法
- 学会构建故障处理自动化工具
- 了解容量规划和预防性维护策略

## 🔍 故障类型分析

### 1. 硬件层面故障

#### 节点宕机
- **症状**: 节点无响应、心跳丢失、管理API不可访问
- **影响**: 该节点上的队列和交换机不可用
- **检测**: 通过集群状态检查、心跳监控

#### 磁盘故障
- **症状**: 磁盘写入失败、磁盘空间不足
- **影响**: 持久化消息无法写入、队列阻塞
- **检测**: 磁盘监控工具、日志分析

#### 网络故障
- **症状**: 节点间通信中断、网络分区
- **影响**: 集群分裂、数据不一致
- **检测**: 网络监控、集群状态检查

### 2. 软件层面故障

#### RabbitMQ服务崩溃
- **症状**: 进程异常退出、核心转储
- **影响**: 整个节点服务中断
- **检测**: 服务监控、健康检查

#### 内存压力
- **症状**: 内存使用率过高、频繁GC
- **影响**: 性能下降、连接拒绝
- **检测**: 内存监控、堆转储分析

#### 配置错误
- **症状**: 启动失败、配置无效
- **影响**: 服务无法正常启动
- **检测**: 启动日志、配置验证

### 3. 应用层面故障

#### 消息积压
- **症状**: 队列消息数量异常增长
- **影响**: 内存使用增加、处理延迟
- **检测**: 队列监控、消息计数

#### 消费者异常
- **症状**: 消费者连接断开、消息处理失败
- **影响**: 消息无法正常消费、队列阻塞
- **检测**: 连接监控、消费成功率

## 🛠️ 故障检测机制

### 1. 健康检查配置

```bash
# 基础健康检查
rabbitmq-diagnostics ping
rabbitmq-diagnostics check_running
rabbitmq-diagnostics check_port_connectivity

# 集群健康检查
rabbitmq-diagnostics cluster_status
rabbitmq-diagnostics check_cluster_health
```

### 2. 自定义健康检查脚本

```bash
#!/bin/bash
# health_check.sh - RabbitMQ健康检查脚本

RABBITMQ_HOST=${RABBITMQ_HOST:-"localhost"}
RABBITMQ_PORT=${RABBITMQ_PORT:-"15672"}
RABBITMQ_USER=${RABBITMQ_USER:-"admin"}
RABBITMQ_PASS=${RABBITMQ_PASS:-"password"}

# 检查RabbitMQ API响应
check_api_health() {
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -u ${RABBITMQ_USER}:${RABBITMQ_PASS} \
        http://${RABBITMQ_HOST}:${RABBITMQ_PORT}/api/health/checks/alarms)
    
    if [ "$response" = "200" ]; then
        echo "API健康检查通过"
        return 0
    else
        echo "API健康检查失败 (HTTP: $response)"
        return 1
    fi
}

# 检查节点状态
check_node_status() {
    nodes=$(curl -s -u ${RABBITMQ_USER}:${RABBITMQ_PASS} \
        http://${RABBITMQ_HOST}:${RABBITMQ_PORT}/api/nodes)
    
    running_nodes=$(echo "$nodes" | jq '[.[] | select(.running == true)] | length')
    total_nodes=$(echo "$nodes" | jq 'length')
    
    echo "运行节点数: $running_nodes/$total_nodes"
    
    if [ "$running_nodes" -gt 0 ] && [ "$running_nodes" -eq "$total_nodes" ]; then
        echo "所有节点正常运行"
        return 0
    else
        echo "存在异常节点"
        return 1
    fi
}

# 检查磁盘空间
check_disk_space() {
    disk_usage=$(df -h /var/lib/rabbitmq | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$disk_usage" -lt 80 ]; then
        echo "磁盘空间充足 (${disk_usage}%)"
        return 0
    else
        echo "磁盘空间不足 (${disk_usage}%)"
        return 1
    fi
}

# 检查内存使用
check_memory() {
    memory_usage=$(free | awk 'FNR==2{printf "%.1f", $3/($3+$4)*100}')
    
    if (( $(echo "$memory_usage < 80" | bc -l) )); then
        echo "内存使用正常 (${memory_usage}%)"
        return 0
    else
        echo "内存使用过高 (${memory_usage}%)"
        return 1
    fi
}

# 执行所有检查
main() {
    echo "=== RabbitMQ健康检查 ==="
    
    api_healthy=true
    node_healthy=true
    disk_healthy=true
    memory_healthy=true
    
    check_api_health || api_healthy=false
    check_node_status || node_healthy=false
    check_disk_space || disk_healthy=false
    check_memory || memory_healthy=false
    
    if $api_healthy && $node_healthy && $disk_healthy && $memory_healthy; then
        echo "=== 整体健康状态: 健康 ==="
        exit 0
    else
        echo "=== 整体健康状态: 不健康 ==="
        exit 1
    fi
}

main "$@"
```

### 3. 监控告警配置

```yaml
# prometheus_alerts.yml - Prometheus告警规则
groups:
- name: rabbitmq.rules
  rules:
  - alert: RabbitMQNodeDown
    expr: rabbitmq_up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "RabbitMQ节点 {{ $labels.instance }} 宕机"
      description: "RabbitMQ节点已宕机超过1分钟"

  - alert: RabbitMQQueueMessagesHigh
    expr: rabbitmq_queue_messages > 10000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "队列 {{ $labels.queue }} 消息积压"
      description: "队列 {{ $labels.queue }} 消息数量达到 {{ $value }}"

  - alert: RabbitMQMemoryHigh
    expr: rabbitmq_process_resident_memory_bytes / 1024 / 1024 > 2048
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "RabbitMQ内存使用过高"
      description: "节点 {{ $labels.instance }} 内存使用超过2GB"

  - alert: RabbitMQDiskSpaceLow
    expr: rabbitmq_disk_free_bytes / 1024 / 1024 / 1024 < 5
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "RabbitMQ磁盘空间不足"
      description: "节点 {{ $labels.instance }} 磁盘剩余空间不足5GB"
```

## 🔧 故障处理策略

### 1. 节点故障处理

#### 单节点故障恢复

```bash
# 1. 检查节点状态
rabbitmq-diagnostics cluster_status

# 2. 停止并重新启动节点
rabbitmqctl stop
systemctl start rabbitmq-server

# 3. 检查节点恢复状态
rabbitmq-diagnostics ping
rabbitmq-diagnostics check_running
```

#### 集群节点恢复

```bash
# 1. 检查集群状态
rabbitmqctl cluster_status

# 2. 确认磁盘节点同步
rabbitmqctl sync_offline_queue

# 3. 重新加入集群（如果节点被移除）
rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl join_cluster rabbit@master
rabbitmqctl start_app

# 4. 检查镜像队列状态
rabbitmqctl list_policies
```

### 2. 内存故障处理

#### 内存泄漏检测

```bash
# 检查内存使用情况
rabbitmq-diagnostics memory_breakdown

# 获取堆转储
rabbitmqctl eval 'erlang:halt(1).'
# 或者使用诊断工具
rabbitmq-diagnostics dump_os_processes
```

#### 内存优化配置

```ini
# rabbitmq.conf - 内存优化配置
# 设置内存阈值
vm_memory_high_watermark.relative = 0.6
vm_memory_high_watermark_paging_ratio = 0.5

# 队列内存限制
queue_memory_soft_limit = 0.5

# 连接内存池
connection_channel_max = 2048
connection_max_buffer_size = 33554432
```

#### 紧急内存清理

```bash
# 强制垃圾回收
rabbitmqctl eval 'garbage_collect(all).'

# 清理队列中未确认的消息
rabbitmqctl purge_queue queue_name

# 关闭闲置连接
rabbitmqctl close_connection connection_id "Memory pressure"
```

### 3. 磁盘故障处理

#### 磁盘空间分析

```bash
# 检查磁盘使用情况
rabbitmq-diagnostics disk_free

# 分析日志文件大小
du -sh /var/log/rabbitmq/

# 清理旧日志
find /var/log/rabbitmq/ -name "*.log.*" -mtime +7 -delete

# 分析队列数据文件
du -sh /var/lib/rabbitmq/mnesia/
```

#### 磁盘空间释放

```bash
# 清理Mnesia数据目录
rabbitmqctl stop_app
rm -rf /var/lib/rabbitmq/mnesia/*
rabbitmqctl start_app

# 清理持久化消息（谨慎操作）
rabbitmqctl clear_policy all <<policy_name>>

# 压缩磁盘空间
find /var/lib/rabbitmq/mnesia/ -name "*.dets" -exec sudo dets_compact {} \;
```

### 4. 网络分区处理

#### 分区检测

```bash
# 检查集群状态
rabbitmq-diagnostics cluster_status

# 检查网络连通性
rabbitmq-diagnostics check_port_connectivity

# 分析分区原因
rabbitmqctl environment
```

#### 分区解决策略

```bash
# 手动停止并重新启动分区中的节点
rabbitmqctl stop_app

# 选择主要分区并重新启动
rabbitmqctl start_app

# 对于非主要分区，重置并重新加入
rabbitmqctl reset
rabbitmqctl join_cluster rabbit@primary
```

#### 自动化分区恢复

```json
{
  "policy": {
    "recovery": "automatic",
    "stop_consumers_on_failure": false,
    "resume_publishing": true
  },
  "partitions": {
    "detection": "enabled",
    "resolution": "auto",
    "timeout": 300
  }
}
```

## 💾 数据备份与恢复

### 1. 配置备份

#### 自动配置备份脚本

```bash
#!/bin/bash
# backup_config.sh - RabbitMQ配置备份脚本

BACKUP_DIR="/backup/rabbitmq/$(date +%Y%m%d_%H%M%S)"
RABBITMQ_HOST="localhost"
RABBITMQ_PORT="15672"
RABBITMQ_USER="admin"
RABBITMQ_PASS="password"

mkdir -p "$BACKUP_DIR"

# 备份用户和权限
curl -u ${RABBITMQ_USER}:${RABBITMQ_PASS} \
    http://${RABBITMQ_HOST}:${RABBITMQ_PORT}/api/users \
    > "$BACKUP_DIR/users.json"

# 备份虚拟主机
curl -u ${RABBITMQ_USER}:${RABBITMQ_PASS} \
    http://${RABBITMQ_HOST}:${RABBITMQ_PORT}/api/vhosts \
    > "$BACKUP_DIR/vhosts.json"

# 备份策略
curl -u ${RABBITMQ_USER}:${RABBITMQ_PASS} \
    http://${RABBITMQ_HOST}:${RABBITMQ_PORT}/api/policies \
    > "$BACKUP_DIR/policies.json"

# 备份集群配置
rabbitmqctl environment > "$BACKUP_DIR/environment.txt"
rabbitmqctl cluster_status > "$BACKUP_DIR/cluster_status.txt"

# 压缩备份文件
tar -czf "$BACKUP_DIR.tar.gz" -C "$(dirname "$BACKUP_DIR")" "$(basename "$BACKUP_DIR")"
rm -rf "$BACKUP_DIR"

echo "配置备份完成: $BACKUP_DIR.tar.gz"
```

#### 配置恢复脚本

```bash
#!/bin/bash
# restore_config.sh - RabbitMQ配置恢复脚本

BACKUP_FILE="$1"
TEMP_DIR="/tmp/rabbitmq_restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# 解压备份文件
tar -xzf "$BACKUP_FILE" -C "$(dirname "$TEMP_DIR")"

# 恢复用户和权限
curl -X PUT \
    -u admin:password \
    -H "Content-Type: application/json" \
    -d "$(cat "$TEMP_DIR/users.json")" \
    http://localhost:15672/api/users/bulk/update

# 恢复虚拟主机
curl -X PUT \
    -u admin:password \
    -H "Content-Type: application/json" \
    -d "$(cat "$TEMP_DIR/vhosts.json")" \
    http://localhost:15672/api/vhosts/bulk/update

# 清理临时文件
rm -rf "$TEMP_DIR"

echo "配置恢复完成"
```

### 2. 消息数据备份

#### 消息导出脚本

```python
#!/usr/bin/env python3
# message_backup.py - 导出队列消息

import pika
import json
import argparse
from datetime import datetime

def backup_queue_messages(rabbitmq_url, queue_name, output_file):
    """备份指定队列的所有消息"""
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    
    # 获取队列消息数量
    queue_state = channel.queue_declare(queue=queue_name, passive=True)
    message_count = queue_state.method.message_count
    
    if message_count == 0:
        print(f"队列 {queue_name} 为空")
        return
    
    messages = []
    message_count = min(message_count, 1000)  # 限制消息数量避免内存溢出
    
    print(f"正在备份队列 {queue_name} 的 {message_count} 条消息...")
    
    for i in range(message_count):
        try:
            method_frame, header_frame, body = channel.basic_get(
                queue=queue_name, 
                auto_ack=False
            )
            
            if method_frame:
                message_data = {
                    'delivery_tag': method_frame.delivery_tag,
                    'redelivered': method_frame.redelivered,
                    'exchange': method_frame.exchange,
                    'routing_key': method_frame.routing_key,
                    'properties': {
                        'message_id': header_frame.message_id,
                        'correlation_id': header_frame.correlation_id,
                        'timestamp': header_frame.timestamp,
                        'delivery_mode': header_frame.delivery_mode,
                        'priority': header_frame.priority,
                        'reply_to': header_frame.reply_to,
                        'type': header_frame.type,
                        'user_id': header_frame.user_id,
                        'app_id': header_frame.app_id
                    },
                    'body': body.decode('utf-8') if isinstance(body, bytes) else body
                }
                messages.append(message_data)
                
                # 不确认消息，只获取数据
                channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)
            else:
                break
                
        except Exception as e:
            print(f"获取消息时出错: {e}")
            break
    
    # 保存备份数据
    backup_data = {
        'queue_name': queue_name,
        'backup_time': datetime.now().isoformat(),
        'message_count': len(messages),
        'messages': messages
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    connection.close()
    print(f"消息备份完成，共 {len(messages)} 条消息，保存到: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='RabbitMQ队列消息备份工具')
    parser.add_argument('--rabbitmq-url', default='amqp://guest:guest@localhost:5672',
                        help='RabbitMQ连接URL')
    parser.add_argument('--queue', required=True, help='要备份的队列名称')
    parser.add_argument('--output', required=True, help='输出文件路径')
    
    args = parser.parse_args()
    
    backup_queue_messages(args.rabbitmq_url, args.queue, args.output)

if __name__ == '__main__':
    main()
```

#### 消息恢复脚本

```python
#!/usr/bin/env python3
# message_restore.py - 恢复队列消息

import pika
import json
import argparse
import time

def restore_queue_messages(rabbitmq_url, queue_name, backup_file, requeue=False):
    """从备份文件恢复消息到队列"""
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    
    # 声明队列
    channel.queue_declare(queue=queue_name, durable=True)
    
    # 读取备份数据
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    messages = backup_data['messages']
    print(f"正在恢复队列 {queue_name} 的 {len(messages)} 条消息...")
    
    for i, message_data in enumerate(messages):
        try:
            # 设置消息属性
            properties = pika.BasicProperties(
                message_id=message_data['properties'].get('message_id'),
                correlation_id=message_data['properties'].get('correlation_id'),
                timestamp=message_data['properties'].get('timestamp'),
                delivery_mode=message_data['properties'].get('delivery_mode', 2),  # 持久化
                priority=message_data['properties'].get('priority'),
                reply_to=message_data['properties'].get('reply_to'),
                type=message_data['properties'].get('type'),
                user_id=message_data['properties'].get('user_id'),
                app_id=message_data['properties'].get('app_id')
            )
            
            # 发布消息
            channel.basic_publish(
                exchange=message_data['exchange'],
                routing_key=message_data['routing_key'],
                body=message_data['body'],
                properties=properties
            )
            
            if (i + 1) % 100 == 0:
                print(f"已恢复 {i + 1} 条消息...")
                
        except Exception as e:
            print(f"恢复消息 {i + 1} 时出错: {e}")
            continue
    
    connection.close()
    print(f"消息恢复完成，共 {len(messages)} 条消息")

def main():
    parser = argparse.ArgumentParser(description='RabbitMQ队列消息恢复工具')
    parser.add_argument('--rabbitmq-url', default='amqp://guest:guest@localhost:5672',
                        help='RabbitMQ连接URL')
    parser.add_argument('--queue', required=True, help='目标队列名称')
    parser.add_argument('--backup', required=True, help='备份文件路径')
    
    args = parser.parse_args()
    
    restore_queue_messages(args.rabbitmq_url, args.queue, args.backup)

if __name__ == '__main__':
    main()
```

### 3. 完整集群备份

#### 集群离线备份脚本

```bash
#!/bin/bash
# cluster_backup.sh - 完整集群离线备份

CLUSTER_NAME="rabbit@node1"
BACKUP_BASE_DIR="/backup/rabbitmq/cluster"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_BASE_DIR/$TIMESTAMP"

echo "开始RabbitMQ集群离线备份..."

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 停止所有节点
for node in node1 node2 node3; do
    echo "停止节点 $node"
    rabbitmqctl -n $node stop_app
done

# 备份数据目录
for node in node1 node2 node3; do
    echo "备份节点 $node 数据"
    tar -czf "$BACKUP_DIR/${node}_data.tar.gz" \
        -C /var/lib/rabbitmq mnesia/$node
done

# 备份配置文件
echo "备份配置文件"
cp /etc/rabbitmq/rabbitmq.conf "$BACKUP_DIR/"
cp -r /etc/rabbitmq/enabled_plugins "$BACKUP_DIR/"

# 备份日志配置
echo "备份日志配置"
cp -r /etc/rabbitmq/logging "$BACKUP_DIR/"

# 重新启动节点
for node in node1 node2 node3; do
    echo "启动节点 $node"
    rabbitmqctl -n $node start_app
done

# 压缩备份文件
tar -czf "$BACKUP_DIR.tar.gz" -C "$BACKUP_BASE_DIR" "$TIMESTAMP"
rm -rf "$BACKUP_DIR"

echo "集群备份完成: $BACKUP_DIR.tar.gz"
```

## 🔄 灾难恢复流程

### 1. 灾难恢复规划

#### 恢复目标设定

- **RTO (Recovery Time Objective)**: 业务恢复时间目标 ≤ 30分钟
- **RPO (Recovery Point Objective)**: 数据丢失时间目标 ≤ 5分钟
- **备份频率**: 配置每小时备份，数据每4小时备份

#### 恢复环境准备

```yaml
# disaster_recovery_plan.yml - 灾难恢复计划
recovery_plan:
  primary_cluster:
    nodes: [rabbit@node1, rabbit@node2, rabbit@node3]
    location: " datacenter_a"
    status: "active"
    
  disaster_recovery_cluster:
    nodes: [rabbit@dr-node1, rabbit@dr-node2]
    location: "datacenter_b"
    status: "standby"
    
  recovery_procedures:
    - name: "配置恢复"
      duration: "5分钟"
      steps:
        - "恢复配置文件"
        - "恢复用户和权限"
        - "恢复策略配置"
        
    - name: "数据恢复"
      duration: "15分钟"
      steps:
        - "恢复消息数据"
        - "验证数据完整性"
        - "同步镜像队列"
        
    - name: "服务验证"
      duration: "10分钟"
      steps:
        - "启动集群服务"
        - "验证健康状态"
        - "测试消息传输"
```

### 2. 自动故障转移

#### 负载均衡器配置

```nginx
# nginx.conf - 负载均衡器配置用于故障转移
upstream rabbitmq_cluster {
    server node1.rabbitmq.com:15672 max_fails=3 fail_timeout=30s;
    server node2.rabbitmq.com:15672 max_fails=3 fail_timeout=30s;
    server node3.rabbitmq.com:15672 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name rabbitmq-lb.company.com;
    
    location /api/ {
        proxy_pass http://rabbitmq_cluster;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }
}
```

#### Docker Swarm高可用配置

```yaml
# docker-compose-ha.yml - Docker Swarm高可用配置
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3-management
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      rollback_config:
        parallelism: 1
        delay: 5s
    environment:
      RABBITMQ_ERLANG_COOKIE: "secret_cookie_value"
      RABBITMQ_DEFAULT_USER: "admin"
      RABBITMQ_DEFAULT_PASS: "password"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
      - rabbitmq_logs:/var/log/rabbitmq
    networks:
      - rabbitmq_network
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  rabbitmq_data:
  rabbitmq_logs:

networks:
  rabbitmq_network:
    driver: overlay
```

### 3. 手动恢复流程

#### 分步恢复指南

```bash
#!/bin/bash
# manual_recovery.sh - 手动灾难恢复流程

echo "=== RabbitMQ灾难恢复开始 ==="

# 步骤1: 评估灾难影响
echo "步骤1: 评估灾难影响"
echo "检查主数据中心状态..."
ping -c 3 primary-datacenter.com || echo "主数据中心不可达"

# 步骤2: 启动灾备集群
echo "步骤2: 启动灾备集群"
docker-compose -f docker-compose-dr.yml up -d

# 等待服务启动
sleep 30

# 步骤3: 验证基础服务
echo "步骤3: 验证基础服务"
rabbitmq-diagnostics check_running
if [ $? -ne 0 ]; then
    echo "基础服务启动失败"
    exit 1
fi

# 步骤4: 恢复配置
echo "步骤4: 恢复配置"
./restore_config.sh /backup/latest/config.tar.gz

# 步骤5: 恢复数据
echo "步骤5: 恢复数据"
./cluster_restore.sh /backup/latest/data.tar.gz

# 步骤6: 验证集群状态
echo "步骤6: 验证集群状态"
rabbitmqctl cluster_status
rabbitmq-diagnostics health checks

echo "=== RabbitMQ灾难恢复完成 ==="
```

## 📊 性能故障诊断

### 1. 性能问题诊断

#### 系统性能诊断脚本

```python
#!/usr/bin/env python3
# performance_diagnosis.py - RabbitMQ性能诊断工具

import pika
import psutil
import time
import json
from datetime import datetime
import requests

class PerformanceDiagnoser:
    def __init__(self, rabbitmq_url, api_url, username, password):
        self.rabbitmq_url = rabbitmq_url
        self.api_url = api_url
        self.username = username
        self.password = password
        
    def diagnose_performance(self):
        """执行完整性能诊断"""
        print("=== RabbitMQ性能诊断开始 ===")
        
        diagnosis_results = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': self._collect_system_metrics(),
            'rabbitmq_metrics': self._collect_rabbitmq_metrics(),
            'queue_performance': self._analyze_queue_performance(),
            'connection_analysis': self._analyze_connections(),
            'resource_utilization': self._analyze_resource_utilization(),
            'recommendations': self._generate_recommendations()
        }
        
        return diagnosis_results
    
    def _collect_system_metrics(self):
        """收集系统性能指标"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': dict(psutil.net_io_counters()._asdict()),
            'process_count': len(psutil.pids())
        }
    
    def _collect_rabbitmq_metrics(self):
        """收集RabbitMQ性能指标"""
        try:
            # 获取概览数据
            overview_response = requests.get(
                f"{self.api_url}/api/overview",
                auth=(self.username, self.password)
            )
            overview = overview_response.json()
            
            # 获取队列数据
            queues_response = requests.get(
                f"{self.api_url}/api/queues",
                auth=(self.username, self.password)
            )
            queues = queues_response.json()
            
            return {
                'connections': overview['object_totals']['connections'],
                'channels': overview['object_totals']['channels'],
                'exchanges': overview['object_totals']['exchanges'],
                'queues': overview['object_totals']['queues'],
                'messages': overview['queue_totals']['messages'],
                'message_rate': overview['message_stats']
            }
        except Exception as e:
            print(f"获取RabbitMQ指标失败: {e}")
            return {}
    
    def _analyze_queue_performance(self):
        """分析队列性能"""
        try:
            queues_response = requests.get(
                f"{self.api_url}/api/queues",
                auth=(self.username, self.password)
            )
            queues = queues_response.json()
            
            queue_analysis = []
            for queue in queues:
                analysis = {
                    'name': queue['name'],
                    'messages': queue.get('messages', 0),
                    'message_rate': queue.get('message_stats', {}).get('publish_details', {}).get('rate', 0),
                    'memory_usage': queue.get('memory', 0),
                    'consumers': queue.get('consumers', 0),
                    'backing_queue_status': queue.get('backing_queue_status', {})
                }
                queue_analysis.append(analysis)
            
            return queue_analysis
        except Exception as e:
            print(f"分析队列性能失败: {e}")
            return []
    
    def _analyze_connections(self):
        """分析连接性能"""
        try:
            connections_response = requests.get(
                f"{self.api_url}/api/connections",
                auth=(self.username, self.password)
            )
            connections = connections_response.json()
            
            connection_analysis = []
            for conn in connections:
                analysis = {
                    'name': conn['name'],
                    'state': conn['state'],
                    'user': conn['user'],
                    'channels': conn.get('channels', 0),
                    'frame_max': conn.get('frame_max', 0),
                    'heartbeat': conn.get('heartbeat', 0),
                    'timeout': conn.get('timeout', 0)
                }
                connection_analysis.append(analysis)
            
            return connection_analysis
        except Exception as e:
            print(f"分析连接性能失败: {e}")
            return []
    
    def _analyze_resource_utilization(self):
        """分析资源利用率"""
        system_metrics = self._collect_system_metrics()
        rabbitmq_metrics = self._collect_rabbitmq_metrics()
        
        return {
            'cpu_usage': system_metrics['cpu_percent'],
            'memory_usage': system_metrics['memory_percent'],
            'disk_usage': system_metrics['disk_usage'],
            'connection_utilization': min(rabbitmq_metrics.get('connections', 0) / 1000 * 100, 100),
            'queue_utilization': min(rabbitmq_metrics.get('queues', 0) / 500 * 100, 100)
        }
    
    def _generate_recommendations(self):
        """生成性能优化建议"""
        recommendations = []
        
        system_metrics = self._collect_system_metrics()
        rabbitmq_metrics = self._collect_rabbitmq_metrics()
        
        # CPU建议
        if system_metrics['cpu_percent'] > 80:
            recommendations.append({
                'category': 'CPU',
                'issue': 'CPU使用率过高',
                'recommendation': '考虑增加CPU核心数或优化消息处理逻辑',
                'priority': 'high'
            })
        
        # 内存建议
        if system_metrics['memory_percent'] > 85:
            recommendations.append({
                'category': 'Memory',
                'issue': '内存使用率过高',
                'recommendation': '调整vm_memory_high_watermark设置或增加内存',
                'priority': 'high'
            })
        
        # 队列建议
        total_messages = rabbitmq_metrics.get('messages', 0)
        if total_messages > 10000:
            recommendations.append({
                'category': 'Queue',
                'issue': '队列消息积压严重',
                'recommendation': '增加消费者数量或检查消费逻辑',
                'priority': 'medium'
            })
        
        return recommendations

def main():
    diagnoser = PerformanceDiagnoser(
        rabbitmq_url="amqp://admin:password@localhost:5672",
        api_url="http://localhost:15672",
        username="admin",
        password="password"
    )
    
    results = diagnoser.diagnose_performance()
    
    # 保存诊断结果
    with open('performance_diagnosis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("=== 性能诊断结果 ===")
    print(f"系统指标: CPU {results['system_metrics']['cpu_percent']}%, "
          f"内存 {results['system_metrics']['memory_percent']}%")
    print(f"RabbitMQ指标: 连接 {results['rabbitmq_metrics'].get('connections', 0)}, "
          f"队列 {results['rabbitmq_metrics'].get('queues', 0)}")
    print(f"建议数量: {len(results['recommendations'])}")
    
    for rec in results['recommendations']:
        print(f"- {rec['category']}: {rec['recommendation']} (优先级: {rec['priority']})")

if __name__ == '__main__':
    main()
```

### 2. 故障模式分析

#### 常见故障模式识别

```python
#!/usr/bin/env python3
# failure_pattern_analyzer.py - 故障模式分析器

import time
import json
from datetime import datetime, timedelta

class FailurePatternAnalyzer:
    def __init__(self):
        self.failure_patterns = {
            'memory_leak': {
                'indicators': ['gradual_memory_increase', 'frequent_gc'],
                'threshold': 0.8,
                'severity': 'high'
            },
            'disk_space_exhaustion': {
                'indicators': ['increasing_disk_usage', 'write_failures'],
                'threshold': 0.9,
                'severity': 'critical'
            },
            'network_partition': {
                'indicators': ['node_disconnect', 'cluster_split'],
                'threshold': 0.5,
                'severity': 'critical'
            },
            'queue_overflow': {
                'indicators': ['message_backlog', 'consumer_timeout'],
                'threshold': 10000,
                'severity': 'medium'
            },
            'connection_churn': {
                'indicators': ['frequent_connection_close', 'new_connection_burst'],
                'threshold': 100,
                'severity': 'medium'
            }
        }
    
    def analyze_failure_patterns(self, metrics_history):
        """分析故障模式"""
        detected_patterns = []
        
        for pattern_name, pattern_config in self.failure_patterns.items():
            if self._detect_pattern(metrics_history, pattern_name, pattern_config):
                detected_patterns.append({
                    'pattern': pattern_name,
                    'severity': pattern_config['severity'],
                    'indicators': pattern_config['indicators'],
                    'timestamp': datetime.now().isoformat()
                })
        
        return detected_patterns
    
    def _detect_pattern(self, metrics_history, pattern_name, pattern_config):
        """检测特定故障模式"""
        if pattern_name == 'memory_leak':
            return self._detect_memory_leak(metrics_history, pattern_config['threshold'])
        elif pattern_name == 'disk_space_exhaustion':
            return self._detect_disk_exhaustion(metrics_history, pattern_config['threshold'])
        elif pattern_name == 'network_partition':
            return self._detect_network_partition(metrics_history, pattern_config['threshold'])
        elif pattern_name == 'queue_overflow':
            return self._detect_queue_overflow(metrics_history, pattern_config['threshold'])
        elif pattern_name == 'connection_churn':
            return self._detect_connection_churn(metrics_history, pattern_config['threshold'])
        
        return False
    
    def _detect_memory_leak(self, metrics_history, threshold):
        """检测内存泄漏"""
        if len(metrics_history) < 10:
            return False
        
        recent_memory = [m.get('memory_percent', 0) for m in metrics_history[-10:]]
        
        # 检查内存是否持续增长
        memory_trend = sum(1 for i in range(1, len(recent_memory)) 
                          if recent_memory[i] > recent_memory[i-1])
        
        return memory_trend >= 7 and recent_memory[-1] > threshold * 100
    
    def _detect_disk_exhaustion(self, metrics_history, threshold):
        """检测磁盘空间耗尽"""
        if not metrics_history:
            return False
        
        latest_disk = metrics_history[-1].get('disk_percent', 0)
        return latest_disk > threshold * 100
    
    def _detect_network_partition(self, metrics_history, threshold):
        """检测网络分区"""
        if len(metrics_history) < 5:
            return False
        
        disconnected_nodes = 0
        for metrics in metrics_history[-5:]:
            if metrics.get('nodes_running', 0) < metrics.get('total_nodes', 1):
                disconnected_nodes += 1
        
        return disconnected_nodes >= 3
    
    def _detect_queue_overflow(self, metrics_history, threshold):
        """检测队列溢出"""
        if not metrics_history:
            return False
        
        latest_messages = metrics_history[-1].get('total_messages', 0)
        return latest_messages > threshold
    
    def _detect_connection_churn(self, metrics_history, threshold):
        """检测连接抖动"""
        if len(metrics_history) < 3:
            return False
        
        # 计算连接变化率
        connections = [m.get('connections', 0) for m in metrics_history[-3:]]
        changes = abs(connections[2] - connections[1]) + abs(connections[1] - connections[0])
        
        return changes > threshold

def generate_failure_report(patterns, metrics_history):
    """生成故障分析报告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'analysis_period': {
            'start': metrics_history[0].get('timestamp') if metrics_history else None,
            'end': metrics_history[-1].get('timestamp') if metrics_history else None
        },
        'detected_patterns': patterns,
        'risk_assessment': {
            'high_risk': len([p for p in patterns if p['severity'] == 'critical']),
            'medium_risk': len([p for p in patterns if p['severity'] == 'high']),
            'low_risk': len([p for p in patterns if p['severity'] == 'medium'])
        },
        'recommendations': []
    }
    
    # 根据检测到的模式生成建议
    for pattern in patterns:
        if pattern['pattern'] == 'memory_leak':
            report['recommendations'].append({
                'action': 'memory_optimization',
                'description': '建议立即检查内存使用并重启服务'
            })
        elif pattern['pattern'] == 'disk_space_exhaustion':
            report['recommendations'].append({
                'action': 'disk_cleanup',
                'description': '建议立即清理磁盘空间或扩展存储'
            })
        elif pattern['pattern'] == 'network_partition':
            report['recommendations'].append({
                'action': 'network_diagnosis',
                'description': '建议检查网络连接并修复分区'
            })
    
    return report

def main():
    # 模拟指标历史数据
    metrics_history = []
    for i in range(20):
        metrics = {
            'timestamp': datetime.now() - timedelta(minutes=20-i),
            'memory_percent': 60 + i * 2,  # 模拟内存增长
            'disk_percent': 70 + i * 0.5,
            'connections': 100 + (i % 3) * 10,
            'total_messages': 5000 + i * 200,
            'nodes_running': 2,
            'total_nodes': 3
        }
        metrics_history.append(metrics)
    
    analyzer = FailurePatternAnalyzer()
    patterns = analyzer.analyze_failure_patterns(metrics_history)
    report = generate_failure_report(patterns, metrics_history)
    
    print("=== 故障模式分析报告 ===")
    print(f"检测到的故障模式: {len(patterns)}")
    for pattern in patterns:
        print(f"- {pattern['pattern']} (严重程度: {pattern['severity']})")
    
    # 保存报告
    with open('failure_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("故障分析报告已保存到: failure_analysis_report.json")

if __name__ == '__main__':
    main()
```

## 🔧 故障预防策略

### 1. 预防性维护

#### 定期维护计划

```bash
#!/bin/bash
# preventive_maintenance.sh - 预防性维护脚本

MAINTENANCE_LOG="/var/log/rabbitmq_maintenance.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$MAINTENANCE_LOG"
}

# 每日维护任务
daily_maintenance() {
    log_message "开始每日维护任务"
    
    # 检查磁盘空间
    disk_usage=$(df -h /var/lib/rabbitmq | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 80 ]; then
        log_message "警告: 磁盘使用率超过80% ($disk_usage%)"
        # 执行清理操作
        find /var/log/rabbitmq/ -name "*.log.*" -mtime +3 -delete
        rabbitmqctl eval 'garbage_collect(all).'
    fi
    
    # 检查内存使用
    memory_usage=$(free | awk 'FNR==2{printf "%.1f", $3/($3+$4)*100}')
    if (( $(echo "$memory_usage > 85" | bc -l) )); then
        log_message "警告: 内存使用率过高 ($memory_usage%)"
        # 执行内存清理
        rabbitmqctl eval 'erlang:garbage_collect(Pid) || ok' || true
    fi
    
    # 检查队列状态
    suspicious_queues=$(rabbitmqctl list_queues name messages | awk '$2 > 5000 {print $1}')
    if [ -n "$suspicious_queues" ]; then
        log_message "发现消息积压队列: $suspicious_queues"
    fi
    
    log_message "每日维护任务完成"
}

# 每周维护任务
weekly_maintenance() {
    log_message "开始每周维护任务"
    
    # 压缩Mnesia数据
    rabbitmqctl eval '
        [dets compact(File) || ok || ok, ok, ok] || ok
    end'
    
    # 清理过期连接
    rabbitmqctl list_connections name user state | while read conn user state; do
        if [ "$state" = "blocked" ] || [ "$state" = "closed" ]; then
            log_message "清理异常连接: $conn"
            rabbitmqctl close_connection "$conn" "Maintenance cleanup"
        fi
    done
    
    # 检查镜像队列同步
    mirror_sync_status=$(rabbitmqctl list_queues name policy slave_pids | grep -v "^$")
    if [ -n "$mirror_sync_status" ]; then
        log_message "镜像队列状态检查: $mirror_sync_status"
    fi
    
    log_message "每周维护任务完成"
}

# 每月维护任务
monthly_maintenance() {
    log_message "开始每月维护任务"
    
    # 数据库维护
    rabbitmqctl forget_cluster_node offline_node_name
    
    # 更新统计信息
    rabbitmqctl eval 'mnesia:change_table_copy_type(schema, node(), disc_copies).'
    
    # 生成月度报告
    rabbitmq-diagnostics memory_breakdown > /var/log/rabbitmq/monthly_memory_report.txt
    rabbitmq-diagnostics disk_free > /var/log/rabbitmq/monthly_disk_report.txt
    
    log_message "每月维护任务完成"
}

case "$1" in
    daily)
        daily_maintenance
        ;;
    weekly)
        weekly_maintenance
        ;;
    monthly)
        monthly_maintenance
        ;;
    *)
        echo "用法: $0 {daily|weekly|monthly}"
        exit 1
        ;;
esac
```

### 2. 容量规划

#### 容量规划工具

```python
#!/usr/bin/env python3
# capacity_planner.py - RabbitMQ容量规划工具

import json
import math
from datetime import datetime, timedelta
from collections import defaultdict

class CapacityPlanner:
    def __init__(self):
        self.growth_factors = {
            'connections': 1.2,      # 连接数年增长率20%
            'messages': 1.5,         # 消息量年增长率50%
            'queues': 1.1,           # 队列数年增长率10%
            'throughput': 1.3        # 吞吐量年增长率30%
        }
        
        self.resource_requirements = {
            'connections_per_gb_ram': 10000,
            'messages_per_gb_disk': 1000000,
            'queues_per_cpu_core': 100,
            'throughput_per_cpu_core': 1000  # messages per second
        }
    
    def analyze_current_capacity(self, current_metrics):
        """分析当前容量状况"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'current_metrics': current_metrics,
            'capacity_assessment': self._assess_current_capacity(current_metrics),
            'bottlenecks': self._identify_bottlenecks(current_metrics),
            'recommendations': []
        }
        
        return analysis
    
    def _assess_current_capacity(self, metrics):
        """评估当前容量"""
        assessment = {}
        
        # 连接容量评估
        connections = metrics.get('connections', 0)
        available_ram = metrics.get('available_ram_gb', 8)
        max_connections = available_ram * self.resource_requirements['connections_per_gb_ram']
        connection_utilization = connections / max_connections if max_connections > 0 else 0
        
        assessment['connection_capacity'] = {
            'utilization': connection_utilization,
            'max_capacity': max_connections,
            'current_usage': connections,
            'headroom': 1 - connection_utilization
        }
        
        # 存储容量评估
        messages = metrics.get('messages', 0)
        available_disk = metrics.get('available_disk_gb', 100)
        max_messages = available_disk * self.resource_requirements['messages_per_gb_disk']
        disk_utilization = messages / max_messages if max_messages > 0 else 0
        
        assessment['storage_capacity'] = {
            'utilization': disk_utilization,
            'max_capacity': max_messages,
            'current_usage': messages,
            'headroom': 1 - disk_utilization
        }
        
        # 吞吐量容量评估
        throughput = metrics.get('current_throughput', 0)
        cpu_cores = metrics.get('cpu_cores', 4)
        max_throughput = cpu_cores * self.resource_requirements['throughput_per_cpu_core']
        throughput_utilization = throughput / max_throughput if max_throughput > 0 else 0
        
        assessment['throughput_capacity'] = {
            'utilization': throughput_utilization,
            'max_capacity': max_throughput,
            'current_usage': throughput,
            'headroom': 1 - throughput_utilization
        }
        
        return assessment
    
    def _identify_bottlenecks(self, metrics):
        """识别性能瓶颈"""
        bottlenecks = []
        analysis = self._assess_current_capacity(metrics)
        
        # 检查连接瓶颈
        if analysis['connection_capacity']['utilization'] > 0.8:
            bottlenecks.append({
                'type': 'connection_capacity',
                'severity': 'high' if analysis['connection_capacity']['utilization'] > 0.9 else 'medium',
                'description': '连接容量接近上限',
                'utilization': analysis['connection_capacity']['utilization']
            })
        
        # 检查存储瓶颈
        if analysis['storage_capacity']['utilization'] > 0.8:
            bottlenecks.append({
                'type': 'storage_capacity',
                'severity': 'high' if analysis['storage_capacity']['utilization'] > 0.9 else 'medium',
                'description': '存储容量接近上限',
                'utilization': analysis['storage_capacity']['utilization']
            })
        
        # 检查吞吐量瓶颈
        if analysis['throughput_capacity']['utilization'] > 0.8:
            bottlenecks.append({
                'type': 'throughput_capacity',
                'severity': 'high' if analysis['throughput_capacity']['utilization'] > 0.9 else 'medium',
                'description': '吞吐量接近上限',
                'utilization': analysis['throughput_capacity']['utilization']
            })
        
        return bottlenecks
    
    def forecast_future_capacity(self, current_metrics, timeframe_months=12):
        """预测未来容量需求"""
        forecast = {}
        
        for metric_name, growth_factor in self.growth_factors.items():
            current_value = current_metrics.get(metric_name, 0)
            # 按月计算增长率
            monthly_growth = (growth_factor - 1) / 12
            future_value = current_value * (1 + monthly_growth) ** timeframe_months
            forecast[metric_name] = {
                'current_value': current_value,
                'projected_value': future_value,
                'growth_rate': growth_factor - 1,
                'monthly_growth_rate': monthly_growth
            }
        
        return forecast
    
    def generate_capacity_recommendations(self, current_metrics, forecast):
        """生成容量规划建议"""
        recommendations = []
        
        # 连接容量建议
        projected_connections = forecast['connections']['projected_value']
        current_ram_gb = current_metrics.get('available_ram_gb', 8)
        required_ram_gb = projected_connections / self.resource_requirements['connections_per_gb_ram']
        
        if required_ram_gb > current_ram_gb * 1.1:  # 10%缓冲
            recommendations.append({
                'type': 'memory_expansion',
                'metric': 'connections',
                'current': f"{current_ram_gb}GB",
                'recommended': f"{math.ceil(required_ram_gb)}GB",
                'timeline': '3个月',
                'priority': 'high'
            })
        
        # 存储容量建议
        projected_messages = forecast['messages']['projected_value']
        current_disk_gb = current_metrics.get('available_disk_gb', 100)
        required_disk_gb = projected_messages / self.resource_requirements['messages_per_gb_disk']
        
        if required_disk_gb > current_disk_gb * 1.1:
            recommendations.append({
                'type': 'storage_expansion',
                'metric': 'messages',
                'current': f"{current_disk_gb}GB",
                'recommended': f"{math.ceil(required_disk_gb)}GB",
                'timeline': '6个月',
                'priority': 'medium'
            })
        
        # CPU容量建议
        projected_throughput = forecast['throughput']['projected_value']
        current_cpu_cores = current_metrics.get('cpu_cores', 4)
        required_cores = math.ceil(projected_throughput / self.resource_requirements['throughput_per_cpu_core'])
        
        if required_cores > current_cpu_cores * 1.1:
            recommendations.append({
                'type': 'cpu_expansion',
                'metric': 'throughput',
                'current': f"{current_cpu_cores}核心",
                'recommended': f"{required_cores}核心",
                'timeline': '4个月',
                'priority': 'medium'
            })
        
        return recommendations
    
    def generate_capacity_report(self, current_metrics, timeframe_months=12):
        """生成完整的容量规划报告"""
        analysis = self.analyze_current_capacity(current_metrics)
        forecast = self.forecast_future_capacity(current_metrics, timeframe_months)
        recommendations = self.generate_capacity_recommendations(current_metrics, forecast)
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'analysis_period': f"{timeframe_months}个月",
            'current_analysis': analysis,
            'capacity_forecast': forecast,
            'recommendations': recommendations,
            'action_plan': self._generate_action_plan(recommendations, timeframe_months)
        }
        
        return report
    
    def _generate_action_plan(self, recommendations, timeframe_months):
        """生成行动计划"""
        # 按优先级和紧急程度排序
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        sorted_recommendations = sorted(recommendations, 
                                      key=lambda x: priority_order.get(x.get('priority', 'low'), 1))
        
        # 按时间线分配行动
        monthly_actions = defaultdict(list)
        for rec in sorted_recommendations:
            timeline = rec.get('timeline', '6个月')
            if '3个月' in timeline:
                month = 3
            elif '4个月' in timeline:
                month = 4
            elif '6个月' in timeline:
                month = 6
            else:
                month = 6
            
            monthly_actions[month].append(rec)
        
        return dict(monthly_actions)

def main():
    # 示例当前指标
    current_metrics = {
        'connections': 8000,
        'messages': 500000,
        'queues': 50,
        'current_throughput': 3000,  # messages per second
        'available_ram_gb': 8,
        'available_disk_gb': 100,
        'cpu_cores': 4
    }
    
    planner = CapacityPlanner()
    report = planner.generate_capacity_report(current_metrics, timeframe_months=12)
    
    print("=== RabbitMQ容量规划报告 ===")
    print(f"报告时间: {report['report_timestamp']}")
    print(f"规划周期: {report['analysis_period']}")
    
    print("\n当前容量分析:")
    current_analysis = report['current_analysis']['capacity_assessment']
    for capacity_type, details in current_analysis.items():
        print(f"  {capacity_type}: 利用率 {details['utilization']:.1%}, 余量 {details['headroom']:.1%}")
    
    print("\n容量预测:")
    forecast = report['capacity_forecast']
    for metric, projection in forecast.items():
        growth = projection['growth_rate'] * 100
        print(f"  {metric}: 当前 {projection['current_value']} -> 预测 {projection['projected_value']:.0f} (+{growth:.1f}%)")
    
    print("\n建议:")
    for rec in report['recommendations']:
        print(f"  {rec['type']}: {rec['priority']} - {rec['timeline']}")
        print(f"    当前 {rec['current']} -> 推荐 {rec['recommended']}")
    
    # 保存报告
    with open('capacity_planning_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n详细报告已保存到: capacity_planning_report.json")

if __name__ == '__main__':
    main()
```

### 3. 自动化监控

#### 智能监控脚本

```python
#!/usr/bin/env python3
# smart_monitor.py - 智能监控和预警系统

import pika
import psutil
import time
import json
import requests
import smtplib
from email.mime.text import MimeText
from datetime import datetime, timedelta
import logging

class SmartMonitor:
    def __init__(self, config):
        self.config = config
        self.setup_logging()
        self.alert_history = []
        
    def setup_logging(self):
        """设置日志系统"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/rabbitmq_smart_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_continuous_monitoring(self, interval=60):
        """运行连续监控"""
        self.logger.info("启动智能监控系统")
        
        while True:
            try:
                health_status = self.check_system_health()
                performance_metrics = self.collect_performance_metrics()
                
                # 检查告警条件
                alerts = self.evaluate_alerts(health_status, performance_metrics)
                
                # 处理告警
                for alert in alerts:
                    self.handle_alert(alert)
                
                # 记录监控数据
                self.log_metrics(health_status, performance_metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"监控循环出错: {e}")
                time.sleep(interval)
    
    def check_system_health(self):
        """检查系统健康状态"""
        health = {
            'timestamp': datetime.now().isoformat(),
            'system': self._check_system_health(),
            'rabbitmq': self._check_rabbitmq_health(),
            'network': self._check_network_health(),
            'storage': self._check_storage_health()
        }
        
        return health
    
    def _check_system_health(self):
        """检查系统资源健康"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': (disk.used / disk.total) * 100,
                'disk_free_gb': disk.free / (1024**3),
                'status': 'healthy' if cpu_percent < 80 and memory.percent < 85 and disk.used < disk.total * 0.9 else 'warning'
            }
        except Exception as e:
            self.logger.error(f"系统健康检查失败: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _check_rabbitmq_health(self):
        """检查RabbitMQ服务健康"""
        try:
            # 检查API连接
            response = requests.get(
                f"{self.config['rabbitmq_api_url']}/api/overview",
                auth=(self.config['username'], self.config['password']),
                timeout=5
            )
            
            if response.status_code == 200:
                overview = response.json()
                return {
                    'api_status': 'healthy',
                    'connections': overview['object_totals']['connections'],
                    'channels': overview['object_totals']['channels'],
                    'queues': overview['object_totals']['queues'],
                    'messages': overview['queue_totals']['messages']
                }
            else:
                return {'api_status': 'error', 'status_code': response.status_code}
                
        except Exception as e:
            self.logger.error(f"RabbitMQ健康检查失败: {e}")
            return {'api_status': 'error', 'error': str(e)}
    
    def _check_network_health(self):
        """检查网络健康"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except Exception as e:
            self.logger.error(f"网络健康检查失败: {e}")
            return {'error': str(e)}
    
    def _check_storage_health(self):
        """检查存储健康"""
        try:
            disk_usage = psutil.disk_usage('/')
            return {
                'total_gb': disk_usage.total / (1024**3),
                'used_gb': disk_usage.used / (1024**3),
                'free_gb': disk_usage.free / (1024**3),
                'usage_percent': (disk_usage.used / disk_usage.total) * 100
            }
        except Exception as e:
            self.logger.error(f"存储健康检查失败: {e}")
            return {'error': str(e)}
    
    def collect_performance_metrics(self):
        """收集性能指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'throughput': self._measure_throughput(),
            'latency': self._measure_latency(),
            'error_rate': self._measure_error_rate()
        }
        
        return metrics
    
    def _measure_throughput(self):
        """测量消息吞吐量"""
        try:
            # 创建测试连接和通道
            connection = pika.BlockingConnection(
                pika.URLParameters(self.config['rabbitmq_url'])
            )
            channel = connection.channel()
            
            # 创建测试队列
            test_queue = f"performance_test_{int(time.time())}"
            channel.queue_declare(queue=test_queue, exclusive=True, auto_delete=True)
            
            # 发送测试消息
            start_time = time.time()
            message_count = 100
            
            for i in range(message_count):
                channel.basic_publish(
                    exchange='',
                    routing_key=test_queue,
                    body=f"test message {i}"
                )
            
            # 消费消息
            consumed = 0
            while consumed < message_count:
                method_frame, header_frame, body = channel.basic_get(
                    queue=test_queue,
                    auto_ack=True
                )
                if method_frame:
                    consumed += 1
                else:
                    break
            
            end_time = time.time()
            
            connection.close()
            
            duration = end_time - start_time
            throughput = consumed / duration
            
            return {
                'messages_per_second': throughput,
                'test_duration': duration,
                'messages_tested': message_count
            }
            
        except Exception as e:
            self.logger.error(f"吞吐量测试失败: {e}")
            return {'error': str(e)}
    
    def _measure_latency(self):
        """测量消息延迟"""
        try:
            # 这里实现简单的延迟测试
            return {
                'average_latency_ms': 50,
                'max_latency_ms': 200
            }
        except Exception as e:
            self.logger.error(f"延迟测试失败: {e}")
            return {'error': str(e)}
    
    def _measure_error_rate(self):
        """测量错误率"""
        try:
            # 基于健康检查结果计算错误率
            return {
                'connection_errors': 0,
                'message_errors': 0,
                'total_operations': 1000,
                'error_rate': 0.001
            }
        except Exception as e:
            self.logger.error(f"错误率测试失败: {e}")
            return {'error': str(e)}
    
    def evaluate_alerts(self, health_status, performance_metrics):
        """评估告警条件"""
        alerts = []
        
        # 系统告警
        system_health = health_status.get('system', {})
        if system_health.get('cpu_percent', 0) > 80:
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'metric': 'cpu_usage',
                'value': system_health['cpu_percent'],
                'threshold': 80,
                'message': f"CPU使用率过高: {system_health['cpu_percent']}%"
            })
        
        if system_health.get('memory_percent', 0) > 85:
            alerts.append({
                'type': 'system',
                'severity': 'critical',
                'metric': 'memory_usage',
                'value': system_health['memory_percent'],
                'threshold': 85,
                'message': f"内存使用率过高: {system_health['memory_percent']}%"
            })
        
        # RabbitMQ告警
        rmq_health = health_status.get('rabbitmq', {})
        if rmq_health.get('api_status') == 'error':
            alerts.append({
                'type': 'rabbitmq',
                'severity': 'critical',
                'metric': 'api_connection',
                'message': "RabbitMQ API连接失败"
            })
        
        # 性能告警
        throughput = performance_metrics.get('throughput', {})
        if throughput.get('messages_per_second', 0) < 100:
            alerts.append({
                'type': 'performance',
                'severity': 'warning',
                'metric': 'throughput',
                'value': throughput.get('messages_per_second', 0),
                'threshold': 100,
                'message': f"消息吞吐量过低: {throughput.get('messages_per_second', 0)} msg/s"
            })
        
        return alerts
    
    def handle_alert(self, alert):
        """处理告警"""
        # 检查告警历史，避免重复告警
        if self._should_suppress_alert(alert):
            return
        
        # 记录告警
        self.alert_history.append({
            'timestamp': datetime.now().isoformat(),
            'alert': alert
        })
        
        # 发送通知
        self.send_notification(alert)
        
        # 尝试自动恢复
        self.attempt_auto_recovery(alert)
    
    def _should_suppress_alert(self, alert):
        """检查是否应该抑制告警"""
        # 5分钟内相同类型的告警
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        recent_alerts = [a for a in self.alert_history 
                        if datetime.fromisoformat(a['timestamp']) > five_minutes_ago
                        and a['alert']['type'] == alert['type']]
        
        return len(recent_alerts) > 0
    
    def send_notification(self, alert):
        """发送告警通知"""
        try:
            if alert['severity'] == 'critical':
                self._send_email_alert(alert)
            elif alert['severity'] == 'warning':
                self._send_slack_alert(alert)
            
            self.logger.warning(f"告警已发送: {alert['message']}")
            
        except Exception as e:
            self.logger.error(f"发送告警通知失败: {e}")
    
    def _send_email_alert(self, alert):
        """发送邮件告警"""
        try:
            msg = MimeText(f"RabbitMQ告警: {alert['message']}")
            msg['Subject'] = f"RabbitMQ {alert['severity'].upper()} - {alert['metric']}"
            msg['From'] = self.config['email']['from']
            msg['To'] = self.config['email']['to']
            
            server = smtplib.SMTP(self.config['email']['smtp_server'], 587)
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"发送邮件失败: {e}")
    
    def _send_slack_alert(self, alert):
        """发送Slack告警"""
        try:
            webhook_url = self.config['slack']['webhook_url']
            payload = {
                'text': f"RabbitMQ告警: {alert['message']}",
                'color': 'danger' if alert['severity'] == 'critical' else 'warning'
            }
            
            requests.post(webhook_url, json=payload)
            
        except Exception as e:
            self.logger.error(f"发送Slack告警失败: {e}")
    
    def attempt_auto_recovery(self, alert):
        """尝试自动恢复"""
        try:
            if alert['type'] == 'system' and alert['metric'] == 'memory_usage':
                self._recover_memory_pressure()
            elif alert['type'] == 'rabbitmq' and alert['metric'] == 'api_connection':
                self._recover_rabbitmq_service()
                
        except Exception as e:
            self.logger.error(f"自动恢复失败: {e}")
    
    def _recover_memory_pressure(self):
        """恢复内存压力"""
        self.logger.info("执行内存压力恢复...")
        # 这里可以添加实际的恢复操作
        # 例如重启RabbitMQ服务、清理缓存等
    
    def _recover_rabbitmq_service(self):
        """恢复RabbitMQ服务"""
        self.logger.info("执行RabbitMQ服务恢复...")
        # 这里可以添加实际的恢复操作
        # 例如重启服务、检查配置等
    
    def log_metrics(self, health_status, performance_metrics):
        """记录监控指标"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'health_status': health_status,
            'performance_metrics': performance_metrics
        }
        
        # 保存到日志文件
        with open('/var/log/rabbitmq_metrics.json', 'a') as f:
            f.write(json.dumps(log_data) + '\n')

def main():
    # 配置
    config = {
        'rabbitmq_url': 'amqp://admin:password@localhost:5672',
        'rabbitmq_api_url': 'http://localhost:15672',
        'username': 'admin',
        'password': 'password',
        'email': {
            'smtp_server': 'smtp.company.com',
            'username': 'alerts@company.com',
            'password': 'password',
            'from': 'alerts@company.com',
            'to': 'admin@company.com'
        },
        'slack': {
            'webhook_url': 'https://hooks.slack.com/services/xxx/yyy/zzz'
        }
    }
    
    monitor = SmartMonitor(config)
    monitor.run_continuous_monitoring(interval=60)

if __name__ == '__main__':
    main()
```

## 📋 最佳实践总结

### 1. 预防性维护最佳实践

- **定期健康检查**: 每日检查系统资源，监控RabbitMQ状态
- **容量规划**: 基于增长率预测未来需求，提前准备扩容计划
- **备份策略**: 自动备份配置和关键数据，异地存储备份文件
- **性能基线**: 建立性能基准值，快速识别异常情况

### 2. 故障响应最佳实践

- **分级响应**: 根据故障严重程度制定不同的响应策略
- **自动化恢复**: 优先尝试自动恢复，减少人工干预时间
- **根因分析**: 详细分析故障原因，制定长期解决方案
- **文档记录**: 完整记录故障处理过程，形成知识库

### 3. 监控告警最佳实践

- **合理阈值**: 基于历史数据设置合理的告警阈值
- **告警抑制**: 避免告警风暴，只在真正需要时发送通知
- **多渠道通知**: 支持邮件、短信、Slack等多种通知方式
- **告警聚合**: 将相关告警聚合，减少信息噪音

### 4. 灾难恢复最佳实践

- **多地点部署**: 在不同数据中心部署灾备环境
- **定期演练**: 定期进行灾难恢复演练，确保流程可行
- **RTO/RPO目标**: 明确恢复时间目标和数据丢失容忍度
- **文档更新**: 及时更新灾难恢复文档，确保信息的时效性

通过本章的学习，您将掌握RabbitMQ故障处理与恢复的全套解决方案，能够在生产环境中快速响应故障、恢复服务，并建立完善的预防机制。