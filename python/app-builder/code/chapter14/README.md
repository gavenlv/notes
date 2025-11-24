# 第十四章：Extending Flask App-Builder with Plugins

本章展示了如何使用插件扩展Flask-AppBuilder应用程序的功能。我们实现了多个插件来演示不同的扩展方式：

## 插件概述

### 1. Audit Log Plugin (审计日志插件)
- 记录用户操作日志
- 提供装饰器用于自动记录函数调用
- 支持安全事件记录

### 2. Email Service Plugin (邮件服务插件)
- 异步邮件发送功能
- 支持HTML和纯文本邮件
- 模板邮件系统
- 批量邮件发送

### 3. Task Manager Plugin (任务管理插件)
- 任务和任务分类管理
- 任务状态跟踪
- 任务仪表板视图

### 4. Redis Cache Plugin (Redis缓存插件)
- 基于Redis的数据缓存
- 支持多种数据序列化格式
- 缓存装饰器
- 缓存统计信息

### 5. Celery Tasks Plugin (Celery任务插件)
- 异步任务处理
- 定时任务调度
- 任务状态监控
- 任务管理接口

## 项目结构

```
chapter14/
├── app/
│   ├── __init__.py          # 应用工厂和插件注册
│   ├── models.py           # 共享数据模型
│   └── views.py            # 共享视图
├── plugins/
│   ├── audit_log/          # 审计日志插件
│   │   ├── __init__.py
│   │   └── plugin.py
│   ├── email_service/      # 邮件服务插件
│   │   ├── __init__.py
│   │   └── plugin.py
│   ├── task_manager/       # 任务管理插件
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   └── plugin.py
│   ├── redis_cache/        # Redis缓存插件
│   │   ├── __init__.py
│   │   └── plugin.py
│   └── celery_tasks/       # Celery任务插件
│       ├── __init__.py
│       └── plugin.py
├── config.py               # 配置文件
├── requirements.txt        # 依赖包
├── Dockerfile             # Docker配置
├── Makefile               # 构建脚本
└── README.md              # 说明文档
```

## 安装和运行

### 环境要求
- Python 3.7+
- Redis server (用于缓存和Celery)
- 数据库 (SQLite, PostgreSQL, MySQL)

### 安装步骤

1. 克隆项目:
   ```bash
   git clone <repository-url>
   cd chapter14
   ```

2. 创建虚拟环境:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

4. 初始化数据库:
   ```bash
   make db-init
   ```

5. 运行应用:
   ```bash
   make run
   ```

### Docker部署

```bash
# 构建镜像
make docker-build

# 运行容器
make docker-run
```

## 使用插件

### 注册插件
插件在`app/__init__.py`中自动注册。要启用或禁用插件，请修改`config.py`中的`ENABLED_PLUGINS`配置。

### 配置插件
每个插件都可以通过`config.py`中的相应配置项进行自定义。

## 开发新插件

要创建新的插件，请遵循以下步骤：

1. 在`plugins/`目录下创建新的插件目录
2. 实现继承自`BasePlugin`的插件类
3. 在`config.py`中添加相应的配置选项
4. 在`app/__init__.py`的插件注册函数中添加插件初始化代码

## 测试

运行测试:
```bash
make test
```

## License

MIT License