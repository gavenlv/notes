#!/usr/bin/env python3
"""
RabbitMQ集群与高可用性示例代码
包含集群管理、镜像队列、负载均衡、故障恢复等功能
"""

import pika
import json
import time
import random
import logging
import threading
import requests
from datetime import datetime
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ClusterNode:
    """集群节点信息"""
    host: str
    port: int = 5672
    management_port: int = 15672
    weight: int = 1
    health_score: int = 100
    is_available: bool = True
    last_check: datetime = None

class ClusterConnectionManager:
    """集群连接管理器"""
    
    def __init__(self, nodes: List[ClusterNode], username: str, password: str):
        self.nodes = nodes
        self.username = username
        self.password = password
        self.credentials = pika.PlainCredentials(username, password)
        self.current_node_index = 0
        self.connection = None
        self.channel = None
        self.health_check_thread = None
        self.running = False
        
    def start_health_check(self, interval: int = 30):
        """启动健康检查"""
        self.running = True
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            args=(interval,)
        )
        self.health_check_thread.daemon = True
        self.health_check_thread.start()
        
    def stop_health_check(self):
        """停止健康检查"""
        self.running = False
        if self.health_check_thread:
            self.health_check_thread.join()
            
    def _health_check_loop(self, interval: int):
        """健康检查循环"""
        while self.running:
            try:
                self._check_node_health()
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
            time.sleep(interval)
            
    def _check_node_health(self):
        """检查节点健康状态"""
        for node in self.nodes:
            try:
                # 尝试连接管理接口
                url = f"http://{node.host}:{node.management_port}/api/overview"
                response = requests.get(url, auth=(self.username, self.password), timeout=5)
                
                if response.status_code == 200:
                    node.is_available = True
                    node.health_score = 100
                    node.last_check = datetime.now()
                    logger.debug(f"节点 {node.host}:{node.port} 健康检查通过")
                else:
                    node.is_available = False
                    node.health_score = 0
                    logger.warning(f"节点 {node.host}:{node.port} 健康检查失败: {response.status_code}")
                    
            except Exception as e:
                node.is_available = False
                node.health_score = 0
                logger.error(f"节点 {node.host}:{node.port} 健康检查异常: {e}")
                
    def get_available_nodes(self) -> List[ClusterNode]:
        """获取可用节点"""
        return [node for node in self.nodes if node.is_available]
        
    def connect(self, strategy: str = 'round_robin') -> bool:
        """连接集群"""
        available_nodes = self.get_available_nodes()
        
        if not available_nodes:
            logger.error("没有可用的集群节点")
            return False
            
        # 根据策略选择节点
        if strategy == 'round_robin':
            node = available_nodes[self.current_node_index % len(available_nodes)]
            self.current_node_index += 1
        elif strategy == 'random':
            node = random.choice(available_nodes)
        elif strategy == 'health_based':
            node = max(available_nodes, key=lambda n: n.health_score)
        else:
            node = available_nodes[0]
            
        try:
            parameters = pika.ConnectionParameters(
                host=node.host,
                port=node.port,
                credentials=self.credentials,
                connection_attempts=3,
                retry_delay=5,
                heartbeat=30,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            logger.info(f"成功连接到集群节点: {node.host}:{node.port}")
            return True
            
        except Exception as e:
            logger.error(f"连接集群失败: {e}")
            return False
            
    def reconnect(self, strategy: str = 'round_robin') -> bool:
        """重新连接"""
        self.disconnect()
        return self.connect(strategy)
        
    def disconnect(self):
        """断开连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            
    def publish(self, exchange: str, routing_key: str, message: dict) -> bool:
        """发布消息"""
        try:
            if not self.connection or not self.connection.is_open:
                if not self.reconnect():
                    return False
                    
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化
                    timestamp=int(time.time())
                )
            )
            return True
            
        except Exception as e:
            logger.error(f"发布消息失败: {e}")
            return False
            
    def consume(self, queue_name: str, callback: Callable, auto_ack: bool = False):
        """消费消息"""
        try:
            if not self.connection or not self.connection.is_open:
                if not self.reconnect():
                    return False
                    
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=auto_ack
            )
            
            logger.info(f"开始消费队列: {queue_name}")
            self.channel.start_consuming()
            
        except Exception as e:
            logger.error(f"消费消息失败: {e}")
            return False

class MirrorQueueManager:
    """镜像队列管理器"""
    
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"http://{host}:15672/api"
        
    def create_mirror_policy(self, policy_name: str, pattern: str, definition: Dict, priority: int = 0) -> bool:
        """创建镜像策略"""
        url = f"{self.base_url}/policies/%2f/{policy_name}"
        
        payload = {
            "pattern": pattern,
            "definition": definition,
            "priority": priority
        }
        
        try:
            response = requests.put(
                url,
                data=json.dumps(payload),
                auth=(self.username, self.password),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"镜像策略 {policy_name} 创建成功")
                return True
            else:
                logger.error(f"创建镜像策略失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"创建镜像策略异常: {e}")
            return False
            
    def create_ha_queue(self, queue_name: str, durable: bool = True, auto_delete: bool = False) -> bool:
        """创建高可用队列"""
        url = f"{self.base_url}/queues/%2f/{queue_name}"
        
        payload = {
            "durable": durable,
            "auto_delete": auto_delete,
            "arguments": {
                "x-queue-type": "classic",
                "x-ha-policy": "all"
            }
        }
        
        try:
            response = requests.put(
                url,
                data=json.dumps(payload),
                auth=(self.username, self.password),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"高可用队列 {queue_name} 创建成功")
                return True
            else:
                logger.error(f"创建高可用队列失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"创建高可用队列异常: {e}")
            return False
            
    def get_queue_status(self, queue_name: str) -> Optional[Dict]:
        """获取队列状态"""
        url = f"{self.base_url}/queues/%2f/{queue_name}"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.password)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取队列状态失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取队列状态异常: {e}")
            return None

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, nodes: List[ClusterNode]):
        self.nodes = nodes
        self.current_index = 0
        self.weights = [node.weight for node in nodes]
        self.total_weight = sum(self.weights)
        
    def select_node(self, strategy: str = 'round_robin') -> ClusterNode:
        """选择节点"""
        available_nodes = [node for node in self.nodes if node.is_available]
        
        if not available_nodes:
            raise Exception("没有可用的节点")
            
        if strategy == 'round_robin':
            node = available_nodes[self.current_index % len(available_nodes)]
            self.current_index += 1
            return node
            
        elif strategy == 'weighted_round_robin':
            return self._weighted_selection(available_nodes)
            
        elif strategy == 'health_based':
            return max(available_nodes, key=lambda n: n.health_score)
            
        elif strategy == 'random':
            return random.choice(available_nodes)
            
        else:
            return available_nodes[0]
            
    def _weighted_selection(self, available_nodes: List[ClusterNode]) -> ClusterNode:
        """权重选择"""
        # 简单的权重轮询实现
        random_weight = random.randint(1, self.total_weight)
        cumulative_weight = 0
        
        for node in available_nodes:
            cumulative_weight += node.weight
            if random_weight <= cumulative_weight:
                return node
                
        return available_nodes[0]

class ClusterMonitor:
    """集群监控器"""
    
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"http://{host}:15672/api"
        
    def get_cluster_status(self) -> Dict:
        """获取集群状态"""
        url = f"{self.base_url}/overview"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.password),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取集群状态失败: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"获取集群状态异常: {e}")
            return {}
            
    def get_nodes_status(self) -> List[Dict]:
        """获取节点状态"""
        url = f"{self.base_url}/nodes"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.password),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取节点状态失败: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"获取节点状态异常: {e}")
            return []
            
    def get_queue_status(self) -> List[Dict]:
        """获取队列状态"""
        url = f"{self.base_url}/queues"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.password),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取队列状态失败: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"获取队列状态异常: {e}")
            return []
            
    def get_health_score(self) -> float:
        """获取集群健康评分"""
        nodes = self.get_nodes_status()
        if not nodes:
            return 0.0
            
        running_nodes = sum(1 for node in nodes if node.get("running", False))
        return (running_nodes / len(nodes)) * 100

class FaultRecovery:
    """故障恢复管理器"""
    
    def __init__(self, nodes: List[ClusterNode], username: str, password: str):
        self.nodes = nodes
        self.username = username
        self.password = password
        
    def detect_failures(self) -> List[ClusterNode]:
        """检测故障节点"""
        failed_nodes = []
        
        for node in self.nodes:
            try:
                # 尝试连接管理接口
                url = f"http://{node.host}:{node.management_port}/api/overview"
                response = requests.get(url, auth=(self.username, self.password), timeout=5)
                
                if response.status_code != 200:
                    failed_nodes.append(node)
                    logger.warning(f"检测到故障节点: {node.host}:{node.port}")
                    
            except Exception as e:
                failed_nodes.append(node)
                logger.error(f"检测节点 {node.host}:{node.port} 失败: {e}")
                
        return failed_nodes
        
    def auto_failover(self, failed_nodes: List[ClusterNode]) -> bool:
        """自动故障转移"""
        if not failed_nodes:
            return True
            
        logger.info(f"开始故障转移，故障节点: {[n.host for n in failed_nodes]}")
        
        try:
            # 标记节点为不可用
            for node in failed_nodes:
                node.is_available = False
                node.health_score = 0
                
            # 这里可以添加更复杂的故障转移逻辑
            # 例如：重新分配队列、通知负载均衡器等
            
            logger.info("故障转移完成")
            return True
            
        except Exception as e:
            logger.error(f"故障转移失败: {e}")
            return False

class ClusterExamples:
    """集群示例演示类"""
    
    def __init__(self):
        # 定义集群节点
        self.nodes = [
            ClusterNode("localhost", 5672, 15672, weight=10),
            ClusterNode("localhost", 5673, 15673, weight=5),
            ClusterNode("localhost", 5674, 15674, weight=1)
        ]
        
        self.username = "admin"
        self.password = "admin123"
        
    def basic_cluster_connection_example(self):
        """基础集群连接示例"""
        print("=== 基础集群连接示例 ===")
        
        # 创建连接管理器
        manager = ClusterConnectionManager(self.nodes, self.username, self.password)
        
        # 启动健康检查
        manager.start_health_check(interval=10)
        
        try:
            # 连接到集群
            if manager.connect(strategy='round_robin'):
                print("✓ 成功连接到集群")
                
                # 创建测试队列
                manager.channel.queue_declare(queue='cluster_test', durable=True)
                
                # 发布测试消息
                test_message = {
                    "message": "集群连接测试",
                    "timestamp": datetime.now().isoformat()
                }
                
                if manager.publish('', 'cluster_test', test_message):
                    print("✓ 消息发布成功")
                else:
                    print("✗ 消息发布失败")
                    
                # 消费消息
                def message_callback(ch, method, properties, body):
                    print(f"收到消息: {json.loads(body)}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                manager.channel.basic_consume(
                    queue='cluster_test',
                    on_message_callback=message_callback,
                    auto_ack=False
                )
                
                print("开始消费消息...")
                time.sleep(5)
                
            else:
                print("✗ 连接集群失败")
                
        except Exception as e:
            print(f"✗ 集群连接示例失败: {e}")
            
        finally:
            manager.stop_health_check()
            manager.disconnect()
            
    def mirror_queue_example(self):
        """镜像队列示例"""
        print("\n=== 镜像队列示例 ===")
        
        try:
            # 创建镜像队列管理器
            mirror_manager = MirrorQueueManager("localhost", self.username, self.password)
            
            # 创建镜像策略
            policy_definition = {
                "ha-mode": "all",
                "ha-sync-mode": "automatic"
            }
            
            if mirror_manager.create_mirror_policy("ha-all", "^ha\.", policy_definition):
                print("✓ 镜像策略创建成功")
            else:
                print("✗ 镜像策略创建失败")
                return
                
            # 创建高可用队列
            ha_queue_name = "ha.test.queue"
            if mirror_manager.create_ha_queue(ha_queue_name):
                print(f"✓ 高可用队列 {ha_queue_name} 创建成功")
            else:
                print(f"✗ 高可用队列 {ha_queue_name} 创建失败")
                return
                
            # 获取队列状态
            queue_status = mirror_manager.get_queue_status(ha_queue_name)
            if queue_status:
                print(f"队列状态: {queue_status.get('state', 'unknown')}")
                print(f"消息数: {queue_status.get('messages', 0)}")
                print(f"消费者数: {queue_status.get('consumers', 0)}")
            else:
                print("✗ 无法获取队列状态")
                
            # 使用集群连接管理器测试高可用队列
            manager = ClusterConnectionManager(self.nodes, self.username, self.password)
            
            if manager.connect():
                # 发布消息到高可用队列
                for i in range(5):
                    message = {
                        "id": i,
                        "message": f"镜像队列测试消息 {i}",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    if manager.publish('', ha_queue_name, message):
                        print(f"✓ 消息 {i} 发布成功")
                    else:
                        print(f"✗ 消息 {i} 发布失败")
                        
                manager.disconnect()
            else:
                print("✗ 无法连接集群")
                
        except Exception as e:
            print(f"✗ 镜像队列示例失败: {e}")
            
    def load_balancing_example(self):
        """负载均衡示例"""
        print("\n=== 负载均衡示例 ===")
        
        try:
            # 创建负载均衡器
            load_balancer = LoadBalancer(self.nodes)
            
            # 模拟消息发布
            def publish_with_load_balancing():
                manager = ClusterConnectionManager(self.nodes, self.username, self.password)
                
                if manager.connect():
                    for i in range(10):
                        # 选择节点
                        selected_node = load_balancer.select_node(strategy='round_robin')
                        print(f"选择节点: {selected_node.host}:{selected_node.port}")
                        
                        message = {
                            "id": i,
                            "node": f"{selected_node.host}:{selected_node.port}",
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        manager.publish('', 'load_balancer_test', message)
                        time.sleep(0.1)
                        
                    manager.disconnect()
                    
            # 使用线程池模拟并发
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(publish_with_load_balancing) for _ in range(3)]
                
                for future in futures:
                    try:
                        future.result(timeout=30)
                    except Exception as e:
                        print(f"负载均衡任务失败: {e}")
                        
            print("✓ 负载均衡测试完成")
            
        except Exception as e:
            print(f"✗ 负载均衡示例失败: {e}")
            
    def cluster_monitoring_example(self):
        """集群监控示例"""
        print("\n=== 集群监控示例 ===")
        
        try:
            # 创建监控器
            monitor = ClusterMonitor("localhost", self.username, self.password)
            
            # 获取集群状态
            cluster_status = monitor.get_cluster_status()
            if cluster_status:
                print("集群状态:")
                print(f"  节点数: {cluster_status.get('cluster_nodes', {}).get('nodes', 'unknown')}")
                print(f"  队列数: {cluster_status.get('object_totals', {}).get('queues', 'unknown')}")
                print(f"  消息数: {cluster_status.get('queue_totals', {}).get('messages', 'unknown')}")
            else:
                print("✗ 无法获取集群状态")
                
            # 获取节点状态
            nodes_status = monitor.get_nodes_status()
            if nodes_status:
                print("\n节点状态:")
                for node in nodes_status:
                    print(f"  {node.get('name', 'unknown')}: {node.get('state', 'unknown')}")
            else:
                print("✗ 无法获取节点状态")
                
            # 获取健康评分
            health_score = monitor.get_health_score()
            print(f"\n集群健康评分: {health_score:.1f}%")
            
            # 获取队列状态
            queue_status = monitor.get_queue_status()
            if queue_status:
                print(f"\n队列概况: 共 {len(queue_status)} 个队列")
                for queue in queue_status[:5]:  # 只显示前5个队列
                    print(f"  {queue.get('name', 'unknown')}: {queue.get('messages', 0)} 条消息")
            else:
                print("✗ 无法获取队列状态")
                
        except Exception as e:
            print(f"✗ 集群监控示例失败: {e}")
            
    def fault_recovery_example(self):
        """故障恢复示例"""
        print("\n=== 故障恢复示例 ===")
        
        try:
            # 创建故障恢复管理器
            recovery = FaultRecovery(self.nodes, self.username, self.password)
            
            # 模拟故障检测
            print("检测集群故障...")
            failed_nodes = recovery.detect_failures()
            
            if failed_nodes:
                print(f"检测到 {len(failed_nodes)} 个故障节点:")
                for node in failed_nodes:
                    print(f"  - {node.host}:{node.port}")
                    
                # 执行故障转移
                if recovery.auto_failover(failed_nodes):
                    print("✓ 故障转移成功")
                else:
                    print("✗ 故障转移失败")
            else:
                print("✓ 未检测到故障节点")
                
        except Exception as e:
            print(f"✗ 故障恢复示例失败: {e}")
            
    def performance_test_example(self):
        """性能测试示例"""
        print("\n=== 性能测试示例 ===")
        
        try:
            # 创建连接管理器
            manager = ClusterConnectionManager(self.nodes, self.username, self.password)
            
            if not manager.connect():
                print("✗ 无法连接集群")
                return
                
            # 创建测试队列
            test_queue = "performance_test"
            manager.channel.queue_declare(queue=test_queue, durable=True)
            
            # 性能测试参数
            message_count = 1000
            message_size = 1024  # 1KB
            
            print(f"开始性能测试: {message_count} 条消息，每条 {message_size} 字节")
            
            # 生成测试消息
            test_message = {
                "data": "x" * message_size,
                "timestamp": datetime.now().isoformat()
            }
            
            # 开始计时
            start_time = time.time()
            
            # 发布消息
            success_count = 0
            for i in range(message_count):
                test_message["id"] = i
                if manager.publish('', test_queue, test_message):
                    success_count += 1
                    
                if i % 100 == 0:
                    print(f"已发布 {i}/{message_count} 条消息")
                    
            # 结束计时
            end_time = time.time()
            duration = end_time - start_time
            
            # 计算性能指标
            throughput = success_count / duration
            success_rate = (success_count / message_count) * 100
            
            print(f"\n性能测试结果:")
            print(f"  总消息数: {message_count}")
            print(f"  成功消息数: {success_count}")
            print(f"  成功率: {success_rate:.1f}%")
            print(f"  总耗时: {duration:.2f} 秒")
            print(f"  吞吐量: {throughput:.1f} 消息/秒")
            
            manager.disconnect()
            
        except Exception as e:
            print(f"✗ 性能测试失败: {e}")

def main():
    """主函数"""
    print("RabbitMQ集群与高可用性示例")
    print("=" * 40)
    
    # 创建示例实例
    examples = ClusterExamples()
    
    # 运行示例
    try:
        examples.basic_cluster_connection_example()
        examples.mirror_queue_example()
        examples.load_balancing_example()
        examples.cluster_monitoring_example()
        examples.fault_recovery_example()
        examples.performance_test_example()
        
        print("\n" + "=" * 40)
        print("所有示例运行完成！")
        
    except KeyboardInterrupt:
        print("\n用户中断，示例停止")
    except Exception as e:
        print(f"运行示例时发生错误: {e}")

if __name__ == "__main__":
    main()