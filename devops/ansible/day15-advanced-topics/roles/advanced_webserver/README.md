# Advanced Webserver Role

这是一个高级 Web 服务器角色示例，演示了 Ansible 角色的最佳实践。

## 功能特性

- 支持多种 Web 服务器（Nginx, Apache）
- 自动 SSL 配置
- 安全头配置
- 性能优化
- 日志管理
- 监控集成

## 变量

### 默认变量 (defaults/main.yml)

```yaml
# Web 服务器配置
webserver_type: nginx
webserver_port: 80
webserver_ssl_port: 443

# SSL 配置
webserver_ssl_enabled: false
webserver_ssl_certificate: /etc/ssl/certs/webserver.crt
webserver_ssl_certificate_key: /etc/ssl/private/webserver.key

# 安全配置
webserver_security_headers: true
webserver_hsts_enabled: true
webserver_hsts_max_age: 31536000

# 性能配置
webserver_worker_processes: auto
webserver_worker_connections: 1024
webserver_keepalive_timeout: 65

# 日志配置
webserver_access_log: /var/log/webserver/access.log
webserver_error_log: /var/log/webserver/error.log
```

## 依赖

此角色没有强制依赖，但建议与以下角色一起使用：
- `geerlingguy.certbot` (用于 SSL 证书)
- `geerlingguy.firewall` (用于防火墙配置)

## 使用示例

```yaml
- hosts: webservers
  roles:
    - role: advanced_webserver
      webserver_type: nginx
      webserver_ssl_enabled: true
      webserver_ssl_certificate: /etc/ssl/certs/example.com.crt
      webserver_ssl_certificate_key: /etc/ssl/private/example.com.key
```

## License

MIT

## Author

Your Name