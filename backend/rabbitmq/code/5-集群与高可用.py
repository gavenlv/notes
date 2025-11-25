#!/usr/bin/env python3
"""
RabbitMQ第5章：集群与高可用代码示例

这个文件包含了第5章"集群与高可用"的所有代码示例，包括：
- 集群状态监控
- 镜像队列配置
- 仲裁队列配置
- 故障转移处理
- 负载均衡
- 队列分片
- 客户端重连机制

使用方法：
python 5-集群与高可用.py [选项]

选项：
--demo <demo_name>    运行特定的演示
--host <hostname>     指定RabbitMQ服务器地址
--username <username>  指定用户名
--password <password>  指定密码
--help                显示帮助信息

可用演示：
cluster_monitor       集群状态监控
mirrored_queue        镜像队列配置
quorum_queue          仲裁队列配置
failover              故障转移处理
load_balancing        负载均衡
queue_sharding        队列分片
client_reconnect      客户端重连
all                   运行所有演示（默认）

示例：
python 5-集群与高可用.py --demo mirrored_queue
python 5-集群与高可用.py --host rabbitmq-server --username admin
"""

import pika
import json
import time
import threading
import random
import sys
import argparse
import hashlib
import requests
from datetime import datetime
import logging
from collections import defaultdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class RabbitMQConnection:
    """RabbitMQ连接管理类"""
    
    def __init__(self, host='localhost', port=5672, username='admin', password='password', virtual_host='/'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.connection = None
        self.channel = None
        
        self.connect()
    
    def connect(self):
        """连接到RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("Connection to RabbitMQ closed")
    
    def reconnect(self):
        """重新连接"""
        self.close()
        return self.connect()


class ClusterMonitor:
    """RabbitMQ集群监控类"""
    
    def __init__(self, mgmt_host='localhost', mgmt_port=15672, username='admin', password='password'):
        self.mgmt_host = mgmt_host
        self.mgmt_port = mgmt_port
        self.username = username
        self.password = password
        self.base_url = f"http://{mgmt_host}:{mgmt_port}/api/"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.history = []
        
        logger.info(f"Cluster monitor initialized for {mgmt_host}:{mgmt_port}")
    
    def get_overview(self):
        """获取集群概览信息"""
        try:
            response = self.session.get(self.base_url + "overview")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get overview: {e}")
            return None
    
    def get_nodes(self):
        """获取节点信息"""
        try:
            response = self.session.get(self.base_url + "nodes")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get nodes: {e}")
            return None
    
    def get_queues(self, vhost=None):
        """获取队列信息"""
        try:
            if vhost:
                response = self.session.get(self.base_url + f"queues/{vhost}")
            else:
                response = self.session.get(self.base_url + "queues")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get queues: {e}")
            return None
    
    def get_connections(self):
        """获取连接信息"""
        try:
            response = self.session.get(self.base_url + "connections")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get connections: {e}")
            return None
    
    def check_cluster_health(self):
        """检查集群健康状态"""
        try:
            overview = self.get_overview()
            nodes = self.get_nodes()
            queues = self.get_queues()
            
            if not overview or not nodes or not queues:
                logger.error("Failed to get cluster data")
                return None
            
            # 检查节点状态
            online_nodes = [node for node in nodes if node["running"]]
            total_nodes = len(nodes)
            nodes_health = len(online_nodes) / total_nodes * 100
            
            # 检查分区
            partitions = len(overview.get("partitions", []))
            
            # 检查内存使用
            total_mem_used = sum(node.get("mem_used", 0) for node in nodes)
            total_mem_limit = sum(node.get("mem_limit", 0) for node in nodes)
            mem_usage_percent = (total_mem_used / total_mem_limit) * 100 if total_mem_limit > 0 else 0
            
            # 检查队列状态
            total_messages = sum(queue.get("messages", 0) for queue in queues)
            total_unacked = sum(queue.get("messages_unacknowledged", 0) for queue in queues)
            
            # 检查连接状态
            connections = self.get_connections() or []
            total_connections = len(connections)
            
            # 计算健康分数
            health_score = (
                nodes_health * 0.3 +  # 节点健康度权重30%
                (100 if partitions == 0 else 0) * 0.2 +  # 无分区权重20%
                (100 if mem_usage_percent < 80 else max(0, 100 - mem_usage_percent)) * 0.2 +  # 内存健康权重20%
                (100 if total_unacked < total_messages * 0.1 else 0) * 0.3  # 消息确认健康权重30%
            )
            
            health_data = {
                "timestamp": datetime.now().isoformat(),
                "health_score": health_score,
                "nodes": {
                    "total": total_nodes,
                    "online": len(online_nodes),
                    "health_percent": nodes_health
                },
                "memory": {
                    "used": total_mem_used,
                    "limit": total_mem_limit,
                    "usage_percent": mem_usage_percent
                },
                "partitions": partitions,
                "messages": {
                    "total": total_messages,
                    "unacknowledged": total_unacked,
                    "unacked_percent": (total_unacked / total_messages * 100) if total_messages > 0 else 0
                },
                "connections": total_connections
            }
            
            self.history.append(health_data)
            
            # 保持历史记录在合理范围内
            if len(self.history) > 1000:
                self.history = self.history[-1000:]
            
            return health_data
            
        except Exception as e:
            logger.error(f"Error checking cluster health: {e}")
            return None
    
    def print_health_status(self, health_data):
        """打印健康状态"""
        if not health_data:
            print("Failed to get health data")
            return
        
        print("\n" + "=" * 60)
        print(f"Cluster Health Report - {health_data['timestamp']}")
        print("=" * 60)
        print(f"Health Score: {health_data['health_score']:.1f}/100")
        print(f"Nodes: {health_data['nodes']['online']}/{health_data['nodes']['total']} ({health_data['nodes']['health_percent']:.1f}%)")
        print(f"Memory Usage: {health_data['memory']['usage_percent']:.1f}% ({health_data['memory']['used']/1024/1024:.1f}MB/{health_data['memory']['limit']/1024/1024:.1f}MB)")
        print(f"Partitions: {health_data['partitions']}")
        print(f"Messages: {health_data['messages']['total']} total, {health_data['messages']['unacknowledged']} unacked ({health_data['messages']['unacked_percent']:.1f}%)")
        print(f"Connections: {health_data['connections']}")
        
        # 状态指示
        if health_data['health_score'] >= 90:
            status = "[EXCELLENT]"
        elif health_data['health_score'] >= 70:
            status = "[GOOD]"
        elif health_data['health_score'] >= 50:
            status = "[WARNING]"
        else:
            status = "[CRITICAL]"
        
        print(f"Overall Status: {status}")
    
    def monitor_loop(self, interval=30, iterations=10):
        """监控循环"""
        print(f"Starting cluster monitor with {interval}s interval for {iterations} iterations...")
        
        for i in range(iterations):
            health_data = self.check_cluster_health()
            if health_data:
                self.print_health_status(health_data)
            else:
                print("Failed to get cluster health data")
            
            if i < iterations - 1:  # 不是最后一次迭代
                print(f"\nWaiting {interval} seconds before next check...")
                time.sleep(interval)
        
        return self.history
    
    def get_health_trends(self):
        """获取健康趋势"""
        if len(self.history) < 2:
            return "Insufficient data for trend analysis"
        
        recent_scores = [entry["health_score"] for entry in self.history[-10:]]
        trend = "STABLE"
        
        if all(recent_scores[i] < recent_scores[i+1] for i in range(len(recent_scores)-1)):
            trend = "IMPROVING"
        elif all(recent_scores[i] > recent_scores[i+1] for i in range(len(recent_scores)-1)):
            trend = "DECLINING"
        
        avg_score = sum(recent_scores) / len(recent_scores)
        min_score = min(recent_scores)
        max_score = max(recent_scores)
        
        return {
            "trend": trend,
            "average_score": avg_score,
            "min_score": min_score,
            "max_score": max_score,
            "volatility": max_score - min_score
        }
    
    def export_history(self, filename):
        """导出历史数据"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.info(f"History exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to export history: {e}")
            return False


class MirroredQueueDemo:
    """镜像队列演示"""
    
    def __init__(self, host='localhost', username='admin', password='password'):
        self.connection = RabbitMQConnection(host=host, username=username, password=password)
        
        if not self.connection.connection:
            raise Exception("Failed to connect to RabbitMQ")
        
        self.channel = self.connection.channel
        logger.info("MirroredQueueDemo initialized")
    
    def setup_mirrored_queues(self):
        """设置镜像队列"""
        print("\n=== Setting up Mirrored Queues ===")
        
        # 创建交换机
        self.channel().exchange_declare(
            exchange='mirrored_demo',
            exchange_type='topic',
            durable=True
        )
        print("Exchange 'mirrored_demo' created")
        
        # 创建不同类型的镜像队列
        # 1. 在所有节点镜像
        self.channel().queue_declare(
            queue='ha_all_queue',
            durable=True,
            arguments={
                "x-ha-policy": "all"  # 在所有节点镜像
            }
        )
        self.channel().queue_bind(
            exchange='mirrored_demo',
            queue='ha_all_queue',
            routing_key='ha.all.*'
        )
        print("Queue 'ha_all_queue' created with x-ha-policy: all")
        
        # 2. 在指定数量节点镜像
        self.channel().queue_declare(
            queue='ha_exactly_queue',
            durable=True,
            arguments={
                "x-ha-policy": "exactly",
                "x-ha-params": 2  # 在2个节点镜像
            }
        )
        self.channel().queue_bind(
            exchange='mirrored_demo',
            queue='ha_exactly_queue',
            routing_key='ha.exactly.*'
        )
        print("Queue 'ha_exactly_queue' created with x-ha-policy: exactly (2 nodes)")
        
        # 3. 在指定节点镜像
        self.channel().queue_declare(
            queue='ha_nodes_queue',
            durable=True,
            arguments={
                "x-ha-policy": "nodes",
                "x-ha-nodes": ["rabbit@node1", "rabbit@node2"]  # 在指定节点镜像
            }
        )
        self.channel().queue_bind(
            exchange='mirrored_demo',
            queue='ha_nodes_queue',
            routing_key='ha.nodes.*'
        )
        print("Queue 'ha_nodes_queue' created with x-ha-policy: nodes (rabbit@node1, rabbit@node2)")
        
        print("\nMirrored queues configured successfully")
    
    def check_queue_status(self, queue_name):
        """检查队列状态"""
        try:
            # 这里应该调用管理API，但为了示例，我们使用passive声明
            method = self.channel().queue_declare(queue=queue_name, passive=True)
            
            # 在实际环境中，应该调用API获取更详细的信息
            print(f"Queue '{queue_name}': {method.method.message_count} messages")
            return True
        except pika.exceptions.ChannelClosedByBroker as e:
            print(f"Queue '{queue_name}' not found: {e}")
            return False
    
    def produce_messages(self):
        """生产消息到镜像队列"""
        print("\n=== Producing Messages ===")
        
        messages = [
            ("ha.all.critical", "Critical system message - should be on all nodes"),
            ("ha.exactly.warning", "Warning message - should be on exactly 2 nodes"),
            ("ha.nodes.info", "Info message - should be on specific nodes"),
            ("ha.all.critical", "Another critical message"),
            ("ha.exactly.warning", "Another warning message"),
            ("ha.nodes.info", "Another info message")
        ]
        
        for routing_key, message in messages:
            self.channel().basic_publish(
                exchange='mirrored_demo',
                routing_key=routing_key,
                body=message.encode('utf-8'),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                    timestamp=time.time()
                )
            )
            print(f"Published to {routing_key}: {message}")
    
    def consume_messages(self, queue_name, max_messages=5):
        """消费消息"""
        print(f"\n=== Consuming from '{queue_name}' ===")
        consumed = 0
        
        def callback(ch, method, properties, body):
            nonlocal consumed
            consumed += 1
            print(f"Received from {queue_name}: {body.decode()}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            if consumed >= max_messages:
                ch.stop_consuming()
        
        self.channel().basic_qos(prefetch_count=1)
        self.channel().basic_consume(
            queue=queue_name,
            on_message_callback=callback
        )
        
        try:
            self.channel().start_consuming()
        except KeyboardInterrupt:
            self.channel().stop_consuming()
        
        print(f"Consumed {consumed} messages from '{queue_name}'")
        return consumed
    
    def run_demo(self):
        """运行完整的镜像队列演示"""
        try:
            # 1. 设置镜像队列
            self.setup_mirrored_queues()
            
            # 2. 生产消息
            self.produce_messages()
            
            # 3. 检查队列状态
            print("\n=== Checking Queue Status ===")
            for queue in ["ha_all_queue", "ha_exactly_queue", "ha_nodes_queue"]:
                self.check_queue_status(queue)
            
            # 4. 消费消息
            for queue in ["ha_all_queue", "ha_exactly_queue", "ha_nodes_queue"]:
                self.consume_messages(queue, max_messages=2)
            
            print("\n=== Mirrored Queue Demo Completed ===")
            
        except Exception as e:
            logger.error(f"Error in MirroredQueueDemo: {e}")
        finally:
            self.connection.close()
    
    def cleanup(self):
        """清理资源"""
        if self.connection and self.connection.connection:
            # 删除测试队列和交换机
            queues = ["ha_all_queue", "ha_exactly_queue", "ha_nodes_queue"]
            exchanges = ["mirrored_demo"]
            
            for queue in queues:
                try:
                    self.channel().queue_delete(queue=queue)
                    print(f"Deleted queue: {queue}")
                except Exception:
                    pass
            
            for exchange in exchanges:
                try:
                    self.channel().exchange_delete(exchange=exchange)
                    print(f"Deleted exchange: {exchange}")
                except Exception:
                    pass
            
            self.connection.close()


class QuorumQueueDemo:
    """仲裁队列演示"""
    
    def __init__(self, host='localhost', username='admin', password='password'):
        self.connection = RabbitMQConnection(host=host, username=username, password=password)
        
        if not self.connection.connection:
            raise Exception("Failed to connect to RabbitMQ")
        
        self.channel = self.connection.channel
        logger.info("QuorumQueueDemo initialized")
    
    def setup_quorum_queues(self):
        """设置仲裁队列"""
        print("\n=== Setting up Quorum Queues ===")
        
        # 创建交换机
        self.channel().exchange_declare(
            exchange='quorum_demo',
            exchange_type='topic',
            durable=True
        )
        print("Exchange 'quorum_demo' created")
        
        # 1. 基本仲裁队列
        self.channel().queue_declare(
            queue='basic_quorum_queue',
            durable=True,
            arguments={
                "x-queue-type": "quorum"  # 声明为仲裁队列
            }
        )
        self.channel().queue_bind(
            exchange='quorum_demo',
            queue='basic_quorum_queue',
            routing_key='quorum.basic.*'
        )
        print("Queue 'basic_quorum_queue' created as quorum queue")
        
        # 2. 高级仲裁队列
        self.channel().queue_declare(
            queue='advanced_quorum_queue',
            durable=True,
            arguments={
                "x-queue-type": "quorum",
                "x-delivery-limit": 10,           # 投递限制
                "x-max-length": 10000,            # 最大消息数
                "x-max-length-bytes": 1000000000,  # 最大字节数
                "x-overflow": "drop-head",        # 溢出策略
                "x-quorum-initial-group-size": 3, # 初始副本数
                "x-dead-letter-exchange": "",      # 死信交换机
                "x-dead-letter-routing-key": "dlq_quorum"  # 死信路由键
            }
        )
        self.channel().queue_bind(
            exchange='quorum_demo',
            queue='advanced_quorum_queue',
            routing_key='quorum.advanced.*'
        )
        print("Queue 'advanced_quorum_queue' created with advanced settings")
        
        # 3. 死信队列
        self.channel().queue_declare(
            queue='dlq_quorum',
            durable=True,
            arguments={
                "x-queue-type": "quorum"
            }
        )
        print("Queue 'dlq_quorum' created as dead letter queue")
        
        print("\nQuorum queues configured successfully")
    
    def produce_messages(self):
        """生产消息到仲裁队列"""
        print("\n=== Producing Messages ===")
        
        messages = [
            ("quorum.basic.info", "Basic info message"),
            ("quorum.basic.warning", "Basic warning message"),
            ("quorum.advanced.critical", "Advanced critical message"),
            ("quorum.advanced.error", "Advanced error message"),
        ]
        
        for routing_key, message in messages:
            self.channel().basic_publish(
                exchange='quorum_demo',
                routing_key=routing_key,
                body=message.encode('utf-8'),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                    timestamp=time.time()
                )
            )
            print(f"Published to {routing_key}: {message}")
    
    def test_delivery_limit(self):
        """测试投递限制"""
        print("\n=== Testing Delivery Limit ===")
        
        # 发送消息到高级仲裁队列
        self.channel().basic_publish(
            exchange='quorum_demo',
            routing_key='quorum.advanced.test',
            body="Test message for delivery limit".encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )
        
        # 模拟多次接收并拒绝消息
        def callback(ch, method, properties, body):
            print(f"Received message (attempt {method.redelivered + 1}): {body.decode()}")
            # 拒绝消息，重新入队
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        self.channel().basic_consume(
            queue='advanced_quorum_queue',
            on_message_callback=callback
        )
        
        print("Starting consumer to test delivery limit (will stop after a few attempts)...")
        
        # 运行一段时间后停止
        def stop_consumer():
            time.sleep(5)
            self.channel().stop_consuming()
        
        threading.Thread(target=stop_consumer, daemon=True).start()
        
        try:
            self.channel().start_consuming()
        except KeyboardInterrupt:
            self.channel().stop_consuming()
        
        print("Delivery limit test completed")
    
    def consume_messages(self, queue_name, max_messages=5):
        """消费消息"""
        print(f"\n=== Consuming from '{queue_name}' ===")
        consumed = 0
        
        def callback(ch, method, properties, body):
            nonlocal consumed
            consumed += 1
            print(f"Received from {queue_name}: {body.decode()}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            if consumed >= max_messages:
                ch.stop_consuming()
        
        self.channel().basic_qos(prefetch_count=1)
        self.channel().basic_consume(
            queue=queue_name,
            on_message_callback=callback
        )
        
        try:
            self.channel().start_consuming()
        except KeyboardInterrupt:
            self.channel().stop_consuming()
        
        print(f"Consumed {consumed} messages from '{queue_name}'")
        return consumed
    
    def run_demo(self):
        """运行完整的仲裁队列演示"""
        try:
            # 1. 设置仲裁队列
            self.setup_quorum_queues()
            
            # 2. 生产消息
            self.produce_messages()
            
            # 3. 测试投递限制
            self.test_delivery_limit()
            
            # 4. 消费消息
            self.consume_messages("basic_quorum_queue", max_messages=2)
            self.consume_messages("advanced_quorum_queue", max_messages=2)
            
            # 5. 检查死信队列
            self.consume_messages("dlq_quorum", max_messages=2)
            
            print("\n=== Quorum Queue Demo Completed ===")
            
        except Exception as e:
            logger.error(f"Error in QuorumQueueDemo: {e}")
        finally:
            self.connection.close()
    
    def cleanup(self):
        """清理资源"""
        if self.connection and self.connection.connection:
            # 删除测试队列和交换机
            queues = ["basic_quorum_queue", "advanced_quorum_queue", "dlq_quorum"]
            exchanges = ["quorum_demo"]
            
            for queue in queues:
                try:
                    self.channel().queue_delete(queue=queue)
                    print(f"Deleted queue: {queue}")
                except Exception:
                    pass
            
            for exchange in exchanges:
                try:
                    self.channel().exchange_delete(exchange=exchange)
                    print(f"Deleted exchange: {exchange}")
                except Exception:
                    pass
            
            self.connection.close()


class FailoverHandler:
    """故障转移处理器"""
    
    def __init__(self, hosts, username='admin', password='password'):
        self.hosts = hosts
        self.username = username
        self.password = password
        self.current_host_index = 0
        self.connection = None
        self.channel = None
        self.is_connected = False
        self.reconnect_thread = None
        self.stop_flag = False
        self.connection_callbacks = []
        
        # 初始连接
        self._connect()
        logger.info("FailoverHandler initialized")
    
    def _connect(self):
        """连接到RabbitMQ集群"""
        max_attempts = len(self.hosts)
        attempts = 0
        
        while attempts < max_attempts and not self.stop_flag:
            try:
                if self.connection and self.connection.is_open:
                    self.connection.close()
                
                host = self.hosts[self.current_host_index]
                logger.info(f"Connecting to RabbitMQ at {host}...")
                
                credentials = pika.PlainCredentials(self.username, self.password)
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host,
                        credentials=credentials,
                        heartbeat=600,  # 心跳间隔
                        blocked_connection_timeout=300,  # 阻塞连接超时
                    )
                )
                self.channel = self.connection.channel()
                
                self.is_connected = True
                logger.info(f"Connected to RabbitMQ at {host}")
                
                # 通知连接回调
                for callback in self.connection_callbacks:
                    try:
                        callback(True, host)
                    except Exception as e:
                        logger.error(f"Connection callback error: {e}")
                
                return True
                
            except Exception as e:
                logger.warning(f"Failed to connect to {host}: {e}")
                
                # 尝试下一个节点
                self.current_host_index = (self.current_host_index + 1) % len(self.hosts)
                attempts += 1
                time.sleep(2)
        
        logger.error("Failed to connect to any RabbitMQ node")
        
        # 通知连接回调
        for callback in self.connection_callbacks:
            try:
                callback(False, None)
            except Exception as e:
                logger.error(f"Connection callback error: {e}")
        
        return False
    
    def _ensure_connected(self):
        """确保连接有效"""
        if not self.is_connected or not self.connection or not self.connection.is_open:
            self.is_connected = False
            return self._connect()
        return self.is_connected
    
    def _monitor_connection(self):
        """监控连接状态并自动重连"""
        while not self.stop_flag:
            try:
                if self.is_connected and self.connection:
                    try:
                        # 测试连接
                        self.connection.process_data_events(time_limit=1)
                    except pika.exceptions.ConnectionClosed:
                        logger.warning("Connection lost, attempting to reconnect...")
                        self.is_connected = False
                    except pika.exceptions.AMQPConnectionError:
                        logger.warning("Connection error, attempting to reconnect...")
                        self.is_connected = False
                
                if not self.is_connected:
                    self._connect()
                
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in connection monitor: {e}")
                time.sleep(10)
    
    def add_connection_callback(self, callback):
        """添加连接状态回调"""
        self.connection_callbacks.append(callback)
    
    def start_monitoring(self):
        """启动连接监控"""
        if self.reconnect_thread is None or not self.reconnect_thread.is_alive():
            self.stop_flag = False
            self.reconnect_thread = threading.Thread(target=self._monitor_connection)
            self.reconnect_thread.daemon = True
            self.reconnect_thread.start()
            logger.info("Connection monitoring started")
    
    def stop_monitoring(self):
        """停止连接监控"""
        self.stop_flag = True
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            self.reconnect_thread.join(timeout=5)
        logger.info("Connection monitoring stopped")
    
    def publish_message(self, exchange, routing_key, message):
        """发布消息（带有自动重连）"""
        if not self._ensure_connected():
            return False
        
        try:
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message.encode('utf-8'),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                    timestamp=time.time()
                )
            )
            logger.debug(f"Published to {self.hosts[self.current_host_index]}: {message}")
            return True
        except (pika.exceptions.ConnectionClosed, pika.exceptions.AMQPConnectionError):
            logger.warning("Connection lost during publish, marking as disconnected")
            self.is_connected = False
            return False
    
    def consume_messages(self, queue_name, callback):
        """消费消息（带有自动重连）"""
        if not self._ensure_connected():
            return False
        
        try:
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            logger.debug(f"Set up consumer for {queue_name}")
            return True
        except (pika.exceptions.ConnectionClosed, pika.exceptions.AMQPConnectionError):
            logger.warning("Connection lost during consume setup, marking as disconnected")
            self.is_connected = False
            return False
    
    def start_consuming(self):
        """开始消费消息"""
        if self._ensure_connected():
            try:
                self.channel.start_consuming()
            except (pika.exceptions.ConnectionClosed, pika.exceptions.AMQPConnectionError):
                logger.warning("Connection lost during consume, marking as disconnected")
                self.is_connected = False
    
    def stop_consuming(self):
        """停止消费消息"""
        if self.channel:
            try:
                self.channel.stop_consuming()
            except Exception as e:
                logger.error(f"Error stopping consuming: {e}")
    
    def get_current_host(self):
        """获取当前连接的主机"""
        if self.is_connected:
            return self.hosts[self.current_host_index]
        return None
    
    def close(self):
        """关闭连接"""
        self.stop_monitoring()
        
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
            except Exception:
                pass
        
        logger.info("Connection closed")


