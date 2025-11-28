# 第1章：RabbitMQ基础入门 - 代码示例说明

## 概述

本章的代码示例全面演示了RabbitMQ的核心概念和基础用法，通过实际代码帮助理解消息队列的工作原理。

## 📁 文件结构

```
chapter1/
├── basic_examples.py    # 基础示例代码集合
└── README.md           # 本文档
```

## 🚀 快速开始

### 环境准备

1. **安装RabbitMQ**
   ```bash
   # Windows (使用 Chocolatey)
   choco install rabbitmq
   
   # 或下载安装包
   # https://www.rabbitmq.com/download.html
   ```

2. **安装Python依赖**
   ```bash
   pip install pika requests
   ```

3. **启用管理界面**
   ```bash
   rabbitmq-plugins enable rabbitmq_management
   ```

4. **启动服务**
   ```bash
   rabbitmq-server
   ```

5. **访问管理界面**
   - 浏览器打开: http://localhost:15672
   - 默认用户: guest / guest

### 运行示例

```bash
cd d:\workspace\superset-github\notes\rabbitmq\code\chapter1
python basic_examples.py
```

## 📚 代码组件详解

### 1. RabbitMQConnector - 连接管理器

**功能**: 统一管理RabbitMQ连接，支持上下文管理器

**核心特性**:
- 自动连接建立和断开
- 连接参数配置
- 异常处理
- 连接池管理

**使用示例**:
```python
with RabbitMQConnector(host='localhost') as connector:
    channel = connector.channel
    # 执行RabbitMQ操作
```

### 2. BasicExamples - 基础示例

#### Hello World模式
- **生产者**: 发送简单问候消息
- **消费者**: 接收并处理消息
- **演示内容**: 
  - 基础连接建立
  - 队列声明
  - 消息发送/接收
  - 消息确认机制

**运行方式**:
```bash
# 终端1: 运行生产者
python basic_examples.py
# 选择 1 -> 1

# 终端2: 运行消费者
python basic_examples.py
# 选择 1 -> 2
```

### 3. WorkQueueExamples - 工作队列模式

#### 功能特点
- **任务分发**: 支持多个工作者公平竞争任务
- **消息持久化**: 任务消息持久化存储
- **消息确认**: 确保任务处理完成
- **预取控制**: 通过prefetch_count控制并发

#### 核心组件
- **task_producer**: 生成各种任务的工作者
- **task_worker**: 处理任务的工作者

**运行方式**:
```bash
# 终端1: 运行生产者
python basic_examples.py
# 选择 2 -> 1

# 终端2-3: 运行多个工作者
python basic_examples.py
# 选择 2 -> 3  # 启动多个工作者
```

### 4. PublishSubscribeExamples - 发布订阅模式

#### 交换机类型: Fanout
- **广播特性**: 所有订阅者都能收到消息
- **临时队列**: 订阅结束时自动删除
- **解耦合**: 发布者和订阅者互不依赖

#### 核心组件
- **news_publisher**: 新闻发布中心
- **news_subscriber**: 新闻订阅者

**运行方式**:
```bash
# 终端1: 运行发布者
python basic_examples.py
# 选择 3 -> 1

# 终端2-4: 运行多个订阅者
python basic_examples.py
# 选择 3 -> 2
```

### 5. TopicExchangeExamples - 主题交换机模式

#### 路由键模式
- **通配符**: `*` 匹配单个词，`#` 匹配零个或多个词
- **灵活订阅**: 支持复杂的消息过滤
- **分层结构**: 使用 `.` 分隔的层次化键

#### 核心组件
- **log_publisher**: 生成各种系统日志
- **log_subscriber**: 按模式订阅日志

**运行方式**:
```bash
# 终端1: 运行日志发布者
python basic_examples.py
# 选择 4 -> 1

# 终端2-5: 运行不同模式的订阅者
python basic_examples.py
# 选择 4 -> 2
```

### 6. demonstrate_monitoring - 监控功能

#### 监控内容
- **集群状态**: 集群名称、版本信息
- **消息统计**: 发布数量、确认数量
- **队列信息**: 队列数量、消息积压情况
- **连接状态**: 活跃连接数

#### 前提条件
- 启用RabbitMQ管理插件
- 配置管理员账户
- 确保API访问权限

## 🎯 学习目标

### 基础概念掌握
1. **连接管理**: 理解连接建立、断开和错误处理
2. **队列操作**: 队列声明、绑定、删除等操作
3. **消息传递**: 发送、接收、确认的完整流程
4. **交换机类型**: 直连、主题、广播交换机的作用

