#!/bin/bash

# 日志查询实验脚本
# 适用于 Linux/macOS 系统

echo "=== 日志查询实验 ==="

# 创建测试日志目录
mkdir -p test-logs

# 生成测试数据
echo "生成测试数据..."

# 生成API服务日志
cat > test-logs/api.log << EOF
2023-10-01T10:00:00.000Z [INFO] API service started
2023-10-01T10:01:00.000Z [INFO] GET /api/users - 200 - 120ms
2023-10-01T10:02:00.000Z [INFO] POST /api/login - 200 - 250ms
2023-10-01T10:03:00.000Z [WARN] POST /api/login - 401 - 150ms
2023-10-01T10:04:00.000Z [ERROR] Database connection failed
2023-10-01T10:05:00.000Z [INFO] GET /api/users/123 - 200 - 80ms
2023-10-01T10:06:00.000Z [ERROR] User not found: 456
2023-10-01T10:07:00.000Z [INFO] DELETE /api/users/123 - 200 - 100ms
2023-10-01T10:08:00.000Z [WARN] Rate limit exceeded for IP: 192.168.1.100
2023-10-01T10:09:00.000Z [INFO] PUT /api/users/123 - 200 - 180ms
2023-10-01T10:10:00.000Z [ERROR] Authentication failed: invalid token
EOF

