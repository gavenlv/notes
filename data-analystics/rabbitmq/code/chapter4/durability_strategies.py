#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第4章：消息和队列持久化策略演示
展示不同持久化策略的效果和性能差异
"""

import pika
import time
import uuid
import threading
import json
import pickle
import os
import statistics
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

class DurabilityLevel(Enum):
    """持久化级别"""
    NONE = "none"           # 无持久化
    QUEUE_ONLY = "queue"    # 队列持久化
    MESSAGE_ONLY = "message" # 消息持久化
    FULL = "full"           # 完全持久化

class StorageType(Enum):
    """存储类型"""
    DISK = "disk"
    MEMORY = "memory"

@dataclass
class PersistConfig:
    """持久化配置"""
    level: DurabilityLevel
    storage_type: StorageType
    queue_name: str
    exchange_name: str
    durable: bool = False
    auto_delete: bool = False
    exclusive: bool = False

class DurabilityPerformanceTracker:
    """持久化性能跟踪器"""
    
    def __init__(self):
        self.results: List[Dict] = []
        self.lock = threading.Lock()
    
    def add_result(self, level: str, operation: str, duration: float, 
                   message_count: int = 0, success: bool = True):
        """添加性能结果"""
        with self.lock:
            result = {
                'level': level,
                'operation': operation,
                'duration': duration,
                'message_count': message_count,
                'success': success,
                'throughput': message_count / duration if duration > 0 else 0,
                'timestamp': time.time()
            }
            self.results.append(result)
    
    def get_level_statistics(self, level: str) -> Dict:
        """获取指定级别的统计信息"""
        with self.lock:
            level_results = [r for r in self.results if r['level'] == level]
            
            if not level_results:
                return {}
            
            send_results = [r for r in level_results if r['operation'] == 'send']
            receive_results = [r for r in level_results if r['operation'] == 'receive']
            
            return {
                'send_operations': len(send_results),
                'receive_operations': len(receive_results),
                'avg_send_time': statistics.mean([r['duration'] for r in send_results]) if send_results else 0,
                'avg_receive_time': statistics.mean([r['duration'] for r in receive_results]) if receive_results else 0,
                'total_throughput': statistics.mean([r['throughput'] for r in level_results]) if level_results else 0,
                'success_rate': (sum(1 for r in level_results if r['success']) / len(level_results)) * 100
            }
    
    def print_level_report(self, level: str):
        """打印级别报告"""
        stats = self.get_level_statistics(level)
        if not stats:
            return
        
        print(f"\n📊 {level} 持久化级别统计:")
        print(f"  发送操作数: {stats['send_operations']}")
        print(f"  接收操作数: {stats['receive_operations']}")
        print(f"  平均发送时间: {stats['avg_send_time']:.4f}s")
        print(f"  平均接收时间: {stats['avg_receive_time']:.4f}s")
        print(f"  总吞吐量: {stats['total_throughput']:.2f} 消息/秒")
        print(f"  成功率: {stats['success_rate']:.2f}%")

class DurabilityStrategyDemo:
    """持久化策略演示"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.connection_params = pika.ConnectionParameters(
            host=host,
            port=port,
            heartbeat=30,
            connection_attempts=3
        )
        self.tracker = DurabilityPerformanceTracker()
        self.configs = {}
        
    def create_config(self, level: DurabilityLevel) -> PersistConfig:
        """创建持久化配置"""
        config_id = str(uuid.uuid4())[:8]
        queue_name = f"{level.value}_queue_{config_id}"
        exchange_name = f"{level.value}_exchange_{config_id}"
        
        config = PersistConfig(
            level=level,
            storage_type=StorageType.DISK if level != DurabilityLevel.NONE else StorageType.MEMORY,
            queue_name=queue_name,
            exchange_name=exchange_name,
            durable=(level in [DurabilityLevel.QUEUE_ONLY, DurabilityLevel.FULL]),
            auto_delete=False,
            exclusive=False
        )
        
        self.configs[level.value] = config
        return config
    
    def setup_infrastructure(self, level: DurabilityLevel):
        """设置基础设施"""
        config = self.create_config(level)
        
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        try:
            # 创建交换机
            channel.exchange_declare(
                exchange=config.exchange_name,
                exchange_type='direct',
                durable=config.durable
            )
            
            # 创建队列
            channel.queue_declare(
                queue=config.queue_name,
                durable=config.durable,
                auto_delete=config.auto_delete,
                exclusive=config.exclusive,
                arguments={
                    'x-message-ttl': 300000,  # 5分钟TTL
                    'x-dead-letter-exchange': f"dlx_{config.exchange_name}",
                    'x-dead-letter-routing-key': f"dead_letter_{config.queue_name}"
                } if level in [DurabilityLevel.QUEUE_ONLY, DurabilityLevel.FULL] else {}
            )
            
            # 创建死信交换机和队列
            if level in [DurabilityLevel.QUEUE_ONLY, DurabilityLevel.FULL]:
                dlx_exchange = f"dlx_{config.exchange_name}"
                dlx_queue = f"dead_letter_{config.queue_name}"
                
                channel.exchange_declare(
                    exchange=dlx_exchange,
                    exchange_type='direct',
                    durable=True
                )
                
                channel.queue_declare(
                    queue=dlx_queue,
                    durable=True,
                    auto_delete=False,
                    exclusive=False
                )
                
                channel.queue_bind(
                    exchange=dlx_exchange,
                    queue=dlx_queue,
                    routing_key=f"dead_letter_{config.queue_name}"
                )
            
            # 绑定队列到交换机
            channel.queue_bind(
                exchange=config.exchange_name,
                queue=config.queue_name,
                routing_key=config.queue_name
            )
            
            print(f"✅ {level.value} 基础设施设置完成")
            
        except Exception as e:
            print(f"❌ {level.value} 基础设施设置失败: {e}")
        finally:
            connection.close()
    
    def prepare_messages(self, count: int, payload_size: int = 1024) -> List[Dict]:
        """准备测试消息"""
        messages = []
        
        # 生成测试负载
        test_payload = "x" * payload_size
        
        for i in range(count):
            message = {
                'id': str(uuid.uuid4()),
                'sequence': i + 1,
                'timestamp': time.time(),
                'payload': test_payload,
                'checksum': hashlib.md5(test_payload.encode()).hexdigest(),
                'size': len(test_payload),
                'priority': i % 10
            }
            
            messages.append(message)
        
        return messages
    
    def send_messages(self, level: DurabilityLevel, message_count: int = 100) -> Dict:
        """发送消息"""
        config = self.configs[level.value]
        messages = self.prepare_messages(message_count)
        
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        start_time = time.time()
        sent_count = 0
        
        try:
            for i, message in enumerate(messages):
                try:
                    # 设置消息属性
                    properties = pika.BasicProperties()
                    
                    if level in [DurabilityLevel.MESSAGE_ONLY, DurabilityLevel.FULL]:
                        properties.delivery_mode = 2  # 持久化消息
                    
                    properties.priority = message['priority']
                    properties.message_id = message['id']
                    properties.timestamp = int(message['timestamp'])
                    properties.correlation_id = f"{config.queue_name}_{message['sequence']}"
                    
                    # 发送消息
                    channel.basic_publish(
                        exchange=config.exchange_name,
                        routing_key=config.queue_name,
                        body=json.dumps(message),
                        properties=properties
                    )
                    
                    sent_count += 1
                    
                    if (i + 1) % 25 == 0:
                        print(f"  已发送: {i + 1}/{message_count}")
                        
                except Exception as e:
                    print(f"❌ 发送消息失败 {i+1}: {e}")
                    break
            
        except Exception as e:
            print(f"❌ {level.value} 发送过程失败: {e}")
        
        finally:
            duration = time.time() - start_time
            self.tracker.add_result(
                level.value, 'send', duration, sent_count, sent_count == message_count
            )
            connection.close()
        
        return {
            'sent_count': sent_count,
            'duration': duration,
            'throughput': sent_count / duration if duration > 0 else 0
        }
    
    def receive_messages(self, level: DurabilityLevel, expected_count: int = 100) -> Dict:
        """接收消息"""
        config = self.configs[level.value]
        
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        # 预取设置（根据持久化级别调整）
        if level == DurabilityLevel.FULL:
            channel.basic_qos(prefetch_count=10)  # 较低预取以确保可靠性
        else:
            channel.basic_qos(prefetch_count=20)  # 较高预取以提高性能
        
        received_messages = []
        start_time = time.time()
        
        def message_callback(ch, method, properties, body):
            try:
                message = json.loads(body.decode())
                
                # 验证消息完整性
                if 'checksum' in message:
                    payload = message['payload']
                    expected_checksum = message['checksum']
                    actual_checksum = hashlib.md5(payload.encode()).hexdigest()
                    
                    if expected_checksum != actual_checksum:
                        raise ValueError(f"消息校验和不一致")
                
                received_messages.append(message)
                
                # 模拟处理延迟
                if level == DurabilityLevel.FULL:
                    time.sleep(0.001)  # 更长的处理时间
                
                # 手动确认
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"❌ 接收消息失败: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        try:
            # 开始消费
            channel.basic_consume(
                queue=config.queue_name,
                on_message_callback=message_callback,
                auto_ack=False
            )
            
            # 接收指定数量的消息
            while len(received_messages) < expected_count:
                try:
                    connection.process_data_events(time_limit=1.0)
                    
                    # 检查是否超时
                    if time.time() - start_time > 30:  # 30秒超时
                        print(f"⚠️ 接收超时，已接收: {len(received_messages)}/{expected_count}")
                        break
                        
                except Exception as e:
                    print(f"❌ 接收过程异常: {e}")
                    break
        
        except Exception as e:
            print(f"❌ {level.value} 接收过程失败: {e}")
        
        finally:
            duration = time.time() - start_time
            self.tracker.add_result(
                level.value, 'receive', duration, len(received_messages), 
                len(received_messages) == expected_count
            )
            connection.close()
        
        return {
            'received_count': len(received_messages),
            'duration': duration,
            'throughput': len(received_messages) / duration if duration > 0 else 0,
            'lost_count': expected_count - len(received_messages)
        }
    
    def crash_recovery_test(self, level: DurabilityLevel):
        """崩溃恢复测试"""
        print(f"\n💥 {level.value} 崩溃恢复测试")
        config = self.configs[level.value]
        
        # 第一阶段：发送消息
        print("第一阶段：发送消息...")
        send_result = self.send_messages(level, 50)
        print(f"  已发送 {send_result['sent_count']} 条消息")
        
        # 模拟崩溃（断开连接）
        print("模拟系统崩溃...")
        time.sleep(1)
        
        # 第二阶段：尝试接收
        print("第二阶段：系统恢复后尝试接收...")
        receive_result = self.receive_messages(level, 50)
        
        recovery_rate = (receive_result['received_count'] / send_result['sent_count']) * 100
        print(f"  恢复率: {recovery_rate:.2f}%")
        print(f"  丢失消息: {receive_result['lost_count']} 条")
        
        return {
            'recovery_rate': recovery_rate,
            'send_count': send_result['sent_count'],
            'receive_count': receive_result['received_count'],
            'lost_count': receive_result['lost_count']
        }
    
    def stress_test(self, level: DurabilityLevel, message_count: int = 500):
        """压力测试"""
        print(f"\n🔥 {level.value} 压力测试 (发送 {message_count} 条消息)")
        
        # 发送消息
        send_result = self.send_messages(level, message_count)
        
        # 启动接收线程
        received_count = [0]  # 使用列表来支持闭包修改
        
        def receive_worker():
            result = self.receive_messages(level, message_count)
            received_count[0] = result['received_count']
        
        receiver_thread = threading.Thread(target=receive_worker)
        receiver_thread.start()
        
        # 等待接收完成
        receiver_thread.join(timeout=60)
        
        print(f"  发送: {send_result['sent_count']} 条")
        print(f"  接收: {received_count[0]} 条")
        print(f"  吞吐量: {send_result['throughput']:.2f} 消息/秒")
        
        return {
            'send_count': send_result['sent_count'],
            'receive_count': received_count[0],
            'throughput': send_result['throughput']
        }
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🧪 开始持久化策略综合测试")
        print("=" * 70)
        
        levels = [DurabilityLevel.NONE, DurabilityLevel.QUEUE_ONLY, 
                 DurabilityLevel.MESSAGE_ONLY, DurabilityLevel.FULL]
        
        results = {}
        
        for level in levels:
            print(f"\n🔧 测试 {level.value.upper()} 持久化级别")
            print("-" * 50)
            
            # 设置基础设施
            self.setup_infrastructure(level)
            
            # 发送接收测试
            send_result = self.send_messages(level, 100)
            receive_result = self.receive_messages(level, 100)
            
            # 崩溃恢复测试
            crash_result = self.crash_recovery_test(level)
            
            # 压力测试
            stress_result = self.stress_test(level, 200)
            
            results[level.value] = {
                'send': send_result,
                'receive': receive_result,
                'crash_recovery': crash_result,
                'stress': stress_result
            }
        
        # 生成对比报告
        self.generate_comparison_report(results)
    
    def generate_comparison_report(self, results: Dict):
        """生成对比报告"""
        print("\n" + "=" * 70)
        print("📈 持久化策略性能对比报告")
        print("=" * 70)
        
        levels = list(results.keys())
        
        # 性能对比表
        print(f"\n{'级别':<15} {'发送性能':<12} {'接收性能':<12} {'崩溃恢复率':<12}")
        print("-" * 65)
        
        for level in levels:
            result = results[level]
            send_throughput = result['send']['throughput']
            receive_throughput = result['receive']['throughput']
            recovery_rate = result['crash_recovery']['recovery_rate']
            
            print(f"{level:<15} {send_throughput:.2f}/秒     {receive_throughput:.2f}/秒     {recovery_rate:.2f}%")
        
        # 详细分析
        print(f"\n💡 分析结果:")
        
        none_results = results['none']
        full_results = results['full']
        
        performance_impact = ((full_results['send']['throughput'] - none_results['send']['throughput']) 
                            / none_results['send']['throughput'] * 100)
        
        reliability_improvement = (full_results['crash_recovery']['recovery_rate'] 
                                 - none_results['crash_recovery']['recovery_rate'])
        
        print(f"  性能影响: 完全持久化相比无持久化吞吐量下降 {abs(performance_impact):.1f}%")
        print(f"  可靠性提升: 崩溃恢复率提升 {reliability_improvement:.1f}%")
        
        # 选择建议
        print(f"\n💭 选择建议:")
        print("  无持久化: 性能最佳，适合临时消息或实时数据流")
        print("  队列持久化: 平衡性能与可靠性，适合多数业务场景")
        print("  消息持久化: 确保消息持久性，适合重要但不频繁的消息")
        print("  完全持久化: 最高可靠性，适合关键业务和事务性消息")
    
    def cleanup_infrastructure(self):
        """清理基础设施"""
        print("\n🧹 清理测试基础设施...")
        
        for level, config in self.configs.items():
            try:
                connection = pika.BlockingConnection(self.connection_params)
                channel = connection.channel()
                
                # 清理队列
                try:
                    channel.queue_delete(queue=config.queue_name)
                except:
                    pass
                
                # 清理交换机
                try:
                    channel.exchange_delete(exchange=config.exchange_name)
                except:
                    pass
                
                # 清理死信交换机和队列
                if config.durable:
                    try:
                        dlx_exchange = f"dlx_{config.exchange_name}"
                        dlx_queue = f"dead_letter_{config.queue_name}"
                        
                        channel.queue_delete(queue=dlx_queue)
                        channel.exchange_delete(exchange=dlx_exchange)
                    except:
                        pass
                
                connection.close()
                
            except Exception as e:
                print(f"⚠️ 清理 {level} 时出现错误: {e}")

def main():
    """主函数"""
    print("💾 消息和队列持久化策略演示")
    print("确保RabbitMQ服务正在运行...")
    
    try:
        demo = DurabilityStrategyDemo()
        
        # 运行综合测试
        demo.run_comprehensive_test()
        
        # 询问是否清理
        cleanup = input("\n是否清理测试基础设施？(y/N): ").strip().lower()
        if cleanup == 'y':
            demo.cleanup_infrastructure()
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        print("请确保:")
        print("1. RabbitMQ服务正在运行")
        print("2. 可以连接到 localhost:5672")
        print("3. 已安装必要库: pip install pika")

if __name__ == "__main__":
    main()