### 实践技能获得
1. **代码结构**: 学习如何组织RabbitMQ代码
2. **异常处理**: 掌握错误恢复和重试机制
3. **性能优化**: 理解预取数量和并发控制
4. **监控方法**: 学会使用管理API进行监控

### 最佳实践理解
1. **连接复用**: 使用连接池避免频繁创建连接
2. **消息持久化**: 确保消息不丢失
3. **消费者确认**: 保证消息处理完整性
4. **资源清理**: 及时释放队列和交换机

## 🔧 配置参数详解

### 连接参数
```python
connection_params = pika.ConnectionParameters(
    host='localhost',          # RabbitMQ服务器地址
    port=5672,                 # AMQP端口
    username='guest',          # 用户名
    password='guest',          # 密码
    virtual_host='/',          # 虚拟主机
    heartbeat=600,             # 心跳超时(秒)
    blocked_connection_timeout=300  # 阻塞连接超时
)
```

### 消息属性
```python
properties = pika.BasicProperties(
    delivery_mode=2,           # 1: 非持久, 2: 持久
    priority=5,               # 消息优先级(0-255)
    message_id='msg_123',     # 消息ID
    timestamp=int(time.time()), # 时间戳
    content_type='application/json'  # 内容类型
)
```

### QoS设置
```python
channel.basic_qos(
    prefetch_count=1,          # 预取消息数量
    all_channels=False         # 是否应用到所有通道
)
```

## 🛠️ 故障排查指南

### 常见问题

#### 1. 连接失败
```
❌ 连接失败: Connection refused
```
**解决方案**:
- 检查RabbitMQ服务是否启动
- 确认端口5672是否被占用
- 验证连接参数配置

#### 2. 队列不存在
```
❌ 处理消息失败: NOT_FOUND - no queue 'hello'
```
**解决方案**:
- 确认消费者先于生产者运行
- 检查队列名称拼写
- 验证虚拟主机配置

#### 3. 权限不足
```
❌ 操作失败: access_refused
```
**解决方案**:
- 确认用户名密码正确
- 检查虚拟主机权限
- 验证队列绑定权限

#### 4. 内存不足
```
❌ 消息发布失败: resource_error
```
**解决方案**:
- 增加RabbitMQ内存限制
- 清理队列中的消息
- 调整生产速率

### 调试技巧

#### 1. 启用详细日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. 使用管理界面
- 访问 http://localhost:15672
- 查看队列状态
- 监控连接数
- 检查消息积压

#### 3. 消息跟踪
```python
# 启用消息跟踪
channel.confirm_delivery()
```

## 📈 性能优化建议

### 1. 连接管理
- 使用连接池复用连接
- 设置合理的心跳间隔
- 实现连接重试机制

### 2. 消息处理
- 调整预取数量平衡性能
- 使用消息确认确保可靠性
- 合理设置消息超时时间

### 3. 资源清理
- 使用临时队列减少资源占用
- 及时删除不需要的交换机
- 监控队列内存使用

## 🔍 扩展学习

### 相关主题
- [第2章: 高级消息模式](./../chapter2/) - 学习复杂路由模式
- [第3章: 消息可靠性](./../chapter3/) - 深入消息确认机制
- [第4章: 集群与高可用](./../chapter4/) - 了解集群部署

### 官方资源
- [RabbitMQ官方文档](https://www.rabbitmq.com/documentation.html)
- [Pika客户端文档](https://pika.readthedocs.io/)
- [AMQP协议规范](https://www.amqp.org/)

### 社区资源
- [RabbitMQ GitHub](https://github.com/rabbitmq/rabbitmq-server)
- [RabbitMQ讨论组](https://groups.google.com/group/rabbitmq-discuss)

## 💡 实践建议

### 1. 从简单开始
- 先运行Hello World示例
- 理解基本的发送接收流程
- 观察管理界面中的队列变化

### 2. 逐步深入
- 尝试工作队列的多消费者模式
- 实验不同交换机类型的特性
- 测试消息持久化和确认机制

### 3. 实际应用
- 思考在工作项目中的应用场景
- 设计适合的消息模式
- 实现完整的错误处理机制

### 4. 持续优化
- 监控消息处理性能
- 优化代码结构
- 学习最佳实践

---

🎉 **恭喜完成第1章学习！** 现在你已经掌握了RabbitMQ的基础概念，接下来可以进入更高级的主题学习。