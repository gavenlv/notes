# 第5章：队列管理与负载均衡 - 代码示例

本目录包含第5章"队列管理与负载均衡"的完整代码示例，演示队列生命周期管理、负载均衡策略、性能监控和自动扩缩容等核心功能。

## 📁 文件说明

### 1. queue_management_demo.py
**队列生命周期管理演示**

核心功能：
- 队列创建和配置管理
- 队列生命周期演示（创建、运行、暂停、恢复、删除）
- 消息积压处理策略
- 死信队列配置
- 队列配额和限流
- 队列统计和监控
- 错误处理和恢复机制

演示场景：
- 基础队列操作
- 队列生命周期管理
- 高级队列配置

### 2. load_balancing_strategies.py
**负载均衡策略演示**

核心功能：
- **轮询分发(Round Robin)**：依次分配消息到消费者
- **公平分发(Fair Distribution)**：根据消费者处理能力分配
- **优先级队列(Priority Queue)**：高优先级消息优先处理
- **权重队列(Weighted Queue)**：不同队列配置不同权重
- 负载均衡效果分析
- 消费者性能统计
- 自动负载调整

演示场景：
- 轮询分发测试
- 公平分发测试
- 优先级队列测试
- 权重队列测试

### 3. monitoring_health_check.py
**性能监控与健康检查演示**

核心功能：
- **性能监控**：队列消息数、消费者数量、内存使用等
- **健康检查**：系统资源、RabbitMQ连接、队列状态
- **自动扩缩容**：根据负载情况自动调整消费者数量
- **告警系统**：性能阈值监控和告警通知
- **统计分析**：性能趋势分析和报告生成
- **实时监控**：定期收集和分析系统指标

演示场景：
- 实时性能监控
- 综合健康检查
- 自动扩缩容演示

## 🔧 环境要求

### 基础环境
- Python 3.7+
- pika >= 1.2.0
- psutil >= 5.8.0
- RabbitMQ 3.8+

### 安装依赖
```bash
pip install pika psutil
```

### 启动RabbitMQ
```bash
# 使用Docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# 或使用系统服务
sudo systemctl start rabbitmq-server
```

## 🚀 使用方法

### 1. 队列管理演示
```bash
python queue_management_demo.py
```

**主要演示内容：**
- 队列创建和基础配置
- 消息发送和接收
- 队列生命周期管理
- 死信队列配置
- 性能测试

**预期输出示例：**
```
🐰 RabbitMQ 队列管理演示
============================================================
✅ 成功连接到RabbitMQ
✅ 创建队列: demo_lifecycle_queue
🚀 队列生命周期演示开始
📤 发布测试消息到队列...
👥 启动消息消费者...
📊 队列状态监控...
✅ 队列管理演示完成
```

### 2. 负载均衡策略演示
```bash
python load_balancing_strategies.py
```

**主要演示内容：**
- 轮询分发策略效果
- 公平分发机制
- 优先级队列处理
- 权重队列配置
- 负载均衡效果分析

**预期输出示例：**
```
🔄 轮询分发测试
============================================================
✅ 轮询队列设置完成: test_round_robin
📤 发布测试消息...
👥 启动 3 个消费者...
⏳ 等待消息处理完成...
📊 Round Robin 测试结果
总体统计:
  期望消息数: 60
  处理消息数: 60
  成功率: 100.0%
⚖️  负载均衡效果:
  最大处理量: 20
  最小处理量: 20
  均衡比例: 100.00%
  ✅ 负载均衡效果良好
```

### 3. 监控与健康检查演示
```bash
python monitoring_health_check.py
```

**主要演示内容：**
- 实时性能监控
- 系统资源监控
- 健康状态检查
- 自动扩缩容
- 告警通知

**预期输出示例：**
```
📊 队列监控和健康检查演示
============================================================
✅ 创建队列: monitoring_high_load_queue
🔍 开始监控，持续时间: 60 秒
📡 开始生成流量到队列: monitoring_high_load_queue
🚨 队列 monitoring_high_load_queue 消息积压严重: 523
📈 monitoring_high_load_queue 性能报告:
   当前消息数: 567
   平均消息数: 445.2
   当前消费者: 1
✅ 整体健康状态: warning (分数: 72.5)
```

## 📊 性能调优参数

### 队列配置优化
```python
# 高吞吐量队列配置
queue_args = {
    'x-max-length': 10000,        # 最大队列长度
    'x-overflow': 'reject-publish',  # 溢出策略
    'x-message-ttl': 300000,      # 消息TTL(毫秒)
    'x-dead-letter-exchange': 'dlx_exchange',  # 死信交换机
    'x-dead-letter-routing-key': 'dlx_key'     # 死信路由键
}
```

