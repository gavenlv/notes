# 第1章：RabbitMQ基础入门

> 本章为RabbitMQ学习的起点，适合零基础的读者。我们将从最基本的概念开始，逐步深入，确保每个人都能理解并掌握。

## 目录
1. [什么是消息队列](#什么是消息队列)
2. [RabbitMQ简介](#rabbitmq简介)
3. [为什么选择RabbitMQ](#为什么选择rabbitmq)
4. [核心概念解析](#核心概念解析)
5. [安装与配置](#安装与配置)
6. [管理界面使用](#管理界面使用)
7. [第一个Hello World程序](#第一个hello-world程序)
8. [实验验证](#实验验证)

---

## 什么是消息队列

### 基本概念

**消息队列（Message Queue）** 是一种异步通信方式，用于应用程序之间的通信。就像邮局一样，发送方把消息放入"队列"，接收方从"队列"中取出消息进行处理。

### 生活类比

想象您在餐厅点餐：
- **传统方式（同步）**：您坐在桌子旁，等厨师做完每一道菜才上下一道菜
- **消息队列方式（异步）**：您点完餐，服务员给您一个号牌，您可以去做其他事情，厨师做好后会叫号

### 消息队列的优势

1. **解耦**：发送者和接收者不需要同时在线
2. **异步处理**：提高系统响应速度
3. **削峰填谷**：平滑处理高并发请求
4. **可靠性**：消息持久化，防止丢失
5. **扩展性**：支持分布式部署和负载均衡

---

## RabbitMQ简介

### RabbitMQ是什么

**RabbitMQ** 是基于Erlang开发的一个开源消息代理软件，实现了高级消息队列协议（AMQP）。它就像一个"邮局"，负责接收、存储、转发消息。

### 主要特点

- **可靠性**：支持消息持久化、确认机制
- **灵活性**：多种交换机类型，支持复杂的路由规则
- **易用性**：提供Web管理界面和命令行工具
- **集群支持**：支持分布式部署和高可用
- **多协议支持**：AMQP、MQTT、STOMP等
- **插件系统**：丰富的插件生态系统

### 应用场景

- **微服务通信**：服务间的异步消息传递
- **日志收集**：分布式系统日志聚合
- **任务队列**：后台任务处理
- **事件驱动架构**：基于事件的系统设计
- **数据同步**：数据库间的数据复制

---

## 为什么选择RabbitMQ

### 对比其他消息队列

| 特性 | RabbitMQ | Apache Kafka | Redis Pub/Sub | ActiveMQ |
|------|----------|--------------|---------------|----------|
| **协议** | AMQP | 自定义协议 | Redis协议 | AMQP, OpenWire |
| **可靠性** | 高 | 非常高 | 低 | 高 |
| **性能** | 中等 | 非常高 | 高 | 中等 |
| **学习成本** | 低 | 高 | 很低 | 中等 |
| **集群支持** | 优秀 | 优秀 | 无 | 优秀 |
| **管理界面** | 有 | 无 | 无 | 有 |

### RabbitMQ的适用场景

- **中等规模消息量**：每日百万到千万条消息
- **复杂路由需求**：需要多级路由和消息分发
- **可靠性要求高**：金融、电商等场景
- **快速原型开发**：学习成本低，文档完善

---

## 核心概念解析

### 1. 生产者（Producer）

**定义**：发送消息的应用程序
**作用**：创建消息并发送到RabbitMQ

```python
# 生产者示例
# 就像邮寄信件的人
sender = MessageProducer()
sender.send("Hello World")
```

### 2. 消费者（Consumer）

**定义**：接收消息的应用程序
**作用**：从队列中获取并处理消息

```python
# 消费者示例
# 就像收信的人
receiver = MessageConsumer()
receiver.receive()  # 等待并接收消息
```

### 3. 队列（Queue）

**定义**：存储消息的缓冲区
**特点**：
- 先进先出（FIFO）
- 可以持久化
- 支持多个消费者

```
队列就像邮箱：
┌─────────────────────────────────┐
│  消息1 → 消息2 → 消息3 → 消息4   │
│  ↑                              │
│  下一个被消费的消息               │
└─────────────────────────────────┘
```

### 4. 交换机（Exchange）

**定义**：接收生产者的消息并路由到队列
**作用**：根据规则决定消息的去向

```
交换机就像邮局分拣中心：
生产者 → 交换机 → 根据路由规则 → 不同的队列
```

### 5. 绑定（Binding）

**定义**：交换机和队列之间的路由规则
**作用**：告诉交换机哪些消息应该发送到哪些队列

### 6. 路由键（Routing Key）

**定义**：消息的标识符，用于路由决策
**格式**：通常是点分隔的字符串，如 "order.created"

### 7. AMQP协议

**定义**：高级消息队列协议
**作用**：定义了消息传递的标准格式和语义

---

## 安装与配置

### 系统要求

- **操作系统**：Linux, Windows, macOS
- **Erlang/OTP**：RabbitMQ依赖的运行环境
- **内存**：建议2GB以上
- **磁盘**：根据消息量需求而定

### Windows安装步骤

#### 1. 安装Erlang

```bash
# 下载Erlang安装包
# 访问 https://www.erlang.org/downloads
# 下载最新的OTP Windows 64-bit版本
# 安装并配置环境变量
```

验证安装：
```bash
# 在命令提示符中运行
erl -version
```

#### 2. 安装RabbitMQ

```bash
# 下载RabbitMQ安装包
# 访问 https://www.rabbitmq.com/install-windows.html
# 下载 rabbitmq-server-3.x.x.exe
# 安装并添加到系统服务
```

验证安装：
```bash
# 检查服务状态
rabbitmqctl status
```

#### 3. 启用管理界面

```bash
# 启用管理插件
rabbitmq-plugins enable rabbitmq_management

# 重启服务
net stop RabbitMQ
net start RabbitMQ
```

### Linux安装步骤（Ubuntu/Debian）

#### 1. 安装Erlang

```bash
# 更新软件包列表
sudo apt update

# 安装Erlang
sudo apt install erlang-base erlang-asn1 erlang-crypto erlang-eldap \
    erlang-ftp erlang-inets erlang-mnesia erlang-os-mon erlang-parsetools \
    erlang-public-key erlang-runtime-tools erlang-snmp erlang-ssl \
    erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl

# 验证安装
erl -version
```

#### 2. 安装RabbitMQ

```bash
# 添加RabbitMQ仓库密钥
wget -O- https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/gpg.E495BB49CC3BBE5B.key | sudo apt-key add -

# 添加RabbitMQ仓库
wget -O- https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/gpg.9F4587F226208342.key | sudo apt-key add -

# 更新软件包列表
sudo apt update

# 安装RabbitMQ
sudo apt install rabbitmq-server

# 启用管理界面
sudo rabbitmq-plugins enable rabbitmq_management

# 启动服务
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

### Docker安装（推荐）

```bash
# 拉取RabbitMQ镜像
docker pull rabbitmq:3-management

# 运行容器
docker run -d \
    --hostname my-rabbit \
    --name rabbitmq \
    -p 5672:5672 \
    -p 15672:15672 \
    rabbitmq:3-management

# 查看运行状态
docker ps
```

### 配置管理

#### 配置文件位置

- **Windows**: `C:\Program Files\RabbitMQ Server\rabbitmq_server-3.x.x\etc\`
- **Linux**: `/etc/rabbitmq/`

#### 常用配置

```ini
# rabbitmq.conf 基本配置
loopback_users.guest = false
listeners.tcp.default = 5672
default_user = admin
default_pass = admin123
```

```bash
# 设置管理员用户
rabbitmqctl add_user admin admin123
rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

---

## 管理界面使用

### 访问管理界面

- **URL**: http://localhost:15672
- **默认用户**: guest / guest
- **默认端口**: 15672

### 主要功能

1. **概览页面**
   - 连接数、通道数、队列数
   - 消息速率
   - 集群状态

2. **队列管理**
   - 查看队列状态
   - 队列消息数量
   - 队列属性配置

3. **交换机管理**
   - 查看交换机列表
   - 交换机类型
   - 绑定关系

4. **连接管理**
   - 查看活跃连接
   - 客户端信息
   - 连接状态

5. **用户管理**
   - 用户列表
   - 权限配置
   - 虚拟主机管理

### 常用操作

- **清空队列**: 选择队列 → Delete → 勾选"Delete all messages"
- **查看消息**: 选择队列 → Get messages
- **监控指标**: Charts标签页查看实时数据

---

## 第一个Hello World程序

### Python环境准备

```bash
# 安装Python依赖
pip install pika

# 或者使用conda
conda install -c conda-forge pika
```

### 生产者代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第1章：RabbitMQ第一个Hello World程序 - 生产者
这个程序演示如何向RabbitMQ发送消息
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
        # 1. 建立连接
        # ConnectionParameters用于配置连接参数
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',  # RabbitMQ服务器地址
                port=5672,        # RabbitMQ端口
                # credentials=pika.PlainCredentials('guest', 'guest')  # 如果需要认证
            )
        )
        
        # 2. 创建通道
        # channel是执行AMQP操作的主要接口
        channel = connection.channel()
        
        # 3. 声明队列
        # durable=True表示队列持久化，重启后不会丢失
        channel.queue_declare(queue='hello', durable=True)
        
        # 4. 发送消息
        # exchange=''表示使用默认交换机
        # routing_key='hello'指定队列名称
        # properties设置消息属性
        channel.basic_publish(
            exchange='',              # 默认交换机
            routing_key='hello',      # 队列名称
            body=message,             # 消息内容
            properties=pika.BasicProperties(
                delivery_mode=2,      # 使消息持久化
            )
        )
        
        print(f" [✓] 发送成功: '{message}'")
        
        # 5. 关闭连接
        connection.close()
        
    except Exception as e:
        print(f" [✗] 发送失败: {e}")


def send_multiple_messages(count=5):
    """
    发送多条消息
    
    Args:
        count (int): 消息数量
    """
    print(f"开始发送 {count} 条消息...")
    
    for i in range(count):
        message = f"消息 {i+1}: Hello World!"
        send_message(message)
        time.sleep(1)  # 间隔1秒
        
    print("所有消息发送完成！")


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        custom_message = " ".join(sys.argv[1:])
        send_message(custom_message)
    else:
        # 发送默认消息
        send_message()
        
    # 如果想发送多条消息，可以取消下面的注释
    # send_multiple_messages(10)
```

### 消费者代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第1章：RabbitMQ第一个Hello World程序 - 消费者
这个程序演示如何从RabbitMQ接收消息
"""

import pika
import time
import sys


def receive_message():
    """
    接收消息的函数
    """
    try:
        # 1. 建立连接
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5672,
            )
        )
        
        # 2. 创建通道
        channel = connection.channel()
        
        # 3. 声明队列
        # 注意：消费者和生产者都应该声明队列，避免队列不存在的错误
        channel.queue_declare(queue='hello', durable=True)
        
        print(' [*] 等待消息. 按 Ctrl+C 退出')
        
        # 4. 定义消息处理函数
        def callback(ch, method, properties, body):
            """
            当收到消息时调用的回调函数
            
            Args:
                ch: channel对象
                method: 包含投递信息
                properties: 消息属性
                body: 消息内容
            """
            message = body.decode('utf-8')
            print(f" [x] 收到: '{message}'")
            
            # 模拟消息处理时间
            time.sleep(1)
            print(f" [✓] 处理完成: '{message}'")
            
            # 手动确认消息
            # basic_ack确认消息已被成功处理
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        # 5. 设置消费者
        # queue='hello'指定队列
        # on_message_callback=callback指定处理函数
        # auto_ack=False关闭自动确认，需要手动确认
        channel.basic_consume(
            queue='hello',
            on_message_callback=callback,
            auto_ack=False
        )
        
        # 6. 开始消费消息
        # 这是一个阻塞循环，会持续监听消息
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print("\n [INFO] 用户中断，正在关闭连接...")
        try:
            connection.close()
        except:
            pass
        print(" [INFO] 程序已退出")
        
    except Exception as e:
        print(f" [✗] 接收失败: {e}")


def receive_with_confirmation():
    """
    演示消息确认机制
    """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        channel = connection.channel()
        
        channel.queue_declare(queue='hello', durable=True)
        
        print(' [*] 等待消息 (带确认机制)')
        print('     按 Ctrl+C 退出\n')
        
        def callback_with_confirmation(ch, method, properties, body):
            message = body.decode('utf-8')
            print(f" [📥] 接收: '{message}'")
            
            # 模拟处理过程
            try:
                # 模拟可能失败的处理
                if "error" in message.lower():
                    raise Exception("模拟处理错误")
                
                time.sleep(2)  # 模拟耗时处理
                print(f" [✅] 成功处理: '{message}'")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f" [❌] 处理失败: '{message}' - {e}")
                # 消息会被重新放回队列
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        channel.basic_consume(
            queue='hello',
            on_message_callback=callback_with_confirmation,
            auto_ack=False
        )
        
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print("\n [INFO] 程序退出")
        if 'connection' in locals():
            connection.close()


if __name__ == "__main__":
    print("=" * 50)
    print("RabbitMQ Hello World 消费者")
    print("=" * 50)
    
    # 选择运行模式
    if len(sys.argv) > 1 and sys.argv[1] == "confirm":
        receive_with_confirmation()
    else:
        receive_message()
```

---

## 实验验证

### 实验1：基本消息传递

#### 步骤1：启动消费者

```bash
# 打开一个终端窗口
python consumer.py
```

#### 步骤2：发送消息

```bash
# 打开另一个终端窗口
python producer.py "Hello RabbitMQ!"
```

#### 预期结果
- 消费者显示：收到消息
- 消费者处理完成后显示：处理完成

### 实验2：消息确认机制

#### 步骤1：启动带确认的消费者

```bash
python consumer.py confirm
```

#### 步骤2：发送不同类型的消息

```bash
# 正常消息
python producer.py "正常消息"

# 包含错误的消息
python producer.py "处理这个 error 消息"
```

#### 预期结果
- 正常消息：正常处理和确认
- 错误消息：处理失败，重新放回队列

### 实验3：多个消费者

#### 步骤1：启动多个消费者

```bash
# 终端1
python consumer.py

# 终端2  
python consumer.py
```

#### 步骤2：发送多条消息

```bash
# 发送5条消息
python producer.py "消息1"
python producer.py "消息2"
python producer.py "消息3"
python producer.py "消息4"
python producer.py "消息5"
```

#### 预期结果
- 消息在多个消费者间轮流分发
- 负载自动均衡

### 实验4：管理界面验证

1. 打开浏览器访问：http://localhost:15672
2. 使用 guest/guest 登录
3. 查看"Queues"页面，确认消息数量变化
4. 查看"Connections"页面，查看活跃连接
5. 使用"Get messages"功能查看队列中的消息

---

## 故障排查

### 常见问题

#### 1. 连接失败

**症状**：
```
pika.exceptions.ConnectionClosed: Connection to 127.0.0.1:5672 failed
```

**解决方案**：
- 检查RabbitMQ服务是否启动：`rabbitmqctl status`
- 检查端口是否被占用：`netstat -an | grep 5672`
- 检查防火墙设置

#### 2. 队列不存在

**症状**：
```
Channel closed by server: 404 (NOT-FOUND)
```

**解决方案**：
- 确保生产者和消费者都声明队列
- 检查队列名称拼写

#### 3. 权限问题

**症状**：
```
Access refused: login failed
```

**解决方案**：
- 检查用户名密码
- 检查用户权限配置

### 调试命令

```bash
# 查看RabbitMQ状态
rabbitmqctl status

# 查看队列列表
rabbitmqctl list_queues

# 查看连接列表
rabbitmqctl list_connections

# 清除所有队列
rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl start_app

# 查看日志
tail -f /var/log/rabbitmq/rabbit@hostname.log
```

---

## 本章总结

### 关键概念回顾

- **消息队列**：异步通信方式
- **生产者**：发送消息的应用程序
- **消费者**：接收消息的应用程序
- **队列**：存储消息的缓冲区
- **AMQP协议**：消息传递标准

### 实践要点

- ✅ 成功安装和配置RabbitMQ
- ✅ 理解基本概念
- ✅ 运行第一个Hello World程序
- ✅ 掌握消息发送和接收
- ✅ 理解消息确认机制

### 下章预告

第2章我们将深入学习AMQP协议，了解消息传递的底层机制，以及RabbitMQ的内部架构。这将帮助您更好地理解为什么RabbitMQ如此强大和可靠。

### 练习题

1. **概念理解**：用自己的话解释什么是消息队列，为什么需要它？
2. **实践操作**：在您的环境中安装RabbitMQ，并运行本章的示例代码
3. **思考题**：如果生产者的速度比消费者快，会发生什么情况？
4. **扩展实验**：尝试创建多个队列，观察消息分发情况

---

## 代码文件

- **生产者**: [code/chapter1/producer.py](code/chapter1/producer.py)
- **消费者**: [code/chapter1/consumer.py](code/chapter1/consumer.py)
- **Docker配置**: [code/chapter1/docker-compose.yml](code/chapter1/docker-compose.yml)

---

> **学习建议**：建议读者先理解概念，然后动手实践。不要跳过实验环节，因为实践是学习的最佳方式。如果遇到问题，请参考故障排查部分或查看官方文档。