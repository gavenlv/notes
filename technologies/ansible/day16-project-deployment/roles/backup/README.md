# Backup Role

此角色用于在Ansible Day16项目中配置和管理备份策略。

## 功能特性

- 配置数据库备份（MySQL、PostgreSQL、MongoDB等）
- 配置文件和目录备份
- 支持本地和远程备份存储
- 配置备份保留策略
- 设置备份计划任务
- 配置备份通知和告警
- 支持备份压缩和加密

## 支持的备份类型

- 数据库备份
- 文件系统备份
- 应用配置备份
- 系统状态备份

## 默认变量

```yaml
# 备份配置
backup_enabled: true
backup_schedule: "0 2 * * *"  # 每天凌晨2点执行备份

# 备份存储配置
backup_storage_type: "local"  # local, s3, nfs, rsync
backup_local_path: "/backup"
backup_retention_days: 30

# 数据库备份配置
database_backup_enabled: true
database_backup_types:
  - mysql
  - postgresql

# 文件备份配置
file_backup_enabled: true
file_backup_paths:
  - /etc
  - /home
  - /var/log
```

## 使用示例

```yaml
- hosts: backup_servers
  roles:
    - role: backup
```

## 许可证

MIT