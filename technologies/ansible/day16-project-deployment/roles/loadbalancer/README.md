# Load Balancer Role

负载均衡器配置角色，用于配置和管理负载均衡服务。

## 功能特性

- Nginx负载均衡配置
- HAProxy负载均衡配置
- 健康检查配置
- SSL/TLS终端配置
- 访问控制配置
- 日志和监控集成
- 高可用性配置

## 支持的负载均衡器

- Nginx (默认)
- HAProxy

## 变量

### 默认变量 (defaults/main.yml)

```yaml
# 负载均衡器类型
lb_type: "nginx"

# 监听端口
lb_port: 80
lb_ssl_port: 443

# SSL配置
lb_ssl_enabled: false
lb_ssl_certificate: ""
lb_ssl_certificate_key: ""

# 后端服务器
lb_backend_servers: []
```

## 使用示例

```yaml
- hosts: loadbalancers
  roles:
    - role: loadbalancer
      lb_type: nginx
      lb_port: 80
      lb_backend_servers:
        - name: web1
          address: 10.0.1.10
          port: 8080
        - name: web2
          address: 10.0.1.11
          port: 8080
```

## License

MIT