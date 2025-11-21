# Gunicorn 代码示例目录

本目录包含了与Gunicorn教程各章节相关的代码示例，帮助您理解和实践Gunicorn的各种功能和使用场景。

## 目录结构

```
code/
├── chapter1/     # 第1章：Gunicorn简介与环境搭建
├── chapter2/     # 第2章：Gunicorn核心概念与架构
├── chapter3/     # 第3章：Gunicorn配置与部署
├── chapter4/     # 第4章：Gunicorn性能优化
├── chapter5/     # 第5章：Gunicorn监控与日志管理
├── chapter6/     # 第6章：Gunicorn高可用与负载均衡
├── chapter7/     # 第7章：Gunicorn安全性最佳实践
├── chapter8/     # 第8章：Gunicorn故障排除与常见问题
└── README.md     # 本文件
```

## 各章节内容概览

### 第1章：Gunicorn简介与环境搭建

- **simple_wsgi_app.py** - 简单的WSGI应用示例
- **flask_example.py** - Flask应用示例
- **gunicorn_config.py** - 基本Gunicorn配置
- **start_gunicorn.sh** - Linux/macOS启动脚本
- **start_gunicorn.bat** - Windows启动脚本
- **requirements.txt** - 依赖列表

### 第2章：Gunicorn核心概念与架构

- **worker_comparison.py** - 用于比较不同Worker类型的测试应用
- **async_app.py** - 异步应用示例
- **benchmark.sh** - Worker性能测试脚本
- **signal_test.py** - 信号处理测试应用
- **send_signals.sh** - 信号发送脚本
- **requirements.txt** - 依赖列表

### 第3章：Gunicorn配置与部署

- **gunicorn_prod.conf.py** - 生产环境Gunicorn配置
- **gunicorn_dev.conf.py** - 开发环境Gunicorn配置
- **nginx.conf** - Nginx主配置
- **site.conf** - Nginx站点配置（含SSL）
- **README.md** - 本章说明文档

### 第4章：Gunicorn性能优化

- **performance_app.py** - 性能测试应用
- **benchmark_test.sh** - 性能基准测试脚本
- **requirements.txt** - 依赖列表
- **README.md** - 本章说明文档

### 第5章：Gunicorn监控与日志管理

- **monitoring_app.py** - 监控功能演示应用
- **log_analyzer.py** - 日志分析工具
- **requirements.txt** - 依赖列表
- **README.md** - 本章说明文档

### 第6-8章：高级主题

第6-8章的代码示例主要以配置文件和脚本为主，各章节README文档中有详细说明。

## 使用指南

### 1. 环境准备

所有示例都需要Python环境，建议使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv gunicorn-examples

# 激活虚拟环境
# Linux/macOS:
source gunicorn-examples/bin/activate
# Windows:
gunicorn-examples\Scripts\activate

# 升级pip
pip install --upgrade pip
```

### 2. 安装依赖

每个章节都有自己的requirements.txt文件，根据需要安装：

```bash
# 进入特定章节目录
cd code/chapter3

# 安装依赖
pip install -r requirements.txt
```

### 3. 运行示例

每个章节的README文档都包含详细的使用说明，以下是一些通用示例：

```bash
# 启动基本WSGI应用（第1章）
cd code/chapter1
gunicorn simple_wsgi_app:application

# 使用配置文件启动（第3章）
cd code/chapter3
gunicorn -c gunicorn_prod.conf.py myapp:application

# 运行性能测试（第4章）
cd code/chapter4
gunicorn -w 4 -k sync performance_app:application

# 在另一个终端运行基准测试
./benchmark_test.sh
```

## 实践建议

1. **循序渐进**：按照章节顺序学习和实践
2. **实际操作**：不要只看代码，一定要运行和修改
3. **实验记录**：记录不同配置下的测试结果
4. **问题记录**：记录遇到的问题和解决方案
5. **扩展应用**：在示例基础上添加自己的功能

## 常见问题

### 1. 端口占用

如果遇到端口占用错误：

```bash
# 查找占用端口的进程
lsof -i :8000
# 或
netstat -tulpn | grep :8000

# 终止进程
kill -9 <PID>
```

### 2. 权限问题

如果遇到权限问题：

```bash
# 使用非特权端口
gunicorn app:application -b 0.0.0.0:8080

# 或以适当用户运行
sudo -u www-data gunicorn app:application
```

### 3. 依赖安装

如果遇到依赖安装问题：

```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 使用特定版本
pip install package==version
```

## 进阶学习

完成所有示例后，您可以考虑：

1. **构建完整应用**：使用学到的知识构建一个完整的Web应用
2. **容器化部署**：将应用Docker化并部署
3. **Kubernetes部署**：在Kubernetes中部署应用
4. **性能优化**：针对特定应用场景进行性能优化
5. **监控集成**：集成Prometheus、Grafana等监控系统

## 反馈与贡献

如果您在学习过程中遇到问题或有改进建议，请：

1. 检查文档中的说明
2. 查看GitHub Issues
3. 提交新的Issue或Pull Request

## 参考资源

- [Gunicorn官方文档](https://docs.gunicorn.org/)
- [Flask官方文档](https://flask.palletsprojects.com/)
- [Nginx官方文档](https://nginx.org/en/docs/)
- [Docker官方文档](https://docs.docker.com/)

祝您学习愉快！