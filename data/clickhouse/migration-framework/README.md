# ClickHouse 迁移框架

一个用于 ClickHouse 数据库迁移的自动化框架，支持版本控制、迁移应用、回滚操作等功能。

## 📁 目录结构

```
migration-framework/
├── core/                           # 核心模块
│   ├── migration_manager.py        # 迁移管理器
│   ├── migration_parser.py         # 迁移解析器
│   ├── rollback_manager.py         # 回滚管理器
│   └── version_control.py          # 版本控制器
├── templates/                      # 模板文件
│   ├── migration_template.sql      # 迁移文件模板
│   └── rollback_template.sql       # 回滚文件模板
├── migrations/                     # 迁移文件
├── configs/                        # 配置文件
│   ├── environments/               # 环境配置
│   ├── templates/                  # 配置模板
│   └── migration-config.yml        # 主配置文件
├── scripts/                        # 脚本工具
│   ├── migrate.py                  # 迁移脚本
│   ├── rollback.py                 # 回滚脚本
│   └── status.py                   # 状态检查脚本
├── examples/                       # 示例文件
│   ├── sample_migration.sql        # 示例迁移文件
│   └── sample_rollback.sql         # 示例回滚文件
├── requirements.txt                # Python依赖
└── README.md                       # 本文件
```

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置文件

编辑 `configs/migration-config.yml` 文件以适应你的环境：

```yaml
database:
  host: localhost
  port: 9000
  database: your_database
  user: your_username
  password: your_password
```

### 创建迁移文件

```bash
python scripts/migrate.py create --name "create_users_table"
```

### 应用迁移

```bash
python scripts/migrate.py migrate
```

### 回滚迁移

```bash
python scripts/rollback.py --last
```

### 查看状态

```bash
python scripts/status.py
```

## 🛠️ 核心功能

### 1. 版本控制
- 自动跟踪已应用的迁移
- 确保迁移按正确顺序应用
- 防止重复应用同一迁移

### 2. 迁移管理
- 支持创建新的迁移文件
- 自动解析迁移文件内容
- 验证迁移文件语法

### 3. 回滚机制
- 支持回滚到最后一个版本
- 支持回滚到指定版本
- 自动生成回滚SQL语句

### 4. 环境配置
- 支持多环境配置（开发、测试、生产）
- 环境特定的数据库连接
- 环境特定的迁移设置

## 📄 迁移文件格式

### 迁移文件示例

```sql
-- Version: V1__create_users_table
-- Description: Create initial users table

CREATE TABLE users (
    id UInt64,
    name String,
    email String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (id);
```

### 回滚文件示例

```sql
-- Version: V1__create_users_table
-- Description: Rollback for creating initial users table

DROP TABLE users;
```

## ⚙️ 配置说明

### 主要配置项

```yaml
# 数据库配置
database:
  host: localhost           # 数据库主机
  port: 9000               # 数据库端口
  database: default        # 数据库名称
  user: default            # 用户名
  password: ""             # 密码
  secure: false            # 是否使用SSL
  verify: false            # 是否验证证书

# 迁移设置
migration:
  table_name: schema_migrations    # 迁移跟踪表名
  version_format: "V{version}__{description}"  # 版本命名格式
  rollback_enabled: true           # 是否启用回滚
  parallel_execution: false        # 是否并行执行
  dry_run: false                   # 是否预览模式

# 环境配置
environments:
  development:
    database: dev_db
    user: dev_user
  production:
    database: prod_db
    user: prod_user
    rollback_enabled: false  # 生产环境禁用回滚
```

## 🔧 使用场景

### 1. 开发环境同步
确保所有开发者使用相同的数据库结构

### 2. 测试环境部署
自动化测试环境的数据库初始化

### 3. 生产环境更新
安全地应用数据库变更到生产环境

### 4. 版本回退
当出现问题时快速回滚到之前的版本

## 📈 最佳实践

### 1. 迁移文件命名
使用清晰的描述性名称：
```
V1__create_users_table.sql
V2__add_email_index.sql
V3__modify_user_schema.sql
```

### 2. 迁移文件内容
- 每个迁移文件应该只做一件事
- 迁移应该是幂等的
- 包含适当的注释说明

### 3. 回滚策略
- 为每个迁移文件编写对应的回滚文件
- 在生产环境中谨慎使用回滚功能
- 测试回滚操作以确保其正确性

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个迁移框架！

## 📄 许可证

MIT License