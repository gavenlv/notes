# 第4章：Thanos核心组件详解

## 4.1 Query组件：查询路由和聚合

### 4.1.1 Query组件架构

Query组件是Thanos系统的查询入口，负责：

1. **查询路由**：将查询请求路由到正确的数据源
2. **结果聚合**：合并多个数据源的查询结果
3. **去重处理**：基于副本标签去除重复数据
4. **查询优化**：智能优化查询性能和资源使用

### 4.1.2 核心功能详解

**查询路由机制**：
```
用户查询请求 → Query组件 → 路由决策 → 并行查询 → 结果合并 → 返回用户
                              │
                              ├── Sidecar（实时数据）
                              ├── Store（历史数据）
                              └── Ruler（告警数据）
```

**去重算法**：
- 基于`replica`标签识别相同数据的多个副本
- 使用时间戳和指标值进行智能去重
- 支持自定义去重策略

### 4.1.3 高级配置示例

```yaml
# query-advanced.yaml
query:
  # 查询配置
  timeout: 5m
  max_concurrent: 50
  default_evaluation_interval: 1m
  
  # 自动降采样
  auto_downsampling: true
  
  # 部分响应（提高可用性）
  partial_response: true
  
  # 查询重写规则
  query_replica_label: "replica"
  
  # 存储节点发现
  store:
    - dnssrv+_grpc._tcp.thanos-sidecar.monitoring.svc.cluster.local
    - dnssrv+_grpc._tcp.thanos-store.monitoring.svc.cluster.local
    
  # 缓存配置
  query_range_response_cache:
    max_size: "2GB"
    validity: 1h

# Web配置
web:
  # 外部访问地址（用于生成链接）
  external_prefix: "https://thanos.example.com"
  
  # CORS配置
  cors_origin: ".*"
  
  # 前缀路径（反向代理场景）
  prefix_header: "X-Forwarded-Prefix"

# 日志配置
log:
  level: info
  format: json
  
# 指标配置
metrics:
  # 指标路径
  path: "/metrics"
  
  # 指标标签
  labels:
    component: "query"
    environment: "production"
```

## 4.2 Store组件：历史数据查询

### 4.2.1 Store组件架构

Store组件负责从对象存储查询历史数据：

1. **索引管理**：维护对象存储中数据块的索引
2. **查询执行**：执行针对历史数据的查询请求
3. **缓存优化**：使用本地缓存提高查询性能
4. **数据过滤**：基于时间范围和标签过滤数据

### 4.2.2 数据查询流程

```
查询请求 → Store组件 → 索引查找 → 数据块加载 → 查询执行 → 结果返回
              │
              ├── 本地缓存（热数据）
              └── 对象存储（冷数据）
```

### 4.2.3 性能优化配置

```yaml
# store-optimized.yaml
store:
  # 对象存储配置
  objstore:
    type: S3
    config:
      bucket: "thanos-data"
      endpoint: "s3.amazonaws.com"
      access_key: "${AWS_ACCESS_KEY}"
      secret_key: "${AWS_SECRET_KEY}"
      
  # 索引缓存配置
  index_cache:
    type: IN-MEMORY
    config:
      max_size: "1GB"
      validity: 24h
      
  # 块缓存配置
  chunk_cache:
    type: IN-MEMORY
    config:
      max_size: "2GB"
      validity: 6h
      
  # 查询配置
  query_timeout: 10m
  max_concurrent_selects: 20
  
  # 数据过滤
  min_time: "-2w"  # 最小查询时间
  max_time: "-1h"  # 最大查询时间（相对于当前时间）
  
  # 同步配置
  sync_block_duration: 3m
  blocking_timeout: 5m

# 监控配置
monitoring:
  # 健康检查间隔
  healthcheck_interval: 30s
  
  # 指标收集
  metrics:
    enabled: true
    path: "/metrics"
```

## 4.3 Compactor组件：数据压缩

### 4.3.1 压缩机制详解

Compactor组件负责数据压缩和优化：

1. **块文件压缩**：合并小文件为大文件
2. **数据去重**：去除重复的时间序列数据
3. **降采样处理**：生成低精度数据用于长期存储
4. **索引重建**：优化查询性能的索引结构

### 4.3.2 压缩策略

**压缩级别**：
- **Level 0**：原始数据块（2小时）
- **Level 1**：压缩为6小时块
- **Level 2**：压缩为24小时块
- **Level 3+**：进一步压缩为更长时间范围

**降采样策略**：
- **5m**：5分钟精度（保留30天）
- **1h**：1小时精度（保留1年）
- **1d**：1天精度（永久保留）

