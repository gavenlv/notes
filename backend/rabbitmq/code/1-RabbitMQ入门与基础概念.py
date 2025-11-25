"""
RabbitMQ入门与基础概念 - 完整可运行代码
本章包含以下内容：
1. 基本的生产者和消费者示例
2. 连接管理和连接池
3. 消息持久化和确认机制
4. 资源限制和TTL设置
5. 错误处理和重连机制
"""

import pika
import pika_pool
import time
import threading
import logging
import sys
import os
import random
import json
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# RabbitMQ连接参数
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'
RABBITMQ_VHOST = '/'

class RabbitMQManager:
    """RabbitMQ连接管理器"""
    
    def __init__(self, host=RABBITMQ_HOST, port=RABBITMQ_PORT, 
                 username=RABBITMQ_USER, password=RABBITMQ_PASS, 
                 virtual_host=RABBITMQ_VHOST):
        """初始化RabbitMQ连接参数"""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.connection = None
        self.channel = None
        self.connection_pool = None
        
    def create_connection_params(self):
        """创建连接参数"""
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=credentials,
            heartbeat=600,  # 心跳间隔
            blocked_connection_timeout=300  # 阻塞连接超时
        )
        return parameters
    
    def connect(self):
        """建立连接"""
        try:
            parameters = self.create_connection_params()
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("成功连接到RabbitMQ服务器")
            return True
        except Exception as e:
            logger.error(f"连接RabbitMQ失败: {e}")
            return False
    
    def connect_with_retry(self, max_retries=5, retry_interval=5):
        """带重试的连接方法"""
        for i in range(max_retries):
            try:
                if self.connect():
                    return True
                logger.warning(f"连接失败，第{i+1}次尝试，{retry_interval}秒后重试...")
                time.sleep(retry_interval)
            except Exception as e:
                logger.error(f"连接异常: {e}")
                if i < max_retries - 1:
                    time.sleep(retry_interval)
        logger.error("连接RabbitMQ失败，已达到最大重试次数")
        return False
    
    def create_connection_pool(self, pool_size=5):
        """创建连接池"""
        try:
            self.connection_pool = pika_pool.QueuedConnectionPool(
                create=lambda: pika.BlockingConnection(self.create_connection_params()),
                max_size=pool_size,
                max_overflow=pool_size
            )
            logger.info(f"创建连接池成功，大小为{pool_size}")
            return True
        except Exception as e:
            logger.error(f"创建连接池失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("RabbitMQ连接已关闭")
        except Exception as e:
            logger.error(f"关闭连接时出错: {e}")
    
    def get_connection_from_pool(self):
        """从连接池获取连接"""
        if not self.connection_pool:
            self.create_connection_pool()
        return self.connection_pool.acquire()
    
    def return_connection_to_pool(self, connection):
        """将连接返回连接池"""
        connection.release()


class SimpleProducer:
    """简单消息生产者"""
    
    def __init__(self, rabbitmq_manager):
        """初始化生产者"""
        self.manager = rabbitmq_manager
        self.connection = None
        self.channel = None
    
    def setup(self):
        """设置生产者"""
        self.connection = self.manager.get_connection_from_pool()
        self.channel = self.connection.channel()
        # 启用发布确认
        self.channel.confirm_select()
        logger.info("生产者设置完成，已启用发布确认")
    
    def publish_message(self, queue_name, message, exchange='', routing_key=None, 
                       durable=False, ttl=None, priority=None):
        """发布消息"""
        try:
            # 声明队列
            self.channel.queue_declare(queue=queue_name, durable=durable)
            
            # 设置路由键
            if routing_key is None:
                routing_key = queue_name
            
            # 设置消息属性
            properties = pika.BasicProperties(
                delivery_mode=2 if durable else 1,  # 持久化或非持久化
                priority=priority if priority else 0,  # 优先级
                timestamp=datetime.now(),  # 时间戳
                message_id=f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}",  # 消息ID
            )
            
            # 设置TTL
            if ttl:
                properties.expiration = str(ttl)
            
            # 发布消息
            result = self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message.encode('utf-8'),
                properties=properties
            )
            
            # 等待确认
            if self.channel.wait_for_conflicts(timeout=5):
                logger.info(f"消息发布成功: {message}")
                return True
            else:
                logger.warning("消息发布未确认")
                return False
                
        except Exception as e:
            logger.error(f"发布消息时出错: {e}")
            return False
    
    def close(self):
        """关闭生产者"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection:
                self.manager.return_connection_to_pool(self.connection)
            logger.info("生产者已关闭")
        except Exception as e:
            logger.error(f"关闭生产者时出错: {e}")


class SimpleConsumer:
    """简单消息消费者"""
    
    def __init__(self, rabbitmq_manager):
        """初始化消费者"""
        self.manager = rabbitmq_manager
        self.connection = None
        self.channel = None
        self.consuming = False
    
    def setup(self, queue_name, durable=False, prefetch_count=1, auto_ack=False):
        """设置消费者"""
        self.connection = self.manager.get_connection_from_pool()
        self.channel = self.connection.channel()
        
        # 声明队列
        self.channel.queue_declare(queue=queue_name, durable=durable)
        
        # 设置预取计数
        self.channel.basic_qos(prefetch_count=prefetch_count)
        
        self.queue_name = queue_name
        self.auto_ack = auto_ack
        logger.info(f"消费者设置完成，队列: {queue_name}, 预取计数: {prefetch_count}")
    
    def callback(self, ch, method, properties, body):
        """消息处理回调函数"""
        try:
            message = body.decode('utf-8')
            logger.info(f"收到消息: {message}")
            
            # 模拟消息处理
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)
            
            # 手动确认消息
            if not self.auto_ack:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"消息处理完成并确认: {message}")
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            if not self.auto_ack:
                # 拒绝消息并重新入队
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """开始消费消息"""
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                auto_ack=self.auto_ack,
                on_message_callback=self.callback
            )
            
            self.consuming = True
            logger.info("开始消费消息，按Ctrl+C停止")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("用户中断，停止消费")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"消费消息时出错: {e}")
            self.stop_consuming()
    
    def stop_consuming(self):
        """停止消费消息"""
        if self.consuming:
            self.consuming = False
            if self.channel and not self.channel.is_closed:
                self.channel.stop_consuming()
                logger.info("已停止消费消息")
    
    def close(self):
        """关闭消费者"""
        try:
            self.stop_consuming()
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection:
                self.manager.return_connection_to_pool(self.connection)
            logger.info("消费者已关闭")
        except Exception as e:
            logger.error(f"关闭消费者时出错: {e}")


class TaskQueueDemo:
    """任务队列演示"""
    
    def __init__(self, rabbitmq_manager):
        """初始化任务队列演示"""
        self.manager = rabbitmq_manager
        self.producer = None
        self.consumers = []
    
    def setup_producer(self):
        """设置生产者"""
        self.producer = SimpleProducer(self.manager)
        self.producer.setup()
    
    def setup_consumers(self, num_consumers=2, auto_ack=False):
        """设置多个消费者"""
        self.consumers = []
        
        for i in range(num_consumers):
            consumer = SimpleConsumer(self.manager)
            consumer.setup(
                queue_name="task_queue", 
                durable=True, 
                auto_ack=auto_ack,
                prefetch_count=1
            )
            self.consumers.append(consumer)
            
            # 在单独线程中启动消费者
            consumer_thread = threading.Thread(
                target=consumer.start_consuming,
                daemon=True,
                name=f"Consumer-{i+1}"
            )
            consumer_thread.start()
            logger.info(f"启动消费者线程: Consumer-{i+1}")
        
        # 等待消费者线程启动
        time.sleep(1)
    
    def send_tasks(self, num_tasks=10):
        """发送任务"""
        if not self.producer:
            self.setup_producer()
        
        for i in range(num_tasks):
            task = f"任务 {i+1}"
            dots = '.' * (i + 1)
            message = f"Hello{dots}{task}"
            
            self.producer.publish_message(
                queue_name="task_queue",
                message=message,
                durable=True
            )
            time.sleep(0.2)
    
    def stop_consumers(self):
        """停止所有消费者"""
        for consumer in self.consumers:
            consumer.close()
        self.consumers.clear()
    
    def close(self):
        """关闭任务队列演示"""
        if self.producer:
            self.producer.close()
        self.stop_consumers()


class AdvancedProducer:
    """高级消息生产者，支持复杂消息属性"""
    
    def __init__(self, rabbitmq_manager):
        """初始化高级生产者"""
        self.manager = rabbitmq_manager
        self.connection = None
        self.channel = None
    
    def setup(self):
        """设置高级生产者"""
        self.connection = self.manager.get_connection_from_pool()
        self.channel = self.connection.channel()
        # 启用发布确认
        self.channel.confirm_select()
        logger.info("高级生产者设置完成")
    
    def publish_json_message(self, queue_name, data, exchange='', routing_key=None, 
                           headers=None, correlation_id=None):
        """发布JSON格式的消息"""
        try:
            # 声明队列
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            # 设置路由键
            if routing_key is None:
                routing_key = queue_name
            
            # 转换为JSON
            json_message = json.dumps(data)
            
            # 设置消息属性
            properties = pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2,  # 持久化
                headers=headers or {},
                correlation_id=correlation_id,
                timestamp=datetime.now(),
                message_id=f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
            )
            
            # 发布消息
            result = self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json_message.encode('utf-8'),
                properties=properties
            )
            
            # 等待确认
            if self.channel.wait_for_conflicts(timeout=5):
                logger.info(f"JSON消息发布成功: {json_message}")
                return True
            else:
                logger.warning("JSON消息发布未确认")
                return False
                
        except Exception as e:
            logger.error(f"发布JSON消息时出错: {e}")
            return False
    
    def close(self):
        """关闭高级生产者"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection:
                self.manager.return_connection_to_pool(self.connection)
            logger.info("高级生产者已关闭")
        except Exception as e:
            logger.error(f"关闭高级生产者时出错: {e}")


