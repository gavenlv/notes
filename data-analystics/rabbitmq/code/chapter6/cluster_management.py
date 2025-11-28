#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ集群管理与配置演示

这个模块展示了如何在Python中管理RabbitMQ集群：
- 集群节点连接管理
- 镜像队列配置
- 负载均衡策略
- 故障检测与恢复
- 性能监控
"""

import pika
import time
import json
import threading
from datetime import datetime
from typing import List, Dict, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClusterNode:
    """集群节点信息类"""
    
    def __init__(self, hostname: str, port: int = 5672, is_master: bool = False):
        self.hostname = hostname
        self.port = port
        self.is_master = is_master
        self.connection = None
        self.channel = None
        self.is_connected = False
        self.last_heartbeat = None
        self.message_count = 0
        self.consumer_count = 0
    
    def connect(self, username: str = 'admin', password: str = 'admin123') -> bool:
        """连接节点"""
        try:
            credentials = pika.PlainCredentials(username, password)
            connection_params = pika.ConnectionParameters(
                host=self.hostname,
                port=self.port,
                credentials=credentials,
                heartbeat=30,
                connection_attempts=3,
                retry_delay=5
            )
            
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            self.is_connected = True
            self.last_heartbeat = datetime.now()
            
            logger.info(f"✅ 成功连接到节点: {self.hostname}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 连接到节点失败 {self.hostname}: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """断开节点连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            self.is_connected = False
            logger.info(f"🔌 断开节点连接: {self.hostname}")
    
    def get_queue_stats(self, queue_name: str) -> Dict:
        """获取队列统计信息"""
        if not self.is_connected:
            return {}
        
        try:
            # 声明队列以获取统计信息
            result = self.channel.queue_declare(queue=queue_name, passive=True)
            
            stats = {
                'queue': queue_name,
                'messages': result.method.message_count,
                'consumers': result.method.consumer_count,
                'node': self.hostname,
                'timestamp': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 获取队列统计失败 {self.hostname}: {e}")
            return {}
    
    def create_mirrored_queue(self, queue_name: str, ha_policy: str = 'all') -> bool:
        """创建镜像队列"""
        if not self.is_connected:
            return False
        
        try:
            arguments = {
                'x-ha-policy': ha_policy,
                'x-ha-sync-batch-size': 100
            }
            
            self.channel.queue_declare(
                queue=queue_name,
                durable=True,
                arguments=arguments
            )
            
            logger.info(f"✅ 镜像队列创建成功: {queue_name} on {self.hostname}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建镜像队列失败 {self.hostname}: {e}")
            return False

class RabbitMQClusterManager:
    """RabbitMQ集群管理器"""
    
    def __init__(self, nodes: List[str], cluster_name: str = "rabbitmq-cluster"):
        self.nodes = [ClusterNode(node) for node in nodes]
        self.cluster_name = cluster_name
        self.mirror_queues = []
        self.connections = {}
        self.monitoring_active = False
        self.heartbeat_interval = 30
        
    def connect_all_nodes(self, username: str = 'admin', password: str = 'admin123') -> Dict[str, bool]:
        """连接到所有集群节点"""
        results = {}
        threads = []
        
        def connect_node(node):
            results[node.hostname] = node.connect(username, password)
        
        # 并行连接所有节点
        for node in self.nodes:
            thread = threading.Thread(target=connect_node, args=(node,))
            thread.start()
            threads.append(thread)
        
        # 等待所有连接完成
        for thread in threads:
            thread.join()
        
        successful_nodes = sum(results.values())
        logger.info(f"📊 集群连接结果: {successful_nodes}/{len(self.nodes)} 节点连接成功")
        
        return results
    
    def setup_cluster(self, queue_name: str, ha_policy: str = 'all') -> bool:
        """设置集群镜像队列"""
        if not self.nodes:
            logger.error("❌ 没有可用的集群节点")
            return False
        
        # 在第一个节点上创建镜像队列
        master_node = self.nodes[0]
        if master_node.is_connected:
            success = master_node.create_mirrored_queue(queue_name, ha_policy)
            if success:
                self.mirror_queues.append(queue_name)
                logger.info(f"✅ 集群镜像队列设置完成: {queue_name}")
            return success
        
        return False
    
    def publish_to_cluster(self, queue_name: str, messages: List[str], 
                          exchange: str = '') -> bool:
        """向集群发布消息"""
        # 选择当前可用的节点
        available_nodes = [node for node in self.nodes if node.is_connected]
        if not available_nodes:
            logger.error("❌ 没有可用的集群节点")
            return False
        
        # 使用主节点发布消息
        master_node = available_nodes[0]
        
        try:
            for i, message in enumerate(messages):
                properties = pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                    message_id=f"msg-{i}",
                    timestamp=int(time.time())
                )
                
                master_node.channel.basic_publish(
                    exchange=exchange,
                    routing_key=queue_name,
                    body=json.dumps(message),
                    properties=properties
                )
                
                master_node.message_count += 1
                logger.info(f"📤 发布消息到集群: {message}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 发布消息到集群失败: {e}")
            return False
    
    def consume_from_cluster(self, queue_name: str, max_messages: int = 10):
        """从集群消费消息"""
        available_nodes = [node for node in self.nodes if node.is_connected]
        if not available_nodes:
            logger.error("❌ 没有可用的集群节点")
            return
        
        # 使用消费者节点
        consumer_node = available_nodes[-1]  # 选择最后一个可用节点
        
        def callback(ch, method, properties, body):
            try:
                message_data = json.loads(body.decode())
                logger.info(f"📥 消费消息: {message_data}")
                
                # 模拟消息处理
                time.sleep(0.1)
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logger.error(f"❌ 处理消息失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # 设置QOS和手动确认
        consumer_node.channel.basic_qos(prefetch_count=1)
        
        # 开始消费
        consumer_node.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False
        )
        
        logger.info(f"👥 开始从集群消费消息: {queue_name}")
        
        try:
            # 消费指定数量的消息
            message_count = 0
            while message_count < max_messages:
                consumer_node.channel.connection.process_data_events(time_limit=1)
                if not consumer_node.channel._consumer_tags:
                    break
                message_count += 1
            
        except KeyboardInterrupt:
            logger.info("⏹️  用户中断消费")
        finally:
            consumer_node.channel.stop_consuming()
    
    def get_cluster_status(self) -> Dict:
        """获取集群状态"""
        status = {
            'cluster_name': self.cluster_name,
            'total_nodes': len(self.nodes),
            'connected_nodes': 0,
            'nodes': [],
            'mirror_queues': self.mirror_queues,
            'total_messages': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        for node in self.nodes:
            node_status = {
                'hostname': node.hostname,
                'is_connected': node.is_connected,
                'is_master': node.is_master,
                'message_count': node.message_count,
                'consumer_count': node.consumer_count,
                'last_heartbeat': node.last_heartbeat.isoformat() if node.last_heartbeat else None
            }
            
            if node.is_connected:
                status['connected_nodes'] += 1
                status['total_messages'] += node.message_count
            
            status['nodes'].append(node_status)
        
        return status
    
    def monitor_cluster_health(self, duration: int = 300):
        """监控集群健康状态"""
        logger.info(f"🔍 开始集群健康监控 (持续 {duration} 秒)")
        self.monitoring_active = True
        
        start_time = time.time()
        health_logs = []
        
        while self.monitoring_active and (time.time() - start_time) < duration:
            try:
                # 获取当前集群状态
                cluster_status = self.get_cluster_status()
                
                # 检查节点健康
                unhealthy_nodes = []
                for node_info in cluster_status['nodes']:
                    if not node_info['is_connected']:
                        unhealthy_nodes.append(node_info['hostname'])
                
                # 记录健康状态
                health_log = {
                    'timestamp': datetime.now().isoformat(),
                    'connected_nodes': cluster_status['connected_nodes'],
                    'total_nodes': cluster_status['total_nodes'],
                    'unhealthy_nodes': unhealthy_nodes,
                    'total_messages': cluster_status['total_messages']
                }
                
                health_logs.append(health_log)
                
                # 输出状态摘要
                logger.info(f"📊 集群状态: {cluster_status['connected_nodes']}/{cluster_status['total_nodes']} 节点在线")
                
                if unhealthy_nodes:
                    logger.warning(f"⚠️  不健康节点: {unhealthy_nodes}")
                
                # 等待下一次检查
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"❌ 集群监控异常: {e}")
                time.sleep(5)
        
        self.monitoring_active = False
        logger.info("🏁 集群健康监控结束")
        
        return health_logs
    
    def perform_failover_test(self, target_node_hostname: str):
        """执行故障转移测试"""
        logger.info(f"🧪 开始故障转移测试，目标节点: {target_node_hostname}")
        
        # 查找目标节点
        target_node = next((node for node in self.nodes if node.hostname == target_node_hostname), None)
        if not target_node:
            logger.error(f"❌ 未找到目标节点: {target_node_hostname}")
            return False
        
        # 记录初始状态
        initial_status = self.get_cluster_status()
        logger.info(f"📊 初始集群状态: {initial_status}")
        
        # 模拟节点故障 - 断开目标节点连接
        logger.info(f"💥 模拟节点故障: {target_node_hostname}")
        target_node.disconnect()
        
        # 等待一段时间让集群检测到故障
        time.sleep(10)
        
        # 检查故障后的状态
        failover_status = self.get_cluster_status()
        logger.info(f"📊 故障转移后状态: {failover_status}")
        
        # 恢复节点连接
        logger.info(f"🔧 恢复节点连接: {target_node_hostname}")
        reconnected = target_node.connect()
        
        if reconnected:
            logger.info("✅ 故障转移测试成功")
            return True
        else:
            logger.error("❌ 故障转移测试失败")
            return False
    
    def optimize_cluster_performance(self):
        """优化集群性能"""
        logger.info("⚡ 开始集群性能优化")
        
        optimizations = []
        
        for node in self.nodes:
            if node.is_connected:
                try:
                    # 设置prefetch count优化
                    node.channel.basic_qos(prefetch_count=100)
                    optimizations.append(f"设置 {node.hostname} prefetch_count=100")
                    
                    # 启用publisher confirms
                    node.channel.confirm_delivery()
                    optimizations.append(f"启用 {node.hostname} publisher confirms")
                    
                    # 设置ack timeout
                    node.connection.heartbeat = 30
                    optimizations.append(f"设置 {node.hostname} heartbeat=30")
                    
                except Exception as e:
                    logger.error(f"❌ 节点性能优化失败 {node.hostname}: {e}")
        
        logger.info(f"✅ 集群性能优化完成: {optimizations}")
        return optimizations
    
    def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理集群资源...")
        
        for node in self.nodes:
            node.disconnect()
        
        self.monitoring_active = False
        logger.info("✅ 集群资源清理完成")