### 4.3.3 高级压缩配置

```yaml
# compactor-advanced.yaml
compactor:
  # 数据保留策略
  retention:
    # 原始数据保留
    raw: 30d
    
    # 5分钟精度数据保留
    5m: 180d
    
    # 1小时精度数据保留
    1h: 1y
    
    # 1天精度数据保留
    1d: 0d  # 永久保留
    
  # 压缩配置
  compaction:
    # 并发压缩数
    concurrency: 2
    
    # 压缩间隔
    interval: 2h
    
    # 块大小限制
    block_size_limit: 2GB
    
    # 压缩超时
    timeout: 24h
    
  # 降采样配置
  downsampling:
    # 启用降采样
    enabled: true
    
    # 降采样间隔
    resolution: 5m
    
    # 并发降采样数
    concurrency: 1
    
  # 对象存储配置
  objstore:
    type: S3
    config:
      bucket: "thanos-data"
      endpoint: "s3.amazonaws.com"
      
  # 临时工作目录
  data_dir: "/var/thanos/compactor"
  
  # 一致性检查
  consistency_delay: 30m
  
  # 等待块文件稳定
  wait_interval: 5m
```

## 4.4 Ruler组件：告警规则管理

### 4.4.1 Ruler组件架构

Ruler组件负责告警规则评估和管理：

1. **规则加载**：从对象存储或本地文件加载告警规则
2. **规则评估**：定期执行告警规则计算
3. **告警发送**：通过Alertmanager发送告警通知
4. **规则同步**：在多实例间同步规则状态

### 4.4.2 告警流程

```
规则文件 → Ruler组件 → 规则解析 → 定期评估 → 告警判断 → Alertmanager
              │
              ├── 对象存储（规则持久化）
              └── 本地缓存（规则缓存）
```

### 4.4.3 高可用配置

```yaml
# ruler-ha.yaml
ruler:
  # 规则存储配置
  rule:
    # 规则文件路径（对象存储）
    path: "/rules"
    
    # 规则同步间隔
    sync_interval: 1m
    
    # 规则评估间隔
    evaluation_interval: 30s
    
    # 告警历史保留
    alert_history_limit: 100
    
  # Alertmanager配置
  alertmanagers:
    - dnssrv+_http._tcp.alertmanager.monitoring.svc.cluster.local
    
  # 查询配置
  query:
    # Query组件地址
    endpoints:
      - dnssrv+_grpc._tcp.thanos-query.monitoring.svc.cluster.local
      
    # 查询超时
    timeout: 2m
    
    # 最大重试次数
    max_retries: 3
    
  # 高可用配置
  ha:
    # 集群模式
    cluster:
      # 集群地址
      peers: dnssrv+_grpc._tcp.thanos-ruler.monitoring.svc.cluster.local
      
      # 集群通信超时
      timeout: 10s
      
      # 选举间隔
      election_interval: 30s
      
  # 对象存储配置
  objstore:
    type: S3
    config:
      bucket: "thanos-rules"
      
  # 本地存储配置
  data_dir: "/var/thanos/ruler"
  
  # 日志配置
  log:
    level: info
    format: json
```

## 4.5 Receiver组件：数据接收

### 4.5.1 Receiver组件功能

Receiver组件提供远程写入接口：

1. **数据接收**：通过Remote Write API接收数据
2. **数据验证**：验证接收数据的完整性和格式
3. **数据转发**：将数据转发到对象存储
4. **多租户支持**：支持多租户数据隔离

### 4.5.2 接收流程

```
Remote Write → Receiver → 数据验证 → 临时存储 → 块生成 → 对象存储
                    │
                    ├── 多租户隔离
                    └── 数据压缩
```

### 4.5.3 多租户配置

```yaml
# receiver-multi-tenant.yaml
receiver:
  # HTTP配置
  http:
    address: "0.0.0.0"
    port: 19291
    
    # 多租户头部
    tenant_header: "THANOS-TENANT"
    tenant_certificate_field: "tenant_id"
    
  # gRPC配置
  grpc:
    address: "0.0.0.0"
    port: 19292
    
  # 远程写入配置
  remote_write:
    # 接收缓冲区大小
    buffer_size: 256MB
    
    # 最大并发写入
    max_concurrent: 10
    
    # 重试配置
    retry_on_failure:
      max_retries: 3
      backoff: 1s
      
  # 租户配置
  tenants:
    # 默认租户配置
    default:
      # 存储配额
      storage_quota: 100GB
      
      # 保留策略
      retention: 30d
      
    # 自定义租户配置
    tenant-a:
      storage_quota: 1TB
      retention: 90d
      
    tenant-b:
      storage_quota: 500GB
      retention: 60d
      
  # 对象存储配置
  objstore:
    type: S3
    config:
      bucket: "thanos-receive"
      
  # 本地存储配置
  data_dir: "/var/thanos/receive"
  
  # TSDB配置
  tsdb:
    # 块持续时间
    block_duration: 2h
    
    # 保留时间
    retention: 2h
    
    # WAL配置
    wal_compression: true
    
    # 采样配置
    stripe_size: 16384
```

