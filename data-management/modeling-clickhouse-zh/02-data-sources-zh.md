# 2. 数据源接入策略

## 2.1 数据源类型概述

现代数据架构需要处理多种类型的数据源，每种数据源都有其特定的接入策略和扫描逻辑。

### 2.1.1 API数据源
- **特点**: 结构化数据，实时性高，接口标准化
- **常见场景**: 第三方服务集成、微服务架构
- **扫描逻辑**: 增量拉取、轮询机制、Webhook推送

### 2.1.2 消息队列数据源
- **特点**: 异步处理，高吞吐量，数据流式传输
- **常见场景**: 事件驱动架构、日志收集
- **扫描逻辑**: 消费者组、分区消费、消息回溯

### 2.1.3 直接连接数据源
- **特点**: 低延迟，数据一致性高，连接稳定
- **常见场景**: 数据库同步、文件系统集成
- **扫描逻辑**: CDC（变更数据捕获）、批量同步、实时同步

## 2.2 API数据源接入策略

### 2.2.1 接入模式

#### 轮询模式 (Polling)
```python
# 示例：基于时间戳的增量轮询
def poll_api_data(last_timestamp):
    params = {
        'since': last_timestamp,
        'limit': 1000
    }
    response = requests.get('https://api.example.com/data', params=params)
    return response.json()
```

#### Webhook模式
```python
# 示例：Webhook接收器
@app.route('/webhook/data', methods=['POST'])
def handle_webhook():
    data = request.json
    # 直接处理推送的数据
    process_realtime_data(data)
    return {'status': 'success'}
```

### 2.2.2 扫描逻辑设计

**ETL层处理**:
- 数据格式验证和标准化
- 基础数据清洗
- 增量数据识别
- API限流和重试机制

**ClickHouse层处理**:
- 避免在ClickHouse中进行API调用
- 专注于数据分析和查询优化

## 2.3 消息队列数据源接入策略

### 2.3.1 接入模式

#### Kafka消费者模式
```java
// 示例：Flink Kafka消费者
DataStream<String> stream = env
    .addSource(new FlinkKafkaConsumer<>("topic", 
        new SimpleStringSchema(), properties))
    .map(new DataTransformer())
    .keyBy(Data::getKey)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(new DataAggregator());
```

#### RabbitMQ工作队列模式
```python
# 示例：RabbitMQ消费者
def callback(ch, method, properties, body):
    data = json.loads(body)
    # 处理消息数据
    process_message_data(data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='data_queue', 
                     on_message_callback=callback)
```

### 2.3.2 扫描逻辑设计

**ETL层处理**:
- 消息反序列化和格式转换
- 数据去重和顺序保证
- 错误处理和重试机制
- 流量控制和背压处理

**ClickHouse层处理**:
- 批量数据插入优化
- 数据分区和索引设计
- 查询性能优化

## 2.4 直接连接数据源接入策略

### 2.4.1 接入模式

#### 数据库CDC模式
```sql
-- 示例：MySQL CDC配置
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    price DECIMAL(10,2)
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = 'localhost',
    'port' = '3306',
    'username' = 'flinkuser',
    'password' = 'flinkpw',
    'database-name' = 'inventory',
    'table-name' = 'products'
);
```

#### 文件系统监控模式
```python
# 示例：文件系统监控
class FileWatcher:
    def __init__(self, directory):
        self.directory = directory
        self.observer = Observer()
    
    def on_created(self, event):
        if event.is_directory:
            return
        # 处理新文件
        process_new_file(event.src_path)
```

### 2.4.2 扫描逻辑设计

**ETL层处理**:
- 数据抽取和增量识别
- 数据格式转换和清洗
- 连接管理和故障恢复
- 数据质量检查

**ClickHouse层处理**:
- 高效的数据加载策略
- 数据压缩和存储优化
- 查询执行计划优化

## 2.5 扫描逻辑划分最佳实践

### 2.5.1 实时性要求
- **高实时性**: 消息队列 + Flink流处理
- **准实时**: API + 定时任务
- **批处理**: 直接连接 + 批量ETL

### 2.5.2 数据量考虑
- **小数据量**: API直接接入
- **大数据量**: 消息队列分流
- **海量数据**: 分布式文件系统 + 批量处理

### 2.5.3 数据质量要求
- **高一致性**: 直接连接 + 事务处理
- **最终一致性**: 消息队列 + 重试机制
- **容错性**: 多副本 + 数据校验

## 2.6 总结

合理的数据源接入策略是构建高效数据架构的基础。根据数据源类型、实时性要求和数据量大小，选择适当的接入模式和扫描逻辑划分，可以显著提升整体系统的性能和可靠性。下一章将深入讨论ETL层的具体职责和扫描逻辑设计。