# 第3章：交换机类型深入研究 - 代码示例

## 📚 概述

本章代码示例深入展示了RabbitMQ中各种交换机类型的实际应用和高级特性，包括智能消息分类和动态路由机制。

## 📁 文件说明

### 1. exchange_patterns_demo.py
**主要功能：** 交换机模式完整演示
- **直连交换机演示**：系统日志按级别分发
- **主题交换机演示**：多级日志模式匹配
- **扇形交换机演示**：事件广播到所有订阅者
- **头交换机演示**：基于消息头属性的智能分发
- **复杂路由演示**：多级处理链和回调机制

**核心特性：**
- 🎯 交互式演示模式
- 📊 实时路由结果展示
- 🔧 环境自动清理
- 📈 详细的消息流分析

### 2. message_classification_demo.py
**主要功能：** 智能消息分类与路由
- **消息分类器**：基于规则的智能分类系统
- **动态路由**：实时路由决策生成
- **优先级处理**：多级优先级消息管理
- **统计监控**：实时分类统计和性能监控

**核心特性：**
- 🤖 规则引擎驱动分类
- 📋 自定义分类规则
- 📊 分类效果统计
- 🔄 路由历史追踪

## 🚀 使用方法

### 环境准备

```bash
# 确保RabbitMQ服务正在运行
# 进入chapter3目录
cd d:\\workspace\\superset-github\\notes\\data-analystics\\rabbitmq\\code\\chapter3

# 安装依赖（如果需要）
pip install pika uuid dataclasses
```

### 运行演示

#### 1. 交换机模式演示

```bash
# 交互式演示
python exchange_patterns_demo.py --interactive

# 完整演示（自动运行所有场景）
python exchange_patterns_demo.py --demo

# 指定RabbitMQ连接
python exchange_patterns_demo.py --host localhost --port 5672
```

**交互式演示操作：**
```
请选择演示场景:
1. 直连交换机 - 系统日志分发
2. 主题交换机 - 多级日志匹配
3. 扇形交换机 - 事件广播
4. 头交换机 - 属性匹配分发
5. 复杂路由 - 多级处理链
6. 运行所有演示
7. 退出
```

#### 2. 消息分类演示

```bash
# 交互式分类演示
python message_classification_demo.py --interactive

# 指定连接参数
python message_classification_demo.py --host 192.168.1.100 --port 5672
```

**分类演示操作：**
```
请选择操作:
1. 运行标准分类演示
2. 添加自定义分类规则
3. 查看分类统计
4. 手动分类消息
5. 清理环境
6. 退出
```

## 🔬 实验指南

### 实验1：交换机模式对比
1. 运行 `exchange_patterns_demo.py`
2. 分别选择每种交换机模式进行观察
3. 对比不同交换机的路由特点
4. 理解各种交换机的适用场景

### 实验2：消息分类测试
1. 运行 `message_classification_demo.py`
2. 观察标准分类过程
3. 添加自定义分类规则
4. 测试不同消息的分类效果
5. 分析分类统计结果

### 实验3：复杂路由模拟
1. 运行复杂路由演示
2. 观察多级处理链
3. 理解路由决策过程
4. 分析性能统计

### 实验4：自定义规则实验
1. 在分类演示中添加自定义规则
2. 测试不同正则表达式模式
3. 调整优先级和权重
4. 观察分类结果变化

## 📊 预期输出示例

### 交换机演示输出
```
🎬 直连交换机演示
==================================================
场景：系统日志按级别分发到不同队列

📤 发送 error 消息到 error_queue
   内容: 数据库连接失败
📤 发送 warning 消息到 warning_queue
   内容: 用户登录尝试异常频繁
📤 发送 info 消息到 info_queue
   内容: 支付处理成功

📥 模拟消费者消费
   队列 error_queue 收到相关消息
   队列 warning_queue 收到相关消息
   队列 info_queue 收到相关消息
   ✅ 所有消息已被处理
```

### 消息分类输出
```
🏗️ 设置消息分类环境
==================================================
✅ 分类环境设置完成
   创建了 7 个交换机
   创建了 16 个处理器队列

📊 开始处理 10 条消息

--- 消息 1/10 ---
📤 分类并路由消息:
   路由键: system.database.error
   分类: system
   目标交换机: system.processor
   预期队列: system_error
   优先级: 7
   处理时间: 0.003s

📈 分类统计:
   总处理消息数: 10
   平均处理时间: 0.002s
   激活规则数: 5/5

📊 分类分布:
   system: 3 (30.0%)
   business: 2 (20.0%)
   security: 2 (20.0%)
   audit: 1 (10.0%)
   analytics: 1 (10.0%)
   performance: 1 (10.0%)
```

## 🔧 故障排查

### 常见问题

1. **连接失败**
   ```bash
   # 检查RabbitMQ服务状态
   rabbitmqctl status
   
   # 检查防火墙设置
   netstat -an | grep 5672
   ```

2. **权限错误**
   ```bash
   # 检查用户权限
   rabbitmqctl list_users
   rabbitmqctl list_permissions
   ```

3. **交换机创建失败**
   - 确认交换机名称符合规范
   - 检查交换机类型是否正确
   - 验证durable参数设置

4. **消息无法路由**
   - 检查路由键格式
   - 确认绑定关系
   - 验证队列存在

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **查看队列状态**
   ```bash
   rabbitmqctl list_queues name messages durable
   ```

3. **监控交换机绑定**
   ```bash
   rabbitmqctl list_exchanges name type bindings
   ```

## 🎯 学习要点

### 交换机核心概念
- **直连交换机**：精确路由，单一路由键匹配
- **主题交换机**：模式匹配，支持通配符
- **扇形交换机**：广播分发，所有绑定队列
- **头交换机**：属性匹配，基于消息头

### 实际应用场景
- **日志系统**：不同级别的日志分发
- **事件驱动**：多订阅者事件通知
- **内容过滤**：基于属性的智能分发
- **复杂路由**：多级处理和决策链

### 性能优化
- 合理选择交换机类型
- 优化路由键设计
- 避免过度复杂的规则
- 监控路由性能

## 🔗 相关资源

- [RabbitMQ交换机文档](https://www.rabbitmq.com/tutorials/amqp-concepts.html)
- [消息路由详解](https://www.rabbitmq.com/routing.html)
- [RabbitMQ管理界面](http://localhost:15672)

## 📞 技术支持

如果在实验过程中遇到问题，请：
1. 检查RabbitMQ服务状态
2. 验证网络连接
3. 查看详细错误日志
4. 参考故障排查指南

---

**作者：** RabbitMQ学习教程  
**版本：** 1.0  
**更新时间：** 2025年11月