class AdvancedConsumer:
    """高级消息消费者，支持复杂消息处理"""
    
    def __init__(self, rabbitmq_manager):
        """初始化高级消费者"""
        self.manager = rabbitmq_manager
        self.connection = None
        self.channel = None
        self.consuming = False
        self.processed_count = 0
    
    def setup(self, queue_name, durable=True, prefetch_count=1):
        """设置高级消费者"""
        self.connection = self.manager.get_connection_from_pool()
        self.channel = self.connection.channel()
        
        # 声明队列
        self.channel.queue_declare(queue=queue_name, durable=durable)
        
        # 设置预取计数
        self.channel.basic_qos(prefetch_count=prefetch_count)
        
        self.queue_name = queue_name
        logger.info(f"高级消费者设置完成，队列: {queue_name}")
    
    def json_callback(self, ch, method, properties, body):
        """处理JSON格式消息的回调函数"""
        try:
            # 解析JSON消息
            json_data = json.loads(body.decode('utf-8'))
            
            # 提取消息信息
            content_type = properties.content_type
            headers = properties.headers
            correlation_id = properties.correlation_id
            message_id = properties.message_id
            timestamp = properties.timestamp
            
            logger.info(f"收到JSON消息: {json_data}")
            logger.info(f"消息属性: ID={message_id}, CorrelationID={correlation_id}, Headers={headers}")
            
            # 模拟处理
            processing_time = random.uniform(0.2, 0.8)
            time.sleep(processing_time)
            
            # 增加处理计数
            self.processed_count += 1
            logger.info(f"已处理消息数: {self.processed_count}")
            
            # 确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # 不重新入队
        except Exception as e:
            logger.error(f"处理JSON消息时出错: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # 重新入队
    
    def start_consuming(self):
        """开始消费消息"""
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.json_callback
            )
            
            self.consuming = True
            logger.info("开始消费JSON消息，按Ctrl+C停止")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("用户中断，停止消费")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"消费JSON消息时出错: {e}")
            self.stop_consuming()
    
    def stop_consuming(self):
        """停止消费消息"""
        if self.consuming:
            self.consuming = False
            if self.channel and not self.channel.is_closed:
                self.channel.stop_consuming()
                logger.info("已停止消费JSON消息")
    
    def close(self):
        """关闭高级消费者"""
        try:
            self.stop_consuming()
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection:
                self.manager.return_connection_to_pool(self.connection)
            logger.info("高级消费者已关闭")
        except Exception as e:
            logger.error(f"关闭高级消费者时出错: {e}")