def main():
    """主函数 - 演示集群管理功能"""
    
    # 集群节点配置
    cluster_nodes = [
        'rabbitmq-node1',  # 主节点
        'rabbitmq-node2',  # 从节点1
        'rabbitmq-node3'   # 从节点2
    ]
    
    # 创建集群管理器
    cluster_manager = RabbitMQClusterManager(cluster_nodes, "demo-cluster")
    
    try:
        # 1. 连接所有集群节点
        logger.info("🔗 连接集群节点...")
        connection_results = cluster_manager.connect_all_nodes()
        
        # 2. 设置镜像队列
        logger.info("🪞 设置镜像队列...")
        queue_name = "cluster-demo-queue"
        cluster_manager.setup_cluster(queue_name, ha_policy='all')
        
        # 3. 发布测试消息
        logger.info("📤 发布测试消息...")
        test_messages = [
            {'id': 1, 'content': '集群测试消息1'},
            {'id': 2, 'content': '集群测试消息2'},
            {'id': 3, 'content': '集群测试消息3'}
        ]
        cluster_manager.publish_to_cluster(queue_name, test_messages)
        
        # 4. 优化集群性能
        logger.info("⚡ 优化集群性能...")
        cluster_manager.optimize_cluster_performance()
        
        # 5. 监控集群健康（后台运行）
        logger.info("🔍 启动集群健康监控...")
        monitoring_thread = threading.Thread(
            target=cluster_manager.monitor_cluster_health,
            args=(60,)  # 监控60秒
        )
        monitoring_thread.start()
        
        # 6. 消费消息
        logger.info("👥 消费消息...")
        time.sleep(2)  # 等待消息完全发布
        cluster_manager.consume_from_cluster(queue_name, max_messages=3)
        
        # 7. 获取集群状态
        logger.info("📊 获取集群状态...")
        cluster_status = cluster_manager.get_cluster_status()
        logger.info(f"📈 最终集群状态: {json.dumps(cluster_status, indent=2, ensure_ascii=False)}")
        
        # 8. 故障转移测试（可选）
        if len(cluster_nodes) > 1:
            failover_choice = input("是否执行故障转移测试？(y/N): ")
            if failover_choice.lower() == 'y':
                target_node = cluster_nodes[1]  # 测试第二个节点
                cluster_manager.perform_failover_test(target_node)
        
        # 等待监控线程完成
        monitoring_thread.join()
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  用户中断")
    except Exception as e:
        logger.error(f"❌ 集群管理异常: {e}")
    finally:
        # 清理资源
        cluster_manager.cleanup()

if __name__ == '__main__':
    main()