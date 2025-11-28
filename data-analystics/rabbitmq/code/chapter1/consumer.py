#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第1章：RabbitMQ第一个Hello World程序 - 消费者
这个程序演示如何从RabbitMQ接收消息

使用方法:
    python consumer.py                    # 普通模式
    python consumer.py confirm            # 确认模式
    python consumer.py batch              # 批量处理模式
"""

import pika
import time
import sys
import signal
import threading


class RabbitMQConsumer:
    """RabbitMQ消费者类"""
    
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None
        self.running = False
        self.message_count = 0
        self.processed_count = 0
        
        # 注册信号处理器，用于优雅关闭
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """信号处理器，优雅关闭程序"""
        print(f"\n [INFO] 收到信号 {signum}，正在优雅关闭...")
        self.stop()
        sys.exit(0)
    
    def connect(self):
        """连接到RabbitMQ"""
        try:
            print(f" [INFO] 连接到 RabbitMQ ({self.host}:{self.port})...")
            
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    # credentials=pika.PlainCredentials('guest', 'guest')
                )
            )
            
            self.channel = self.connection.channel()
            
            # 声明队列
            self.channel.queue_declare(queue='hello', durable=True)
            print(" [✓] 连接成功，队列 'hello' 就绪")
            
            return True
            
        except Exception as e:
            print(f" [✗] 连接失败: {e}")
            return False
    
    def stop(self):
        """停止消费，关闭连接"""
        self.running = False
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print(" [✓] 连接已关闭")
    
    def basic_callback(self, ch, method, properties, body):
        """
        基础消息回调函数
        """
        message = body.decode('utf-8')
        self.message_count += 1
        
        print(f" [📥] 接收消息 #{self.message_count}: '{message}'")
        
        # 模拟消息处理时间
        processing_time = len(message) * 0.1  # 简单的处理时间模拟
        time.sleep(processing_time)
        
        print(f" [⚙️] 处理中... (耗时 {processing_time:.1f}秒)")
        print(f" [✅] 处理完成: '{message}'")
        
        # 手动确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)
        self.processed_count += 1
        
        print(f" [📊] 已处理 {self.processed_count} 条消息")
        print("-" * 50)
    
    def callback_with_confirmation(self, ch, method, properties, body):
        """
        带确认机制的消息回调函数
        """
        message = body.decode('utf-8')
        self.message_count += 1
        
        print(f" [📥] 接收消息 #{self.message_count}: '{message}'")
        
        try:
            # 模拟可能失败的处理
            if "error" in message.lower():
                raise Exception("模拟处理错误：消息包含'error'")
            if "fail" in message.lower():
                raise Exception("模拟处理失败：消息包含'fail'")
            
            # 正常处理时间
            processing_time = 2
            print(f" [⚙️] 开始处理... (预计耗时 {processing_time}秒)")
            time.sleep(processing_time)
            
            print(f" [✅] 处理成功: '{message}'")
            
            # 确认消息已成功处理
            ch.basic_ack(delivery_tag=method.delivery_tag)
            self.processed_count += 1
            
        except Exception as e:
            print(f" [❌] 处理失败: '{message}'")
            print(f" [💡] 错误信息: {e}")
            print(f" [🔄] 消息将被重新放回队列")
            
            # 拒绝消息并重新放回队列
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        print(f" [📊] 总计接收: {self.message_count}, 成功处理: {self.processed_count}")
        print("-" * 50)
    
    def batch_callback(self, ch, method, properties, body):
        """
        批量处理消息的回调函数
        """
        message = body.decode('utf-8')
        self.message_count += 1
        
        print(f" [📦] 批量处理 - 消息 #{self.message_count}: '{message}'")
        
        # 批量处理逻辑
        batch_size = 5
        if self.message_count % batch_size == 0:
            print(f" [📊] 达到批次大小 {batch_size}，执行批量操作...")
            time.sleep(3)  # 模拟批量处理的额外时间
            print(f" [✅] 批次 {self.message_count//batch_size} 处理完成")
        
        # 正常处理
        processing_time = 1
        time.sleep(processing_time)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        self.processed_count += 1
        
        print(f" [✅] 消息处理完成 (总耗时 {processing_time}秒)")
    
    def start_consuming(self, mode="basic"):
        """
        开始消费消息
        
        Args:
            mode (str): 消费模式 ('basic', 'confirm', 'batch')
        """
        if not self.connect():
            return False
        
        print(f" [INFO] 启动 {mode} 消费模式")
        print(" [INFO] 按 Ctrl+C 退出")
        print("=" * 60)
        
        # 选择回调函数
        if mode == "confirm":
            callback = self.callback_with_confirmation
        elif mode == "batch":
            callback = self.batch_callback
        else:
            callback = self.basic_callback
        
        self.running = True
        
        try:
            # 设置消费者
            self.channel.basic_consume(
                queue='hello',
                on_message_callback=callback,
                auto_ack=False  # 手动确认
            )
            
            # 开始消费（这会阻塞直到收到停止信号）
            while self.running:
                try:
                    # 设置超时，以便能够检查running状态
                    self.connection.process_data_events(time_limit=1)
                except Exception as e:
                    print(f" [✗] 处理消息时出错: {e}")
                    break
                    
        except KeyboardInterrupt:
            print("\n [INFO] 用户中断")
        except Exception as e:
            print(f" [✗] 消费过程中出错: {e}")
        finally:
            self.stop()
        
        return True
    
    def get_stats(self):
        """获取统计信息"""
        return {
            'message_count': self.message_count,
            'processed_count': self.processed_count,
            'success_rate': self.processed_count / max(1, self.message_count)
        }


def main():
    """主函数"""
    print("=" * 60)
    print("RabbitMQ Hello World - 消费者程序")
    print("=" * 60)
    
    # 创建消费者实例
    consumer = RabbitMQConsumer()
    
    # 解析命令行参数
    mode = "basic"
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    
    # 启动消费
    consumer.start_consuming(mode)
    
    # 显示统计信息
    stats = consumer.get_stats()
    print(f"\n [📊] 最终统计:")
    print(f"     接收消息总数: {stats['message_count']}")
    print(f"     成功处理数: {stats['processed_count']}")
    print(f"     成功率: {stats['success_rate']:.1%}")
    
    print("\n [INFO] 程序退出")
    
    # 使用方法说明
    print(f"\n [TIP] 使用方法:")
    print(f"   python consumer.py                    # 基础消费模式")
    print(f"   python consumer.py confirm            # 确认机制模式")
    print(f"   python consumer.py batch              # 批量处理模式")


if __name__ == "__main__":
    main()