# 生成Web服务器日志
cat > test-logs/web.log << EOF
192.168.1.100 - - [01/Oct/2023:10:01:00 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [01/Oct/2023:10:02:00 +0000] "GET /css/style.css HTTP/1.1" 200 567 "-" "Mozilla/5.0"
192.168.1.102 - - [01/Oct/2023:10:03:00 +0000] "POST /api/login HTTP/1.1" 401 89 "-" "curl/7.68.0"
192.168.1.100 - - [01/Oct/2023:10:04:00 +0000] "GET /dashboard HTTP/1.1" 200 2345 "-" "Mozilla/5.0"
192.168.1.103 - - [01/Oct/2023:10:05:00 +0000] "DELETE /api/users/123 HTTP/1.1" 200 12 "-" "axios/0.21.1"
192.168.1.104 - - [01/Oct/2023:10:06:00 +0000] "GET /api/users HTTP/1.1" 200 567 "-" "Mozilla/5.0"
192.168.1.105 - - [01/Oct/2023:10:07:00 +0000] "GET /admin HTTP/1.1" 403 23 "-" "Mozilla/5.0"
192.168.1.100 - - [01/Oct/2023:10:08:00 +0000] "POST /api/upload HTTP/1.1" 500 34 "-" "curl/7.68.0"
192.168.1.106 - - [01/Oct/2023:10:09:00 +0000] "GET /favicon.ico HTTP/1.1" 200 1024 "-" "Mozilla/5.0"
192.168.1.101 - - [01/Oct/2023:10:10:00 +0000] "GET /api/products HTTP/1.1" 200 890 "-" "Mozilla/5.0"
EOF

# 生成JSON格式日志
cat > test-logs/app.json << EOF
{"timestamp": "2023-10-01T10:00:00.000Z", "level": "INFO", "service": "auth", "message": "Service started", "version": "1.2.3"}
{"timestamp": "2023-10-01T10:01:00.000Z", "level": "INFO", "service": "auth", "message": "User login successful", "user_id": "12345", "ip": "192.168.1.100"}
{"timestamp": "2023-10-01T10:02:00.000Z", "level": "WARN", "service": "auth", "message": "Failed login attempt", "user_id": "0", "ip": "192.168.1.102"}
{"timestamp": "2023-10-01T10:03:00.000Z", "level": "ERROR", "service": "auth", "message": "Database connection failed", "error": "connection timeout"}
{"timestamp": "2023-10-01T10:04:00.000Z", "level": "INFO", "service": "payment", "message": "Payment processed", "payment_id": "pay_12345", "amount": 99.99, "currency": "USD"}
{"timestamp": "2023-10-01T10:05:00.000Z", "level": "INFO", "service": "payment", "message": "Refund processed", "payment_id": "pay_67890", "amount": 25.50, "currency": "USD"}
{"timestamp": "2023-10-01T10:06:00.000Z", "level": "ERROR", "service": "payment", "message": "Payment gateway timeout", "payment_id": "pay_11111", "error": "timeout after 30s"}
{"timestamp": "2023-10-01T10:07:00.000Z", "level": "INFO", "service": "notification", "message": "Email sent", "recipient": "user@example.com", "template": "welcome"}
{"timestamp": "2023-10-01T10:08:00.000Z", "level": "WARN", "service": "notification", "message": "Email delivery failed", "recipient": "invalid-email", "error": "invalid address"}
{"timestamp": "2023-10-01T10:09:00.000Z", "level": "INFO", "service": "notification", "message": "SMS sent", "recipient": "+1234567890", "template": "verification"}
EOF

# 创建Promtail配置文件
echo "创建Promtail配置..."
cat > promtail-config.yaml << EOF
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://host.docker.internal:3100/loki/api/v1/push

scrape_configs:
  # API服务日志
  - job_name: api
    static_configs:
      - targets:
          - localhost
        labels:
          job: api
          component: backend
        __path__: /var/log/api.log

    pipeline_stages:
      - regex:
          expression: '(?P<timestamp>\S+) \[(?P<level>\w+)\] (?P<message>.*)'
      - timestamp:
          format: RFC3339Nano
          source: timestamp
      - labels:
          level:
          - output:
              source: message

  # Web服务器日志
  - job_name: web
    static_configs:
      - targets:
          - localhost
        labels:
          job: nginx
          component: frontend
        __path__: /var/log/web.log

    pipeline_stages:
      - regex:
          expression: '(?P<client_ip>\S+) - - \[(?P<timestamp>.+)\] "(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" (?P<status>\d+) (?P<size>\d+)'
      - labels:
          method:
          status:
      - output:
          source: message

  # JSON格式日志
  - job_name: app
    static_configs:
      - targets:
          - localhost
        labels:
          job: app
        __path__: /var/log/app.json

    pipeline_stages:
      - json:
          expressions:
            level: level
            service: service
            message: message
            user_id: user_id
            ip: ip
            error: error
            payment_id: payment_id
            amount: amount
            currency: currency
            recipient: recipient
            template: template
      - labels:
          level:
          service:
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

  promtail:
    image: grafana/promtail:2.9.0
    container_name: promtail
    volumes:
      - ./promtail-config.yaml:/etc/promtail/config.yml
      - ./test-logs:/var/log:ro
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

# 等待日志收集
echo "等待日志收集..."
sleep 10

# 查询函数
run_query() {
  local query_name="$1"
  local query="$2"
  
  echo "=== $query_name ==="
  echo "查询: $query"
  
  curl -G -s "http://localhost:3100/loki/api/v1/query" \
    --data-urlencode "query=$query" \
    -H 'Accept: application/json' | jq '.data.result[0].metric, .data.result[0].value'
  echo ""
}

# 范围查询函数
run_range_query() {
  local query_name="$1"
  local query="$2"
  
  echo "=== $query_name ==="
  echo "查询: $query"
  
  curl -G -s "http://localhost:3100/loki/api/v1/query_range" \
    --data-urlencode "query=$query" \
    --data-urlencode 'start=2023-10-01T09:00:00.000Z' \
    --data-urlencode 'end=2023-10-01T11:00:00.000Z' \
    --data-urlencode 'step=30s' \
    -H 'Accept: application/json' | jq '.data.result[0].metric, (.data.result[0].values | length)'
  echo ""
}

echo "=== 基础查询示例 ==="

# 1. 查询所有日志
run_query "查询所有日志" '{job=~".+"}'

# 2. 按作业查询
run_query "查询API服务日志" '{job="api"}'
run_query "查询Web服务器日志" '{job="nginx"}'
run_query "查询应用日志" '{job="app"}'

# 3. 按组件查询
run_query "查询后端组件日志" '{component="backend"}'
run_query "查询前端组件日志" '{component="frontend"}'

echo "=== 内容过滤查询 ==="

# 4. 简单内容过滤
run_query "包含error的日志" '{job=~".+"} |= "error"'
run_query "包含ERROR的日志" '{job=~".+"} |= "ERROR"'

# 5. 正则表达式过滤
run_query "包含数据库相关错误" '{job="api"} |~ "database|Database"'

# 6. 不包含过滤
run_query "不包含INFO的日志" '{job="api"} != "INFO"'

echo "=== JSON日志查询 ==="

# 7. JSON字段过滤
run_query "支付服务的日志" '{job="app"} | json | service="payment"'
run_query "ERROR级别的日志" '{job="app"} | json | level="ERROR"'

# 8. 提取标签后的查询
run_query "认证服务的ERROR日志" '{job="app",service="auth",level="ERROR"}'

echo "=== Web服务器日志查询 ==="

# 9. HTTP状态码过滤
run_query "4xx错误" '{job="nginx",status=~"4.."}'
run_query "5xx错误" '{job="nginx",status=~"5.."}'

# 10. HTTP方法过滤
run_query "POST请求" '{job="nginx",method="POST"}'

echo "=== 聚合查询 ==="

# 11. 计数查询
run_range_query "API服务日志计数" 'count_over_time({job="api"} [5m])'
run_range_query "ERROR日志计数" 'count_over_time({job=~".+"} |= "ERROR" [5m])'

# 12. 错误率计算
run_query "API服务错误率" 'sum(count_over_time({job="api"} |= "ERROR" [5m])) / sum(count_over_time({job="api"} [5m])) * 100'

# 13. 按级别分组的计数
run_range_query "按级别分组的日志计数" 'sum by (level) (count_over_time({job="app"} [5m]))'

# 14. 按服务分组的计数
run_range_query "按服务分组的计数" 'sum by (service) (count_over_time({job="app"} [5m]))'

echo "=== 性能测试 ==="

# 测试查询性能
echo "=== 查询性能测试 ==="

# 测试标签查询性能
echo "测试标签查询性能..."
time_start=$(date +%s%N)
curl -s "http://localhost:3100/loki/api/v1/query" --data-urlencode 'query={job="api"}' > /dev/null
time_end=$(date +%s%N)
query_time_ms=$(( (time_end - time_start) / 1000000 ))
echo "标签查询时间: ${query_time_ms}ms"

# 测试内容过滤查询性能
echo "测试内容过滤查询性能..."
time_start=$(date +%s%N)
curl -s "http://localhost:3100/loki/api/v1/query" --data-urlencode 'query={job="api"} |= "ERROR"' > /dev/null
time_end=$(date +%s%N)
query_time_ms=$(( (time_end - time_start) / 1000000 ))
echo "内容过滤查询时间: ${query_time_ms}ms"

# 测试JSON查询性能
echo "测试JSON查询性能..."
time_start=$(date +%s%N)
curl -s "http://localhost:3100/loki/api/v1/query" --data-urlencode 'query={job="app"} | json | service="payment"' > /dev/null
time_end=$(date +%s%N)
query_time_ms=$(( (time_end - time_start) / 1000000 ))
echo "JSON查询时间: ${query_time_ms}ms"

# 显示访问信息
echo "=== 访问信息 ==="
echo "Grafana: http://localhost:3000"
echo "默认用户名/密码: admin/admin"
echo ""
echo "在Grafana中练习查询:"
echo "1. 转到 Explore 模式"
echo "2. 选择 Loki 数据源"
echo "3. 尝试上述各种查询"
echo "4. 探索不同的查询组合"

# 保存查询示例到文件
echo "=== 保存查询示例到文件 ==="
cat > loki-queries-examples.md << 'EOF'
# Loki查询示例

## 基础查询

### 查询所有日志
```
{job=~".+"}
```

### 按作业查询
```
{job="api"}
{job="nginx"}
{job="app"}
```

### 按组件查询
```
{component="backend"}
{component="frontend"}
```

## 内容过滤查询

### 简单内容过滤
```
{job=~".+"} |= "error"
{job=~".+"} |= "ERROR"
```

### 正则表达式过滤
```
{job="api"} |~ "database|Database"
```

### 不包含过滤
```
{job="api"} != "INFO"
```

## JSON日志查询

### JSON字段过滤
```
{job="app"} | json | service="payment"
{job="app"} | json | level="ERROR"
```

### 提取标签后的查询
```
{job="app",service="auth",level="ERROR"}
```

## Web服务器日志查询

### HTTP状态码过滤
```
{job="nginx",status=~"4.."}
{job="nginx",status=~"5.."}
```

### HTTP方法过滤
```
{job="nginx",method="POST"}
```

## 聚合查询

### 计数查询
```
count_over_time({job="api"} [5m])
count_over_time({job=~".+"} |= "ERROR" [5m])
```

### 错误率计算
```
sum(count_over_time({job="api"} |= "ERROR" [5m])) / sum(count_over_time({job="api"} [5m])) * 100
```

### 按级别分组的计数
```
sum by (level) (count_over_time({job="app"} [5m]))
```

### 按服务分组的计数
```
sum by (service) (count_over_time({job="app"} [5m]))
```
EOF

echo "查询示例已保存到 loki-queries-examples.md"

# 提供测试命令
echo "=== 有用的测试命令 ==="
echo "查看Loki日志: docker-compose logs -f loki"
echo "查看Promtail日志: docker-compose logs -f promtail"
echo "停止服务: docker-compose down"
echo "清理数据: docker-compose down -v"