# 第3章：与Prometheus集成

## 3.1 Prometheus Sidecar模式配置

### 3.1.1 Sidecar模式工作原理

Sidecar模式是Thanos与Prometheus集成的核心方式，其工作原理如下：

```
┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │   Thanos        │
│                 │    │   Sidecar       │
│ • 数据采集       │    │ • 监控TSDB变化  │
│ • 本地存储       │◄───┤ • 上传数据块    │
│ • 规则评估       │    │ • 提供查询接口  │
└─────────────────┘    └─────────────────┘
        │                       │
        ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   本地TSDB       │    │   对象存储       │
│   (wal+块文件)   │    │   (S3/GCS等)    │
└─────────────────┘    └─────────────────┘
```

### 3.1.2 Sidecar配置详解

创建Sidecar配置文件 `sidecar-config.yaml`：

```yaml
# Sidecar基础配置
http:
  address: "0.0.0.0"
  port: 19191
  grace_period: 2m

grpc:
  address: "0.0.0.0"
  port: 19090
  grace_period: 2m

# Prometheus连接配置
prometheus:
  url: "http://localhost:9090"
  ready_timeout: 10m
  # TSDB路径（必须与Prometheus配置一致）
  tsdb_path: "/prometheus"

# 对象存储配置
objstore:
  type: S3
  config:
    bucket: "thanos"
    endpoint: "minio:9000"
    access_key: "thanos"
    secret_key: "thanos123"
    insecure: true
    signature_version2: false

# 数据上传配置
shipper:
  # 上传间隔
  upload_compacted: false
  # 忽略部分块文件（可选）
  ignore_ulid_thanos_meta: false

# 健康检查配置
healthcheck:
  # 健康检查间隔
  interval: 30s
  # 超时时间
  timeout: 10s

# 日志配置
log:
  level: info
  format: logfmt

# 指标收集配置
metrics:
  # 指标路径
  path: "/metrics"
```

### 3.1.3 Sidecar启动脚本

创建Sidecar启动脚本 `start-sidecar.sh`：

```bash
#!/bin/bash

# Sidecar启动脚本
set -e

echo "=== 启动Thanos Sidecar ==="

# 检查Prometheus是否就绪
echo "检查Prometheus服务..."
until curl -s http://localhost:9090/-/ready > /dev/null; do
    echo "等待Prometheus就绪..."
    sleep 5
done

# 检查TSDB路径
if [ ! -d "/prometheus" ]; then
    echo "错误: TSDB路径 /prometheus 不存在"
    exit 1
fi

# 启动Sidecar
echo "启动Thanos Sidecar..."
thanos sidecar \
    --http-address=0.0.0.0:19191 \
    --grpc-address=0.0.0.0:19090 \
    --prometheus.url=http://localhost:9090 \
    --tsdb.path=/prometheus \
    --objstore.config-file=/etc/thanos/minio-bucket.yaml \
    --log.level=info \
    --reloader.config-file=/etc/prometheus/prometheus.yml \
    --reloader.config-envsubst-file=/etc/prometheus/prometheus.yml \
    --reloader.rule-dir=/etc/prometheus/rules/ \
    --reloader.watch-interval=5s

echo "=== Sidecar启动完成 ==="
```

## 3.2 数据上传到对象存储

### 3.2.1 数据上传机制

Thanos Sidecar的数据上传机制包括：

1. **块文件监控**
   - 监控TSDB目录的块文件变化
   - 检测新生成的块文件
   - 验证块文件完整性

2. **上传流程**
   ```
   检测新块文件 → 验证完整性 → 生成元数据 → 上传到对象存储 → 更新索引
   ```

3. **重试机制**
   - 网络故障自动重试
   - 上传失败标记重试
   - 一致性检查确保数据完整

### 3.2.2 对象存储配置

**支持的对象存储类型**：
- AWS S3
- Google Cloud Storage
- Azure Blob Storage
- 阿里云OSS
- 腾讯云COS
- MinIO（兼容S3）

**通用配置模板**：