## 4.6 组件间通信机制

### 4.6.1 gRPC通信协议

Thanos组件间使用gRPC进行通信：

**通信模式**：
- **单向流**：Query → Store（数据查询）
- **双向流**：Query ↔ Sidecar（实时数据）
- **服务发现**：DNS-based服务发现

**协议定义**：
```protobuf
// Store API
service Store {
  // 系列信息查询
  rpc Series(SeriesRequest) returns (stream SeriesResponse);
  
  // 标签查询
  rpc LabelNames(LabelNamesRequest) returns (LabelNamesResponse);
  
  // 标签值查询
  rpc LabelValues(LabelValuesRequest) returns (LabelValuesResponse);
}

// Query API
service Query {
  // 即时查询
  rpc Query(QueryRequest) returns (QueryResponse);
  
  // 范围查询
  rpc QueryRange(QueryRangeRequest) returns (QueryRangeResponse);
}
```

### 4.6.2 服务发现机制

**静态配置**：
```yaml
store:
  - 10.0.1.10:19090
  - 10.0.1.11:19090
```

**DNS服务发现**：
```yaml
store:
  - dnssrv+_grpc._tcp.thanos-store.monitoring.svc.cluster.local
```

**文件服务发现**：
```yaml
store:
  - file:///etc/thanos/store-endpoints.json
```

## 4.7 组件监控和告警

### 4.7.1 关键监控指标

**Query组件指标**：
- `thanos_query_requests_total`：查询请求总数
- `thanos_query_request_duration_seconds`：查询延迟
- `thanos_query_store_nodes_healthy`：健康存储节点数

**Store组件指标**：
- `thanos_store_bucket_operations_total`：对象存储操作数
- `thanos_store_series_data_size_bytes`：系列数据大小
- `thanos_store_cached_series_hits_total`：缓存命中数

**Compactor指标**：
- `thanos_compactor_blocks_processed_total`：处理的块数
- `thanos_compactor_downsample_operations_total`：降采样操作数
- `thanos_compactor_garbage_collection_duration_seconds`：垃圾回收时间

### 4.7.2 告警规则示例

```yaml
groups:
- name: thanos-component-alerts
  rules:
  - alert: ThanosQueryHighLatency
    expr: histogram_quantile(0.99, thanos_query_request_duration_seconds_bucket) > 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Thanos Query组件高延迟"
      description: "Query组件P99延迟超过10秒"
      
  - alert: ThanosStoreUnhealthy
    expr: thanos_store_nodes_healthy < 2
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Thanos Store节点不健康"
      description: "健康Store节点数少于2个"
      
  - alert: ThanosCompactorStuck
    expr: changes(thanos_compactor_blocks_processed_total[1h]) == 0
    for: 1h
    labels:
      severity: warning
    annotations:
      summary: "Thanos Compactor卡住"
      description: "Compactor在过去1小时内没有处理任何块"
```

## 4.8 本章总结

本章详细介绍了Thanos的核心组件及其功能：

**核心组件要点**：
- **Query组件**：查询路由和聚合，支持全局查询视图
- **Store组件**：历史数据查询，优化对象存储访问
- **Compactor组件**：数据压缩和降采样，优化存储效率
- **Ruler组件**：告警规则管理，支持高可用评估
- **Receiver组件**：远程数据接收，支持多租户架构

**配置最佳实践**：
1. 根据数据量合理配置缓存大小
2. 设置适当的超时和重试参数
3. 启用部分响应提高系统可用性
4. 配置合理的压缩和降采样策略
5. 建立完善的监控和告警机制

**性能优化建议**：
- Query组件：增加并发数，启用查询缓存
- Store组件：优化索引缓存，使用SSD存储
- Compactor组件：合理设置压缩间隔和并发数
- Ruler组件：优化规则评估间隔和告警历史

在下一章中，我们将深入探讨Thanos的查询和存储功能，包括全局查询语法、多集群数据聚合和存储优化策略。