### 消费者配置优化
```python
# 预取配置
channel.basic_qos(prefetch_count=10)  # 批处理模式
channel.basic_qos(prefetch_count=1)   # 公平分发模式

# 确认模式
channel.basic_consume(
    queue='queue_name',
    on_message_callback=callback,
    auto_ack=False  # 手动确认
)
```

### 负载均衡策略选择
```python
# 不同场景的策略选择
strategies = {
    'high_throughput': 'round_robin',     # 高吞吐量场景
    'fair_processing': 'fair_distribution', # 公平处理场景
    'priority_business': 'priority',      # 优先级业务场景
    'resource_optimization': 'weighted'   # 资源优化场景
}
```

## 📈 监控指标说明

### 队列监控指标
- **消息积压数**：队列中等待处理的消息数量
- **消费者数量**：当前活跃的消费者实例数
- **处理速率**：消息处理的平均速率
- **内存使用**：队列占用的系统内存

### 系统监控指标
- **CPU使用率**：系统CPU占用百分比
- **内存使用率**：系统内存占用百分比
- **磁盘使用率**：磁盘空间占用百分比
- **网络延迟**：网络通信延迟

### 健康检查指标
- **连接状态**：RabbitMQ连接是否正常
- **队列状态**：队列是否可正常访问
- **消费者状态**：消费者是否正常工作
- **系统资源**：系统资源是否充足

## 🔧 故障排查

### 常见问题及解决方案

#### 1. 连接失败
```python
# 检查RabbitMQ服务状态
systemctl status rabbitmq-server

# 检查端口是否开放
netstat -tlnp | grep 5672

# 验证认证信息
rabbitmqctl list_users
```

#### 2. 消息积压
```python
# 检查消费者数量
# 增加消费者实例
# 调整预取值
channel.basic_qos(prefetch_count=10)
```

#### 3. 内存使用过高
```python
# 监控队列长度
# 设置队列最大长度
# 配置消息TTL
# 启用队列镜像
```

#### 4. 消费者异常
```python
# 启用手动确认
# 处理异常和重试
# 配置死信队列
# 监控错误日志
```

### 调试技巧
1. **启用详细日志**：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **监控队列状态**：
```bash
# RabbitMQ管理界面
http://localhost:15672

# 命令行监控
rabbitmqctl list_queues
rabbitmqctl list_consumers
```

3. **性能分析**：
```python
# 使用性能监控器
monitor = PerformanceMonitor()
report = monitor.generate_performance_report('queue_name')
```

## 🎯 最佳实践

### 1. 队列设计原则
- **合理设置队列长度**：避免无限增长
- **配置TTL**：防止消息长时间堆积
- **使用死信队列**：处理失败和超时消息
- **镜像队列**：保证高可用性

### 2. 负载均衡优化
- **选择合适的策略**：根据业务特点选择负载均衡算法
- **控制预取值**：平衡处理效率和公平性
- **监控消费者性能**：及时调整资源配置
- **故障转移**：准备备用消费者

### 3. 监控和告警
- **实时监控**：持续监控系统指标
- **阈值告警**：设置合理的告警阈值
- **趋势分析**：分析性能变化趋势
- **自动扩缩容**：基于监控数据自动调整

### 4. 性能优化建议
- **批处理**：提高消息处理效率
- **连接池**：复用连接资源
- **异步处理**：避免阻塞操作
- **数据压缩**：减少网络传输

## 📚 扩展学习

### 相关文档
- [RabbitMQ官方文档](https://www.rabbitmq.com/documentation.html)
- [pika客户端文档](https://pika.readthedocs.io/)
- [队列管理最佳实践](https://www.rabbitmq.com/queues.html)

### 进阶主题
- **集群管理**：多节点集群部署和管理
- **镜像队列**：高可用队列配置
- **流控机制**：消息流量控制和限流
- **安全配置**：认证授权和安全策略

## 🤝 贡献指南

如果您发现代码问题或有改进建议，请：
1. 提交Issue描述问题
2. Fork项目并创建特性分支
3. 提交Pull Request贡献代码
4. 更新相关文档

## 📞 技术支持

如遇到技术问题，可以：
- 查看代码注释和文档
- 搜索相关技术文档
- 参考故障排查指南
- 提交GitHub Issue

---

**注意**：请确保在生产环境使用前充分测试，并根据实际业务场景调整配置参数。