```yaml
# S3兼容存储配置
type: S3
config:
  bucket: "thanos-bucket"
  endpoint: "s3.amazonaws.com"
  region: "us-east-1"
  access_key: "YOUR_ACCESS_KEY"
  secret_key: "YOUR_SECRET_KEY"
  insecure: false
  signature_version2: false
  put_user_metadata: {}
  http_config:
    idle_conn_timeout: 90s
    response_header_timeout: 2m
    tls_config:
      insecure_skip_verify: false
  trace:
    enable: false
  part_size: 134217728
  sse_config:
    type: "SSE-S3"
    kms_key_id: ""
    kms_encryption_context: ""
    encryption_key: ""

# GCS配置
type: GCS
config:
  bucket: "thanos-bucket"
  service_account: "path/to/service-account.json"

# Azure配置
type: AZURE
config:
  storage_account: "thanosstorage"
  storage_account_key: "YOUR_KEY"
  container: "thanos-container"
  endpoint: "blob.core.windows.net"
  max_retries: 20
```

### 3.2.3 数据上传监控脚本

创建上传监控脚本 `monitor-upload.sh`：

```bash
#!/bin/bash

echo "=== 数据上传监控 ==="

# 检查Sidecar状态
echo "检查Sidecar服务状态..."
sidecar_status=$(curl -s http://localhost:19191/-/healthy)
if [ "$sidecar_status" = "Healthy" ]; then
    echo "✓ Sidecar健康状态: $sidecar_status"
else
    echo "✗ Sidecar异常: $sidecar_status"
fi

# 检查上传指标
echo "检查数据上传指标..."
upload_metrics=$(curl -s http://localhost:19191/metrics | grep -E "thanos_shipper_")

# 解析关键指标
blocks_uploaded=$(echo "$upload_metrics" | grep "thanos_shipper_uploads_total" | awk '{print $2}')
blocks_failed=$(echo "$upload_metrics" | grep "thanos_shipper_upload_failures_total" | awk '{print $2}')
last_upload=$(echo "$upload_metrics" | grep "thanos_shipper_last_upload_timestamp" | awk '{print $2}')

if [ -n "$blocks_uploaded" ]; then
    echo "✓ 已上传块文件数量: $blocks_uploaded"
else
    echo "⚠ 无法获取上传数量"
fi

if [ -n "$blocks_failed" ] && [ "$blocks_failed" -gt "0" ]; then
    echo "⚠ 上传失败数量: $blocks_failed"
else
    echo "✓ 上传失败数量: ${blocks_failed:-0}"
fi

if [ -n "$last_upload" ] && [ "$last_upload" -gt "0" ]; then
    last_upload_time=$(date -d @$last_upload)
    echo "✓ 最后上传时间: $last_upload_time"
else
    echo "⚠ 无法获取最后上传时间"
fi

# 检查对象存储中的块文件
echo "检查对象存储中的块文件..."
if command -v aws &> /dev/null; then
    # AWS S3检查
    bucket_files=$(aws s3 ls s3://thanos-bucket/ --recursive | grep ".json\|.tsdb" | wc -l)
    echo "对象存储中文件数量: $bucket_files"
elif docker ps | grep -q minio; then
    # MinIO检查
    bucket_files=$(docker exec thanos-minio mc ls local/thanos/ --recursive | grep -E "chunks|index|meta" | wc -l)
    echo "MinIO中文件数量: $bucket_files"
else
    echo "⚠ 无法检查对象存储"
fi

echo "=== 监控完成 ==="
```

## 3.3 查询路由配置

### 3.3.1 Query组件配置

Query组件是Thanos的查询入口，负责路由查询到正确的数据源：

**基础配置** `query-config.yaml`：

```yaml
# Query基础配置
http:
  address: "0.0.0.0"
  port: 19192
  grace_period: 2m

grpc:
  address: "0.0.0.0"
  port: 19091
  grace_period: 2m

# 存储节点配置
store:
  # Sidecar节点（实时数据）
  - 10.0.1.10:19090
  - 10.0.1.11:19090
  # Store节点（历史数据）
  - 10.0.2.10:19091
  - 10.0.2.11:19091

# 查询配置
query:
  # 副本标签（用于去重）
  replica_label: "replica"
  # 查询超时
  timeout: 2m
  # 最大并发查询
  max_concurrent: 20
  # 默认查询时间范围
  default_evaluation_interval: 1m

# 自动发现配置（可选）
dns_sd_configs:
  - names:
      - "thanos-sidecar."
    type: "A"
    port: 19090

# Web配置
web:
  # 外部访问地址
  external_prefix: ""
  # 前缀路径
  prefix_header: ""
  # CORS配置
  cors_origin: ".*"

# 日志配置
log:
  level: info
  format: logfmt
```

