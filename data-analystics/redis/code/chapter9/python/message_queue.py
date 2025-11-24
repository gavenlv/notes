#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis消息队列实现
支持List队列、Pub/Sub、Stream等模式
"""

import redis
import json
import time
import threading
import random
from typing import Any, Callable, List, Optional
from concurrent.futures import ThreadPoolExecutor
from threading import Event


class ListMessageQueue:
    """List队列实现（简单的FIFO队列）"""
    
    def __init__(self, redis_client: redis.Redis, queue_name: str):
        self.redis = redis_client
        self.queue_name = queue_name
    
    def send_message(self, message: Any) -> bool:
        """发送消息"""
        try:
            serialized_message = json.dumps(message)
            self.redis.rpush(self.queue_name, serialized_message)
            return True
        except Exception as e:
            print(f"消息发送失败: {e}")
            return False
    
    def receive_message(self, timeout: int = 30) -> Optional[Any]:
        """接收消息（阻塞）"""
        try:
            # 阻塞弹出消息
            result = self.redis.blpop(self.queue_name, timeout=timeout)
            
            if result is None:
                return None
            
            _, message = result
            return json.loads(message)
        except Exception as e:
            print(f"消息接收失败: {e}")
            return None
    
    def batch_send_messages(self, messages: List[Any]) -> bool:
        """批量发送消息"""
        try:
            serialized_messages = [json.dumps(msg) for msg in messages]
            self.redis.rpush(self.queue_name, *serialized_messages)
            return True
        except Exception as e:
            print(f"批量消息发送失败: {e}")
            return False


class PubSubMessageQueue:
    """Pub/Sub消息队列实现"""
    
    def __init__(self, redis_client: redis.Redis, channel_name: str):
        self.redis = redis_client
        self.channel_name = channel_name
        self.pubsub = self.redis.pubsub()
        self.running = False
        self.thread = None
    
    def publish_message(self, message: Any) -> bool:
        """发布消息"""
        try:
            serialized_message = json.dumps(message)
            self.redis.publish(self.channel_name, serialized_message)
            return True
        except Exception as e:
            print(f"消息发布失败: {e}")
            return False
    
    def subscribe(self, message_handler: Callable[[Any], None]):
        """订阅消息"""
        def message_listener():
            self.pubsub.subscribe(self.channel_name)
            
            for message in self.pubsub.listen():
                if not self.running:
                    break
                
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        message_handler(data)
                    except Exception as e:
                        print(f"消息处理失败: {e}")
        
        self.running = True
        self.thread = threading.Thread(target=message_listener)
        self.thread.daemon = True
        self.thread.start()
    
    def unsubscribe(self):
        """取消订阅"""
        self.running = False
        if self.thread:
            self.pubsub.unsubscribe(self.channel_name)
            self.thread.join(timeout=5)


class StreamMessageQueue:
    """Stream消息队列实现（Redis 5.0+）"""
    
    def __init__(self, redis_client: redis.Redis, stream_name: str):
        self.redis = redis_client
        self.stream_name = stream_name
    
    def send_message(self, message: Any) -> Optional[str]:
        """发送消息"""
        try:
            serialized_message = json.dumps(message)
            
            message_data = {
                'data': serialized_message,
                'timestamp': str(int(time.time()))
            }
            
            # 使用自动生成的ID
            message_id = self.redis.xadd(self.stream_name, message_data)
            return message_id
        except Exception as e:
            print(f"Stream消息发送失败: {e}")
            return None
    
    def read_messages(self, count: int = 10, start_id: str = '0') -> List[Any]:
        """读取消息"""
        try:
            # 从指定位置开始读取
            results = self.redis.xread(
                {self.stream_name: start_id},
                count=count,
                block=0
            )
            
            messages = []
            
            if results:
                for stream_name, entries in results:
                    for entry_id, entry_data in entries:
                        try:
                            message_data = json.loads(entry_data['data'])
                            messages.append({
                                'id': entry_id,
                                'data': message_data,
                                'timestamp': entry_data.get('timestamp', '')
                            })
                        except Exception as e:
                            print(f"消息解析失败: {e}")
            
            return messages
        except Exception as e:
            print(f"Stream消息读取失败: {e}")
            return []
    
    def create_consumer_group(self, group_name: str, start_id: str = '0') -> bool:
        """创建消费者组"""
        try:
            self.redis.xgroup_create(self.stream_name, group_name, start_id, mkstream=True)
            return True
        except Exception as e:
            # 如果组已存在，忽略错误
            if "BUSYGROUP" in str(e):
                return True
            print(f"创建消费者组失败: {e}")
            return False
    
    def read_messages_by_group(self, group_name: str, consumer_name: str, 
                              count: int = 10) -> List[Any]:
        """消费者组读取消息"""
        try:
            # 消费者组读取
            results = self.redis.xreadgroup(
                group_name, 
                consumer_name,
                {self.stream_name: '>'},
                count=count,
                block=5000
            )
            
            messages = []
            
            if results:
                for stream_name, entries in results:
                    for entry_id, entry_data in entries:
                        try:
                            message_data = json.loads(entry_data['data'])
                            messages.append({
                                'id': entry_id,
                                'data': message_data,
                                'timestamp': entry_data.get('timestamp', '')
                            })
                            
                            # 确认消息处理
                            self.redis.xack(self.stream_name, group_name, entry_id)
                        except Exception as e:
                            print(f"消息解析失败: {e}")
            
            return messages
        except Exception as e:
            print(f"消费者组消息读取失败: {e}")
            return []


class DelayedMessageQueue:
    """延迟消息队列实现"""
    
    def __init__(self, redis_client: redis.Redis, queue_name: str):
        self.redis = redis_client
        self.queue_name = queue_name
        self.delayed_set = f"{queue_name}:delayed"
        self.running = False
        self.thread = None
    
    def send_delayed_message(self, message: Any, delay_seconds: int) -> bool:
        """发送延迟消息"""
        try:
            serialized_message = json.dumps(message)
            deliver_time = int(time.time()) + delay_seconds
            
            # 使用有序集合存储延迟消息
            self.redis.zadd(self.delayed_set, {serialized_message: deliver_time})
            
            # 启动检查线程（如果未运行）
            if not self.running:
                self.start_delivery_check()
            
            return True
        except Exception as e:
            print(f"延迟消息发送失败: {e}")
            return False
    
    def start_delivery_check(self):
        """启动投递检查线程"""
        def delivery_checker():
            while self.running:
                try:
                    current_time = int(time.time())
                    
                    # 获取所有到期的消息
                    expired_messages = self.redis.zrangebyscore(
                        self.delayed_set, 0, current_time
                    )
                    
                    if expired_messages:
                        # 投递到实际队列
                        self.redis.rpush(self.queue_name, *expired_messages)
                        
                        # 从延迟队列中移除
                        self.redis.zremrangebyscore(self.delayed_set, 0, current_time)
                    
                    # 每秒检查一次
                    time.sleep(1)
                except Exception as e:
                    print(f"投递检查失败: {e}")
                    time.sleep(5)  # 错误时等待更长时间
        
        self.running = True
        self.thread = threading.Thread(target=delivery_checker)
        self.thread.daemon = True
        self.thread.start()
    
    def receive_message(self, timeout: int = 30) -> Optional[Any]:
        """接收消息"""
        try:
            result = self.redis.blpop(self.queue_name, timeout=timeout)
            
            if result is None:
                return None
            
            _, message = result
            return json.loads(message)
        except Exception as e:
            print(f"消息接收失败: {e}")
            return None
    
    def stop(self):
        """停止队列"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)


