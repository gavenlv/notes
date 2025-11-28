#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第4章：消息确认策略对比演示
展示不同的消息确认模式的实际效果和性能差异
"""

import pika
import time
import uuid
import threading
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

class AckMode(Enum):
    """确认模式"""
    AUTO = "auto"
    MANUAL = "manual"
    BATCH = "batch"
    TRANSACTION = "transaction"

@dataclass
class MessageResult:
    """消息处理结果"""
    message_id: str
    ack_mode: str
    sent_time: float
    received_time: float
    processing_time: float
    status: str  # success, failed, timeout
    retry_count: int

class MessagePerformanceTracker:
    """消息性能跟踪器"""
    
    def __init__(self):
        self.results: List[MessageResult] = []
        self.lock = threading.Lock()
    
    def add_result(self, result: MessageResult):
        """添加结果"""
        with self.lock:
            self.results.append(result)
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        with self.lock:
            if not self.results:
                return {}
            
            processing_times = [r.processing_time for r in self.results]
            success_count = sum(1 for r in self.results if r.status == 'success')
            failed_count = sum(1 for r in self.results if r.status == 'failed')
            
            return {
                'total_messages': len(self.results),
                'success_count': success_count,
                'failed_count': failed_count,
                'success_rate': (success_count / len(self.results)) * 100,
                'avg_processing_time': statistics.mean(processing_times),
                'min_processing_time': min(processing_times),
                'max_processing_time': max(processing_times),
                'median_processing_time': statistics.median(processing_times)
            }
    
    def print_statistics(self, ack_mode: str):
        """打印统计信息"""
        stats = self.get_statistics()
        if not stats:
            return
        
        print(f"\n📊 {ack_mode} 模式统计:")
        print(f"  总消息数: {stats['total_messages']}")
        print(f"  成功数: {stats['success_count']}")
        print(f"  失败数: {stats['failed_count']}")
        print(f"  成功率: {stats['success_rate']:.2f}%")
        print(f"  平均处理时间: {stats['avg_processing_time']:.4f}s")
        print(f"  最小处理时间: {stats['min_processing_time']:.4f}s")
        print(f"  最大处理时间: {stats['max_processing_time']:.4f}s")
        print(f"  中位数处理时间: {stats['median_processing_time']:.4f}s")

class AcknowledgmentStrategyDemo:
    """消息确认策略演示"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.connection_params = pika.ConnectionParameters(
            host=host,
            port=port,
            heartbeat=30,
            connection_attempts=3
        )
        self.tracker = MessagePerformanceTracker()
        self.test_results = {}
    
    def setup_queues(self):
        """设置测试队列"""
        queues_to_create = [
            'auto_ack_queue',
            'manual_ack_queue', 
            'batch_ack_queue',
            'transaction_queue'
        ]
        
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        # 创建交换机（如果需要）
        channel.exchange_declare(
            exchange='ack_test_exchange',
            exchange_type='topic',
            durable=True
        )
        
        # 创建队列
        for queue_name in queues_to_create:
            channel.queue_declare(queue=queue_name, durable=True)
            
            # 根据队列类型绑定到交换机
            if queue_name != 'auto_ack_queue':
                channel.queue_bind(
                    exchange='ack_test_exchange',
                    queue=queue_name,
                    routing_key=queue_name
                )
        
        connection.close()
        print("✅ 测试队列设置完成")
    
    def auto_ack_producer(self, message_count: int = 100) -> Dict:
        """自动确认生产者"""
        print(f"\n🚀 开始自动确认模式生产者测试 (发送 {message_count} 条消息)")
        
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        # 绑定到交换机
        channel.queue_bind(
            exchange='ack_test_exchange',
            queue='auto_ack_queue',
            routing_key='auto_ack_queue'
        )
        
        sent_count = 0
        start_time = time.time()
        
        try:
            for i in range(message_count):
                message = {
                    'id': str(uuid.uuid4()),
                    'content': f'自动确认消息 {i+1}',
                    'timestamp': time.time(),
                    'mode': 'auto'
                }
                
                channel.basic_publish(
                    exchange='ack_test_exchange',
                    routing_key='auto_ack_queue',
                    body=json.dumps(message)
                )
                
                sent_count += 1
                
                if (i + 1) % 20 == 0:
                    print(f"  已发送: {i + 1}/{message_count}")
        
        except Exception as e:
            print(f"❌ 发送失败: {e}")
        
        finally:
            duration = time.time() - start_time
            connection.close()
        
        return {
            'sent_count': sent_count,
            'duration': duration,
            'throughput': sent_count / duration if duration > 0 else 0
        }
    
    def auto_ack_consumer(self, message_count: int = 100, consume_time: float = 5.0):
        """自动确认消费者"""
        print(f"📥 启动自动确认消费者 (预计处理 {message_count} 条消息)")
        
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        # 公平调度
        channel.basic_qos(prefetch_count=10)
        
        processed_count = 0
        start_time = time.time()
        
        def auto_callback(ch, method, properties, body):
            nonlocal processed_count
            
            try:
                message = json.loads(body.decode())
                message_id = message['id']
                sent_time = message['timestamp']
                
                # 模拟消息处理
                time.sleep(0.01)  # 10ms处理时间
                
                received_time = time.time()
                processing_time = received_time - sent_time
                
                result = MessageResult(
                    message_id=message_id,
                    ack_mode='auto',
                    sent_time=sent_time,
                    received_time=received_time,
                    processing_time=processing_time,
                    status='success',
                    retry_count=0
                )
                
                self.tracker.add_result(result)
                processed_count += 1
                
                if processed_count % 20 == 0:
                    elapsed = time.time() - start_time
                    print(f"  已处理: {processed_count}/{message_count}, 耗时: {elapsed:.1f}s")
                
            except Exception as e:
                print(f"❌ 处理消息失败: {e}")
        
        # 自动确认消费
        channel.basic_consume(
            queue='auto_ack_queue',
            on_message_callback=auto_callback,
            auto_ack=True
        )
        
        try:
            # 设置消费超时
            timeout_start = time.time()
            while processed_count < message_count:
                if time.time() - timeout_start > consume_time:
                    break
                connection.process_data_events(time_limit=1.0)
                
        except KeyboardInterrupt:
            print("⏹️ 消费者被中断")
        finally:
            connection.close()
        
        print(f"✅ 自动确认消费完成，处理了 {processed_count} 条消息")
    
    def manual_ack_producer(self, message_count: int = 100) -> Dict:
        """手动确认生产者"""
        print(f"\n🚀 开始手动确认模式生产者测试 (发送 {message_count} 条消息)")
        
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        # 启用发布确认
        channel.confirm_delivery()
        
        sent_count = 0
        start_time = time.time()
        
        try:
            for i in range(message_count):
                message = {
                    'id': str(uuid.uuid4()),
                    'content': f'手动确认消息 {i+1}',
                    'timestamp': time.time(),
                    'mode': 'manual'
                }
                
                # 发送消息并等待确认
                channel.basic_publish(
                    exchange='ack_test_exchange',
                    routing_key='manual_ack_queue',
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2  # 持久化
                    )
                )
                
                sent_count += 1
                
                if (i + 1) % 20 == 0:
                    print(f"  已发送: {i + 1}/{message_count}")
        
        except Exception as e:
            print(f"❌ 发送失败: {e}")
        
        finally:
            duration = time.time() - start_time
            connection.close()
        
        return {
            'sent_count': sent_count,
            'duration': duration,
            'throughput': sent_count / duration if duration > 0 else 0
        }
    
    def manual_ack_consumer(self, message_count: int = 100, consume_time: float = 5.0):
        """手动确认消费者"""
        print(f"📥 启动手动确认消费者 (预计处理 {message_count} 条消息)")
        
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        # 公平调度
        channel.basic_qos(prefetch_count=5)
        
        processed_count = 0
        start_time = time.time()
        
        def manual_callback(ch, method, properties, body):
            nonlocal processed_count
            
            try:
                message = json.loads(body.decode())
                message_id = message['id']
                sent_time = message['timestamp']
                
                # 模拟消息处理
                time.sleep(0.02)  # 20ms处理时间
                
                received_time = time.time()
                processing_time = received_time - sent_time
                
                # 模拟处理失败的情况（10%失败率）
                if processed_count % 10 == 0:
                    # 拒绝消息但不重新入队
                    ch.basic_nack(
                        delivery_tag=method.delivery_tag,
                        requeue=False
                    )
                    
                    result = MessageResult(
                        message_id=message_id,
                        ack_mode='manual',
                        sent_time=sent_time,
                        received_time=received_time,
                        processing_time=processing_time,
                        status='failed',
                        retry_count=0
                    )
                else:
                    # 正常确认
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                    result = MessageResult(
                        message_id=message_id,
                        ack_mode='manual',
                        sent_time=sent_time,
                        received_time=received_time,
                        processing_time=processing_time,
                        status='success',
                        retry_count=0
                    )
                
                self.tracker.add_result(result)
                processed_count += 1
                
                if processed_count % 20 == 0:
                    elapsed = time.time() - start_time
                    print(f"  已处理: {processed_count}/{message_count}, 耗时: {elapsed:.1f}s")
                
            except Exception as e:
                print(f"❌ 处理消息失败: {e}")
        
        # 手动确认消费
        channel.basic_consume(
            queue='manual_ack_queue',
            on_message_callback=manual_callback,
            auto_ack=False
        )
        
        try:
            # 设置消费超时
            timeout_start = time.time()
            while processed_count < message_count:
                if time.time() - timeout_start > consume_time:
                    break
                connection.process_data_events(time_limit=1.0)
                
        except KeyboardInterrupt:
            print("⏹️ 消费者被中断")
        finally:
            connection.close()
        
        print(f"✅ 手动确认消费完成，处理了 {processed_count} 条消息")
    
    def batch_ack_demo(self, message_count: int = 100):
        """批量确认演示"""
        print(f"\n📦 批量确认演示 (处理 {message_count} 条消息)")
        
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        # 较高的预取数量
        channel.basic_qos(prefetch_count=20)
        
        processed_count = 0
        batch_size = 5
        current_batch = []
        start_time = time.time()
        
        def batch_callback(ch, method, properties, body):
            nonlocal processed_count, current_batch
            
            try:
                message = json.loads(body.decode())
                message_id = message['id']
                sent_time = message['timestamp']
                
                # 模拟消息处理
                time.sleep(0.015)  # 15ms处理时间
                
                received_time = time.time()
                processing_time = received_time - sent_time
                
                current_batch.append((message_id, sent_time, received_time, processing_time))
                processed_count += 1
                
                # 批量确认
                if processed_count % batch_size == 0 or processed_count == message_count:
                    # 确认当前批次
                    ch.basic_ack(delivery_tag=method.delivery_tag, multiple=True)
                    
                    # 记录结果
                    for msg_id, s_time, r_time, p_time in current_batch:
                        result = MessageResult(
                            message_id=msg_id,
                            ack_mode='batch',
                            sent_time=s_time,
                            received_time=r_time,
                            processing_time=p_time,
                            status='success',
                            retry_count=0
                        )
                        self.tracker.add_result(result)
                    
                    current_batch.clear()
                    
                    if processed_count % (batch_size * 4) == 0:
                        elapsed = time.time() - start_time
                        print(f"  已处理: {processed_count}/{message_count}, 耗时: {elapsed:.1f}s")
                
            except Exception as e:
                print(f"❌ 处理消息失败: {e}")
        
        # 消费消息
        channel.basic_consume(
            queue='batch_ack_queue',
            on_message_callback=batch_callback,
            auto_ack=False
        )
        
        try:
            # 发送测试消息
            for i in range(message_count):
                test_message = {
                    'id': str(uuid.uuid4()),
                    'content': f'批量确认消息 {i+1}',
                    'timestamp': time.time(),
                    'mode': 'batch'
                }
                
                channel.basic_publish(
                    exchange='ack_test_exchange',
                    routing_key='batch_ack_queue',
                    body=json.dumps(test_message)
                )
                
                if (i + 1) % 20 == 0:
                    print(f"  已发送: {i + 1}/{message_count}")
            
            # 开始消费
            connection.process_data_events(time_limit=30.0)
                
        except Exception as e:
            print(f"❌ 批量确认演示失败: {e}")
        finally:
            connection.close()
        
        print(f"✅ 批量确认演示完成")
    
    def transaction_demo(self, message_count: int = 20):
        """事务演示"""
        print(f"\n🔄 事务演示 (发送 {message_count} 条消息)")
        
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        start_time = time.time()
        success_count = 0
        
        try:
            # 开始事务
            channel.tx_select()
            
            for i in range(message_count):
                message = {
                    'id': str(uuid.uuid4()),
                    'content': f'事务消息 {i+1}',
                    'timestamp': time.time(),
                    'mode': 'transaction'
                }
                
                try:
                    channel.basic_publish(
                        exchange='ack_test_exchange',
                        routing_key='transaction_queue',
                        body=json.dumps(message)
                    )
                    
                    # 模拟在第10条消息时发生错误
                    if i == 10:
                        raise Exception("模拟事务错误")
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"❌ 事务中发生错误: {e}")
                    print("🔄 执行事务回滚")
                    
                    # 回滚事务
                    channel.tx_rollback()
                    
                    # 重新开始事务
                    channel.tx_select()
                    
                    # 重新发送之前的消息（从第0条开始）
                    for j in range(i + 1):
                        retry_message = {
                            'id': str(uuid.uuid4()),
                            'content': f'重试事务消息 {j+1}',
                            'timestamp': time.time(),
                            'mode': 'retry'
                        }
                        
                        channel.basic_publish(
                            exchange='ack_test_exchange',
                            routing_key='transaction_queue',
                            body=json.dumps(retry_message)
                        )
                        success_count += 1
                    
                    break
            
            # 提交事务
            channel.tx_commit()
            print("✅ 事务提交成功")
            
        except Exception as e:
            print(f"❌ 事务执行失败: {e}")
        finally:
            duration = time.time() - start_time
            connection.close()
        
        return {
            'total_attempts': message_count,
            'success_count': success_count,
            'duration': duration
        }
    
    def run_comparison_test(self):
        """运行对比测试"""
        print("🧪 开始消息确认策略对比测试")
        print("=" * 60)
        
        # 设置队列
        self.setup_queues()
        
        # 测试参数
        message_count = 50
        consume_time = 15.0
        
        # 1. 自动确认测试
        print("\n📊 测试1: 自动确认模式")
        producer_result = self.auto_ack_producer(message_count)
        self.test_results['auto_producer'] = producer_result
        
        # 启动消费者线程
        consumer_thread = threading.Thread(
            target=self.auto_ack_consumer,
            args=(message_count, consume_time)
        )
        consumer_thread.start()
        consumer_thread.join()
        
        self.tracker.print_statistics("自动确认")
        
        # 2. 手动确认测试
        print("\n📊 测试2: 手动确认模式")
        producer_result = self.manual_ack_producer(message_count)
        self.test_results['manual_producer'] = producer_result
        
        consumer_thread = threading.Thread(
            target=self.manual_ack_consumer,
            args=(message_count, consume_time)
        )
        consumer_thread.start()
        consumer_thread.join()
        
        self.tracker.print_statistics("手动确认")
        
        # 3. 批量确认测试
        print("\n📊 测试3: 批量确认模式")
        self.batch_ack_demo(message_count)
        
        self.tracker.print_statistics("批量确认")
        
        # 4. 事务测试
        print("\n📊 测试4: 事务模式")
        transaction_result = self.transaction_demo(20)
        self.test_results['transaction'] = transaction_result
        
        # 生成对比报告
        self.generate_comparison_report()
    
    def generate_comparison_report(self):
        """生成对比报告"""
        print("\n" + "=" * 60)
        print("📈 消息确认策略对比报告")
        print("=" * 60)
        
        # 生产者性能
        print("\n📤 生产者性能对比:")
        for key, result in self.test_results.items():
            if 'producer' in key:
                mode_name = key.split('_')[0].capitalize()
                print(f"  {mode_name}模式:")
                print(f"    发送数量: {result['sent_count']}")
                print(f"    持续时间: {result['duration']:.3f}s")
                print(f"    吞吐量: {result['throughput']:.2f} 消息/秒")
        
        # 消费者性能
        print("\n📥 消费者性能对比:")
        auto_stats = self.tracker.get_statistics()
        if auto_stats:
            print("  自动确认模式:")
            print(f"    成功率: {auto_stats['success_rate']:.2f}%")
            print(f"    平均处理时间: {auto_stats['avg_processing_time']:.4f}s")
        
        # 事务性能
        if 'transaction' in self.test_results:
            tx_result = self.test_results['transaction']
            print("  事务模式:")
            print(f"    尝试发送: {tx_result['total_attempts']}")
            print(f"    成功发送: {tx_result['success_count']}")
            print(f"    持续时间: {tx_result['duration']:.3f}s")
        
        # 建议
        print("\n💡 选择建议:")
        print("  自动确认: 性能最高，但可能丢失消息，适合非关键数据")
        print("  手动确认: 可靠性最佳，适合关键业务消息")
        print("  批量确认: 平衡性能和可靠性，适合中等规模应用")
        print("  事务模式: 保证原子性，但性能较低，适合强一致性场景")

def main():
    """主函数"""
    print("🚀 消息确认策略对比演示")
    print("确保RabbitMQ服务正在运行...")
    
    try:
        # 创建演示实例
        demo = AcknowledgmentStrategyDemo()
        
        # 运行对比测试
        demo.run_comparison_test()
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        print("请确保:")
        print("1. RabbitMQ服务正在运行")
        print("2. 可以连接到 localhost:5672")
        print("3. 已安装 pika 库: pip install pika")

if __name__ == "__main__":
    main()