### 3.3.2 查询路由策略

Thanos Query支持多种查询路由策略：

1. **时间范围路由**
   - 实时数据：查询Sidecar
   - 历史数据：查询Store

2. **负载均衡路由**
   - 轮询多个相同数据源
   - 基于响应时间智能路由

3. **故障转移路由**
   - 自动检测故障节点
   - 故障时路由到健康节点

### 3.3.3 查询验证脚本

创建查询验证脚本 `verify-query.sh`：

```bash
#!/bin/bash

echo "=== 查询功能验证 ==="

# 基础查询测试
queries=(
    "up"
    "rate(prometheus_tsdb_head_samples_appended_total[5m])"
    "sum by (job) (up)"
    "prometheus_build_info"
)

for query in "${queries[@]}"; do
    echo -n "测试查询: $query..."
    response=$(curl -s "http://localhost:19192/api/v1/query?query=${query}")
    
    if echo "$response" | grep -q '"status":"success"'; then
        result_count=$(echo "$response" | jq '.data.result | length')
        echo "✓ 成功 (结果数: $result_count)"
    else
        echo "✗ 失败"
        echo "响应: $response"
    fi
done

# 范围查询测试
echo -n "测试范围查询..."
range_response=$(curl -s "http://localhost:19192/api/v1/query_range?query=up&start=$(date -d '1 hour ago' +%s)&end=$(date +%s)&step=15")

if echo "$range_response" | grep -q '"status":"success"'; then
    echo "✓ 范围查询成功"
else
    echo "✗ 范围查询失败"
fi

# 元数据查询测试
echo -n "测试元数据查询..."
metadata_response=$(curl -s "http://localhost:19192/api/v1/label/__name__/values")

if echo "$metadata_response" | grep -q '"status":"success"'; then
    label_count=$(echo "$metadata_response" | jq '.data | length')
    echo "✓ 元数据查询成功 (标签数: $label_count)"
else
    echo "✗ 元数据查询失败"
fi

# 存储节点状态检查
echo -n "检查存储节点状态..."
stores_response=$(curl -s "http://localhost:19192/api/v1/stores")

if echo "$stores_response" | grep -q '"status":"success"'; then
    store_count=$(echo "$stores_response" | jq '.data | length')
    echo "✓ 存储节点正常 (节点数: $store_count)"
else
    echo "✗ 存储节点检查失败"
fi

echo "=== 查询验证完成 ==="
```

## 3.4 数据一致性验证

### 3.4.1 一致性检查机制

Thanos提供多种数据一致性检查机制：

1. **块文件完整性检查**
   - 校验和验证
   - 索引一致性检查
   - 元数据完整性验证

2. **数据同步状态检查**
   - 上传进度监控
   - 延迟检测
   - 数据丢失检测

### 3.4.2 一致性验证脚本

创建一致性验证脚本 `verify-consistency.sh`：

```bash
#!/bin/bash

echo "=== 数据一致性验证 ==="

# 检查Sidecar和Prometheus数据一致性
echo "检查实时数据一致性..."

# 从Prometheus直接查询
prometheus_data=$(curl -s "http://localhost:9090/api/v1/query?query=up")
prometheus_count=$(echo "$prometheus_data" | jq '.data.result | length')

# 从Thanos Query查询
thanos_data=$(curl -s "http://localhost:19192/api/v1/query?query=up")
thanos_count=$(echo "$thanos_data" | jq '.data.result | length')

if [ "$prometheus_count" -eq "$thanos_count" ]; then
    echo "✓ 实时数据一致性: 匹配 (指标数: $prometheus_count)"
else
    echo "⚠ 实时数据不一致: Prometheus($prometheus_count) vs Thanos($thanos_count)"
fi

# 检查历史数据可用性
echo "检查历史数据可用性..."

# 查询1小时前的数据
one_hour_ago=$(date -d '1 hour ago' +%s)
historical_query=$(curl -s "http://localhost:19192/api/v1/query?query=up&time=${one_hour_ago}")

if echo "$historical_query" | grep -q '"status":"success"'; then
    historical_count=$(echo "$historical_query" | jq '.data.result | length')
    echo "✓ 历史数据查询成功 (指标数: $historical_count)"
else
    echo "⚠ 历史数据查询失败"
fi

# 检查对象存储数据完整性
echo "检查对象存储数据完整性..."

# 使用thanos工具检查块文件
if command -v thanos &> /dev/null; then
    # 检查块文件完整性
    bucket_verify=$(thanos tools bucket verify --objstore.config-file=minio-bucket.yaml 2>&1)
    
    if echo "$bucket_verify" | grep -q "checking"; then
        echo "✓ 对象存储数据完整性检查启动"
        # 这里可以解析详细结果
    else
        echo "⚠ 对象存储检查失败"
    fi
else
    echo "⚠ Thanos工具不可用，跳过对象存储检查"
fi

# 检查数据延迟
echo "检查数据延迟..."
latency_metrics=$(curl -s http://localhost:19191/metrics | grep -E "thanos_sidecar.*latency|thanos_shipper.*lag")

if echo "$latency_metrics" | grep -q "thanos_sidecar_latest_upload"; then
    upload_lag=$(echo "$latency_metrics" | grep "thanos_sidecar_latest_upload" | awk '{print $2}')
    current_time=$(date +%s)
    lag_seconds=$((current_time - upload_lag))
    
    if [ "$lag_seconds" -lt 300 ]; then
        echo "✓ 数据延迟正常 (${lag_seconds}秒)"
    else
        echo "⚠ 数据延迟较高 (${lag_seconds}秒)"
    fi
else
    echo "⚠ 无法获取延迟指标"
fi

echo "=== 一致性验证完成 ==="
```