class FailoverDemo:
    """故障转移演示"""
    
    def __init__(self, hosts, username='admin', password='password'):
        self.failover_handler = FailoverHandler(hosts, username, password)
        self.failover_handler.start_monitoring()
        logger.info("FailoverDemo initialized")
    
    def connection_state_callback(self, connected, host):
        """连接状态回调"""
        if connected:
            print(f"✓ Connected to {host}")
        else:
            print("✗ Disconnected from RabbitMQ")
    
    def run_demo(self):
        """运行故障转移演示"""
        print("\n=== Failover Demo ===")
        print(f"Trying to connect to hosts: {', '.join(self.failover_handler.hosts)}")
        
        # 添加连接状态回调
        self.failover_handler.add_connection_callback(self.connection_state_callback)
        
        # 等待连接
        if not self.failover_handler._ensure_connected():
            print("Failed to establish initial connection")
            return
        
        current_host = self.failover_handler.get_current_host()
        print(f"Initial connection established with {current_host}")
        
        # 创建队列
        try:
            self.failover_handler.channel.queue_declare(queue='failover_demo', durable=True)
            print("Queue 'failover_demo' created")
        except Exception as e:
            print(f"Failed to create queue: {e}")
            return
        
        # 发布消息
        print("\n=== Publishing Messages ===")
        messages = [
            "Message 1: System is running",
            "Message 2: Processing requests",
            "Message 3: Maintenance scheduled",
        ]
        
        for message in messages:
            success = self.failover_handler.publish_message("", "failover_demo", message)
            if success:
                print(f"Published: {message}")
            else:
                print(f"Failed to publish: {message}")
            time.sleep(1)
        
        # 设置消费者
        message_count = {"count": 0}
        
        def message_callback(ch, method, properties, body):
            message_count["count"] += 1
            host = self.failover_handler.get_current_host() or "Unknown"
            print(f"[{host}] Received #{message_count['count']}: {body.decode()}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.failover_handler.consume_messages("failover_demo", message_callback)
        
        # 启动消费者线程
        consumer_thread = threading.Thread(
            target=self.failover_handler.start_consuming,
            daemon=True
        )
        consumer_thread.start()
        
        # 运行一段时间
        print("\n=== Consuming Messages ===")
        print("Consumer is running... (Wait for messages or simulate failover)")
        print("You can stop the current RabbitMQ node to test failover")
        print("Press Ctrl+C to stop the demo")
        
        try:
            # 持续发送消息
            for i in range(20, 0, -1):
                print(f"\nDemo will stop in {i} seconds (or press Ctrl+C)")
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        # 停止消费
        try:
            self.failover_handler.stop_consuming()
            consumer_thread.join(timeout=2)
        except Exception:
            pass
        
        print("\n=== Failover Demo Completed ===")
        print(f"Total messages received: {message_count['count']}")
        
        # 关闭连接
        self.failover_handler.close()


class ClientLoadBalancer:
    """客户端负载均衡器"""
    
    def __init__(self, hosts, username='admin', password='password'):
        self.hosts = hosts
        self.username = username
        self.password = password
        self.connections = {}
        self.channels = {}
        self.round_robin_index = 0
        
        # 初始化所有连接
        for host in hosts:
            self._create_connection(host)
        
        logger.info("ClientLoadBalancer initialized")
    
    def _create_connection(self, host):
        """创建连接"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host,
                    credentials=credentials,
                    heartbeat=600
                )
            )
            
            self.connections[host] = connection
            self.channels[host] = connection.channel()
            logger.info(f"Connected to {host}")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to {host}: {e}")
            return False
    
    def get_random_connection(self):
        """获取随机连接"""
        available_hosts = list(self.connections.keys())
        if not available_hosts:
            return None, None
        
        host = random.choice(available_hosts)
        return host, self.connections[host]
    
    def get_round_robin_connection(self):
        """获取轮询连接"""
        available_hosts = list(self.connections.keys())
        if not available_hosts:
            return None, None
        
        host = available_hosts[self.round_robin_index % len(available_hosts)]
        self.round_robin_index += 1
        return host, self.connections[host]
    
    def publish_with_load_balance(self, exchange, routing_key, message, strategy="random"):
        """使用负载均衡发布消息"""
        if strategy == "random":
            host, connection = self.get_random_connection()
        elif strategy == "round_robin":
            host, connection = self.get_round_robin_connection()
        else:
            host, connection = self.get_random_connection()
        
        if not connection:
            logger.error("No available connections")
            return False
        
        try:
            channel = self.channels[host]
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message.encode('utf-8'),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                )
            )
            logger.info(f"Sent to {host}: {message}")
            return True
        except Exception as e:
            logger.warning(f"Failed to publish to {host}: {e}")
            # 尝试重新连接
            self._create_connection(host)
            return False
    
    def close_all(self):
        """关闭所有连接"""
        for host, connection in self.connections.items():
            try:
                connection.close()
                logger.info(f"Closed connection to {host}")
            except Exception as e:
                logger.error(f"Error closing connection to {host}: {e}")


class QueueSharding:
    """队列分片"""
    
    def __init__(self, host='localhost', shard_count=3, username='admin', password='password'):
        self.connection = RabbitMQConnection(host=host, username=username, password=password)
        
        if not self.connection.connection:
            raise Exception("Failed to connect to RabbitMQ")
        
        self.channel = self.connection.channel
        self.shard_count = shard_count
        
        # 创建分片队列
        self._create_sharded_queues()
        logger.info(f"QueueSharding initialized with {shard_count} shards")
    
    def _create_sharded_queues(self):
        """创建分片队列"""
        for i in range(self.shard_count):
            queue_name = f"sharded_queue_{i}"
            self.channel().queue_declare(queue=queue_name, durable=True)
            logger.debug(f"Created shard queue: {queue_name}")
        
        logger.info(f"Created {self.shard_count} shard queues")
    
    def _get_shard_number(self, key):
        """根据键获取分片编号"""
        # 使用哈希算法确定分片
        hash_obj = hashlib.md5(key.encode())
        return int(hash_obj.hexdigest(), 16) % self.shard_count
    
    def publish_to_shard(self, message, key=None):
        """发布消息到特定分片"""
        if key is None:
            # 如果没有键，随机选择分片
            shard_num = random.randint(0, self.shard_count - 1)
        else:
            # 根据键确定分片
            shard_num = self._get_shard_number(key)
        
        queue_name = f"sharded_queue_{shard_num}"
        
        self.channel().basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message.encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 持久化
            )
        )
        
        logger.info(f"Sent to shard {shard_num} ({queue_name}): {message}")
        return shard_num
    
    def create_shard_consumer(self, shard_num, callback):
        """创建特定分片的消费者"""
        queue_name = f"sharded_queue_{shard_num}"
        
        self.channel().basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False
        )
        
        logger.debug(f"Consumer for shard {shard_num} started")
        return queue_name
    
    def consume_all_shards(self, callback):
        """消费所有分片的消息"""
        for i in range(self.shard_count):
            self.create_shard_consumer(i, callback)
        
        logger.info(f"Consuming from all {self.shard_count} shards")
        self.channel().start_consuming()
    
    def close(self):
        """关闭连接"""
        self.connection.close()


class DemoRunner:
    """演示运行器"""
    
    def __init__(self, host='localhost', username='admin', password='password'):
        self.host = host
        self.username = username
        self.password = password
        logger.info(f"DemoRunner initialized with host={host}")
    
    def run_cluster_monitor_demo(self):
        """运行集群监控演示"""
        print("\n" + "=" * 60)
        print("RabbitMQ Cluster Monitor Demo")
        print("=" * 60)
        
        # 注意：这需要RabbitMQ管理API可用
        monitor = ClusterMonitor(
            mgmt_host=self.host,
            mgmt_port=15672,
            username=self.username,
            password=self.password
        )
        
        # 运行监控
        history = monitor.monitor_loop(interval=5, iterations=3)
        
        if history:
            # 获取健康趋势
            trends = monitor.get_health_trends()
            print("\nHealth Trends:")
            print(f"  Trend: {trends['trend']}")
            print(f"  Average Score: {trends['average_score']:.1f}")
            print(f"  Min/Max Score: {trends['min_score']:.1f}/{trends['max_score']:.1f}")
            print(f"  Volatility: {trends['volatility']:.1f}")
            
            # 导出历史数据
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cluster_health_{timestamp}.json"
            monitor.export_history(filename)
        
        print("\nCluster Monitor Demo Completed\n")
    
    def run_mirrored_queue_demo(self):
        """运行镜像队列演示"""
        print("\n" + "=" * 60)
        print("RabbitMQ Mirrored Queue Demo")
        print("=" * 60)
        
        demo = MirroredQueueDemo(host=self.host, username=self.username, password=self.password)
        demo.run_demo()
        demo.cleanup()
        
        print("\nMirrored Queue Demo Completed\n")
    
    def run_quorum_queue_demo(self):
        """运行仲裁队列演示"""
        print("\n" + "=" * 60)
        print("RabbitMQ Quorum Queue Demo")
        print("=" * 60)
        
        demo = QuorumQueueDemo(host=self.host, username=self.username, password=self.password)
        demo.run_demo()
        demo.cleanup()
        
        print("\nQuorum Queue Demo Completed\n")
    
    def run_failover_demo(self):
        """运行故障转移演示"""
        print("\n" + "=" * 60)
        print("RabbitMQ Failover Demo")
        print("=" * 60)
        
        # 注意：在实际环境中，这里应该提供多个不同的主机地址
        hosts = [self.host] * 3  # 在示例中使用相同主机，实际应该不同
        demo = FailoverDemo(hosts=hosts, username=self.username, password=self.password)
        demo.run_demo()
        
        print("\nFailover Demo Completed\n")
    
    def run_load_balancing_demo(self):
        """运行负载均衡演示"""
        print("\n" + "=" * 60)
        print("RabbitMQ Load Balancing Demo")
        print("=" * 60)
        
        # 注意：在实际环境中，这里应该提供多个不同的主机地址
        hosts = [self.host] * 3  # 在示例中使用相同主机，实际应该不同
        load_balancer = ClientLoadBalancer(hosts=hosts, username=self.username, password=self.password)
        
        try:
            # 发布消息到不同分片
            print(" [*] Publishing messages with random strategy")
            for i in range(10):
                message = f"Message {i}"
                load_balancer.publish_with_load_balance("", "load_balance_test", message, "random")
                time.sleep(0.1)
            
            # 发布消息到不同分片
            print("\n [*] Publishing messages with round-robin strategy")
            for i in range(10):
                message = f"Message {i}"
                load_balancer.publish_with_load_balance("", "load_balance_test", message, "round_robin")
                time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\n [*] Shutting down")
        finally:
            load_balancer.close_all()
        
        print("\nLoad Balancing Demo Completed\n")
    
    def run_queue_sharding_demo(self):
        """运行队列分片演示"""
        print("\n" + "=" * 60)
        print("RabbitMQ Queue Sharding Demo")
        print("=" * 60)
        
        sharding = QueueSharding(host=self.host, shard_count=3, username=self.username, password=self.password)
        
        def message_callback(ch, method, properties, body):
            queue_name = method.routing_key
            shard_num = queue_name.split('_')[-1]
            print(f" [x] Received from shard {shard_num}: {body.decode()}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        try:
            # 发布消息到不同分片
            users = ["user1", "user2", "user3", "user4", "user5"]
            for user in users:
                message = f"Order data for {user}"
                sharding.publish_to_shard(message, key=user)
            
            # 消费所有分片的消息
            print("\n [*] Consuming from all shards")
            
            # 启动消费者线程
            consumer_thread = threading.Thread(
                target=sharding.consume_all_shards,
                args=(message_callback,),
                daemon=True
            )
            consumer_thread.start()
            
            # 运行一段时间
            time.sleep(5)
            
            # 停止消费
            try:
                sharding.connection.channel.stop_consuming()
                consumer_thread.join(timeout=2)
            except Exception:
                pass
            
        except KeyboardInterrupt:
            print("\n [*] Shutting down")
        finally:
            sharding.close()
        
        print("\nQueue Sharding Demo Completed\n")
    
    def run_all_demos(self):
        """运行所有演示"""
        print("\n" + "=" * 80)
        print("Running All RabbitMQ Cluster & High Availability Demos")
        print("=" * 80)
        
        demos = [
            ("Cluster Monitor", self.run_cluster_monitor_demo),
            ("Mirrored Queue", self.run_mirrored_queue_demo),
            ("Quorum Queue", self.run_quorum_queue_demo),
            ("Failover", self.run_failover_demo),
            ("Load Balancing", self.run_load_balancing_demo),
            ("Queue Sharding", self.run_queue_sharding_demo)
        ]
        
        for demo_name, demo_func in demos:
            try:
                demo_func()
                print(f"✓ {demo_name} Demo completed successfully")
            except Exception as e:
                print(f"✗ {demo_name} Demo failed: {e}")
            
            print("\n" + "-" * 80)
        
        print("\nAll demos completed!")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='RabbitMQ第5章：集群与高可用演示')
    parser.add_argument('--demo', type=str, default='all',
                        choices=['cluster_monitor', 'mirrored_queue', 'quorum_queue', 
                                'failover', 'load_balancing', 'queue_sharding', 'all'],
                        help='要运行的演示名称')
    parser.add_argument('--host', type=str, default='localhost',
                        help='RabbitMQ服务器地址')
    parser.add_argument('--username', type=str, default='admin',
                        help='RabbitMQ用户名')
    parser.add_argument('--password', type=str, default='password',
                        help='RabbitMQ密码')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("RabbitMQ第5章：集群与高可用")
    print("=" * 80)
    
    # 创建演示运行器
    runner = DemoRunner(
        host=args.host,
        username=args.username,
        password=args.password
    )
    
    try:
        if args.demo == 'all':
            runner.run_all_demos()
        elif args.demo == 'cluster_monitor':
            runner.run_cluster_monitor_demo()
        elif args.demo == 'mirrored_queue':
            runner.run_mirrored_queue_demo()
        elif args.demo == 'quorum_queue':
            runner.run_quorum_queue_demo()
        elif args.demo == 'failover':
            runner.run_failover_demo()
        elif args.demo == 'load_balancing':
            runner.run_load_balancing_demo()
        elif args.demo == 'queue_sharding':
            runner.run_queue_sharding_demo()
    except KeyboardInterrupt:
        print("\n[*] Demonstrations interrupted")
    except Exception as e:
        print(f"\n[!] Error running demonstrations: {e}")
    
    print("\n[*] Demonstrations finished")


if __name__ == "__main__":
    main()