def demo_basic_producer_consumer():
    """演示基本的生产者和消费者"""
    print("\n" + "="*50)
    print("基本生产者和消费者演示")
    print("="*50)
    
    # 创建RabbitMQ管理器
    manager = RabbitMQManager()
    
    if not manager.connect():
        logger.error("无法连接到RabbitMQ，请检查服务是否启动")
        return
    
    try:
        # 创建消费者
        consumer = SimpleConsumer(manager)
        consumer.setup(queue_name="hello")
        
        # 在单独线程中启动消费者
        consumer_thread = threading.Thread(target=consumer.start_consuming, daemon=True)
        consumer_thread.start()
        
        # 等待消费者启动
        time.sleep(1)
        
        # 创建生产者
        producer = SimpleProducer(manager)
        producer.setup()
        
        # 发送消息
        for i in range(5):
            message = f"Hello World! 第{i+1}条消息"
            producer.publish_message(queue_name="hello", message=message)
            time.sleep(0.5)
        
        # 等待消息处理
        time.sleep(2)
        
        # 关闭生产者和消费者
        producer.close()
        consumer.close()
        
    except Exception as e:
        logger.error(f"演示过程中出错: {e}")
    finally:
        manager.close()


def demo_task_queue():
    """演示任务队列"""
    print("\n" + "="*50)
    print("任务队列演示")
    print("="*50)
    
    # 创建RabbitMQ管理器
    manager = RabbitMQManager()
    
    if not manager.connect():
        logger.error("无法连接到RabbitMQ，请检查服务是否启动")
        return
    
    try:
        # 创建任务队列演示
        task_demo = TaskQueueDemo(manager)
        
        # 设置消费者
        task_demo.setup_consumers(num_consumers=2, auto_ack=False)
        
        # 发送任务
        task_demo.send_tasks(num_tasks=10)
        
        # 等待任务处理
        time.sleep(5)
        
        # 关闭任务队列演示
        task_demo.close()
        
    except Exception as e:
        logger.error(f"任务队列演示过程中出错: {e}")
    finally:
        manager.close()


