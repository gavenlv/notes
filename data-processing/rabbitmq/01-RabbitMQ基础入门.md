# 第1章：RabbitMQ基础入门

## 概述

RabbitMQ是一个功能强大的开源消息代理软件，基于AMQP（Advanced Message Queuing Protocol）协议标准。它提供了一个完整的消息队列系统，支持可靠、高性能、可扩展的消息传递机制。本章将介绍RabbitMQ的基本概念、架构原理、核心组件以及基础配置和安装。

## 目录

1. [消息队列概述](#1-消息队列概述)
2. [RabbitMQ简介](#2-rabbitmq简介)
3. [AMQP协议详解](#3-amqp协议详解)
4. [RabbitMQ架构组件](#4-rabbitmq架构组件)
5. [核心概念解析](#5-核心概念解析)
6. [安装与配置](#6-安装与配置)
7. [第一个应用示例](#7-第一个应用示例)
8. [工作模式详解](#8-工作模式详解)
9. [管理界面使用](#9-管理界面使用)
10. [常用命令与工具](#10-常用命令与工具)

---

## 1. 消息队列概述

### 1.1 什么是消息队列

消息队列（Message Queue，简称MQ）是一种进程间通信或同一进程内线程间通信的实现方式，允许应用程序通过发送和接收消息进行异步通信。

#### 消息队列的核心特性

- **异步性**: 发送方和接收方不需要同时在线，消息存储在队列中等待处理
- **可靠性**: 消息持久化存储，确保消息不会丢失
- **解耦性**: 降低系统各组件之间的直接依赖
- **负载均衡**: 可以让多个消费者共同处理队列中的消息
- **可扩展性**: 可以根据需求动态增加消费者处理能力

#### 消息队列的应用场景

- **异步处理**: 将耗时操作放入消息队列，异步处理提高系统响应速度
- **应用解耦**: 降低不同应用模块之间的直接依赖
- **流量削峰**: 控制系统在高峰期承受的负载压力
- **数据同步**: 不同系统之间的数据同步和一致性保障
- **日志处理**: 日志收集、分析和处理

### 1.2 主流消息队列对比

| 特性 | RabbitMQ | Apache Kafka | ActiveMQ | Redis Queue |
|------|----------|--------------|----------|-------------|
| **协议支持** | AMQP, STOMP, MQTT | 自定义协议 | AMQP, OpenWire, STOMP | RESP |
| **吞吐量** | 中等 | 极高 | 中等 | 中等 |
| **消息可靠性** | 高 | 高 | 高 | 中等 |
| **事务支持** | 支持 | 支持 | 支持 | 不支持 |
| **集群模式** | 支持 | 支持 | 支持 | 支持 |
| **管理界面** | 完善 | 一般 | 完善 | 基础 |
| **学习难度** | 中等 | 高 | 中等 | 低 |

### 1.3 为什么选择RabbitMQ

- **标准化协议**: 基于AMQP标准，确保互操作性
- **丰富的功能**: 支持多种消息模式、确认机制、持久化等
- **完善的生态**: 多种编程语言的客户端库
- **管理界面**: 提供直观的管理控制台
- **活跃社区**: 活跃的开源社区和商业支持
- **企业级特性**: 高可用、集群、镜像等企业级功能

---

## 2. RabbitMQ简介

### 2.1 RabbitMQ历史

RabbitMQ最初由LShift公司开发，后来被SpringSource（现VMware）收购，2013年又被Pivotal分拆。2019年，Rabbit Technologies被VMware收购，成为VMware的一部分。

### 2.2 RabbitMQ特点

#### 技术特点
- **基于Erlang**: 使用Erlang语言开发，具有高并发和高可用特性
- **基于AMQP**: 完全遵循AMQP标准，支持消息传递模式
- **可靠性保证**: 支持消息确认、持久化、事务等可靠性机制
- **灵活的路由**: 支持多种交换机类型和路由策略
- **集群支持**: 支持分布式集群，提供高可用性

#### 业务特点
- **成熟稳定**: 在生产环境中广泛应用，经过大量验证
- **功能丰富**: 支持多种消息模式和企业级特性
- **易于使用**: 相对简单的配置和学习曲线
- **可扩展性**: 支持水平和垂直扩展
- **监控友好**: 提供详细的监控和管理界面

### 2.3 典型使用场景

#### 企业集成
- **微服务架构**: 服务间的异步通信
- **企业服务总线**: 集成不同的企业系统
- **数据同步**: 系统间的数据一致性保障

#### 互联网应用
- **用户行为分析**: 收集和分析用户行为数据
- **订单处理**: 电商订单的异步处理
- **日志聚合**: 分布式日志的收集和分析
- **内容推送**: 消息推送和通知服务

#### 数据处理
- **实时数据处理**: 流式数据处理和计算
- **批处理任务**: 定时任务和批量处理
- **数据管道**: 构建数据处理管道

---

## 3. AMQP协议详解

### 3.1 AMQP概述

AMQP（Advanced Message Queuing Protocol）是一个开放标准的应用层协议，用于消息中间件的通信。它定义了消息传递的通用模型，包括消息的生产、路由、存储和消费。

### 3.2 AMQP核心概念

#### 实体关系
```
Publisher ──→ Exchange ──→ Queue ──→ Consumer
                      │
                      ├─ Binding ──→ Queue
                      │
                      └─ Routing Key
```

#### 基本术语
- **Producer（生产者）**: 发送消息的应用程序
- **Consumer（消费者）**: 接收消息的应用程序
- **Exchange（交换机）**: 接收生产者消息并路由到队列
- **Queue（队列）**: 存储消息的容器
- **Binding（绑定）**: 交换机和队列之间的路由规则
- **Routing Key（路由键）**: 交换机用于路由消息的键
- **Virtual Host（虚拟主机）**: 隔离不同的用户和权限

### 3.3 AMQP消息流

#### 基本流程
1. **生产者发布消息**: 生产者连接AMQP服务器，发布消息到交换机
2. **交换机路由**: 交换机根据绑定规则和路由键确定目标队列
3. **消息存储**: 消息被存储到目标队列中
4. **消费者获取**: 消费者连接到队列，接收消息
5. **消息确认**: 消费者处理消息后发送确认

#### 确认机制
- **生产者确认**: 交换机确认消息收到
- **队列确认**: 队列确认消息存储成功
- **消费者确认**: 消费者确认消息处理完成

### 3.4 AMQP特性

#### 事务支持
```erlang
% AMQP事务示例
ch.tx_select()  % 开启事务
ch.basic_publish(exchange='amq.direct', routing_key='test')
ch.tx_commit()  % 提交事务
```

#### 消息确认
```python
# 自动确认
ch.basic_consume(callback, queue='test')

# 手动确认
ch.basic_consume(callback, queue='test', auto_ack=False)
def callback(ch, method, properties, body):
    try:
        # 业务处理
        process_message(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)  # 确认消息
    except Exception:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # 拒绝消息
```

#### 预取控制
```python
# 设置预取数量，控制消费者并发处理
ch.basic_qos(prefetch_count=10)
```

---

## 4. RabbitMQ架构组件

### 4.1 整体架构

RabbitMQ采用经典的发布/订阅模式架构，主要包含以下组件：

```
┌─────────────────┐    ┌─────────────────┐
│   Producer      │    │   Consumer 1    │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     │
          ┌──────────▼──────────┐
          │     Exchange        │
          │  (Direct/Topic/     │
          │   Fanout/Headers)   │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │      Queue          │
          │  [ Message Store ]  │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │   Consumer N        │
          └─────────────────────┘
```

### 4.2 核心组件详解

#### 4.2.1 连接管理（Connection）

**连接（Connection）**表示AMQP客户端与服务器之间的网络连接。

```python
# 连接示例
import pika

# 创建连接
credentials = pika.PlainCredentials('guest', 'guest')
connection_params = pika.ConnectionParameters(
    host='localhost',
    port=5672,
    credentials=credentials,
    virtual_host='/'
)

connection = pika.BlockingConnection(connection_params)
```

**连接特点**:
- TCP长连接，减少连接开销
- 支持连接池复用
- 自动心跳检测
- 支持SSL/TLS加密

#### 4.2.2 通道（Channel）

**通道（Channel）**是连接内的虚拟连接，用于发送AMQP命令。

```python
# 通道示例
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='hello')

# 发布消息
channel.basic_publish(
    exchange='',
    routing_key='hello',
    body='Hello World!'
)
```

**通道特点**:
- 连接内的轻量级连接
- 支持多通道并发操作
- 线程安全（每个线程使用独立通道）
- 支持事务和确认

#### 4.2.3 交换机（Exchange）

**交换机（Exchange）**接收生产者发送的消息并根据路由规则将消息分发到队列。

```python
# 交换机示例
# 声明直接交换机
channel.exchange_declare(
    exchange='direct_exchange',
    exchange_type='direct'
)

# 发布消息到交换机
channel.basic_publish(
    exchange='direct_exchange',
    routing_key='order.created',
    body='Order created message'
)
```

**交换机类型**:

1. **Direct Exchange（直接交换机）**
   - 完全匹配路由键
   - 适用于点对点通信

2. **Topic Exchange（主题交换机）**
   - 支持通配符匹配（* 和 #）
   - 适用于发布订阅模式

3. **Fanout Exchange（广播交换机）**
   - 忽略路由键，广播到所有绑定队列
   - 适用于广播通知

4. **Headers Exchange（头交换机）**
   - 基于消息头属性匹配
   - 适用于复杂的路由规则

#### 4.2.4 队列（Queue）

**队列（Queue）**是存储消息的缓冲区，遵循FIFO原则。

```python
# 队列示例
channel.queue_declare(
    queue='task_queue',
    durable=True,           # 持久化
    arguments={
        'x-max-priority': 10,        # 最大优先级
        'x-message-ttl': 3600000,    # 消息生存时间
        'x-dead-letter-exchange': 'dlx'  # 死信交换机
    }
)
```

**队列特性**:
- **持久化**: 队列内容在服务器重启后保持
- **优先级**: 支持消息优先级处理
- **TTL**: 消息生存时间限制
- **长度限制**: 队列消息数量和大小限制
- **死信**: 消息过期或拒绝后的处理

#### 4.2.5 绑定（Binding）

**绑定（Binding）**是交换机和队列之间的路由规则定义。

```python
# 绑定示例
channel.queue_bind(
    exchange='topic_exchange',
    queue='task_queue',
    routing_key='order.*'
)
```

**绑定规则**:
- 基于路由键的匹配
- 支持通配符（* 和 #）
- 可以指定头属性匹配
- 支持参数化配置

### 4.3 虚拟主机（Virtual Host）

**虚拟主机**提供逻辑隔离，将不同的应用或用户分配到不同的虚拟主机中。

```python
# 虚拟主机示例
connection_params = pika.ConnectionParameters(
    host='localhost',
    virtual_host='my_app'
)
```

**虚拟主机特点**:
- 逻辑隔离不同应用
- 独立的用户权限管理
- 独立的交换机和队列命名空间
- 资源配额和限制

---

## 5. 核心概念解析

### 5.1 消息生命周期

#### 消息状态转换
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Published │───▶│  Enqueued   │───▶│   Ready     │
└─────────────┘    └─────────────┘    └─────────────┘
                                               │
                                               ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Deleted   │◀───│   Unacked   │◀───│   Fetched   │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### 详细状态说明
- **Published**: 消息刚发布到交换机
- **Enqueued**: 消息进入队列
- **Ready**: 消息可以被消费者获取
- **Fetched**: 消息被消费者获取但未确认
- **Unacked**: 消息已发送给消费者，等待确认
- **Deleted**: 消息已被确认处理完成

### 5.2 消息确认机制

#### 5.2.1 生产者确认
```python
# 开启发布者确认
channel.confirm_delivery()

# 发布消息
if channel.basic_publish(exchange='test', routing_key='test', body='message'):
    print("消息发送成功")
else:
    print("消息发送失败")
```

#### 5.2.2 消费者确认
```python
# 手动确认模式
def callback(ch, method, properties, body):
    try:
        # 业务处理
        print(f"处理消息: {body}")
        # 确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"处理失败: {e}")
        # 拒绝消息并重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

channel.basic_consume(queue='test_queue', on_message_callback=callback)
```

### 5.3 消息持久化

#### 5.3.1 交换机持久化
```python
channel.exchange_declare(
    exchange='persistent_exchange',
    exchange_type='direct',
    durable=True  # 交换机持久化
)
```

#### 5.3.2 队列持久化
```python
channel.queue_declare(
    queue='persistent_queue',
    durable=True  # 队列持久化
)
```

#### 5.3.3 消息持久化
```python
channel.basic_publish(
    exchange='persistent_exchange',
    routing_key='persistent_key',
    body='persistent message',
    properties=pika.BasicProperties(
        delivery_mode=2  # 消息持久化
    )
)
```

### 5.4 预取控制

```python
# 全局预取
channel.basic_qos(prefetch_count=10)

# 基于消费者的预取
channel.basic_consume(
    queue='high_priority_queue',
    on_message_callback=callback,
    arguments={'prefetch_count': 50}
)
```

**预取策略**:
- **prefetch_count=1**: 每次只获取一条消息，处理完成再获取下一条
- **prefetch_count=N**: 一次获取N条消息，提高吞吐量但可能影响公平性
- **prefetch_count=0**: 不限制预取数量（默认）

### 5.5 消费者公平调度

```python
# 设置预取数量确保公平调度
channel.basic_qos(prefetch_count=10)

def callback(ch, method, properties, body):
    # 处理消息
    process_message(body)
    
    # 模拟处理时间
    time.sleep(random.uniform(0.1, 2.0))
    
    # 确认消息
    ch.basic_ack(delivery_tag=method.delivery_tag)
```

**公平调度原则**:
- 确保处理快的消费者不会"饿死"处理慢的消费者
- 通过合理的预取数量控制
- 使用手动确认机制

---

## 6. 安装与配置

### 6.1 系统要求

#### 硬件要求
- **CPU**: 2核心以上推荐
- **内存**: 4GB以上推荐，生产环境建议8GB以上
- **磁盘**: SSD推荐，至少50GB可用空间
- **网络**: 千兆网络推荐

#### 软件要求
- **操作系统**: 
  - Linux: Ubuntu 18.04+, CentOS 7+, RHEL 7+
  - Windows: Windows Server 2016+
  - macOS: 10.14+
- **Erlang**: 21.3+ (RabbitMQ依赖)
- **Python**: 3.6+ (用于Python客户端开发)

### 6.2 在Ubuntu上安装

#### 6.2.1 安装Erlang
```bash
# 更新包列表
sudo apt-get update

# 安装Erlang
sudo apt-get install erlang-base erlang-dev erlang-crypto erlang-ssl \
    erlang-inets erlang-mnesia erlang-os-mon erlang-parsetools \
    erlang-public-key erlang-runtime-tools erlang-snmp erlang-syntax-tools \
    erlang-tftp erlang-tools erlang-xmerl

# 验证安装
erl -version
```

#### 6.2.2 添加RabbitMQ仓库
```bash
# 添加RabbitMQ官方APT仓库
curl -fsSL https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA | sudo gpg --dearmor | sudo tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null

# 添加Erlang Solutions仓库
curl -fsSL https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/gpg.9F4587F226208342.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg > /dev/null

# 添加RabbitMQ仓库
curl -fsSL https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/gpg.9F4587F226208342.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg > /dev/null

# 更新包列表
sudo apt-get update
```

#### 6.2.3 安装RabbitMQ
```bash
# 安装RabbitMQ Server
sudo apt-get install rabbitmq-server

# 启动服务
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# 检查状态
sudo systemctl status rabbitmq-server
```

### 6.3 在CentOS/RHEL上安装

#### 6.3.1 安装Erlang
```bash
# 安装EPEL仓库
sudo yum install epel-release

# 安装Erlang
sudo yum install erlang

# 验证安装
erl -version
```

#### 6.3.2 安装RabbitMQ
```bash
# 下载并安装RabbitMQ
wget https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.12.0/rabbitmq-server-3.12.0-1.el8.noarch.rpm

# 安装RabbitMQ
sudo rpm -ivh rabbitmq-server-3.12.0-1.el8.noarch.rpm

# 启动服务
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

### 6.4 使用Docker安装

#### 6.4.1 单节点安装
```bash
# 拉取镜像
docker pull rabbitmq:3.12-management

# 运行容器
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=admin123 \
  rabbitmq:3.12-management
```

#### 6.4.2 集群安装
```bash
# 创建网络
docker network create rabbitmq-cluster

# 创建数据卷
docker volume create rabbitmq-data

# 启动第一个节点
docker run -d \
  --name rabbitmq1 \
  --hostname rabbitmq1 \
  -p 5672:5672 \
  -p 15672:15672 \
  -v rabbitmq-data:/var/lib/rabbitmq \
  -e RABBITMQ_ERLANG_COOKIE=secret_cookie \
  rabbitmq:3.12-management

# 启动更多节点
for i in {2..3}; do
  docker run -d \
    --name rabbitmq$i \
    --hostname rabbitmq$i \
    -p 567${i}:5672 \
    -p 1567${i}:15672 \
    -v rabbitmq-data:/var/lib/rabbitmq \
    -e RABBITMQ_ERLANG_COOKIE=secret_cookie \
    rabbitmq:3.12-management
done
```

### 6.5 配置管理

#### 6.5.1 配置文件位置
```bash
# Ubuntu/Debian
/etc/rabbitmq/rabbitmq.conf
/etc/rabbitmq/advanced.config

# CentOS/RHEL
/etc/rabbitmq/rabbitmq.conf
/etc/rabbitmq/advanced.config

# Docker
/opt/rabbitmq/etc/rabbitmq/
```

#### 6.5.2 基本配置示例
```ini
# /etc/rabbitmq/rabbitmq.conf

# 监听端口
listeners.tcp.default = 5672
listeners.ssl.default = 5671

# 默认用户设置
default_user = admin
default_pass = admin123
default_permissions.configure = .*
default_permissions.read = .*
default_permissions.write = .*

# 内存限制
vm_memory_high_watermark = 0.6

# 磁盘空间限制
disk_free_limit = 2GB

# 集群配置
cluster_formation.peer_discovery_backend = classic_config
cluster_formation.classic_config.nodes.1 = rabbit@rabbitmq1
cluster_formation.classic_config.nodes.2 = rabbit@rabbitmq2

# 日志配置
log.file.level = info
log.console = true
log.console.level = info
```

#### 6.5.3 环境变量配置
```bash
# /etc/rabbitmq/rabbitmq-env.conf

# Erlang路径
ERLANG_PATH=/usr/lib/erlang/bin

# RabbitMQ安装路径
RABBITMQ_HOME=/usr/lib/rabbitmq

# 配置文件路径
CONFIG_FILE=/etc/rabbitmq/rabbitmq

# 环境变量
RABBITMQ_NODENAME=rabbit@localhost
RABBITMQ_NODE_PORT=5672
RABBITMQ_LOG_BASE=/var/log/rabbitmq

# 集群配置
RABBITMQ_SERVER_ERL_ARGS="+K true +A30 +P 131072"
```

### 6.6 用户管理

#### 6.6.1 添加用户
```bash
# 创建用户
rabbitmqctl add_user myuser mypassword

# 设置用户标签
rabbitmqctl set_user_tags myuser administrator

# 设置权限
rabbitmqctl set_permissions -p / myuser ".*" ".*" ".*"
```

#### 6.6.2 用户权限
- **配置权限（configure）**: 创建、删除、修改队列和交换机
- **写权限（write）**: 发布消息
- **读权限（read）**: 消费消息

#### 6.6.3 删除用户
```bash
# 删除用户
rabbitmqctl delete_user myuser

# 清除用户权限
rabbitmqctl clear_user_permissions myuser
```

---

## 7. 第一个应用示例

### 7.1 Python开发环境准备

#### 7.1.1 安装pika客户端
```bash
# 使用pip安装
pip install pika

# 或者使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install pika
```

#### 7.1.2 安装其他客户端库
```bash
# aio-pika (异步客户端)
pip install aio-pika

# Celery (分布式任务队列)
pip install celery

# PHP AMQP扩展
pecl install amqp

# Node.js AMQP库
npm install amqplib
```

### 7.2 简单Hello World示例

#### 7.2.1 生产者（Producer）
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单生产者示例 - Hello World
"""

import pika
import json

def main():
    # 连接参数
    connection_params = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=pika.PlainCredentials('guest', 'guest'),
        virtual_host='/'
    )
    
    try:
        # 建立连接
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        
        # 声明队列
        # durable=True 使队列持久化
        channel.queue_declare(queue='hello', durable=True)
        
        print(" [x] 发送消息到队列 'hello'")
        
        # 发送消息
        message = {
            'type': 'greeting',
            'content': 'Hello World!',
            'timestamp': '2024-01-01 12:00:00'
        }
        
        channel.basic_publish(
            exchange='',  # 默认交换机
            routing_key='hello',  # 队列名称
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 使消息持久化
                content_type='application/json',
                priority=1,
                message_id='msg_001',
                timestamp=1640995200
            )
        )
        
        print(f" [x] 消息已发送: {message}")
        
        # 关闭连接
        connection.close()
        
    except Exception as e:
        print(f"发送消息失败: {e}")

if __name__ == '__main__':
    main()
```

#### 7.2.2 消费者（Consumer）
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单消费者示例 - Hello World
"""

import pika
import json
import time

def callback(ch, method, properties, body):
    """消息处理回调函数"""
    try:
        # 解析消息
        message = json.loads(body)
        
        print(f" [x] 收到消息: {message}")
        print(f"     路由键: {method.routing_key}")
        print(f"     消息ID: {properties.message_id}")
        print(f"     时间戳: {properties.timestamp}")
        
        # 模拟消息处理时间
        print(" [.] 处理消息中...")
        time.sleep(1)
        
        # 手动确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(" [x] 消息处理完成，已确认")
        
    except Exception as e:
        print(f"处理消息失败: {e}")
        # 处理失败，消息重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    # 连接参数
    connection_params = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=pika.PlainCredentials('guest', 'guest'),
        virtual_host='/'
    )
    
    try:
        # 建立连接
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        
        # 声明队列
        channel.queue_declare(queue='hello', durable=True)
        
        # 设置预取数量，确保公平调度
        channel.basic_qos(prefetch_count=1)
        
        print(' [*] 等待消息。要退出请按 CTRL+C')
        
        # 开始消费消息
        # auto_ack=False 启用手动确认
        channel.basic_consume(
            queue='hello',
            on_message_callback=callback,
            auto_ack=False
        )
        
        # 开始消费
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print("\n [.] 消费者已停止")
        channel.stop_consuming()
        
    except Exception as e:
        print(f"消费消息失败: {e}")
        
    finally:
        try:
            connection.close()
        except:
            pass

if __name__ == '__main__':
    main()
```

### 7.3 工作队列示例

#### 7.3.1 任务生产者
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作队列生产者示例
"""

import pika
import sys
import time
import random

def send_task(task_message):
    """发送任务到队列"""
    connection_params = pika.ConnectionParameters('localhost')
    
    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        
        # 声明队列，durable=True 确保队列持久化
        channel.queue_declare(queue='task_queue', durable=True)
        
        print(f" [x] 发送任务: {task_message}")
        
        # 发布任务消息
        channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=task_message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # 使消息持久化
                priority=1
            )
        )
        
        connection.close()
        
    except Exception as e:
        print(f"发送任务失败: {e}")

def main():
    """主函数，发送多个任务"""
    tasks = [
        "任务1: 数据处理",
        "任务2: 图片处理",
        "任务3: 文件上传",
        "任务4: 邮件发送",
        "任务5: 数据库备份",
        "任务6: 日志分析",
        "任务7: 报告生成",
        "任务8: 监控检查"
    ]
    
    print("发送任务队列...")
    
    for i, task in enumerate(tasks, 1):
        # 添加任务编号
        numbered_task = f"{i}. {task}"
        send_task(numbered_task)
        
        # 添加随机延迟
        time.sleep(random.uniform(0.5, 2.0))

if __name__ == '__main__':
    main()
```

#### 7.3.2 任务消费者
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作队列消费者示例
"""

import pika
import time
import random

def process_task(ch, method, properties, body):
    """处理任务"""
    task_message = body.decode('utf-8')
    
    print(f" [x] 开始处理: {task_message}")
    
    # 模拟任务处理时间（根据任务复杂度）
    task_duration = random.uniform(1, 5)
    print(f" [.] 预计处理时间: {task_duration:.1f}秒")
    
    time.sleep(task_duration)
    
    print(f" [x] 任务完成: {task_message}")
    
    # 确认消息处理完成
    ch.basic_ack(delivery_tag=method.delivery_tag)

def worker():
    """工作进程"""
    connection_params = pika.ConnectionParameters('localhost')
    
    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        
        # 声明队列
        channel.queue_declare(queue='task_queue', durable=True)
        
        # 设置公平调度
        channel.basic_qos(prefetch_count=1)
        
        print(' [*] 工作进程启动，等待任务...')
        print('     按 Ctrl+C 退出')
        
        # 开始消费任务
        channel.basic_consume(
            queue='task_queue',
            on_message_callback=process_task,
            auto_ack=False
        )
        
        # 开始处理任务
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print("\n [.] 工作进程已停止")
        channel.stop_consuming()
        
    except Exception as e:
        print(f"工作进程错误: {e}")
        
    finally:
        try:
            connection.close()
        except:
            pass

if __name__ == '__main__':
    worker()
```

### 7.4 发布/订阅模式示例

#### 7.4.1 发布者
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布/订阅模式发布者示例
"""

import pika
import json
import time

def publish_news(news_item):
    """发布新闻到广播交换机"""
    connection_params = pika.ConnectionParameters('localhost')
    
    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        
        # 声明广播交换机
        channel.exchange_declare(
            exchange='news_exchange',
            exchange_type='fanout'  # 广播交换机
        )
        
        print(f" [x] 发布新闻: {news_item['title']}")
        
        # 发布消息到交换机
        channel.basic_publish(
            exchange='news_exchange',
            routing_key='',  # 广播交换机忽略路由键
            body=json.dumps(news_item, ensure_ascii=False),
            properties=pika.BasicProperties(
                content_type='application/json',
                message_id=f"news_{int(time.time())}"
            )
        )
        
        connection.close()
        
    except Exception as e:
        print(f"发布新闻失败: {e}")

def main():
    """发布多条新闻"""
    news_items = [
        {
            "title": "技术突破：AI在医疗领域取得重大进展",
            "content": "最新的研究报告显示，人工智能在医疗诊断领域的准确率已达到95%",
            "category": "科技",
            "timestamp": "2024-01-01 10:00:00"
        },
        {
            "title": "市场分析：电动车行业持续高速增长",
            "content": "2024年全球电动车销量预计将增长50%，达到1400万辆",
            "category": "商业",
            "timestamp": "2024-01-01 11:00:00"
        },
        {
            "title": "国际动态：多国签署气候合作协议",
            "content": "50个国家签署了新的气候合作协议，承诺2030年减排50%",
            "category": "国际",
            "timestamp": "2024-01-01 12:00:00"
        }
    ]
    
    print("开始发布新闻...")
    
    for news in news_items:
        publish_news(news)
        time.sleep(2)  # 间隔2秒发布一条新闻

if __name__ == '__main__':
    main()
```

#### 7.4.2 订阅者
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布/订阅模式订阅者示例
"""

import pika
import json

def news_subscriber(subscriber_name, news_queue_name):
    """新闻订阅者"""
    connection_params = pika.ConnectionParameters('localhost')
    
    def callback(ch, method, properties, body):
        """处理接收到的新闻"""
        try:
            news = json.loads(body.decode('utf-8'))
            
            print(f"\n📰 [{subscriber_name}] 收到新闻:")
            print(f"     标题: {news['title']}")
            print(f"     内容: {news['content']}")
            print(f"     分类: {news['category']}")
            print(f"     时间: {news['timestamp']}")
            print(f"     队列: {news_queue_name}")
            
            # 确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"[{subscriber_name}] 处理新闻失败: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        
        # 声明临时队列
        # exclusive=True 使队列为临时队列
        # auto_delete=True 在消费者断开连接后自动删除
        result = channel.queue_declare(
            queue=news_queue_name,
            exclusive=True,
            auto_delete=True
        )
        
        queue_name = result.method.queue
        
        # 绑定队列到广播交换机
        channel.queue_bind(
            exchange='news_exchange',
            queue=queue_name
        )
        
        print(f"[{subscriber_name}] 订阅成功，等待新闻...")
        print(f"     队列名称: {queue_name}")
        
        # 设置预取数量
        channel.basic_qos(prefetch_count=1)
        
        # 开始消费
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False
        )
        
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print(f"\n[{subscriber_name}] 订阅已停止")
        channel.stop_consuming()
        
    except Exception as e:
        print(f"[{subscriber_name}] 订阅错误: {e}")
        
    finally:
        try:
            connection.close()
        except:
            pass

def main():
    """启动多个订阅者"""
    subscribers = [
        ("订阅者A", "subscriber_a"),
        ("订阅者B", "subscriber_b"),
        ("订阅者C", "subscriber_c")
    ]
    
    # 创建订阅者线程
    import threading
    threads = []
    
    for name, queue in subscribers:
        thread = threading.Thread(
            target=news_subscriber,
            args=(name, queue)
        )
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    try:
        # 等待所有线程完成
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n所有订阅者已停止")

if __name__ == '__main__':
    main()
```

---

## 8. 工作模式详解

### 8.1 基本消息模式

#### 8.1.1 点对点模式（Point-to-Point）
```python
# 点对点模式 - 生产者
def send_point_to_point():
    channel.exchange_declare(exchange='direct_exchange', exchange_type='direct')
    
    # 发送消息到特定路由键
    channel.basic_publish(
        exchange='direct_exchange',
        routing_key='user.register',
        body='User registered message'
    )

# 点对点模式 - 消费者
def consume_point_to_point():
    # 绑定队列到交换机，使用特定路由键
    channel.queue_bind(queue='user_queue', exchange='direct_exchange', routing_key='user.register')
    
    def callback(ch, method, properties, body):
        print(f"处理用户消息: {body}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_consume(queue='user_queue', on_message_callback=callback)
```

#### 8.1.2 发布订阅模式（Publish-Subscribe）
```python
# 发布订阅模式 - 发布者
def publish_subscribe():
    channel.exchange_declare(exchange='fanout_exchange', exchange_type='fanout')
    
    # 广播消息到所有绑定队列
    channel.basic_publish(
        exchange='fanout_exchange',
        routing_key='',
        body='Broadcast message'
    )

# 发布订阅模式 - 订阅者
def subscribe_fanout():
    # 创建临时队列
    result = channel.queue_declare(exclusive=True, auto_delete=True)
    queue_name = result.method.queue
    
    # 绑定队列到广播交换机
    channel.queue_bind(exchange='fanout_exchange', queue=queue_name)
    
    def callback(ch, method, properties, body):
        print(f"收到广播: {body}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
```

#### 8.1.3 主题模式（Topic）
```python
# 主题模式 - 发布者
def publish_topic():
    channel.exchange_declare(exchange='topic_exchange', exchange_type='topic')
    
    # 发布不同主题的消息
    messages = [
        ('user.created', 'User created message'),
        ('user.updated', 'User updated message'),
        ('order.created', 'Order created message'),
        ('payment.processed', 'Payment processed message')
    ]
    
    for routing_key, message in messages:
        channel.basic_publish(
            exchange='topic_exchange',
            routing_key=routing_key,
            body=message
        )

# 主题模式 - 订阅者
def subscribe_topic(pattern):
    result = channel.queue_declare(exclusive=True, auto_delete=True)
    queue_name = result.method.queue
    
    # 绑定队列，pattern为路由键模式
    channel.queue_bind(
        exchange='topic_exchange', 
        queue=queue_name, 
        routing_key=pattern
    )
    
    def callback(ch, method, properties, body):
        print(f"模式 {pattern} 收到消息: {body}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

# 使用示例
# subscribe_topic('user.*')      # 接收所有用户相关消息
# subscribe_topic('*.created')   # 接收所有创建消息
# subscribe_topic('#')           # 接收所有消息
```

### 8.2 高级工作模式

#### 8.2.1 消息路由模式
```python
# 高级路由模式
def advanced_routing():
    # 声明主题交换机
    channel.exchange_declare(exchange='advanced_routing', exchange_type='topic')
    
    # 发送消息到不同的路由键
    messages = [
        ('critical.system.error', 'Critical error message'),
        ('warning.system.slow', 'System performance warning'),
        ('info.user.login', 'User login information'),
        ('debug.database.query', 'Database query debug')
    ]
    
    for routing_key, message in messages:
        channel.basic_publish(
            exchange='advanced_routing',
            routing_key=routing_key,
            body=message
        )

# 消费者绑定不同的路由模式
def bind_routing_patterns():
    patterns = {
        'critical_queue': 'critical.*',
        'system_queue': '*.system.*',
        'user_queue': 'info.user.*',
        'all_queue': '#'
    }
    
    for queue, pattern in patterns.items():
        result = channel.queue_declare(queue=queue, durable=True)
        
        channel.queue_bind(
            exchange='advanced_routing',
            queue=queue,
            routing_key=pattern
        )
```

#### 8.2.2 消息持久化模式
```python
# 消息持久化生产者
def persistent_producer():
    # 声明持久化交换机
    channel.exchange_declare(
        exchange='persistent_exchange',
        exchange_type='direct',
        durable=True  # 交换机持久化
    )
    
    # 声明持久化队列
    channel.queue_declare(
        queue='persistent_queue',
        durable=True  # 队列持久化
    )
    
    # 发布持久化消息
    for i in range(10):
        message = f"Persistent message {i}"
        channel.basic_publish(
            exchange='persistent_exchange',
            routing_key='persistent_key',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # 消息持久化
                content_type='text/plain',
                message_id=str(i),
                timestamp=int(time.time())
            )
        )
```

#### 8.2.3 消息优先级模式
```python
# 消息优先级生产者
def priority_producer():
    channel.queue_declare(
        queue='priority_queue',
        arguments={
            'x-max-priority': 5  # 设置最大优先级为5
        }
    )
    
    # 发送不同优先级的消息
    for i in range(10):
        priority = random.randint(1, 5)
        message = f"Message {i} with priority {priority}"
        
        channel.basic_publish(
            exchange='',
            routing_key='priority_queue',
            body=message,
            properties=pika.BasicProperties(
                priority=priority  # 设置消息优先级
            )
        )

# 优先级消费者
def priority_consumer():
    def callback(ch, method, properties, body):
        priority = properties.priority
        print(f"处理优先级为 {priority} 的消息: {body}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_consume(
        queue='priority_queue',
        on_message_callback=callback,
        auto_ack=False
    )
```

### 8.3 消息确认模式

#### 8.3.1 自动确认模式
```python
# 自动确认消费者
def auto_ack_consumer():
    def callback(ch, method, properties, body):
        print(f"自动确认处理消息: {body}")
        # 不需要手动确认，auto_ack=True 自动确认
    
    channel.basic_consume(
        queue='auto_ack_queue',
        on_message_callback=callback,
        auto_ack=True  # 启用自动确认
    )
```

#### 8.3.2 手动确认模式
```python
# 手动确认消费者
def manual_ack_consumer():
    def callback(ch, method, properties, body):
        try:
            print(f"处理消息: {body}")
            
            # 业务处理逻辑
            process_message(body)
            
            # 手动确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("消息已确认")
            
        except Exception as e:
            print(f"处理失败: {e}")
            
            # 拒绝消息并重新入队
            ch.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=True  # 重新入队
            )
    
    channel.basic_consume(
        queue='manual_ack_queue',
        on_message_callback=callback,
        auto_ack=False  # 禁用自动确认
    )
```

#### 8.3.3 批量确认模式
```python
# 批量确认消费者
def batch_ack_consumer():
    message_count = 0
    
    def callback(ch, method, properties, body):
        nonlocal message_count
        message_count += 1
        
        print(f"处理消息 {message_count}: {body}")
        
        # 每处理10条消息确认一次
        if message_count % 10 == 0:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"批量确认了 {message_count} 条消息")
    
    channel.basic_consume(
        queue='batch_ack_queue',
        on_message_callback=callback,
        auto_ack=False
    )
```

### 8.4 消息预取模式

#### 8.4.1 公平预取
```python
# 公平预取消费者
def fair_consumer():
    # 设置预取数量，确保处理快的消费者不会被饿死
    channel.basic_qos(prefetch_count=1)
    
    def callback(ch, method, properties, body):
        print(f"处理消息: {body}")
        
        # 模拟处理时间
        processing_time = random.uniform(0.5, 3.0)
        time.sleep(processing_time)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_consume(queue='fair_queue', on_message_callback=callback)
```

#### 8.4.2 高吞吐量预取
```python
# 高吞吐量消费者
def high_throughput_consumer():
    # 设置较高的预取数量以提高吞吐量
    channel.basic_qos(prefetch_count=100)
    
    # 使用批量处理
    messages = []
    
    def callback(ch, method, properties, body):
        messages.append((method, properties, body))
        
        # 批量处理消息
        if len(messages) >= 10:
            process_batch(messages)
            
            # 批量确认
            for method, _, _ in messages:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
            messages.clear()
    
    channel.basic_consume(
        queue='throughput_queue',
        on_message_callback=callback,
        auto_ack=False
    )

def process_batch(messages):
    """批量处理消息"""
    print(f"批量处理 {len(messages)} 条消息")
    # 批量业务处理逻辑
    time.sleep(1)  # 模拟批处理时间
```

---

## 9. 管理界面使用

### 9.1 管理界面概述

RabbitMQ管理界面（RabbitMQ Management UI）提供基于Web的监控和管理功能，允许用户：

- 查看队列、交换机、绑定关系
- 监控消息速率、队列深度
- 管理用户和权限
- 查看连接和通道状态
- 监控集群状态（多节点）
- 导出/导入配置

### 9.2 启用管理界面

#### 9.2.1 通过插件启用
```bash
# 启用管理界面插件
rabbitmq-plugins enable rabbitmq_management

# 重启RabbitMQ服务
sudo systemctl restart rabbitmq-server

# 或者在Docker中
docker exec rabbitmq rabbitmq-plugins enable rabbitmq_management
```

#### 9.2.2 访问管理界面
- **URL**: http://localhost:15672
- **默认用户**: guest / guest
- **注意**: guest用户只能从本地主机访问

### 9.3 管理界面功能详解

#### 9.3.1 总览页面（Overview）
```python
# 查看集群概览信息
def get_overview():
    # 通过管理API获取概览信息
    import requests
    
    url = "http://localhost:15672/api/overview"
    auth = ('admin', 'admin123')
    
    response = requests.get(url, auth=auth)
    
    if response.status_code == 200:
        overview = response.json()
        
        # 集群信息
        cluster_name = overview['cluster_name']
        print(f"集群名称: {cluster_name}")
        
        # 消息统计
        message_stats = overview['message_stats']
        print(f"消息总数: {message_stats.get('message_count', 0)}")
        print(f"消息速率: {message_stats.get('rate', 0)} msg/s")
        
        # 队列统计
        queue_totals = overview['queue_totals']
        print(f"队列总数: {len(overview['queues'])}")
        print(f"队列消息总数: {queue_totals.get('messages', 0)}")
        
        # 监听端口
        listeners = overview['listeners']
        for listener in listeners:
            print(f"监听: {listener['protocol']} {listener['ip_address']}:{listener['port']}")
```

#### 9.3.2 队列管理（Queues）
```python
# 通过管理API管理队列
def manage_queues():
    import requests
    
    auth = ('admin', 'admin123')
    base_url = "http://localhost:15672/api"
    
    # 获取所有队列
    response = requests.get(f"{base_url}/queues", auth=auth)
    queues = response.json()
    
    for queue in queues:
        print(f"队列: {queue['name']}")
        print(f"  消息数量: {queue.get('messages', 0)}")
        print(f"  状态: {queue['state']}")
        print(f"  持久化: {queue['durable']}")
        print(f"  消息速率: {queue.get('message_stats', {}).get('publish_details', {}).get('rate', 0)} msg/s")
    
    # 创建队列
    queue_config = {
        "vhost": "/",
        "durable": True,
        "auto_delete": False,
        "arguments": {
            "x-max-priority": 5,
            "x-message-ttl": 3600000
        }
    }
    
    response = requests.put(
        f"{base_url}/queues/test_queue",
        json=queue_config,
        auth=auth,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        print("队列创建成功")
    
    # 删除队列
    response = requests.delete(
        f"{base_url}/queues/test_queue",
        auth=auth
    )
    
    if response.status_code == 204:
        print("队列删除成功")
```

#### 9.3.3 交换机管理（Exchanges）
```python
# 管理交换机
def manage_exchanges():
    import requests
    
    auth = ('admin', 'admin123')
    base_url = "http://localhost:15672/api"
    
    # 获取所有交换机
    response = requests.get(f"{base_url}/exchanges", auth=auth)
    exchanges = response.json()
    
    for exchange in exchanges:
        print(f"交换机: {exchange['name']}")
        print(f"  类型: {exchange['type']}")
        print(f"  持久化: {exchange['durable']}")
        print(f"  虚拟主机: {exchange['vhost']}")
    
    # 创建主题交换机
    exchange_config = {
        "vhost": "/",
        "type": "topic",
        "durable": True,
        "auto_delete": False,
        "internal": False,
        "arguments": {}
    }
    
    response = requests.put(
        f"{base_url}/exchanges/topic_exchange",
        json=exchange_config,
        auth=auth,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        print("主题交换机创建成功")
    
    # 创建绑定
    binding_config = {
        "routing_key": "user.*",
        "arguments": {}
    }
    
    response = requests.put(
        f"{base_url}/queues/test_queue/bindings/topic_exchange",
        json=binding_config,
        auth=auth,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        print("绑定创建成功")
```

#### 9.3.4 连接和通道管理（Connections & Channels）
```python
# 管理连接和通道
def manage_connections():
    import requests
    
    auth = ('admin', 'admin123')
    base_url = "http://localhost:15672/api"
    
    # 获取所有连接
    response = requests.get(f"{base_url}/connections", auth=auth)
    connections = response.json()
    
    for conn in connections:
        print(f"连接: {conn['name']}")
        print(f"  用户: {conn['user']}")
        print(f"  状态: {conn['state']}")
        print(f"  客户端: {conn['client_properties']['connection_name']}")
        print(f"  时长: {conn['connected_at']}")
        
        # 获取该连接的通道
        conn_name = conn['name'].replace('/', '%2f')
        channels_response = requests.get(
            f"{base_url}/connections/{conn_name}/channels",
            auth=auth
        )
        
        if channels_response.status_code == 200:
            channels = channels_response.json()
            print(f"  通道数: {len(channels)}")
            
            for channel in channels:
                print(f"    通道: {channel['name']}")
                print(f"      预取数: {channel['prefetch_count']}")
                print(f"      未确认消息: {channel['unacked_messages']}")
        
        print()
    
    # 关闭连接
    response = requests.delete(
        f"{base_url}/connections/{conn_name}",
        auth=auth
    )
    
    if response.status_code == 204:
        print("连接已关闭")
```

### 9.4 用户和权限管理

#### 9.4.1 用户管理
```python
# 管理用户
def manage_users():
    import requests
    
    auth = ('admin', 'admin123')
    base_url = "http://localhost:15672/api"
    
    # 获取所有用户
    response = requests.get(f"{base_url}/users", auth=auth)
    users = response.json()
    
    for user in users:
        print(f"用户: {user['name']}")
        print(f"  标签: {', '.join(user['tags'])}")
        print(f"  密码哈希: {user['password_hash']}")
    
    # 创建用户
    user_config = {
        "password": "user123",
        "tags": ["app"]
    }
    
    response = requests.put(
        f"{base_url}/users/app_user",
        json=user_config,
        auth=auth,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        print("用户创建成功")
    
    # 删除用户
    response = requests.delete(
        f"{base_url}/users/app_user",
        auth=auth
    )
    
    if response.status_code == 204:
        print("用户删除成功")
```

#### 9.4.2 权限管理
```python
# 管理权限
def manage_permissions():
    import requests
    
    auth = ('admin', 'admin123')
    base_url = "http://localhost:15672/api"
    
    # 获取用户权限
    response = requests.get(f"{base_url}/users/app_user/permissions", auth=auth)
    permissions = response.json()
    
    for perm in permissions:
        print(f"权限: {perm['vhost']}")
        print(f"  配置: {perm['configure']}")
        print(f"  写权限: {perm['write']}")
        print(f"  读权限: {perm['read']}")
    
    # 设置用户权限
    perm_config = {
        "configure": "^amq\\.default$",
        "read": "^test.*",
        "write": "^test.*"
    }
    
    response = requests.put(
        f"{base_url}/users/app_user/permissions",
        json=perm_config,
        auth=auth,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        print("权限设置成功")
    
    # 清除用户权限
    response = requests.delete(
        f"{base_url}/users/app_user/permissions",
        auth=auth
    )
    
    if response.status_code == 204:
        print("权限清除成功")
```

### 9.5 集群管理

#### 9.5.1 集群状态监控
```python
# 监控集群状态
def monitor_cluster():
    import requests
    
    auth = ('admin', 'admin123')
    base_url = "http://localhost:15672/api"
    
    # 获取集群节点信息
    response = requests.get(f"{base_url}/cluster-name", auth=auth)
    cluster_info = response.json()
    print(f"集群名称: {cluster_info['name']}")
    
    # 获取所有节点状态
    response = requests.get(f"{base_url}/nodes", auth=auth)
    nodes = response.json()
    
    for node in nodes:
        print(f"节点: {node['name']}")
        print(f"  类型: {node['type']}")
        print(f"  状态: {node['running']}")
        print(f"  内存使用: {node['mem_used']} / {node['mem_limit']}")
        print(f"  队列数量: {node['queues']}")
        print(f"  磁盘空间: {node['disk_free']}")
        print(f"  文件描述符: {node['fd_used']} / {node['fd_total']}")
        
        # 集群健康状态
        health_score = 0
        if node['running']:
            health_score += 50
        if node['mem_used'] < node['mem_limit'] * 0.9:
            health_score += 25
        if node['disk_free'] > 1024 * 1024 * 1024:  # 1GB
            health_score += 25
        
        print(f"  健康分数: {health_score}/100")
```

#### 9.5.2 集群管理操作
```python
# 集群管理操作
def cluster_operations():
    import requests
    
    auth = ('admin', 'admin123')
    base_url = "http://localhost:15672/api"
    
    # 强制重新均衡集群
    response = requests.post(
        f"{base_url}/cluster/rebalance",
        json={"cluster_nodes": ["rabbit@node1", "rabbit@node2"]},
        auth=auth,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print("集群重新均衡成功")
    
    # 停止节点
    response = requests.post(
        f"{base_url}/nodes/rabbit@node2/stop",
        json={"timeout": 10},
        auth=auth,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print("节点停止成功")
    
    # 重启节点
    response = requests.post(
        f"{base_url}/nodes/rabbit@node2/start",
        auth=auth
    )
    
    if response.status_code == 200:
        print("节点重启成功")
```

---

## 10. 常用命令与工具

### 10.1 RabbitMQ命令行工具

#### 10.1.1 rabbitmqctl命令
```bash
# 服务管理
sudo systemctl start rabbitmq-server    # 启动服务
sudo systemctl stop rabbitmq-server     # 停止服务
sudo systemctl restart rabbitmq-server  # 重启服务
sudo systemctl status rabbitmq-server   # 查看状态

# 用户管理
rabbitmqctl add_user username password      # 添加用户
rabbitmqctl delete_user username            # 删除用户
rabbitmqctl change_password username password  # 修改密码
rabbitmqctl list_users                      # 列出用户

# 权限管理
rabbitmqctl set_user_tags username administrator    # 设置用户标签
rabbitmqctl set_permissions username ".*" ".*" ".*" # 设置权限
rabbitmqctl list_user_permissions username          # 查看用户权限
rabbitmqctl clear_user_permissions username         # 清除权限

# 集群管理
rabbitmqctl join_cluster rabbit@node1         # 加入集群
rabbitmqctl cluster_status                    # 查看集群状态
rabbitmqctl forget_cluster_node rabbit@node2  # 忘记节点

# 插件管理
rabbitmqctl list_plugins                     # 列出插件
rabbitmqctl enable_plugin plugin_name        # 启用插件
rabbitmqctl disable_plugin plugin_name       # 禁用插件
rabbitmq-plugins enable plugin_name          # 启用插件（直接使用）

# 队列管理
rabbitmqctl list_queues                      # 列出队列
rabbitmqctl list_queues name messages durable  # 查看队列详细信息
rabbitmqctl purge_queue queue_name           # 清空队列

# 交换机管理
rabbitmqctl list_exchanges                   # 列出交换机
rabbitmqctl list_exchanges name type durable # 查看交换机详情

# 连接管理
rabbitmqctl list_connections                 # 列出连接
rabbitmqctl list_connections user state      # 查看连接用户和状态
rabbitmqctl close_connection connection_name reason  # 关闭连接
```

#### 10.1.2 rabbitmqadmin工具
```bash
# 安装 rabbitmqadmin
wget http://localhost:15672/cli/rabbitmqadmin
chmod +x rabbitmqadmin

# 队列操作
./rabbitmqadmin list queues
./rabbitmqadmin publish exchange=amq.direct routing_key=test payload="Hello World"
./rabbitmqadmin get queue=test requeue=false

# 交换机操作
./rabbitmqadmin list exchanges
./rabbitmqadmin declare exchange name=my_exchange type=topic durable=true

# 用户操作
./rabbitmqadmin list users
./rabbitmqadmin declare user name=test_user password=test_pass tags=app

# 权限操作
./rabbitmqadmin declare permission user=test_user vhost=/ \
    configure="^test.*" write="^test.*" read="^test.*"
```

### 10.2 Python管理工具

#### 10.2.1 队列监控工具
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ队列监控工具
"""

import pika
import json
import time
from datetime import datetime
from typing import Dict, List

class QueueMonitor:
    def __init__(self, connection_params):
        self.connection_params = connection_params
        self.connection = None
        self.channel = None
    
    def connect(self):
        """连接到RabbitMQ"""
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()
    
    def disconnect(self):
        """断开连接"""
        if self.connection:
            self.connection.close()
    
    def get_queue_info(self, queue_name: str) -> Dict:
        """获取队列信息"""
        try:
            method = self.channel.queue_declare(queue=queue_name, passive=True)
            queue_info = {
                'queue_name': queue_name,
                'message_count': method.method.message_count,
                'consumer_count': method.method.consumer_count,
                'timestamp': datetime.now().isoformat()
            }
            return queue_info
        except Exception as e:
            return {'queue_name': queue_name, 'error': str(e)}
    
    def list_all_queues(self) -> List[str]:
        """列出所有队列"""
        try:
            result = self.channel.queue_declare(queue='', passive=True)
            queue_names = []
            
            # 使用RabbitMQ管理API获取队列列表
            import requests
            
            auth = ('guest', 'guest')
            url = "http://localhost:15672/api/queues"
            
            response = requests.get(url, auth=auth)
            
            if response.status_code == 200:
                queues = response.json()
                queue_names = [q['name'] for q in queues if q['vhost'] == '/']
            
            return queue_names
        except Exception as e:
            print(f"获取队列列表失败: {e}")
            return []
    
    def monitor_queues(self, interval: int = 5):
        """持续监控队列"""
        print("开始监控队列...")
        print("按 Ctrl+C 停止监控\n")
        
        try:
            while True:
                queue_names = self.list_all_queues()
                
                print(f"\n=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
                
                for queue_name in queue_names:
                    queue_info = self.get_queue_info(queue_name)
                    if 'error' not in queue_info:
                        print(f"队列 {queue_name}:")
                        print(f"  消息数量: {queue_info['message_count']}")
                        print(f"  消费者数量: {queue_info['consumer_count']}")
                    else:
                        print(f"队列 {queue_name}: 获取信息失败")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n停止监控")
        except Exception as e:
            print(f"监控失败: {e}")

def main():
    """主函数"""
    connection_params = pika.ConnectionParameters('localhost')
    
    monitor = QueueMonitor(connection_params)
    
    try:
        monitor.connect()
        monitor.monitor_queues(interval=10)
    finally:
        monitor.disconnect()

if __name__ == '__main__':
    main()
```

#### 10.2.2 性能测试工具
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ性能测试工具
"""

import pika
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

class PerformanceTester:
    def __init__(self, connection_params):
        self.connection_params = connection_params
        self.connection = None
        self.channel = None
        
        # 性能统计
        self.stats = {
            'sent_count': 0,
            'received_count': 0,
            'start_time': None,
            'end_time': None,
            'send_errors': 0,
            'receive_errors': 0
        }
        self.lock = threading.Lock()
    
    def connect(self):
        """建立连接"""
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()
        
        # 声明测试队列
        self.channel.queue_declare(queue='performance_test', durable=True)
    
    def disconnect(self):
        """断开连接"""
        if self.connection:
            self.connection.close()
    
    def send_messages(self, count: int, message_size: int = 100, 
                     rate_limit: int = 0):
        """发送消息测试"""
        print(f"开始发送 {count} 条消息，每条大小 {message_size} 字节")
        
        # 生成测试消息
        message_body = "x" * message_size
        message = {
            'content': message_body,
            'timestamp': time.time(),
            'index': 0
        }
        
        send_interval = 0
        if rate_limit > 0:
            send_interval = 1.0 / rate_limit
        
        start_time = time.time()
        
        for i in range(count):
            message['index'] = i
            
            try:
                self.channel.basic_publish(
                    exchange='',
                    routing_key='performance_test',
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2  # 持久化
                    )
                )
                
                with self.lock:
                    self.stats['sent_count'] += 1
                
                if rate_limit > 0:
                    time.sleep(send_interval)
                
            except Exception as e:
                with self.lock:
                    self.stats['send_errors'] += 1
                print(f"发送消息失败: {e}")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"发送完成，耗时 {elapsed_time:.2f} 秒")
        print(f"发送速率: {count/elapsed_time:.2f} 消息/秒")
    
    def receive_messages(self, count: int, auto_ack: bool = False):
        """接收消息测试"""
        print(f"开始接收 {count} 条消息")
        
        received_count = 0
        start_time = time.time()
        
        def message_handler(ch, method, properties, body):
            nonlocal received_count
            
            try:
                message = json.loads(body.decode())
                received_count += 1
                
                with self.lock:
                    self.stats['received_count'] += 1
                
                if received_count >= count:
                    ch.stop_consuming()
                
                if not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                with self.lock:
                    self.stats['receive_errors'] += 1
                print(f"接收消息失败: {e}")
        
        try:
            self.channel.basic_consume(
                queue='performance_test',
                on_message_callback=message_handler,
                auto_ack=auto_ack
            )
            
            self.channel.start_consuming()
            
        except Exception as e:
            print(f"消费消息失败: {e}")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"接收完成，耗时 {elapsed_time:.2f} 秒")
        print(f"接收速率: {received_count/elapsed_time:.2f} 消息/秒")
    
    def run_throughput_test(self, message_count: int = 10000, 
                          message_size: int = 100):
        """运行吞吐量测试"""
        print("开始吞吐量测试...")
        print(f"参数: {message_count} 条消息，每条 {message_size} 字节")
        
        # 重置统计
        with self.lock:
            self.stats = {
                'sent_count': 0,
                'received_count': 0,
                'start_time': time.time(),
                'send_errors': 0,
                'receive_errors': 0
            }
        
        # 并发测试
        with ThreadPoolExecutor(max_workers=2) as executor:
            # 启动发送线程
            sender = executor.submit(self.send_messages, message_count, message_size)
            
            # 启动接收线程
            receiver = executor.submit(self.receive_messages, message_count)
            
            # 等待完成
            sender.result()
            receiver.result()
        
        # 统计结果
        with self.lock:
            self.stats['end_time'] = time.time()
            total_time = self.stats['end_time'] - self.stats['start_time']
            
            print(f"\n=== 测试结果 ===")
            print(f"发送消息数: {self.stats['sent_count']}")
            print(f"接收消息数: {self.stats['received_count']}")
            print(f"发送错误数: {self.stats['send_errors']}")
            print(f"接收错误数: {self.stats['receive_errors']}")
            print(f"总耗时: {total_time:.2f} 秒")
            print(f"平均发送速率: {self.stats['sent_count']/total_time:.2f} 消息/秒")
            print(f"平均接收速率: {self.stats['received_count']/total_time:.2f} 消息/秒")

def main():
    """主函数"""
    connection_params = pika.ConnectionParameters(
        'localhost',
        credentials=pika.PlainCredentials('guest', 'guest')
    )
    
    tester = PerformanceTester(connection_params)
    
    try:
        tester.connect()
        tester.run_throughput_test(message_count=5000, message_size=1024)
    finally:
        tester.disconnect()

if __name__ == '__main__':
    main()
```

#### 10.2.3 配置管理工具
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RabbitMQ配置管理工具