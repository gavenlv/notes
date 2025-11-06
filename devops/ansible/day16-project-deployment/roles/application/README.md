# Application Role

应用部署和管理角色，用于部署和配置应用程序。

## 功能特性

- 应用包部署
- 配置文件管理
- 服务管理
- 健康检查
- 日志配置
- 监控集成

## 变量

### 默认变量 (defaults/main.yml)

```yaml
# 应用基本信息
app_name: "myapp"
app_version: "1.0.0"
app_user: "appuser"
app_group: "appgroup"

# 部署配置
app_deploy_path: "/var/www/{{ app_name }}"
app_config_path: "/etc/{{ app_name }}"
app_log_path: "/var/log/{{ app_name }}"

# 服务配置
app_service_name: "{{ app_name }}"
app_port: 8080
app_environment: "production"

# 数据库配置
app_db_host: "localhost"
app_db_port: 5432
app_db_name: "{{ app_name }}"
app_db_user: "{{ app_name }}_user"
```

## 使用示例

```yaml
- hosts: webservers
  roles:
    - role: application
      app_name: mywebapp
      app_version: 2.1.0
      app_port: 3000
```

## License

MIT