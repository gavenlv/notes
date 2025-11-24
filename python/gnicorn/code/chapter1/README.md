# 第1章代码示例

本章包含Gunicorn基础使用的代码示例，帮助您快速上手Gunicorn。

## 文件说明

- `simple_wsgi_app.py` - 简单的WSGI应用示例
- `flask_example.py` - Flask应用示例
- `gunicorn_config.py` - Gunicorn配置文件示例
- `start_gunicorn.sh` - Linux/macOS下启动Gunicorn的脚本
- `start_gunicorn.bat` - Windows下启动Gunicorn的脚本
- `requirements.txt` - 项目依赖列表

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行简单WSGI应用

```bash
gunicorn simple_wsgi_app:application
```

### 运行Flask应用

```bash
gunicorn flask_example:app
```

### 使用配置文件启动

```bash
gunicorn simple_wsgi_app:application -c gunicorn_config.py
```

### 使用脚本启动

Linux/macOS:
```bash
chmod +x start_gunicorn.sh
./start_gunicorn.sh
```

Windows:
```bash
start_gunicorn.bat
```

## 测试应用

启动后，您可以在浏览器中或使用curl测试应用：

```bash
# 测试简单WSGI应用
curl http://localhost:8000/
curl http://localhost:8000/about
curl http://localhost:8000/info

# 测试Flask应用
curl http://localhost:8000/
curl http://localhost:8000/api/data
curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' http://localhost:8000/api/echo
```

## 注意事项

1. 确保没有其他进程占用8000端口
2. 如果需要使用异步worker类型，请安装相应的依赖（gevent、eventlet等）
3. 生产环境建议使用配置文件而非命令行参数
4. 建议在虚拟环境中运行Gunicorn