## 3.5 高级集成配置

### 3.5.1 多集群集成

**多集群配置示例**：

```yaml
# 集群A配置
thanos-sidecar-a:
  image: thanosio/thanos:latest
  command:
    - sidecar
    - --http-address=0.0.0.0:19191
    - --grpc-address=0.0.0.0:19090
    - --prometheus.url=http://prometheus-a:9090
    - --tsdb.path=/prometheus
    - --objstore.config-file=/etc/thanos/bucket.yaml
    - --label=cluster=cluster-a
    - --label=replica=01

# 集群B配置
thanos-sidecar-b:
  image: thanosio/thanos:latest
  command:
    - sidecar
    - --http-address=0.0.0.0:19192
    - --grpc-address=0.0.0.0:19091
    - --prometheus.url=http://prometheus-b:9090
    - --tsdb.path=/prometheus
    - --objstore.config-file=/etc/thanos/bucket.yaml
    - --label=cluster=cluster-b
    - --label=replica=01

# Query组件配置（聚合多集群）
thanos-query:
  image: thanosio/thanos:latest
  command:
    - query
    - --http-address=0.0.0.0:19193
    - --grpc-address=0.0.0.0:19092
    - --query.replica-label=replica
    - --store=thanos-sidecar-a:19090
    - --store=thanos-sidecar-b:19091
    - --store=thanos-store:19093
```

### 3.5.2 安全配置

**TLS加密配置**：

```yaml
# Sidecar TLS配置
thanos-sidecar:
  command:
    - sidecar
    - --grpc-server-tls-cert=/etc/thanos/tls/server.crt
    - --grpc-server-tls-key=/etc/thanos/tls/server.key
    - --grpc-server-tls-client-ca=/etc/thanos/tls/ca.crt

# Query TLS配置
thanos-query:
  command:
    - query
    - --grpc-client-tls-secure
    - --grpc-client-tls-cert=/etc/thanos/tls/client.crt
    - --grpc-client-tls-key=/etc/thanos/tls/client.key
    - --grpc-client-tls-ca=/etc/thanos/tls/ca.crt
```

## 3.6 本章总结

本章详细介绍了Thanos与Prometheus的集成配置，包括：

**关键集成点**：
- Sidecar模式的工作原理和配置方法
- 数据上传到对象存储的完整流程
- Query组件的查询路由和聚合机制
- 数据一致性验证和监控方法

**最佳实践**：
1. 为每个Prometheus实例配置独立的Sidecar
2. 使用标签区分不同集群和环境
3. 配置合理的上传间隔和重试策略
4. 建立完善的数据一致性监控
5. 在生产环境启用TLS加密通信

**故障排查要点**：
- 检查Sidecar与Prometheus的网络连通性
- 验证对象存储的访问权限和配置
- 监控数据上传延迟和失败率
- 定期进行数据一致性检查

在下一章中，我们将深入探讨Thanos的核心组件，包括Store、Compactor和Ruler组件的详细配置和使用方法。