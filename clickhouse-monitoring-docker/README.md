# ClickHouse + Prometheus + Grafana 监控系统

使用Docker在本地快速搭建完整的ClickHouse数据库监控系统，包含Prometheus指标收集和Grafana可视化展示。

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ClickHouse     │    │   Prometheus    │    │     Grafana      │
│  数据库服务      │◄───│  指标收集       │◄───│  可视化展示     │
│  端口: 8123/9000│    │  端口: 9090     │    │  端口: 3000     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │   ClickHouse Exporter      │
                    │  指标导出器               │
                    │  端口: 9333               │
                    └───────────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     Node Exporter         │
                    │    系统指标收集           │
                    │    端口: 9100             │
                    └───────────────────────────┘
```

## 快速开始

### 1. 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少4GB可用内存

### 2. 镜像源配置

系统已配置专用镜像源 `zlsmshoqvwt6q1.xuanyuan.run`，解决国内网络访问问题。

### 3. 启动服务

#### Linux/macOS:
```bash
chmod +x start.sh
./start.sh
```

#### Windows PowerShell (推荐):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\start.ps1
```

#### Windows CMD:
```cmd
start.bat
```

### 3. 访问服务

服务启动后，可以通过以下地址访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| Grafana | http://localhost:3000 | 可视化监控面板，用户名: `admin`，密码: `admin123` |
| Prometheus | http://localhost:9090 | 指标收集和查询 |
| ClickHouse | http://localhost:8123 | 数据库HTTP接口 |
| Node Exporter | http://localhost:9100 | 系统指标 |
| ClickHouse Exporter | http://localhost:9333 | ClickHouse指标导出 |

## 监控指标

### ClickHouse核心指标

#### 资源使用
- **内存使用量**: `clickhouse_metrics_MemoryUsage`
- **磁盘使用率**: `clickhouse_metrics_DiskSpaceUsed / clickhouse_metrics_DiskSpaceTotal`
- **表大小**: `clickhouse_metrics_TableSizeBytes`

#### 查询性能
- **查询速率**: `rate(clickhouse_events_Total{event="Query"}[5m])`
- **查询延迟**: `histogram_quantile(0.95, rate(clickhouse_metrics_QueryDurationMicroseconds_bucket[5m]))`
- **查询队列**: `clickhouse_metrics_QueryQueueSize`

#### 错误统计
- **失败查询**: `rate(clickhouse_events_QueryFailed[5m])`
- **异常数量**: `rate(clickhouse_events_Exception[5m])`

#### 连接信息
- **TCP连接数**: `clickhouse_metrics_TCPConnection`
- **HTTP连接数**: `clickhouse_metrics_HTTPConnection`

#### 副本同步
- **副本延迟**: `clickhouse_metrics_ReplicasDelay`

### 系统指标

通过Node Exporter收集的系统级指标：
- CPU使用率
- 内存使用率
- 磁盘I/O
- 网络流量
- 系统负载

## 告警规则

系统包含以下预定义的告警规则：

### 关键告警 (Critical)
- 内存使用率 > 90%
- 磁盘空间使用率 > 90%
- 查询失败率 > 10%
- 连接拒绝率过高

### 警告告警 (Warning)
- CPU使用率 > 80%
- 查询延迟P95 > 10秒
- 查询队列 > 50
- 副本延迟 > 30秒
- TCP连接数 > 1000

## 配置文件说明

### Docker Compose配置
- `docker-compose.yml` - 主配置文件，定义所有服务

### ClickHouse配置
- `clickhouse/config.xml` - ClickHouse服务器配置
- `clickhouse/users.xml` - 用户认证配置

### Prometheus配置
- `prometheus/prometheus.yml` - Prometheus主配置
- `prometheus/clickhouse_rules.yml` - 告警规则配置

### Grafana配置
- `grafana/provisioning/datasources/prometheus.yml` - 数据源配置
- `grafana/provisioning/dashboards/dashboards.yml` - 仪表板配置
- `grafana/dashboards/clickhouse-overview.json` - ClickHouse监控仪表板

## 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs clickhouse
docker-compose logs prometheus
docker-compose logs grafana

# 停止服务
docker-compose down

# 重启特定服务
docker-compose restart clickhouse

# 查看资源使用
docker stats

# 进入容器
docker exec -it clickhouse bash
```

## 数据持久化

所有重要数据都进行了持久化存储：

- ClickHouse数据: `clickhouse-data` 卷
- ClickHouse日志: `clickhouse-logs` 卷
- Prometheus数据: `prometheus-data` 卷
- Grafana数据: `grafana-data` 卷

## 自定义配置

### 修改密码

修改 `docker-compose.yml` 中的环境变量：

```yaml
environment:
  - CLICKHOUSE_PASSWORD=your_new_password
  - GF_SECURITY_ADMIN_PASSWORD=your_new_password
```

### 添加新的监控指标

1. 在 `prometheus/prometheus.yml` 中添加新的抓取任务
2. 在 `prometheus/clickhouse_rules.yml` 中添加告警规则
3. 在Grafana中创建新的仪表板

### 镜像源配置

系统使用专用镜像源 `zlsmshoqvwt6q1.xuanyuan.run`，启动脚本会自动：

1. 从专用镜像源拉取镜像
2. 重新标记为原始镜像名称
3. 删除临时镜像

如需修改镜像源，编辑 `start.ps1` 或 `start.sh` 中的 `$registry` 变量。

### 扩展监控范围

可以添加以下组件：

- **Alertmanager**: 告警通知管理
- **Loki**: 日志收集和查询
- **Tempo**: 分布式追踪
- **Jaeger**: 调用链追踪

## 故障排除

### 常见问题

1. **端口冲突**: 修改 `docker-compose.yml` 中的端口映射
2. **内存不足**: 增加Docker内存分配或优化ClickHouse配置
3. **服务启动失败**: 检查日志 `docker-compose logs [service]`

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs clickhouse

# 实时查看日志
docker-compose logs -f prometheus
```

## 性能优化建议

1. **内存配置**: 根据实际需求调整ClickHouse内存限制
2. **存储优化**: 使用SSD硬盘提升I/O性能
3. **网络优化**: 确保容器间网络通信畅通
4. **监控优化**: 根据业务负载调整监控频率

## 安全考虑

1. **生产环境**: 修改默认密码
2. **网络隔离**: 使用内部网络，限制外部访问
3. **访问控制**: 配置适当的防火墙规则
4. **数据加密**: 考虑启用TLS加密通信

## 相关资源

- [ClickHouse官方文档](https://clickhouse.com/docs/)
- [Prometheus官方文档](https://prometheus.io/docs/)
- [Grafana官方文档](https://grafana.com/docs/)
- [ClickHouse Exporter](https://github.com/ClickHouse/clickhouse-exporter)

## 许可证

本项目基于MIT许可证开源。

---

**注意**: 本配置适用于开发和测试环境，生产环境部署请根据实际需求进行安全加固和性能优化。