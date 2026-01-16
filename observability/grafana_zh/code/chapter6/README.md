# 第6章：高级功能和最佳实践 - 可运行代码示例

本章提供了Grafana高级功能和最佳实践的完整实现，包括高可用性配置、插件管理、性能优化、安全配置等。

## 快速开始

### 1. 启动高可用集群

```bash
# 进入chapter6目录
cd chapter6

# 启动所有服务
docker-compose up -d
```

### 2. 访问服务

- **Grafana主实例**: http://localhost:3000 (admin/admin123)
- **Grafana备用实例**: http://localhost:3002 (admin/admin123)
- **负载均衡器**: http://localhost:80
- **Prometheus**: http://localhost:9090
- **MySQL**: localhost:3306 (root/root123)
- **Redis**: localhost:6379

### 3. 验证高可用性

1. 访问负载均衡器: http://localhost:80
2. 停止主实例: `docker stop grafana-primary`
3. 验证备用实例自动接管
4. 重启主实例: `docker start grafana-primary`

## 架构说明

### 高可用架构
- **Grafana主实例**: 主要服务实例
- **Grafana备用实例**: 热备服务实例
- **MySQL数据库**: 共享数据存储
- **Redis缓存**: 会话和缓存管理
- **Nginx负载均衡器**: 流量分发和故障转移

### 监控体系
- **Prometheus**: 指标收集和告警
- **Node Exporter**: 系统指标监控
- **自定义指标**: 性能监控和用户活动跟踪

## 文件结构

```
chapter6/
├── docker-compose.yml          # 高可用集群编排
├── mysql/
│   └── init.sql               # 数据库初始化和性能监控表
├── nginx/
│   └── nginx.conf             # 负载均衡器配置
├── prometheus/
│   └── prometheus.yml         # 监控配置
├── provisioning/
│   ├── datasources/
│   │   └── datasource.yml     # 多数据源配置
│   ├── dashboards/
│   │   └── dashboard.yml      # 仪表板自动配置
│   └── plugins/
│       └── plugins.yml        # 插件管理配置
└── README.md                  # 说明文档
```

## 高级功能实现

### 1. 高可用性配置

#### 数据库共享
```ini
# Grafana配置
GF_DATABASE_TYPE=mysql
GF_DATABASE_HOST=mysql
GF_DATABASE_NAME=grafana
GF_DATABASE_USER=grafana
GF_DATABASE_PASSWORD=grafana123
```

#### 会话共享
```ini
# 使用Redis进行会话管理
[session]
provider = redis
provider_config = addr=redis:6379,password=,db=0,pool_size=100
cookie_name = grafana_sess
cookie_secure = false
session_life_time = 86400
```

### 2. 负载均衡配置

#### Nginx配置
```nginx
upstream grafana_backend {
    least_conn;
    server grafana-primary:3000 max_fails=3 fail_timeout=30s;
    server grafana-secondary:3000 max_fails=3 fail_timeout=30s backup;
}
```

### 3. 性能优化

#### 数据库连接池
```yaml
jsonData:
  maxOpenConns: 10
  maxIdleConns: 10
  connMaxLifetime: 14400
  cacheMode: "true"
```

#### 缓存配置
```ini
[cache]
enabled = true
backend = redis
backend_config = addr=redis:6379,password=,db=1,pool_size=100
```

### 4. 安全配置

#### 安全头设置
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

#### 数据库安全
```sql
-- 创建专用用户
CREATE USER 'grafana'@'%' IDENTIFIED BY 'grafana123';
GRANT SELECT, INSERT, UPDATE, DELETE ON grafana.* TO 'grafana'@'%';
```

## 最佳实践

### 1. 高可用性最佳实践

#### 故障转移策略
- 使用最少连接负载均衡算法
- 设置合理的健康检查间隔
- 配置备份服务器自动接管

#### 数据一致性
- 使用共享数据库确保数据一致性
- 配置会话共享避免用户登录状态丢失
- 定期备份关键数据

### 2. 性能优化最佳实践

#### 查询优化
- 使用适当的查询时间范围
- 避免过于复杂的查询表达式
- 利用缓存减少数据库查询

#### 资源管理
- 合理配置连接池大小
- 监控内存和CPU使用情况
- 设置适当的超时时间

### 3. 安全最佳实践

#### 访问控制
- 使用强密码策略
- 限制数据库用户权限
- 配置适当的防火墙规则

#### 数据保护
- 加密敏感配置信息
- 定期更新软件版本
- 监控安全日志

## 监控和告警

### 系统监控指标
- CPU使用率、内存使用率、磁盘空间
- 网络流量、连接数、响应时间
- 数据库性能、缓存命中率

### 业务监控指标
- 用户活跃度、仪表板访问量
- 查询性能、数据源健康状态
- 插件使用情况、系统负载

### 告警规则
```yaml
- alert: HighAvailabilityFailover
  expr: up{instance=~"grafana-.*"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Grafana实例故障转移"
    description: "Grafana实例发生故障转移"
```

## 故障排除

### 常见问题

#### 高可用性问题
1. **实例无法同步**
   - 检查数据库连接状态
   - 验证网络连通性
   - 查看会话配置

2. **负载均衡失效**
   - 检查Nginx健康检查配置
   - 验证后端服务状态
   - 查看负载均衡日志

#### 性能问题
1. **响应缓慢**
   - 检查数据库性能
   - 验证缓存配置
   - 监控系统资源

2. **内存泄漏**
   - 检查Grafana日志
   - 监控内存使用趋势
   - 调整JVM参数

### 日志分析

```bash
# 查看Grafana日志
docker logs grafana-primary
docker logs grafana-secondary

# 查看Nginx日志
docker logs nginx-chapter6

# 查看数据库日志
docker logs mysql-chapter6

# 查看监控日志
docker logs prometheus-chapter6
```

## 扩展配置

### 添加新的数据源
在`provisioning/datasources/datasource.yml`中添加：

```yaml
- name: New-Data-Source
  type: prometheus
  access: proxy
  url: http://new-prometheus:9090
  jsonData:
    timeInterval: 5s
```

### 配置新的插件
在`provisioning/plugins/plugins.yml`中添加：

```yaml
- type: new-plugin
  version: 1.0.0
```

### 优化性能参数
根据实际需求调整：
- 数据库连接池大小
- 缓存配置参数
- 负载均衡策略
- 监控采集频率

## 维护操作

### 定期维护
1. **数据库维护**
   ```sql
   -- 清理过期数据
   DELETE FROM user_activity WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
   
   -- 优化表性能
   OPTIMIZE TABLE performance_metrics;
   ```

2. **缓存清理**
   ```bash
   # 清理Redis缓存
   docker exec redis-chapter6 redis-cli FLUSHDB
   ```

3. **日志轮转**
   ```bash
   # 配置日志轮转策略
   logrotate /etc/logrotate.d/grafana
   ```

### 备份和恢复
1. **数据库备份**
   ```bash
   # 备份MySQL数据
   docker exec mysql-chapter6 mysqldump -u root -p grafana > backup.sql
   ```

2. **配置文件备份**
   ```bash
   # 备份关键配置
   tar -czf grafana-config-backup.tar.gz provisioning/ nginx/ prometheus/
   ```

3. **恢复操作**
   ```bash
   # 恢复数据库
   docker exec -i mysql-chapter6 mysql -u root -p grafana < backup.sql
   ```