def demo_advanced_messaging():
    """演示高级消息处理"""
    print("\n" + "="*50)
    print("高级消息处理演示")
    print("="*50)
    
    # 创建RabbitMQ管理器
    manager = RabbitMQManager()
    
    if not manager.connect():
        logger.error("无法连接到RabbitMQ，请检查服务是否启动")
        return
    
    try:
        # 创建高级生产者
        producer = AdvancedProducer(manager)
        producer.setup()
        
        # 创建高级消费者
        consumer = AdvancedConsumer(manager)
        consumer.setup(queue_name="advanced_queue")
        
        # 在单独线程中启动消费者
        consumer_thread = threading.Thread(target=consumer.start_consuming, daemon=True)
        consumer_thread.start()
        
        # 等待消费者启动
        time.sleep(1)
        
        # 发送JSON消息
        for i in range(5):
            data = {
                "id": i+1,
                "name": f"产品{i+1}",
                "price": round(random.uniform(10.0, 100.0), 2),
                "category": random.choice(["电子产品", "家居用品", "服装", "食品"]),
                "in_stock": random.choice([True, False])
            }
            
            headers = {
                "source": "demo",
                "priority": random.choice(["high", "medium", "low"])
            }
            
            producer.publish_json_message(
                queue_name="advanced_queue",
                data=data,
                headers=headers,
                correlation_id=f"req_{i+1}"
            )
            time.sleep(0.5)
        
        # 等待消息处理
        time.sleep(3)
        
        # 关闭生产者和消费者
        producer.close()
        consumer.close()
        
    except Exception as e:
        logger.error(f"高级消息处理演示过程中出错: {e}")
    finally:
        manager.close()


def demo_connection_pool():
    """演示连接池的使用"""
    print("\n" + "="*50)
    print("连接池演示")
    print("="*50)
    
    # 创建RabbitMQ管理器
    manager = RabbitMQManager()
    
    if not manager.create_connection_pool(pool_size=3):
        logger.error("无法创建连接池")
        return
    
    def worker(worker_id):
        """工作线程函数"""
        try:
            with manager.get_connection_from_pool() as connection:
                with connection.channel() as channel:
                    # 声明队列
                    queue_name = f"worker_{worker_id}_queue"
                    channel.queue_declare(queue=queue_name)
                    
                    # 发送消息
                    message = f"来自工作线程 {worker_id} 的消息"
                    channel.basic_publish(
                        exchange='',
                        routing_key=queue_name,
                        body=message.encode('utf-8')
                    )
                    
                    logger.info(f"工作线程 {worker_id} 发送了消息")
                    
                    # 模拟工作
                    time.sleep(1)
        except Exception as e:
            logger.error(f"工作线程 {worker_id} 出错: {e}")
    
    try:
        # 创建多个工作线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i+1,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        logger.info("所有工作线程已完成")
        
    except Exception as e:
        logger.error(f"连接池演示过程中出错: {e}")
    finally:
        if manager.connection_pool:
            manager.connection_pool.close()


def main():
    """主函数"""
    print("RabbitMQ入门与基础概念 - 完整代码示例")
    print("请确保RabbitMQ服务正在运行")
    
    # 检查RabbitMQ连接
    manager = RabbitMQManager()
    if not manager.connect():
        print("\n错误: 无法连接到RabbitMQ服务器")
        print("请检查:")
        print("1. RabbitMQ服务是否正在运行")
        print("2. 连接参数是否正确 (主机: localhost, 端口: 5672)")
        print("3. 用户名和密码是否正确 (默认: guest/guest)")
        return
    manager.close()
    
    print("\n连接RabbitMQ成功!")
    
    # 运行演示
    demo_basic_producer_consumer()
    time.sleep(2)
    
    demo_task_queue()
    time.sleep(2)
    
    demo_advanced_messaging()
    time.sleep(2)
    
    demo_connection_pool()
    
    print("\n" + "="*50)
    print("所有演示完成!")
    print("="*50)


if __name__ == "__main__":
    main()