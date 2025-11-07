#!/bin/bash

# 日志收集优化实验脚本
# 适用于 Linux/macOS 系统

echo "=== 日志收集优化实验 ==="

# 创建测试目录
mkdir -p test-logs promtail-configs

# 生成高基数日志
echo "生成高基数日志..."
for i in {1..1000}; do
  echo "2023-10-01T10:00:00.000Z [INFO] Request processed with ID $(uuidgen)" >> test-logs/high-cardinality.log
done

# 生成低基数日志
echo "生成低基数日志..."
for i in {1..1000}; do
  echo "2023-10-01T10:00:00.000Z [INFO] Request processed" >> test-logs/low-cardinality.log
done

# 生成JSON格式日志
echo "生成JSON格式日志..."
for i in {1..500}; do
  echo '{"timestamp": "2023-10-01T10:00:00.000Z", "level": "INFO", "message": "Request processed", "request_id": "'$(uuidgen)'", "user_id": "'$((RANDOM % 1000))'", "response_time_ms": '$((RANDOM % 1000))' }' >> test-logs/structured.log
done

# 创建高基数配置
echo "创建高基数配置..."
cat > promtail-configs/high-cardinality.yaml << EOF
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions-high.yaml

clients:
  - url: http://host.docker.internal:3100/loki/api/v1/push

scrape_configs:
  - job_name: high-cardinality
    static_configs:
      - targets:
          - localhost
        labels:
          job: high-cardinality
        __path__: /var/log/high-cardinality.log

    pipeline_stages:
      # 从日志中提取请求ID作为标签
      - regex:
          expression: 'ID (?P<request_id>[a-f0-9-]+)'
      - labels:
          request_id:
EOF

# 创建低基数配置
echo "创建低基数配置..."
cat > promtail-configs/low-cardinality.yaml << EOF
server:
  http_listen_port: 9081
  grpc_listen_port: 0

positions:
  filename: /tmp/positions-low.yaml

clients:
  - url: http://host.docker.internal:3100/loki/api/v1/push

scrape_configs:
  - job_name: low-cardinality
    static_configs:
      - targets:
          - localhost
        labels:
          job: low-cardinality
        __path__: /var/log/low-cardinality.log
EOF

# 创建结构化日志配置（带优化）
echo "创建结构化日志配置..."
cat > promtail-configs/structured.yaml << EOF
server:
  http_listen_port: 9082
  grpc_listen_port: 0

positions:
  filename: /tmp/positions-structured.yaml

clients:
  - url: http://host.docker.internal:3100/loki/api/v1/push

scrape_configs:
  - job_name: structured
    static_configs:
      - targets:
          - localhost
        labels:
          job: structured
        __path__: /var/log/structured.log

    pipeline_stages:
      # 解析JSON
      - json:
          expressions:
            timestamp: timestamp
            level: level
            message: message
            request_id: request_id
            user_id: user_id
            response_time_ms: response_time_ms

      # 时间戳提取
      - timestamp:
          format: RFC3339Nano
          source: timestamp

      # 优化标签策略：不提取高基数request_id，而是提取其他有用字段
      - labels:
          level:
          - output:
              source: message

      # 对响应时间进行范围分组，减少基数
      - match:
          selector: '{response_time_ms <= "100"}'
          pipeline_stages:
            - labels:
                response_time_range: fast

      - match:
          selector: '{response_time_ms > "100"} <= "500"'
          pipeline_stages:
            - labels:
                response_time_range: medium

      - match:
          selector: '{response_time_ms > "500"}'
          pipeline_stages:
            - labels:
                response_time_range: slow

      # 对用户ID进行哈希处理，减少基数
      - template:
          source: user_id_hash
          template: '{{ .user_id | hash "crc32" }}'
      - labels:
          user_id_hash:
EOF

# 创建批处理优化配置
echo "创建批处理优化配置..."
cat > promtail-configs/batch-optimized.yaml << EOF
server:
  http_listen_port: 9083
  grpc_listen_port: 0

positions:
  filename: /tmp/positions-batch.yaml

clients:
  - url: http://host.docker.internal:3100/loki/api/v1/push
    batchwait: 5s               # 增加等待时间
    batchsize: 1024 * 1024       # 增大批大小(1MB)
    timeout: 30s                 # 增加超时时间
    backoff_config:
      minbackoff: 100ms
      maxbackoff: 5s
      maxretries: 10

scrape_configs:
  - job_name: batch-optimized
    static_configs:
      - targets:
          - localhost
        labels:
          job: batch-optimized
        __path__: /var/log/structured.log

    pipeline_stages:
      - json:
          expressions:
            timestamp: timestamp
            level: level
            message: message
            response_time_ms: response_time_ms

      - timestamp:
          format: RFC3339Nano
          source: timestamp

      - labels:
          level:

      - output:
          source: message
