# Database Role

数据库部署和管理角色，用于安装、配置和管理数据库服务。

## 功能特性

- 数据库安装 (PostgreSQL, MySQL, MongoDB)
- 数据库配置管理
- 用户和权限管理
- 数据库备份和恢复
- 性能优化
- 安全配置
- 主从复制配置
- 数据库监控集成

## 支持的数据库

- PostgreSQL (默认)
- MySQL
- MongoDB

## 变量

### 默认变量 (defaults/main.yml)

```yaml
# 数据库类型
db_type: "postgresql"

# 数据库版本
db_version: "13"

# 数据库管理员用户
db_admin_user: "postgres"

# 数据库监听配置
db_listen_addresses: "localhost"
db_port: 5432

# 数据库存储配置
db_data_directory: "/var/lib/postgresql/{{ db_version }}/main"
db_wal_directory: ""

# 数据库内存配置
db_shared_buffers: "128MB"
db_effective_cache_size: "4GB"
```

## 使用示例

```yaml
- hosts: databases
  roles:
    - role: database
      db_type: postgresql
      db_version: 14
      db_databases:
        - name: myapp_production
          owner: myapp_user
```

## License

MIT