#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第1章：RabbitMQ第一个Hello World程序 - 生产者
这个程序演示如何向RabbitMQ发送消息

使用方法:
    python producer.py "你的消息内容"
    python producer.py  # 使用默认消息
"""

import pika
import sys
import time


def send_message(message="Hello World!"):
    """
    发送消息到RabbitMQ
    
    Args:
        message (str): 要发送的消息内容
    """
    try:
        print(f" [INFO] 正在连接到 RabbitMQ...")
        
        # 1. 建立连接
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',  # RabbitMQ服务器地址
                port=5672,        # RabbitMQ端口
                # credentials=pika.PlainCredentials('guest', 'guest')  # 如果需要认证
            )
        )
        
        print(" [✓] 连接成功")
        
        # 2. 创建通道
        channel = connection.channel()
        
        # 3. 声明队列
        # durable=True表示队列持久化，重启后不会丢失
        channel.queue_declare(queue='hello', durable=True)
        print(" [✓] 队列 'hello' 声明成功")
        
        # 4. 发送消息
        channel.basic_publish(
            exchange='',              # 默认交换机
            routing_key='hello',      # 队列名称
            body=message,             # 消息内容
            properties=pika.BasicProperties(
                delivery_mode=2,      # 使消息持久化
            )
        )
        
        print(f" [✓] 消息发送成功: '{message}'")
        print(f" [INFO] 消息已路由到队列 'hello'")
        
        # 5. 关闭连接
        connection.close()
        print(" [✓] 连接已关闭")
        
        return True
        
    except Exception as e:
        print(f" [✗] 发送失败: {e}")
        print(" [TIP] 请确保RabbitMQ服务已启动并运行在localhost:5672")
        return False


def send_multiple_messages(count=5, delay=1):
    """
    发送多条消息
    
    Args:
        count (int): 消息数量
        delay (int): 发送间隔（秒）
    """
    print(f"开始发送 {count} 条消息...")
    print("=" * 50)
    
    success_count = 0
    
    for i in range(count):
        message = f"消息 {i+1}: Hello World! 时间: {time.strftime('%H:%M:%S')}"
        
        if send_message(message):
            success_count += 1
        
        if i < count - 1:  # 最后一条消息后不等待
            print(f" [INFO] 等待 {delay} 秒后发送下一条消息...")
            time.sleep(delay)
            print("-" * 30)
        
    print("=" * 50)
    print(f"发送完成！成功发送 {success_count}/{count} 条消息")
    return success_count == count


def send_batch_messages():
    """
    批量发送消息的演示
    """
    messages = [
        "欢迎使用RabbitMQ！",
        "这是第2条消息",
        "这是第3条消息", 
        "这是第4条消息",
        "RabbitMQ很棒！"
    ]
    
    print("批量发送消息演示")
    print("=" * 40)
    
    for i, message in enumerate(messages, 1):
        print(f"发送第 {i} 条消息...")
        send_message(message)
        
        if i < len(messages):
            print("等待2秒...")
            time.sleep(2)
        print("-" * 30)


def test_connection():
    """
    测试RabbitMQ连接
    """
    try:
        print("测试RabbitMQ连接...")
        
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost', port=5672)
        )
        
        # 尝试创建一个通道来测试连接
        channel = connection.channel()
        
        print(" [✓] 连接测试成功！RabbitMQ服务正常运行")
        
        # 获取服务器信息
        connection.close()
        return True
        
    except pika.exceptions.ConnectionClosedByBroker:
        print(" [✗] 连接被服务器拒绝")
        return False
    except pika.exceptions.AMQPConnectionError:
        print(" [✗] 无法连接到RabbitMQ服务")
        print(" [TIP] 请检查:")
        print("   1. RabbitMQ服务是否启动")
        print("   2. 服务是否运行在localhost:5672")
        print("   3. 防火墙是否阻止连接")
        return False
    except Exception as e:
        print(f" [✗] 连接测试失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("RabbitMQ Hello World - 生产者程序")
    print("=" * 60)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # 测试连接
            test_connection()
        elif sys.argv[1] == "batch":
            # 批量发送
            send_batch_messages()
        elif sys.argv[1] == "multi":
            # 发送多条消息
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            send_multiple_messages(count)
        else:
            # 发送自定义消息
            custom_message = " ".join(sys.argv[1:])
            send_message(custom_message)
    else:
        # 发送默认消息
        print("发送默认消息...")
        send_message()
    
    print("\n [INFO] 程序执行完成")
    print(" [TIP] 使用方法:")
    print("   python producer.py                    # 发送默认消息")
    print("   python producer.py '你的消息'          # 发送自定义消息") 
    print("   python producer.py test               # 测试连接")
    print("   python producer.py batch              # 批量发送")
    print("   python producer.py multi 10           # 发送10条消息")