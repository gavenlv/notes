# Common Role

通用系统配置角色，用于为所有服务器设置基础环境。

## 功能特性

- 用户和组管理
- 基础软件包安装
- 系统安全配置
- 时间同步配置
- 日志管理配置
- 网络配置优化

## 变量

### 默认变量 (defaults/main.yml)

```yaml
# 系统用户配置
common_system_users: []
# 示例:
# common_system_users:
#   - name: appuser
#     uid: 1001
#     group: appgroup
#     home: /home/appuser

# 基础软件包
common_base_packages:
  - curl
  - wget
  - vim
  - htop
  - git
  - rsync

# 防火墙配置
common_firewall_enabled: true
common_firewall_ports:
  - 22
  - 80
  - 443

# 时间同步
common_ntp_enabled: true
common_ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org

# 日志配置
common_logrotate_enabled: true
```

## 使用示例

```yaml
- hosts: all
  roles:
    - role: common
      common_system_users:
        - name: appuser
          uid: 1001
          group: appgroup
```

## License

MIT