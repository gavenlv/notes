# Grafana 企业级部署示例

这是一个完整的Grafana企业级高可用部署示例，包含负载均衡、多实例部署、共享存储、认证集成等企业级功能。

## 架构组件

- **Nginx**: 负载均衡和SSL终止
- **Grafana Enterprise**: 3个Grafana实例
- **PostgreSQL**: 共享数据库
- **Redis**: 缓存和会话存储
- **Prometheus**: 监控数据源

## 部署前准备

1. 安装 Docker 和 Docker Compose
2. 准备SSL证书
3. 配置环境变量
4. 准备SAML认证配置

## 部署步骤

1. 克隆或创建配置文件
2. 配置环境变量（.env文件）
3. 准备SSL证书
4. 启动服务

```bash
# 创建SSL证书目录
mkdir -p ssl

# 将SSL证书复制到ssl目录
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem

# 启动服务
docker-compose up -d
```

## 配置说明

### 环境变量

- `ADMIN_PASSWORD`: Grafana管理员密码
- `DB_PASSWORD`: PostgreSQL数据库密码
- `REDIS_PASSWORD`: Redis缓存密码

### SSL/TLS配置

将SSL证书放在`ssl`目录下：
- `ssl/cert.pem`: SSL证书
- `ssl/key.pem`: SSL私钥

### SAML配置

将SAML配置文件放在`saml`目录下：
- `saml/cert.pem`: SAML证书
- `saml/key.pem`: SAML私钥

## 扩展功能

### 高可用性

- 3个Grafana实例提供高可用性
- Nginx负载均衡确保流量分配
- PostgreSQL提供共享持久化存储

### 安全性

- TLS/SSL加密所有通信
- SAML企业级认证集成
- 安全头部防止常见攻击
- 数据库审计日志

### 可扩展性

- 可轻松添加更多Grafana实例
- 独立的缓存层提高性能
- 模块化设计便于扩展

## 监控和告警

### Prometheus集成

- 收集Grafana实例指标
- 监控系统资源使用
- 设置告警规则

### 日志管理

```bash
# 查看Grafana日志
docker-compose logs grafana-1
docker-compose logs grafana-2
docker-compose logs grafana-3

# 查看Nginx日志
docker-compose logs nginx

# 查看所有服务状态
docker-compose ps
```

## 备份和恢复

### 数据库备份

```bash
# 备份PostgreSQL
docker-compose exec postgres pg_dump -U grafana grafana > grafana_backup.sql

# 恢复PostgreSQL
docker-compose exec -T postgres psql -U grafana grafana < grafana_backup.sql
```

### 配置备份

```bash
# 备份配置文件
tar -czf grafana_config_backup.tar.gz ./
```

## 故障排除

### 常见问题

1. **Grafana实例无法启动**
   - 检查环境变量配置
   - 确认数据库连接
   - 查看容器日志

2. **负载均衡不工作**
   - 检查Nginx配置
   - 确认后端服务状态
   - 验证端口开放

3. **SAML认证失败**
   - 检查证书文件
   - 验证IDP配置
   - 查看Grafana日志

### 调试命令

```bash
# 进入容器调试
docker-compose exec grafana-1 bash

# 检查网络连接
docker-compose exec grafana-1 ping postgres

# 查看环境变量
docker-compose exec grafana-1 env | grep GF_
```

## 维护操作

### 更新服务

```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d
```

### 扩展实例

```bash
# 添加更多Grafana实例，在docker-compose.yml中添加新的服务
# 然后在nginx.conf中更新upstream配置
```

### 资源限制

根据需要调整资源限制：

```yaml
# 在docker-compose.yml中添加资源限制
services:
  grafana-1:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

## 性能优化

1. **数据库优化**
   - 调整PostgreSQL配置
   - 优化查询和索引
   - 定期清理旧数据

2. **缓存策略**
   - 配置Redis缓存
   - 调整Grafana缓存设置
   - 使用CDN分发静态资源

3. **网络优化**
   - 优化Nginx配置
   - 启用HTTP/2
   - 使用连接复用

## 参考资料

- [Grafana企业版文档](https://grafana.com/docs/enterprise/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Nginx负载均衡指南](https://nginx.org/en/docs/http/load_balancing.html)
- [PostgreSQL性能优化](https://www.postgresql.org/docs/current/performance-tips.html)