EOF

# 创建Docker Compose文件
echo "创建Docker Compose文件..."
cat > docker-compose.yaml << EOF
version: "3.8"

services:
  loki:
    image: grafana/loki:2.9.0
    container_name: loki
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./config/loki-local-config.yaml:/etc/loki/local-config.yaml
      - ./data:/loki
    networks:
      - loki

  # 高基数测试
  promtail-high:
    image: grafana/promtail:2.9.0
    container_name: promtail-high
    volumes:
      - ./promtail-configs/high-cardinality.yaml:/etc/promtail/config.yml
      - ./test-logs/high-cardinality.log:/var/log/high-cardinality.log:ro
    command: -config.file=/etc/promtail/config.yml
    networks:
      - loki

  # 低基数测试
  promtail-low:
    image: grafana/promtail:2.9.0
    container_name: promtail-low
    volumes:
      - ./promtail-configs/low-cardinality.yaml:/etc/promtail/config.yml
      - ./test-logs/low-cardinality.log:/var/log/low-cardinality.log:ro
    command: -config.file=/etc/promtail/config.yml
    networks:
      - loki

  # 结构化日志测试
  promtail-structured:
    image: grafana/promtail:2.9.0
    container_name: promtail-structured
    volumes:
      - ./promtail-configs/structured.yaml:/etc/promtail/config.yml
      - ./test-logs/structured.log:/var/log/structured.log:ro
    command: -config.file=/etc/promtail/config.yml
    networks:
      - loki

  # 批处理优化测试
  promtail-batch:
    image: grafana/promtail:2.9.0
    container_name: promtail-batch
    volumes:
      - ./promtail-configs/batch-optimized.yaml:/etc/promtail/config.yml
      - ./test-logs/structured.log:/var/log/structured.log:ro
    command: -config.file=/etc/promtail/config.yml
    networks:
      - loki

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana
    networks:
      - loki

volumes:
  grafana-storage:

networks:
  loki:
    driver: bridge
EOF

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 15

# 性能测试函数
performance_test() {
  echo "=== 性能测试: $1 ==="
  start_time=$(date +%s)
  
  # 执行查询
  curl -G -s "http://localhost:3100/loki/api/v1/query_range" \
    --data-urlencode 'query='"$2"'' \
    --data-urlencode 'start=2023-10-01T09:00:00.000Z' \
    --data-urlencode 'end=2023-10-01T11:00:00.000Z' \
    --data-urlencode 'step=30s' > /dev/null
    
  end_time=$(date +%s)
  duration=$((end_time - start_time))
  echo "$1 查询时间: ${duration}s"
  
  # 检查目标状态
  curl -s "http://localhost:3100/loki/api/v1/label/stream/values" | jq ".data[]" | grep "$3" | wc -l
}

echo "等待Promtail收集日志..."
sleep 10

# 测试查询性能
echo "=== 测试不同配置的查询性能 ==="
performance_test "高基数" '{job="high-cardinality"}' "high-cardinality"
performance_test "低基数" '{job="low-cardinality"}' "low-cardinality"
performance_test "结构化" '{job="structured"}' "structured"
performance_test "批处理优化" '{job="batch-optimized"}' "batch-optimized"

# 检查标签基数
echo "=== 检查标签基数 ==="
echo "高基数配置的request_id标签数量:"
curl -s "http://localhost:3100/loki/api/v1/label/request_id/values" | jq '.data | length'

echo "结构化配置的response_time_range标签数量:"
curl -s "http://localhost:3100/loki/api/v1/label/response_time_range/values" | jq '.data'

echo "结构化配置的user_id_hash标签数量:"
curl -s "http://localhost:3100/loki/api/v1/label/user_id_hash/values" | jq '.data | length'

# 检查资源使用
echo "=== 检查资源使用 ==="
docker stats --no-stream | grep -E "promtail|loki"

# 显示访问信息
echo "=== 访问信息 ==="
echo "Grafana: http://localhost:3000"
echo "默认用户名/密码: admin/admin"
echo ""
echo "在Grafana中比较不同配置的性能:"
echo "1. 转到 Explore 模式"
echo "2. 选择 Loki 数据源"
echo "3. 尝试以下查询:"
echo "   - {job=\"high-cardinality\"}"
echo "   - {job=\"low-cardinality\"}"
echo "   - {job=\"structured\"}"
echo "   - {job=\"batch-optimized\"}"
echo "4. 比较查询性能和结果"

# 提供测试命令
echo "=== 有用的测试命令 ==="
echo "查看Promtail日志: docker-compose logs -f promtail-high"
echo "停止服务: docker-compose down"
echo "清理数据: docker-compose down -v"