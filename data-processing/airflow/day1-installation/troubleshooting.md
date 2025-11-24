# Airflow 安装故障排除指南

本文档提供了在安装和配置 Airflow 过程中可能遇到的常见问题及其解决方案。

## 常见问题与解决方案

### 1. Python 版本兼容性问题

**问题描述：** 安装 Airflow 时出现 Python 版本不兼容错误。

**解决方案：**
- 确保使用 Python 3.8 或更高版本
- 使用 `python --version` 检查当前版本
- 如果版本过低，请升级 Python 或使用 pyenv 管理多版本 Python

**命令示例：**
```bash
# 检查 Python 版本
python --version

# 使用 pyenv 安装 Python 3.9
pyenv install 3.9.10
pyenv local 3.9.10
```

### 2. 依赖包安装失败

**问题描述：** 安装 Airflow 或其依赖包时出现错误。

**解决方案：**
- 升级 pip 到最新版本：`pip install --upgrade pip`
- 使用国内镜像源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple apache-airflow`
- 检查网络连接和防火墙设置
- 对于 Windows 用户，可能需要安装 Microsoft C++ Build Tools

**命令示例：**
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像源安装
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple apache-airflow

# 安装特定版本的 Airflow
pip install apache-airflow==2.5.0
```

### 3. 数据库连接问题

**问题描述：** Airflow 无法连接到数据库。

**解决方案：**
- 检查数据库服务是否正在运行
- 验证连接字符串格式是否正确
- 确保数据库用户有足够的权限
- 检查防火墙设置是否阻止了数据库连接

**SQLite 连接示例：**
```ini
[database]
sql_alchemy_conn = sqlite:////path/to/your/airflow.db
```

**PostgreSQL 连接示例：**
```ini
[database]
sql_alchemy_conn = postgresql+psycopg2://user:password@localhost:5432/airflow
```

### 4. 权限问题

**问题描述：** Airflow 无法创建或访问必要的文件和目录。

**解决方案：**
- 确保 AIRFLOW_HOME 目录存在且可写
- 检查 DAGs、logs 和 plugins 目录的权限
- 对于 Linux/Mac，使用 `chmod` 修改权限
- 对于 Windows，确保用户有足够的权限

**命令示例：**
```bash
# 创建 Airflow 目录
mkdir -p ~/airflow/{dags,logs,plugins}

# 设置权限 (Linux/Mac)
chmod -R 755 ~/airflow
```

### 5. Web 服务器启动失败

**问题描述：** Airflow Web 服务器无法启动或访问。

**解决方案：**
- 检查端口是否被其他服务占用
- 确认防火墙设置允许访问指定端口
- 检查 Web 服务器配置是否正确
- 查看错误日志获取详细信息

**命令示例：**
```bash
# 检查端口占用
netstat -tulpn | grep :8080

# 使用不同端口启动
airflow webserver --port 8081
```

### 6. 调度器不工作

**问题描述：** DAG 不被调度执行。

**解决方案：**
- 确保调度器正在运行
- 检查调度器配置
- 验证 DAG 文件语法是否正确
- 确认 DAG 的 `start_date` 和 `schedule_interval` 设置正确

**命令示例：**
```bash
# 检查调度器状态
airflow scheduler --help

# 手动触发 DAG 运行
airflow dags trigger your_dag_id
```

### 7. DAG 加载问题

**问题描述：** DAG 文件无法加载或显示错误。

**解决方案：**
- 检查 DAG 文件语法是否正确
- 确保所有导入的模块已安装
- 验证 DAG 文件位于正确的 DAGs 目录
- 检查 DAG 定义是否遵循最佳实践

**命令示例：**
```bash
# 验证 DAG 文件
python -m py_compile your_dag_file.py

# 检查 DAG 列表
airflow dags list
```

### 8. Worker 进程问题 (CeleryExecutor)

**问题描述：** 使用 CeleryExecutor 时 Worker 进程出现问题。

**解决方案：**
- 确保 Redis 或 RabbitMQ 服务正在运行
- 检查 Celery 配置是否正确
- 验证 Worker 进程状态
- 查看 Celery 日志获取详细信息

**命令示例：**
```bash
# 检查 Celery worker 状态
celery -A airflow.executors.celery_executor.app inspect active

# 重启 Celery worker
pkill -f "airflow celery worker"
airflow celery worker
```

### 9. Docker 相关问题

**问题描述：** 使用 Docker 运行 Airflow 时遇到问题。

**解决方案：**
- 确保 Docker 和 Docker Compose 已正确安装
- 检查 Docker Compose 文件语法
- 验证容器之间的网络连接
- 查看容器日志获取详细信息

**命令示例：**
```bash
# 检查 Docker 状态
docker --version
docker-compose --version

# 查看容器日志
docker-compose logs airflow-webserver

# 重启所有服务
docker-compose down
docker-compose up -d
```

### 10. Windows 特有问题

**问题描述：** 在 Windows 环境下安装或运行 Airflow 时遇到问题。

**解决方案：**
- 使用 Windows Subsystem for Linux (WSL)
- 确保路径分隔符使用正确
- 使用 PowerShell 而不是 Command Prompt
- 考虑使用 Docker Desktop 运行 Airflow

**命令示例：**
```powershell
# 使用 PowerShell 设置环境变量
$env:AIRFLOW_HOME = "C:\airflow"

# 使用 WSL 安装 Airflow
wsl --install
```

## 调试技巧

### 1. 启用调试模式

在 `airflow.cfg` 中设置：
```ini
[core]
debug = True
```

### 2. 查看详细日志

```bash
# 查看 Web 服务器日志
tail -f $AIRFLOW_HOME/logs/webserver.log

# 查看调度器日志
tail -f $AIRFLOW_HOME/logs/scheduler.log

# 查看特定任务日志
airflow tasks log your_dag_id your_task_id your_execution_date
```

### 3. 使用 Airflow CLI 检查状态

```bash
# 检查 DAG 列表
airflow dags list

# 检查任务实例状态
airflow tasks list your_dag_id

# 检查连接
airflow connections list
```

### 4. 验证配置

```bash
# 显示当前配置
airflow config list

# 测试数据库连接
airflow db check
```

## 获取帮助

### 1. 官方文档

- [Apache Airflow 官方文档](https://airflow.apache.org/docs/)
- [Airflow GitHub 仓库](https://github.com/apache/airflow)

### 2. 社区资源

- [Airflow 邮件列表](https://airflow.apache.org/community/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/apache-airflow)
- [Airflow Slack](https://apache-airflow.slack.com/)

### 3. 搜索技巧

- 使用错误消息作为搜索关键词
- 包含 Airflow 版本信息
- 指定操作系统和执行器类型

## 预防措施

1. **定期备份**：定期备份 Airflow 元数据库和 DAG 文件
2. **版本控制**：使用 Git 管理 DAG 文件和配置
3. **监控**：设置监控和警报系统
4. **测试**：在生产环境部署前在测试环境充分测试
5. **文档**：记录自定义配置和修改

通过遵循本指南，您应该能够解决大多数 Airflow 安装和配置问题。如果问题仍然存在，请考虑在社区论坛或 Stack Overflow 上寻求帮助。