def test_message_queues():
    """测试消息队列功能"""
    # 创建Redis连接
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    print("=== 测试List消息队列 ===")
    list_queue = ListMessageQueue(r, "test:list:queue")
    
    # 发送测试消息
    test_message = {"type": "test", "content": "Hello List Queue"}
    list_queue.send_message(test_message)
    
    # 接收消息
    received_message = list_queue.receive_message(timeout=5)
    print(f"List队列接收消息: {received_message}")
    
    print("\n=== 测试Pub/Sub消息队列 ===")
    pubsub_queue = PubSubMessageQueue(r, "test:pubsub:channel")
    
    # 使用事件等待消息接收
    message_received = Event()
    received_messages = []
    
    def message_handler(message):
        received_messages.append(message)
        print(f"Pub/Sub队列接收消息: {message}")
        message_received.set()
    
    # 订阅消息
    pubsub_queue.subscribe(message_handler)
    
    # 等待订阅建立
    time.sleep(0.1)
    
    # 发布消息
    pubsub_message = {"type": "test", "content": "Hello Pub/Sub"}
    pubsub_queue.publish_message(pubsub_message)
    
    # 等待消息接收
    message_received.wait(timeout=5)
    pubsub_queue.unsubscribe()
    
    print("\n=== 测试Stream消息队列 ===")
    stream_queue = StreamMessageQueue(r, "test:stream:queue")
    
    # 发送消息
    stream_message = {"type": "test", "content": "Hello Stream"}
    message_id = stream_queue.send_message(stream_message)
    print(f"Stream队列发送消息，ID: {message_id}")
    
    # 读取消息
    stream_messages = stream_queue.read_messages(count=10)
    print(f"Stream队列读取消息: {stream_messages}")
    
    # 测试消费者组
    print("\n=== 测试Stream消费者组 ===")
    stream_queue.create_consumer_group("test_group", "0")
    
    # 消费者组读取
    group_messages = stream_queue.read_messages_by_group(
        "test_group", "consumer1", count=10
    )
    print(f"消费者组读取消息: {group_messages}")
    
    print("\n=== 测试延迟消息队列 ===")
    delayed_queue = DelayedMessageQueue(r, "test:delayed:queue")
    
    # 发送延迟消息（2秒后投递）
    delayed_message = {"type": "test", "content": "Hello Delayed Queue"}
    delayed_queue.send_delayed_message(delayed_message, 2)
    
    # 立即尝试接收（应该收不到）
    immediate_message = delayed_queue.receive_message(timeout=1)
    print(f"立即接收延迟消息: {immediate_message}")
    
    # 等待2秒后接收
    time.sleep(2.5)
    delayed_received_message = delayed_queue.receive_message(timeout=1)
    print(f"延迟后接收消息: {delayed_received_message}")
    
    delayed_queue.stop()
    
    print("\n消息队列测试完成!")


if __name__ == "__main__":
    test_message_queues()