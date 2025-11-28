# 第2章：AMQP协议深入理解 - 代码示例

## 概述

本目录包含第2章"AMQP协议深入理解"的所有可运行代码示例，涵盖了AMQP协议的核心概念、交换机类型、消息流分析和可靠性测试。

## 文件说明

### 1. exchange_comparison.py
**功能**：对比四种交换机类型的路由效果
- **直连交换机 (Direct)**：基于精确匹配路由键
- **主题交换机 (Topic)**：基于模式匹配路由键
- **扇形交换机 (Fanout)**：广播到所有绑定队列
- **头交换机 (Headers)**：基于消息头属性匹配

**运行方式**：
```bash
python exchange_comparison.py --interactive  # 交互模式
python exchange_comparison.py --demo        # 自动演示模式
```

### 2. amqp_message_flow.py
**功能**：AMQP消息流分析和监控工具
- 监控AMQP连接状态
- 跟踪消息路由路径
- 分析消息性能指标
- 调试消息流问题
- 生成消息流报告

**运行方式**：
```bash
python amqp_message_flow.py --interactive  # 交互模式
python amqp_message_flow.py --demo        # 运行演示
```

### 3. reliability_test.py
**功能**：消息可靠性测试套件
- 测试消息确认机制（手动确认、自动确认）
- 测试消息持久化机制
- 测试事务处理
- 测试死信队列处理
- 测试消息过期处理
- 测试消息优先级

**运行方式**：
```bash
python reliability_test.py --interactive  # 交互模式
python reliability_test.py               # 运行所有测试
```

## 环境要求

### 依赖包
```bash
pip install pika
```

### RabbitMQ配置
确保RabbitMQ服务运行在：
- **主机**：localhost
- **端口**：5672 (AMQP), 15672 (管理界面)
- **用户**：guest/guest 或 admin/admin123

### Docker启动（推荐）
```bash
docker-compose up -d
```

## 使用说明

### 1. 快速开始
```bash
# 启动RabbitMQ
docker-compose up -d

# 运行所有示例
python exchange_comparison.py --demo
python amqp_message_flow.py --demo
python reliability_test.py
```

### 2. 交互式实验
```bash
# 交互式交换机对比
python exchange_comparison.py --interactive

# 交互式消息流分析
python amqp_message_flow.py --interactive

# 交互式可靠性测试
python reliability_test.py --interactive
```

### 3. 自定义参数
```bash
# 指定RabbitMQ连接参数
python exchange_comparison.py --host 192.168.1.100 --port 5672

# 指定分析时间窗口
python amqp_message_flow.py --demo --window 120
```

## 实验指南

### 实验1：交换机类型对比
1. 运行 `exchange_comparison.py --interactive`
2. 选择不同交换机类型进行测试
3. 观察消息路由结果
4. 理解各种交换机的适用场景

### 实验2：消息流分析
1. 运行 `amqp_message_flow.py --demo`
2. 观察消息流记录
3. 查看性能指标
4. 分析消息路由路径

### 实验3：消息可靠性
1. 运行 `reliability_test.py`
2. 测试各种可靠性机制
3. 观察测试结果
4. 理解最佳实践

## 学习目标

通过这些实验，你将学会：

1. **交换机类型掌握**
   - 理解四种交换机的不同特点
   - 掌握路由键的匹配规则
   - 学会选择合适的交换机类型

2. **消息流监控**
   - 使用RabbitMQ监控工具
   - 分析消息流向和性能
   - 诊断消息路由问题

3. **可靠性保障**
   - 掌握消息确认机制
   - 理解持久化的重要性
   - 学会处理异常情况

4. **最佳实践**
   - 设计健壮的消息系统
   - 优化性能和可靠性
   - 避免常见错误

## 故障排查

### 常见问题

1. **连接失败**
   ```bash
   # 检查RabbitMQ状态
   systemctl status rabbitmq-server
   
   # 检查端口是否开放
   netstat -an | grep 5672
   ```

2. **权限错误**
   ```bash
   # 检查用户权限
   rabbitmqctl list_users
   rabbitmqctl list_permissions
   ```

3. **资源不足**
   ```bash
   # 检查RabbitMQ资源使用
   rabbitmqctl status
   ```

### 调试模式
所有脚本都支持详细日志输出：
```bash
python exchange_comparison.py --demo --verbose
```

## 扩展学习

### 进阶实验
1. 消息流监控和报警
2. 高吞吐量测试
3. 集群环境验证
4. 故障恢复测试

### 性能优化
1. 批量消息处理
2. 连接池管理
3. 内存优化
4. 网络调优

## 相关资源

- [RabbitMQ官方文档](https://www.rabbitmq.com/documentation.html)
- [AMQP 0.9.1规范](https://www.rabbitmq.com/amqp-0-9-1-reference.html)
- [RabbitMQ管理界面](http://localhost:15672)

---

**提示**：这些实验需要在实际的RabbitMQ环境中运行，建议先启动RabbitMQ服务再开始实验。